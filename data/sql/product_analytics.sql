-- ==============================================================================
-- PART 1: FUNNEL ANALYSIS
-- ==============================================================================

-- Q1: Full Conversion Funnel & Drop-off Rates
-- Identifies how many users make it through each stage of the core product journey.
WITH funnel_steps AS (
    SELECT 
        COUNT(DISTINCT CASE WHEN event_type = 'signup' THEN user_id END) as signups,
        COUNT(DISTINCT CASE WHEN event_type = 'onboarding_start' THEN user_id END) as ob_starts,
        COUNT(DISTINCT CASE WHEN event_type = 'onboarding_complete' THEN user_id END) as ob_completes,
        COUNT(DISTINCT CASE WHEN event_type = 'feature_use' THEN user_id END) as first_feature,
        COUNT(DISTINCT CASE WHEN event_type = 'payment_success' THEN user_id END) as upgrades
    FROM events
)
SELECT 
    signups,
    ob_starts, ROUND((ob_starts/signups)*100, 2) as start_rate,
    ob_completes, ROUND((ob_completes/ob_starts)*100, 2) as completion_rate,
    first_feature, ROUND((first_feature/ob_completes)*100, 2) as feature_rate,
    upgrades, ROUND((upgrades/first_feature)*100, 2) as upgrade_rate,
    ROUND((upgrades/signups)*100, 2) as overall_conversion_rate
FROM funnel_steps;

-- Q2: Funnel Conversion Drop-off by Signup Source
-- Which marketing channel brings users with the highest intent?
SELECT 
    u.signup_source,
    COUNT(DISTINCT e1.user_id) as signups,
    COUNT(DISTINCT e2.user_id) as ob_completes,
    ROUND(COUNT(DISTINCT e2.user_id) / COUNT(DISTINCT e1.user_id) * 100, 2) as completion_rate
FROM users u
LEFT JOIN events e1 ON u.user_id = e1.user_id AND e1.event_type = 'signup'
LEFT JOIN events e2 ON u.user_id = e2.user_id AND e2.event_type = 'onboarding_complete'
GROUP BY u.signup_source
ORDER BY completion_rate DESC;

-- Q3: Funnel Conversion by Platform
SELECT 
    platform,
    COUNT(DISTINCT CASE WHEN event_type = 'signup' THEN user_id END) as signups,
    COUNT(DISTINCT CASE WHEN event_type = 'payment_success' THEN user_id END) as upgrades,
    ROUND(COUNT(DISTINCT CASE WHEN event_type = 'payment_success' THEN user_id END) / 
          COUNT(DISTINCT CASE WHEN event_type = 'signup' THEN user_id END) * 100, 2) as conversion_rate
FROM events
GROUP BY platform;

-- Q4: Time-to-Convert (Days from Signup to Paid)
WITH user_dates AS (
    SELECT 
        u.user_id,
        u.signup_date,
        MIN(s.start_date) as first_payment_date
    FROM users u
    JOIN subscriptions s ON u.user_id = s.user_id
    GROUP BY u.user_id, u.signup_date
)
SELECT 
    AVG(DATEDIFF(first_payment_date, signup_date)) as avg_days_to_convert,
    MAX(DATEDIFF(first_payment_date, signup_date)) as max_days_to_convert
FROM user_dates;

-- ==============================================================================
-- PART 2: COHORT RETENTION
-- ==============================================================================

-- Q5: Monthly Cohort Retention Matrix (Raw Data for Heatmap)
-- Tracks users based on their signup month and counts active users in subsequent months.
WITH cohort_items AS (
    SELECT 
        user_id,
        DATE_FORMAT(signup_date, '%Y-%m-01') as cohort_month
    FROM users
),
user_activities AS (
    SELECT DISTINCT 
        user_id, 
        DATE_FORMAT(start_time, '%Y-%m-01') as activity_month
    FROM sessions
),
cohort_size AS (
    SELECT cohort_month, COUNT(DISTINCT user_id) as total_users
    FROM cohort_items
    GROUP BY cohort_month
)
SELECT 
    c.cohort_month,
    s.total_users,
    TIMESTAMPDIFF(MONTH, c.cohort_month, a.activity_month) as month_number,
    COUNT(DISTINCT a.user_id) as active_users,
    ROUND(COUNT(DISTINCT a.user_id) / s.total_users * 100, 2) as retention_pct
FROM cohort_items c
JOIN user_activities a ON c.user_id = a.user_id
JOIN cohort_size s ON c.cohort_month = s.cohort_month
WHERE TIMESTAMPDIFF(MONTH, c.cohort_month, a.activity_month) >= 0
GROUP BY c.cohort_month, s.total_users, month_number
ORDER BY c.cohort_month, month_number;

-- ==============================================================================
-- PART 3: ENGAGEMENT & REVENUE METRICS
-- ==============================================================================

-- Q9: DAU, MAU, and Stickiness Ratio
-- High stickiness (>20%) means the product is a daily habit.
WITH daily_active AS (
    SELECT DATE(start_time) as activity_date, COUNT(DISTINCT user_id) as dau
    FROM sessions GROUP BY DATE(start_time)
),
monthly_active AS (
    SELECT DATE_FORMAT(start_time, '%Y-%m-01') as activity_month, COUNT(DISTINCT user_id) as mau
    FROM sessions GROUP BY DATE_FORMAT(start_time, '%Y-%m-01')
)
SELECT 
    d.activity_date,
    d.dau,
    m.mau,
    ROUND((d.dau / m.mau) * 100, 2) as stickiness_ratio
FROM daily_active d
JOIN monthly_active m ON DATE_FORMAT(d.activity_date, '%Y-%m-01') = m.activity_month
ORDER BY d.activity_date;

-- Q10: Power User Identification
WITH monthly_sessions AS (
    SELECT user_id, DATE_FORMAT(start_time, '%Y-%m') as month, COUNT(session_id) as total_sessions
    FROM sessions
    GROUP BY user_id, DATE_FORMAT(start_time, '%Y-%m')
)
SELECT 
    month,
    COUNT(CASE WHEN total_sessions >= 20 THEN user_id END) as power_users,
    COUNT(user_id) as total_active_users,
    ROUND(COUNT(CASE WHEN total_sessions >= 20 THEN user_id END) / COUNT(user_id) * 100, 2) as power_user_pct
FROM monthly_sessions
GROUP BY month
ORDER BY month;

-- Q11: Feature Adoption Rates
WITH active_base AS (
    SELECT COUNT(DISTINCT user_id) as total_users FROM users
)
SELECT 
    f.feature_name,
    COUNT(DISTINCT f.user_id) as users_adopted,
    ROUND(COUNT(DISTINCT f.user_id) / b.total_users * 100, 2) as adoption_rate
FROM features f
CROSS JOIN active_base b
GROUP BY f.feature_name, b.total_users
ORDER BY adoption_rate DESC;

-- Q12: Monthly Recurring Revenue (MRR) Growth
SELECT 
    DATE_FORMAT(start_date, '%Y-%m-01') as revenue_month,
    SUM(mrr) as total_mrr
FROM subscriptions
GROUP BY DATE_FORMAT(start_date, '%Y-%m-01')
ORDER BY revenue_month;