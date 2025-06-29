import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# Cache data loading for better performance
@st.cache_data
def load_and_process_data():
    """Load and preprocess the bacteria antibiotics data."""
    df = pd.read_csv("bacteria_with_spacer.csv")
    
    # Store the original order from CSV (including spacer)
    original_order = df["Bacteria"].tolist()
    
    # Keep all rows including spacer - just handle NaN values for spacer row
    df_processed = df.copy()
    
    # For spacer row, fill NaN values with 0 or a small value for processing
    # We'll handle the display separately
    spacer_mask = df_processed["Bacteria"] == "---"
    if spacer_mask.any():
        # Fill numeric columns with 0 for spacer row
        numeric_cols = ["Penicillin", "Streptomycin", "Neomycin"]
        for col in numeric_cols:
            df_processed.loc[spacer_mask, col] = 0
        # Fill string columns appropriately
        df_processed.loc[spacer_mask, "Gram_Staining"] = "spacer"
        df_processed.loc[spacer_mask, "Genus"] = "spacer"
    
    # Melt to long format
    df_long = df_processed.melt(
        id_vars=["Bacteria", "Gram_Staining", "Genus"],
        value_vars=["Penicillin", "Streptomycin", "Neomycin"],
        var_name="Antibiotic", 
        value_name="MIC"
    )
    
    # Compute effectiveness (handle spacer rows with 0 MIC)
    df_long["Effectiveness"] = np.where(
        df_long["MIC"] > 0, 
        -np.log10(df_long["MIC"]), 
        0  # Set effectiveness to 0 for spacer rows
    )
    
    return df_long, original_order

@st.cache_data
def create_chart_data(df_long, original_order, chart_type):
    """Create and sort chart data based on selected view, preserving CSV order with spacer."""

    # Filter plot data based on view
    if chart_type == "Most Effective Across All":
        # For non-spacer rows, get the most effective antibiotic
        non_spacer_df = df_long[df_long["Bacteria"] != "---"]
        plot_df_non_spacer = non_spacer_df.loc[non_spacer_df.groupby("Bacteria")["Effectiveness"].idxmax()].copy()
        
        # For spacer rows, just take one entry (they're all the same)
        spacer_df = df_long[df_long["Bacteria"] == "---"]
        if not spacer_df.empty:
            plot_df_spacer = spacer_df.iloc[[0]].copy()  # Take first spacer entry
            plot_df = pd.concat([plot_df_non_spacer, plot_df_spacer], ignore_index=True)
        else:
            plot_df = plot_df_non_spacer
            
        title = "Most Effective Antibiotic per Bacteria Strain"
    else:
        antibiotic = chart_type.split(" ")[0]
        plot_df = df_long[df_long["Antibiotic"] == antibiotic].copy()
        title = f"Effectiveness of {antibiotic} Against Various Bacteria"

    # Get bacteria that are actually in this filtered view (including spacer)
    used_bacteria = plot_df["Bacteria"].unique().tolist()
    
    # Create order preserving original CSV sequence
    bacteria_order_for_chart = [b for b in original_order if b in used_bacteria]
    
    # Create a sorting key by prepending order numbers to bacteria names
    # This forces alphabetical sorting to follow our desired order
    bacteria_to_order = {bacteria: i for i, bacteria in enumerate(original_order)}
    
    def create_sort_key(bacteria_name):
        order_num = bacteria_to_order.get(bacteria_name, 999)
        return f"{order_num:03d}_{bacteria_name}"
    
    plot_df["Bacteria_Sort"] = plot_df["Bacteria"].apply(create_sort_key)
    plot_df = plot_df.sort_values("Bacteria_Sort")

    # Find spacer position for divider line (no longer needed since spacer is visible)
    bacteria_before_spacer = None
    if "---" in original_order and "---" in used_bacteria:
        # We'll use the spacer row itself as the divider
        bacteria_before_spacer = "---"

    return plot_df, bacteria_order_for_chart, title, bacteria_before_spacer


