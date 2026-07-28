********************************************************************************
* Reproduce all Stata-generated exhibits referenced by revision.tex
********************************************************************************

version 17
clear all
set more off
do 00_setup.do

local scripts ///
    "fig_baseline_sm_use.do" ///
    "fig_change_quesionnaire.do" ///
    "fig_expdemand.do" ///
    "fig_ideal_vs_actual_time.do" ///
    "fig_interview_dur.do" ///
    "fig_mechanisms_sm_followup.do" ///
    "fig_treatment_effect_main.do" ///
    "fig_treatment_effect_sm_minutes.do" ///
    "fig_treatment_followup.do" ///
    "fig_verify_scrtime.do" ///
    "tab_appuse.do" ///
    "tab_attrition_sm.do" ///
    "tab_balance.do" ///
    "tab_balance_followup.do" ///
    "tab_client_counseling.do" ///
    "tab_emotions.do" ///
    "tab_heterogeneity_timeuse_by_basetime.do" ///
    "tab_heterogeneity_timeuse_by_wedge.do" ///
    "tab_main_treatment_effect.do" ///
    "tab_main_treatment_effect_duration_control.do" ///
    "tab_main_treatment_effect_mht.do" ///
    "tab_mechanism_strategies_followup.do" ///
    "tab_screenshot_validation.do" ///
    "tab_selection_into_upload.do" ///
    "tab_treatment_effect_motivation_followup.do" ///
    "tab_treatment_effects_closetoideal_followup.do" ///
    "tab_verified_screentime_robustness.do" ///
    "tab_wtp_perceived_cost_mapping.do"

foreach script of local scripts {
    display as result "Running `script'"
    do "`script'"
}

* Several source scripts also emit exploratory intermediates that revision.tex
* does not use. Remove those so results/ remains an exhibit-only directory.
capture erase "${overleaf}/figures/fig_hist_interview_dur.pdf"
capture erase "${overleaf}/tables/tab_main_treatment_effects_sm_mechanisms_holm.tex"
capture erase "${overleaf}/tables/tab_main_treatment_effects_sm_minutes_holm.tex"
capture erase "${overleaf}/tables/tab_sm_change.tex"
capture erase "${overleaf}/tables/tab_sm_client_counseling.tex"
