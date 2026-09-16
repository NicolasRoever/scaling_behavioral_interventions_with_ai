*===============================================================================
* Overall treatment differences in the number of strategies adopted at follow-up
*===============================================================================

version 17
clear all
set more off
do 00_setup.do

use "${data_folder}/processed/main_social_media/clean_merged.dta", clear
keep if followup_responded == 1 & !missing(w2_time_mechanism)

* Count all 12 named strategies plus Other (one additional selected category).
* No steps taken is not a strategy. Unlike the old commented-out count, this
* includes reduced phone use, curated feed, replacement activities, and willpower.
local strategy_items w2_mechanism_settings w2_mechanism_blocker ///
    w2_mechanism_notif w2_mechanism_friction w2_mechanism_delete ///
    w2_mechanism_rules w2_mechanism_reach w2_mechanism_reduce_phone ///
    w2_mechanism_curate_feed w2_mechanism_replace_act w2_mechanism_help ///
    w2_mechanism_willpower w2_mechanism_other
local n_strategies : word count `strategy_items'

foreach item of local strategy_items {
    assert inlist(`item', 0, 1) | missing(`item')
}
egen strategy_items_missing = rowmiss(`strategy_items')
egen strategy_count = rowtotal(`strategy_items')
* Do not silently count missing answers as non-adoption.
replace strategy_count = . if strategy_items_missing > 0
assert inrange(strategy_count, 0, `n_strategies') if !missing(strategy_count)
label variable strategy_count "Number of strategies adopted"

quietly count if strategy_items_missing > 0
display as text "Respondents with incomplete strategy items: " as result r(N)
quietly count if w2_mechanism_none == 1 & strategy_count > 0 & !missing(strategy_count)
display as text "Respondents selecting both No steps and a strategy: " as result r(N)
* If inconsistent selections exist, count the selected strategies as recorded.

* OLS with robust SEs estimates differences in the mean strategy count, using
* the same baseline controls as the existing follow-up mechanisms analysis.
eststo clear
regress strategy_count ib0.T $controls_followup, vce(robust)
quietly summarize strategy_count if e(sample) & T == 0
estadd scalar controlmean = r(mean)
estadd local controls "Yes"

* Omnibus test across all FOUR arms (including control):
* H0: all three treatment effects relative to control equal zero.
testparm i.T
estadd scalar p_all_arms = r(p)

* Omnibus test across the THREE active treatments:
* H0: Change Talk = Decisional Balance = Direct Persuasion.
test (1.T = 2.T) (1.T = 3.T)
estadd scalar p_active_arms = r(p)

* Pairwise active-treatment comparisons (unadjusted p-values).
test 1.T = 2.T
estadd scalar p_amb_cha = r(p)
test 1.T = 3.T
estadd scalar p_cha_per = r(p)
test 2.T = 3.T
estadd scalar p_amb_per = r(p)
eststo total_count

* Descriptive means use exactly the regression sample.
tabstat strategy_count if e(sample), by(T) statistics(n mean sd min max)

* Share formatting between the Results window and the paper's LaTeX table.
foreach destination in screen latex {
    local export_target
    local export_options
    if "`destination'" == "latex" {
        local export_target `"using "${overleaf}/tables/tab_differences_strategies.tex""'
        local export_options booktabs fragment replace
    }

esttab total_count `export_target', se b(3) nobase noomitted keep(*.T) label ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("Total strategy count") ///
    coeflabels(1.T "Change Talk (a)" 2.T "Decisional Balance (b)" ///
        3.T "Direct Persuasion (c)") ///
    stats(N r2 controlmean controls p_all_arms p_active_arms ///
        p_amb_cha p_cha_per p_amb_per, ///
        fmt(%9.0fc %9.3f %9.3f %9s %9.4f %9.4f %9.4f %9.4f %9.4f) ///
        labels("Observations" "R-squared" "Control group mean" "Controls" ///
            "p-value: all four arms equal" "p-value: a=b=c" ///
            "p-value: a=b" "p-value: a=c" "p-value: b=c")) ///
    `export_options'
}
