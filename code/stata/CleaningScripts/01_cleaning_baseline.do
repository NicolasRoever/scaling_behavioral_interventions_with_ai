********************************************************************************
* Project: MI SOCIAL MEDIA
* Purpose : Clean raw survey data and construct analysis variables
********************************************************************************

********************************************************************************
* Import data
********************************************************************************

* Do this once for easier cleaning later on. Saves a bit of time
* clear
* import spss using "${raw_folder}/main_socialmedia/main_raw.sav", case(lower)
* destring *, replace
* save "${raw_folder}/main_socialmedia/main_raw.dta", replace

use "${raw_folder}/main_socialmedia/main_raw.dta", clear

********************************************************************************
* Remove test responses 
********************************************************************************

* Filter start_time_raw to keep only observations on/after 18-Dec-2025 04:00. 
local cutofftime clock("18-Dec-2025 04:00:00", "DMYhms")

count
local Nbefore = r(N)
drop if startdate < `cutofftime'
count
local Nafter = r(N)
local Ndropped = `Nbefore' - `Nafter'
local pctdrop = `Ndropped' / `Nbefore'
display as text "Dropped `Ndropped' observations (`=round(`pctdrop'*100, 0.1)') where startdate was before 18-Dec-2025 04:00."


********************************************************************************
* Pre-registered exclusion conditions
********************************************************************************

* 1. Drop non-consenting respondents
drop if consent != 1
drop consent

* 2. Drop people that were not assigned to treatment
drop if missing(treatment)

* 3. Drop people without any outcome data
drop if missing(motivation)

* 4.Drop people with less than 20 characters in writing task
gen writing_chars = length(writing)
drop if writing_chars <= 20

