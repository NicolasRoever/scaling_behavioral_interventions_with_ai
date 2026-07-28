*===============================================================================
* Figure Mechanism Question Effects
*===============================================================================


* Add Controls
do 00_setup

* Load data
clear all

use "${data_folder}/processed/main_social_media/clean_merged.dta", clear


*-------------------------------
* Run Regression
*-------------------------------

rename (w2_mechanism_reduce_phone w2_mechanism_curate_feed w2_mechanism_replace_act w2_mechanism_willpower) (w2_msm_reduce_phone w2_msm_curate_feed w2_msm_replace_act w2_msm_willpower)

local mechanisms ///
    w2_mechanism_settings ///
    w2_mechanism_blocker ///
    w2_mechanism_notif ///
    w2_mechanism_friction ///
    w2_mechanism_delete ///
    w2_mechanism_rules ///
    w2_mechanism_reach ///
    w2_msm_reduce_phone ///
    w2_msm_curate_feed ///
    w2_msm_replace_act ///
    w2_mechanism_help ///
    w2_msm_willpower ///
    w2_mechanism_other ///
    w2_mechanism_none
	
	
eststo clear
foreach y of local mechanisms {
    reg `y' i.T $controls_followup
    eststo model_`y'
}

* Combine estimates using suest
suest model_w2_mechanism_settings ///
      model_w2_mechanism_blocker ///
      model_w2_mechanism_notif ///
      model_w2_mechanism_friction ///
      model_w2_mechanism_delete ///
      model_w2_mechanism_rules ///
      model_w2_mechanism_reach ///
      model_w2_msm_reduce_phone ///
      model_w2_msm_curate_feed ///
      model_w2_msm_replace_act ///
      model_w2_mechanism_help ///
      model_w2_msm_willpower ///
      model_w2_mechanism_other ///
      model_w2_mechanism_none, r

* Store the combined results
est sto all

*-------------------------------
* Coefplot
*-------------------------------

coefplot ///
    (all, keep(*:1.T) ///
        offset(0.2) ///
        mcolor(maroon) msymbol(O) msize(1.2) ///
        ciopts(recast(rcap) lwidth(0.4) lcolor(maroon) lpattern(solid))) ///
	(all, keep(*:2.T) ///
        offset(0) ///
        mcolor(gs8) msymbol(S) msize(1.2) ///
        ciopts(recast(rcap) lwidth(0.4) lcolor(gs8) lpattern(solid))) ///
	(all, keep(*:3.T) ///
        offset(-0.2) ///
        mcolor(navy) msymbol(T) msize(1.2) ///
        ciopts(recast(rcap) lwidth(0.4) lcolor(navy) lpattern(solid))), ///
    swapnames label ///
	  coeflabel( ///
		 model_w2_mechanism_settings_mean  =     "Built-in phone settings" ///
    model_w2_mechanism_blocker_mean    =  "Third-party app blocker" ///
    model_w2_mechanism_notif_mean       =   "Turned off/muted notifications" ///
    model_w2_mechanism_friction_mean     =  "Made access harder" ///
    model_w2_mechanism_delete_mean       =  "Deleted/uninstalled apps" ///
    model_w2_mechanism_rules_mean        = "Set specific rules/goals" ///
    model_w2_mechanism_reach_mean       =  "Put phone out of reach" ///
    model_w2_msm_reduce_phone_mean =   "Reduced overall phone use" ///
    model_w2_msm_curate_feed_mean =    "Changed feed content" ///
    model_w2_msm_replace_act_mean =    "Replaced with other activities" ///
    model_w2_mechanism_help_mean =      "Asked for help/accountability" ///
    model_w2_msm_willpower_mean =      "Relied on willpower" ///
    model_w2_mechanism_other_mean =        "Other strategy" ///
    model_w2_mechanism_none_mean =          "No steps taken",  ///
		     wrap(30) labsize(small) ///
    ) ///
    xtitle("Treatment effects", size(small)) ///
    xmtick(##2)  ///
	ysize(8) ///
	xsize(12) ///
    xlab(-0.15(0.05)0.2, labsize(small)) ///
    grid(between glcolor(gs10) glwidth(medthick)) ///
	    legend( ///
        label(2 "Change Talk") ///
        label(4 "Decisional Balance") ///
		label(6 "Direct Persuasion") ///
		ring(0) pos(3) ///
        region(lcolor(black) lwidth(0.1) fcolor(white)) ///
        size(small) ///
    ) ///
	 xline(0, lpattern(dash) lcolor(gs10) lwidth(0.35)) sort
		

graph export "${overleaf}/figures/fig_sm_followup_mechanisms.pdf", replace
