********************************************************************************
* Project: MI SOCIAL MEDIA
* Purpose : Clean raw follow up survey data and construct analysis variables
********************************************************************************

********************************************************************************
* Import data
********************************************************************************

* Do this once for easier cleaning later on. Saves a bit of time
clear
import spss using "${raw_folder}/main_socialmedia/follow_up_raw.sav", case(lower)
destring *, replace
save "${raw_folder}/main_socialmedia/follow_up_raw.dta", replace

use "${raw_folder}/main_socialmedia/follow_up_raw.dta", clear

* Consent
keep if consent == 1
drop consent


********************************************************************************
* Drop metadata / technical variables 
********************************************************************************

* Sort by startdate within prolific ids
sort prolific_pid startdate 

* Only keep the duplicates with max progress
bysort prolific_pid: egen max_progress = max(progress)
gen tmp = progress == max_progress
keep if tmp == 1
* If we have multiple with same progress, keep the first one
duplicates tag prolific_pid , generate(dup_tag)
bysort prolific_pid: gen n = _n
drop if n > 1
* Check that no duplicates are left
drop dup_tag
duplicates tag prolific_pid , generate(dup_tag)
fre dup_tag
drop dup_tag n max_progress tmp


drop meta_data_browser meta_data_version meta_data_operating_system meta_data_resolution
drop q_recaptcha* q_duplicate* distributionchannel userlanguage

********************************************************************************
* Rename key identifiers and timing variables
********************************************************************************

rename responseid     response_id
rename prolific_pid   prolific_id
rename study_id       study_id_raw

rename startdate      start_time_raw
rename enddate        end_time_raw
rename duration__*    duration_seconds

label var response_id      "Survey response ID"
label var prolific_id      "Prolific ID"
label var study_id_raw     "Original study ID"
label var start_time_raw   "Survey start time (raw)"
label var end_time_raw     "Survey end time (raw)"
label var duration_seconds "Survey duration in seconds"

* Convert duration to minutes
gen double duration_minutes = duration_seconds/60.0
label var duration_minutes "Survey duration in minutes"

********************************************************************************
* Convert date–time variables to Stata datetimes
********************************************************************************

capture confirm numeric variable start_time_raw
if _rc {
    * Example if they are strings; adapt mask to your format
    gen double start_time = clock(start_time_raw, "YMDhms")
    gen double end_time   = clock(end_time_raw,   "YMDhms")
}
else {
    gen double start_time = start_time_raw
    gen double end_time   = end_time_raw
}

format start_time end_time %tc
label var start_time "Survey start time"
label var end_time   "Survey end time"


********************************************************************************
* Motivation
********************************************************************************

la var motivation "Motivation"

********************************************************************************
* Cost Benefits
********************************************************************************

gen costbenefits = (costsbenefits_1 + costsbenefits_2 + costsbenefits_3 + costsbenefits_4) / 4 if !missing(costsbenefits_1, costsbenefits_2, costsbenefits_3, costsbenefits_4)
la var costbenefits "Cost-benefit"

********************************************************************************
* Social Media better Worse
********************************************************************************

la var smartphone_better_wo "Smartphone makes life better/worse"
rename smartphone_better_wo smartphone_better_worse 

********************************************************************************
* Actual Time
********************************************************************************

* Destring time variables before conversion
destring actual_time_1_1_1 actual_time_1_1_2, replace force

* Convert actual social media time from hours/minutes to total minutes
gen actual_social_min = actual_time_1_1_1 * 60 + actual_time_1_1_2 if !missing(actual_time_1_1_1, actual_time_1_1_2)
la var actual_social_min "Self-reported actual social media time (minutes)"
drop actual_time_1_1_1 actual_time_1_1_2


* Generate winsorized social media time variables (pre-registered)

winsor2 actual_social_min, cuts(5 95) suffix(_wins)
la var actual_social_min_wins "Actual social media time (minutes, winsorized)"


