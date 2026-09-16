* Optional argument: exhibit root containing figures/ and tables/ directories.
version 17
args output_root
do 00_setup.do
if `"`output_root'"' == "" local output_root "${overleaf}"
do "${code_folder}/Helpers/load_expdemand_data.do" "${data_folder}"

* Duplicate observations only inside preserve to add the pooled distribution.
* Percentages sum to 100 within each arm (and separately within the full sample).
preserve
keep if !missing(llm_category_expdemand)
generate byte arm = T + 1
expand 2, generate(pooled)
replace arm = 0 if pooled
contract arm llm_category_expdemand, zero
bysort arm: egen denominator = total(_freq)
generate percent = 100 * _freq / denominator
bysort arm: egen percent_sum = total(percent)
assert abs(percent_sum - 100) < 1e-8
keep arm llm_category_expdemand percent
reshape wide percent, i(llm_category_expdemand) j(arm)

* Share category labels and styling across the two exhibits.
local graph_options ///
    over(llm_category_expdemand, label(labsize(small))) ///
    blabel(bar, format(%9.1f) size(small)) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(none)) ///
    intensity(100) lintensity(100)

* Original pooled figure: retain its filename and maroon bars.
graph hbar (asis) percent0, `graph_options' ///
    bar(1, color(maroon)) legend(off) ///
    ytitle("Frequency (%)", size(medium)) ///
    ylab(, nogrid glwidth(none)) ///
    xsize(8) ysize(5) name(expdemand_overall, replace)
graph export "`output_root'/figures/fig_llm_exp_demand.pdf", replace

restore
