*===============================================================================
* Companion tables for the two main treatment-effect figures
* Holm-adjusted p-values control the familywise error rate within each table.
*===============================================================================

do 00_setup
set more off

capture mata: mata drop holm_adjust()
mata:
real rowvector holm_adjust(real rowvector p)
{
    real scalar rank, hypotheses, running_max, candidate
    real colvector sorted_index
    real rowvector adjusted

    if (hasmissing(p)) {
        _error(3498, "Holm adjustment requires nonmissing p-values")
    }

    hypotheses = cols(p)
    sorted_index = order(p', 1)
    adjusted = J(1, hypotheses, .)
    running_max = 0

    for (rank = 1; rank <= hypotheses; rank++) {
        candidate = (hypotheses - rank + 1) * p[sorted_index[rank]]
        running_max = max((running_max, candidate))
        adjusted[sorted_index[rank]] = min((1, running_max))
    }

    return(adjusted)
}
end

capture program drop holm_family
program define holm_family, rclass
    version 17
    syntax, PAIRS(string) PREFIX(name)

    local outcome_count : word count `pairs'
    if `outcome_count' == 0 {
        display as error "pairs() must contain at least one outcome:controlmacro pair"
        exit 198
    }

    quietly levelsof T if !missing(T), local(all_treatment_levels)
    local treatment_levels
    foreach treatment of local all_treatment_levels {
        if `treatment' != 0 {
            local treatment_levels `treatment_levels' `treatment'
        }
    }

    local treatment_count : word count `treatment_levels'
    if `treatment_count' == 0 {
        display as error "No noncontrol treatment levels found in T"
        exit 198
    }

    local hypothesis_count = `outcome_count' * `treatment_count'
    matrix family_p_raw = J(1, `hypothesis_count', .)

    eststo clear
    local raw_models
    local outcome_index = 0

    foreach pair of local pairs {
        local ++outcome_index
        local separator = strpos("`pair'", ":")
        if `separator' <= 1 | `separator' == strlen("`pair'") {
            display as error "Invalid pair `pair'; expected outcome:controlmacro"
            exit 198
        }

        local outcome = substr("`pair'", 1, `separator' - 1)
        local controls_name = substr("`pair'", `separator' + 1, .)
        local regression_controls "${`controls_name'}"
        if `"`regression_controls'"' == "" {
            display as error "Global macro `controls_name' is empty or undefined"
            exit 198
        }

        quietly regress `outcome' i.T `regression_controls', vce(robust)
        quietly summarize `outcome' if control == 1 & e(sample)
        estadd scalar controlmean = r(mean)
        estadd local controls "Yes"

        matrix p_raw = e(b) * .
        local treatment_index = 0
        foreach treatment of local treatment_levels {
            local ++treatment_index
            local hypothesis_index = ///
                `treatment_count' * (`outcome_index' - 1) + `treatment_index'
            local coefficient `treatment'.T
            matrix family_p_raw[1, `hypothesis_index'] = ///
                2 * ttail(e(df_r), abs(_b[`coefficient'] / _se[`coefficient']))
            matrix p_raw[1, colnumb(p_raw, "`coefficient'")] = ///
                family_p_raw[1, `hypothesis_index']
        }

        estadd matrix p_raw = p_raw
        local model_name `prefix'_`outcome_index'_raw
        estimates store `model_name'
        local raw_models `raw_models' `model_name'
    }

    mata: st_matrix("family_p_holm", holm_adjust(st_matrix("family_p_raw")))

    local adjusted_models
    local outcome_index = 0
    foreach model_name of local raw_models {
        local ++outcome_index
        estimates restore `model_name'
        matrix p_holm = e(b) * .

        local treatment_index = 0
        foreach treatment of local treatment_levels {
            local ++treatment_index
            local hypothesis_index = ///
                `treatment_count' * (`outcome_index' - 1) + `treatment_index'
            local coefficient `treatment'.T
            matrix p_holm[1, colnumb(p_holm, "`coefficient'")] = ///
                family_p_holm[1, `hypothesis_index']
        }

        estadd matrix p_holm = p_holm
        local adjusted_model_name `prefix'_`outcome_index'_holm
        estimates store `adjusted_model_name'
        local adjusted_models `adjusted_models' `adjusted_model_name'
    }

    return local models `adjusted_models'
    return local treatment_levels `treatment_levels'
    return scalar hypotheses = `hypothesis_count'
    return matrix p_raw = family_p_raw
    return matrix p_holm = family_p_holm
end

*-------------------------------------------------------------------------------
* 1. Motivation, beliefs, and WTP: match fig_main_treatment_effects_sm_v001.pdf
*-------------------------------------------------------------------------------

* Only the preregistered secondary-outcome family appears in the revision.
* 3. Preregistered secondary outcomes: one joint Holm family
*-------------------------------------------------------------------------------

use "${data_folder}/processed/main_social_media/clean_data.dta", clear
rename z_smart_bett_wors_revers z_phone_rev

local apps tiktok instagram snapchat facebook youtube reddit twitter
foreach app of local apps {
    quietly summarize posterior_app_use_plan_`app' ///
        if control == 1 & `app'_use_dummy == 1
    generate z_app_expectation_`app' = ///
        (posterior_app_use_plan_`app' - r(mean)) / r(sd) ///
        if `app'_use_dummy == 1
}

