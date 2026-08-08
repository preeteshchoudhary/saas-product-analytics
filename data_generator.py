import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import uuid
import os

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Set seeds for reproducibility
np.random.seed(42)
random.seed(42)

# --- CONFIGURATION ---
NUM_USERS = 10000
START_DATE = datetime(2025, 6, 1)
END_DATE = datetime(2026, 5, 31)
DATE_RANGE = (END_DATE - START_DATE).days

SOURCES = ['organic', 'paid_google', 'paid_facebook', 'referral', 'direct']
SOURCE_PROBS = [0.40, 0.25, 0.15, 0.10, 0.10]

PLANS = ['free', 'basic', 'pro', 'enterprise']
PLAN_PROBS = [0.60, 0.25, 0.10, 0.05]
PLAN_MRR = {'free': 0, 'basic': 19, 'pro': 49, 'enterprise': 199}

PLATFORMS = ['web', 'ios', 'android']
PLATFORM_PROBS = [0.70, 0.20, 0.10]

print("Starting SaaS synthetic data generation...")

# --- 1. USERS TABLE ---
print("Generating Users...")
user_ids = [str(uuid.uuid4()) for _ in range(NUM_USERS)]
signup_offsets = np.random.randint(0, DATE_RANGE, NUM_USERS)
signup_dates = [START_DATE + timedelta(days=int(offset)) for offset in signup_offsets]

# Simulate churn
# Free users churn ~30% in first 30 days. Paid churn ~10%.
churn_flags = []
plans_array = np.random.choice(PLANS, NUM_USERS, p=PLAN_PROBS)

for plan in plans_array:
    if plan == 'free':
        churn_flags.append(np.random.random() < 0.35) # 35% churn for free
    else:
        churn_flags.append(np.random.random() < 0.12) # 12% churn for paid

users_df = pd.DataFrame({
    'user_id': user_ids,
    'signup_date': signup_dates,
    'signup_source': np.random.choice(SOURCES, NUM_USERS, p=SOURCE_PROBS),
    'plan_type': plans_array,
    'country': np.random.choice(['US', 'UK', 'CA', 'IN', 'AU', 'DE', 'FR'], NUM_USERS, p=[0.45, 0.15, 0.10, 0.10, 0.05, 0.05, 0.10]),
    'industry': np.random.choice(['Tech', 'Retail', 'Finance', 'Healthcare', 'Education'], NUM_USERS),
    'is_churned': churn_flags
})
users_df['signup_date'] = pd.to_datetime(users_df['signup_date']).dt.date

# --- 2. AB TESTS TABLE ---
print("Generating A/B Tests...")
ab_users = []
ab_experiments = []
ab_variants = []
ab_dates = []

for idx, row in users_df.iterrows():
    # Onboarding test (50/50 split)
    ab_users.append(row['user_id'])
    ab_experiments.append('new_onboarding_flow')
    ab_variants.append(np.random.choice(['control', 'treatment']))
    ab_dates.append(row['signup_date'])
    
    # Pricing test (random subset of users, 50/50 split)
    if random.random() < 0.6:  
        ab_users.append(row['user_id'])
        ab_experiments.append('pricing_page_redesign')
        ab_variants.append(np.random.choice(['control', 'treatment']))
        ab_dates.append(row['signup_date'] + timedelta(days=random.randint(1, 14)))

ab_tests_df = pd.DataFrame({
    'user_id': ab_users,
    'experiment_name': ab_experiments,
    'variant': ab_variants,
    'assigned_date': ab_dates
})

# --- 3. SUBSCRIPTIONS TABLE ---
print("Generating Subscriptions...")
sub_ids = []
sub_users = []
sub_plans = []
sub_starts = []
sub_ends = []
sub_mrr = []

for idx, row in users_df.iterrows():
    if row['plan_type'] != 'free':
        sub_ids.append(str(uuid.uuid4()))
        sub_users.append(row['user_id'])
        sub_plans.append(row['plan_type'])
        
        upgrade_delay = random.randint(1, 45)
        start_date = row['signup_date'] + timedelta(days=upgrade_delay)
        sub_starts.append(start_date)
        
        sub_mrr.append(PLAN_MRR[row['plan_type']])
        
        if row['is_churned']:
            churn_delay = random.randint(30, 180)
            sub_ends.append(start_date + timedelta(days=churn_delay))
        else:
            sub_ends.append(None)

