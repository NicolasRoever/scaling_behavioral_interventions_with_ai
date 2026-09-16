* This exhibit uses the historical survey snapshot identified in REPRODUCIBILITY_NOTES.md.
*===============================================================================
*  Overleaf Regression Tables - Main Effects (Split Tables)
*===============================================================================

* Add Controls
do 00_setup

* Load data
clear all
use "${data_folder}/processed/main_social_media/manuscript_followup_snapshot.dta", clear


gen baseline_wedge = baseline_actual_social_min - baseline_ideal_social_min
* gen baseline_wedge = baseline_actual_social_min_w

summ baseline_wedge, de
gen high_wedge = baseline_wedge > r(p50)



* Run regressions and store with custom stats
eststo clear
foreach y in posterior_actual_social_min_w w2_actual_social_min_wins {
    * REGRESSION 1: BELOW MEDIAN WEDGE
    eststo: reg `y' i.T $controls_followup if high_wedge==0, r
    
    * Add control mean
    qui summ `y' if control & high_wedge==0
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

    * REGRESSION 2: ABOVE MEDIAN WEDGE
    eststo: reg `y' i.T $controls_followup if high_wedge==1, r
    
    * Add control mean
    qui summ `y' if control & high_wedge==1
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

esttab * , se b(3) starlevel(* 0.1 ** 0.05 *** 0.01) nobase noomitted label keep(*T) mtitles("Low gap" "High gap" "Low gap" "High gap" "Low gap" "High gap") mgroups("Ideal social time" "Predicted social time" "Actual social time", pattern(1 0 1 0 1 0))


esttab * using "${overleaf}/tables/tab_heterogeneity_timeuse_by_wedge.tex", se b(3) starlevel(* 0.1 ** 0.05 *** 0.01) nobase noomitted label keep(*T) mtitles("Low gap" "High gap" "Low gap" "High gap") mgroups("Predicted social time" "Actual social time", pattern(1 0 1 0 1 0) prefix(\multicolumn{@span}{c}{) suffix(}) span erepeat(\cmidrule(lr){@span}))  coeflabel(1.T "Change Talk (a)" 2.T "Decisional Balance (b)" 3.T "Direct Persuasion (c)") stats(N r2 controlmean controls p_amb_cha p_cha_per p_amb_per, fmt(%9.0fc %9.3f %9.3f %9.3f %9.3f %9.3f %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: a=b" "p-value: a=c" "p-value: b=c")) booktabs fragment replace



/* eststo clear
eststo: reg z_motivation  i.T $controls if high_wedge==0, r
eststo: reg z_motivation  i.T $controls if high_wedge==1, r
esttab * , se b(3) starlevel(* 0.1 ** 0.05 *** 0.01) nobase noomitted label keep(*T)

eststo clear
eststo: reg posterior_ideal_social_min_w i.T $controls_followup if high_wedge==0, r
eststo: reg posterior_ideal_social_min_w i.T $controls_followup if high_wedge==1, r
esttab * , se b(3) starlevel(* 0.1 ** 0.05 *** 0.01) nobase noomitted label keep(*T)

eststo clear
eststo: reg posterior_actual_social_min_w i.T $controls_followup if high_wedge==0, r
eststo: reg posterior_actual_social_min_w i.T $controls_followup if high_wedge==1, r
esttab * , se b(3) starlevel(* 0.1 ** 0.05 *** 0.01) nobase noomitted label keep(*T) */
