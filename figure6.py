# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
import pdb 
plt.rcParams['svg.fonttype'] = 'none'

# Load the data
disciplines_df = pd.read_csv('sample_data/parsed_disciplines.csv')
scores_df = pd.read_csv('sample_data/Nature_scores.csv')
subjects_df = pd.read_csv('sample_data/Nature_subjects.csv')

# Merge scores with subjects
df = pd.merge(scores_df, subjects_df, on='doi', how='inner')

# Apply 95% CI filter on FKGL scores
fkgl_025 = df['fk_idx'].quantile(0.025)
fkgl_975 = df['fk_idx'].quantile(0.975)
filtered_df = df[(df['fk_idx'] >= fkgl_025) & (df['fk_idx'] <= fkgl_975)].copy()

# Add period column
filtered_df['date'] = pd.to_datetime(filtered_df['date'])
filtered_df['period'] = np.where(filtered_df['date'] < '2022-11-22', 'Before', 'After')

# Remove rows with missing subjects
filtered_df = filtered_df.dropna(subset=['subject'])

# Now that filtered_df is ready, calculate variance by subject for before and after periods
# and create the scatterplot as requested

# Calculate variance and count for each subject in each period
var_stats = filtered_df.groupby(['subject', 'period'])['fk_idx'].agg(['var', 'count']).reset_index()

# Pivot the data to get before and after variances in separate columns
var_pivot = var_stats.pivot(index='subject', columns='period', values=['var', 'count'])
var_pivot.columns = ['var_before', 'var_after', 'count_before', 'count_after']
var_pivot = var_pivot.reset_index()

# Calculate total frequency for each subject
var_pivot['total_count'] = var_pivot['count_before'].fillna(0) + var_pivot['count_after'].fillna(0)

# Filter to only keep subjects with at least 50 articles in total
min_articles = 50
filtered_subjects = var_pivot[var_pivot['total_count'] >= min_articles].copy()

# Get the new top 10 most frequent subjects
top_10_subjects = filtered_subjects.nlargest(10, 'total_count')

# Recalculate mean variance for filtered subjects
out = filtered_df.groupby(["period"])["fk_idx"].agg(["var"])
mean_var_before = float(out[out.index == "Before"]["var"])
mean_var_after = float(out[out.index == "After"]["var"])

# Show the filtered table and new means
print(top_10_subjects[['subject', 'var_before', 'var_after', 'total_count']])
print('Mean variance before:', mean_var_before)
print('Mean variance after:', mean_var_after)

# Create scatter plot with filtered subjects
plt.figure(figsize=(12, 8))

# Plot filtered points in gray
plt.scatter(filtered_subjects['var_before'], filtered_subjects['var_after'], 
           alpha=0.5, color='gray', label='Subjects (≥50 articles)')

# Plot top 10 subjects in red with labels
plt.scatter(top_10_subjects['var_before'], top_10_subjects['var_after'], 
           color='red', alpha=0.7, label='Top 10 most frequent subjects')

# Add labels for top 10 subjects
for _, row in top_10_subjects.iterrows():
    plt.annotate(row['subject'], 
                (row['var_before'], row['var_after']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=8)

# Plot mean variance point
plt.scatter(mean_var_before, mean_var_after, color='blue', s=100, 
           label='Mean variance', zorder=5)

# Add diagonal line
max_var = max(filtered_subjects['var_before'].max(), filtered_subjects['var_after'].max())
plt.plot([0, max_var], [0, max_var], '--', color='gray', alpha=0.5)

plt.xlabel('Variance Before Nov 22, 2022')
plt.ylabel('Variance After Nov 22, 2022')
plt.title('FKGL Score Variance by Subject: Before vs After Nov 22, 2022\
(Subjects with ≥50 articles)')
plt.legend()

# Make axes equal
plt.axis('equal')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("figures/figure6_raw.svg")
plt.savefig("figures/figure6_raw.png")
