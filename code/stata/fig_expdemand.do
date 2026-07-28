clear 

use "${data_folder}/processed/main_social_media/df_merged_llm_category_expdemand_v001"


*Assign Labels
* Define the value label scheme

label define purpose_lbl ///
    1 "Correct: chatbot + reduction" ///
    2 "Partial: reduction only" ///
    3 "Partial: chatbot only" ///
    4 "Neither: no Chatbot/reduction" ///
    5 "Unclear/don't know"

* Apply the label to the variable
destring llm_category_expdemand, replace
label values llm_category_expdemand purpose_lbl


graph hbar (percent), ///
    over(llm_category_expdemand, label(labsize(small))) ///
    bar(1, color(maroon)) ///
    blabel(bar, format(%9.1f) size(small)) ///
    ytitle("Frequency (%)", size(medium)) ///
    graphregion(fcolor(white) lcolor(white)) ///
    plotregion(fcolor(white) lcolor(none)) ///
    ylab(, nogrid glwidth(none)) ///
    intensity(100) lintensity(100)


* Export the graph
graph export "${overleaf}/figures/fig_llm_exp_demand.pdf", replace


*Regression
gen predict_reduction = inlist(llm_category_expdemand, 1,2)
reg predict_reduction control, r


*Regression
reg predict_reduction i.T if control == 0


eststo clear 
eststo reg3: reg motivation i.T $controls 
eststo reg2: reg motivation i.T $controls if inlist(llm_category_expdemand, 1,2) &!missing(llm_category_expdemand)
eststo reg1: reg motivation i.T $controls if inlist(llm_category_expdemand, 3,4,5) &!missing(llm_category_expdemand)


esttab reg1 reg2 reg3, se b(3) starlevel(* 0.1 ** 0.05 *** 0.01) nobase noomitted label keep(*T)

qui suest reg1 reg2,r

test ([reg1_mean]1.T = [reg2_mean]1.T) ///
     ([reg1_mean]2.T = [reg2_mean]2.T) ///
     ([reg1_mean]3.T = [reg2_mean]3.T)
	 
	 
*Regression Cost Benefits
reg predict_reduction i.T if control == 0
eststo clear 
eststo reg1: reg z_costbenefits i.T $controls if inlist(llm_category_expdemand, 1,2) &!missing(llm_category_expdemand)
eststo reg2: reg z_costbenefits i.T $controls if inlist(llm_category_expdemand, 3,4,5) &!missing(llm_category_expdemand)


esttab reg1 reg2, se b(3) starlevel(* 0.1 ** 0.05 *** 0.01) nobase noomitted label keep(*T)

qui suest reg1 reg2,r

test ([reg1_mean]1.T = [reg2_mean]1.T) ///
     ([reg1_mean]2.T = [reg2_mean]2.T) ///
     ([reg1_mean]3.T = [reg2_mean]3.T)
