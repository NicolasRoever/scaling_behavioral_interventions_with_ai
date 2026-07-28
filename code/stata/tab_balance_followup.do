version 17
clear all
set more off

do 00_setup.do
use "${data_folder}/processed/main_social_media/clean_merged.dta", clear
keep if followup_responded == 1

* Rename some long variables
rename baseline_actual_social_min_w actual_social_short
rename baseline_ideal_social_min_w ideal_social_short
rename baseline_tiktok_min_midpoint tiktok_short
rename baseline_facebook_min_midpoint facebook_short
rename baseline_instagram_min_midpoint instagram_short
rename baseline_youtube_min_midpoint youtube_short

gen log_actual_social_short = log(actual_social_short)
gen log_ideal_social_short = log(ideal_social_short)

* Balance variables
local balance_vars age female college employed log_income white black hispanic country_us actual_social_short iphone_user app_installed_tiktok_or_insta


qui reg T `balance_vars' if inlist(T, 0, 1), r
qui testparm `balance_vars'
local fval_C_T1 : di %5.3f r(p)
di "Joint F-test p-value for Control vs T1: " %6.3f `fval_C_T1'

qui reg T `balance_vars' if inlist(T, 0, 2), r
qui testparm `balance_vars'
local fval_C_T2 : di %5.3f r(p)
di "Joint F-test p-value for Control vs T2: " %6.3f `fval_C_T2'

qui reg T `balance_vars' if inlist(T, 0, 3), r
qui testparm `balance_vars'
local fval_C_T3 : di %5.3f r(p)
di "Joint F-test p-value for Control vs T3: " %6.3f `fval_C_T3'

qui reg T `balance_vars' if inlist(T, 1, 2), r
qui testparm `balance_vars'
local fval_T1_T2 : di %5.3f r(p)
di "Joint F-test p-value for T1 vs T2: " %6.3f `fval_T1_T2'

qui reg T `balance_vars' if inlist(T, 1, 3), r
qui testparm `balance_vars'
local fval_T1_T3 : di %5.3f r(p)
di "Joint F-test p-value for T1 vs T3: " %6.3f `fval_T1_T3'

qui reg T `balance_vars' if inlist(T, 2, 3), r
qui testparm `balance_vars'
local fval_T2_T3 : di %5.3f r(p)
di "Joint F-test p-value for T2 vs T3: " %6.3f `fval_T2_T3'

la var age "Age" 
la var female "Female" 
la var college "College degree" 
la var employed "Employed" 
la var hispanic "Hispanic origin" 
la var log_income "Log household income"
la var actual_social_short "Social media use (min/day)"
la var iphone_user "iPhone user"
la var app_installed_tiktok_or_insta "TikTok or Instagram user"


gen T1 = T==1
gen T2 = T==2
gen T3 = T==3

* Balance table
balancetable (mean) (diff T1 if inlist(T, 0, 1)) (diff T2 if inlist(T, 0, 2)) (diff T3 if inlist(T, 0, 3)) (diff T2 if inlist(T, 1, 2)) (diff T3 if inlist(T, 1, 3)) (diff T3 if inlist(T, 2, 3)) `balance_vars' using "${overleaf}/tables/tab_balance_followup.tex", replace pvalues varlabels booktabs starlevels(* 0.1 ** 0.05 *** 0.01) ctitles("" "C vs T1" "C vs T2" "C vs T3" "T1 vs T2" "T1 vs T3" "T2 vs T3") groups("Sample mean" "Mean differences and \textit{p}-values", pattern(1 1 0 0 0 0 0) end("\cmidrule(lr){2-2} \cmidrule(lr){3-8}")) leftctitle(" ") prefoot("& & & & & & & \\ \textit{p}-value of joint \textit{F}-test & & `fval_C_T1' & `fval_C_T2' & `fval_C_T3' & `fval_T1_T2' & `fval_T1_T3' & `fval_T2_T3' \\ & & & & & & & \\ \hline")
