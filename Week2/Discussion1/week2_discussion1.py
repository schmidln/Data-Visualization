import altair as alt
import pandas as pd
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def visualization1(data):
    chart = alt.Chart(data, title="Income vs. Life Expectancy (OECD, 2014)").mark_circle(size=60).encode(
        x=alt.X('LifeExpectancy:Q', title='Life Expectancy (Years)'),
        y=alt.Y('Income:Q', title='Income per Capita (USD)'),
        color=alt.Color('Region:N', legend=alt.Legend(title="Region")),
        tooltip=['Region','Country', 'LifeExpectancy', 'Income']
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

def visualization2(data):
    data['Population_In_Millions'] = data['Population'] / 1_000_000
    chart = alt.Chart(data, title="Total Population per Region (OECD, 2014)").mark_bar().encode(
        x=alt.X('Region:N', title='Region'),
        y=alt.Y('sum(Population_In_Millions):Q', title='Population (in millions)'),
        color=alt.Color('Region:N', legend=alt.Legend(title="Region")),
        tooltip=[
            alt.Tooltip('Region:N', title='Region'),
            alt.Tooltip('sum(Population_In_Millions):Q', title='Population (in millions)', format='.0f')
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

def visualization3(data):

    # Create chart
    chart = alt.Chart(data, title="Avg Life Expectancy by Region (OECD, 2014)").transform_aggregate(
        avg_life_expectancy='mean(LifeExpectancy)',
        avg_population='mean(Population)',
        avg_income='mean(Income)',
        groupby=['Region']
    ).mark_circle().encode(
        x=alt.X('Region:N', title='Region'),
        y=alt.Y('avg_life_expectancy:Q', 
                title='Avg Life Expectancy (Years)',
                scale=alt.Scale(domain=[60,80])),
        size=alt.Size('avg_population:Q', title='Avg Population', scale=alt.Scale(range=[0, 20000])),
        color=alt.Color('avg_income:Q',
                      title='Avg Income (USD)',
                      scale=alt.Scale(scheme='blues')),
        tooltip=['Region:N', 'avg_life_expectancy:Q']
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

def visualization4(data):
    chart = alt.Chart(data, title="Test 1").mark_point().encode(
        x=alt.X('LifeExpectancy',bins=5),
        y=alt.Y('Income',bins=5),
        size='count()',
        color='Region:N',
        tooltip=['Region', 'LifeExpectancy', 'Income']
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
    with open('oecd-wealth-health-2014.csv', 'r') as data:
        data = pd.read_csv(data)
except FileNotFoundError:
    print("File not found. Please ensure the file path is correct.")

visual = visualization1(data)
visual.save('week2Chart1.html')

visual = visualization2(data)
visual.save('week2Chart2.html')

visual = visualization3(data)
visual.save('week2Chart3.html')

visual = visualization4(data)
visual.save('week2Chart4.html')