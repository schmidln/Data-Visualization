import streamlit as st
import pandas as pd
import altair as alt

# Data
data = {
    "Year": ["2025", "2035", "2050", "2050 (Ideal)"] * 2,
    "Vehicle Type": ["Electric"] * 4 + ["Gasoline"] * 4,
    "Percentage": [1, 10, 40, 96, 99, 90, 60, 4]
}
df = pd.DataFrame(data)

# Streamlit App
st.title("Projected Composition of Vehicles on US Roads")
st.write("The chart below shows the estimated share of electric and gasoline-powered vehicles on U.S. roads over time under different policy and market adoption scenarios.")

# Base bar chart
bar_chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Year:N', title="Year", axis=alt.Axis(labelAngle=0)),
    y=alt.Y('Percentage:Q', stack='zero', title='Share of Vehicles (%)'),
    color=alt.Color('Vehicle Type:N', scale=alt.Scale(range=["#1f77b4", "#ff7f0e"])),
    tooltip=['Vehicle Type', 'Percentage']
)

# Add labels only for Gasoline bars
gasoline_df = df[df["Vehicle Type"] == "Gasoline"]
gasoline_labels = alt.Chart(gasoline_df).transform_calculate(
    label="datum.Percentage + '%'"
).mark_text(
    dy=-10,
    color='black'
).encode(
    x=alt.X('Year:N'),
    y=alt.Y('Percentage:Q', stack='zero'),
    text=alt.Text('label:N')
)

# Combine chart and labels
final_chart = (bar_chart + gasoline_labels).properties(width=700, height=400)
st.altair_chart(final_chart, use_container_width=True)

# Debrief paragraph
st.markdown("""
**What does "2050 (Ideal)" mean?**  
This scenario assumes that **100% of all new vehicle sales are electric by 2035**.  
Given average vehicle lifespans and turnover rates, this results in **96% of all vehicles on the road being electric by 2050**—a near-complete transition away from internal combustion engines.

These projections help illustrate the scale and speed of electrification needed to meet long-term climate targets.
""")