local secondary_pairs ///
    z_selfefficacy:controls ///
    z_awareness:controls ///
    z_phone_rev:controls ///
    posterior_ideal_social_min_w:controls ///
    posterior_actual_social_min_w:controls ///
    wtp_dollars:controls ///
    z_app_expectation_tiktok:controls ///
    z_app_expectation_instagram:controls ///
    z_app_expectation_snapchat:controls ///
    z_app_expectation_facebook:controls ///
    z_app_expectation_youtube:controls ///
    z_app_expectation_reddit:controls ///
    z_app_expectation_twitter:controls

holm_family, pairs("`secondary_pairs'") prefix(secondary)
local secondary_models_holm `r(models)'
matrix secondary_p = r(p_raw)
matrix secondary_p_holm = r(p_holm)

local secondary_models_a
forvalues model_index = 1/6 {
    local model_name : word `model_index' of `secondary_models_holm'
    local secondary_models_a `secondary_models_a' `model_name'
}

local secondary_models_b
forvalues model_index = 7/13 {
    local model_name : word `model_index' of `secondary_models_holm'
    local secondary_models_b `secondary_models_b' `model_name'
}

esttab `secondary_models_a' ///
    using "${overleaf}/tables/tab_secondary_outcomes_holm_panel_a.tex", ///
    cells(b(star pvalue(p_holm) fmt(3)) ///
          se(par fmt(3)) ///
          p_holm(par([ ]) fmt(3))) ///
    keep(1.T 2.T 3.T) ///
    coeflabel(1.T "Change Talk" ///
              2.T "Decisional Balance" ///
              3.T "Direct Persuasion") ///
    mtitles("\makecell{Self-efficacy\\(std.)}" ///
            "\makecell{Awareness of\\self-control problems\\(std.)}" ///
            "\makecell{Social media\\makes life worse\\(std.)}" ///
            "\makecell{Ideal social\\media time (min)}" ///
            "\makecell{Predicted social\\media time (min)}" ///
            "\makecell{WTP\\(\\$)}") ///
    stats(N r2 controlmean controls, ///
          fmt(%9.0fc %9.3f %9.3f %9s) ///
          labels("Observations" ///
                 "R\textsuperscript{2}" ///
                 "Control group mean" ///
                 "Controls")) ///
    collabels(none) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    booktabs fragment replace

esttab `secondary_models_b' ///
    using "${overleaf}/tables/tab_secondary_outcomes_holm_panel_b.tex", ///
    cells(b(star pvalue(p_holm) fmt(3)) ///
          se(par fmt(3)) ///
          p_holm(par([ ]) fmt(3))) ///
    keep(1.T 2.T 3.T) ///
    coeflabel(1.T "Change Talk" ///
              2.T "Decisional Balance" ///
              3.T "Direct Persuasion") ///
    mtitles("TikTok" ///
            "Instagram" ///
            "Snapchat" ///
            "Facebook" ///
            "YouTube" ///
            "Reddit" ///
            "Twitter/X") ///
    stats(N r2 controlmean controls, ///
          fmt(%9.0fc %9.3f %9.3f %9s) ///
          labels("Observations" ///
                 "R\textsuperscript{2}" ///
                 "Control group mean" ///
                 "Controls")) ///
    collabels(none) ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    booktabs fragment replace

matrix list secondary_p
matrix list secondary_p_holm

