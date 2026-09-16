********************************************************************************
* Project: MI SOCIAL MEDIA
* Purpose: Main treatment effects, controlling for interview duration
********************************************************************************

version 17
clear all
set more off

do 00_setup.do
use "${data_folder}/processed/main_social_media/clean_data.dta", clear

local outcomes ///
    z_motivation ///
    z_costbenefits ///
    z_smart_bett_wors_revers ///
    z_awareness ///
    z_selfefficacy ///
    wtp_dollars

local regression_controls "$controls time_interview_minutes"

eststo clear
foreach outcome of local outcomes {
    eststo: regress `outcome' i.T `regression_controls', vce(robust)

    quietly summarize `outcome' if control
    estadd scalar controlmean = r(mean)

    estadd local controls "Yes"
    estadd local duration_control "Yes"

    test 1.T = 2.T
    estadd scalar p_amb_cha = r(p)

    test 1.T = 3.T
    estadd scalar p_cha_per = r(p)

    test 2.T = 3.T
    estadd scalar p_amb_per = r(p)
}

esttab * using ///
    "${overleaf}/tables/tab_main_treatment_effects_sm_mechanisms_duration_control.tex", ///
    se b(3) nobase noomitted ///
    drop(`regression_controls' _cons) ///
    label starlevels(* 0.10 ** 0.05 *** 0.01) ///
    mtitles( ///
        "\makecell{Motivation\\ (std.)}" ///
        "\makecell{Perceived cost\\ of social\\ media (std.)}" ///
        "\makecell{Social media\\makes life \\ worse (std.)}" ///
        "\makecell{Awareness\\ self-control\\ problems (std.)}" ///
        "\makecell{Self-\\efficacy\\ belief (std.)}" ///
        "\makecell{WTP\\(\$)}" ///
    ) ///
    coeflabel( ///
        1.T "Change Talk (a)" ///
        2.T "Decisional Balance (b)" ///
        3.T "Direct Persuasion (c)" ///
    ) ///
    stats( ///
        N r2 controlmean controls duration_control ///
        p_amb_cha p_cha_per p_amb_per, ///
        fmt(%9.0fc %9.3f %9.3f %9s %9s %9.3f %9.3f %9.3f) ///
        labels( ///
            "Observations" ///
            "R\textsuperscript{2}" ///
            "Control group mean" ///
            "Baseline controls" ///
            "Interview duration control" ///
            "p-value: a=b" ///
            "p-value: a=c" ///
            "p-value: b=c" ///
        ) ///
    ) ///
    booktabs fragment replace
