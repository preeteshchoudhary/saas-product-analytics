import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_mrr_trend(subs):
    subs['month'] = pd.to_datetime(subs['start_date']).dt.to_period('M').astype(str)
    mrr_trend = subs.groupby('month')['mrr'].sum().reset_index()
    fig = px.line(mrr_trend, x='month', y='mrr', title="MRR Growth Trend", markers=True, 
                  color_discrete_sequence=['#2A9D8F'])
    return fig

def plot_funnel(events):
    funnel_steps = ['signup', 'onboarding_start', 'onboarding_complete', 'feature_use', 'payment_success']
    counts = events['event_type'].value_counts().reindex(funnel_steps).reset_index()
    counts.columns = ['Stage', 'Users']
    fig = go.Figure(go.Funnel(y=counts['Stage'], x=counts['Users'], marker={"color": "#E9C46A"}))
    fig.update_layout(title="Core Product Conversion Funnel")
    return fig
    