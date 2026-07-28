*===============================================================================
*  Overleaf Regression Tables - Main Effects (Split Tables)
*===============================================================================


* Add Controls
do 00_setup

* Load data
clear all

use "${data_folder}/processed/main_social_media/clean_data.dta", clear


*-------------------------------
* 1a. First table: Mechanism outcomes (non-minutes)
*-------------------------------
rename z_smart_bett_wors_revers z_phone_rev
local outcomes z_motivation z_costbenefits z_selfefficacy z_awareness z_phone_rev z_wtp_dollars

* Run regressions and store with custom stats
eststo clear
foreach y of local outcomes {
    reg `y' i.T $controls
    eststo model_`y'
}

suest model_z_motivation model_z_costbenefits model_z_phone_rev model_z_awareness model_z_selfefficacy model_z_wtp_dollars, r
est sto all

*-------------------------------
* 3. Coefplot v001
*-------------------------------
ereturn list

coefplot ///
    (all, keep(*:1.T) ///
        offset(0.25) ///
        mcolor(maroon) msymbol(O) msize(2.5) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(maroon) lpattern(solid))) ///
	(all, keep(*:2.T) ///
        offset(0) ///
        mcolor(gs8) msymbol(S) msize(2.5) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(gs8) lpattern(solid))) ///
	(all, keep(*:3.T) ///
        offset(-0.25) ///
        mcolor(navy) msymbol(T) msize(2.5) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(navy) lpattern(solid))), ///
    swapnames label ///
	  coeflabel( ///
	  model_z_motivation_mean  = "Motivation" ///
       model_z_costbenefits_mean = "Perceived costs of social media" ///
	   model_z_selfefficacy_mean = "Self-efficacy belief" ///
	   model_z_awareness_mean = "Awareness of self-control problems" ///
	   model_z_phone_rev_mean = "Social media makes life worse" ///
	   model_z_wtp_dollars_mean = "WTP", ///
        wrap(20) labsize(medsmall) ///
    ) ///
    xtitle("Treatment effect (in standard deviations)", size(medsmall)) ///
    xmtick(##2)  ///
	xlab(-0.3(0.1)0.8, labsize(medsmall)) ///
	ysize(7) ///
	xline(0, lpattern(dash) lcolor(gs8) lwidth(0.4)) ///
	xsize(12) ///
    grid(between glcolor(gs10) ) ///
	    legend( ///
        label(2 "Change Talk") ///
        label(4 "Decisional Balance") ///
		label(6 "Direct Persuasion") ///
        ring(0) pos(3) fcolor(white) ///
        region(lcolor(black) lwidth(0.2) fcolor(white)) ///
        size(medsmall) ///
    ) ///




graph export "${overleaf}/figures/fig_main_treatment_effects_sm_v001.pdf", as(pdf) replace


/* *-------------------------------
* 3. Coefplot v002
*-------------------------------

ereturn list
* Option 1: List all coefficients in the Results window (transposed for readability)

* Option 2: Use the coeflegend option to see how to refer to them
suest, coeflegend

* Get the number of models to loop over
local n_models : word count `models'

* Define the model names (must match suest equations) and their display titles
local models model_z_motivation model_z_costbenefits model_z_selfefficacy model_z_awareness model_z_phone_better
local titles "Motivation" "Cost-Benefits" "Self-Efficacy" "Awareness" "Better/Worse"
	

* MOTIVATION
coefplot ///
	(all, keep(model_z_motivation_mean:1.T) offset(-0.01) /// ///
		mcolor(maroon) msymbol(O) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(maroon) lpattern(solid))) ///
	(all, keep(model_z_motivation_mean:2.T)       offset(0) /// ///
		mcolor(gs8) msymbol(S) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(gs8) lpattern(solid))) ///
	(all, keep(model_z_motivation_mean:3.T) offset(0.01) /// ///
		mcolor(navy) msymbol(T) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(navy) lpattern(solid))), ///
	xtitle("Treatment Effect") ///
	xmtick(##2) ///
	xlabel(-0.3(0.1)0.5) ///
    mlabposition(1) ///
    mlabel(string(@b, "%9.2fc")) ///
    mlabsize(small) ///
	xline(0, lpattern(dash) lcolor(gs8) lwidth(0.4)) ///
	legend(off) ///
	ysize(2) ///
	xsize(3.5) ///
	title("{bf:Motivation}") ///
	grid(none) ///
	xsc(r(-0.1 0.6)) ///
	ylabel(none) yscale(noline) ///
	name(plot_motivation, replace) 
	
* COST BENEFITS
coefplot ///
	(all, keep(model_z_costbenefits_mean:1.T) offset(-0.1) /// ///
		mcolor(maroon) msymbol(O) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(maroon) lpattern(solid))) ///
	(all, keep(model_z_costbenefits_mean:2.T)       offset(0) /// ///
		mcolor(gs8) msymbol(S) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(gs8) lpattern(solid))) ///
	(all, keep(model_z_costbenefits_mean:3.T) offset(0.1) /// ///
		mcolor(navy) msymbol(T) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(navy) lpattern(solid))), ///
	xtitle("Treatment Effect") ///
	xmtick(##2) ///
		xlabel(-0.3(0.1)0.5) ///
    mlabposition(1) ///
    mlabel(string(@b, "%9.2fc")) ///
    mlabsize(small) ///
	xline(0, lpattern(dash) lcolor(gs8) lwidth(0.4)) ///
	legend(off) ///
		ysize(2) ///
	xsize(3.5) ///
	title("{bf:Cost-Benefits}") ///
	grid(none) ///
	xsc(r(-0.1 0.6)) ///
	ylabel(none) yscale(noline) ///
	name(plot_costbenefits, replace) 
	
*AWARENESS
coefplot ///
	(all, keep(model_z_awareness_mean:1.T) offset(-0.1) /// ///
		mcolor(maroon) msymbol(O) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(maroon) lpattern(solid))) ///
	(all, keep(model_z_awareness_mean:2.T)       offset(0) /// ///
		mcolor(gs8) msymbol(S) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(gs8) lpattern(solid))) ///
	(all, keep(model_z_awareness_mean:3.T) offset(0.1) /// ///
		mcolor(navy) msymbol(T) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(navy) lpattern(solid))), ///
	xtitle("Treatment Effect") ///
	xmtick(##2) ///
		xlabel(-0.3(0.1)0.5) ///
    mlabposition(1) ///
    mlabel(string(@b, "%9.2fc")) ///
    mlabsize(small) ///
		ysize(2) ///
	xsize(3.5) ///
	xline(0, lpattern(dash) lcolor(gs8) lwidth(0.4)) ///
	legend(off) ///
	title("{bf:Awareness}") ///
	grid(none) ///
	xsc(r(-0.1 0.6)) ///
	ylabel(none) yscale(noline) ///
	name(plot_awareness, replace) 
	
coefplot ///
	(all, keep(model_z_phone_better_mean:1.T) offset(-0.1) /// ///
		mcolor(maroon) msymbol(O) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(maroon) lpattern(solid))) ///
	(all, keep(model_z_phone_better_mean:2.T)       offset(0) /// ///
		mcolor(gs8) msymbol(S) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(gs8) lpattern(solid))) ///
	(all, keep(model_z_phone_better_mean:3.T) offset(0.1) /// ///
		mcolor(navy) msymbol(T) msize(2.5) ///
		ciopts(recast(rcap) lwidth(0.75) lcolor(navy) lpattern(solid))), ///
	xtitle("Treatment Effect") ///
	xmtick(##2) ///
		xlabel(-0.3(0.1)0.5) ///
    mlabposition(1) ///
    mlabel(string(@b, "%9.2fc")) ///
    mlabsize(small) ///
	xline(0, lpattern(dash) lcolor(gs8) lwidth(0.4)) ///
	title("{bf:Better/Worse}") ///
	grid(none) ///
		ysize(2) ///
	xsize(3.5) ///
	xsc(r(-0.1 0.6)) ///
	ylabel(none) yscale(noline) ///
	legend( ///
        label(2 "Change Talk") ///
        label(4 "Decisional Balance") ///
		label(6 "Persuasion") ///
        region(lcolor(black) lwidth(0.1)) ///
        size(small) ///
		ring(0) pos(4) ///
    ) name(plot_better_worse, replace) 
	 */

// graph combine ///
//     plot_motivation plot_costbenefits ///
//     plot_awareness plot_better_worse, ///
//     cols(2) ///
//     imargin(0 0 0 0)
//	
// graph export "${overleaf}/figures/fig_main_treatment_effects_sm_v002.pdf", as(pdf) replace
