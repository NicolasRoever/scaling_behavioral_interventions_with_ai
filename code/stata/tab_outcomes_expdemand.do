********************************************************************************
* Survey 1 outcomes conditional on hypothesis identification.
* Run from the Stata code directory:
*   do tab_outcomes_expdemand.do
* Output root: ${overleaf}, configured for GUI and batch Stata in 00_setup.do.
* LaTeX fragments: ${overleaf}/tables/.
* Two-page PDF: ${overleaf}/figures/tab_outcomes_expdemand.pdf.
* PDF rendering requires Python 3 and pdflatex (MacTeX on macOS).
********************************************************************************
version 17
do 00_setup.do
local output_root "${overleaf}"
if `"`output_root'"' == "" {
    display as error "Define the overleaf macro in 00_setup.do before running this script."
    exit 198
}
capture mkdir "`output_root'"
capture mkdir "`output_root'/tables"
capture mkdir "`output_root'/figures"

* Reuse exactly the data merge and classification used by fig_expdemand.do.
do "${code_folder}/Helpers/load_expdemand_data.do" "${data_folder}"
local baseline_controls "$controls"
local outcomes z_motivation z_costbenefits ///
    posterior_ideal_social_min_w posterior_actual_social_min_w

* Motivation and beliefs are standardized using the baseline Control mean/SD.
* Survey 1 post-treatment ideal and predicted time are in minutes per day,
* winsorized at the 5th/95th percentiles by the cleaning pipeline, as in the
* main treatment-effect tables. Hypothesis identification is post-treatment:
* conditional associations, not causal effects of identifying the hypothesis.
* Missing classifications are excluded by regress, not recoded to zero.
eststo clear
foreach specification in additive interacted {
    local rhs "ib0.T ib0.predict_reduction"
    local rows "1.T 2.T 3.T 1.predict_reduction"
    local extra_stats
    local extra_formats
    local extra_labels
    local interpretation "Treatment coefficients are relative to Control."
    if "`specification'" == "interacted" {
        local rhs "ib0.T##ib0.predict_reduction"
        local rows "`rows' 1.T#1.predict_reduction 2.T#1.predict_reduction 3.T#1.predict_reduction"
        local extra_stats p_interactions
        local extra_formats %9.4f
        local extra_labels `""p-value: all interactions = 0""'
        local interpretation "Treatment main effects apply when the hypothesis was not identified."
    }

    local models
    local outcome_index = 0
    foreach outcome of local outcomes {
        local ++outcome_index
        regress `outcome' `rhs' `baseline_controls', vce(robust)
        quietly summarize `outcome' if e(sample) & T == 0
        estadd scalar controlmean = r(mean)
        estadd local controls "Yes"
        if "`specification'" == "interacted" {
            test 1.T#1.predict_reduction 2.T#1.predict_reduction 3.T#1.predict_reduction
            estadd scalar p_interactions = r(p)
        }
        * Short estimate names stay within Stata's 32-character name limit.
        local model "`specification'_`outcome_index'"
        eststo `model'
        local models "`models' `model'"
        tabulate T predict_reduction if e(sample), missing
    }

    * Keep the Results window and LaTeX exports consistent.
    foreach destination in screen latex {
        local export_target
        local export_options
        local titles `""Motivation (std.)" "Cost-benefit beliefs (std.)" "Ideal time (min/day)" "Predicted time (min/day)""'
        if "`destination'" == "latex" {
            local export_target `"using "`output_root'/tables/tab_outcomes_expdemand_`specification'.tex""'
            local export_options booktabs fragment replace
            local titles `""\makecell{Motivation\\(std.)}" "\makecell{Cost-benefit\\beliefs (std.)}" "\makecell{Ideal social\\media time\\(min/day)}" "\makecell{Predicted social\\media time\\(min/day)}""'
        }
        esttab `models' `export_target', ///
            se b(3) nobase noomitted keep(`rows') order(`rows') label ///
            starlevels(* 0.10 ** 0.05 *** 0.01) mtitles(`titles') ///
            coeflabels(1.T "Change Talk" 2.T "Decisional Balance" ///
                3.T "Direct Persuasion" ///
                1.predict_reduction "Identified reduction hypothesis" ///
                1.T#1.predict_reduction "Change Talk x identified hypothesis" ///
                2.T#1.predict_reduction "Decisional Balance x identified hypothesis" ///
                3.T#1.predict_reduction "Direct Persuasion x identified hypothesis") ///
            stats(N r2 controlmean controls `extra_stats', ///
                fmt(%9.0fc %9.3f %9.3f %9s `extra_formats') ///
                labels("Observations" "R-squared" "Control group mean" ///
                    "All baseline controls" `extra_labels')) ///
            `export_options'
    }
}