subs_df = pd.DataFrame({
    'subscription_id': sub_ids,
    'user_id': sub_users,
    'plan': sub_plans,
    'start_date': sub_starts,
    'end_date': sub_ends,
    'mrr': sub_mrr
})

# --- 4 & 5. SESSIONS & EVENTS TABLE ---
print("Generating Sessions and Events (This takes a moment)...")
session_records = []
event_records = []

EVENT_FUNNEL = ['page_view', 'signup', 'onboarding_start', 'onboarding_complete', 'feature_use', 'invite_sent', 'upgrade_click', 'payment_success']
FEATURES = ['dashboard', 'reports', 'integrations', 'automations', 'api_access']

onboarding_variants = ab_tests_df[ab_tests_df['experiment_name'] == 'new_onboarding_flow'].set_index('user_id')['variant'].to_dict()

for idx, row in users_df.iterrows():
    user = row['user_id']
    signup = row['signup_date']
    is_churned = row['is_churned']
    plan = row['plan_type']
    
    if is_churned:
        num_sessions = random.randint(1, 10)
        active_days = random.randint(1, 45)
    elif plan == 'free':
        num_sessions = random.randint(5, 30)
        active_days = random.randint(10, 150)
    else: 
        num_sessions = random.randint(20, 150)
        active_days = random.randint(30, 300)
        
    for i in range(num_sessions):
        session_id = str(uuid.uuid4())
        session_date = signup + timedelta(days=random.randint(0, active_days))
        
        if session_date.weekday() >= 5 and random.random() < 0.6:
            continue
            
        platform = np.random.choice(PLATFORMS, p=PLATFORM_PROBS)
        pages_viewed = random.randint(1, 8)
        
        session_records.append({
            'session_id': session_id,
            'user_id': user,
            'start_time': pd.Timestamp(session_date) + pd.Timedelta(hours=random.randint(6, 22), minutes=random.randint(0, 59)),
            'pages_viewed': pages_viewed,
            'platform': platform
        })
        
        num_events = random.randint(1, pages_viewed)
        for e in range(num_events):
            if i == 0: 
                funnel_depth = random.randint(1, 4)
                variant = onboarding_variants.get(user, 'control')
                if variant == 'treatment' and random.random() < 0.30: 
                    funnel_depth = 4 
                
                event_type = EVENT_FUNNEL[min(e, funnel_depth-1)]
            else:
                event_type = np.random.choice(['feature_use', 'feature_use', 'page_view', 'invite_sent', 'upgrade_click'])
            
            event_records.append({
                'event_id': str(uuid.uuid4()),
                'user_id': user,
                'session_id': session_id,
                'event_type': event_type,
                'event_timestamp': session_records[-1]['start_time'] + pd.Timedelta(minutes=e*random.randint(1,5)),
                'platform': platform
            })

sessions_df = pd.DataFrame(session_records)
events_df = pd.DataFrame(event_records)

sessions_df['end_time'] = sessions_df['start_time'] + pd.to_timedelta(sessions_df['pages_viewed'] * np.random.randint(1, 5, len(sessions_df)), unit='m')

# --- 6. FEATURES TABLE ---
print("Generating Features...")
feature_records = []
for user in users_df['user_id']:
    if users_df.loc[users_df['user_id']==user, 'is_churned'].iloc[0] and random.random() < 0.5:
        continue 
        
    num_features = random.randint(1, len(FEATURES))
    used_features = random.sample(FEATURES, num_features)
    
    for f in used_features:
        feature_records.append({
            'user_id': user,
            'feature_name': f,
            'first_used_date': users_df.loc[users_df['user_id']==user, 'signup_date'].iloc[0] + timedelta(days=random.randint(1, 10)),
            'times_used_30d': random.randint(1, 50)
        })

features_df = pd.DataFrame(feature_records)

users_df = users_df.drop(columns=['is_churned'])

# --- EXPORT TO CSV ---
print("Exporting data to CSV in /data directory...")
users_df.to_csv('data/users.csv', index=False)
events_df.to_csv('data/events.csv', index=False)
sessions_df.to_csv('data/sessions.csv', index=False)
subs_df.to_csv('data/subscriptions.csv', index=False)
ab_tests_df.to_csv('data/ab_tests.csv', index=False)
features_df.to_csv('data/features.csv', index=False)

print("Data generation complete! Data saved to the 'data' folder.")