* 5. Drop 1% tails based on speed
gen duration_pretreatment = 0
foreach var in time_captcha time_consent time_audio_screener time_writing tim_op_system tim_app_current tim_actual_time time_social_apps tim_time_each tim_platform_usage tim_addicted time_tutorial {
    replace duration_pretreatment = duration_pretreatment + `var'_page_submit
}
la var duration_pretreatment "Pretreatment duration (seconds)"
summ duration_pretreatment, detail
drop if (duration_pretreatment < r(p1)) | (duration_pretreatment > r(p99))

* 6. Drop if writing speed is too high
replace typing_speed = "0" if typing_speed == "#"
destring typing_speed, replace
summ typing_speed, detail
drop if typing_speed > 10

* 7. Drop the 4 people who did not complete the survey
*    This doesn't affect results but makes tables easier to compare because the sample is identical.
*drop if r_status !=  "completed"
drop if finished == 0
drop finished progress

********************************************************************************
* Drop metadata / technical variables 
********************************************************************************

drop q_recaptcha* q_duplicate* human_screen* distributionchannel userlanguage
drop llm_audio_screener_1 status
drop session_id interview_endpoint first_question

	 
********************************************************************************
* Rename key identifiers and timing variables
********************************************************************************

rename responseid     response_id
rename prolific_pid   prolific_id
rename study_id       study_id_raw
rename user_id        user_id_raw
rename interview_id   interview_id_raw

rename startdate      start_time_raw
rename enddate        end_time_raw
rename duration__*    duration_seconds

label var response_id      "Survey response ID"
label var prolific_id      "Prolific ID"
label var study_id_raw     "Original study ID"
label var user_id_raw      "Original platform user ID"
label var interview_id_raw "Interview ID"
label var start_time_raw   "Survey start time (raw)"
label var end_time_raw     "Survey end time (raw)"
label var duration_seconds "Survey duration in seconds"

* Convert duration to minutes
gen double duration_minutes = duration_seconds/60.0
label var duration_minutes "Survey duration in minutes"


********************************************************************************
* Convert date–time variables to Stata datetimes
********************************************************************************

capture confirm numeric variable start_time_raw
if _rc {
    * Example if they are strings; adapt mask to your format
    gen double start_time = clock(start_time_raw, "YMDhms")
    gen double end_time   = clock(end_time_raw,   "YMDhms")
}
else {
    gen double start_time = start_time_raw
    gen double end_time   = end_time_raw
}

format start_time end_time %tc
label var start_time "Survey start time"
label var end_time   "Survey end time"


********************************************************************************
* App Installed Multiple Choice
********************************************************************************
label define yesno 0 "No" 1 "Yes", replace

rename app_current_1 app_installed_tiktok
rename app_current_2 app_installed_instagram  
rename app_current_4 app_installed_snapchat
rename app_current_5 app_installed_facebook
rename app_current_12 app_installed_youtube
rename app_current_6 app_installed_reddit
rename app_current_9 app_installed_twitter
foreach var of varlist app_installed_* {
    replace `var' = `var' == 1
    la val `var' yesno
}
label var app_installed_tiktok     "TikTok installed (0/1)"
label var app_installed_instagram  "Instagram installed (0/1)"
label var app_installed_snapchat   "Snapchat installed (0/1)"
label var app_installed_facebook   "Facebook installed (0/1)"
label var app_installed_youtube    "YouTube installed (0/1)"
label var app_installed_reddit     "Reddit installed (0/1)"
label var app_installed_twitter    "Twitter installed (0/1)"

* Sanity check for Prolific screener condition.
gen app_installed_tiktok_or_insta = app_installed_tiktok == 1 | app_installed_instagram == 1
la var app_installed_tiktok_or_insta "TikTok or Instagram installed (0/1)"
la val app_installed_tiktok_or_insta yesno



********************************************************************************
* Writing task
********************************************************************************

la var writing "Writing task: Favourite month of the year"
la var writing_chars "Number of characters in writing task"


********************************************************************************
* Device type (iPhone/Android)
********************************************************************************

rename oper_system smartphone_OS
la var smartphone_OS "Smartphone operating system"
gen iphone_user = smartphone_OS == 2
la val iphone_user yesno
la var iphone_user "iPhone user"



********************************************************************************
* Actual and ideal Time
********************************************************************************

* Destring time variables before conversion
destring actual_time_1_1_1 actual_time_1_1_2 ideal_social_time_1_1_1 ideal_social_time_1_1_2, replace force

* Convert actual social media time from hours/minutes to total minutes
gen baseline_actual_social_min = actual_time_1_1_1 * 60 + actual_time_1_1_2
la var baseline_actual_social_min "Actual social media time (minutes)"
drop actual_time_1_1_1 actual_time_1_1_2

* Convert ideal social media time from hours/minutes to total minutes
gen baseline_ideal_social_min = ideal_social_time_1_1_1 * 60 + ideal_social_time_1_1_2
la var baseline_ideal_social_min "Ideal social media time (minutes)"
drop ideal_social_time_1_1_1 ideal_social_time_1_1_2

* Generate winsorized social media time variables (pre-registered)
winsor2 baseline_actual_social_min baseline_ideal_social_min, cuts(5 95) suffix(_w)
la var baseline_actual_social_min_w "Actual social media time (minutes, winsorized)"
la var baseline_ideal_social_min_w "Ideal social media time (minutes, winsorized)"

********************************************************************************
* Baseline time on different social media apps
********************************************************************************

* Rename variables
rename time_each_1 baseline_tiktok_min
rename time_each_2 baseline_instagram_min
rename time_each_3 baseline_snapchat_min
rename time_each_4 baseline_youtube_min
rename time_each_5 baseline_facebook_min
rename time_each_6 baseline_reddit_min
rename time_each_7 baseline_twitter_min

* Convert to midpoint of scale
foreach var in baseline_tiktok_min baseline_instagram_min baseline_snapchat_min baseline_youtube_min baseline_facebook_min baseline_reddit_min baseline_twitter_min {
    gen `var'_midpoint = .
    replace `var'_midpoint = 0    if `var' == 0
    replace `var'_midpoint = 2.5  if `var' == 1
    replace `var'_midpoint = 10   if `var' == 2
    replace `var'_midpoint = 22.5 if `var' == 3
    replace `var'_midpoint = 45   if `var' == 4
    replace `var'_midpoint = 90   if `var' == 5
    replace `var'_midpoint = 150  if `var' == 6
}
label var baseline_tiktok_min_midpoint    "TikTok time (midpoint minutes)"
label var baseline_instagram_min_midpoint "Instagram time (midpoint minutes)"
label var baseline_snapchat_min_midpoint  "Snapchat time (midpoint minutes)"
label var baseline_facebook_min_midpoint  "Facebook time (midpoint minutes)"
label var baseline_youtube_min_midpoint   "YouTube time (midpoint minutes)"
label var baseline_reddit_min_midpoint    "Reddit time (midpoint minutes)"
label var baseline_twitter_min_midpoint    "Twitter time (midpoint minutes)"

