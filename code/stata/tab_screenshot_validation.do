*===============================================================================
*  Appendix: Screenshot Validation (Reviewer Comment 1, items 1-2)
*  1. Self-reported vs. verified social media time correlation, by treatment arm
*  2. Pooled regression of verified on self-reported time, fully interacted with
*     treatment, with a joint test that the slopes are equal across arms
*===============================================================================

* Add Controls
do 00_setup

* Load data
clear all
use "${data_folder}/processed/main_social_media/clean_merged_with_scrshots.dta", clear

*-------------------------------------------------------------------------
* 1. Self-reported vs. verified time: correlation and bias by treatment arm
*    Per-arm block: raw Pearson correlation (with Fisher z 95% CI and N),
*    and bias (mean self-reported minus verified time, with a paired t-test
*    p-value that it differs from zero).
*    Below that: pairwise tests, across all arm pairs, of whether the
*    correlation differs (independent-samples Fisher z-test) and whether
*    the bias differs (Welch two-sample t-test) between the two arms.
*-------------------------------------------------------------------------

local armlabel0 "Control"
local armlabel1 "Change Talk"
local armlabel2 "Decisional Balance"
local armlabel3 "Direct Persuasion"

gen diff_self_verified = w2_actual_social_min_wins - verified_prefered_time_w

forvalues t = 0/3 {
    qui corr verified_prefered_time_w w2_actual_social_min_wins if T == `t'
    local rho`t' = r(rho)
    local n`t' = r(N)

    * Fisher z 95% confidence interval for the raw Pearson correlation.
    local z = atanh(`rho`t'')
    local zcrit = invnormal(.975)
    local ci_lo_z = `z' - `zcrit' / sqrt(`n`t'' - 3)
    local ci_hi_z = `z' + `zcrit' / sqrt(`n`t'' - 3)
    local ci_lo`t' = (exp(2 * `ci_lo_z') - 1) / (exp(2 * `ci_lo_z') + 1)
    local ci_hi`t' = (exp(2 * `ci_hi_z') - 1) / (exp(2 * `ci_hi_z') + 1)

    * Bias: mean(self-reported - verified) and a one-sample t-test that it is 0.
    qui ttest diff_self_verified == 0 if T == `t'
    local bias`t' = r(mu_1)
    local p_bias`t' = r(p)

    di as text "Arm `t' (`armlabel`t''): rho = " as result %9.3f `rho`t'' ///
        as text ", 95% CI = [" as result %9.3f `ci_lo`t'' as text ", " ///
        as result %9.3f `ci_hi`t'' as text "], N = " as result %9.0fc `n`t'' ///
        as text ", bias = " as result %9.3f `bias`t'' as text ", p = " as result %9.3f `p_bias`t''
}

* Pairwise tests of differential correlation and differential bias across arms.
forvalues i = 0/3 {
    forvalues j = 0/3 {
        if `j' > `i' {
            * Differential correlation: independent-samples Fisher z-test.
            local zi = atanh(`rho`i'')
            local zj = atanh(`rho`j'')
            local se_diff = sqrt(1 / (`n`i'' - 3) + 1 / (`n`j'' - 3))
            local zstat = (`zi' - `zj') / `se_diff'
            local p_corr_`i'_`j' = 2 * (1 - normal(abs(`zstat')))

            * Differential bias: Welch two-sample t-test.
            qui ttest diff_self_verified if inlist(T, `i', `j'), by(T) unequal
            local p_bias_`i'_`j' = r(p)

            di as text "`armlabel`i'' vs. `armlabel`j'': p(rho equal) = " ///
                as result %9.3f `p_corr_`i'_`j'' ///
                as text ", p(bias equal) = " as result %9.3f `p_bias_`i'_`j''
        }
    }
}

