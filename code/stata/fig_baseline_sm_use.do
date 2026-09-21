* Load data
clear all
use "${data_folder}/processed/main_social_media/clean_data.dta", clear

* ---------------------------------------------------------
* Prepare Data
* ---------------------------------------------------------


* Calculate the raw mean and the 95th percentile before truncating the graph
summarize baseline_actual_social_min, detail
local raw_mean_val = r(mean)
local p95_val = r(p95)

* Omit observations above the raw distribution's 95th percentile from the graph
drop if baseline_actual_social_min > `p95_val'

* Calculate the mean and median of the observations displayed in the graph
summarize baseline_actual_social_min, detail
local displayed_mean_val = r(mean)
local displayed_med_val = r(p50)

* Format the statistics for display
local raw_mean_str : di %3.0f `raw_mean_val'
local displayed_mean_str : di %3.0f `displayed_mean_val'
local displayed_med_str : di %3.0f `displayed_med_val'

* ---------------------------------------------------------
* Plot Histogram
* ---------------------------------------------------------

histogram baseline_actual_social_min , ///
    width(30) /// 
    xtitle("Self-reported daily social media use (minutes)") ///
    ytitle("Density") ///
    fcolor(maroon) lcolor(black) ///
    xline(`raw_mean_val', lcolor(black) lpattern(dash)) ///
    note("{bf:Full-sample raw mean: `raw_mean_str' minutes}" ///
         "{bf:Mean of observations shown: `displayed_mean_str' minutes}" ///
         "{bf:Median of observations shown: `displayed_med_str' minutes}", ///
         ring(0) pos(3) size(small))

* Export merged graph
graph export "${overleaf}/figures/fig_hst_baseline_sm_use.pdf", replace