* Dummies: 1 if app minutes > 0, 0 otherwise
foreach app in tiktok instagram snapchat facebook youtube reddit twitter {
    gen byte `app'_use_dummy = (baseline_`app'_min_midpoint > 0)
    label var `app'_use_dummy "`=proper("`app'")' use dummy (1=uses app)"
}


********************************************************************************
* Ideal Use Per app
********************************************************************************
	 
rename platform_usage_1 baseline_ideal_tiktok_use
rename platform_usage_2 baseline_ideal_instagram_use
rename platform_usage_3 baseline_ideal_snapchat_use
rename platform_usage_4 baseline_ideal_facebook_use
rename platform_usage_5 baseline_ideal_youtube_use
rename platform_usage_6 baseline_ideal_reddit_use
rename platform_usage_7 baseline_ideal_twitter_use
la var baseline_ideal_tiktok_use      "Ideal TikTok use"
la var baseline_ideal_instagram_use   "Ideal Instagram use"
la var baseline_ideal_snapchat_use    "Ideal Snapchat use"
la var baseline_ideal_facebook_use    "Ideal Facebook use"
la var baseline_ideal_youtube_use     "Ideal YouTube use"
la var baseline_ideal_reddit_use      "Ideal Reddit use"
la var baseline_ideal_twitter_use     "Ideal Twitter use"
 
 
********************************************************************************
* Addiction for Each App
********************************************************************************

rename addicted_1 addiction_tiktok
rename addicted_2 addiction_instagram
rename addicted_3 addiction_snapchat
rename addicted_4 addiction_facebook
rename addicted_5 addiction_youtube
rename addicted_6 addiction_reddit
rename addicted_7 addiction_twitter


********************************************************************************
* Treatment variables
********************************************************************************

gen T = .
replace T = 0 if treatment == "control"
replace T = 1 if treatment == "changetalk"
replace T = 2 if treatment == "ambivalence"
replace T = 3 if treatment == "persuasion"

gen control = T == 0
gen changetalk = T == 1
gen ambivalence = T == 2
gen persuasion = T == 3
la val control     yesno
la val persuasion  yesno
la val ambivalence yesno
la val changetalk  yesno
la var control     "Control"
la var persuasion  "Persuasion"
la var ambivalence "Ambivalence"
la var changetalk  "Change Talk"
la var T "Treatment group"
label define T_lab 0 "Control" 1 "Change Talk" 2 "Ambivalence" 3 "Persuasion", replace
label values T T_lab

order T control persuasion ambivalence changetalk, first

********************************************************************************
* Motivation
********************************************************************************

summ motivation if control , de
gen z_motivation = (motivation - r(mean)) / r(sd) 
la var z_motivation "Motivation (std.)"
la var motivation "Motivation"

********************************************************************************
* Cost Benefits
********************************************************************************

