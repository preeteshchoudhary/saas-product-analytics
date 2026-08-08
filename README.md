# SaaS Product Analytics & A/B Testing Engine

![Python](https://img.shields.io/badge/Python-3.10-blue)
![SQL](https://img.shields.io/badge/MySQL-Advanced-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-red)

## 📌 Project Overview
An end-to-end product analytics system for a B2B SaaS platform. Analyzed 10k+ users and 500k+ events to optimize the conversion funnel, evaluate A/B tests with statistical rigor, and track cohort retention. 

👉 **[View Live Dashboard Here](#)** *(Add your Streamlit Cloud link here)*

## 🛠 Tech Stack
- **Database:** MySQL (Window Functions, CTEs, Aggregations)
- **Data Manipulation:** Python (Pandas, NumPy)
- **Statistical Testing:** SciPy (Chi-Squared tests, P-values, Confidence Intervals)
- **Visualization:** Streamlit, Plotly, Seaborn, Matplotlib

## 📊 Key Business Insights
1. **Funnel Bottleneck:** Identified a massive drop-off between onboarding completion and payment success.
2. **A/B Test Shipped:** Proved that the `new_onboarding_flow` yielded a statistically significant conversion lift (p < 0.05), projecting a $45k annualized MRR increase.
3. **Retention Crisis:** Discovered Month-1 churn dropping to 32%, triggering a shift in product strategy towards D7-D30 lifecycle engagement.

## 🚀 How to Run Locally
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd app
streamlit run app.py