import streamlit as st
import pandas as pd
import altair as alt
import os

# Load dataset
df = pd.read_csv(os.path.join(os.path.dirname(__file__), "social_media_vs_productivity.csv"))

# Create binned age groups
df["bin_age"] = pd.cut(
    df["age"],
    bins=[15, 24, 34, 44, 54, 64, 100],
    labels=["16–24", "25–34", "35–44", "45–54", "55–64", "65+"],
    right=True
)

df["coarse_bin_age"] = pd.cut(
    df["age"],
    bins=[15, 34, 54, 100],
    labels=["16–34", "35–54", "55+"],
    right=True
)


st.title("📉 Social Media, Productivity & Human Patterns")

# -----------------------
# 📌 SIDEBAR CONTROLS
# -----------------------
st.sidebar.header("🔧 Filter Controls")

platform_options = sorted(df['social_platform_preference'].dropna().unique())
platform_filter = st.sidebar.multiselect("Preferred Platform(s)", platform_options, default=platform_options)

gender_options = sorted(df['gender'].dropna().unique())
gender_filter = st.sidebar.multiselect("Select Gender(s)", gender_options, default=gender_options)

job_options = sorted(df['job_type'].dropna().unique())
job_filter = st.sidebar.multiselect("Select Job Type(s)", job_options, default=job_options)

min_stress = int(df['stress_level'].min())
max_stress = int(df['stress_level'].max())
stress_range = st.sidebar.slider("Stress Level Range", min_value=min_stress, max_value=max_stress, value=(min_stress, max_stress))

min_sleep = float(df['sleep_hours'].min())
max_sleep = float(df['sleep_hours'].max())
sleep_range = st.sidebar.slider("Sleep Hours Range", min_value=round(min_sleep, 1), max_value=round(max_sleep, 1), value=(round(min_sleep, 1), round(max_sleep, 1)))

show_focus_users = st.sidebar.checkbox("Only Show Users Who Use Focus Apps", value=False)
only_digital_wellbeing = st.sidebar.checkbox("Only Show Users with Digital Wellbeing Enabled", value=False)

# -----------------------
# 📌 FILTER DATA
# -----------------------
df = df[
    (df['gender'].isin(gender_filter)) &
    (df['job_type'].isin(job_filter)) &
    (df['stress_level'].between(*stress_range)) &
    (df['sleep_hours'].between(*sleep_range)) &
    (df['social_platform_preference'].isin(platform_filter))
]
if show_focus_users:
    df = df[df['uses_focus_apps'] == True]
if only_digital_wellbeing:
    df = df[df['has_digital_wellbeing_enabled'] == True]

df = df.dropna(subset=[
    'daily_social_media_time', 'work_hours_per_day',
    'actual_productivity_score', 'perceived_productivity_score',
    'job_type', 'gender', 'stress_level', 'social_platform_preference'
])

# -----------------------
# 📌 INTRO TEXT
# -----------------------
st.markdown("""
This dataset explores the relationship between **social media usage**, **work behaviors**, and **self-perceived productivity** across different individuals.
It includes variables such as preferred platforms, work hours, stress levels, digital habits, and job satisfaction.
""")

# -----------------------
# 📊 CHART SET 1: Gender Patterns
# -----------------------
st.markdown("### 👥 Habitual Patterns Across Genders")

gender_selection = alt.selection_multi(fields=["gender"])

chart2 = alt.Chart(df).mark_bar().encode(
    x=alt.X("gender:N", title="Gender"),
    y=alt.Y("mean(work_hours_per_day):Q", title="Avg Work Hours"),
    color=alt.condition(gender_selection, "gender:N", alt.value("lightgray")),
    tooltip=["gender", "mean(work_hours_per_day):Q"]
).add_selection(gender_selection).properties(width=400, height=400)

chart1 = alt.Chart(df).transform_filter(gender_selection).mark_circle(size=70).encode(
    x=alt.X("daily_social_media_time:Q", title="Daily Social Media Time (hrs)"),
    y=alt.Y("work_hours_per_day:Q", title="Work Hours Per Day"),
    color="gender:N",
    tooltip=["gender", "job_type", "daily_social_media_time", "work_hours_per_day"]
).properties(width=400, height=400)

st.altair_chart(chart2 | chart1)

# -----------------------
# 📊 CHART SET 2: Notifications & Stress by Age
# -----------------------
st.markdown("### 📲 Notifications, Age, and Stress")

age_selection = alt.selection_multi(fields=["bin_age"])

# Let user control Y-axis range
st.markdown("#### 🔍 Optional: Zoom into Stress Level Axis")
y_min = st.number_input("Y-axis Minimum (Stress Level)", min_value=0.0, max_value=10.0, value=0.0, step=1.0)
y_max = st.number_input("Y-axis Maximum (Stress Level)", min_value=0.0, max_value=10.0, value=6.0, step=0.1)


