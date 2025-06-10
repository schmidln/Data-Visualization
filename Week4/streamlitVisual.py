import streamlit as st
import pandas as pd
import altair as alt
import numpy as np  # <-- add this import
import os

# Ensure current working directory is set correctly
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load the data
df = pd.read_csv("bacteria_timeline_tableau.csv")

# Optional: Set MIC to log-scale for better visual scaling (larger size = more effective)
df["log_MIC"] = df["MIC"].apply(lambda x: None if x <= 0 else round(-1 * np.log10(x), 2))  # <-- fixed here

# Create chart
chart = alt.Chart(df).mark_circle().encode(
    x=alt.X('Order:O', title='Testing Order'),
    y=alt.Y('Bacteria:N', sort=alt.EncodingSortField(field='Order', order='ascending')),
    color=alt.Color('Antibiotic:N', scale=alt.Scale(scheme='category10')),
    size=alt.Size('log_MIC:Q', title='-log10(MIC)', scale=alt.Scale(range=[50, 300])),
    tooltip=['Bacteria', 'Antibiotic', 'MIC', 'Gram_Staining']
).properties(
    width=800,
    height=600,
    title='Antibiotic Effectiveness Timeline by Bacteria (Inverse MIC)'
).configure_axis(
    grid=True
).configure_title(
    fontSize=18,
    anchor='start'
)

chart.show()
