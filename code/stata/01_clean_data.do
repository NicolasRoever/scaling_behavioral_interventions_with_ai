********************************************************************************
* Project: MI SOCIAL MEDIA
* Purpose: Run the complete cleaning pipeline in a fixed order
********************************************************************************

version 17
clear all
set more off

* Run this controller from the Stata project folder.
do 00_setup.do

capture log close cleaning_pipeline
log using "${data_folder}/processed/main_social_media/cleaning_pipeline.log", ///
    name(cleaning_pipeline) text replace

* Record backend run times as Unix seconds.
local stata_unix_origin = clock("01jan1970 00:00:00", "DMYhms")
local started_ms = clock("`c(current_date)' `c(current_time)'", "DMY hms")
local started_unix = floor((`started_ms' - `stata_unix_origin') / 1000)
display as text "Cleaning pipeline started (Unix): `started_unix'"

local cleaning_scripts ///
    "01_cleaning_baseline.do" ///
    "02_cleaning_followup.do" ///
    "03_clean_screenshot_data.do" ///
    "04_create_full_data.do" ///
    "05_create_clean_chat_data.do"

foreach script of local cleaning_scripts {
    display as result "Running CleaningScripts/`script'"
    capture noisily do "${code_folder}/CleaningScripts/`script'"
    local return_code = _rc

    if `return_code' {
        display as error "Pipeline stopped in `script' with return code `return_code'."
        log close cleaning_pipeline
        exit `return_code'
    }
}

local finished_ms = clock("`c(current_date)' `c(current_time)'", "DMY hms")
local finished_unix = floor((`finished_ms' - `stata_unix_origin') / 1000)
display as text "Cleaning pipeline completed (Unix): `finished_unix'"

log close cleaning_pipeline
