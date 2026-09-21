********************************************************************************
* Project: MI SOCIAL MEDIA
* Purpose: Prior/posterior proportions reporting exactly 30 minutes, by arm
*          Four individual figures and a combined 2-by-2 panel
********************************************************************************

version 17
clear all
set more off

* Run from the project's Stata directory.
do 00_setup.do
use "${data_folder}/processed/main_social_media/clean_merged_with_scrshots.dta", clear
* Save all manuscript figures using the destination configured in 00_setup.do.
local output_dir "${overleaf}/figures"

* Use raw minutes: winsorized values can create artificial mass points.
* Each outcome has its own denominator of nonmissing responses within each arm.
keep if inlist(T, 0, 1, 2, 3)

* The prior counterpart to posterior predicted use is baseline actual use.
* Keep this distinction explicit in the figure titles and filenames.
local outcomes baseline_actual_social_min baseline_ideal_social_min ///
    posterior_actual_social_min posterior_ideal_social_min
local graph_names prior_actual_30 prior_ideal_30 ///
    posterior_predicted_30 posterior_ideal_30 
local file_stems prior_actual prior_ideal posterior_predicted posterior_ideal 
local title1 "Prior actual time: exactly 30 minutes"
local title2 "Prior ideal time: exactly 30 minutes"
local title3 "Posterior predicted time: exactly 30 minutes"
local title4 "Posterior ideal time: exactly 30 minutes"

forvalues panel_index = 1/4 {
    local outcome : word `panel_index' of `outcomes'
    local graph_name : word `panel_index' of `graph_names'
    local file_stem : word `panel_index' of `file_stems'
    local panel_letter = char(64 + `panel_index')
    local graph_title "`panel_letter'. `title`panel_index''"

    tempvar exactly30
    generate byte `exactly30' = (`outcome' == 30) if !missing(`outcome')

    * Report denominators and proportions in the Stata output as well.
    display "`graph_title'"
    tabstat `exactly30', by(T) statistics(n mean) format(%9.3f)

    preserve
    collapse (mean) `exactly30', by(T)
    twoway (bar `exactly30' T, barwidth(0.6) color(maroon)) ///
        (scatter `exactly30' T, msymbol(none) mlabel(`exactly30') ///
            mlabformat(%4.3f) mlabposition(12) mlabcolor(black) mlabsize(small)), ///
        xlabel(0 "Control" 1 `""Change" "Talk""' ///
            2 `""Decisional" "Balance""' 3 `""Direct" "Persuasion""', ///
            labsize(small) noticks nogrid) ///
        xtitle("") xscale(range(-0.5 3.5)) ///
        ytitle("Proportion of respondents") ///
        ylabel(0(0.05)0.30, angle(horizontal) format(%4.2f)) ///
        yscale(range(0 0.30)) ///
        title("{bf:`graph_title'}", size(medsmall)) ///
        legend(off) graphregion(color(white)) xsize(8) ysize(5) ///
        name(`graph_name', replace)

    restore
    drop `exactly30'
}

* Rows: prior then posterior. Columns: actual/predicted use then ideal use.
graph combine prior_actual_30 prior_ideal_30 ///
    posterior_predicted_30 posterior_ideal_30, ///
    cols(2) ycommon iscale(0.5) graphregion(color(white)) ///
    xsize(12) ysize(8) name(prior_posterior_30_panel, replace)
graph export "`output_dir'/fig_prior_posterior_exactly_30_panel.pdf", replace
