*===============================================================================
* All numbers quoted in text
*===============================================================================

clear all
do 00_setup
use "${data_folder}/processed/main_social_media/clean_merged.dta", clear


**********************************************************************
***************** Numbers quoted in section 2.1 **********************
**********************************************************************

*Income
summ income_in_usd
local mean_income = r(mean)
display as text "Mean income in the sample in Dollars is " %9.0f `mean_income'


*At least one hour
count if baseline_actual_social_min > 60
display "Percentage of sample at least 1 hour on social media per day: " (r(N) / _N) * 100



**********************************************************************
***************** Numbers quoted in section 2.2.1**********************
**********************************************************************

*Interview Time
summ time_interview_minutes
local mean_interview_duration = r(mean)
display "Average interview duration in the sample in minutes is" %3.0f `mean_interview_duration'

*Revisit WTP Downwards
count if correct_wtp == 1
display "Percentage of sample revising their WTP downwards: " (r(N) / _N) * 100

*Revisit WTP Upwards
count if correct_wtp == 2
display "Percentage of sample revising their WTP upwards " (r(N) / _N) * 100


**********************************************************************
***************** Numbers quoted in section 2.2.2**********************
**********************************************************************

summarize followup_responded
local recontact_rate = r(mean)
display "Recontact rate was at " %9.4f `recontact_rate'

count if !missing(prolific_id)
local total = r(N)
count if w2_finished == 1 & !missing(prolific_id)
local finished = r(N)
display "Finished w2 out of total sample: `finished' / `total' (" ///
    %5.1f (100 * `finished' / `total') "%)"



**********************************************************************
***************** Numbers quoted in section 3.1 **********************
**********************************************************************



* Baseline Time (raw, not winsorized)
summarize baseline_actual_social_min

local mean_val = r(mean)
local sd_val   = r(sd)

local mean_str_av : display %3.0f `mean_val'
local sd_str_av   : display %3.0f `sd_val'

display as text "On average, participants spend `mean_str_av' minutes on social media per day (SD = `sd_str_av' minutes)."


*Ideal Time
summarize baseline_ideal_social_min
local mean_val = r(mean)
local mean_str_ideal : di %3.0f `mean_val'

display as text "Ideally, participants want to spend `mean_str_ideal' on social media per day."


* Preference for Reduction
gen wants_less_social = (baseline_actual_social_min > baseline_ideal_social_min) ///
    if !missing(baseline_actual_social_min, baseline_ideal_social_min)
sum wants_less_social
local mean_val = r(mean)
local mean_less: di %3.2f `mean_val'
display as text "Overall, `mean_less' have a preference for reduction"


*Addiction to at least one app
foreach var in tiktok instagram snapchat facebook youtube reddit twitter {
    gen addicted_`var' = .
    replace addicted_`var' = inlist(addiction_`var', 4, 5, 6) if (addiction_`var' != 1) & !missing(addiction_`var')
}

egen feels_addicted = rowtotal(addicted_tiktok addicted_instagram addicted_snapchat addicted_facebook addicted_youtube addicted_reddit addicted_twitter)
summarize feels_addicted
generate addiction_indicator = (feels_addicted > 0)
summarize addiction_indicator
local mean_val = r(mean)
local mean_addiction: di %3.2f `mean_val'
display as text "Overall, `mean_addiction' report being at least somewhat addicted"


*Addiction to Tiktok, Insta and Youtube
summ addicted_tiktok
local mean_val = r(mean)
local mean_tiktok: di %3.2f `mean_val'

summ addicted_instagram
local mean_val = r(mean)
local mean_instagram: di %3.2f `mean_val'

summ addicted_youtube
local mean_val = r(mean)
local mean_youtube: di %3.2f `mean_val'
display as text "Overall, `mean_tiktok' report being at least somewhat addicted to Tiktok, `mean_instagram' to Instagram and `mean_youtube' to YouTube."


*Use Data Tiktok Insta YouTube
summ baseline_tiktok_min_midpoint
local mean_val = r(mean)
local mean_tiktok: di %3.0f `mean_val'

summ baseline_instagram_min_midpoint
local mean_val = r(mean)
local mean_instagram: di %3.0f `mean_val'

summ baseline_youtube_min_midpoint
local mean_val = r(mean)
local mean_youtube: di %3.0f `mean_val'

display as text "Average usage of Tiktok is `mean_tiktok', if Instagram is `mean_instagram' and of YouTube is`mean_youtube'."



*Descriptive Interview Length
 summ time_interview_minutes



*People Who Use Audio
count if audio_count > 0
display "Percentage > 0: " (r(N) / _N) * 100


**********************************************************************
***************** Numbers quoted in section 4.4.1**********************
**********************************************************************



* Difference between above and below median
reg z_motivation high_social_media_use if control , r
local b_hsm = _b[high_social_media_use]
display as text "Specifically, control group participants with above-median baseline social media use report a " %4.2f `b_hsm' " standard deviation higher motivation than participants with below-median baseline social media use"


*Difference in Minutes
summ baseline_actual_social_min_w if control & high_social_media_use == 0
local mean_0 = r(mean)
summ baseline_actual_social_min_w if control & high_social_media_use == 1
local mean_1 = r(mean)
local diff = `mean_1' - `mean_0'

di "Mean 0: `mean_0'"
di "Mean 1: `mean_1'"
di "Difference: `diff'"


*Percentage Reduction Prediction
eststo clear
summ posterior_actual_social_min_w if control, de
local controlmean = r(mean)
eststo reg1: reg posterior_actual_social_min_w $controls i.T
qui suest reg1, r
* Extract treatment coefficients (adjust base level to your design)
scalar b_change = _b[1.T]
scalar b_db     = _b[2.T]

* Percent differences
local perc_diff_change = b_change / `controlmean' * 100
local perc_diff_db     = b_db     / `controlmean' * 100


display "Reduction of predicted posterior time is " %9.0f `perc_diff_change' " percent for change talk relative to control mean and " %9.0f `perc_diff_db' "for decisional balance"




**********************************************************************
***************** Numbers quoted in section 4.4.2**********************
**********************************************************************

use "${data_folder}/processed/main_social_media/clean_merged_with_scrshots.dta", clear

* Screen Time enabled at baseline
count if screen_time_enabled == 1
local screen_time_enabled = r(N)
display as text "At baseline, " as result %9.0fc `screen_time_enabled' ///
    as text " participants had Screen Time enabled."


* Valid screenshots for both of the two previous weeks (weeks 1 and 52)
count if valid_scr_wk1 == 1 & valid_scr_wk52 == 1
local valid_previous_two_weeks = r(N)

* The two-week verified outcome must use exactly this paired sample.
count if !missing(verified_prefered_time)
assert r(N) == `valid_previous_two_weeks'

display as text "Valid screenshots for both previous weeks were uploaded by " ///
    as result %9.0fc `valid_previous_two_weeks' as text " participants."


*SUR Regression
eststo clear
qui eststo reg1: reg verified_prefered_time_w $controls_followup i.T
qui eststo reg2: reg w2_actual_social_min_w $controls_followup i.T if !missing(verified_prefered_time_w)
qui suest reg1 reg2,r

test ([reg1_mean]1.T = [reg2_mean]1.T) ///
     ([reg1_mean]2.T = [reg2_mean]2.T) ///
     ([reg1_mean]3.T = [reg2_mean]3.T)

local pval = r(p)
display as text "The p-value of no differences in treatment effects is  " as result `pval'

* 1. Run pwcorr to get the coefficient and sample size
pwcorr verified_prefered_time_w w2_actual_social_min_w
matrix C = r(C)
local corr_val = C[2,1]
local N = r(N)

* 2. Calculate t-statistic and p-value
* t = r * sqrt(N-2) / sqrt(1-r^2)
local t_stat = `corr_val' * sqrt(`N' - 2) / sqrt(1 - `corr_val'^2)
local p_val = 2 * ttail(`N' - 2, abs(`t_stat'))


display "The correlation is " %4.3f `corr_val' " (p=" %5.4f `p_val' ")"




**********************************************************************
***************** Numbers quoted in section 4.4.5**********************
**********************************************************************
clear

do "${code_folder}/Helpers/load_expdemand_data.do" "${data_folder}"

*Motivation
eststo clear
eststo reg1: reg z_motivation i.T $controls if inlist(llm_category_expdemand, 1,2) &!missing(llm_category_expdemand)
eststo reg2: reg z_motivation i.T $controls if inlist(llm_category_expdemand, 3,4,5) &!missing(llm_category_expdemand)

qui suest reg1 reg2,r

test ([reg1_mean]1.T = [reg2_mean]1.T) ///
     ([reg1_mean]2.T = [reg2_mean]2.T) ///
     ([reg1_mean]3.T = [reg2_mean]3.T)

	local pval = r(p)
display as text "The p-value of no differences in treatment effects on motivation between experimenter demand prone and not prone is  " as result round(`pval',0.01)

*Cost-Benefits
eststo clear
eststo reg1: reg z_costbenefits i.T $controls if inlist(llm_category_expdemand, 1,2) &!missing(llm_category_expdemand)
eststo reg2: reg z_costbenefits i.T $controls if inlist(llm_category_expdemand, 3,4,5) &!missing(llm_category_expdemand)

qui suest reg1 reg2,r

test ([reg1_mean]1.T = [reg2_mean]1.T) ///
     ([reg1_mean]2.T = [reg2_mean]2.T) ///
     ([reg1_mean]3.T = [reg2_mean]3.T)

	local pval = r(p)
display as text "The p-value of no differences in treatment effects on cost-benefits between experimenter demand prone and not prone is  " as result round(`pval',0.01)


**********************************************************************
***************** Unused Variables **********************
**********************************************************************
//
//
//
//
// foreach var in tiktok_use instagram_use snapchat_use facebook_use youtube_use reddit_use twitter_use {
//     gen ideal_`var' = .
//     replace ideal_`var' = inlist(baseline_ideal_`var', 2, 3) if (baseline_ideal_`var' != 1) & !missing(baseline_ideal_`var')
// }
//
// summ ideal_*
//
//
//
// egen ideal_lower = rowtotal(ideal_tiktok_use ideal_instagram_use ideal_snapchat_use ideal_facebook_use ideal_youtube_use ideal_reddit_use ideal_twitter_use)
//
//
//





