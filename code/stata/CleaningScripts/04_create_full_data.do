*----------------------------------------------------------
* Merge Main and Follow Up and Screenshot Data
*----------------------------------------------------------

*Load Followup Data
use "${data_folder}/processed/main_social_media/follow_up_clean.dta", clear

* Safe Renaming: Loop through all variables to safely rename with prefix
foreach var of varlist * {
    * Check if the new name would exceed 32 characters
    if length("w1_`var'") > 32 {
        * Truncate the original name to 29 chars so the total is 32
        local shortname = substr("`var'", 1, 29)
        rename `var' w2_`shortname'
    }
    else {
        * Otherwise, just add the prefix
        rename `var' w2_`var'
    }
}
rename w2_prolific_id prolific_id

sort prolific_id
merge 1:1 prolific_id using "${data_folder}/processed/main_social_media/clean_data.dta"
tab _merge

* Drop people who are not in the main wave and identify follow-up respondents.
drop if _merge == 1
rename _merge completed_followp
replace completed_followp = completed_followp == 3
label define yesno 0 "No" 1 "Yes", replace
label values completed_followp yesno
label var completed_followp "Matched to a follow-up response (legacy name)"

* Distinguish responding to the follow-up from finishing the entire survey.
gen byte followup_responded = completed_followp
label var followup_responded "Participated in follow-up"
label values followup_responded yesno

gen byte followup_finished = w2_finished == 1 if followup_responded == 1
replace followup_finished = 0 if missing(followup_finished)
label var followup_finished "Finished follow-up survey"
label values followup_finished yesno

gen byte attrition = 1 - followup_responded
label var attrition "Did not participate in follow-up"
label values attrition yesno


********************************************************************************
* Standardize Motivation
********************************************************************************

summ w2_motivation if control , de
gen w2_z_motivation = (w2_motivation - r(mean)) / r(sd) 
la var w2_z_motivation "Motivation (std.)"

********************************************************************************
* Cost Benefits
********************************************************************************

summ w2_costbenefits if control, de
gen w2_z_costbenefits = (w2_costbenefits - r(mean)) / r(sd)
la var w2_z_costbenefits "Cost-benefit (std.)"

********************************************************************************
* Social Media better Worse
********************************************************************************

summ w2_smartphone_better_worse if control, de
gen w2_z_smartphone_better_worse = (w2_smartphone_better_worse - r(mean)) / r(sd)
la var w2_z_smartphone_better_worse "Social media makes life better (std.)"

gen w2_z_smart_bett_wors_revers = w2_z_smartphone_better_worse * (-1)
la var w2_z_smart_bett_wors_revers "Social media makes life worse (std.)"

* Save the current baseline-follow-up merge used by non-screenshot analyses.
compress
save "${data_folder}/processed/main_social_media/clean_merged.dta", replace



********************************************************************************
* Merge Screenshot Data
********************************************************************************


* 1. Create a variable in the current dataset named 'response_id' to match the using file
capture drop response_id // Safety drop if it already exists
clonevar response_id = w2_response_id

* 2. Ensure the key is a clean string (consistent with the cleaning in the previous do-file)
capture confirm string variable response_id
if _rc tostring response_id, replace
replace response_id = trim(response_id)

* 2. HANDLE MISSING IDs UNIQUELY
gen is_missing_id = 0
replace is_missing_id = 1 if missing(response_id) | response_id == "NA" | response_id == "."

* Assign a unique temp ID like "MISSING_ROW_1", "MISSING_ROW_2" to these rows
replace response_id = "MISSING_ROW_" + string(_n) if is_missing_id == 1

* 4. Perform the 1:1 merge with the Stata-cleaned screenshot file. Do not add
* screenshot-only records that are absent from the cleaned survey sample.
merge 1:1 response_id using ///
    "${data_folder}/processed/main_social_media/clean_scr_data.dta", ///
    keep(master match)

* 5. Review the merge distribution
label variable _merge "Merge status: Social Media Data"
tab _merge


gen verified_prefered_time = (social_time_min_ver_wk1 + social_time_min_ver_wk52) / 14
* We divide by 2 for averaging and by 7 to gewt daily values, so we get /14
la var verified_prefered_time "Screentime from OpenAI in Average Daily Minutes (Week 1 ands 52)"

winsor2 verified_prefered_time, cuts(5 95) suffix(_w)
la var verified_prefered_time_w "Screentime from OpenAI in Average Daily Minutes (Week 1 ands 52), winsorized"


gen ver_pref_tiktok = (tiktok_wk1 + tiktok_wk52) / 14
winsor2 ver_pref_tiktok, cuts(5 95) suffix(_w)
la var ver_pref_tiktok_w "TIktok Time Daily Minutes from Screeenshots Average Week 1 Week 52"


gen ver_pref_instagram = (instagram_wk1 + instagram_wk52) / 14
winsor2 ver_pref_instagram, cuts(5 95) suffix(_w)
la var ver_pref_instagram_w "Instagram Time Daily Minutes from Screeenshots Average Week 1 Week 52"


********************************************************************************
* Extra Variables for Ingar
********************************************************************************

clonevar actual_time = verified_prefered_time_w
clonevar reported_time = w2_actual_social_min_wins 




*------- Save the final merged dataset with MI scores ---------------
save "${data_folder}/processed/main_social_media/clean_merged_with_scrshots.dta", replace
