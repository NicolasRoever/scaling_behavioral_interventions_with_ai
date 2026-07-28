*===============================================================================
*  Overleaf Regression Tables - Main Effects (Split Tables)
*===============================================================================

* Add Controls
do 00_setup

* Load data
clear all
use "${data_folder}/processed/main_social_media/clean_data.dta", clear


local outcomes emotions_interested emotions_excited emotions_upset emotions_guilty emotions_irritated emotions_ashamed emotions_determined emotions_encouraged

foreach var in emotions_interested emotions_excited emotions_upset emotions_guilty emotions_irritated emotions_ashamed emotions_determined emotions_encouraged {
    summ `var' if control, de
    gen z_`var' = (`var' - r(mean)) / r(sd)
}

* Run regressions and store with custom stats
eststo clear
foreach y of local outcomes {
    eststo: reg z_`y' i.T $controls, r
    
    * Add control mean
    qui summ z_`y' if control
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

esttab * , se b(3) nobase noomitted drop($controls _cons) label starlevels(* 0.10 ** 0.05 *** 0.01) mtitles("Interested" "Excited" "Upset" "Guilty" "Irritated" "Ashamed" "Determined" "Encouraged") coeflabel(1.T "Change Talk (a)" 2.T "Decisional Balance (b)" 3.T "Persuasion (c)") stats(N r2 controlmean controls p_amb_cha p_cha_per p_amb_per, fmt(%9.0fc %9.3f %9.3f %9.3f %9.3f %9.3f %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: a=b" "p-value: a=c" "p-value: b=c")) 


*-------------------------------
* Coefplot
*-------------------------------

eststo clear
foreach y of local outcomes {
    reg z_`y' i.T $controls
    eststo model_`y'
}


suest model_emotions_irritated model_emotions_upset  model_emotions_excited model_emotions_ashamed model_emotions_interested model_emotions_guilty  model_emotions_determined model_emotions_encouraged,r
est sto all



coefplot ///
    (all, keep(*:1.T) ///
        offset(0.2) ///
        mcolor(maroon) msymbol(O) msize(2) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(maroon) lpattern(solid))) ///
	(all, keep(*:2.T) ///
        offset(0) ///
        mcolor(gs8) msymbol(S) msize(2) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(gs8) lpattern(solid))) ///
	(all, keep(*:3.T) ///
        offset(-0.2) ///
        mcolor(navy) msymbol(T) msize(2) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(navy) lpattern(solid))), ///
    swapnames label ///
	  coeflabel( ///
		model_emotions_interested_mean = "Interested" ///
		model_emotions_excited_mean = "Excited" ///
		model_emotions_upset_mean = "Upset" ///
		model_emotions_guilty_mean = "Guilty" ///
		model_emotions_irritated_mean = "Irritated" ///
		model_emotions_ashamed_mean = "Ashamed" ///
		model_emotions_determined_mean = "Determined" ///
		model_emotions_encouraged_mean = "Encouraged", ///
		     wrap(15) labsize(medsmall) ///
    ) ///
    xtitle("Treatment effect (in standard deviations)") ///
    xmtick(##2)  ///
	ysize(6) ///
	xsize(8) ///
    xlab(-0.2(0.2)1.2, labsize(medsmall)) ///
	    legend( ///
        label(2 "Change Talk") ///
        label(4 "Decisional Balance") ///
		label(6 "Direct Persuasion") ///
		ring(0) pos(3) ///
        fcolor(white) region(lcolor(black) lwidth(0.1) fcolor(white)) ///
        size(medsmall) ///
    ) ///
    grid(between glcolor(gs10) glwidth(medthick)) ///
	 xline(0, lpattern(dash) lcolor(gs8) lwidth(0.4)) ///
		

graph export "${overleaf}/figures/fig_emotions.pdf", replace
