import pandas as pd
import altair as alt
import numpy as np
import os

# Set working directory to current file
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load data
df = pd.read_csv("bacteria_timeline_tableau.csv")
df["log_MIC"] = df["MIC"].apply(lambda x: None if x <= 0 else round(-1 * np.log10(x), 2))
df["Gram_Emoji"] = df["Gram_Staining"].apply(lambda g: "🧪" if g == "positive" else "🧫")

# Define color gradient: red (bad) to green (good)
color_scale = alt.Scale(domain=[-2, 3], range=["#d73027", "#fee08b", "#1a9850"])

# Chart-specific takeaways
titles = {
    "Penicillin": "Penicillin: Most Effective Against Gram-Positive Bacteria 🧪",
    "Streptomycin": "Streptomycin: Moderate Effectiveness Across the Board",
    "Neomycin": "Neomycin: Broad-Spectrum Power with Some Resistance"
}

# Build each antibiotic chart
charts = []
for antibiotic in ["Penicillin", "Streptomycin", "Neomycin"]:
    sub_df = df[df["Antibiotic"] == antibiotic]

    bars = alt.Chart(sub_df).mark_bar().encode(
        x=alt.X("log_MIC:Q", title="-log10(MIC) (Effectiveness ↑)"),
        y=alt.Y("Bacteria:N", sort='-x'),
        color=alt.Color("log_MIC:Q", scale=color_scale, legend=alt.Legend(title="Effectiveness")),
        tooltip=["Bacteria", "MIC", "Gram_Staining"]
    )

    emoji = alt.Chart(sub_df).mark_text(
        align="left",
        baseline="middle",
        dx=5,
        fontSize=16
    ).encode(
        x="log_MIC:Q",
        y=alt.Y("Bacteria:N", sort='-x'),
        text="Gram_Emoji:N"
    )

    chart = (bars + emoji).properties(
        width=300,
        height=400,
        title=titles[antibiotic]
    )
    charts.append(chart)

# Combine all charts side-by-side with overall title
combined = alt.hconcat(*charts).properties(
    title={
        "text": "💊 Antibiotic Effectiveness Across Bacterial Species",
        "subtitle": ["Color = potency (green = strong), Emoji = Gram type 🧪🧫"],
        "fontSize": 22,
        "subtitleFontSize": 15,
        "anchor": "middle"
    }
)

# Legend explanation
legend_html = """
<br>
<div style="margin: 20px auto; max-width: 960px; font-family: sans-serif; font-size: 14px;">
  <h3 style="margin-bottom: 10px;">🔍 Legend</h3>
  <ul style="line-height: 1.8;">
    <li><b>Bar Color:</b> <span style="color:#d73027;">Red</span> = Low effectiveness, 
        <span style="color:#fee08b;">Yellow</span> = Moderate, 
        <span style="color:#1a9850;">Green</span> = High</li>
    <li><b>🧪</b> = Gram-positive bacteria (susceptible to beta-lactams)</li>
    <li><b>🧫</b> = Gram-negative bacteria (more resistant due to outer membrane)</li>
  </ul>
</div>
"""

# Summary paragraph
summary_html = """
<div style="padding: 20px; font-family: sans-serif; font-size: 14px; line-height: 1.6; max-width: 960px; margin: auto;">
  <p>
    This interactive chart compares how three antibiotics—Penicillin, Streptomycin, and Neomycin—
    perform across a range of bacterial species. Bars are color-coded by effectiveness 
    (green = highly effective, red = weak) based on the -log10 of MIC. Gram stain types 
    are indicated with emoji: 🧪 for Gram-positive, 🧫 for Gram-negative. 
    The visual reveals that Penicillin is most potent against Gram-positive strains, 
    while Neomycin shows broad-spectrum action. Streptomycin offers a balanced middle ground.
  </p>
</div>
"""

# Save full HTML
output_file = "combined_antibiotic_effectiveness.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(combined.to_html())
    f.write("<br>")  # 👈 Extra space between chart and legend
    f.write(legend_html)
    f.write(summary_html)

print(f"✅ Saved: {output_file}")
