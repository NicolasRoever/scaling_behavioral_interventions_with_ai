* Restricted-input method source; original image/transcript files are not distributed.
********************************************************************************
* Project: MI SOCIAL MEDIA
* Purpose: Create analysis-ready screenshot data and remove invalid screenshots
*
* Screenshot-folder mapping:
*   screenshot_upload_1 = week 1
*   Q228                = week 51
*   scr_upload_2        = week 52
*
* Invalid screenshots are identified from the files stored under
* invalid_screenshots/<upload folder>/{all_devices,wrong_week,strange_layout}.
* Files in other_reason are intentionally not excluded.
********************************************************************************

version 17
set more off
capture label define yesno 0 "No" 1 "Yes"

local processed_dir "${data_folder}/processed/main_social_media"
local invalid_root  "${raw_folder}/main_socialmedia/follow_up_screenshots/invalid_screenshots"

tempfile invalid_file_level invalid_by_response
tempname invalid_post

********************************************************************************
* Build a reproducible exclusion register from all three upload folders
********************************************************************************

postfile `invalid_post' ///
    str30 screenshot_folder ///
    int screenshot_week ///
    str20 invalid_reason ///
    str244 screenshot_filename ///
    using `invalid_file_level', replace

foreach folder in screenshot_upload_1 Q228 scr_upload_2 {
    if "`folder'" == "screenshot_upload_1" local week 1
    if "`folder'" == "Q228"                local week 51
    if "`folder'" == "scr_upload_2"        local week 52

    foreach reason in all_devices wrong_week strange_layout {
        local invalid_dir "`invalid_root'/`folder'/`reason'"
        local screenshots : dir "`invalid_dir'" files "*"

        foreach screenshot of local screenshots {
            * Ignore hidden system files such as .DS_Store.
            if substr(`"`screenshot'"', 1, 1) != "." {
                post `invalid_post' ///
                    ("`folder'") ///
                    (`week') ///
                    ("`reason'") ///
                    (`"`screenshot'"')
            }
        }
    }
}
postclose `invalid_post'

use `invalid_file_level', clear

* Qualtrics filenames begin with response_id followed by another underscore.
gen str20 response_id = regexs(1) if regexm(screenshot_filename, "^(R_[^_]+)_")
assert !missing(response_id)

gen byte invalid_screenshot = 1
order response_id screenshot_week screenshot_folder invalid_reason ///
    screenshot_filename invalid_screenshot
sort screenshot_week response_id invalid_reason screenshot_filename

label variable response_id         "Survey response ID"
label variable screenshot_week     "Week shown by screenshot upload"
label variable screenshot_folder   "Qualtrics screenshot upload folder"
label variable invalid_reason      "Reason screenshot is invalid"
label variable screenshot_filename "Filename in invalid-screenshot folder"
label variable invalid_screenshot  "Screenshot excluded from analysis"

save "`processed_dir'/screenshot_exclusions.dta", replace
export delimited using "`processed_dir'/screenshot_exclusions.csv", replace

* Reduce to one set of week-specific flags per survey response. A screenshot can
* appear under more than one invalid reason, so take the maximum within week.
gen byte invalid_scr_wk1  = screenshot_week == 1
gen byte invalid_scr_wk51 = screenshot_week == 51
gen byte invalid_scr_wk52 = screenshot_week == 52

collapse (max) invalid_scr_wk1 invalid_scr_wk51 invalid_scr_wk52, by(response_id)
label variable invalid_scr_wk1  "Week 1 screenshot excluded"
label variable invalid_scr_wk51 "Week 51 screenshot excluded"
label variable invalid_scr_wk52 "Week 52 screenshot excluded"
save `invalid_by_response', replace

********************************************************************************
* Parse each raw extraction file in Stata and apply week-specific exclusions
********************************************************************************

* The extraction CSVs contain the API responses as strings. This program parses
* total time and the top-three apps without relying on a Python-cleaned file.
capture program drop clean_screenshot_week
program define clean_screenshot_week
    version 17
    syntax, TIMEFILE(string) WEEK(integer) SAVING(string) [APPSFILE(string)]

    import delimited using `"`timefile'"', clear varnames(1) ///
        case(lower) bindquote(strict) maxquotedrows(unlimited) encoding(utf8)

    capture confirm string variable response_id
    if _rc tostring response_id, replace
    replace response_id = trim(response_id)
    isid response_id

    * Weeks 1 and 52 have time and app responses in the same extraction file.
    capture confirm variable response_time
    if !_rc {
        rename response_time raw_time_response
        rename response_apps raw_apps_response
    }
    else {
        * The older week-51 extraction stored time and apps separately.
        rename response raw_time_response
        keep response_id raw_time_response
        tempfile time_response
        save `time_response', replace

        import delimited using `"`appsfile'"', clear varnames(1) ///
            case(lower) bindquote(strict) maxquotedrows(unlimited) encoding(utf8)
        capture confirm string variable response_id
        if _rc tostring response_id, replace
        replace response_id = trim(response_id)
        rename response raw_apps_response
        keep response_id raw_apps_response
        isid response_id
        merge 1:1 response_id using `time_response', keep(match) nogen
    }

    * Constrain each match to the value immediately following its JSON key.
    * This leaves strings such as "null" missing rather than accidentally
    * matching later numbers in the stored API metadata.
    capture drop screen_time_hours screen_time_minutes
    gen double screen_time_hours = real(regexs(1)) if ///
        regexm(raw_time_response, ///
        "screen_time_hours[^:]*:[^0-9A-Za-z]*([0-9]+)")
    gen double screen_time_minutes = real(regexs(1)) if ///
        regexm(raw_time_response, ///
        "screen_time_minutes[^:]*:[^0-9A-Za-z]*([0-9]+)")
    gen double social_time_min_ver = ///
        60 * screen_time_hours + screen_time_minutes

    * Parse the name, hours, and minutes for each of the top-three app slots.
    forvalues slot = 1/3 {
        gen str80 app_name`slot' = ustrregexs(1) if ///
            ustrregexm(raw_apps_response, ///
            `"name`slot'[^:]*:[ ]*"([^"]+)""')
        replace app_name`slot' = lower(strtrim(app_name`slot'))

        gen double app_hours`slot' = real(regexs(1)) if ///
            regexm(raw_apps_response, ///
            "hours`slot'[^:]*:[^0-9A-Za-z]*([0-9]+)")
        gen double app_minutes`slot' = real(regexs(1)) if ///
            regexm(raw_apps_response, ///
            "minutes`slot'[^:]*:[^0-9A-Za-z]*([0-9]+)")
    }

    local social_apps facebook instagram linkedin messages messenger telegram ///
        threads tiktok whatsapp snapchat

    foreach app of local social_apps {
        gen double `app' = .
        forvalues slot = 1/3 {
            replace `app' = cond(missing(`app'), 0, `app') + ///
                60 * app_hours`slot' + app_minutes`slot' ///
                if app_name`slot' == "`app'" & ///
                !missing(app_hours`slot', app_minutes`slot')
        }
    }

    keep response_id social_time_min_ver `social_apps'
    keep if !missing(social_time_min_ver)

    rename social_time_min_ver social_time_min_ver_wk`week'
    foreach app of local social_apps {
        rename `app' `app'_wk`week'
    }

    isid response_id
    sort response_id
    save `"`saving'"', replace
