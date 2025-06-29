import streamlit as st
import pandas as pd
import altair as alt

# Load cleaned dataset
df = pd.read_csv("marketing_campaign.csv", sep="\t")

# Rename product columns
product_col_rename = {
    'MntWines': 'Wine Products',
    'MntFruits': 'Fruit Products',
    'MntMeatProducts': 'Meat Products',
    'MntFishProducts': 'Fish Products',
    'MntSweetProducts': 'Sweet Products',
    'MntGoldProds': 'Gold / Consumer Products'
}
df = df.rename(columns=product_col_rename)
spend_cols = list(product_col_rename.values())

# Compute new fields
df['TotalSpend'] = df[spend_cols].sum(axis=1)
df['Age'] = 2025 - df['Year_Birth']
df['TotalAcceptedCampaigns'] = df[['AcceptedCmp1','AcceptedCmp2','AcceptedCmp3','AcceptedCmp4','AcceptedCmp5']].sum(axis=1)

# Filter out absurd entries
df = df[df['TotalSpend'] >= 100]
df = df[~df['Marital_Status'].isin(['Divorced', 'Alone', 'YOLO', 'Absurd'])]
df = df.dropna(subset=['Income'])

# Sidebar filters
st.sidebar.header("🔧 Filter Controls")
age_range = st.sidebar.slider("Age Range", 18, 100, (25, 65))
income_range = st.sidebar.slider("Income Range", int(df['Income'].min()), int(df['Income'].max()), (10000, 120000))
spend_range = st.sidebar.slider("Total Spend", 100, int(df['TotalSpend'].max()), (100, 2000))
webvisits = st.sidebar.slider("Web Visits (Last Month)", 0, 20, (0, 10))
edu = st.sidebar.selectbox("Education", ["All"] + sorted(df['Education'].unique()))
response_filter = st.sidebar.selectbox("Campaign Response", ["All", 0, 1])

# Apply filters
filtered = df[
    (df['Age'].between(*age_range)) &
    (df['Income'].between(*income_range)) &
    (df['TotalSpend'].between(*spend_range)) &
    (df['NumWebVisitsMonth'].between(*webvisits))
]
if edu != "All":
    filtered = filtered[filtered['Education'] == edu]
if response_filter != "All":
    filtered = filtered[filtered['Response'] == response_filter]

# Melt for product-specific scatter plot
melted = filtered.melt(
    id_vars=['ID', 'TotalAcceptedCampaigns', 'Age', 'Income', 'Response', 'Marital_Status', 'Education', 'TotalSpend'],
    value_vars=spend_cols,
    var_name="Product",
    value_name="Amount"
)

# Selections
selection = alt.selection_multi(fields=['Marital_Status'])
education_selection = alt.selection_multi(fields=['Education'])
product_selection = alt.selection_multi(fields=['Product'])

# Chart 1 - Marital Status Bar
bar = alt.Chart(filtered).mark_bar().encode(
    x=alt.X("Marital_Status:N", axis=alt.Axis(labelAngle=25)),
    y=alt.Y("mean(TotalSpend):Q", title="Avg Monthly Spend"),
    color=alt.condition(selection, "Marital_Status:N", alt.value("lightgray")),
    tooltip=["Marital_Status", "mean(TotalSpend):Q"]
).add_selection(selection).properties(
    width=400,
    height=450,
    title="💍 Avg Spend by Marital Status (Click to Filter)"
)

# Chart 2 - Income vs TotalSpend Scatter
scatter = alt.Chart(filtered).transform_filter(selection).mark_circle(size=80).encode(
    x="Income:Q",
    y="TotalSpend:Q",
    color="Marital_Status:N",
    tooltip=["Income", "TotalSpend", "Age", "Education"]
).interactive().properties(
    width=500,
    height=450,
    title="📈 Income vs Spend (Filtered by Marital Status)"
)

# Chart 3 (New) - Age vs Amount per Product Scatter
scatter_product = alt.Chart(melted).transform_filter(
    selection
).transform_filter(
    education_selection
).transform_filter(
    product_selection
).mark_circle(size=70).encode(
    x=alt.X("Age:Q", title="Customer Age"),
    y=alt.Y("Amount:Q", title="Spend on Selected Product"),
    color=alt.Color("Product:N", legend=alt.Legend(title="Product")),
    tooltip=["Age", "Amount", "Product", "Education", "Marital_Status"]
).properties(
    width=700,
    height=500,
    title="🎯 Age vs Spend on Product (Filtered by Marital Status, Education, and Product)"
)

# Chart 4 - Education Bar Chart for filtering
edu_bar = alt.Chart(filtered).mark_bar().encode(
    x=alt.X("Education:N", axis=alt.Axis(labelAngle=25)),
    y=alt.Y("count():Q", title="Customer Count"),
    color=alt.condition(education_selection, "Education:N", alt.value("lightgray")),
    tooltip=["Education", "count():Q"]
).add_selection(education_selection).properties(
    width=400,
    height=450,
    title="🎓 Count by Education (Click to Filter Product Spend)"
)

# Layout
st.title("📊 Consumer Product Marketing Dashboard")
st.altair_chart(bar | scatter, use_container_width=True)
st.altair_chart(edu_bar, use_container_width=True)
st.altair_chart(scatter_product, use_container_width=True)
