********************************************************************************
* Project: MI SOCIAL MEDIA
* Purpose: Differential completion of the follow-up survey (Table A.2)
********************************************************************************

version 17
clear all
set more off

do 00_setup.do
use "${data_folder}/processed/main_social_media/clean_merged.dta", clear

assert inlist(followup_finished, 0, 1)

********************************************************************************
* Differential follow-up completion
********************************************************************************

eststo clear
eststo completed: regress followup_finished ib0.T, vce(robust)

quietly summarize followup_finished if e(sample) & T == 0, meanonly
estadd scalar controlmean = r(mean)

* The manuscript wrapper must use one outcome column:
* \estwide{tables/tab_attrition_analysis_sm.tex}{1}{c}
esttab completed using ///
    "${overleaf}/tables/tab_attrition_analysis_sm.tex", ///
    se(3) b(3) nobase noomitted drop(_cons) label ///
    starlevels(* 0.10 ** 0.05 *** 0.01) ///
    mgroups("Completed follow-up", pattern(1) ///
        prefix(\multicolumn{@span}{c}{) suffix(}) span ///
        erepeat(\cmidrule(lr){@span})) ///
    nomtitles ///
    coeflabel( ///
        1.T "Change Talk" ///
        2.T "Decisional Balance" ///
        3.T "Direct Persuasion" ///
    ) ///
    stats(N r2 controlmean, ///
        fmt(%9.0fc %9.3f %9.3f) ///
        labels( ///
            "Observations" ///
            "R\textsuperscript{2}" ///
            "Control group mean" ///
        ) ///
    ) ///
    booktabs fragment replace

********************************************************************************
* Diagnostics: completion by treatment arm
********************************************************************************

quietly count if followup_finished == 1
local n_finished = r(N)
local finish_rate = 100 * `n_finished' / _N

display as result "Finished follow-up surveys: `n_finished' / " _N ///
    " (" %4.1f `finish_rate' "%)"

tabulate T, summarize(followup_finished)
