*===============================================================================
* Change Questionnaire ~ Treatment + Controls (only want_change) + Coefplot
*===============================================================================

do 00_setup

* Load data
use "${data_folder}/processed/main_social_media/clean_data.dta", clear


*-------------------------------
* 1a. First table: Mechanism outcomes (non-minutes)
*-------------------------------
local mechanisms CQ_want_change CQ_could_change CQ_good_reasons CQ_have_to_reduce CQ_intend_to_reduce CQ_trying_to_reduce


reg CQ_want_change i.T

* Run regressions and store with custom stats
eststo clear
foreach y of local mechanisms {
    reg `y' i.T $controls, r
    eststo `y'
    
    * Add control mean
    qui summ `y' if control
    estadd scalar controlmean = r(mean)
    
    * Add controls indicator
    estadd local controls "Yes"
	
	*Add tests
	test 1.T = 2.T
    estadd scalar p_12 = r(p)
	
	test 2.T = 3.T
    estadd scalar p_23 = r(p)
	
	test 1.T = 3.T
    estadd scalar p_13 = r(p)
}

*-------------------------------
* 2a. Export mechanisms table with p-values
*-------------------------------
esttab * , se b(3) keep(*T) nobase noomitted label starlevel(* 0.1 ** 0.05 *** 0.01)

esttab `mechanisms' ///
       using "${overleaf}/tables/tab_sm_change.tex", ///
       cells(b(fmt(3) star) se(fmt(3) par)) ///
       starlevels(* 0.10 ** 0.05 *** 0.01) ///
	   coeflabel("Ambivalence (a)" "Decisional Balance (b)" "Direct Persuasion (c)") ///
       stats(N r2 controlmean controls p_12 p_13 p_23, ///
             fmt(%9.0f %9.3f %9.3f %9s %9.3f %9.3f %9.3f) ///
             labels("Observations" "R-squared" "Control mean" "Controls" "p-value a=b" "p-value a=c" "p-value c=b")) ///
       keep(1.T 2.T 3.T) ///
       label nobase noomitted ///
       mtitles("Want Change" "Could Change" "Good Reasons" "Have to Reduce" "Intent Reduce" "Try Reduce") ///
       booktabs fragment replace 

	   
	   
*-------------------------------
* 3. Coefplot 
*-------------------------------

eststo clear
foreach y of local mechanisms {
    reg `y' i.T $controls
    eststo model_`y'
}

suest model_CQ_want_change model_CQ_could_change model_CQ_good_reasons model_CQ_have_to_reduce model_CQ_intend_to_reduce model_CQ_trying_to_reduce, r
est sto all

ereturn list

coefplot ///
    (all, keep(*:1.T) ///
        offset(0.2) ///
        mcolor(maroon) msymbol(O) msize(2) ///
        ciopts(recast(rcap) lwidth(0.6) lcolor(maroon) lpattern(solid))) ///
	(all, keep(*:2.T) ///
        offset(0) ///
        mcolor(gs8) msymbol(S) msize(2) ///
        ciopts(recast(rcap) lwidth(0.6) lcolor(gs8) lpattern(solid))) ///
	(all, keep(*:3.T) ///
        offset(-0.2) ///
        mcolor(navy) msymbol(T) msize(2) ///
        ciopts(recast(rcap) lwidth(0.6) lcolor(navy) lpattern(solid))), ///
    swapnames label ///
	  coeflabel( ///
		model_CQ_want_change_mean = "Want change" ///
		model_CQ_could_change_mean="Could change" ///
		model_CQ_good_reasons_mean = "Good reasons" ///
		model_CQ_have_to_reduce_mean = "Have to reduce" /// 
		model_CQ_intend_to_reduce_mean = "Intent to reduce" ///
		model_CQ_trying_to_reduce_mean = "Try to reduce", ///
		     wrap(10) labsize(medsmall) ///
    ) ///
    xtitle("Treatment effect (in standard deviations)") ///
    xmtick(##2)  ///
	ysize(6) ///
	xsize(9) ///
    xlab(-0.2(0.2)0.8, labsize(small)) ///
    grid(between glcolor(gs10) glwidth(medthick)) ///
	    legend( ///
        label(2 "Change Talk") ///
        label(4 "Decisional Balance") ///
		label(6 "Direct Persuasion") ///
		ring(1) pos(3) ///
        region(lcolor(black) lwidth(0.1) fcolor(white)) ///
        size(small) ///
    ) ///
	 xline(0, lpattern(dash) lcolor(gs8) lwidth(0.4) noextend) 
		

graph export "${overleaf}/figures/fig_change_questionnaire.pdf", replace

