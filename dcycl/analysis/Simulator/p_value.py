import pandas as pd
from scipy.stats import f_oneway

# Load the dataset
file_path = 'Distance result.xlsx'
data = pd.ExcelFile(file_path)
sheet_data = data.parse('Sheet1')

# Extract relevant columns and clean the data
scenarios = ['Scenario 1', 'Scenario 2', 'Scenario 3', 'Scenario 4', 'Scenario 5', 'Scenario 6', 'Scenario 7']
distances = {}

for i, scenario in enumerate(scenarios, start=1):
    col_name = f'Unnamed: {2 + (i - 1) * 6}'
    distances[scenario] = pd.to_numeric(sheet_data[col_name], errors='coerce')

# Create a clean data structure for ANOVA
distance_data = pd.DataFrame(distances).dropna()
scenario_distances = [distance_data[scenario].dropna() for scenario in scenarios]

# Perform ANOVA
anova_result = f_oneway(*scenario_distances)
p_value = anova_result.pvalue

print(f"The calculated p-value is: {p_value}")
