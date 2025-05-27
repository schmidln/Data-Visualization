import altair as alt
import pandas as pd
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def visualization1(data):

    chart = alt.Chart(data, title="Estimated Occupancy vs. Number of Beds (Airbnb, 2023)").mark_bar(size=20).encode(
        x=alt.X('beds:Q', title='Number of Beds'),
        y=alt.Y('avg_occupancy:Q', title='Estimated Occupancy (Last 365 Days)'),
    ).transform_aggregate(
        avg_occupancy = 'mean(estimated_occupancy_l365d):Q',
        groupby=['beds']
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
    bars = alt.Chart(data, title="Most Popular Number of Beds by Host").transform_aggregate(
        count='count()',  # create new 'count' field
        groupby=['beds']
    ).mark_bar(size=20).encode(
        x=alt.X('beds:Q', title='Number of Beds'),
        y=alt.Y('count:Q', title='Count of Listings'),  # explicitly set as Quantitative
        color=alt.Color('beds:N', legend=alt.Legend(title="Number of Beds")),
        tooltip=['beds:Q', 'count:Q']  # explicit typing here too
    )

    labels = alt.Chart(data).transform_aggregate(
        count='count()',
        groupby=['beds']
    ).mark_text(
        dy=-5,  # move label above the bar
        fontSize=12
    ).encode(
        x=alt.X('beds:Q'),
        y=alt.Y('count:Q'),
        text=alt.Text('count:Q')
    )

    chart = (bars + labels).properties(
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

    chart = alt.Chart(data, title="Most Popular Number of Beds by Guest").transform_aggregate(
    count='count()',
    total_occupancy='sum(estimated_occupancy_l365d)',
    groupby=['beds']
    ).transform_calculate(
        occupancy_capacity='datum.total_occupancy / datum.count'
    ).mark_bar(size=20).encode(
        x=alt.X('beds:Q', title="Number of Beds"),
        y=alt.Y('occupancy_capacity:Q', title="Average Occupancy per Hosting"),
        tooltip=[
            alt.Tooltip('beds:Q', title='Number of Beds'),
            alt.Tooltip('occupancy_capacity:Q', title='Average Occupancy per Hosting', format='.2f')
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

def visualization4(data):
    # Clean price field
    data['price'] = (
        data['price']
        .replace('[\$,]', '', regex=True)  # Remove $ and commas
        .astype(float)
    )

    # Drop rows with missing 'price' or 'beds'
    data = data.dropna(subset=['price', 'beds'])

    # Convert beds to int for exact matching
    data.loc[:, 'beds'] = data['beds'].astype(int)


    # Filter for 1–4 bed listings
    data = data[data['beds'].isin([1, 2, 3, 4])]

    # Create the chart
    chart = alt.Chart(data).mark_circle().encode(
        x=alt.X('price:Q', title='Price').bin(step=50),
        y=alt.Y('neighbourhood_cleansed:N', title='Neighbourhood', axis=alt.Axis(grid=True)),
        color=alt.Color('beds:N', title='Number of Beds'),
        tooltip=[
            alt.Tooltip('price:Q', title='Price', format='$,.2f'),
            alt.Tooltip('neighbourhood_cleansed:N', title='Neighbourhood'),
            alt.Tooltip('beds:N', title='Number of Beds')
        ]
    ).transform_filter(
        alt.datum.price < 2400
    ).properties(
        width=700,
        height=400,
        title='Price Distribution by Neighbourhood (1–4 Beds Only)'
    )

    return chart





try:
    with open('listings.csv', 'r') as data:
        data = pd.read_csv(data)
except FileNotFoundError:
    print("File not found. Please ensure the file path is correct.")


visual = visualization1(data)
visual.save('visualization1.html')

visual = visualization2(data)
visual.save('visualization2.html')

visual = visualization3(data)
visual.save('visualization3.html')

visual = visualization4(data)
visual.save('visualization4.html')