gen costbenefits = (costsbenefits_1 + costsbenefits_2 + costsbenefits_3 + costsbenefits_4) / 4
summ costbenefits if control, de
gen z_costbenefits = (costbenefits - r(mean)) / r(sd)
la var z_costbenefits "Cost-benefit (std.)"

********************************************************************************
* Cost Benefits
********************************************************************************
gen selfefficacy = (selfefficacy_1 + selfefficacy_2 + selfefficacy_3 + selfefficacy_4) / 4
summ selfefficacy if control, de
gen z_selfefficacy = (selfefficacy - r(mean)) / r(sd)
la var z_selfefficacy "Self-efficacy (std.)"

********************************************************************************
* Awareness
********************************************************************************
gen awareness = (awareness_1 + awareness_2 + awareness_3) / 3
summ awareness if control, de
gen z_awareness = (awareness - r(mean)) / r(sd)
la var z_awareness "Awareness (std.)"


********************************************************************************
* Image
********************************************************************************

gen imagescale = (image_1 + image_2) / 2
summ imagescale, de
gen z_imagescale = (imagescale - r(mean)) / r(sd)
la var z_imagescale "Self/Social Image Scale (std)"
la var imagescale "Self/Social Image Scale"

********************************************************************************
* Social Media better Worse
********************************************************************************

la var smartphone_better_wo "Social media makes life better"
rename smartphone_better_wo smartphone_better_worse 

summ smartphone_better_worse if control, de
gen z_smartphone_better_worse = (smartphone_better_worse - r(mean)) / r(sd)
la var z_smartphone_better_worse "Social media makes life better (std.)"

gen z_smart_bett_wors_revers = z_smartphone_better_worse * (-1)
la var z_smart_bett_wors_revers "Social media makes life worse (std.)"

********************************************************************************
* Posterior Idealtime
********************************************************************************

gen posterior_ideal_social_min = posterior_idealtime_1_1_1 * 60 + posterior_idealtime_1_1_2
label var posterior_ideal_social_min "Posterior ideal social media time (min)"
drop posterior_idealtime_1_1_1 posterior_idealtime_1_1_2

********************************************************************************
* Posterior Prediction
********************************************************************************

gen posterior_actual_social_min = prediction_social_1_1_1 * 60 + prediction_social_1_1_2
label var posterior_actual_social_min "Predicted social media time (min)"
drop prediction_social_1_1_1 prediction_social_1_1_2

* Winsorize
winsor2 posterior_ideal_social_min posterior_actual_social_min, cuts(5 95) suffix(_w)
la var posterior_ideal_social_min_w   "Posterior ideal social media time (min, winsorized)"
la var posterior_actual_social_min_w  "Predicted social media time (min, winsorized)"

********************************************************************************
* Posterior app use intentions over the next four weeks
********************************************************************************

rename app_use_intentions_1 posterior_app_use_plan_tiktok
rename app_use_intentions_2 posterior_app_use_plan_instagram
rename app_use_intentions_3 posterior_app_use_plan_snapchat
rename app_use_intentions_4 posterior_app_use_plan_facebook
rename app_use_intentions_5 posterior_app_use_plan_youtube
rename app_use_intentions_6 posterior_app_use_plan_reddit
rename app_use_intentions_7 posterior_app_use_plan_twitter
la var posterior_app_use_plan_tiktok      "Change in time use over next 4 weeks: TikTok"
la var posterior_app_use_plan_instagram   "Change in time use over next 4 weeks: Instagram"
la var posterior_app_use_plan_snapchat    "Change in time use over next 4 weeks: Snapchat"
la var posterior_app_use_plan_facebook    "Change in time use over next 4 weeks: Facebook"
la var posterior_app_use_plan_youtube     "Change in time use over next 4 weeks: YouTube"
la var posterior_app_use_plan_reddit      "Change in time use over next 4 weeks: Reddit"
la var posterior_app_use_plan_twitter     "Change in time use over next 4 weeks: Twitter"



********************************************************************************
* Change Questionnaire
********************************************************************************

