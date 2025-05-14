# This script generates Figure 1: Histogram of FKGL scores with Gaussian fit, 95% CI filtering, and summary statistics
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

# Load the FKGL scores data
scores_df = pd.read_csv('sample_data/Nature_scores.csv')

# Calculate 95% confidence interval bounds for FKGL
fkgl_025 = scores_df['fk_idx'].quantile(0.025)
fkgl_975 = scores_df['fk_idx'].quantile(0.975)

# Filter out FKGL outliers
filtered_df = scores_df[(scores_df['fk_idx'] >= fkgl_025) & (scores_df['fk_idx'] <= fkgl_975)].copy()

# Split data into before and after Nov 22, 2022
filtered_df['date'] = pd.to_datetime(filtered_df['date'])
before = filtered_df[filtered_df['date'] < '2022-11-22']['fk_idx']
after = filtered_df[filtered_df['date'] >= '2022-11-22']['fk_idx']

# Compute summary statistics
mean_before = before.mean()
var_before = before.var()
n_before = before.count()
mean_after = after.mean()
var_after = after.var()
n_after = after.count()

# Plot histogram with Gaussian fit for both periods
plt.figure(figsize=(10, 6))

# Histogram and Gaussian fit for 'before'
sns.histplot(before, bins=30, color='skyblue', stat='density', label='Before Nov 22, 2022', alpha=0.6)
x_before = np.linspace(before.min(), before.max(), 200)
plt.plot(x_before, norm.pdf(x_before, mean_before, np.sqrt(var_before)), color='blue', lw=2)
plt.axvline(mean_before, color='blue', linestyle='--', label='Mean Before')

# Histogram and Gaussian fit for 'after'
sns.histplot(after, bins=30, color='salmon', stat='density', label='After Nov 22, 2022', alpha=0.6)
x_after = np.linspace(after.min(), after.max(), 200)
plt.plot(x_after, norm.pdf(x_after, mean_after, np.sqrt(var_after)), color='red', lw=2)
plt.axvline(mean_after, color='red', linestyle='--', label='Mean After')

plt.xlabel('FKGL Score')
plt.ylabel('Density')
plt.title('Figure 1: Distribution of FKGL Scores Before and After Nov 22, 2022\
(95% CI Filtered, Gaussian Fit)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("figures/figure1.svg")
plt.savefig("figures/figure1.png")

# Print summary statistics
table = pd.DataFrame({
    'Period': ['Before Nov 22, 2022', 'After Nov 22, 2022'],
    'Mean FKGL': [mean_before, mean_after],
    'Variance': [var_before, var_after],
    'Sample Size': [n_before, n_after]
})

print('Summary statistics for Figure 1:')
print(table.round(3))

# Script to generate Figure 1: Histogram of FKGL scores with Gaussian fit, 95% CI filtering, and summary statistics

# scores_df = pd.read_csv('Nature_scores.csv')
# fkgl_025 = scores_df['fk_idx'].quantile(0.025)
# fkgl_975 = scores_df['fk_idx'].quantile(0.975)
# filtered_df = scores_df[(scores_df['fk_idx'] >= fkgl_025) & (scores_df['fk_idx'] <= fkgl_975)].copy()
# filtered_df['date'] = pd.to_datetime(filtered_df['date'])
# before = filtered_df[filtered_df['date'] < '2022-11-22']['fk_idx']
# after = filtered_df[filtered_df['date'] >= '2022-11-22']['fk_idx']
# mean_before = before.mean()
# var_before = before.var()
# n_before = before.count()
# mean_after = after.mean()
# var_after = after.var()
# n_after = after.count()
# plt.figure(figsize=(10, 6))
# sns.histplot(before, bins=30, color='skyblue', stat='density', label='Before Nov 22, 2022', alpha=0.6)
# x_before = np.linspace(before.min(), before.max(), 200)
# plt.plot(x_before, norm.pdf(x_before, mean_before, np.sqrt(var_before)), color='blue', lw=2)
# plt.axvline(mean_before, color='blue', linestyle='--', label='Mean Before')
# sns.histplot(after, bins=30, color='salmon', stat='density', label='After Nov 22, 2022', alpha=0.6)
# x_after = np.linspace(after.min(), after.max(), 200)
# plt.plot(x_after, norm.pdf(x_after, mean_after, np.sqrt(var_after)), color='red', lw=2)
# plt.axvline(mean_after, color='red', linestyle='--', label='Mean After')
# plt.xlabel('FKGL Score')
# plt.ylabel('Density')
# plt.title('Figure 1: Distribution of FKGL Scores Before and After Nov 22, 2022\
# (95% CI Filtered, Gaussian Fit)')
# plt.legend()
# plt.grid(True, alpha=0.3)
# plt.tight_layout()
# plt.savefig("figures/figure1.svg")
# table = pd.DataFrame({
#     'Period': ['Before Nov 22, 2022', 'After Nov 22, 2022'],
#     'Mean FKGL': [mean_before, mean_after],
#     'Variance': [var_before, var_after],
#     'Sample Size': [n_before, n_after]
# })
# print('Summary statistics for Figure 1:')
# print(table.round(3))

