********************************************************************************
* 1. Prepare Survey Data (Clean Data)
* Analogous to: survey_data = pd.read_stata(...)
********************************************************************************
use "${data_folder}/processed/main_social_media/clean_data.dta", clear

* Keep only necessary variables
keep T user_id_raw

* Ensure user_id_raw is integer
capture destring user_id_raw, replace
recast long user_id_raw, force

* Save as tempfile for merging
tempfile survey_data_merge
save `survey_data_merge'

********************************************************************************
* 2. Prepare Chats Data (Raw)
********************************************************************************
import delimited "${raw_folder}/main_socialmedia/chats_raw.csv", clear ///
    delimiter(",") bindquote(strict) maxquotedrows(unlimited) encoding(utf8)

* Create user_id_raw from session_id
gen user_id_raw_str = substr(session_id, strrpos(session_id, "-") + 1, .)
destring user_id_raw_str, gen(user_id_raw) force
drop user_id_raw_str

********************************************************************************
* 3. Merge
* Analogous to: df.merge(..., on="user_id_raw", how="left", validate="many_to_one")
********************************************************************************
merge m:1 user_id_raw using `survey_data_merge', keep(master match) nogenerate

* Verify structure (Optional)
describe

sort user_id_raw order
compress
save "${data_folder}/processed/main_social_media/clean_chat_data.dta", replace
