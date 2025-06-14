import streamlit as st
import pandas as pd
import altair as alt

# Load data
df = pd.read_csv("social_media_vs_productivity 2.csv")

st.title("📉 Social Media, Productivity & Human Patterns")

# -----------------------
# 📌 SIDEBAR CONTROLS
# -----------------------
st.sidebar.header("🔧 Filter Controls")

# --- DROPDOWNS ---
platform_options = sorted(df['social_platform_preference'].dropna().unique())
platform_filter = st.sidebar.multiselect(
    "Preferred Platform(s)", platform_options, default=platform_options,
    help="Filter users based on their preferred social media platform."
)

# --- MULTISELECTS ---
gender_options = sorted(df['gender'].dropna().unique())
gender_filter = st.sidebar.multiselect(
    "Select Gender(s)", gender_options, default=gender_options,
    help="Filter the dataset by gender identity."
)

job_options = sorted(df['job_type'].dropna().unique())
job_filter = st.sidebar.multiselect(
    "Select Job Type(s)", job_options, default=job_options,
    help="Select one or more job sectors to include in the analysis."
)

# --- SLIDERS ---
min_stress = int(df['stress_level'].min())
max_stress = int(df['stress_level'].max())
stress_range = st.sidebar.slider(
    "Stress Level Range", min_value=min_stress, max_value=max_stress,
    value=(min_stress, max_stress), help="Filter users based on their reported stress levels."
)

min_sleep = float(df['sleep_hours'].min())
max_sleep = float(df['sleep_hours'].max())
sleep_range = st.sidebar.slider(
    "Sleep Hours Range", min_value=round(min_sleep,1), max_value=round(max_sleep,1),
    value=(round(min_sleep,1), round(max_sleep,1)),
    help="Filter users by the number of hours they sleep per night."
)

# --- CHECKBOXES ---
show_focus_users = st.sidebar.checkbox(
    "Only Show Users Who Use Focus Apps", value=False,
    help="Include only those who use digital focus tools like app blockers or Pomodoro apps."
)

only_digital_wellbeing = st.sidebar.checkbox(
    "Only Show Users with Digital Wellbeing Enabled", value=False,
    help="Restrict dataset to users who have enabled screen-time or wellbeing features on their device."
)

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

The goal is to understand how lifestyle choices and digital behaviors influence productivity — both real and perceived.
""")

# -----------------------
# 📊 CHART SET 1: Gender
# -----------------------
st.markdown("""
### 👥 Habitual Patterns Across Genders

Although men and women may vary in work sector or screen time, the visualized data suggests that humans follow **habitual patterns**. 
The first two charts reveal that while gender may influence the **average work hours**, the relationship between social media use and productivity-related time investment is **remarkably consistent** across genders.
""")

gender_selection = alt.selection_multi(fields=["gender"])

chart2 = alt.Chart(df).mark_bar().encode(
    x=alt.X("gender:N", axis=alt.Axis(labelAngle=0), title="Gender"),
    y=alt.Y("mean(work_hours_per_day):Q", title="Avg Work Hours"),
    color=alt.condition(gender_selection, "gender:N", alt.value("lightgray")),
    tooltip=["gender", "mean(work_hours_per_day):Q"]
).add_selection(gender_selection).properties(
    width=400, height=400,
    title="👥 Avg Work Hours by Gender (Click to Filter Chart 1)"
)

chart1 = alt.Chart(df).transform_filter(
    gender_selection
).mark_circle(size=70).encode(
    x=alt.X("daily_social_media_time:Q", title="Daily Social Media Time (hrs)", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("work_hours_per_day:Q", title="Work Hours Per Day"),
    color="gender:N",
    tooltip=["gender", "job_type", "daily_social_media_time", "work_hours_per_day"]
).properties(
    width=400, height=400,
    title="📱 Social Media Time vs Work Hours"
)

st.altair_chart(chart2 | chart1)

# -----------------------
# 📊 CHART SET 2: Platform
# -----------------------
st.markdown("""
### 📊 Platforms, Stress, and Productivity

Different platforms shape our interaction with digital environments. This pair of charts shows that **platform preference correlates** with perceived stress and actual productivity. 
While platform choice may reflect a user's habits or age group, it also affects how efficiently they work — and how overwhelmed they feel. 
""")

platform_selection = alt.selection_multi(fields=["social_platform_preference"])

# Bar chart base
base_chart3 = alt.Chart(df).mark_bar().encode(
    x=alt.X("social_platform_preference:N", axis=alt.Axis(labelAngle=0), title="Preferred Platform"),
    y=alt.Y("mean(actual_productivity_score):Q", title="Avg Actual Productivity", scale=alt.Scale(domain=[4.5, 5])),
    color=alt.condition(platform_selection, "social_platform_preference:N", alt.value("lightgray")),
    tooltip=["social_platform_preference", "mean(actual_productivity_score):Q"]
).add_selection(platform_selection).properties(
    width=400, height=400,
    title="📊 Productivity by Platform (Click to Filter Chart 4)"
)

# Text labels on bars
labels = alt.Chart(df).mark_text(
    align='center', baseline='bottom', dy=-4, fontSize=12
).encode(
    x=alt.X("social_platform_preference:N"),
    y=alt.Y("mean(actual_productivity_score):Q", scale=alt.Scale(domain=[4.5, 5])),
    text=alt.Text("mean(actual_productivity_score):Q", format=".2f")
).transform_filter(platform_selection)

chart3 = base_chart3 + labels

# Scatter chart
chart4 = alt.Chart(df).transform_filter(
    platform_selection
).mark_circle(size=70).encode(
    x=alt.X("stress_level:Q", title="Stress Level", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("actual_productivity_score:Q", title="Actual Productivity Score"),
    color=alt.Color("social_platform_preference:N", legend=alt.Legend(title="Platform")),
    tooltip=["social_platform_preference", "stress_level", "actual_productivity_score"]
).properties(
    width=400, height=400,
    title="😵 Stress vs Productivity (by Platform)"
)

st.altair_chart(chart3 | chart4)
