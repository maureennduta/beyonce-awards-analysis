import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

# =========================
# LOAD AND PREP DATA
# =========================
df = pd.read_csv("beyonce-awards.csv")

df['Award Category'] = df['Award Category'].fillna('Unknown')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df['Award Institution'] = df['Award Institution'].str.strip()
df = df.dropna(subset=['Year'])

# =========================
# THEME CATEGORIZATION
# =========================
def categorize_sentiment(category):
    c = str(category).lower()

    if any(w in c for w in ['best', 'top', 'favorite', 'outstanding', 'excellence']):
        return 'Achievement & Excellence'
    elif any(w in c for w in ['performance', 'live', 'stage', 'show']):
        return 'Performance & Live'
    elif any(w in c for w in ['video', 'visual', 'cinematography', 'direction']):
        return 'Video & Visual'
    elif any(w in c for w in ['artist', 'entertainer', 'icon', 'legend']):
        return 'Artist Recognition'
    elif any(w in c for w in ['song', 'single', 'record', 'track']):
        return 'Song & Music'
    elif 'album' in c:
        return 'Album'
    elif any(w in c for w in ['collaboration', 'duet', 'featuring', 'group']):
        return 'Collaboration'
    elif any(w in c for w in ['lifetime', 'achievement', 'humanitarian', 'honor', 'tribute']):
        return 'Special Recognition'
    elif any(w in c for w in ['female', 'woman', 'r&b', 'urban', 'black']):
        return 'Identity-Based'
    else:
        return 'Other'

df['Theme'] = df['Award Category'].apply(categorize_sentiment)

# =========================
# KEYWORD EXTRACTION
# =========================
def extract_keywords(category):
    stop_words = ['the', 'and', 'or', 'of', 'in', 'for', 'with', 'to']
    words = re.findall(r'\b[a-zA-Z]+\b', str(category).lower())
    return [w for w in words if w not in stop_words and len(w) > 3]

all_keywords = []
for cat in df['Award Category']:
    all_keywords.extend(extract_keywords(cat))

keyword_freq = Counter(all_keywords).most_common(15)

# =========================
# CORE METRICS
# =========================
df_wins = df[df['Result'].str.lower() == 'won']

theme_counts = df['Theme'].value_counts()
win_rate_by_theme = df.groupby('Theme').apply(
    lambda x: (x['Result'].str.lower() == 'won').sum() / len(x) * 100
).sort_values(ascending=False)

theme_by_year = df_wins.groupby(['Year', 'Theme']).size().reset_index(name='Count')

# =========================
# VISUALIZATIONS (ALL 5)
# =========================
fig, axes = plt.subplots(3, 2, figsize=(18, 18))
axes = axes.flatten()

# -------------------------
# 1. Theme Distribution
# -------------------------
theme_counts_top = theme_counts.head(8)
axes[0].bar(
    theme_counts_top.index,
    theme_counts_top.values,
    color=sns.color_palette("husl", len(theme_counts_top))
)
axes[0].set_title("Distribution of Award Themes (Top 8)", fontsize=14)
axes[0].set_ylabel("Count")
axes[0].tick_params(axis='x', rotation=45)

# -------------------------
# 2. Keyword Frequency
# -------------------------
keywords_df = pd.DataFrame(keyword_freq[:10], columns=['Keyword', 'Count'])
sns.barplot(
    data=keywords_df,
    x='Count',
    y='Keyword',
    palette='viridis',
    ax=axes[1]
)
axes[1].set_title("Top Keywords in Award Categories", fontsize=14)

# -------------------------
# 3. Win Rate by Theme
# -------------------------
win_rate_df = win_rate_by_theme.reset_index()
win_rate_df.columns = ['Theme', 'Win Rate']

sns.barplot(
    data=win_rate_df,
    x='Win Rate',
    y='Theme',
    palette='coolwarm',
    ax=axes[2]
)
axes[2].axvline(50, color='red', linestyle='--', alpha=0.5)
axes[2].set_title("Win Rate by Award Theme", fontsize=14)

# -------------------------
# 4. Theme Evolution Over Time
# -------------------------
top_themes = theme_counts.head(5).index

for theme in top_themes:
    tdata = theme_by_year[theme_by_year['Theme'] == theme]
    axes[3].plot(tdata['Year'], tdata['Count'], marker='o', label=theme)

axes[3].set_title("Award Wins by Theme Over Time", fontsize=14)
axes[3].set_xlabel("Year")
axes[3].set_ylabel("Wins")
axes[3].legend(fontsize=8)

# -------------------------
# 5. Awards vs Release Context
# -------------------------
release_years = {
    2003: "Dangerously in Love",
    2006: "B'Day",
    2008: "I Am... Sasha Fierce",
    2011: "4",
    2013: "Beyoncé",
    2016: "Lemonade",
    2019: "The Lion King: The Gift"
}

awards_per_year = df.groupby('Year').size().reset_index(name='Awards')

axes[4].plot(
    awards_per_year['Year'],
    awards_per_year['Awards'],
    marker='o',
    linewidth=2
)

for year, album in release_years.items():
    axes[4].axvline(year, linestyle='--', alpha=0.4)
    axes[4].text(year, axes[4].get_ylim()[1]*0.95, album,
                 rotation=90, fontsize=8, verticalalignment='top')

axes[4].set_title("Awards Received vs Release Years", fontsize=14)
axes[4].set_xlabel("Year")
axes[4].set_ylabel("Total Awards")

# -------------------------
# EMPTY PANEL (INTENTIONAL)
# -------------------------
axes[5].axis('off')

plt.tight_layout()
plt.savefig("beyonce_awards_full_analysis.png", dpi=300, bbox_inches="tight")
plt.show()
