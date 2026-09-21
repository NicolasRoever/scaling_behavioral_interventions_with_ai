version 17
clear all
set more off
do 00_setup.do
* $0 local run; supplied clean_scr_data.dta contains adjudicated screenshot measures.
do "CleaningScripts/01_cleaning_baseline.do"
do "CleaningScripts/02_cleaning_followup.do"
do "CleaningScripts/04_create_full_data.do"
display "REPLICATION_CLEANING_COMPLETE"
