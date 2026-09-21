*===============================================================================
* Figure: Binned Scatter - Actual vs Ideal Social Media Time
*===============================================================================

* Load data
use "${data_folder}/processed/main_social_media/clean_data.dta", clear

* Convert to hours
gen baseline_actual_social_h = baseline_actual_social_min / 60.0
gen baseline_ideal_social_h = baseline_ideal_social_min / 60.0

* Calculate gap and correlation
cap drop gap
gen gap = baseline_actual_social_h - baseline_ideal_social_h 
summ gap, de
local mean_gap : di %5.2f r(mean)

pwcorr baseline_actual_social_h baseline_ideal_social_h , sig
local corr = string(r(rho), "%5.2f")


* Binned scatterplot - limit axis range to data
binscatter baseline_ideal_social_h  baseline_actual_social_h, ///
    color(maroon) ///
    xlab(0(1)8, nogrid) ylab(0(1)8, nogrid) ///
    xsize(3) ysize(3) legend(off) ///
    xtitle("Actual social media time (hours)") ///
    ytitle("Ideal social media time (hours)") ///
    linetype(none) msymbol(O) xmtick(##5) ymtick(##5) ///
    text(1.8 6.6 "Mean Gap: `mean_gap' hours", size(small)) ///
    text(1.3 6.6 "Correlation: `corr'", size(small)) ///
    xscale(range(0 8)) yscale(range(0 8))
	
	
* Create diagonal points for 45-degree line
cap drop xx yy
gen xx = .
gen yy = .
replace xx = 0.5 in 1
replace yy = 0.5 in 1
replace xx = 5.5 in 2
replace yy = 5.5 in 2
* Add 45-degree line and linear fit
graph addplot line xx yy, lcolor(black) lwidth(0.3) lpattern(dash)



* Export
graph export "${overleaf}/figures/fig_actual_vs_ideal_social_time_binned.pdf", replace
