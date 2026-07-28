********************************************************************************
* Replication-package configuration
* Run Stata from replication_package/code/stata.
********************************************************************************

version 17
clear
set more off
set seed 123
set cformat %5.3f

global package_root "`c(pwd)'/../.."
global data_folder "${package_root}/data"
global raw_folder "${data_folder}/raw"
global code_folder "${package_root}/code/stata"
global overleaf "${package_root}/results"

capture mkdir "${overleaf}/figures"
capture mkdir "${overleaf}/tables"
cd "${code_folder}"

global pm = char(177)
global controls age female log_income fulltime college high_social_media_use ///
    tiktok_use_dummy instagram_use_dummy snapchat_use_dummy facebook_use_dummy ///
    youtube_use_dummy reddit_use_dummy twitter_use_dummy
global controls_followup age female log_income fulltime college ///
    tiktok_use_dummy instagram_use_dummy snapchat_use_dummy facebook_use_dummy ///
    youtube_use_dummy reddit_use_dummy twitter_use_dummy baseline_actual_social_min

set scheme plotplainblind
grstyle init
grstyle set plain, grid noextend compact horizontal
grstyle set legend 3, nobox klength(4)
grstyle set size 10pt: heading

