version 17
clear all
set more off
do 00_setup.do
capture log close _all
log using "${overleaf}/stata.log", text replace
display "Additional API/compute cost: $0; no API calls."
do "fig_baseline_sm_use.do"
do "fig_change_quesionnaire.do"
do "fig_expdemand.do"
do "fig_ideal_vs_actual_time.do"
do "fig_interview_dur.do"
do "fig_mechanisms_sm_followup.do"
do "fig_treatment_effect_main.do"
do "fig_treatment_effect_sm_minutes.do"
do "fig_treatment_followup.do"
do "fig_verify_scrtime.do"
do "tab_appuse.do"
do "tab_attrition_sm.do"
do "tab_balance.do"
do "tab_balance_followup.do"
do "tab_client_counseling.do"
do "tab_emotions.do"
do "tab_heterogeneity_timeuse_by_basetime.do"
do "tab_heterogeneity_timeuse_by_wedge.do"
do "tab_main_treatment_effect.do"
do "tab_main_treatment_effect_duration_control.do"
do "tab_main_treatment_effect_mht.do"
do "tab_mechanism_strategies_followup.do"
do "tab_treatment_effect_motivation_followup.do"
do "tab_treatment_effects_closetoideal_followup.do"
do "tab_wtp_perceived_cost_mapping.do"
do "tab_differences_strategies.do"
do "tab_outcomes_expdemand.do"
do "fig_posterior_exactly_30_by_arm.do"
do "stats_quoted_in_text.do"
display "REPLICATION_STATA_COMPLETE"
log close
