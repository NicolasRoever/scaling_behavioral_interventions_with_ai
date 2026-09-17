# Exhibit manifest

Extracted from active `revision.tex` content, excluding `%` comments and `comment` environments. Computed files under `results/` are refreshed for the active survey snapshot. Released hashes and the separately inspected manuscript hashes are in `manifest/exhibits.json`. The original submission has a separate 12-table crosswalk in `manifest/submission_tables.json`, verified references in `submission_results/`, and a detailed audit in `SUBMISSION_TABLE_AUDIT.md`.

| Manuscript path | Public generating code | Inputs / status |
|---|---|---|
| `tables/manual/tab_treatment_description.tex` | `None` | Static design asset / manually authored table |
| `figures/fig_client_counseling.pdf` | `code/stata/tab_client_counseling.do` | Current public survey data |
| `figures/fig_bertopic.pdf` | `code/python/bertopic_plot.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/fig_main_treatment_effects_sm_v001.pdf` | `code/stata/fig_treatment_effect_main.do` | Current public survey data |
| `figures/fig_minutes_treatment_effects.pdf` | `code/stata/fig_treatment_effect_sm_minutes.do` | Current public survey data |
| `figures/fig_sm_followup_mechanisms.pdf` | `code/stata/fig_mechanisms_sm_followup.do` | Current public survey data |
| `tables/tab_strategies_followup.tex` | `code/stata/tab_mechanism_strategies_followup.do` | Current public survey data |
| `tables/tab_balance.tex` | `code/stata/tab_balance.do` | Current public survey data |
| `tables/tab_attrition_analysis_sm.tex` | `code/stata/tab_attrition_sm.do` | Current public survey data |
| `tables/tab_balance_followup.tex` | `code/stata/tab_balance_followup.do` | Current public survey data |
| `tables/tab_main_treatment_effects_sm_mechanisms_duration_control.tex` | `code/stata/tab_main_treatment_effect_duration_control.do` | Current public survey data |
| `tables/tab_secondary_outcomes_holm_panel_a.tex` | `code/stata/tab_main_treatment_effect_mht.do` | Current public survey data |
| `tables/tab_secondary_outcomes_holm_panel_b.tex` | `code/stata/tab_main_treatment_effect_mht.do` | Current public survey data |
| `tables/tab_main_treatment_effects_sm_mechanisms.tex` | `code/stata/tab_main_treatment_effect.do` | Current public survey data |
| `tables/tab_treatment_effects_motivation_followup.tex` | `code/stata/tab_treatment_effect_motivation_followup.do` | Current public survey data |
| `tables/tab_wtp_perceived_cost_mapping.tex` | `code/stata/tab_wtp_perceived_cost_mapping.do` | Current public survey data |
| `tables/tab_main_treatment_effects_sm_minutes.tex` | `code/stata/tab_main_treatment_effect.do` | Current public survey data |
| `tables/tab_treatment_effects_closetoideal_followup.tex` | `code/stata/tab_treatment_effects_closetoideal_followup.do` | Current public survey data |
| `tables/tab_heterogeneity_timeuse_by_wedge.tex` | `code/stata/tab_heterogeneity_timeuse_by_wedge.do` | Current public survey data |
| `tables/tab_heterogeneity_timeuse_by_basetime.tex` | `code/stata/tab_heterogeneity_timeuse_by_basetime.do` | Current public survey data |
| `tables/tab_differences_strategies.tex` | `code/stata/tab_differences_strategies.do` | Current public survey data |
| `tables/tab_outcomes_expdemand_additive.tex` | `code/stata/tab_outcomes_expdemand.do` | Current public survey data |
| `tables/tab_outcomes_expdemand_interacted.tex` | `code/stata/tab_outcomes_expdemand.do` | Current public survey data |
| `figures/tab_thirty_minute_mentions.tex` | `code/python/mentions_table.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/manual/mi_design.png` | `None` | Static design asset / manually authored table |
| `figures/fig_hst_baseline_sm_use.pdf` | `code/stata/fig_baseline_sm_use.do` | Current public survey data |
| `figures/fig_density_interview_dur_by_treat.pdf` | `code/stata/fig_interview_dur.do` | Current public survey data |
| `screenshots/interview_layout_question_2.png` | `None` | Withheld: contains interview dialogue |
| `figures/fig_cdf_importance_score.pdf` | `code/python/cdf_scores.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/fig_cdf_confidence_score.pdf` | `code/python/cdf_scores.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/fig_actual_vs_ideal_social_time_binned.pdf` | `code/stata/fig_ideal_vs_actual_time.do` | Current public survey data |
| `figures/fig_emotions.pdf` | `code/stata/tab_emotions.do` | Current public survey data |
| `figures/fig_miti_score_histograms.pdf` | `code/python/miti_tables.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/qtype_shares_manual.pdf` | `code/python/question_sequence.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/similarity_by_topic.pdf` | `code/python/language_similarity.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/fig_miti_score_distributions_main_study.pdf` | `code/python/miti_tables.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/wordclouds_by_arm.pdf` | `code/python/wordcloud_plot.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/fig_topic_robustness_elbow.pdf` | `code/python/topic_diagnostics.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/fig_topic_seed_stability.pdf` | `code/python/topic_diagnostics.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/fig_number_pro_con_statements.pdf` | `code/python/pros_cons_plot.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/fig_strategies.pdf` | `code/python/strategies_plot.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/fig_change_questionnaire.pdf` | `code/stata/fig_change_quesionnaire.do` | Current public survey data |
| `figures/fig_main_treatment_effects_sm_followup_v001.pdf` | `code/stata/fig_treatment_followup.do` | Current public survey data |
| `figures/fig_app_use_effects.pdf` | `code/stata/tab_appuse.do` | Current public survey data |
| `figures/fig_scrtime_validation_binned_scatter.pdf` | `code/stata/fig_verify_scrtime.do` | Current public survey data |
| `figures/fig_llm_exp_demand.pdf` | `code/stata/fig_expdemand.do` | Current public survey data |
| `figures/fig_prior_posterior_exactly_30_panel.pdf` | `code/stata/fig_posterior_exactly_30_by_arm.do` | Current public survey data |
| `tables/mi_validation_results_table.tex` | `code/python/miti_tables.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `tables/robustness_handcoded_latex_table.tex` | `code/python/miti_tables.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `figures/score_stability_violin_plot.pdf` | `code/python/miti_tables.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
| `tables/score_stability_latex_table.tex` | `code/python/miti_tables.py` | Saved numeric/categorical results; run via `code/python/run_public.py` |
