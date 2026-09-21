

*===============================================================================
*  Regressions Main Effects
*===============================================================================


* Add Controls
do 00_setup

* Load data
clear all

use "${data_folder}/processed/main_social_media/clean_merged.dta", clear

gen close_to_ideal_5 = abs(w2_actual_social_min_wins - baseline_ideal_social_min_w) <= 5 if !missing(w2_actual_social_min_wins)
gen close_to_ideal_10 = abs(w2_actual_social_min_wins - baseline_ideal_social_min_w) <= 10 if !missing(w2_actual_social_min_wins)
gen close_to_ideal_20 = abs(w2_actual_social_min_wins - baseline_ideal_social_min_w) <= 20 if !missing(w2_actual_social_min_wins)
gen close_to_ideal_30 = abs(w2_actual_social_min_wins - baseline_ideal_social_min_w) <= 30 if !missing(w2_actual_social_min_wins)

eststo clear
eststo: reg close_to_ideal_5 i.T $controls_followup, r
eststo: reg close_to_ideal_10 i.T $controls_followup, r
eststo: reg close_to_ideal_20 i.T $controls_followup, r
eststo: reg close_to_ideal_30 i.T $controls_followup, r




* Run regressions and store with custom stats
eststo clear
foreach y in close_to_ideal_5 close_to_ideal_10 close_to_ideal_20 close_to_ideal_30 {
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

esttab * , se b(3) starlevel(* 0.1 ** 0.05 *** 0.01) keep(*T) label nobase noomitted

esttab * using "${overleaf}/tables/tab_treatment_effects_closetoideal_followup.tex",  se b(3) nobase noomitted keep(*T) label starlevels(* 0.10 ** 0.05 *** 0.01) mtitles("\makecell{Within \\ 5 min}" "\makecell{Within \\ 10 min}" "\makecell{Within \\ 20 min}" "\makecell{Within \\ 30 min}") coeflabel(1.T "Change Talk (a)" 2.T "Decisional Balance (b)" 3.T "Direct Persuasion (c)") stats(N r2 controlmean controls p_amb_cha p_cha_per p_amb_per, fmt(%9.0fc %9.3f %9.3f %9.3f %9.3f %9.3f %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: a=b" "p-value: a=c" "p-value: b=c")) prehead("&\multicolumn{@M}{c}{Actual time is close to ideal social media time (0/1)}\\\cmidrule(lr){2-@span}") booktabs fragment replace





**** OTHER STUFF ******

* For unreported regressions in the self-reported social media time section using data from the follow-up survey
gen reduce_time = w2_actual_social_min_wins < baseline_actual_social_min_w if !missing(w2_actual_social_min_wins)
reg reduce_time i.T $controls_followup, r


