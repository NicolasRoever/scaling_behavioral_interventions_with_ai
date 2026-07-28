# Exhibit manifest

All paths below are relative to the package root.

## Main-text figures

| Manuscript file | Generating code |
|---|---|
| `fig_client_counseling.pdf` | `code/stata/tab_client_counseling.do` |
| `fig_bertopic.pdf` | `code/python/fig_bertopic.py`; upstream: `classify_bertopic.py`, `topic_model_seed_stability.py` |
| `fig_main_treatment_effects_sm_v001.pdf` | `code/stata/fig_treatment_effect_main.do` |
| `fig_minutes_treatment_effects.pdf` | `code/stata/fig_treatment_effect_sm_minutes.do` |
| `fig_sm_followup_mechanisms.pdf` | `code/stata/fig_mechanisms_sm_followup.do` |

## Appendix figures

| Manuscript file | Generating code |
|---|---|
| `manual/mi_design.png` | Manually created design asset; no analysis code |
| `fig_hst_baseline_sm_use.pdf` | `code/stata/fig_baseline_sm_use.do` |
| `fig_density_interview_dur_by_treat.pdf` | `code/stata/fig_interview_dur.do` |
| `interview_layout_question_2.png` | Screenshot; deliberately excluded |
| `fig_cdf_importance_score.pdf`, `fig_cdf_confidence_score.pdf` | `code/python/fig_cdf_interview_scores.ipynb` |
| `fig_actual_vs_ideal_social_time_binned.pdf` | `code/stata/fig_ideal_vs_actual_time.do` |
| `fig_emotions.pdf` | `code/stata/tab_emotions.do` |
| `fig_miti_score_histograms.pdf` | `code/python/fig_density_miti_scores.ipynb` |
| `fig_miti_score_distributions_main_study.pdf` | `code/python/miti_scoring/fig_miti_score_distributions_main_study.py` |
| `fig_miti_scores_main_study.pdf` | `code/python/miti_scoring/fig_miti_scores_main_study.py` |
| `fig_number_pro_con_statements.pdf` | `code/python/fig_pros_cons.ipynb` |
| `fig_strategies.pdf` | `code/python/fig_strategies_by_treatment.ipynb` |
| `fig_change_questionnaire.pdf` | `code/stata/fig_change_quesionnaire.do` |
| `fig_main_treatment_effects_sm_followup_v001.pdf` | `code/stata/fig_treatment_followup.do` |
| `fig_app_use_effects.pdf` | `code/stata/tab_appuse.do` |
| `fig_llm_exp_demand.pdf` | `code/stata/fig_expdemand.do` |
| `fig_scrtime_validation_binned_scatter.pdf` | `code/stata/fig_verify_scrtime.do` |
| `wordclouds_by_arm.pdf` | `code/python/text_analysis/keyness_wordclouds.py` |
| `qtype_shares_manual.pdf` | `code/python/text_analysis/classify_manual.py` |
| `similarity_by_topic.pdf` | `code/python/text_analysis/similarity.py` |
| `fig_topic_robustness_elbow.pdf` | `code/python/topic_model_robustness.py` |
| `fig_topic_seed_stability.pdf` | `code/python/topic_model_seed_stability.py` |
| `score_stability_violin_plot.pdf` | `code/python/miti_scoring/build_score_stability_table.py`, `plot_score_stability_violin.py` |

## Tables

| Manuscript file | Generating code |
|---|---|
| `manual/tab_treatment_description.tex` | Manually maintained |
| `tab_strategies_followup.tex` | `code/stata/tab_mechanism_strategies_followup.do` |
| `tab_balance.tex` | `code/stata/tab_balance.do` |
| `tab_attrition_analysis_sm.tex` | `code/stata/tab_attrition_sm.do` |
| `tab_balance_followup.tex` | `code/stata/tab_balance_followup.do` |
| `tab_main_treatment_effects_sm_mechanisms.tex` | `code/stata/tab_main_treatment_effect.do` |
| `tab_main_treatment_effects_sm_mechanisms_duration_control.tex` | `code/stata/tab_main_treatment_effect_duration_control.do` |
| `tab_main_treatment_effects_sm_minutes.tex` | `code/stata/tab_main_treatment_effect.do` |
| `tab_treatment_effects_motivation_followup.tex` | `code/stata/tab_treatment_effect_motivation_followup.do` |
| `tab_treatment_effects_closetoideal_followup.tex` | `code/stata/tab_treatment_effects_closetoideal_followup.do` |
| `tab_heterogeneity_timeuse_by_wedge.tex` | `code/stata/tab_heterogeneity_timeuse_by_wedge.do` |
| `tab_heterogeneity_timeuse_by_basetime.tex` | `code/stata/tab_heterogeneity_timeuse_by_basetime.do` |
| `tab_screenshot_pooled_interaction.tex`, `tab_screenshot_corr_by_arm.tex` | `code/stata/tab_screenshot_validation.do` |
| `tab_selection_into_upload.tex`, `tab_balance_upload_subsample.tex` | `code/stata/tab_selection_into_upload.do` |
| `tab_verified_screentime_robustness.tex` | `code/stata/tab_verified_screentime_robustness.do` |
| `tab_wtp_perceived_cost_mapping.tex` | `code/stata/tab_wtp_perceived_cost_mapping.do` |
| `tab_secondary_outcomes_holm_panel_a.tex`, `tab_secondary_outcomes_holm_panel_b.tex` | `code/stata/tab_main_treatment_effect_mht.do` |
| `mi_validation_results_table.tex` | `code/python/miti_scoring/recompute_global_validation_n14.py` |
| `robustness_handcoded_latex_table.tex` | `code/python/miti_scoring/create_latex_table_handcoded_robustness.py` |
| `score_stability_latex_table.tex` | `code/python/miti_scoring/build_score_stability_table.py` |
| `irr_comparison_table.tex` | `code/python/miti_scoring/create_latex_table_irr_comparison.py` |

