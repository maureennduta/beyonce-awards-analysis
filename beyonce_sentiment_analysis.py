import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

# Load the dataset
df = pd.read_csv("beyonce-awards.csv")

# Clean and prepare data
df['Award Category'] = df['Award Category'].fillna('Unknown')
df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
df = df.dropna(subset=['Year'])

print("="*60)
print("BEYONCÉ AWARDS - SENTIMENT & CATEGORY ANALYSIS")
print("="*60)
print(f"\nTotal Awards/Nominations: {len(df)}")
print(f"Unique Categories: {df['Award Category'].nunique()}")
print(f"Year Range: {int(df['Year'].min())} - {int(df['Year'].max())}")

# ============ CATEGORY THEME ANALYSIS ============
def categorize_sentiment(category):
    """Categorize awards by thematic sentiment/type"""
    category_lower = str(category).lower()
    
    # Achievement & Excellence
    if any(word in category_lower for word in ['best', 'top', 'favorite', 'outstanding', 'excellence']):
        return 'Achievement & Excellence'
    
    # Performance & Live
    elif any(word in category_lower for word in ['performance', 'live', 'stage', 'show']):
        return 'Performance & Live'
    
    # Video & Visual
    elif any(word in category_lower for word in ['video', 'visual', 'cinematography', 'direction']):
        return 'Video & Visual'
    
    # Artist Recognition
    elif any(word in category_lower for word in ['artist', 'entertainer', 'icon', 'legend']):
        return 'Artist Recognition'
    
    # Song & Music
    elif any(word in category_lower for word in ['song', 'single', 'record', 'track']):
        return 'Song & Music'
    
    # Album
    elif any(word in category_lower for word in ['album']):
        return 'Album'
    
    # Collaboration
    elif any(word in category_lower for word in ['collaboration', 'duet', 'featuring', 'group']):
        return 'Collaboration'
    
    # Special Recognition
    elif any(word in category_lower for word in ['lifetime', 'achievement', 'humanitarian', 'honor', 'special', 'tribute']):
        return 'Special Recognition'
    
    # Identity-based
    elif any(word in category_lower for word in ['female', 'woman', 'r&b', 'soul', 'urban', 'black']):
        return 'Identity-Based'
    
    else:
        return 'Other'

# Apply categorization
df['Theme'] = df['Award Category'].apply(categorize_sentiment)

# ============ KEY WORD EXTRACTION ============
def extract_keywords(category):
    """Extract meaningful keywords from category names"""
    # Remove common words and extract key terms
    stop_words = ['the', 'and', 'or', 'of', 'in', 'for', 'a', 'an']
    words = re.findall(r'\b[a-zA-Z]+\b', str(category).lower())
    return [w for w in words if w not in stop_words and len(w) > 3]

all_keywords = []
for cat in df['Award Category']:
    all_keywords.extend(extract_keywords(cat))

keyword_freq = Counter(all_keywords).most_common(15)

print("\n" + "="*60)
print("TOP 15 KEYWORDS IN AWARD CATEGORIES")
print("="*60)
for word, count in keyword_freq:
    print(f"{word.capitalize():<20} {count:>3} occurrences")

# ============ THEME DISTRIBUTION ============
theme_counts = df['Theme'].value_counts()
print("\n" + "="*60)
print("AWARD THEMES DISTRIBUTION")
print("="*60)
for theme, count in theme_counts.items():
    percentage = (count / len(df)) * 100
    print(f"{theme:<30} {count:>3} ({percentage:>5.1f}%)")

# ============ WIN RATE BY THEME ============
df_wins = df[df['Result'].str.lower() == 'won']
win_rate_by_theme = df.groupby('Theme').apply(
    lambda x: (x['Result'].str.lower() == 'won').sum() / len(x) * 100
).sort_values(ascending=False)

print("\n" + "="*60)
print("WIN RATE BY THEME")
print("="*60)
for theme, rate in win_rate_by_theme.items():
    total = len(df[df['Theme'] == theme])
    wins = len(df_wins[df_wins['Theme'] == theme])
    print(f"{theme:<30} {rate:>5.1f}% ({wins}/{total})")

# ============ VISUALIZATIONS ============

# 1. Theme Distribution Pie Chart
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

theme_counts_top = theme_counts.head(8)
colors = sns.color_palette("husl", len(theme_counts_top))
axes[0, 0].pie(theme_counts_top.values, labels=theme_counts_top.index, 
               autopct='%1.1f%%', startangle=90, colors=colors)
axes[0, 0].set_title('Distribution of Award Themes (Top 8)', fontsize=14, fontweight='bold')

# 2. Top Keywords Bar Chart
keywords_df = pd.DataFrame(keyword_freq[:10], columns=['Keyword', 'Count'])
sns.barplot(data=keywords_df, y='Keyword', x='Count', palette='viridis', ax=axes[0, 1])
axes[0, 1].set_title('Top 10 Keywords in Award Categories', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('Frequency')

# 3. Win Rate by Theme
win_rate_df = win_rate_by_theme.reset_index()
win_rate_df.columns = ['Theme', 'Win_Rate']
sns.barplot(data=win_rate_df, x='Win_Rate', y='Theme', palette='coolwarm', ax=axes[1, 0])
axes[1, 0].set_title('Win Rate by Award Theme', fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('Win Rate (%)')
axes[1, 0].axvline(x=50, color='red', linestyle='--', alpha=0.5, label='50% threshold')
axes[1, 0].legend()

# 4. Theme Evolution Over Time
theme_by_year = df[df['Result'].str.lower() == 'won'].groupby(['Year', 'Theme']).size().reset_index(name='Count')
top_themes = theme_counts.head(5).index

plt.sca(axes[1, 1])
for theme in top_themes:
    theme_data = theme_by_year[theme_by_year['Theme'] == theme]
    if len(theme_data) > 0:
        axes[1, 1].plot(theme_data['Year'], theme_data['Count'], marker='o', label=theme, alpha=0.7)

axes[1, 1].set_title('Award Wins by Theme Over Time (Top 5 Themes)', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('Year')
axes[1, 1].set_ylabel('Number of Wins')
axes[1, 1].legend(fontsize=8, loc='best')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('beyonce_sentiment_analysis.png', dpi=300, bbox_inches='tight')
print("\n" + "="*60)
print("Visualization saved as 'beyonce_sentiment_analysis.png'")
print("="*60)
plt.show()

# ============ DETAILED CATEGORY BREAKDOWN ============
print("\n" + "="*60)
print("MOST COMMON AWARD CATEGORIES (Top 20)")
print("="*60)
category_counts = df['Award Category'].value_counts().head(20)
for i, (category, count) in enumerate(category_counts.items(), 1):
    wins = len(df[(df['Award Category'] == category) & (df['Result'].str.lower() == 'won')])
    print(f"{i:>2}. {category:<50} {count:>3} ({wins} wins)")

# ============ TEMPORAL SENTIMENT SHIFT ============
print("\n" + "="*60)
print("THEME TRENDS BY DECADE")
print("="*60)
df['Decade'] = (df['Year'] // 10) * 10
decade_themes = df[df['Result'].str.lower() == 'won'].groupby(['Decade', 'Theme']).size().unstack(fill_value=0)
print(decade_themes.to_string())
