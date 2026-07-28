

use "${data_folder}/processed/main_social_media/clean_merged_with_scrshots.dta", replace

* 1. Calculate Regression stats (Slope & SE)
reg w2_actual_social_min_wins verified_prefered_time_w
local beta = trim("`: display %9.3f _b[verified_prefered_time]'")
local se   = trim("`: display %9.3f _se[verified_prefered_time]'")

* 2. Calculate Correlation (Rho) - MUST be done before the plot
corr w2_actual_social_min_wins verified_prefered_time_w
local rho = trim("`: display %9.3f r(rho)'")

* 3. Define position (using your logic)
sum w2_actual_social_min if e(sample), meanonly
local x = r(max)*0.80   // This was calculated but not used in your code, I'll use fixed coords like you did
local y = r(max)*0.90

* 4. Plot
binscatter w2_actual_social_min_wins verified_prefered_time_w, ///
    ytitle("Self-reported social media time (min per day) ", size(medsmall)) ///
    xtitle("Social media time from screenshot (min per day)", size(medsmall)) ///
    title("") ///
    text(100 300 `"{&beta} = `beta'"' "{&rho} = `rho'", size(medsmall) justification(left)) ///
    ylab(0(60)400, labsize(medsmall)) /// 
    xlab(0(60)400, labsize(medsmall)) ///
    ymtick(##4) xmtick(##4) ///
    mcolor(navy) msymbol(O) /// 
    name(MyPlot, replace) xsize(6) ysize(6) ///

* 5. Add 45-degree line
graph addplot function y=x, range(0 400) lcolor(gs10)

graph export "${overleaf}/figures/fig_scrtime_validation_binned_scatter.pdf", replace



*************************************
**** SUR analysis for the paper  ****
*************************************

* no controls
eststo clear 
qui eststo reg1: reg verified_prefered_time_w  i.T  
qui eststo reg2: reg w2_actual_social_min_wins  i.T if !missing(verified_prefered_time_w)

qui suest reg1 reg2,r

test ([reg1_mean]1.T = [reg2_mean]1.T) ([reg1_mean]2.T = [reg2_mean]2.T) ([reg1_mean]3.T = [reg2_mean]3.T)

* with controls
eststo clear 
qui eststo reg1: reg verified_prefered_time_w $controls_followup i.T  
qui eststo reg2: reg w2_actual_social_min_wins $controls_followup i.T if !missing(verified_prefered_time_w)

qui suest reg1 reg2,r

test ([reg1_mean]1.T = [reg2_mean]1.T) ([reg1_mean]2.T = [reg2_mean]2.T) ([reg1_mean]3.T = [reg2_mean]3.T)