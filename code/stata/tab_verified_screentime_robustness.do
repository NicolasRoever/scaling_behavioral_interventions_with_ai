********************************************************************************
* Project: MI SOCIAL MEDIA
* Purpose: Robustness of treatment effects on screenshot-measured social media
*          time to outcome construction, tail handling, and covariate adjustment
********************************************************************************

version 17
clear all
set more off

do 00_setup.do
use "${data_folder}/processed/main_social_media/clean_merged_with_scrshots.dta", clear

********************************************************************************
* Construct daily screenshot outcomes
********************************************************************************

* The extracted screenshot variables record weekly minutes. The main outcome is
* the average daily value across weeks 1 and 52 and requires both observations.
gen double verified_week1_daily = social_time_min_ver_wk1 / 7
gen double verified_week52_daily = social_time_min_ver_wk52 / 7

label variable verified_week1_daily  "Screenshot time, week 1 (min/day)"
label variable verified_week52_daily "Screenshot time, week 52 (min/day)"

assert abs(verified_prefered_time - ///
    (verified_week1_daily + verified_week52_daily) / 2) < 0.001 ///
    if !missing(verified_prefered_time)

********************************************************************************
* Estimate paired unadjusted and adjusted specifications
********************************************************************************

local outcomes ///
    verified_prefered_time_w ///
    verified_prefered_time ///
    verified_week1_daily ///
    verified_week52_daily

local model_number = 0
eststo clear

foreach outcome of local outcomes {
    foreach adjusted in 0 1 {
        local ++model_number

        if `adjusted' == 0 {
            eststo model`model_number': regress `outcome' i.T, vce(robust)
            estadd local controls "No"
        }
        else {
            eststo model`model_number': regress `outcome' i.T ///
                $controls_followup, vce(robust)
            estadd local controls "Yes"
        }

        quietly summarize `outcome' if control & e(sample), meanonly
        estadd scalar controlmean = r(mean)

        quietly testparm i.T
        estadd scalar p_joint = r(p)
    }
}

********************************************************************************
* Display and export the appendix table
********************************************************************************

local table_options ///
    se b(3) nobase noomitted keep(1.T 2.T 3.T) label ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("No" "Yes" "No" "Yes" "No" "Yes" "No" "Yes") ///
    mgroups("Both weeks, winsorized" "Both weeks, raw" ///
        "Week 1, raw" "Week 52, raw", ///
        pattern(1 0 1 0 1 0 1 0) ///
        prefix(\multicolumn{@span}{c}{) suffix(}) span ///
        erepeat(\cmidrule(lr){@span})) ///
    coeflabel(1.T "Change Talk" ///
        2.T "Decisional Balance" ///
        3.T "Direct Persuasion") ///
    stats(N controlmean controls p_joint, ///
        fmt(%9.0fc %9.3f %9s %9.3f) ///
        labels("Observations" "Control group mean" "Controls" ///
            "p-value: joint treatment test"))

esttab model1 model2 model3 model4 model5 model6 model7 model8, ///
    `table_options'

esttab model1 model2 model3 model4 model5 model6 model7 model8 ///
    using "${overleaf}/tables/tab_verified_screentime_robustness.tex", ///
    `table_options' booktabs fragment replace
