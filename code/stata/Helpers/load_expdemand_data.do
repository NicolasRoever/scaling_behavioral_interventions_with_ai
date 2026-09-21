* Shared analysis sample and outcome definition for the demand figure and table.
* Input: processed-data root, passed explicitly by the caller.
args data_dir classification_file
if `"`classification_file'"' == "" ///
    local classification_file "df_merged_llm_category_expdemand_luna_v002.dta"
use "`data_dir'/processed/main_social_media/clean_data.dta", clear
isid prolific_id
merge 1:1 prolific_id using ///
    "`data_dir'/processed/main_social_media/`classification_file'", ///
    keepusing(llm_category_expdemand) keep(master match) nogenerate

capture confirm numeric variable llm_category_expdemand
if _rc destring llm_category_expdemand, replace
assert inlist(llm_category_expdemand, 1, 2, 3, 4, 5) | missing(llm_category_expdemand)
assert inlist(T, 0, 1, 2, 3)

label define purpose_lbl ///
    1 "Correct: chatbot + reduction" ///
    2 "Partial: reduction only" ///
    3 "Partial: chatbot only" ///
    4 "Neither: no chatbot/reduction" ///
    5 "Unclear/don't know", replace
label values llm_category_expdemand purpose_lbl

* Categories 1 and 2 mention reduction; 3-5 do not. Missing codes stay missing.
generate byte predict_reduction = inlist(llm_category_expdemand, 1, 2) ///
    if !missing(llm_category_expdemand)
label variable predict_reduction "Identified reduction hypothesis"
quietly count if missing(predict_reduction)
display as text "Participants without a hypothesis classification: " as result r(N)
