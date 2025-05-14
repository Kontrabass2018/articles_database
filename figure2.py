# Remove November 2022, sort data, and plot with .25 and .75 percentile lines
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.rcParams['svg.fonttype'] = 'none'
# Load and filter data
scores_df = pd.read_csv('sample_data/Nature_scores.csv')
fkgl_025 = scores_df['fk_idx'].quantile(0.025)
fkgl_975 = scores_df['fk_idx'].quantile(0.975)
filtered_df = scores_df[(scores_df['fk_idx'] >= fkgl_025) & (scores_df['fk_idx'] <= fkgl_975)].copy()
filtered_df['date'] = pd.to_datetime(filtered_df['date'])
filtered_df['year_month'] = filtered_df['date'].dt.to_period('M')
filtered_df['period'] = np.where(filtered_df['date'] < '2022-11-22', 'Before Nov 22, 2022', 'After Nov 22, 2022')

# Remove November 2022 and sort by year_month
filtered_df = filtered_df[filtered_df['year_month'] != pd.Period('2022-11')]
filtered_df = filtered_df.sort_values('year_month')

# Calculate .25 and .75 percentiles for all filtered data
fkgl_25 = filtered_df['fk_idx'].quantile(0.25)
fkgl_75 = filtered_df['fk_idx'].quantile(0.75)

# Plot boxplots by month, colored by period, with percentile lines
plt.figure(figsize=(16, 4))
sns.boxplot(data=filtered_df, 
            x='year_month', 
            y='fk_idx',
            order=sorted(filtered_df['year_month'].unique()),
            showfliers=True,
            fliersize=2,
            hue='period',
            palette={'Before Nov 22, 2022': 'blue', 'After Nov 22, 2022': 'red'},
            medianprops={'color': 'black'},
            boxprops={'alpha': 0.7})

plt.axhline(y=fkgl_25, color='green', linestyle=':', label='25th percentile')
plt.axhline(y=fkgl_75, color='purple', linestyle=':', label='75th percentile')

plt.xticks(rotation=90)
plt.xlabel('Month')
plt.ylabel('FKGL Score')
plt.title('Monthly Distribution of FKGL Scores (95% CI Filtered, .25/.75 Percentiles)')
plt.grid(axis='y', alpha=0.3)
plt.legend(title='Period & Percentiles')
plt.tight_layout()
plt.savefig("figures/figure2.png")
plt.savefig("figures/figure2.svg")

# Show summary statistics for the percentiles
print('25th percentile:', round(fkgl_25, 2))
print('75th percentile:', round(fkgl_75, 2))