* Assemble the LaTeX table by hand (rows = arms/pairs, not esttab's model columns).
tempname ftab
file open `ftab' using "${overleaf}/tables/tab_screenshot_corr_by_arm.tex", write replace

file write `ftab' "\begin{tabular}{lcc}" _n
file write `ftab' "\toprule" _n
file write `ftab' " & Correlation (\$\rho\$) & Bias (self-report -- verified) \\" _n
file write `ftab' "\midrule" _n

forvalues t = 0/3 {
    local rho_s = trim("`: display %9.3f `rho`t'''")
    local bias_s = trim("`: display %9.3f `bias`t'''")
    local ci_lo_s = trim("`: display %9.3f `ci_lo`t'''")
    local ci_hi_s = trim("`: display %9.3f `ci_hi`t'''")
    local p_bias_s = trim("`: display %9.3f `p_bias`t'''")

    file write `ftab' "`armlabel`t'' & `rho_s' & `bias_s' \\" _n
    file write `ftab' " & [`ci_lo_s', `ci_hi_s'] (N=`n`t'') & \$p\$ = `p_bias_s' \\" _n
}

file write `ftab' "\midrule" _n
file write `ftab' "\multicolumn{3}{l}{\textit{Pairwise tests of equality across arms (p-values)}} \\" _n
file write `ftab' " & \$\Delta\$ Correlation & \$\Delta\$ Bias \\" _n

forvalues i = 0/3 {
    forvalues j = 0/3 {
        if `j' > `i' {
            local p_corr_s = trim("`: display %9.3f `p_corr_`i'_`j'''")
            local p_bias_pair_s = trim("`: display %9.3f `p_bias_`i'_`j'''")
            file write `ftab' "`armlabel`i'' vs.\ `armlabel`j'' & `p_corr_s' & `p_bias_pair_s' \\" _n
        }
    }
}

file write `ftab' "\bottomrule" _n
file write `ftab' "\end{tabular}" _n
file close `ftab'

type "${overleaf}/tables/tab_screenshot_corr_by_arm.tex"


*-------------------------------------------------------------------------
* 2. Pooled regressions: verified on self-reported time
*    Column 1: pooled, no interaction (single slope, all arms combined)
*    Column 2: pooled, fully interacted with T, plus joint test that the
*              slopes are equal across arms
*-------------------------------------------------------------------------

eststo clear
eststo pooled_plain: reg verified_prefered_time_w w2_actual_social_min_wins, r
qui corr verified_prefered_time_w w2_actual_social_min_wins
estadd scalar rho = r(rho)

eststo pooled_interact: reg verified_prefered_time_w c.w2_actual_social_min_wins##i.T, r

* Joint test: slope of self-reported time is the same in every arm
test 1.T#c.w2_actual_social_min_wins = 2.T#c.w2_actual_social_min_wins = 3.T#c.w2_actual_social_min_wins
estadd scalar p_slopes_equal = r(p)

esttab pooled_plain pooled_interact, se b(3) label starlevels(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("Pooled" "Pooled, interacted with T") ///
    drop(0.T 0.T#c.w2_actual_social_min_wins) ///
    coeflabel(w2_actual_social_min_wins "Self-reported time (min/day)" ///
        1.T "Change Talk" 2.T "Decisional Balance" 3.T "Direct Persuasion" ///
        1.T#c.w2_actual_social_min_wins "Change Talk \$\times\$ self-reported time" ///
        2.T#c.w2_actual_social_min_wins "Decisional Balance \$\times\$ self-reported time" ///
        3.T#c.w2_actual_social_min_wins "Direct Persuasion \$\times\$ self-reported time") ///
    stats(rho N r2 p_slopes_equal, fmt(%9.3f %9.0fc %9.3f %9.3f) labels("Correlation (\$\rho\$)" "Observations" "R\textsuperscript{2}" "p-value: slopes equal across arms"))

esttab pooled_plain pooled_interact using "${overleaf}/tables/tab_screenshot_pooled_interaction.tex", ///
    se b(3) label starlevels(* 0.10 ** 0.05 *** 0.01) ///
    mtitles("Pooled" "Pooled, interacted with T") ///
    drop(0.T 0.T#c.w2_actual_social_min_wins) ///
    coeflabel(w2_actual_social_min_wins "Self-reported time (min/day) [Control]" ///
        1.T "Change Talk" 2.T "Decisional Balance" 3.T "Direct Persuasion" ///
        1.T#c.w2_actual_social_min_wins "Change Talk \$\times\$ self-reported time" ///
        2.T#c.w2_actual_social_min_wins "Decisional Balance \$\times\$ self-reported time" ///
        3.T#c.w2_actual_social_min_wins "Direct Persuasion \$\times\$ self-reported time") ///
    stats(rho N r2 p_slopes_equal, fmt(%9.3f %9.0fc %9.3f %9.3f) labels("Correlation (\$\rho\$)" "Observations" "R\textsuperscript{2}" "p-value: slopes equal across arms")) ///
    booktabs fragment replace
