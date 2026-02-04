import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import streamlit as st

# =========================
# PAGE SETUP
# =========================
st.set_page_config(layout="wide")

col1, col2 = st.columns([3, 1])

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
# VIEW SELECTOR
# =========================
view = st.selectbox(
    "Explore the story from different angles",
    [
        "Theme Distribution",
        "Keyword Analysis",
        "Win Rate by Theme",
        "Theme Trends Over Time",
        "Awards vs Release Context"
    ]
)

# =========================
# MAIN LAYOUT
# =========================
with col1:
    if view == "Theme Distribution":
        st.subheader("Recognition Skews Toward Performance and Visibility")

        fig, ax = plt.subplots(figsize=(8, 6))
        top = theme_counts.head(8)
        ax.bar(top.index, top.values, color=sns.color_palette("husl", len(top)))
        ax.set_ylabel("Number of Awards")
        ax.set_xticklabels(top.index, rotation=45, ha="right")
        sns.despine()
        st.pyplot(fig)

    if view == "Keyword Analysis":
        st.subheader("Award Language Emphasizes Excellence Over Experimentation")

        fig, ax = plt.subplots(figsize=(8, 6))
        keywords_df = pd.DataFrame(keyword_freq[:10], columns=['Keyword', 'Count'])
        sns.barplot(data=keywords_df, x='Count', y='Keyword', ax=ax)
        sns.despine()
        st.pyplot(fig)

    if view == "Win Rate by Theme":
        st.subheader("Not All Recognition Converts Into Wins")

        fig, ax = plt.subplots(figsize=(8, 6))
        win_rate_df = win_rate_by_theme.reset_index()
        win_rate_df.columns = ['Theme', 'Win Rate']
        sns.barplot(data=win_rate_df, x='Win Rate', y='Theme', ax=ax)
        ax.axvline(50, linestyle='--', alpha=0.4)
        sns.despine()
        st.pyplot(fig)

    if view == "Theme Trends Over Time":
        st.subheader("Career Recognition Shifts From Songs to Cultural Impact")

        fig, ax = plt.subplots(figsize=(8, 6))
        for theme in theme_counts.head(5).index:
            data = theme_by_year[theme_by_year['Theme'] == theme]
            ax.plot(data['Year'], data['Count'], marker='o', label=theme)

        ax.legend(fontsize=8)
        ax.set_ylabel("Awards Won")
        sns.despine()
        st.pyplot(fig)

    if view == "Awards vs Release Context":
        st.subheader("Awards Continue Even When Albums Pause")

        fig, ax = plt.subplots(figsize=(8, 6))
        awards_per_year = df.groupby('Year').size().reset_index(name='Awards')
        ax.plot(awards_per_year['Year'], awards_per_year['Awards'], marker='o')

        release_years = {
            2003: "Dangerously in Love",
            2006: "B'Day",
            2008: "I Am... Sasha Fierce",
            2011: "4",
            2013: "Beyoncé",
            2016: "Lemonade",
            2019: "The Lion King: The Gift"
        }

        for year, album in release_years.items():
            ax.axvline(year, linestyle='--', alpha=0.3)
            ax.text(year, ax.get_ylim()[1]*0.95, album,
                    rotation=90, fontsize=8, va='top')

        sns.despine()
        st.pyplot(fig)

# =========================
# CONTEXT PANEL
# =========================
with col2:
    st.subheader("Editor’s Note")

    context_map = {
        "Theme Distribution":
            "Recognition is concentrated around performance, visibility, and excellence rather than niche categorization.",

        "Keyword Analysis":
            "Award language consistently reinforces dominance, quality, and leadership over experimentation.",

        "Win Rate by Theme":
            "High nomination volume does not guarantee wins, revealing which forms of recognition carry weight.",

        "Theme Trends Over Time":
            "Over time, awards shift away from individual songs toward broader cultural and artistic impact.",

        "Awards vs Release Context":
            "Recognition persists even in non-release years, indicating sustained cultural presence beyond albums."
    }

    st.write(context_map[view])
