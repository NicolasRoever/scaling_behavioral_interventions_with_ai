********************************************************************************
* Project: MI SOCIAL MEDIA
* Purpose: Cross-sectional mapping from perceived social-media costs to WTP
********************************************************************************

version 17
clear all
set more off

do 00_setup.do
use "${data_folder}/processed/main_social_media/clean_data.dta", clear

* Both measures were collected only after treatment. These regressions therefore
* describe conditional cross-sectional associations, not changes or mediation.
local outcome wtp_dollars
local perceived_cost_index z_costbenefits

eststo clear

* Pooled sample: condition on randomized treatment assignment and baseline controls.
eststo pooled: regress `outcome' `perceived_cost_index' i.T $controls, vce(robust)
quietly summarize `outcome' if e(sample)
estadd scalar outcome_mean = r(mean)
estadd local baseline_controls "Yes"
estadd local treatment_indicators "Yes"

* Control group: association in the absence of an active treatment.
eststo control_group: regress `outcome' `perceived_cost_index' $controls ///
    if control == 1, vce(robust)
quietly summarize `outcome' if e(sample)
estadd scalar outcome_mean = r(mean)
estadd local baseline_controls "Yes"
estadd local treatment_indicators "No"

esttab pooled control_group, ///
    se b(3) ///
    keep(`perceived_cost_index') ///
    label ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("Pooled sample" "Control group") ///
    coeflabel(`perceived_cost_index' "Perceived costs (std.)") ///
    stats( ///
        N r2 outcome_mean baseline_controls treatment_indicators, ///
        fmt(%9.0fc %9.3f %9.3f %9s %9s) ///
        labels( ///
            "Observations" ///
            "R\textsuperscript{2}" ///
            "Mean WTP (\\$)" ///
            "Baseline controls" ///
            "Treatment indicators" ///
        ) ///
    )

esttab pooled control_group using ///
    "${overleaf}/tables/tab_wtp_perceived_cost_mapping.tex", ///
    se b(3) ///
    keep(`perceived_cost_index') ///
    label ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("Pooled sample" "Control group") ///
    coeflabel(`perceived_cost_index' "Perceived costs (std.)") ///
    stats( ///
        N r2 outcome_mean baseline_controls treatment_indicators, ///
        fmt(%9.0fc %9.3f %9.3f %9s %9s) ///
        labels( ///
            "Observations" ///
            "R\textsuperscript{2}" ///
            "Mean WTP (\\$)" ///
            "Baseline controls" ///
            "Treatment indicators" ///
        ) ///
    ) ///
    booktabs fragment replace
