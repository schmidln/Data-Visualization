import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# Cache data loading for better performance
@st.cache_data
def load_and_process_data():
    """Load and preprocess the bacteria antibiotics data."""
    df = pd.read_csv("bacteriaWithSpacer.csv")
    
    # Remove spacer rows
    df = df[df["Bacteria"] != "---"].copy()
    
    # Store the original order from CSV (excluding spacer)
    original_order = df["Bacteria"].tolist()
    
    # Melt to long format
    df_long = df.melt(
        id_vars=["Bacteria", "Gram_Staining", "Genus"],
        value_vars=["Penicillin", "Streptomycin", "Neomycin"],
        var_name="Antibiotic", 
        value_name="MIC"
    )
    
    # Compute effectiveness
    df_long["Effectiveness"] = -np.log10(df_long["MIC"])
    
    return df_long, original_order

@st.cache_data
def create_chart_data(df_long, original_order, chart_type):
    """Create and sort chart data based on selected view, preserving CSV order."""

    # Filter plot data based on view and create descriptive titles
    if chart_type == "Most Effective Across All":
        # Get the most effective antibiotic for each bacteria
        plot_df = df_long.loc[df_long.groupby("Bacteria")["Effectiveness"].idxmax()].copy()
        title = "Comprehensive Antibiotic Arsenal: Our Best Weapons Against Common Bacterial Threats"
    elif chart_type == "Penicillin Only":
        plot_df = df_long[df_long["Antibiotic"] == "Penicillin"].copy()
        title = "Penicillin: The Gold Standard Against Gram-Positive Bacterial Infections"
    elif chart_type == "Neomycin Only":
        plot_df = df_long[df_long["Antibiotic"] == "Neomycin"].copy()
        title = "Neomycin: Highly Effective Broad-Spectrum Agent, Particularly Against Gram-Negative Bacteria"
    elif chart_type == "Streptomycin Only":
        plot_df = df_long[df_long["Antibiotic"] == "Streptomycin"].copy()
        title = "Streptomycin: A Valuable Alternative with Selective Effectiveness Across Bacterial Species"

    # Get bacteria that are actually in this filtered view
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

    return plot_df, bacteria_order_for_chart, title


def create_chart(plot_df, bacteria_order, title):
    """Create the Altair chart with custom colors and gram staining-based outlines."""
    
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
    
    # Create stroke color based on gram staining
    stroke_color = alt.Color(
        "Gram_Staining:N",
        scale=alt.Scale(
            domain=["positive", "negative"],
            range=["#1f77b4", "#d62728"]  # Blue for positive, red for negative
        ),
        title="Gram Stain"
    )
    
    chart = alt.Chart(plot_df).mark_bar(
        strokeWidth=3  # Make the outline more visible
    ).encode(
        x=alt.X("Effectiveness:Q", 
                title="-log₁₀(MIC) (Higher = More Effective)", 
                scale=alt.Scale(domain=[-3, 3])),
        y=alt.Y("Bacteria_Sort:N", 
                sort=None,  # Use natural alphabetical order of our prefixed names
                title="Bacteria Species", 
                axis=alt.Axis(
                    labelLimit=200, 
                    labelFontSize=10,
                    labelExpr="split(datum.value, '_')[1]"  # Remove the order prefix from display
                )),
        color=color,
        stroke=stroke_color,  # Outline color based on gram staining
        tooltip=[
            alt.Tooltip("Bacteria:N", title="Bacteria"),
            alt.Tooltip("Antibiotic:N", title="Antibiotic"),
            alt.Tooltip("MIC:Q", title="MIC", format=".3f"),
            alt.Tooltip("Effectiveness:Q", title="Effectiveness", format=".2f"),
            alt.Tooltip("Gram_Staining:N", title="Gram Stain")
        ]
    ).properties(
        width="container",
        height=max(400, len(bacteria_order) * 30),
        title=alt.TitleParams(text=title, fontSize=16, anchor="start", offset=10)
    ).resolve_scale(color="independent")

    return chart

def main():
    st.set_page_config(page_title="Antibiotic Effectiveness Explorer - We're Prepared!", layout="wide")
    
    st.markdown('<h1 style="font-size:38px;">🧬 Antibiotic Effectiveness Explorer - We are Prepared!</h1>', unsafe_allow_html=True)
    st.markdown("""
    Explore antibiotic effectiveness against different bacterial strains.  
    Humans are generally prepared to fight the most common and dangerous bacterial infections with our arsenal of antibiotics.
    This tool visualizes the effectiveness of three key antibiotics: Penicillin, Streptomycin, and Neomycin, against various bacteria.
    """)
    st.markdown("")  # Empty line
    st.markdown("Bar outlines indicate Gram staining: **Blue** for Gram-positive, **Red** for Gram-negative. However, new strains can emerge that are resistant to our best antibiotics, making continued research essential.")
    st.markdown("")
    
    # Load data
    try:
        df_long, original_order = load_and_process_data()
    except FileNotFoundError:
        st.error("Data file 'bacteriaWithSpacer.csv' not found. Please ensure the file is in the correct location.")
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
        
        # Summary stats
        st.subheader("Data Summary")
        total_bacteria = df_long["Bacteria"].nunique()
        gram_pos = df_long[df_long["Gram_Staining"] == "positive"]["Bacteria"].nunique()
        gram_neg = df_long[df_long["Gram_Staining"] == "negative"]["Bacteria"].nunique()
        
        st.metric("Total Bacteria", total_bacteria)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Gram + (Blue outline)", gram_pos)
        with col2:
            st.metric("Gram - (Red outline)", gram_neg)
    
    # Chart
    plot_df, bacteria_order, title = create_chart_data(df_long, original_order, chart_type)
    chart = create_chart(plot_df, bacteria_order, title)
    st.altair_chart(chart, use_container_width=True)
    
    # Data table
    with st.expander("📊 View Raw Data"):
        display_df = plot_df[["Bacteria", "Gram_Staining", "Antibiotic", "MIC", "Effectiveness"]].round(3)
        st.dataframe(display_df, use_container_width=True)

if __name__ == "__main__":
    main()