end

tempfile clean_wk1 clean_wk51 clean_wk52

clean_screenshot_week, ///
    timefile("`processed_dir'/social_time_week1_v007.csv") ///
    week(1) saving("`clean_wk1'")

clean_screenshot_week, ///
    timefile("`processed_dir'/screenshot_data/social_time_week51_v001.csv") ///
    appsfile("`processed_dir'/Archive/social_apps_week51_v004.csv") ///
    week(51) saving("`clean_wk51'")

clean_screenshot_week, ///
    timefile("`processed_dir'/social_time_week52_v007.csv") ///
    week(52) saving("`clean_wk52'")

********************************************************************************
* Exclude invalid week-level records, then merge all valid screenshots
********************************************************************************

foreach week in 1 51 52 {
    if `week' == 1  local current_week_file `clean_wk1'
    if `week' == 51 local current_week_file `clean_wk51'
    if `week' == 52 local current_week_file `clean_wk52'

    use `current_week_file', clear
    merge 1:1 response_id using `invalid_by_response', keep(master match) nogen
    replace invalid_scr_wk`week' = 0 if missing(invalid_scr_wk`week')
    drop if invalid_scr_wk`week'
    drop invalid_scr_wk1 invalid_scr_wk51 invalid_scr_wk52
    save `current_week_file', replace
}

use `clean_wk1', clear
merge 1:1 response_id using `clean_wk51', nogen
merge 1:1 response_id using `clean_wk52', nogen

merge 1:1 response_id using `invalid_by_response', keep(master match) nogen
foreach flag in invalid_scr_wk1 invalid_scr_wk51 invalid_scr_wk52 {
    replace `flag' = 0 if missing(`flag')
    label values `flag' yesno
}

foreach week in 1 51 52 {
    gen byte valid_scr_wk`week' = !missing(social_time_min_ver_wk`week')
    label variable valid_scr_wk`week' "Valid extracted week `week' screenshot"
    label values valid_scr_wk`week' yesno
}

order response_id valid_scr_wk1 valid_scr_wk51 valid_scr_wk52 ///
    invalid_scr_wk1 invalid_scr_wk51 invalid_scr_wk52 ///
    social_time_min_ver_wk1 social_time_min_ver_wk51 ///
    social_time_min_ver_wk52
sort response_id
compress

save "`processed_dir'/clean_scr_data.dta", replace

********************************************************************************
* End
********************************************************************************
