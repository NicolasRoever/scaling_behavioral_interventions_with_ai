*===============================================================================
*  Overleaf Regression Tables - Main Effects (Split Tables)
*===============================================================================

* Add Controls
do 00_setup

* Load data
clear all
use "${data_folder}/processed/main_social_media/clean_data.dta", clear

rename posterior_* p_*

local apps tiktok instagram snapchat facebook youtube reddit twitter

foreach y of local apps {
    summ p_app_use_plan_`y' if control & `y'_use_dummy==1, de
    gen z_p_app_use_plan_`y' = (p_app_use_plan_`y' - r(mean)) / r(sd)
}


* Run regressions and store with custom stats
eststo clear
foreach y of local apps {
    eststo: reg z_p_app_use_plan_`y' i.T $controls if `y'_use_dummy==1, r
    
    * Add control mean
    qui summ z_p_app_use_plan_`y' if control & `y'_use_dummy==1
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

esttab * , se b(3) nobase noomitted drop($controls _cons) label starlevels(* 0.10 ** 0.05 *** 0.01) mtitles("TikTok" "Instagram" "Snapchat" "Facebook" "YouTube" "Reddit" "Twitter") coeflabel(1.T "Change Talk (a)" 2.T "Decisional Balance (b)" 3.T "Persuasion (c)") stats(N r2 controlmean controls p_amb_cha p_cha_per p_amb_per, fmt(%9.0fc %9.3f %9.3f %9.3f %9.3f %9.3f %9.3f) labels("Observations" "R\textsuperscript{2}" "Control group mean" "Controls" "p-value: a=b" "p-value: a=c" "p-value: b=c")) 



*-------------------------------
* Coefplot
*-------------------------------

eststo clear
foreach y of local apps {
    reg z_p_app_use_plan_`y' i.T $controls if `y'_use_dummy==1
    eststo m_`y'
}

suest m_tiktok m_instagram m_snapchat m_facebook m_youtube m_reddit m_twitter, r
est sto all


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
m_tiktok_mean = "TikTok" ///
m_instagram_mean = "Instagram" ///
 m_snapchat_mean = "Snapchat" ///
 m_facebook_mean = "Facebook" ///
 m_youtube_mean = "YouTube" ///
 m_reddit_mean = "Reddit" ///
 m_twitter_mean = "Twitter/X", ///
		     wrap(15) labsize(medsmall) ///
    ) ///
    xtitle("Treatment effect (in standard deviations)") ///
    xmtick(##2)  ///
	ysize(6) ///
	xsize(9) ///
    xlab(-0.8(0.2)0.2, labsize(medsmall)) ///
    grid(between glcolor(gs10) glwidth(medthick)) ///
	    legend( ///
        label(2 "Change Talk") ///
        label(4 "Decisional Balance") ///
		label(6 "Direct Persuasion") ///
		ring(1) pos(3) ///
        fcolor(white) region(lcolor(black) lwidth(0.1)) ///
        size(medsmall) ///
    ) ///
	 xline(0, lpattern(dash) lcolor(gs8) lwidth(0.4)) sort
		

graph export "${overleaf}/figures/fig_app_use_effects.pdf", replace


