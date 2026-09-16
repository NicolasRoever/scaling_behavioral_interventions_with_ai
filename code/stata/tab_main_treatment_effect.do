*===============================================================================
*  Overleaf Regression Tables - Main Effects (Split Tables)
*===============================================================================

* Add Controls
do 00_setup
* Load data
clear all
use "${data_folder}/processed/main_social_media/clean_merged_with_scrshots.dta", clear


*-------------------------------
* 1a. First table: Mechanism outcomes (non-minutes)
*-------------------------------
local outcomes z_motivation z_costbenefits z_smart_bett_wors_revers z_awareness z_selfefficacy wtp_dollars

* Run regressions and store with custom stats
eststo clear
foreach y of local outcomes {
    eststo: reg `y' i.T $controls, r
    
    * Add control mean
    qui summ `y' if control
    estadd scalar controlmean = r(mean)
    
    * Add controls indicator
    estadd local controls "Yes"
	
	* Add tests
    * Ambivalence vs Change
	test 1.T = 2.T
    estadd scalar p_amb_cha = r(p)
	
    * Ambivalence vs Persuasion
	test 2.T = 3.T
    estadd scalar p_amb_per = r(p)
	
    * Change vs Persuasion
	test 1.T = 3.T
    estadd scalar p_cha_per = r(p)	
}

*-------------------------------
* 2a. Export mechanisms table with p-values
*-------------------------------

esttab * , se b(3) nobase noomitted drop($controls _cons) label starlevels(* 0.10 ** 0.05 *** 0.01) mtitles("\makecell{Motivation\\ (std.)}" "\makecell{Perceived cost\\ of social\\ media (std.)}" "\makecell{Social media\\makes life \\ worse (std.)}" "\makecell{Awareness\\ self-control\\ problems (std.)}"  "\makecell{Self-\\efficacy\\ belief (std.)}"  "\makecell{WTP\\(\\$)}") coeflabel(1.T "Change Talk (a)" 2.T "Decisional Balance (b)" 3.T "Direct Persuasion (c)") stats(N r2 controlmean controls p_amb_cha p_cha_per p_amb_per, fmt(%9.0fc %9.3f %9.3f %9.3f %9.3f %9.3f %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: a=b" "p-value: a=c" "p-value: b=c")) 

esttab * using "${overleaf}/tables/tab_main_treatment_effects_sm_mechanisms.tex",  se b(3) nobase noomitted drop($controls _cons) label starlevels(* 0.10 ** 0.05 *** 0.01) mtitles("\makecell{Motivation\\ (std.)}" "\makecell{Perceived cost\\ of social\\ media (std.)}" "\makecell{Social media\\makes life \\ worse (std.)}" "\makecell{Awareness\\ self-control\\ problems (std.)}"  "\makecell{Self-\\efficacy\\ belief (std.)}"  "\makecell{WTP\\(\\$)}") coeflabel(1.T "Change Talk (a)" 2.T "Decisional Balance (b)" 3.T "Direct Persuasion (c)") stats(N r2 controlmean controls p_amb_cha p_cha_per p_amb_per, fmt(%9.0fc %9.3f %9.3f %9.3f %9.3f %9.3f %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: a=b" "p-value: a=c" "p-value: b=c")) booktabs fragment replace


* old version
* esttab `outcomes' using "${overleaf}/tables/tab_main_treatment_effects_sm_mechanisms.tex", cells(b(fmt(3) star) se(fmt(3) par)) starlevels(* 0.10 ** 0.05 *** 0.01) coeflabel(1.T "Ambivalence (a)" 2.T "Change (b)" 4.T "Direct Persuasion (c)") stats(N r2 controlmean controls p_12 p_14 p_24, fmt(%9.0f %9.3f %9.3f %9s %9.3f %9.3f %9.3f) labels("Observations" "R-squared" "Control mean" "Controls" "p-value a=b" "p-value a=c" "p-value c=b")) keep(1.T 2.T 4.T) label nobase noomitted  booktabs fragment replace 
	   

	   
*-------------------------------
* 1b. Second table: Minutes outcomes
*-------------------------------

local outcomes posterior_ideal_social_min_w posterior_actual_social_min_w

* Run regressions and store with custom stats
eststo clear
foreach y of local outcomes {
    eststo: reg `y' i.T $controls, r
    
    * Add control mean
    qui summ `y' if control
    estadd scalar controlmean = r(mean)
    
    * Add controls indicator
    estadd local controls "Yes"
	
	* Add tests
    * Ambivalence vs Change
	test 1.T = 2.T
    estadd scalar p_amb_cha = r(p)
	
    * Ambivalence vs Persuasion
	test 2.T = 3.T
    estadd scalar p_amb_per = r(p)
	
    * Change vs Persuasion
	test 1.T = 3.T
    estadd scalar p_cha_per = r(p)	
}

* NOW ONLY FOR FOLLOWUP OUTCOMES
foreach y in w2_actual_social_min_wins  {
    eststo: reg `y' i.T $controls_followup, r
    
    * Add control mean
    qui summ `y' if control
    estadd scalar controlmean = r(mean)
    
    * Add controls indicator
    estadd local controls "Yes"
	
	* Add tests
    * Ambivalence vs Change
	test 1.T = 2.T
    estadd scalar p_amb_cha = r(p)
	
    * Ambivalence vs Persuasion
	test 2.T = 3.T
    estadd scalar p_amb_per = r(p)
	
    * Change vs Persuasion
	test 1.T = 3.T
    estadd scalar p_cha_per = r(p)
}

*-------------------------------
* 2b. Export minutes table with p-values
*-------------------------------

esttab * , se b(3) nobase noomitted keep (*T) label starlevels(* 0.10 ** 0.05 *** 0.01) mtitles("\makecell{Ideal social\\ media time (min)}" "\makecell{Predicted social\\ media time (min)}" "\makecell{Actual social\\ media time (min)}") coeflabel(1.T "Change Talk (a)" 2.T "Decisional Balance (b)" 3.T "Direct Persuasion (c)") stats(N r2 controlmean controls p_amb_cha p_cha_per p_amb_per, fmt(%9.0fc %9.3f %9.3f %9.3f %9.3f %9.3f %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: a=b" "p-value: a=c" "p-value: b=c"))


esttab * using "${overleaf}/tables/tab_main_treatment_effects_sm_minutes.tex",  se b(3) nobase noomitted keep(*T) label starlevels(* 0.10 ** 0.05 *** 0.01) mtitles("\makecell{Ideal social\\ media time (min)}" "\makecell{Predicted social\\ media time (min)}" "\makecell{Actual social\\ media time (min)}") coeflabel(1.T "Change Talk (a)" 2.T "Decisional Balance (b)" 3.T "Direct Persuasion (c)") stats(N r2 controlmean controls p_amb_cha p_cha_per p_amb_per, fmt(%9.0fc %9.3f %9.3f %9.3f %9.3f %9.3f %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: a=b" "p-value: a=c" "p-value: b=c"))  booktabs fragment replace
