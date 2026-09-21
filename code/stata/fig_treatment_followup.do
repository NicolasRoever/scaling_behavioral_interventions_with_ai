*===============================================================================
*  Regressions Main Effects
*===============================================================================


* Add Controls
do 00_setup

* Load data
clear all

use "${data_folder}/processed/main_social_media/clean_merged.dta", clear


*-------------------------------
* 1a. First table: Mechanism outcomes (non-minutes)
*-------------------------------
rename w2_z_smart_bett_wors_revers makes_worse
local outcomes w2_z_motivation w2_z_costbenefits makes_worse
* Run regressions and store with custom stats
eststo clear
foreach y of local outcomes {
    reg `y' i.T $controls_followup
    eststo model_`y'
}

suest model_w2_z_motivation model_w2_z_costbenefits model_makes_worse , r
est sto all

*-------------------------------
* 3. Coefplot v001
*-------------------------------
ereturn list

* for nicer vertical lines
cap drop xx yy
gen xx=.
gen yy=.
replace xx=0 in 1
replace yy=0.9 in 1
replace xx=0 in 2
replace yy=2.5 in 2

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
	  model_w2_z_motivation_mean  = "Motivation " ///
       model_w2_z_costbenefits_mean = "Perceived costs of social media" ///
	   model_makes_worse_mean = "Social media makes life worse", ///
        wrap(15) labsize(medsmall) ///
    ) ///
    xtitle("Treatment effect (in standard deviations)") ///
    xmtick(##2) xlab(-0.2(0.1)0.5, labsize(medsmall))  ///
	ysize(6) ///
	xsize(8) ///
    mlabposition(12) ///
    mlabel(string(@b, "%9.2fc")) ///
    mlabsize(small) ///
      grid(between glcolor(gs10) ) ///
	    legend( ///
        label(2 "Change Talk") ///
        label(4 "Decisional Balance") ///
		label(6 "Direct Persuasion") ///
        ring(0) pos(4) ///
        region(lcolor(black) lwidth(0.1)) ///
        size(small) ///
    ) ///
	 xline(0, lpattern(dash) lcolor(gs8) lwidth(0.4) noextend) 




graph export "${overleaf}/figures/fig_main_treatment_effects_sm_followup_v001.pdf", as(pdf) replace