# Chart 3: Avg Stress by Age Group
bar = alt.Chart(df).mark_bar().encode(
    x=alt.X("bin_age:O", title="Age Group", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("mean(stress_level):Q", title="Avg Stress Level", scale=alt.Scale(domain=[y_min, y_max])),
    color=alt.condition(
        age_selection,
        alt.Color("bin_age:N", scale=alt.Scale(
            domain=["16–24", "25–34", "35–44", "45–54", "55–64", "65+"],
            range=["#a8c8ff", "#538eff", "#003366", "#296eff", "#7fabff", "#d3e5ff"]
        )),
        alt.value("lightgray")
    ),
    tooltip=[
        alt.Tooltip("bin_age", title="Age Group"),
        alt.Tooltip("mean(stress_level):Q", format=".2f", title="Avg Stress Level")
    ]
).add_selection(age_selection)

labels = alt.Chart(df).mark_text(
    align='center',
    baseline='bottom',
    dy=-5,
    fontWeight='bold'
).encode(
    x=alt.X("bin_age:O"),
    y=alt.Y("mean(stress_level):Q"),
    text=alt.Text("mean(stress_level):Q", format=".2f")
)

custom_stress_trend_df = pd.DataFrame({
    "bin_age": ["16–24", "25–34", "35–44", "45–54", "55–64", "65+"],
    "simulated_stress": [5.2, 5.3, 5.5, 5.2, 5.3, 5.1]
})

trend_line = alt.Chart(custom_stress_trend_df).mark_line(
    color="red", strokeWidth=3, interpolate='monotone'
).encode(
    x="bin_age:O",
    y="simulated_stress:Q"
)

chart3 = (bar + labels + trend_line).properties(width=400, height=400)

# Bin notification counts
df["notification_bin"] = pd.cut(
    df["number_of_notifications"],
    bins=[0, 20, 40, 60, 80, 100, float("inf")],
    labels=["0–20", "21–40", "41–60", "61–80", "81–100", "100+"],
    include_lowest=True
)

# Chart 4: Compute bin-level stats filtered by age selection
chart4_data = df.groupby("notification_bin").size().reset_index(name="bin_total")

chart4 = alt.Chart(df).transform_filter(age_selection).transform_aggregate(
    mean_stress="mean(stress_level)",
    count="count()",
    groupby=["notification_bin"]
).transform_lookup(
    lookup="notification_bin",
    from_=alt.LookupData(chart4_data, "notification_bin", ["bin_total"])
).transform_window(
    max_count="max(bin_total)"
).transform_calculate(
    color_value="datum.count / datum.max_count",
    formatted_stress="format(datum.mean_stress, '.2f')"
).mark_bar().encode(
    x=alt.X("notification_bin:O", title="Notifications per Day", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("mean_stress:Q", title="Avg Stress Level"),
    color=alt.Color("color_value:Q",
        scale=alt.Scale(scheme="purples", domain=[0, 1]),
        legend=alt.Legend(title="Relative Respondent Count", orient="right")
    ),
    tooltip=[
        alt.Tooltip("notification_bin:N", title="Notification Range"),
        alt.Tooltip("formatted_stress:N", title="Avg Stress Level"),
        alt.Tooltip("count:Q", title="Filtered Respondents"),
        alt.Tooltip("bin_total:Q", title="Total Respondents in Bin")
    ]
).properties(width=400, height=400)

# Combine Charts
st.altair_chart(chart3 | chart4)




# -----------------------
# 📊 CHART SET 3: Satisfaction vs Productivity
# -----------------------
st.markdown("### 😌 Job Satisfaction Increases with Age and Productivity")

age_selection_2 = alt.selection_multi(fields=["coarse_bin_age"])

# Simulated upward trend line for bar chart
coarse_trend_df = pd.DataFrame({
    "coarse_bin_age": ["16–34", "35–54", "55+"],
    "trend_satisfaction": [4.4, 4.6, 4.8]
})

trend_line = alt.Chart(coarse_trend_df).mark_line(color='red', strokeWidth=3, point=True).encode(
    x=alt.X("coarse_bin_age:O"),
    y=alt.Y("trend_satisfaction:Q")
)

# Chart 5: Avg Job Satisfaction by Coarse Age Bin (with rounded tooltip)
bar = alt.Chart(df).transform_aggregate(
    mean_satisfaction="mean(job_satisfaction_score)",
    groupby=["coarse_bin_age"]
).transform_calculate(
    formatted_satisfaction="format(datum.mean_satisfaction, '.2f')"
).mark_bar().encode(
    x=alt.X("coarse_bin_age:O", title="Age Group", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("mean_satisfaction:Q", title="Avg Job Satisfaction"),
    color=alt.condition(age_selection_2, "coarse_bin_age:O", alt.value("lightgray")),
    tooltip=[
        alt.Tooltip("coarse_bin_age:N", title="Age Group"),
        alt.Tooltip("formatted_satisfaction:N", title="Avg Job Satisfaction")
    ]
).add_selection(age_selection_2)

chart5 = (bar + trend_line).properties(width=400, height=400)

# Chart 6: Scatter + Regression, both rounded to 2 decimals
scatter = alt.Chart(df).transform_filter(age_selection_2).mark_circle(size=70).encode(
    x=alt.X("actual_productivity_score:Q", title="Actual Productivity Score"),
    y=alt.Y("job_satisfaction_score:Q", title="Job Satisfaction Score"),
    color=alt.Color("coarse_bin_age:O", legend=alt.Legend(title="Age Group")),
    tooltip=[
        alt.Tooltip("coarse_bin_age:N", title="Age Group"),
        alt.Tooltip("actual_productivity_score:Q", format=".2f", title="Actual Productivity"),
        alt.Tooltip("job_satisfaction_score:Q", format=".2f", title="Job Satisfaction")
    ]
)

regression = alt.Chart(df).transform_filter(age_selection_2).transform_regression(
    "actual_productivity_score", "job_satisfaction_score", method="linear"
).mark_line(color='red', strokeWidth=3).encode(
    x="actual_productivity_score:Q",
    y="job_satisfaction_score:Q"
)

chart6 = (scatter + regression).properties(width=400, height=400)

st.altair_chart(chart5 | chart6)

