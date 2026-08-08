import streamlit as st
import pandas as pd
from data_loader import load_data
from visualizations import plot_mrr_trend, plot_funnel
from ab_testing import run_ab_test

# --- Page Config ---
st.set_page_config(page_title="SaaS Analytics | Portfolio", layout="wide")

# --- Load Data ---
users, events, sessions, subs, ab_tests = load_data()

# --- Sidebar ---
st.sidebar.title("SaaS Analytics")
page = st.sidebar.radio("Navigation", ["Executive Dashboard", "Funnel Analysis", "A/B Testing", "Metrics Health"])

st.sidebar.markdown("---")
st.sidebar.info("Built by Preetesh Choudhary\n\nData Analyst Portfolio Project")

# --- Page 1: Executive Dashboard ---
if page == "Executive Dashboard":
    st.title("Executive Dashboard")
    
    # KPIs
    total_users = users['user_id'].nunique()
    total_mrr = subs['mrr'].sum()
    dau = sessions[sessions['start_time'].dt.date == sessions['start_time'].dt.date.max()]['user_id'].nunique()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", f"{total_users:,}", "+12% MoM")
    col2.metric("Total MRR", f"${total_mrr:,.2f}", "+8% MoM")
    col3.metric("Latest DAU", f"{dau:,}", "-2% WoW")
    
    st.plotly_chart(plot_mrr_trend(subs), use_container_width=True)

# --- Page 2: Funnel Analysis ---
elif page == "Funnel Analysis":
    st.title("Funnel Analysis")
    st.markdown("Analyzing drop-offs from Signup to Paid Upgrade.")
    
    st.plotly_chart(plot_funnel(events), use_container_width=True)
    
    st.subheader("Key Insight")
    st.warning("Massive drop-off between onboarding_complete and payment_success. Recommend introducing an in-app activation prompt.")

# --- Page 3: A/B Testing ---
elif page == "A/B Testing":
    st.title("A/B Test Results")
    
    experiment = st.selectbox("Select Experiment", ["New Onboarding Flow", "Pricing Page Redesign"])
    
    if experiment == "New Onboarding Flow":
        st.subheader("Hypothesis: Simplified onboarding increases completion rate.")
        rate_c, rate_t, lift, p_val, is_sig = run_ab_test(1450, 5000, 1600, 5000) # Mocked aggregated numbers for UI speed
        
        col1, col2 = st.columns(2)
        col1.metric("Control Conversion", f"{rate_c:.2%}")
        col2.metric("Treatment Conversion", f"{rate_t:.2%}", f"{lift:+.2%} Lift")
        
        st.write(f"**P-Value:** {p_val:.5f}")
        if is_sig:
            st.success("Decision: SHIP IT. The result is statistically significant.")
        else:
            st.error("Decision: DO NOT SHIP. Result is not significant.")

# --- Page 4: Metrics Health ---
elif page == "Metrics Health":
    st.title("Business Metrics Health")
    
    metrics_data = {
        "Metric": ["Activation Rate", "D30 Retention", "Gross Churn", "Stickiness (DAU/MAU)"],
        "Value": ["45%", "32%", "4.5%", "18%"],
        "Benchmark": ["40-60%", "40%", "<3%", "20%"],
        "Status": ["🟢 Healthy", "🔴 Critical", "🔴 Critical", "🟡 Warning"]
    }
    st.table(pd.DataFrame(metrics_data))