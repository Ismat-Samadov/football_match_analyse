"""
Football Match Analysis - Business Insights Chart Generator
Generates visualizations focused on strategic business insights
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for professional-looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

# Create charts directory
Path("charts").mkdir(exist_ok=True)

# Load datasets
print("Loading datasets...")
results = pd.read_csv('data/results.csv')
goalscorers = pd.read_csv('data/goalscorers.csv')
shootouts = pd.read_csv('data/shootouts.csv')

# Data preprocessing
results['date'] = pd.to_datetime(results['date'])
results['year'] = results['date'].dt.year
results['decade'] = (results['year'] // 10) * 10
goalscorers['date'] = pd.to_datetime(goalscorers['date'])
shootouts['date'] = pd.to_datetime(shootouts['date'])

print(f"Loaded {len(results)} matches, {len(goalscorers)} goals, {len(shootouts)} shootouts")

# ============================================================================
# CHART 1: Market Growth - International Football Match Volume Over Time
# ============================================================================
print("Generating Chart 1: Match Volume Trends...")
yearly_matches = results.groupby('year').size().reset_index(name='matches')

fig, ax = plt.subplots(figsize=(14, 6))
ax.bar(yearly_matches['year'], yearly_matches['matches'], color='#2E86AB', alpha=0.8, width=0.8)
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Matches', fontsize=12, fontweight='bold')
ax.set_title('International Football Market Growth: Match Volume Trends (1872-2026)',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add trend annotations
for decade in [1950, 1990, 2020]:
    matches = yearly_matches[yearly_matches['year'] == decade]['matches'].values
    if len(matches) > 0:
        ax.axvline(decade, color='red', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.savefig('charts/01_match_volume_trends.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 2: Strategic Value of Home Advantage
# ============================================================================
print("Generating Chart 2: Home Advantage Analysis...")
results['home_win'] = results['home_score'] > results['away_score']
results['away_win'] = results['away_score'] > results['home_score']
results['draw'] = results['home_score'] == results['away_score']

# Exclude neutral venues for home advantage analysis
home_games = results[results['neutral'] == False]
home_stats = pd.DataFrame({
    'Outcome': ['Home Win', 'Draw', 'Away Win'],
    'Matches': [
        home_games['home_win'].sum(),
        home_games['draw'].sum(),
        home_games['away_win'].sum()
    ]
})
home_stats['Percentage'] = (home_stats['Matches'] / home_stats['Matches'].sum() * 100).round(1)

fig, ax = plt.subplots(figsize=(10, 6))
colors = ['#06A77D', '#F4D35E', '#EE6352']
bars = ax.bar(home_stats['Outcome'], home_stats['Percentage'], color=colors, alpha=0.8, edgecolor='black')

# Add percentage labels on bars
for i, (bar, pct, count) in enumerate(zip(bars, home_stats['Percentage'], home_stats['Matches'])):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{pct}%\n({count:,} matches)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylabel('Percentage of Matches (%)', fontsize=12, fontweight='bold')
ax.set_title('Strategic Value of Home Advantage in International Football',
             fontsize=14, fontweight='bold', pad=20)
ax.set_ylim(0, max(home_stats['Percentage']) * 1.2)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('charts/02_home_advantage_value.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 3: Tournament Type Performance - Competitive vs Friendly
# ============================================================================
print("Generating Chart 3: Tournament Performance Analysis...")
results['tournament_category'] = results['tournament'].apply(
    lambda x: 'Competitive' if any(comp in str(x) for comp in
    ['FIFA World Cup', 'qualification', 'Championship', 'Cup of Nations', 'Gold Cup', 'Copa América'])
    else 'Friendly/Other'
)

tournament_stats = results.groupby('tournament_category').agg({
    'home_score': 'mean',
    'away_score': 'mean',
    'date': 'count'
}).round(2)
tournament_stats.columns = ['Avg Home Goals', 'Avg Away Goals', 'Total Matches']
tournament_stats['Avg Total Goals'] = (tournament_stats['Avg Home Goals'] +
                                       tournament_stats['Avg Away Goals']).round(2)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Match distribution
ax1.barh(tournament_stats.index, tournament_stats['Total Matches'],
         color=['#E63946', '#457B9D'], alpha=0.8, edgecolor='black')
ax1.set_xlabel('Number of Matches', fontsize=11, fontweight='bold')
ax1.set_title('Match Distribution by Type', fontsize=12, fontweight='bold')
for i, v in enumerate(tournament_stats['Total Matches']):
    ax1.text(v, i, f' {v:,}', va='center', fontsize=10, fontweight='bold')
ax1.grid(axis='x', alpha=0.3)

# Goal scoring comparison
x = np.arange(len(tournament_stats.index))
width = 0.35
bars1 = ax2.bar(x - width/2, tournament_stats['Avg Home Goals'], width,
                label='Avg Home Goals', color='#06A77D', alpha=0.8, edgecolor='black')
bars2 = ax2.bar(x + width/2, tournament_stats['Avg Away Goals'], width,
                label='Avg Away Goals', color='#F77F00', alpha=0.8, edgecolor='black')

ax2.set_ylabel('Average Goals per Match', fontsize=11, fontweight='bold')
ax2.set_title('Goal Scoring Patterns by Match Type', fontsize=12, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(tournament_stats.index)
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

# Add value labels
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}', ha='center', va='bottom', fontsize=9)

plt.suptitle('Competitive vs Friendly Match Performance Analysis',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('charts/03_tournament_type_performance.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 4: Top 15 Teams by Win Rate - Market Leaders
# ============================================================================
print("Generating Chart 4: Top Performing Teams...")
# Calculate team performance
team_stats = []
for team in pd.concat([results['home_team'], results['away_team']]).unique():
    home_matches = results[results['home_team'] == team]
    away_matches = results[results['away_team'] == team]

    total_matches = len(home_matches) + len(away_matches)
    if total_matches < 50:  # Minimum threshold for relevance
        continue

    wins = (home_matches['home_win'].sum() + away_matches['away_win'].sum())
    win_rate = (wins / total_matches * 100)

    team_stats.append({
        'Team': team,
        'Total Matches': total_matches,
        'Wins': wins,
        'Win Rate (%)': round(win_rate, 1)
    })

team_performance = pd.DataFrame(team_stats).sort_values('Win Rate (%)', ascending=False).head(15)

fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.barh(range(len(team_performance)), team_performance['Win Rate (%)'],
               color='#2E86AB', alpha=0.8, edgecolor='black')

# Color top 3 differently
for i in range(min(3, len(bars))):
    bars[i].set_color('#06A77D')
    bars[i].set_alpha(0.9)

ax.set_yticks(range(len(team_performance)))
ax.set_yticklabels(team_performance['Team'])
ax.set_xlabel('Win Rate (%)', fontsize=12, fontweight='bold')
ax.set_title('Top 15 National Teams by Win Rate - Market Performance Leaders',
             fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, row) in enumerate(zip(bars, team_performance.iterrows())):
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height()/2,
            f" {row[1]['Win Rate (%)']}% ({row[1]['Total Matches']} matches)",
            va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/04_top_teams_win_rate.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 5: Goal Scoring Timing - Tactical Insights
# ============================================================================
print("Generating Chart 5: Goal Timing Analysis...")
# Categorize goals by time period
def categorize_minute(minute):
    if pd.isna(minute):
        return 'Unknown'
    if minute <= 15:
        return '0-15 min'
    elif minute <= 30:
        return '16-30 min'
    elif minute <= 45:
        return '31-45 min'
    elif minute <= 60:
        return '46-60 min'
    elif minute <= 75:
        return '61-75 min'
    else:
        return '76-90+ min'

goalscorers['period'] = goalscorers['minute'].apply(categorize_minute)
period_order = ['0-15 min', '16-30 min', '31-45 min', '46-60 min', '61-75 min', '76-90+ min']
goal_timing = goalscorers[goalscorers['period'] != 'Unknown']['period'].value_counts().reindex(period_order)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(range(len(goal_timing)), goal_timing.values,
              color=['#E63946', '#F77F00', '#F4D35E', '#06A77D', '#2E86AB', '#6A4C93'],
              alpha=0.8, edgecolor='black')

ax.set_xticks(range(len(goal_timing)))
ax.set_xticklabels(goal_timing.index, rotation=0)
ax.set_ylabel('Number of Goals', fontsize=12, fontweight='bold')
ax.set_xlabel('Match Period', fontsize=12, fontweight='bold')
ax.set_title('Goal Scoring Patterns by Match Period - When Teams Strike Most',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels and percentages
total_goals = goal_timing.sum()
for i, (bar, val) in enumerate(zip(bars, goal_timing.values)):
    height = bar.get_height()
    pct = (val / total_goals * 100)
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:,}\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/05_goal_timing_patterns.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 6: Penalty Shootout Success Rates - High-Pressure Performance
# ============================================================================
print("Generating Chart 6: Shootout Performance...")
# Calculate shootout performance by team
shootout_stats = []
for team in pd.concat([shootouts['home_team'], shootouts['away_team']]).unique():
    team_shootouts = shootouts[(shootouts['home_team'] == team) | (shootouts['away_team'] == team)]
    total = len(team_shootouts)
    if total < 5:  # Minimum threshold
        continue
    wins = len(team_shootouts[team_shootouts['winner'] == team])
    win_rate = (wins / total * 100)

    shootout_stats.append({
        'Team': team,
        'Shootouts': total,
        'Wins': wins,
        'Win Rate (%)': round(win_rate, 1)
    })

shootout_performance = pd.DataFrame(shootout_stats).sort_values('Win Rate (%)', ascending=False).head(15)

fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.barh(range(len(shootout_performance)), shootout_performance['Win Rate (%)'],
               color='#E63946', alpha=0.8, edgecolor='black')

# Highlight top performers
for i in range(min(3, len(bars))):
    bars[i].set_color('#06A77D')
    bars[i].set_alpha(0.9)

ax.set_yticks(range(len(shootout_performance)))
ax.set_yticklabels(shootout_performance['Team'])
ax.set_xlabel('Shootout Win Rate (%)', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Teams in Penalty Shootout Success - Clutch Performance Under Pressure',
             fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, row) in enumerate(zip(bars, shootout_performance.iterrows())):
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height()/2,
            f" {row[1]['Win Rate (%)']}% ({row[1]['Wins']}/{row[1]['Shootouts']})",
            va='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/06_shootout_success_rates.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 7: Goals Per Match Evolution - Game Dynamics Over Decades
# ============================================================================
print("Generating Chart 7: Scoring Trends Evolution...")
results['total_goals'] = results['home_score'] + results['away_score']
decade_goals = results.groupby('decade').agg({
    'total_goals': 'mean',
    'date': 'count'
}).round(2)
decade_goals.columns = ['Avg Goals per Match', 'Total Matches']
decade_goals = decade_goals[decade_goals['Total Matches'] >= 100]  # Filter out sparse decades

fig, ax1 = plt.subplots(figsize=(14, 6))

color = '#2E86AB'
ax1.set_xlabel('Decade', fontsize=12, fontweight='bold')
ax1.set_ylabel('Average Goals per Match', fontsize=12, fontweight='bold', color=color)
line1 = ax1.plot(decade_goals.index, decade_goals['Avg Goals per Match'],
                 color=color, marker='o', linewidth=3, markersize=8, label='Avg Goals')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, alpha=0.3)

# Add trend line
z = np.polyfit(decade_goals.index, decade_goals['Avg Goals per Match'], 2)
p = np.poly1d(z)
ax1.plot(decade_goals.index, p(decade_goals.index), "--",
         color='red', linewidth=2, alpha=0.7, label='Trend')

ax1.set_title('Evolution of Goal Scoring Patterns Over Time - Strategic Game Changes',
              fontsize=14, fontweight='bold', pad=20)
ax1.legend(loc='upper left')

plt.tight_layout()
plt.savefig('charts/07_scoring_evolution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 8: Most Active Tournament Types - Market Segmentation
# ============================================================================
print("Generating Chart 8: Tournament Frequency Analysis...")
tournament_freq = results['tournament'].value_counts().head(15)

fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.barh(range(len(tournament_freq)), tournament_freq.values,
               color='#6A4C93', alpha=0.8, edgecolor='black')

ax.set_yticks(range(len(tournament_freq)))
ax.set_yticklabels(tournament_freq.index)
ax.set_xlabel('Number of Matches', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Most Frequent Tournaments - Market Segmentation Analysis',
             fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Add value labels
for bar, val in zip(bars, tournament_freq.values):
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height()/2,
            f' {val:,}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/08_tournament_frequency.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 9: Neutral Venue Impact - Event Hosting Strategy
# ============================================================================
print("Generating Chart 9: Neutral Venue Impact...")
neutral_comparison = results.groupby('neutral').agg({
    'total_goals': 'mean',
    'date': 'count'
}).round(2)
neutral_comparison.columns = ['Avg Goals', 'Total Matches']
neutral_comparison.index = ['Home/Away', 'Neutral Venue']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Match distribution
colors_venue = ['#2E86AB', '#E63946']
bars1 = ax1.bar(neutral_comparison.index, neutral_comparison['Total Matches'],
                color=colors_venue, alpha=0.8, edgecolor='black')
ax1.set_ylabel('Number of Matches', fontsize=11, fontweight='bold')
ax1.set_title('Match Distribution by Venue Type', fontsize=12, fontweight='bold')
ax1.grid(axis='y', alpha=0.3)

for bar, val in zip(bars1, neutral_comparison['Total Matches']):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:,}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Goal scoring comparison
bars2 = ax2.bar(neutral_comparison.index, neutral_comparison['Avg Goals'],
                color=colors_venue, alpha=0.8, edgecolor='black')
ax2.set_ylabel('Average Goals per Match', fontsize=11, fontweight='bold')
ax2.set_title('Scoring Patterns by Venue Type', fontsize=12, fontweight='bold')
ax2.grid(axis='y', alpha=0.3)

for bar, val in zip(bars2, neutral_comparison['Avg Goals']):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.suptitle('Neutral Venue Impact on Match Dynamics - Event Hosting Insights',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('charts/09_neutral_venue_impact.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 10: Penalty vs Open Play Goals - Scoring Method Analysis
# ============================================================================
print("Generating Chart 10: Goal Scoring Methods...")
goal_methods = pd.DataFrame({
    'Method': ['Open Play', 'Penalty Kick', 'Own Goal'],
    'Goals': [
        len(goalscorers[(goalscorers['penalty'] == False) & (goalscorers['own_goal'] == False)]),
        len(goalscorers[goalscorers['penalty'] == True]),
        len(goalscorers[goalscorers['own_goal'] == True])
    ]
})
goal_methods['Percentage'] = (goal_methods['Goals'] / goal_methods['Goals'].sum() * 100).round(1)

fig, ax = plt.subplots(figsize=(10, 6))
colors_methods = ['#06A77D', '#F77F00', '#E63946']
bars = ax.bar(goal_methods['Method'], goal_methods['Percentage'],
              color=colors_methods, alpha=0.8, edgecolor='black')

ax.set_ylabel('Percentage of All Goals (%)', fontsize=12, fontweight='bold')
ax.set_title('Goal Scoring Methods Distribution - How Teams Score',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add percentage and count labels
for bar, pct, count in zip(bars, goal_methods['Percentage'], goal_methods['Goals']):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{pct}%\n({count:,} goals)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

ax.set_ylim(0, max(goal_methods['Percentage']) * 1.2)

plt.tight_layout()
plt.savefig('charts/10_goal_scoring_methods.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 11: Top Goal Scorers - Star Player Impact
# ============================================================================
print("Generating Chart 11: Top Scorers Analysis...")
top_scorers = goalscorers[goalscorers['own_goal'] == False]['scorer'].value_counts().head(20)

fig, ax = plt.subplots(figsize=(12, 8))
bars = ax.barh(range(len(top_scorers)), top_scorers.values,
               color='#F77F00', alpha=0.8, edgecolor='black')

# Highlight top 3
for i in range(min(3, len(bars))):
    bars[i].set_color('#06A77D')
    bars[i].set_alpha(0.9)

ax.set_yticks(range(len(top_scorers)))
ax.set_yticklabels(top_scorers.index)
ax.set_xlabel('International Goals Scored', fontsize=12, fontweight='bold')
ax.set_title('Top 20 All-Time International Goal Scorers - Star Player Performance',
             fontsize=14, fontweight='bold', pad=20)
ax.invert_yaxis()
ax.grid(axis='x', alpha=0.3)

# Add value labels
for bar, val in zip(bars, top_scorers.values):
    width = bar.get_width()
    ax.text(width, bar.get_y() + bar.get_height()/2,
            f' {val}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/11_top_goal_scorers.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 12: Match Intensity Trends - Competitive Balance
# ============================================================================
print("Generating Chart 12: Match Intensity Analysis...")
results['goal_difference'] = abs(results['home_score'] - results['away_score'])
results['match_intensity'] = results['goal_difference'].apply(
    lambda x: 'Highly Competitive (0-1 goal diff)' if x <= 1 else
              'Moderate (2-3 goal diff)' if x <= 3 else
              'Decisive (4+ goal diff)'
)

intensity_dist = results['match_intensity'].value_counts()
intensity_order = ['Highly Competitive (0-1 goal diff)', 'Moderate (2-3 goal diff)', 'Decisive (4+ goal diff)']
intensity_dist = intensity_dist.reindex(intensity_order)

fig, ax = plt.subplots(figsize=(12, 6))
colors_intensity = ['#06A77D', '#F4D35E', '#E63946']
bars = ax.bar(range(len(intensity_dist)), intensity_dist.values,
              color=colors_intensity, alpha=0.8, edgecolor='black')

ax.set_xticks(range(len(intensity_dist)))
ax.set_xticklabels([label.replace(' (', '\n(') for label in intensity_dist.index])
ax.set_ylabel('Number of Matches', fontsize=12, fontweight='bold')
ax.set_title('Match Competitiveness Distribution - Competitive Balance Indicator',
             fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels and percentages
total = intensity_dist.sum()
for bar, val in zip(bars, intensity_dist.values):
    height = bar.get_height()
    pct = (val / total * 100)
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:,}\n({pct:.1f}%)',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/12_match_intensity_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "="*80)
print("CHART GENERATION COMPLETE!")
print("="*80)
print(f"\nAll 12 business insight charts have been saved to the 'charts/' directory")
print("\nCharts created:")
print("  1. Match Volume Trends - Market growth analysis")
print("  2. Home Advantage Value - Strategic venue insights")
print("  3. Tournament Performance - Competitive vs friendly analysis")
print("  4. Top Teams Win Rate - Market leaders identification")
print("  5. Goal Timing Patterns - Tactical scoring insights")
print("  6. Shootout Success Rates - High-pressure performance")
print("  7. Scoring Evolution - Game dynamics over time")
print("  8. Tournament Frequency - Market segmentation")
print("  9. Neutral Venue Impact - Event hosting strategy")
print(" 10. Goal Scoring Methods - Scoring approach analysis")
print(" 11. Top Goal Scorers - Star player impact")
print(" 12. Match Intensity Distribution - Competitive balance")
print("="*80)
