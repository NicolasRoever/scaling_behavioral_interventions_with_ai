*===============================================================================
*  Overleaf Regression Tables - Main Effects (Split Tables)
*===============================================================================

* Add Controls
do 00_setup

* Load data
clear all
use "${data_folder}/processed/main_social_media/clean_merged.dta", clear

eststo clear	   


*  First Regression

regress posterior_ideal_social_min_w i.T $controls
eststo idealtime

regress posterior_actual_social_min_w i.T $controls
eststo predicted_time

regress w2_actual_social_min_wins i.T $controls_followup
eststo actualtime


suest idealtime predicted_time actualtime, r
est sto all

*-------------------------------
* 3. Coefplot for minutes outcomes
*-------------------------------
ereturn list



coefplot ///
    (all, keep(*:1.T) ///
        offset(0.2) ///
        mcolor(maroon) msymbol(O) msize(2.5) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(maroon) lpattern(solid))) ///
	(all, keep(*:2.T) ///
        offset(0) ///
        mcolor(gs8) msymbol(S) msize(2.5) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(gs8) lpattern(solid))) ///
	(all, keep(*:3.T) ///
        offset(-0.2) ///
        mcolor(navy) msymbol(T) msize(2.5) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(navy) lpattern(solid))), ///
    swapnames label ///
	  coeflabel( ///
	  idealtime_mean  = "Ideal social media time" ///
        actualtime_mean = "Self-reported social media time at follow-up" ///
       predicted_time_mean = "Predicted social media time", ///
        wrap(15) labsize(medsmall) ///
    ) ///
    xlab(-50(10)30, labsize(medsmall)) xtitle("Treatment effect (in minutes)", size(medsmall)) ///
    xmtick(##2) ///
    mlabposition(12) ///
    mlabel(string(@b, "%9.1fc")) ///
    mlabsize(small) ///
    grid(none) ///
	    legend( ///
        label(2 "Change Talk") ///
        label(4 "Decisional Balance") ///
		label(6 "Direct Persuasion") ///
        ring(0) pos(3) ///
        region(lcolor(black) lwidth(0.1)) ///
        size(medsmall) ///
    ) ///
	 xline(0, lpattern(dash) lcolor(gs8) lwidth(0.4) noextend)


graph export "${overleaf}/figures/fig_minutes_treatment_effects.pdf", as(pdf) replace
