import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Load the dataset
file_path = "beyonce-awards.csv"
df = pd.read_csv(file_path)

# Inspect the first few rows
print(df.head())

print(df.info())
print(df.describe(include='all'))
print(df.isnull().sum())

df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df['Award Institution'] = df['Award Institution'].str.strip()
df = df.dropna(subset=['Year'])


awards_per_year = df.groupby('Year').size().reset_index(name='Count')
print(awards_per_year.head())

institution_counts = df['Award Institution'].value_counts().reset_index()
institution_counts.columns = ['Award Institution', 'Count']
print(institution_counts.head())

heatmap_data = pd.crosstab(df['Year'], df['Award Institution'])
print(heatmap_data.head())

peak_year = awards_per_year.loc[awards_per_year['Count'].idxmax()]
print(f"Peak year: {peak_year['Year']} with {peak_year['Count']} awards")


##viz-bump chart how each award institution’s rank changed over the years.
# Compute awards count per year and institution
rank_data = df.groupby(['Year', 'Award Institution']).size().reset_index(name='Count')

# # Rank institutions within each year (1 = highest count)
rank_data['Rank'] = rank_data.groupby('Year')['Count'].rank(ascending=False, method='first')
plt.figure(figsize=(10, 6))

# Draw a line for each institution showing how its rank changes over time
for institution in rank_data['Award Institution'].unique():
    inst_data = rank_data[rank_data['Award Institution'] == institution]
    plt.plot(inst_data['Year'], inst_data['Rank'], marker='o', label=institution, alpha=0.7)

plt.gca().invert_yaxis()  # Rank 1 on top
plt.title("Award Institution Rankings Over Time", fontsize=16)
plt.xlabel("Year")
plt.ylabel("Rank (1 = Most Awards)")
plt.legend(
    bbox_to_anchor=(1.05, 1),
    loc='upper left',
    fontsize=7,
    ncol=2,
    frameon=False
)
plt.tight_layout()
plt.show()


sns.clustermap(
    heatmap_data,
    cmap='YlGnBu',
    figsize=(14, 10),
    linewidths=0.5,
    cbar_kws={'label': 'Awards Won'},
    annot=True,
    fmt='d'
)
plt.suptitle("Clustered Heatmap of Beyoncé's Awards", y=1.02, fontsize=16)
plt.show()

# Prepare data for area plot: years as index, institutions as columns
stream_data = df.groupby(['Year', 'Award Institution']).size().unstack(fill_value=0)

plt.figure(figsize=(14, 8))
plt.stackplot(
    stream_data.index,
    stream_data.T,              # stackplot wants each row to be a “series”
    labels=stream_data.columns,
    alpha=0.8
)

plt.title("Share of Awards by Institution Over Time", fontsize=16)
plt.xlabel("Year")
plt.ylabel("Number of Awards")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left',fontsize=7,
     ncol=2,
     frameon=False)


plt.tight_layout()
plt.show()