rename change_questionnaire_1 CQ_want_change
label variable CQ_want_change "Want change"

rename change_questionnaire_2 CQ_could_change
label variable CQ_could_change "Could change"

rename change_questionnaire_3 CQ_good_reasons
label variable CQ_good_reasons "Good reasons"

rename change_questionnaire_4 CQ_have_to_reduce
label variable CQ_have_to_reduce "Have to reduce"

rename change_questionnaire_5 CQ_intend_to_reduce
label variable CQ_intend_to_reduce "Intend to reduce"

rename change_questionnaire_6 CQ_trying_to_reduce
label variable CQ_trying_to_reduce "Trying to reduce"

gen CQ_score = (CQ_want_change + CQ_could_change + CQ_good_reasons + CQ_have_to_reduce + CQ_intend_to_reduce + CQ_trying_to_reduce)
summ CQ_score if control, de
gen z_CQ_score = (CQ_score - r(mean)) / r(sd)
la var z_CQ_score "Change Questionnaire score (std.)"


********************************************************************************
* Client Evaluation of Counseling Scale MI
********************************************************************************

* Rename to clearer variable names
rename mi_clientevaluation_1  mi_help_talk_change
rename mi_clientevaluation_2  mi_make_talk_unwanted
rename mi_clientevaluation_3  mi_discuss_need_change
rename mi_clientevaluation_4  mi_discuss_pros_cons
rename mi_clientevaluation_5  mi_argue_change
rename mi_clientevaluation_6  mi_feel_hopeful_change
rename mi_clientevaluation_7  mi_partner_in_change
rename mi_clientevaluation_8  mi_recognize_need_change
rename mi_clientevaluation_9  mi_tell_what_to_do
rename mi_clientevaluation_10 mi_confident_change
rename mi_clientevaluation_11 mi_act_authority
rename mi_clientevaluation_12 mi_feel_pressured_change

label variable mi_help_talk_change      "Help you talk about changing your behavior"
label variable mi_make_talk_unwanted    "Make you talk about something you didn't want to discuss"
label variable mi_discuss_need_change   "Help you discuss your need to change your behavior"
label variable mi_discuss_pros_cons     "Help you discuss the pros and cons of your behavior"
label variable mi_argue_change          "Argued with you to change your behavior"
label variable mi_feel_hopeful_change   "Help you feel hopeful about changing your behavior"
label variable mi_partner_in_change     "Act as a partner in your behavior change"
label variable mi_recognize_need_change "Help you recognize the need to change your behavior"
label variable mi_tell_what_to_do       "Tell you what to do"
label variable mi_confident_change      "Help you feel confident in your ability to change your behavior"
label variable mi_act_authority         "Act as an authority on your life"
label variable mi_feel_pressured_change "Make you feel pressured to change your behavior"


gen mi_score = (mi_help_talk_change + mi_discuss_need_change + mi_discuss_pros_cons + mi_feel_hopeful_change + mi_partner_in_change + mi_recognize_need_change + mi_confident_change) - (mi_make_talk_unwanted + mi_argue_change + mi_tell_what_to_do + mi_act_authority + mi_feel_pressured_change)

summ mi_score if control, de
la var mi_score "Client Evaluation Score (raw)"
gen z_mi_score = (mi_score - r(mean)) / r(sd)
la var z_mi_score "Client Evaluation Score (std.)"


********************************************************************************
* Emotions during interview
********************************************************************************

rename emotions_panas_1 emotions_interested
rename emotions_panas_2 emotions_excited
rename emotions_panas_3 emotions_upset
rename emotions_panas_4 emotions_guilty
rename emotions_panas_5 emotions_irritated
rename emotions_panas_6 emotions_ashamed
rename emotions_panas_7 emotions_determined
rename emotions_panas_8 emotions_encouraged
la var emotions_interested  "Interested"
la var emotions_excited     "Excited"
la var emotions_upset       "Upset"
la var emotions_guilty      "Guilty"
la var emotions_irritated   "Irritated"
la var emotions_ashamed     "Ashamed"
la var emotions_determined  "Determined"
la var emotions_encouraged  "Encouraged"

