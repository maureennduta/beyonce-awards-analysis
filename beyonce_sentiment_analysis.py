import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import streamlit as st

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


view = st.selectbox(
    "Choose a visualization",
    [
        "Theme Distribution",
        "Keyword Analysis",
        "Win Rate by Theme",
        "Theme Trends Over Time",
        "Awards vs Release Context"
    ]
)

# =========================
# VISUALIZATIONS (ALL 5)
# =========================
# fig, axes = plt.subplots(3, 2, figsize=(18, 18))
# axes = axes.flatten()

# -------------------------
# 1. Theme Distribution
# -------------------------
if view == "Theme Distribution":
    fig, ax = plt.subplots(figsize=(8, 6))

    theme_counts_top = theme_counts.head(8)
    ax.bar(
        theme_counts_top.index,
        theme_counts_top.values,
        color=sns.color_palette("husl", len(theme_counts_top))
    ) 
    ax.set_title("Distribution of Award Themes (Top 8)", fontsize=14)
    ax.set_ylabel("Count")
    ax.set_xticklabels(theme_counts_top.index, rotation=45, ha="right")

    st.pyplot(fig)

# -------------------------
# 2. Keyword Frequency
# -------------------------
if view == "Keyword Analysis":
    fig, ax = plt.subplots()
    keywords_df = pd.DataFrame(keyword_freq[:10], columns=['Keyword', 'Count'])
    sns.barplot(
        data=keywords_df,
        x='Count',
        y='Keyword',
        palette='viridis',
        ax=ax
    )
    ax.set_title("Top Keywords in Award Categories", fontsize=14)

    st.pyplot(fig)

# -------------------------
# 3. Win Rate by Theme
# -------------------------
if view == "Win Rate by Theme":
    fig, ax = plt.subplots()
    win_rate_df = win_rate_by_theme.reset_index()
    win_rate_df.columns = ['Theme', 'Win Rate']

    sns.barplot(
        data=win_rate_df,
        x='Win Rate',
        y='Theme',
        palette='coolwarm',
        ax=ax
    )
    ax.axvline(50, color='red', linestyle='--', alpha=0.5)
    ax.set_title("Win Rate by Award Theme", fontsize=14)
    st.pyplot(fig)

# -------------------------
# 4. Theme Evolution Over Time
# -------------------------
if view == "Theme Trends Over Time":
    fig, ax = plt.subplots()
    top_themes = theme_counts.head(5).index

    for theme in top_themes:
        tdata = theme_by_year[theme_by_year['Theme'] == theme]
        ax.plot(tdata['Year'], tdata['Count'], marker='o', label=theme)

    ax.set_title("Award Wins by Theme Over Time", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Wins")
    ax.legend(fontsize=8)
    st.pyplot(fig)

# -------------------------
# 5. Awards vs Release Context
# -------------------------
if view == "Awards vs Release Context":
    fig, ax = plt.subplots()
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

    ax.plot(
    awards_per_year['Year'],
    awards_per_year['Awards'],
    marker='o',
    linewidth=2
)

    for year, album in release_years.items():
        ax.axvline(year, linestyle='--', alpha=0.4)
        ax.text(year, ax.get_ylim()[1]*0.95, album,
                 rotation=90, fontsize=8, verticalalignment='top')

    ax.set_title("Awards Received vs Release Years", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Total Awards")
    st.pyplot(fig)
