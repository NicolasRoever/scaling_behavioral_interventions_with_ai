* Joint tests on the currently loaded, cleaned experimenter-demand sample.
* Pass controls explicitly. Optional CSV records exact test statistics.
args baseline_controls output_csv
tempname results
if `"`output_csv'"' != "" {
    postfile `results' str32 outcome int n_identified n_not_identified ///
        double chi2 p using "`output_csv'.dta", replace
}
foreach outcome in z_motivation z_costbenefits {
    eststo clear
    eststo identified: regress `outcome' ib0.T `baseline_controls' if predict_reduction == 1
    local n_identified = e(N)
    eststo not_identified: regress `outcome' ib0.T `baseline_controls' if predict_reduction == 0
    local n_not_identified = e(N)
    esttab not_identified identified, se b(3) ///
        starlevels(* 0.10 ** 0.05 *** 0.01) nobase noomitted label keep(*T)
    quietly suest identified not_identified, vce(robust)
    test ([identified_mean]1.T = [not_identified_mean]1.T) ///
         ([identified_mean]2.T = [not_identified_mean]2.T) ///
         ([identified_mean]3.T = [not_identified_mean]3.T)
    local chi2 = r(chi2)
    local p = r(p)
    display as text "Demand subgroup joint test for `outcome': p = " as result %9.6f `p'
    if `"`output_csv'"' != "" ///
        post `results' ("`outcome'") (`n_identified') (`n_not_identified') (`chi2') (`p')
}
if `"`output_csv'"' != "" {
    postclose `results'
    preserve
    use "`output_csv'.dta", clear
    export delimited using "`output_csv'", replace
    restore
    erase "`output_csv'.dta"
}
