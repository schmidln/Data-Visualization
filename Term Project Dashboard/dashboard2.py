import streamlit as st
import pandas as pd
import altair as alt
import os
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import io

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


st.title("A Key to a Healthy & Happy Life: Finding a Job You Love")

# -----------------------
# 📌 SIDEBAR CONTROLS
# -----------------------
st.sidebar.header("🔧 Filter Controls")
st.sidebar.markdown("""
Use the filters below to explore the dataset and customize the visualizations. Please be patient as some charts may take a moment to load based on your selections.
""")

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
The prevailing question for anyone new to the workforce is often **how does our work affect our stress levels, specifically with age?** This dashboard
explores this by investigating stress levels, job satisfaction, and notification counts across different age groups.
""")

st.markdown("<br><br>", unsafe_allow_html=True)

# -----------------------
# 📊 CHART SET 1: Notifications & Stress by Age
# -----------------------
st.markdown("### 📲 Stress May Decrease with Age and Notifications")
st.markdown(
    "<div style='font-size:0.9rem; color:gray;'>Try clicking the bars in the Age vs Stress chart to learn more about each age group's notification usage.</div>",
    unsafe_allow_html=True
)

st.markdown("<br><br>", unsafe_allow_html=True)

age_selection = alt.selection_multi(fields=["bin_age"])

# Let user control Y-axis range
with st.container():
    subcol1, subcol2, subcol3 = st.columns([0.03, 0.64, 0.33])  # Centered with margins

    with subcol2:
        col1, col2 = st.columns(2)

    with col1:
        y_min = st.number_input(
            "Y-axis Min (Stress)",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=1.0,
            help="Controls the lower bound of the Y-axis in Age vs Stress Chart. Recommended: 5.0.\nNote: Adjusting the scale may exaggerate perceived trends—use cautiously to avoid misleading interpretations."
        )

    with col2:
        y_max = st.number_input(
            "Y-axis Max (Stress)",
            min_value=0.0,
            max_value=10.0,
            value=6.0,
            step=0.1,
            help="Controls the upper bound of the Y-axis in Age vs Stress Chart. Recommended: 5.6.\nNote: Adjusting the scale may exaggerate perceived trends—use cautiously to avoid misleading interpretations."
        )





# Chart 3: Avg Stress by Age Group
bar = alt.Chart(df).mark_bar().encode(
    x=alt.X("bin_age:O", title="Age Group", axis=alt.Axis(labelAngle=0)),
    y=alt.Y("mean(stress_level):Q", title="Avg Stress Level", scale=alt.Scale(domain=[y_min, y_max])),
    color=alt.condition(
        age_selection,
        alt.Color("bin_age:N",
            scale=alt.Scale(
                domain=["16–24", "25–34", "35–44", "45–54", "55–64", "65+"],
                range=["#a8c8ff", "#538eff", "#003366", "#296eff", "#7fabff", "#d3e5ff"]
            ),
            legend=alt.Legend(title="Age Groups ")
        ),
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
        legend=alt.Legend(title="Relative\nRespondent\nCount", orient="right")
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


with st.expander("🔎 What These Charts Show (Stress, Age, & Notifications)", expanded=False):
    st.markdown("""
    These two charts explore how **stress levels vary with age** and **how age groups differ in notification volume**.
    
    - In the left chart we find that **perceived stress may peak around middle years** and generally **decrease towards your retirement years.**
    Overall, this would make sense, as younger generations have a greater capacity to deal with stress than older generations who in addition to work related stress
    often experience family related stress, which dwindles as you head toward retirement. 
                
    - The right chart reveals how often each age group receives phone notifications and how that correlates with stress. We found that in your younger years
    16-24 and retirement years 65+ you experienced **greater stress levels when notification volumes were high**, compared with all other age groups were the **highest stress levels
    were reported with fewer notifications**. This may suggest that when you're already stressed (in you middle years) each **additional notification is vexing.**

    """)

with st.expander("❓ Further Questions", expanded=False):
    st.markdown ("""                           
    Further questions:
                 
    - While we suspect that primarily **work** and family are influencing the stress levels, what other factors could be at play?
                 
        - Could it be that if you are happier at your work, you experience less stress?
                 
        - Do you experience less stress because you're happier or because you are more productive?

    We will explore both of these questions in the next section.

    """)

# -----------------------
# 📊 Chart 7: Violin Plot of Stress Level by Age Group
# -----------------------
with st.expander("🎻 Stress Distribution by Age Group Violin Plot (Uncertainty)", expanded=False):
    # Full-width violin plot
    fig, ax = plt.subplots(figsize=(9, 4.5))  # Wide aspect ratio
    sns.violinplot(data=df, x="bin_age", y="stress_level", inner="quartile", palette="muted", ax=ax)
    ax.set_title("Stress Level Distribution by Age Group")
    ax.set_xlabel("Age Group")
    ax.set_ylabel("Stress Level")
    plt.xticks(rotation=0)
    st.pyplot(fig)

    # Explanatory paragraph below the chart
    st.markdown("""
    #### What This Shows  
    The violin plot illustrates the **distribution of stress levels** within each age group,
    capturing both the **spread** and **density** of responses.  
    The shape of each "violin" shows where stress levels are most concentrated — for example, wider sections mean more respondents reported stress in that range.  
    Overall we find that eventhough the Age vs Stress chart above suggests a potential slight relationship, through this violin plot we find that **more 
    investigation** is needed to draw any conclusions about the relationship between age and stress levels, as there is much overlap.
    Nonetheless, what is interesting is that even in the violin plot, we find that 65+ age group has the widest base, compared to younger generations that
    have a slightly wider top. This suggests that with **more investigation** we may uncover **reliable patterns** that imply **stress is parabolic across age groups**, peaking in the middle age groups and decreasing in older generations. 
    """)


st.markdown("<br><br>", unsafe_allow_html=True)



# -----------------------
# 📊 CHART SET 2: Satisfaction vs Productivity
# -----------------------
st.markdown("### 😌 Job Satisfaction Increases with Age and Productivity")
st.markdown(
    "<div style='font-size:0.9rem; color:gray;'>Try clicking the bars in the Age vs Job Satisfaction chart to learn more about each age group's Actual Productivity spread.</div>",
    unsafe_allow_html=True
)

st.markdown("<br><br>", unsafe_allow_html=True)

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

# Display charts side by side
st.altair_chart(chart5 | chart6)

with st.expander("🔎 What These Charts Show (Job Satisfaction, Age, & Productivity)", expanded=False):
    st.markdown("""
    These charts examine the **relationship between age, productivity, and job satisfaction**.

    - The left bar chart highlights how average job satisfaction may rise with age. Overall, this would explain the lower stress levels in the older (retirement) age group
    as they are more satisfied with their work. 
    - The right scatter plot shows how actual productivity scores relate to job satisfaction, with a red regression line. We see that job satisfaction and productivity are 
    **positively correlated** across all age groups, suggesting that **higher productivity may lead to greater job satisfaction** and vice versa.

    Taken together, these charts suggest that **older individuals may report both higher satisfaction and a stronger alignment between productivity and happiness at work** which lowers their
    perceived stress. Now why is it that older generations are more likely to feel this way than younger generations? It may be because they've had more time to find a job that suits them or
    they've merely grown into their roles at comfortable jobs. 
            
    """)

with st.expander("📌 The Big Takeaway", expanded=False):
    st.markdown("""
                
    This suggests that one key to a healthy life is finding **a job that excites you,** as this may **boost** your **overall productivity and job satisfaction**, **lowering** your overall **stress levels**. This way you may only
    experience **significant stress** during particuraly **busy times** at your work (which may be correlated with **higher notification volumes**). 
                
    However, of course as outlined in the uncertainty section **more investigation is required** to determine a proper causal relationship, as there remains significant of uncertainty.
    
    """)

with st.expander("📌 Further Exploration - Filter Controls - Big Takeaway", expanded=False):
    st.markdown("""
                
    If you **toggle on** the "Only Show Users Who Use Focus Apps" filter, you will find that the **stress levels are significantly lower** across all age groups, and decrease linearly with age. 
    This suggests that **using focus apps may help reduce stress levels**.
                
    The question just remains why are focus apps more effective with increasing age. One reason may be that discipline increases with age, meaning focus apps become more effective. However, more research is required
    to truly determine this.
                
    Overall, **consider using focus apps** as they may help **boost** **productivity** and **lower stress levels** even if you are not satisfied with your job.
    
    """)



st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; font-size: 0.85rem; color: gray;'>
        📊 Data Source: <a href="https://www.kaggle.com/datasets/mahdimashayekhi/social-media-vs-productivity" target="_blank">Kaggle – Social Media vs Productivity</a><br>
        © Lucas Schmidt, 2025. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
