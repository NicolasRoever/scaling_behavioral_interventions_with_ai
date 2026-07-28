* Load data
clear all
use "${data_folder}/processed/main_social_media/clean_data.dta", clear

* ---------------------------------------------------------
* Prepare Data
* ---------------------------------------------------------


* Drop data above 95th percentile of social_hours

* Calculate statistics (including percentiles)
summarize baseline_actual_social_min, detail

* Drop if value is greater than the 95th percentile stored in r(p95)
drop if baseline_actual_social_min > r(p95)

* 2. Calculate Mean and Median
summarize baseline_actual_social_min, detail
local mean_val = r(mean)
local med_val  = r(p50)

* 3. Format them for display (2 decimal places)
local mean_str : di %3.0f `mean_val'
local med_str  : di %3.0f `med_val'

* ---------------------------------------------------------
* Plot Histogram
* ---------------------------------------------------------

histogram baseline_actual_social_min , ///
    width(30) /// 
    xtitle("Self-reported daily social media use (minutes)") ///
    ytitle("Density") ///
    fcolor(maroon) lcolor(black) ///
    note("{bf:Mean: `mean_str' minutes}" "{bf:Median: `med_str' minutes}", ring(0) pos(3) size(small))

* Export merged graph
graph export "${overleaf}/figures/fig_hst_baseline_sm_use.pdf", replace