def create_chart(plot_df, bacteria_order, title, spacer_bacteria):
    """Create the Altair chart with custom colors and spacer row handling."""
    
    unique_antibiotics = plot_df["Antibiotic"].unique()
    antibiotic_color_map = {
        "Penicillin": "orange",
        "Streptomycin": "green",
        "Neomycin": "blue"
    }
    
    if len(unique_antibiotics) == 1:
        color = alt.value(antibiotic_color_map.get(unique_antibiotics[0], "gray"))
    else:
        color = alt.Color(
            "Antibiotic:N", 
            title="Antibiotic",
            scale=alt.Scale(scheme="category10")
        )
    
    # Create separate dataframes for regular bacteria and spacer
    regular_df = plot_df[plot_df["Bacteria"] != "---"].copy()
    spacer_df = plot_df[plot_df["Bacteria"] == "---"].copy()
    
    chart_layers = []
    
    # Regular bacteria bars
    if not regular_df.empty:
        bars = alt.Chart(regular_df).mark_bar(
            stroke="white", strokeWidth=0.5
        ).encode(
            x=alt.X("Effectiveness:Q", title="-log₁₀(MIC) (Higher = More Effective)", scale=alt.Scale(domain=[-3, 3])),
            y=alt.Y("Bacteria_Sort:N", 
                    sort=None,  # Use natural alphabetical order of our prefixed names
                    title="Bacteria Species", 
                    axis=alt.Axis(
                        labelLimit=200, 
                        labelFontSize=10,
                        labelExpr="split(datum.value, '_')[1]"  # Remove the order prefix from display
                    )),
            color=color,
            tooltip=[
                alt.Tooltip("Bacteria:N", title="Bacteria"),
                alt.Tooltip("Antibiotic:N", title="Antibiotic"),
                alt.Tooltip("MIC:Q", title="MIC", format=".3f"),
                alt.Tooltip("Effectiveness:Q", title="Effectiveness", format=".2f"),
                alt.Tooltip("Gram_Staining:N", title="Gram Stain")
            ]
        )
        chart_layers.append(bars)
    
    # Spacer row as a divider line
    if not spacer_df.empty:
        spacer_line = alt.Chart(spacer_df).mark_rule(
            strokeDash=[4, 2], color="gray", strokeWidth=3, opacity=0.8
        ).encode(
            y=alt.Y("Bacteria_Sort:N", sort=None),
            tooltip=[alt.Tooltip("Bacteria:N", title="Separator")]
        )
        chart_layers.append(spacer_line)
        
        # Add Gram staining labels
        label_pos = alt.Chart(spacer_df).mark_text(
            align="left", baseline="middle", dx=5, dy=-30,
            fontSize=14, fontWeight="bold", color="darkblue"
        ).encode(
            y=alt.Y("Bacteria_Sort:N", sort=None),
            x=alt.value(-2.8),
            text=alt.value("Gram-positive ↑")
        )

        label_neg = alt.Chart(spacer_df).mark_text(
            align="left", baseline="middle", dx=5, dy=30,
            fontSize=14, fontWeight="bold", color="darkred"
        ).encode(
            y=alt.Y("Bacteria_Sort:N", sort=None),
            x=alt.value(-2.8),
            text=alt.value("Gram-negative ↓")
        )
        
        chart_layers.extend([label_pos, label_neg])

    chart = alt.layer(*chart_layers).properties(
        width="container",
        height=max(400, len(bacteria_order) * 30),
        title=alt.TitleParams(text=title, fontSize=16, anchor="start", offset=10)
    ).resolve_scale(color="independent")

    return chart

def main():
    st.set_page_config(page_title="Antibiotic Effectiveness Explorer", layout="wide")
    
    st.title("🧬 Antibiotic Effectiveness Explorer")
    st.markdown("""
    Explore antibiotic effectiveness against different bacterial strains.  
    Bacteria are displayed in the same order as listed in the original dataset.
    """)
    
    # Load data
    try:
        df_long, original_order = load_and_process_data()
    except FileNotFoundError:
        st.error("Data file 'bacteria_with_spacer.csv' not found. Please ensure the file is in the correct location.")
        return
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return
    
    # Sidebar controls
    with st.sidebar:
        st.header("Chart Options")
        chart_type = st.selectbox(
            "Select Chart View", 
            [
                "Penicillin Only",
                "Streptomycin Only", 
                "Neomycin Only",
                "Most Effective Across All"
            ],
            help="Choose which antibiotic data to display"
        )
        
        # Summary stats (excluding spacer)
        st.subheader("Data Summary")
        non_spacer_df = df_long[df_long["Bacteria"] != "---"]
        total_bacteria = non_spacer_df["Bacteria"].nunique()
        gram_pos = non_spacer_df[non_spacer_df["Gram_Staining"] == "positive"]["Bacteria"].nunique()
        gram_neg = non_spacer_df[non_spacer_df["Gram_Staining"] == "negative"]["Bacteria"].nunique()
        
        st.metric("Total Bacteria", total_bacteria)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Gram +", gram_pos)
        with col2:
            st.metric("Gram -", gram_neg)
    
    # Chart
    plot_df, bacteria_order, title, spacer_bacteria = create_chart_data(df_long, original_order, chart_type)
    chart = create_chart(plot_df, bacteria_order, title, spacer_bacteria)
    st.altair_chart(chart, use_container_width=True)
    
    # Data table (excluding spacer for clarity)
    with st.expander("📊 View Raw Data"):
        display_df = plot_df[plot_df["Bacteria"] != "---"][["Bacteria", "Gram_Staining", "Antibiotic", "MIC", "Effectiveness"]].round(3)
        st.dataframe(display_df, use_container_width=True)

if __name__ == "__main__":
    main()