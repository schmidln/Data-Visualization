import altair as alt
import pandas as pd
import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def chart1(data):
    chart = alt.Chart(data, title="Social Media vs Actual Productivity").mark_circle(size=20).encode(
        x=alt.X("daily_social_media_time:Q", title="Daily Social Media Usage (Hours per Day)"),
        y=alt.Y("actual_productivity_score:Q", title="Actual Productivity (Hours per Day)"),
        tooltip=["daily_social_media_time:Q", "actual_productivity_score:Q"]
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


try:
    with open('oecd-wealth-health-2014.csv', 'r') as file:
        data = pd.read_csv(file)
except FileNotFoundError:
    print("File not found. Please ensure the file path is correct.")
    sys.exit()


visual1 = chart1(data)
visual1.save('visualization1.html')
