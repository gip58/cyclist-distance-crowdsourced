import numpy as np
import statsmodels.stats.power as smp

# Set the parameters
effect_size = 0.3  # The effect size you expect (Cohen's d)
alpha = 0.05  # Significance level
power = 0.8  # Desired power level
n_conditions = 21  # Number of conditions (scenarios)

# Adjust for repeated measures - assuming a moderate correlation between repeated measures (intra-group correlation)
corr = 0.5  # This is a rough estimate, but it can vary depending on the context of your study
adjusted_effect_size = effect_size * np.sqrt(1 - corr)

# Initialize power analysis for F-test (ANOVA-like)
power_analysis = smp.FTestAnovaPower()

# Calculate the required sample size
sample_size = power_analysis.solve_power(effect_size=adjusted_effect_size, power=power, alpha=alpha,
                                         k_groups=n_conditions)

print(f"Required sample size for repeated measures: {np.ceil(sample_size)} participants")
