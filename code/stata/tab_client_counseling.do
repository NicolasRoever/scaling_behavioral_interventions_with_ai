*===============================================================================
*  Overleaf Regression Tables - Main Effects (Split Tables)
*===============================================================================

* Add Controls
do 00_setup

* Load data
use "${data_folder}/processed/main_social_media/clean_data.dta", clear

* Clear old estimates
eststo clear

*-------------------------------
* 1a. First table: Mechanism outcomes (non-minutes)
*-------------------------------
local outcomes mi_help_talk_change mi_make_talk_unwanted mi_discuss_need_change mi_discuss_pros_cons mi_argue_change mi_feel_hopeful_change mi_partner_in_change mi_recognize_need_change mi_tell_what_to_do mi_confident_change mi_act_authority mi_feel_pressured_change
	
	
	
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

/*
esttab * , se b(3) nobase noomitted drop($controls _cons) label starlevels(* 0.10 ** 0.05 *** 0.01) mtitles("Help" "Unwanted Talk" "Discuss Need" "Pros/Cons" "Argue Change" "Hopeful" "Recognize" "Partner in Change" "Tell What to Do" "Confidence" "Authority" "Pressure" ) coeflabel(1.T "Change Talk (a)" 2.T "Ambivalence (b)" 3.T "Persuasion (c)") stats(N r2 controlmean controls p_amb_cha p_cha_per p_amb_per, fmt(%9.0fc %9.3f %9.3f %9.3f %9.3f %9.3f %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: a=b" "p-value: a=c" "p-value: b=c"))  
*/



*-------------------------------
* 2a. Coefplot
*-------------------------------


eststo clear
foreach y of local outcomes {
    reg `y' i.T $controls
    eststo m_`y'
}
suest m_mi_help_talk_change m_mi_discuss_need_change ///
m_mi_discuss_pros_cons ///
m_mi_feel_hopeful_change ///
m_mi_recognize_need_change ///
m_mi_partner_in_change ///
m_mi_confident_change ///
m_mi_tell_what_to_do ///
m_mi_feel_pressured_change ///
m_mi_argue_change ///
m_mi_act_authority ///
m_mi_make_talk_unwanted ///
, r ///

est sto all

coefplot ///
    (all, keep(*:1.T) ///
        offset(0.25) ///
        mcolor(maroon) msymbol(O) msize(2) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(maroon) lpattern(solid))) ///
	(all, keep(*:2.T) ///
        offset(0) ///
        mcolor(gs8) msymbol(S) msize(2) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(gs8) lpattern(solid))) ///
	(all, keep(*:3.T) ///
        offset(-0.25) ///
        mcolor(navy) msymbol(T) msize(2) ///
        ciopts(recast(rcap) lwidth(0.75) lcolor(navy) lpattern(solid))), ///
    swapnames label ///
	  coeflabel( ///
m_mi_help_talk_change_mean      = "Help talk about behavior change" ///
m_mi_discuss_need_change_mean   = "Discuss need for behavior change" ///
m_mi_discuss_pros_cons_mean     = "Discuss pros and cons of behavior" ///
m_mi_feel_hopeful_change_mean   = "Feel hopeful about change" ///
m_mi_partner_in_change_mean     = "Act as a partner in change" ///
m_mi_recognize_need_change_mean = "Recognize need for change" ///
m_mi_confident_change_mean      = "Feel confident about change" ///
m_mi_argue_change_mean          = "Argue for behavior change" ///
m_mi_tell_what_to_do_mean       = "Tell you what to do" ///
m_mi_make_talk_unwanted_mean    = "Make you discuss unwanted topics" ///
m_mi_act_authority_mean         = "Act as an authority" ///
m_mi_feel_pressured_change_mean = "Feel pressured to change", ///
		     wrap(20) labsize(small) ///
    ) ///
    xtitle("Treatment effect (in standard deviations)", ) ///
    xmtick(##2)  ///
	ysize(6) ///
	xsize(8) ///
    grid(between glcolor(gs10) glwidth(medthick)) ///
	    legend( ///
        label(2 "Change Talk") ///
        label(4 "Decisional Balance") ///
		label(6 "Direct Persuasion") ///
		ring(0) pos(4) ///
        region(lcolor(black) lwidth(0.1) fcolor(white)) ///
        size(small) ///
    ) ///
	 xline(0, lpattern(dash) lcolor(gs8) lwidth(0.4)) ///
     xlab(-0.5(0.5)3)
		

graph export "${overleaf}/figures/fig_client_counseling.pdf", replace
