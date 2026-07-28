*===============================================================================
*  Appendix: Selection into Uploading Screenshots (Reviewer Comment 1, item 4)
*  1. Regress an upload indicator on treatment plus baseline covariates
*  2. Balance table comparing the screenshot subsample to the full follow-up
*     sample, broken out by arm
*===============================================================================

* Add Controls
do 00_setup

* Load data
clear all
use "${data_folder}/processed/main_social_media/clean_merged_with_scrshots.dta", clear

* Restrict to the full follow-up sample; _merge==3 identifies respondents
* whose screenshots were successfully matched and verified
keep if followup_responded == 1
gen byte uploaded_screenshot = (_merge == 3)
la var uploaded_screenshot "Uploaded verified screenshot"


*-------------------------------------------------------------------------
* 1. Selection into uploading: regress upload indicator on T + covariates
*-------------------------------------------------------------------------

eststo clear
eststo model1: reg uploaded_screenshot i.T $controls_followup, r
estadd local controls "Yes"

qui summ uploaded_screenshot if control
estadd scalar controlmean = r(mean)

* Joint F-test: are the three treatment dummies jointly significant predictors
* of uploading a screenshot? (tests for differential selection into the
* verified-screenshot subsample by treatment arm)
qui testparm i.T
estadd scalar p_joint_T = r(p)

esttab model1, se b(3) nobase noomitted drop($controls_followup _cons) label ///
    starlevels(* 0.10 ** 0.05 *** 0.01) mtitles("Uploaded screenshot") ///
    coeflabel(1.T "Change Talk" 2.T "Decisional Balance" 3.T "Direct Persuasion") ///
    stats(N r2 controlmean controls p_joint_T, fmt(%9.0fc %9.3f %9.3f %9s %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: joint F-test, treatment"))

esttab model1 using "${overleaf}/tables/tab_selection_into_upload.tex", ///
    se b(3) nobase noomitted drop($controls_followup _cons) label ///
    starlevels(* 0.10 ** 0.05 *** 0.01) mtitles("Uploaded screenshot") ///
    coeflabel(1.T "Change Talk" 2.T "Decisional Balance" 3.T "Direct Persuasion") ///
    stats(N r2 controlmean controls p_joint_T, fmt(%9.0fc %9.3f %9.3f %9s %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: joint F-test, treatment")) ///
    booktabs fragment replace


*-------------------------------------------------------------------------
* 2. Balance table: screenshot subsample vs. full follow-up sample, by arm
*-------------------------------------------------------------------------

local balance_vars age female log_income fulltime college baseline_actual_social_min tiktok_use_dummy instagram_use_dummy snapchat_use_dummy facebook_use_dummy youtube_use_dummy reddit_use_dummy twitter_use_dummy

qui reg uploaded_screenshot `balance_vars', r
qui testparm `balance_vars'
local fval_all : di %5.3f r(p)
di "Joint F-test p-value, Full sample: " %6.3f `fval_all'

qui reg uploaded_screenshot `balance_vars' if T == 0, r
qui testparm `balance_vars'
local fval_C : di %5.3f r(p)
di "Joint F-test p-value, Control: " %6.3f `fval_C'

qui reg uploaded_screenshot `balance_vars' if T == 1, r
qui testparm `balance_vars'
local fval_T1 : di %5.3f r(p)
di "Joint F-test p-value, Change Talk: " %6.3f `fval_T1'

qui reg uploaded_screenshot `balance_vars' if T == 2, r
qui testparm `balance_vars'
local fval_T2 : di %5.3f r(p)
di "Joint F-test p-value, Decisional Balance: " %6.3f `fval_T2'

qui reg uploaded_screenshot `balance_vars' if T == 3, r
qui testparm `balance_vars'
local fval_T3 : di %5.3f r(p)
di "Joint F-test p-value, Direct Persuasion: " %6.3f `fval_T3'

la var age "Age"
la var female "Female"
la var log_income "Log household income"
la var fulltime "Full-time employed"
la var college "College degree"
la var baseline_actual_social_min "Social media use (min/day)"
la var tiktok_use_dummy "TikTok user"
la var instagram_use_dummy "Instagram user"
la var snapchat_use_dummy "Snapchat user"
la var facebook_use_dummy "Facebook user"
la var youtube_use_dummy "YouTube user"
la var reddit_use_dummy "Reddit user"
la var twitter_use_dummy "Twitter user"

* Uploaded-vs-not-uploaded difference, for the whole sample and within each arm
balancetable (diff uploaded_screenshot) (diff uploaded_screenshot if T == 0) (diff uploaded_screenshot if T == 1) (diff uploaded_screenshot if T == 2) (diff uploaded_screenshot if T == 3) `balance_vars' using "${overleaf}/tables/tab_balance_upload_subsample.tex", replace pvalues varlabels booktabs starlevels(* 0.1 ** 0.05 *** 0.01) ctitles("Full sample" "Control" "Change Talk" "Decisional Balance" "Direct Persuasion") groups("Uploaded vs. not uploaded, by sample and arm", pattern(1 0 0 0 0) end("\cmidrule(lr){2-6}")) leftctitle(" ") prefoot("& & & & & \\ \textit{p}-value of joint \textit{F}-test & `fval_all' & `fval_C' & `fval_T1' & `fval_T2' & `fval_T3' \\ & & & & & \\ \hline")
