import scipy.stats as stats
import math

def run_ab_test(control_conversions, control_total, treatment_conversions, treatment_total):
    rate_con = control_conversions / control_total
    rate_treat = treatment_conversions / treatment_total
    
    chi2, p_val, _, _ = stats.chi2_contingency([
        [control_conversions, control_total - control_conversions],
        [treatment_conversions, treatment_total - treatment_conversions]
    ])
    
    lift = rate_treat - rate_con
    significant = p_val < 0.05
    
    return rate_con, rate_treat, lift, p_val, significant