rename tpb_emotions_2 feelings_about_socialtime_reduce
la var feelings_about_socialtime_reduce "Feelings about reducing social media time"



********************************************************************************
* WTP for freedom app
********************************************************************************

rename current_use uses_screentime_app
la var uses_screentime_app "Uses a screen time management app (0/1)"

rename familiar_freedom familiar_with_freedom
la var familiar_with_freedom "Familiar with Freedom app"

* Dummy for revised WTP estimate
gen respondent_revised_wtp = correct_wtp != 3
la var respondent_revised_wtp "Respondent revised their first WTP estimate (1=yes,0=no)"


* First elicitation: How often is Freedom chosen?
egen n_freedom_1 = anycount(wtp_freedom_1-wtp_freedom_13), values(1)

* Second elicitation: How often is Freedom chosen?
egen n_freedom_2 = anycount(wtp_free_2_1-wtp_free_2_13), values(1)
replace n_freedom_2 = . if missing(wtp_free_2_1)

* Final WTP based on revised responses
gen wtp_count = n_freedom_1 if respondent_revised_wtp == 0
replace wtp_count = n_freedom_2 if respondent_revised_wtp == 1
label var wtp_count "WTP (count)"

* WTP in dollars (using the midpoint of the interval; 0 and 22.5 for never switchers)
gen wtp_dollars = .
replace wtp_dollars = 0   if wtp_count == 0
replace wtp_dollars = 0.5   if wtp_count == 1
replace wtp_dollars = 1.5   if wtp_count == 2
replace wtp_dollars = 2.5   if wtp_count == 3
replace wtp_dollars = 3.5   if wtp_count == 4
replace wtp_dollars = 4.5   if wtp_count == 5
replace wtp_dollars = 5.5   if wtp_count == 6
replace wtp_dollars = 6.5   if wtp_count == 7
replace wtp_dollars = 7.5   if wtp_count == 8
replace wtp_dollars = 8.5   if wtp_count == 9
replace wtp_dollars = 9.5   if wtp_count == 10
replace wtp_dollars = 12.5  if wtp_count == 11
replace wtp_dollars = 17.5  if wtp_count == 12
replace wtp_dollars = 22.5    if wtp_count == 13
la var wtp_dollars "WTP (USD)"

summ wtp_dollars if control, de
gen z_wtp_dollars = (wtp_dollars - r(mean)) / r(sd)
la var z_wtp_dollars "WTP (USD) z-scored"

order wtp_dollars wtp_count, after(changetalk)
drop n_freedom_1 n_freedom_2
drop wtp_free_2_1 wtp_free_2_2 wtp_free_2_3 wtp_free_2_4 wtp_free_2_5 wtp_free_2_6 wtp_free_2_7 wtp_free_2_8 wtp_free_2_9 wtp_free_2_10 wtp_free_2_11 wtp_free_2_12 wtp_free_2_13
drop wtp_freedom_1 wtp_freedom_2 wtp_freedom_3 wtp_freedom_4 wtp_freedom_5 wtp_freedom_6 wtp_freedom_7 wtp_freedom_8 wtp_freedom_9 wtp_freedom_10 wtp_freedom_11 wtp_freedom_12 wtp_freedom_13


********************************************************************************
* Time variables
********************************************************************************

* Fix time variables
drop *_first_click *_click_count *_last_click
rename *_page_submit *

* Convert interview time from seconds to minutes
gen time_interview_minutes = time_interview / 60.0
label var time_interview_minutes "Interview duration (minutes)"
drop time_interview

* Mean and standard deviation
summ time_interview_minutes

* Rename some time variables
rename tim_* time_*
order time_*, last


