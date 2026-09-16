* Load data
clear all
use "${data_folder}/processed/main_social_media/clean_data.dta", clear



*1) Full Histogram

histogram time_interview_minutes, ///
    width(1) ///
    xtitle("Interview duration (minutes)") ///
    ytitle("Density") ///
    fcolor(maroon) lcolor(black)
	
	
* Export merged graph



*----------------------------------------------------------------
* 2) Histogram by Treatment with Means
*----------------------------------------------------------------

* Calculate means for each group to use in xlines or legend
summarize time_interview_minutes if control, meanonly
local m_ctrl = r(mean)

summarize time_interview_minutes if T == 1, meanonly
local m_t1 = r(mean)

summarize time_interview_minutes if T == 2, meanonly
local m_t2 = r(mean)

summarize time_interview_minutes if T == 3, meanonly
local m_t3 = r(mean)

* Format means for display (e.g., 1 decimal place)
local m_ctrl_fmt : di %3.1f `m_ctrl'
local m_t1_fmt : di %3.1f `m_t1'
local m_t2_fmt : di %3.1f `m_t2'
local m_t3_fmt : di %3.1f `m_t3'

* Plot with updated colors: gs8 (Control), navy (T1), maroon (T2), teal (T3)
twoway ///
    (kdensity time_interview_minutes if control, lcolor(gs8)    lpattern(dash) lwidth(0.55))    ///
    (kdensity time_interview_minutes if T == 1,  lcolor(navy)   lpattern(dash) lwidth(0.55))     ///
    (kdensity time_interview_minutes if T == 2,  lcolor(maroon) lpattern(solid) lwidth(0.55))      ///
    (kdensity time_interview_minutes if T == 3,  lcolor(teal)   lpattern(longdash)lwidth(0.55)), ///
    xtitle("Interview duration (minutes)", size(medium)) ///
    ytitle("Kernel Density", size(medium)) ///
    legend( ///
	region(lcolor(black) lwidth(thin)) ///
	order(1 "Control (Mean: `m_ctrl_fmt')" ///
                 2 "Change Talk (Mean: `m_t1_fmt')" ///
                 3 "Decisional Balance (Mean: `m_t2_fmt')" ///
                 4 "Direct Persuasion (Mean: `m_t3_fmt')") ///
           ring(0) pos(2) cols(1) size(medium)) ///

graph export "${overleaf}/figures/fig_density_interview_dur_by_treat.pdf", replace