********************************************************************************
* Clean Mechanism Variables
********************************************************************************

* Ensure yes/no label exists
capture label define yesno 0 "No" 1 "Yes"

* 1. Clean the string variables first
* If "NA" is stored as text, convert it to an empty string so !missing() works correctly.
foreach var of varlist mechanisms_* {
    capture replace `var' = "" if `var' == "NA"
}

* 2. Generate new binary variables with descriptive names
* Logic: If the string is not empty (!missing), they ticked the box -> 1. Else -> 0.

gen mechanism_settings      = !missing(mechanisms_1) if !missing(time_mechanism_page_submit)
gen mechanism_blocker       = !missing(mechanisms_10) if !missing(time_mechanism_page_submit)
gen mechanism_notif         = !missing(mechanisms_11) if !missing(time_mechanism_page_submit)
gen mechanism_friction      = !missing(mechanisms_12) if !missing(time_mechanism_page_submit)
gen mechanism_delete        = !missing(mechanisms_13) if !missing(time_mechanism_page_submit)
gen mechanism_rules         = !missing(mechanisms_14) if !missing(time_mechanism_page_submit)
gen mechanism_reach         = !missing(mechanisms_15) if !missing(time_mechanism_page_submit)
gen mechanism_reduce_phone  = !missing(mechanisms_16) if !missing(time_mechanism_page_submit)
gen mechanism_curate_feed   = !missing(mechanisms_17) if !missing(time_mechanism_page_submit)
gen mechanism_replace_act   = !missing(mechanisms_18) if !missing(time_mechanism_page_submit)
gen mechanism_help          = !missing(mechanisms_19) if !missing(time_mechanism_page_submit)
gen mechanism_willpower     = !missing(mechanisms_20) if !missing(time_mechanism_page_submit)
gen mechanism_other         = !missing(mechanisms_21) if !missing(time_mechanism_page_submit)
gen mechanism_none          = !missing(mechanisms_22) if !missing(time_mechanism_page_submit)

drop mechanisms_1 mechanisms_10 mechanisms_11 mechanisms_12 mechanisms_13 mechanisms_14 mechanisms_15 mechanisms_16 mechanisms_17 mechanisms_18 mechanisms_19 mechanisms_20 mechanisms_21 mechanisms_22 mechanisms_21_text

* 3. Label the variables
label var mechanism_settings      "Used built-in phone settings (Screen Time/Digital Wellbeing)"
label var mechanism_blocker       "Used a third-party app blocker"
label var mechanism_notif         "Turned off or muted notifications"
label var mechanism_friction      "Made access harder (e.g., logged out, hid apps)"
label var mechanism_delete        "Deleted/uninstalled apps or deactivated account"
label var mechanism_rules         "Set specific rules/goals (e.g., no phone at bedtime)"
label var mechanism_reach         "Put phone out of reach"
label var mechanism_reduce_phone  "Reduced overall phone use"
label var mechanism_curate_feed   "Changed feed content (e.g., unfollowed accounts)"
label var mechanism_replace_act   "Replaced social media with other activities"
label var mechanism_help          "Asked someone else to help (accountability)"
label var mechanism_willpower     "Relied on willpower/discipline"
label var mechanism_other         "Other mechanism"
label var mechanism_none          "No steps taken"

* 4. Apply value labels
label values mechanism_* yesno

* 5. (Optional) Drop the original raw variables to clean up
* drop mechanisms_1 mechanisms_10-mechanisms_22 mechanisms_21_text


order time_*, last
drop time_*_click_count time_*_first_click time_*_last_click
rename time_*_page_submit time_*
order tim_*, last
drop tim_*_click_count tim_*_first_click tim_*_last_click
rename tim_*_page_submit time_*


********************************************************************************
* Exoport Data
********************************************************************************

compress
order prolific_id motivation costbenefits smartphone_better_worse mechanism_*, first
save "${data_folder}/processed/main_social_media/follow_up_clean.dta", replace

