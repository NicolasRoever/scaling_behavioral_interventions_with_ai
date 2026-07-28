********************************************************************************
* Remove screenshot-upload file metadata from the public survey copies.
* Structured screen-time measures and analysis indicators remain available.
********************************************************************************

version 17
clear all
set more off
do 00_setup.do

local files ///
    ${data_folder}/raw/main_socialmedia/follow_up_raw.dta ///
    ${data_folder}/processed/main_social_media/follow_up_clean.dta ///
    ${data_folder}/processed/main_social_media/clean_merged.dta ///
    ${data_folder}/processed/main_social_media/clean_merged_with_scrshots.dta ///
    ${data_folder}/processed/main_social_media/df_merged_llm_category_expdemand_v001.dta

foreach file of local files {
    use "`file'", clear
    capture drop screenshot_upload_1_id screenshot_upload_1_name ///
        screenshot_upload_1_size screenshot_upload_1_type
    capture drop w2_screenshot_upload_1_id w2_screenshot_upload_1_name ///
        w2_screenshot_upload_1_size w2_screenshot_upload_1_type
    save "`file'", replace
}
