import altair as alt
import pandas as pd
import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def chart1(data):
    chart = alt.Chart(data, title="Social Media vs Actual Productivity").mark_circle(size=20).encode(
        x=alt.X("daily_social_media_time:Q", title="Daily Social Media Usage (Hours per Day)"),
        y=alt.Y("actual_productivity_score:Q", title="Actual Productivity (Hours per Day)"),
        color=alt.Color("social_platform_preference:N", title="Preferred Social Platform"),
        tooltip=["daily_social_media_time:Q", "actual_productivity_score:Q","social_platform_preference:N"]
    ).properties(
        width=600,
        height=400
    ).configure_title(
        fontSize=18,
        anchor='middle',
        font='Helvetica'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )
    return chart

def chart2(data):
    chart = alt.Chart(data, title="Social Media vs Perceived Productivity").mark_circle(size=20).encode(
        x=alt.X("daily_social_media_time:Q", title="Daily Social Media Usage (Hours per Day)"),
        y=alt.Y("perceived_productivity_score:Q", title="Actual Productivity (Hours per Day)"),
        color=alt.Color("social_platform_preference:N", title="Preferred Social Platform"),
        tooltip=["daily_social_media_time:Q", "perceived_productivity_score:Q","social_platform_preference:N"]
    ).properties(
        width=600,
        height=400
    ).configure_title(
        fontSize=18,
        anchor='middle',
        font='Helvetica'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )
    return chart

def chart3(data):
    # Get min and max stress levels
    stress_min = data["stress_level"].min()
    stress_max = data["stress_level"].max()

    chart = alt.Chart(data, title="Average Screen Time Before Sleep vs Sleep Duration").mark_bar().encode(
        x=alt.X("sleep_hours:Q", bin=alt.Bin(maxbins=10), title="Average Hours Slept Per Day"),
        y=alt.Y("mean(screen_time_before_sleep):Q", title="Avg Screen Time Before Sleep (hrs)"),
        color=alt.Color("mean(stress_level):Q", 
                        scale=alt.Scale(scheme='blues', domain=[stress_min, stress_max]),
                        title="Average Stress Level"),
        tooltip=[
            alt.Tooltip("sleep_hours:Q", bin=True, title="Sleep Bin (hrs)"),
            alt.Tooltip("mean(screen_time_before_sleep):Q", title="Avg Screen Time (hrs)", format=".2f"),
            alt.Tooltip("mean(stress_level):Q", title="Average Stress Level", format=".2f")
        ]
    ).properties(
        width=600,
        height=400
    ).configure_title(
        fontSize=18,
        anchor='middle',
        font='Helvetica'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )
    return chart

def chart4(data):
    # Get min and max stress levels
    breaks_min = data["breaks_during_work"].min()
    breaks_max = data["breaks_during_work"].max()

    chart = alt.Chart(data, title="Average Screen Time Before Sleep vs Sleep Duration").mark_circle(size=20).encode(
        x=alt.X("daily_social_media_time:Q", title="Daily Hours on Social Media"),
        y=alt.Y("actual_productivity_score:Q", title="Actual Productivity Score"),
        color=alt.Color("breaks_during_work:Q", 
                        scale=alt.Scale(scheme='blues', domain=[breaks_min, breaks_max]),
                        title="Number of Breaks During Work"),
        tooltip=[
            alt.Tooltip("breaks_during_work:Q", title="Number of Breaks During Work"),
            alt.Tooltip("actual_productivity_score:Q", title="Actual Productivity Score"),
            alt.Tooltip("daily_social_media_time:Q", title="Daily Social Media Time (Hours)")
        ]
    ).properties(
        width=600,
        height=400
    ).configure_title(
        fontSize=18,
        anchor='middle',
        font='Helvetica'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )
    return chart


