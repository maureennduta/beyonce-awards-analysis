

# line graph-- 


# import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns

# # Load CSV
# df = pd.read_csv("beyonce-awards.csv")

# # Keep only wins
# df_wins = df[df["Result"].str.lower() == "won"].copy()

# # Standardize award names
# df_wins["Award_clean"] = df_wins["Award Institution"].str.strip().str.lower()

# major_awards = {
#     "bet awards": "BET Awards",
#     "bet hip hop awards": "BET Hip Hop Awards",
#     "grammy awards": "Grammy Awards",
#     "mtv video music awards": "MTV Video Music Awards",
#     "naacp image awards": "NAACP Image Awards"
# }

# # Filter only major awards and map display names
# df_major = df_wins[df_wins["Award_clean"].isin(major_awards.keys())].copy()
# df_major["Award_clean"] = df_major["Award_clean"].map(major_awards)

# # Convert Year to number
# df_major["Year"] = pd.to_numeric(df_major["Year"], errors="coerce")

# # Group by Year + Award
# df_grouped = df_major.groupby(["Year", "Award_clean"]).size().reset_index(name="Wins")

# # Plot line graph
# plt.figure(figsize=(12,6))
# sns.lineplot(
#     data=df_grouped,
#     x="Year",
#     y="Wins",
#     hue="Award_clean",
#     marker="o"
# )

# plt.title("Beyoncé's Major Awards Over Time", fontsize=14)
# plt.xlabel("Year")
# plt.ylabel("Number of Awards Won")
# # plt.xticks(rotation=45)
# plt.xticks(sorted(df_major['Year'].unique()))  # Force integer year ticks
# plt.legend(title="Award")
# plt.tight_layout()
# plt.show()


#point plot 

# import pandas as pd
# import seaborn as sns
# import matplotlib.pyplot as plt

# # Load dataset
# df = pd.read_csv("beyonce-awards.csv")

# # Keep only wins
# df_wins = df[df["Result"].str.lower() == "won"].copy()

# # Clean award names
# df_wins["Award_clean"] = df_wins["Award Institution"].str.strip().str.lower()

# # Major awards mapping
# major_awards = {
#     "bet awards": "BET Awards",
#     "bet hip hop awards": "BET Hip Hop Awards",
#     "grammy awards": "Grammy Awards",
#     "mtv video music awards": "MTV Video Music Awards",
#     "naacp image awards": "NAACP Image Awards"
# }

# # Filter to major awards only
# df_major = df_wins[df_wins["Award_clean"].isin(major_awards.keys())].copy()
# df_major["Award_clean"] = df_major["Award_clean"].map(major_awards)

# # Convert Year to numeric
# df_major["Year"] = pd.to_numeric(df_major["Year"], errors="coerce")

# # Count wins per year per award
# counts = df_major.groupby(["Year", "Award_clean"]).size().reset_index(name="Count")

# # ---- Seaborn Point Plot ----
# plt.figure(figsize=(10,6))
# sns.pointplot(
#     data=counts,
#     x="Year", y="Count",
#     hue="Award_clean",
#     dodge=True, markers="o"
# )

# plt.title("Beyoncé's Major Awards (Point Plot)", fontsize=14)
# plt.xlabel("Year")
# plt.ylabel("Number of Awards")
# plt.grid(True)
# plt.tight_layout()
# plt.show()


#heat map

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.colors import LinearSegmentedColormap

# Load dataset
df = pd.read_csv("beyonce-awards.csv")

# Keep only wins
df_wins = df[df["Result"].str.lower() == "won"].copy()

# Clean award names
df_wins["Award_clean"] = df_wins["Award Institution"].str.strip().str.lower()

# Major awards mapping
major_awards = {
    "bet awards": "BET Awards",
    "bet hip hop awards": "BET Hip Hop Awards",
    "grammy awards": "Grammy Awards",
    "mtv video music awards": "MTV Video Music Awards",
    "naacp image awards": "NAACP Image Awards"
}

# Filter to major awards only
df_major = df_wins[df_wins["Award_clean"].isin(major_awards.keys())].copy()
df_major["Award_clean"] = df_major["Award_clean"].map(major_awards)

# Convert Year to numeric
df_major["Year"] = pd.to_numeric(df_major["Year"], errors="coerce")

# Count wins per year per award
counts = df_major.groupby(["Year", "Award_clean"]).size().reset_index(name="Count")

# Pivot for heatmap (Years as rows, Awards as columns)
heatmap_data = counts.pivot(index="Year", columns="Award_clean", values="Count").fillna(0)

# Reverse the order of the years (rows)
heatmap_data = heatmap_data.sort_index(ascending=False)

# ---- Heatmap ----
plt.figure(figsize=(12,6))

sns.heatmap(
    heatmap_data,
    cmap="YlOrRd", annot=True, fmt=".0f", linewidths=0.5, cbar_kws={'label': 'Awards Won'}
)

plt.title("Beyoncé's Major Awards Heatmap", fontsize=14)
plt.ylabel("Year")
plt.xlabel("Award Institution")
plt.tight_layout()
plt.show()