********************************************************************************
* Demographics: country, gender, age, race, education, income
********************************************************************************

* Country
label var country "Country of residence"
gen country_us = country == 1
label var country_us "Country: United States"
label values country_us yesno
gen country_uk = country == 2
label var country_uk "Country: United Kingdom"
label values country_uk yesno

* Gender
label var gender "Gender (raw)"
gen female = gender == 2
label var female "Female"
label values female yesno

* Age
label var age "Age in years"

* Race / ethnicity
label var race       "Race (US coding)"
label var race_uk    "Race (UK coding)"
label var ethnicity  "Hispanic origin"
rename ethnicity hispanic

gen white = (race == 3) if country_us
replace white = (race_uk == 3) if country_uk

gen black = (race == 1) if country_us
replace black = (race_uk == 1) if country_uk

la var white "Caucasian/White"
la val white yesno
la var black "African American/Black"
la val black yesno

* Employment
gen byte fulltime = (employment == 1)
label var fulltime "Full-time employed"
label values fulltime yesno

gen employed = inlist(employment, 1, 2)
label var employed "Employed (part- or full-time)"
label values employed yesno


* Education
label var education_us "Highest education (US)"
label var education_uk "Highest education (UK)"
gen byte college = 0
replace college = 1 if inlist(education_us, 5, 6)
replace college = 1 if inlist(education_uk, 7, 8)

label var college "College degree"
label values college yesno

* Income
label var income_us "Household income band (USD)"
label var income_uk "Household income band (pounds)"


* 1. Define GBP→USD conversion rate
local gbptousd = 1/0.74

* 2. Create unified income midpoint in USD
generate double income_in_usd = .

* US respondents (income_us already in USD)
replace income_in_usd =  7500   if income_us == 1
replace income_in_usd = 20000   if income_us == 2
replace income_in_usd = 37500   if income_us == 3
replace income_in_usd = 62500   if income_us == 4
replace income_in_usd = 87500   if income_us == 5
replace income_in_usd = 125000  if income_us == 6
replace income_in_usd = 175000  if income_us == 7
replace income_in_usd = 225000  if income_us == 8

* UK respondents (income_uk in GBP → convert midpoints to USD)
replace income_in_usd = 7500*`gbptousd'   if income_uk == 1
replace income_in_usd = 20000*`gbptousd'  if income_uk == 2
replace income_in_usd = 37500*`gbptousd'  if income_uk == 3
replace income_in_usd = 62500*`gbptousd'  if income_uk == 4
replace income_in_usd = 87500*`gbptousd'  if income_uk == 6
replace income_in_usd = 125000*`gbptousd' if income_uk == 5
replace income_in_usd = 175000*`gbptousd' if income_uk == 7
replace income_in_usd = 225000*`gbptousd' if income_uk == 8

label var income_in_usd "Annual household income midpoint"
gen log_income = log(income_in_usd)
label var log_income "Log annual household income"




********************************************************************************
* Control variable: above median baseline social media use
********************************************************************************

summ baseline_actual_social_min, detail
gen byte high_social_media_use = (baseline_actual_social_min > r(p50))
label var high_social_media_use "Actual social media time > median (1=yes,0=no)"

********************************************************************************
* Merge interview scores
********************************************************************************

* Save current data to tempfile to preserve it
tempfile current_data
save `current_data'

* Load the social media dataset (assuming main file is something like social_media.dta)
use "${data_folder}/processed/main_social_media/interview_scores_extracted.dta", clear

* Sort both datasets by prolific_id
sort prolific_id

* Switch back to current data and merge
use `current_data', clear
sort prolific_id
merge 1:1 prolific_id using "${data_folder}/processed/main_social_media/interview_scores_extracted.dta"

* Check merge results
tab _merge
drop _merge

********************************************************************************
* Exoport Data
********************************************************************************

compress
order prolific_id, first
save "${data_folder}/processed/main_social_media/clean_data.dta", replace
