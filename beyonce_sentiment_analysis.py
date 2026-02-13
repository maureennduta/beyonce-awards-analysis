import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
import streamlit as st

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(layout="wide")

# =========================
# REMOVE STREAMLIT CHROME
# =========================
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# FIX DROPDOWN MENU (SELECTBOX POPUP)
st.markdown("""
<style>

/* Dropdown popup panel */
ul[role="listbox"] {
    background-color: #EFE6D6 !important;
    color: #1F1A17 !important;
    border: 1px solid #D8CDB8 !important;
}

/* Individual options */
ul[role="listbox"] li {
    background-color: #EFE6D6 !important;
    color: #1F1A17 !important;
}

/* Hover state */
ul[role="listbox"] li:hover {
    background-color: #E6DBC8 !important;
    color: #1F1A17 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# EDITORIAL DESIGN SYSTEM
# =========================
st.markdown("""
<style>

.stApp {
    background-color: #F7F3EA;
    color: #1F1A17;
    font-family: Georgia, serif;
}

h1, h2, h3 {
    font-family: "Playfair Display", serif;
    color: #1F1A17;
}

p, div {
    color: #1F1A17;
}

.block-container {
    padding-top: 2rem;
}

div[data-baseweb="select"] {
    background-color: #EFE6D6 !important;
    border-radius: 6px;
    border: 1px solid #D8CDB8;
}

div[data-baseweb="select"] * {
    color: #1F1A17 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HERO SECTION
# =========================
st.markdown("""
<h1 style="
font-size:42px;
font-weight:600;
letter-spacing:1px;
margin-bottom:0;
">
Beyoncé: Recognition vs Dominance
</h1>

<div style="
font-size:16px;
color:#6B5E52;
margin-bottom:30px;
">
A data study of awards, wins, and cultural impact
</div>

<hr style="border:1px solid #C6A34A;">
""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

# =========================
# LOAD DATA
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
# MAIN PANEL
# =========================
with col1:

    if view == "Theme Distribution":
        st.markdown("## RECOGNITION BY CATEGORY")

        fig, ax = plt.subplots(figsize=(9, 6))
        fig.patch.set_facecolor("#F7F3EA")
        ax.set_facecolor("#F7F3EA")

        top = theme_counts.head(8).sort_values()
        ax.barh(top.index, top.values, color="#C6A34A")

        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.xaxis.grid(True, alpha=0.15)

        st.pyplot(fig)

    if view == "Keyword Analysis":
        st.markdown("## AWARD LANGUAGE PATTERNS")

        fig, ax = plt.subplots(figsize=(9, 6))
        fig.patch.set_facecolor("#F7F3EA")
        ax.set_facecolor("#F7F3EA")

        keywords_df = pd.DataFrame(keyword_freq[:10], columns=['Keyword', 'Count'])
        ax.barh(keywords_df['Keyword'], keywords_df['Count'], color="#C6A34A")

        ax.spines[['top', 'right', 'left']].set_visible(False)

        st.pyplot(fig)

    if view == "Win Rate by Theme":
        st.markdown("## NOT ALL RECOGNITION CONVERTS INTO WINS")

        fig, ax = plt.subplots(figsize=(9, 6))
        fig.patch.set_facecolor("#F7F3EA")
        ax.set_facecolor("#F7F3EA")

        win_rate_df = win_rate_by_theme.reset_index()
        win_rate_df.columns = ['Theme', 'Win Rate']
        win_rate_df = win_rate_df.sort_values("Win Rate")

        ax.barh(win_rate_df["Theme"], win_rate_df["Win Rate"], color="#C6A34A")
        ax.axvline(50, linestyle='--', alpha=0.4)

        ax.spines[['top', 'right', 'left']].set_visible(False)
        ax.xaxis.grid(True, alpha=0.15)
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

    st.markdown("""
    <div style="
        background:#EFE6D6;
        padding:20px;
        border-radius:6px;
        border-left:4px solid #C6A34A;
    ">
    <h3 style="margin-top:0;">Editor’s Note</h3>
    </div>
    """, unsafe_allow_html=True)

    context_map = {
        "Theme Distribution":
            "Recognition concentrates around performance, visibility, and excellence.",
        "Keyword Analysis":
            "Award language reinforces dominance over experimentation.",
        "Win Rate by Theme":
            "Nomination volume does not guarantee wins.",
        "Theme Trends Over Time":
            "Recognition shifts toward cultural impact over time.",
        "Awards vs Release Context":
            "Awards persist even during non-release years."
    }

    st.write(context_map[view])