* This exhibit uses the historical survey snapshot identified in REPRODUCIBILITY_NOTES.md.
*===============================================================================
* Figure Mechanism Question Effects
*===============================================================================

* Add Controls
do 00_setup

* Load data
clear all

use "${data_folder}/processed/main_social_media/manuscript_followup_snapshot.dta", clear
keep if !missing(w2_motivation)
keep if !missing(w2_time_mechanism)

*-------------------------------
* Run Regression
*-------------------------------

rename (w2_mechanism_reduce_phone w2_mechanism_curate_feed w2_mechanism_replace_act w2_mechanism_willpower) (w2_msm_reduce_phone w2_msm_curate_feed w2_msm_replace_act w2_msm_willpower)

gen msm_technology = 0
foreach var in w2_mechanism_settings w2_mechanism_blocker w2_msm_curate_feed w2_mechanism_notif w2_mechanism_delete {
    replace msm_technology = 1 if `var' == 1 
}

gen msm_behavioral = 0
foreach var in w2_mechanism_rules w2_mechanism_reach w2_msm_replace_act w2_mechanism_help w2_msm_willpower w2_mechanism_friction w2_msm_reduce_phone  {
    replace msm_behavioral = 1 if `var' == 1
}





eststo clear
foreach y in w2_mechanism_none msm_behavioral msm_technology {
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

esttab * , se b(3) starlevel(* 0.1 ** 0.05 *** 0.01) nobase noomitted keep(*T) label mtitles("No steps taken" "Behavioral strategies" "Technology-based strategies")


*-------------------------------
* 2a. Export mechanisms table with p-values
*-------------------------------

esttab * using "${overleaf}/tables/tab_strategies_followup.tex", se b(3) nobase noomitted keep(*T) label starlevels(* 0.10 ** 0.05 *** 0.01) mtitles("\makecell{No steps \\ taken}" "\makecell{Behavioral\\ strategy used}" "\makecell{Technolgy-based\\strategy used}") coeflabel(1.T "Change Talk (a)" 2.T "Decisional Balance (b)" 3.T "Direct Persuasion (c)") stats(N r2 controlmean controls p_amb_cha p_cha_per p_amb_per, fmt(%9.0fc %9.3f %9.3f %9.3f %9.3f %9.3f %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: a=b" "p-value: a=c" "p-value: b=c")) booktabs fragment replace



* Overall count works but let's not go into this. Extensive margin is fine.
/* egen strategy_count = rowtotal(w2_mechanism_settings w2_mechanism_blocker w2_mechanism_notif w2_mechanism_friction w2_mechanism_delete w2_mechanism_rules w2_mechanism_reach w2_mechanism_help w2_mechanism_other)
egen tech_count = rowtotal(w2_mechanism_settings w2_mechanism_blocker w2_msm_curate_feed w2_mechanism_notif w2_mechanism_delete)
egen behav_count = rowtotal(w2_mechanism_rules w2_mechanism_reach w2_msm_replace_act w2_mechanism_help w2_msm_willpower w2_mechanism_friction w2_msm_reduce_phone)

eststo clear
eststo: reg strategy_count i.T, r
eststo: reg tech_count i.T, r
eststo: reg behav_count i.T, r
esttab * , se b(3) starlevel(* 0.1 ** 0.05 *** 0.01) nobase noomitted keep(*T) label mtitles("Total count" "Tech count" "Behavior count") */
