import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import pdb
plt.rcParams['svg.fonttype'] = 'none'
# Load and merge datasets
basepath = "sample_data"
scores_df = pd.read_csv(f'{basepath}/Nature_scores.csv')
subjects_df = pd.read_csv(f'{basepath}/Nature_subjects.csv')
df = pd.merge(scores_df, subjects_df, on='doi', how='inner')

# Apply 95% CI filter to FKGL scores
fkgl_025 = df['fk_idx'].quantile(0.025)
fkgl_975 = df['fk_idx'].quantile(0.975)
filtered_df = df[(df['fk_idx'] >= fkgl_025) & (df['fk_idx'] <= fkgl_975)].copy()


# Convert date and add period indicator
filtered_df['date'] = pd.to_datetime(filtered_df['date'])
filtered_df['period'] = np.where(filtered_df['date'] < '2022-11-22', 
                                'Before Nov 22, 2022', 
                                'After Nov 22, 2022')

# Calculate article counts by subject and period
subject_counts = filtered_df.groupby(['subject', 'period'])['doi'].count().unstack()


# Find subjects with at least 50 articles in each period
valid_subjects = subject_counts[
    (subject_counts['Before Nov 22, 2022'] >= 50) & 
    (subject_counts['After Nov 22, 2022'] >= 50)
].index

# Perform analysis for each valid subject
results = []
for subject in valid_subjects:
    subject_data = filtered_df[filtered_df['subject'] == subject]
    
    before = subject_data[subject_data['period'] == 'Before Nov 22, 2022']['fk_idx']
    after = subject_data[subject_data['period'] == 'After Nov 22, 2022']['fk_idx']
    
    t_stat, p_val = stats.ttest_ind(before, after, equal_var=False)
    
    results.append({
        'subject': subject,
        't_statistic': t_stat,
        'p_value': p_val,
        'before_mean': before.mean(),
        'after_mean': after.mean(),
        'before_count': len(before),
        'after_count': len(after)
    })

# Convert results to DataFrame
results_df = pd.DataFrame(results)
results_df['significant'] = results_df['p_value'] < 0.05

# Create the scatter plot
plt.figure(figsize=(12, 8))

# Plot the diagonal line y=x
min_val = min(results_df['before_mean'].min(), results_df['after_mean'].min())
max_val = max(results_df['before_mean'].max(), results_df['after_mean'].max())
plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='No change line')

# Create scatter plot
colors = ['red' if sig else 'gray' for sig in results_df['significant']]
plt.scatter(results_df['before_mean'], results_df['after_mean'], 
           c=colors, alpha=0.6, s=100)

# Add labels only for the most significant subjects (p < 0.01)
for idx, row in results_df[results_df['p_value'] < 0.05].iterrows():
    plt.annotate(row['subject'], 
                (row['before_mean'], row['after_mean']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=10, alpha=1.0)

# Customize the plot
plt.xlabel('Mean FKGL Score Before Nov 22, 2022', fontsize=12)
plt.ylabel('Mean FKGL Score After Nov 22, 2022', fontsize=12)
plt.title('Figure 3.1: Subject-Specific Changes in FKGL Scores\
Red points indicate significant changes (p < 0.05)\
Labels shown for most significant changes (p < 0.01)', 
          fontsize=14)

# Add grid
plt.grid(True, alpha=0.3)

# Make plot square with equal axes
plt.axis('equal')

plt.tight_layout()
plt.savefig("figures/figure3_raw.svg")
plt.savefig("figures/figure3_raw.png")

from scipy.stats import norm



fig, axes = plt.subplots(2, 3, figsize=(22, 12), sharex=True, sharey=True)
axes = axes.flatten()
for idx, subject in enumerate(results_df[results_df['significant']]["subject"][:6]):
    ax = axes[idx]
    for period, color, label in zip(['Before Nov 22, 2022', 'After Nov 22, 2022'], ['skyblue', 'salmon'], ['Before', 'After']):
        data = filtered_df[(filtered_df['subject'] == subject) & (filtered_df['period'] == period)]['fk_idx']

        
        mean = data.mean()
        var = data.var()
        n = len(data)
        # Plot normalized histogram
        ax.hist(data, bins=20, density=True, alpha=0.6, color=color, label=label + f' (n={n})')
        # Plot mean as a vertical line
        ax.axvline(mean, color=color, linestyle='--', linewidth=2)
        # Annotate mean and variance
        ax.text(mean, ax.get_ylim()[1]*0.8, f"μ={mean:.2f}\
σ²={var:.2f}", color=color, ha='center', fontweight='bold')
        # Gaussian fit
        # pdb.set_trace() 
        x = np.linspace(data.min(), data.max(), 200)
        pdf = norm.pdf(x, mean, np.sqrt(var))
        ax.plot(x, pdf, color=color, lw=2)
    ax.set_title(subject)
    ax.set_xlabel('FKGL Score')
    ax.set_ylabel('Density')
    ax.legend()
    ax.grid(True, alpha=0.3)

plt.suptitle('Distribution of FKGL Scores for Significant Subjects\
(Before vs After Nov 22, 2022, 95% CI Filtered, Gaussian Fit)', fontsize=18)
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("figures/figure4_raw.svg")
plt.savefig("figures/figure4_raw.png")