def chart5(data):
    bar = alt.Chart(data, title="Average Social Media Usage by Burnout Days").mark_bar().encode(
        x=alt.X("days_feeling_burnout_per_month:O", title="Days Feeling Burnout per Month"),
        y=alt.Y("mean(daily_social_media_time):Q", title="Average Social Media Usage (Hours per Day)"),
        tooltip=[
            alt.Tooltip("days_feeling_burnout_per_month:O", title="Burnout Days"),
            alt.Tooltip("mean(daily_social_media_time):Q", title="Avg Social Media (hrs)", format=".2f")
        ]
    ).properties(
        width=700,
        height=400
    ).configure_title(
        fontSize=18,
        anchor='middle',
        font='Helvetica'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_axisX(
        labelAngle=0
    )
    
    return bar


def chart6(data):
    filtered_df = data[['breaks_during_work', 'actual_productivity_score', 'social_platform_preference']].dropna()

    chart = alt.Chart(filtered_df, title="Breaks vs Actual Productivity by Social Media Preference").mark_line().encode(
        x=alt.X('breaks_during_work:Q', title='Breaks During Work'),
        y=alt.Y('mean(actual_productivity_score):Q',
                title='Average Actual Productivity',
                scale=alt.Scale(domain=[4.7, 5.2])),  # << Custom scale here
        color=alt.Color('social_platform_preference:N', title='Preferred Social Platform'),
    ).properties(
        width=700,
        height=400
    ).configure_title(
        fontSize=18,
        anchor='middle',
        font='Helvetica'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )

    return chart


def chart7(data):
    plot_data = data[['actual_productivity_score', 'perceived_productivity_score']].dropna()

    chart = alt.Chart(plot_data, title="Perceived vs Actual Productivity").mark_circle(size=60, opacity=0.6).encode(
        x=alt.X("perceived_productivity_score:Q", title="Perceived Productivity"),
        y=alt.Y("actual_productivity_score:Q", title="Actual Productivity"),
        tooltip=["perceived_productivity_score", "actual_productivity_score"]
    ).properties(width=600, height=400)

    return chart


def chart8(data):
    plot_data = data[['actual_productivity_score', 'job_satisfaction_score']].dropna()
    plot_data['job_satisfaction_bin'] = pd.cut(plot_data['job_satisfaction_score'], bins=6).astype(str)

    chart = alt.Chart(plot_data, title="Actual Productivity by Job Satisfaction Level").mark_bar().encode(
        x=alt.X("job_satisfaction_bin:N", title="Job Satisfaction Level (Binned)"),
        y=alt.Y("mean(actual_productivity_score):Q", title="Average Actual Productivity"),
        tooltip=["job_satisfaction_bin", "mean(actual_productivity_score):Q"]
    ).properties(width=600, height=400).configure_axisX(
        labelAngle=0
    )

    return chart


def chart9(data):
    plot_data = data[['daily_social_media_time', 'job_satisfaction_score']].dropna()
    plot_data['job_satisfaction_bin'] = pd.cut(plot_data['job_satisfaction_score'], bins=6).astype(str)

    chart = alt.Chart(plot_data, title="Social Media Time by Job Satisfaction Level").mark_bar().encode(
        x=alt.X("job_satisfaction_bin:N", title="Job Satisfaction Level (Binned)"),
        y=alt.Y("mean(daily_social_media_time):Q", title="Avg Social Media Time (Hours/Day)"),
        tooltip=["job_satisfaction_bin", "mean(daily_social_media_time):Q"]
    ).properties(width=600, height=400).configure_axisX(
        labelAngle=0
    )

    return chart


def chart10(data):
    plot_data = data[['breaks_during_work', 'job_satisfaction_score']].dropna()
    plot_data['job_satisfaction_bin'] = pd.cut(plot_data['job_satisfaction_score'], bins=6).astype(str)

    chart = alt.Chart(plot_data, title="Breaks per Day by Job Satisfaction Level").mark_bar().encode(
        x=alt.X("job_satisfaction_bin:N", title="Job Satisfaction Level (Binned)"),
        y=alt.Y("mean(breaks_during_work):Q", title="Avg Breaks per Day"),
        tooltip=["job_satisfaction_bin", "mean(breaks_during_work):Q"]
    ).properties(width=600, height=400).configure_axisX(
        labelAngle=0
    )

    return chart

def chart11(data):

    time_min = data["stress_level"].min()
    time_max = data["stress_level"].max()

    plot_data = data[['job_type', 'actual_productivity_score', 'daily_social_media_time']].dropna()

    chart = alt.Chart(plot_data, title="Productivity by Job Type and Social Media Time").mark_bar().encode(
        x=alt.X("job_type:N", title="Job Type"),
        y=alt.Y("mean(actual_productivity_score):Q", title="Avg Actual Productivity"),
        color=alt.Color("mean(daily_social_media_time):Q", 
                        title="Avg Social Media Time (hrs/day)",
                        scale=alt.Scale(scheme='blues', domain=[time_min, time_max])),
        tooltip=[
            "job_type",
            alt.Tooltip("mean(actual_productivity_score):Q", title="Avg Productivity", format=".2f"),
            alt.Tooltip("mean(daily_social_media_time):Q", title="Avg Social Media Time", format=".2f")
        ]
    ).properties(
        width=700,
        height=400
    ).configure_axisX(
        labelAngle=0
    )

    return chart

def chart12(data):
    plot_data = data[['daily_social_media_time', 'job_satisfaction_score']].dropna()
    plot_data = plot_data[
        plot_data['daily_social_media_time'].between(
            plot_data['daily_social_media_time'].quantile(0.05),
            plot_data['daily_social_media_time'].quantile(0.95)
        )  # Removes outliers (5th to 95th percentile)
    ]
    plot_data['job_satisfaction_bin'] = pd.cut(plot_data['job_satisfaction_score'], bins=6).astype(str)

    chart = alt.Chart(plot_data, title="Social Media Time by Job Satisfaction Level - Data Cleaned (Only 5th-95th Quartiles)").mark_bar().encode(
        x=alt.X("job_satisfaction_bin:N", title="Job Satisfaction Level (Binned)"),
        y=alt.Y("mean(daily_social_media_time):Q", title="Avg Social Media Time (hrs/day)"),
        tooltip=["job_satisfaction_bin", "mean(daily_social_media_time):Q"]
    ).properties(
        width=600,
        height=400
    ).configure_axisX(
        labelAngle=0
    )

    return chart


def chart13(data):
    plot_data = data[['number_of_notifications', 'social_platform_preference']].dropna()

    chart = alt.Chart(plot_data, title="Average Notifications by Social Media Platform").mark_bar().encode(
        x=alt.X("social_platform_preference:N", title="Preferred Social Media Platform"),
        y=alt.Y("mean(number_of_notifications):Q", title="Avg Notifications per Day"),
        tooltip=[
            "social_platform_preference",
            alt.Tooltip("mean(number_of_notifications):Q", title="Avg Notifications", format=".1f")
        ]
    ).properties(
        width=600,
        height=400
    ).configure_axisX(
        labelAngle=0
    )

    return chart


def chart14(data):
    plot_data = data[['gender', 'actual_productivity_score']].dropna()

    chart = alt.Chart(plot_data, title="Actual Productivity by Gender").mark_bar().encode(
        x=alt.X("gender:N", title="Gender"),
        y=alt.Y("mean(actual_productivity_score):Q", title="Avg Actual Productivity"),
        tooltip=["gender", "mean(actual_productivity_score):Q"]
    ).properties(width=600, height=400).configure_axisX(labelAngle=0)

    return chart


def chart15(data):
    plot_data = data[['gender', 'daily_social_media_time']].dropna()

    chart = alt.Chart(plot_data, title="Daily Social Media Time by Gender").mark_bar().encode(
        x=alt.X("gender:N", title="Gender"),
        y=alt.Y("mean(daily_social_media_time):Q", title="Avg Social Media Time (hrs/day)"),
        tooltip=["gender", "mean(daily_social_media_time):Q"]
    ).properties(width=600, height=400).configure_axisX(labelAngle=0)

    return chart


def chart16(data):
    plot_data = data[['gender', 'breaks_during_work']].dropna()

    chart = alt.Chart(plot_data, title="Breaks During Work by Gender").mark_bar().encode(
        x=alt.X("gender:N", title="Gender"),
        y=alt.Y("mean(breaks_during_work):Q", title="Avg Breaks per Day"),
        tooltip=["gender", "mean(breaks_during_work):Q"]
    ).properties(width=600, height=400).configure_axisX(labelAngle=0)

    return chart


def chart17(data):
    plot_data = data[['gender', 'social_platform_preference']].dropna()

    chart = alt.Chart(plot_data, title="Social Media Preference by Gender").mark_bar().encode(
        x=alt.X("gender:N", title="Gender"),
        y=alt.Y("count():Q", title="Number of People"),
        color=alt.Color("social_platform_preference:N", title="Preferred Platform"),
        tooltip=["gender", "social_platform_preference", "count()"]
    ).properties(width=600, height=400).configure_axisX(labelAngle=0)

    return chart


def chart18(data):
    plot_data = data[['gender', 'stress_level']].dropna()

    chart = alt.Chart(plot_data, title="Stress Level by Gender").mark_bar().encode(
        x=alt.X("gender:N", title="Gender"),
        y=alt.Y("mean(stress_level):Q", title="Avg Stress Level"),
        tooltip=["gender", "mean(stress_level):Q"]
    ).properties(width=600, height=400).configure_axisX(labelAngle=0)

    return chart


def chart19(data):
    plot_data = data[['gender', 'job_satisfaction_score']].dropna()

    chart = alt.Chart(plot_data, title="Job Satisfaction by Gender").mark_bar().encode(
        x=alt.X("gender:N", title="Gender"),
        y=alt.Y("mean(job_satisfaction_score):Q", title="Avg Job Satisfaction"),
        tooltip=["gender", "mean(job_satisfaction_score):Q"]
    ).properties(width=600, height=400).configure_axisX(labelAngle=0)

    return chart


def chart20(data):
    plot_data = data[['gender', 'days_feeling_burnout_per_month']].dropna()

    chart = alt.Chart(plot_data, title="Burnout Days per Month by Gender").mark_bar().encode(
        x=alt.X("gender:N", title="Gender"),
        y=alt.Y("mean(days_feeling_burnout_per_month):Q", title="Avg Burnout Days/Month"),
        tooltip=["gender", "mean(days_feeling_burnout_per_month):Q"]
    ).properties(width=600, height=400).configure_axisX(labelAngle=0)

    return chart


def chart21(data):
    plot_data = data[['gender', 'coffee_consumption_per_day']].dropna()

    chart = alt.Chart(plot_data, title="Coffee Consumption by Gender").mark_bar().encode(
        x=alt.X("gender:N", title="Gender"),
        y=alt.Y("mean(coffee_consumption_per_day):Q", title="Avg Cups of Coffee/Day"),
        tooltip=["gender", "mean(coffee_consumption_per_day):Q"]
    ).properties(width=600, height=400).configure_axisX(labelAngle=0)

    return chart


def chart22(data):
    plot_data = data[['gender', 'weekly_offline_hours']].dropna()

    chart = alt.Chart(plot_data, title="Weekly Offline Hours by Gender").mark_bar().encode(
        x=alt.X("gender:N", title="Gender"),
        y=alt.Y("mean(weekly_offline_hours):Q", title="Avg Offline Hours/Week"),
        tooltip=["gender", "mean(weekly_offline_hours):Q"]
    ).properties(width=600, height=400).configure_axisX(labelAngle=0)

    return chart


def chart23(data):
    plot_data = data[['number_of_notifications', 'actual_productivity_score', 'social_platform_preference']].dropna()

    # Sort by notifications for smoother lines
    plot_data = plot_data.sort_values('number_of_notifications')

    chart = alt.Chart(plot_data, title="Notifications vs Actual Productivity (Line Chart)").mark_line(point=True).encode(
        x=alt.X("number_of_notifications:Q", title="Notifications per Day"),
        y=alt.Y("actual_productivity_score:Q", title="Actual Productivity Score"),
        color=alt.Color("social_platform_preference:N", title="Preferred Social Platform"),
        tooltip=["number_of_notifications", "actual_productivity_score", "social_platform_preference"]
    ).properties(
        width=600,
        height=400
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=18,
        anchor='middle'
    )

    return chart




def chart24(data):
    plot_data = data[['number_of_notifications', 'actual_productivity_score', 'social_platform_preference']].dropna()

    chart = alt.Chart(plot_data, title="Notifications vs Actual Productivity (Scatter Plot)").mark_circle(size=60, opacity=0.5).encode(
        x=alt.X("number_of_notifications:Q", title="Notifications per Day"),
        y=alt.Y("actual_productivity_score:Q", title="Actual Productivity Score"),
        color=alt.Color("social_platform_preference:N", title="Preferred Social Platform"),
        tooltip=["number_of_notifications", "actual_productivity_score", "social_platform_preference"]
    ).properties(
        width=600,
        height=400
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=18,
        anchor='middle'
    )

    return chart







try:
    with open('social_media_vs_productivity 2.csv', 'r') as file:
        data = pd.read_csv(file)
except FileNotFoundError:
    print("File not found. Please ensure the file path is correct.")
    sys.exit()


visual1 = chart1(data)
visual1.save('Chart1_Social_Media_vs_Actual_Productivity.html')

visual2 = chart2(data)
visual2.save('Chart2_Social_Media_vs_Perceived_Productivity.html')

visual3 = chart3(data)
visual3.save('Chart3_Social_Media_vs_Sleep_and_Stress.html')

visual4 = chart4(data)
visual4.save('Chart4_Social_Media_vs_Breaks_and_Productivity.html')

visual5 = chart5(data)
visual5.save('Chart5_Social_Media_vs_Burnout_Days.html')

visual6 = chart6(data)
visual6.save('Chart6_Social_Media_vs_Breaks_and_Productivity_by_Preference.html')

visual7 = chart7(data)
visual7.save('Chart7_Perceived_vs_Actual_Productivity.html')

visual8 = chart8(data)
visual8.save('Chart8_Actual_Productivity_by_Job_Satisfaction.html')

visual9 = chart9(data)
visual9.save('Chart9_Social_Media_Time_by_Job_Satisfaction.html')

visual10 = chart10(data)
visual10.save('Chart10_Breaks_per_Day_by_Job_Satisfaction.html')

visual11 = chart11(data)
visual11.save('Chart11_Productivity_by_Job_Type_and_Social_Media_Time.html')

visual12 = chart12(data)
visual12.save('Chart12_Social_Media_Time_by_Job_Satisfaction_Binned_Deep.html')

visual13 = chart13(data)
visual13.save('Chart13_Notifications_by_Social_Media_Platform.html')

visual14 = chart14(data)
visual14.save("Chart14_Gender_vs_Actual_Productivity.html")

visual15 = chart15(data)
visual15.save("Chart15_Gender_vs_Social_Media_Time.html")

visual16 = chart16(data)
visual16.save("Chart16_Gender_vs_Breaks_During_Work.html")

visual17 = chart17(data)
visual17.save("Chart17_Gender_vs_Social_Media_Preference.html")

visual18 = chart18(data)
visual18.save("Chart18_Gender_vs_Stress_Level.html")

visual19 = chart19(data)
visual19.save("Chart19_Gender_vs_Job_Satisfaction.html")

visual20 = chart20(data)
visual20.save("Chart20_Gender_vs_Burnout_Days.html")

visual21 = chart21(data)
visual21.save("Chart21_Gender_vs_Coffee_Consumption.html")

visual22 = chart22(data)
visual22.save("Chart22_Gender_vs_Weekly_Offline_Hours.html")

visual23 = chart23(data)
visual23.save("Chart23_Notifications_by_Platform_Line.html")

visual24 = chart24(data)
visual24.save("Chart24_Notifications_by_Platform_Scatter.html")
