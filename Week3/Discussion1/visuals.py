import altair as alt
import pandas as pd
import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def interactive_visualization(data):
    # Selections
    region_select = alt.selection_point(fields=["Region"], bind="legend", toggle=True)
    brush_select = alt.selection_interval(encodings=["x"])
    country_select = alt.selection_point(fields=["Country"], toggle=False, empty="none")
    hover = alt.selection_point(on="mouseover", encodings=["x"], empty="none")

    # Histogram
    histogram = alt.Chart(data).mark_bar().encode(
        x=alt.X("LifeExpectancy:Q", bin=alt.Bin(maxbins=10), title="Life Expectancy (years)"),
        y=alt.Y("count():Q", title="Number of Countries"),
        color=alt.condition(hover, alt.value("gold"), alt.Color("Region:N", title="Region")),
        opacity=alt.condition(brush_select, alt.value(1), alt.value(0.3)),
        tooltip=["Region:N", alt.Tooltip("count():Q", title="Number of Countries")]
    ).add_params(
        region_select,
        brush_select,
        hover
    ).transform_filter(
        region_select
    ).properties(
        width=600,
        height=200,
        title="Life Expectancy by Region"
    )

    # Scatter plot (zoomable and linked)
    scatter = alt.Chart(data).mark_circle(size=100).encode(
        x=alt.X("Income:Q", title="Income per Capita (USD)", scale=alt.Scale(domain="unaggregated")),
        y=alt.Y("LifeExpectancy:Q", title="Life Expectancy (Years)", scale=alt.Scale(domain="unaggregated")),
        color=alt.condition(country_select, alt.value('red'), alt.Color("Region:N")),
        tooltip=["Region:N", "Country:N", "Income:Q", "LifeExpectancy:Q"],
        opacity=alt.condition(region_select, alt.value(1), alt.value(0.1)),
        size=alt.condition(country_select, alt.value(200), alt.value(80))
    ).add_params(
        country_select
    ).transform_filter(
        region_select
    ).transform_filter(
        brush_select
    ).properties(
        width=600,
        height=400,
        title="Income vs Life Expectancy"
    ).interactive()

    return alt.vconcat(histogram, scatter).configure_title(anchor="start")





try:
    with open('oecd-wealth-health-2014 (1).csv', 'r') as file:
        data = pd.read_csv(file)
        alt.data_transformers.enable('default', max_rows=None)
except FileNotFoundError:
    print("File not found. Please ensure the file path is correct.")
    sys.exit()


chart = interactive_visualization(data)
chart.save('interactive_visualization.html')