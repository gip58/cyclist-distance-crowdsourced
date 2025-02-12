import os
import zipfile
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import ttest_rel

# -----------------------------
# Load and Process Data
# -----------------------------
# Define folder path where the scenario data is stored
scenario_folder_path = "D:\OneDrive - TU Eindhoven\Master\M1.2\cyclist-distance-crowdsourced\dcycl\analysis\Simulator\path"  # <- Update this path!

# Identify scenario folders
scenario_files = os.listdir(scenario_folder_path)

# Load all scenarios into a single DataFrame
all_data = []
for scenario in scenario_files:
    scenario_path = os.path.join(scenario_folder_path, scenario)
    csv_files = [f for f in os.listdir(scenario_path) if f.endswith(".csv")]
    
    for csv_file in csv_files:
        file_path = os.path.join(scenario_path, csv_file)
        df_scenario = pd.read_csv(file_path)
        df_scenario["Scenario"] = scenario  # Add scenario label
        all_data.append(df_scenario)

df_combined = pd.concat(all_data, ignore_index=True)

# Clean column names
df_combined.columns = df_combined.columns.str.strip()

# -----------------------------
# Preprocessing
# -----------------------------
# Remove the first 4 seconds (due to countdown)
df_filtered = df_combined[df_combined["Time"] >= 4]

# Bin time into 0.5s intervals
time_bins_filtered = np.arange(4, df_filtered["Time"].max(), 0.5)
df_filtered["TimeBin"] = pd.cut(df_filtered["Time"], bins=time_bins_filtered, labels=time_bins_filtered[:-1])

# Compute the average overtaking distance for each time bin within each scenario
df_binned_filtered = df_filtered.groupby(["TimeBin", "Scenario"])["Distance"].mean().reset_index()
df_binned_filtered["TimeBin"] = df_binned_filtered["TimeBin"].astype(float)  # Convert to numeric

# -----------------------------
# Create Line Plot (Overtaking Distance Over Time)
# -----------------------------
fig_line = px.line(
    df_binned_filtered, 
    x="TimeBin", 
    y="Distance", 
    color="Scenario", 
    title="Average Overtaking Distance Over Time for Different Scenarios",
    labels={"TimeBin": "Time (s)", "Distance": "Average Overtaking Distance (m)", "Scenario": "Scenario"}
)

fig_line.show()

# -----------------------------
# Perform T-Test (Scenario 5 as Control)
# -----------------------------
control_scenario = "Scenario_5"
p_values_matrix = []
time_bins_unique = df_binned_filtered["TimeBin"].unique()
scenarios = [s for s in df_binned_filtered["Scenario"].unique() if s != control_scenario]

for time_bin in time_bins_unique:
    p_values_row = []  

    control_data = df_filtered[(df_filtered["TimeBin"] == time_bin) & (df_filtered["Scenario"] == control_scenario)]["Distance"]

    if control_data.empty:
        p_values_matrix.append([np.nan] * len(scenarios))
        continue

    for scenario in scenarios:
        scenario_data = df_filtered[(df_filtered["TimeBin"] == time_bin) & (df_filtered["Scenario"] == scenario)]["Distance"]

        if scenario_data.empty:
            p_values_row.append(np.nan)
        else:
            t_stat, p_value = ttest_rel(control_data, scenario_data, alternative="two-sided")
            p_values_row.append(p_value)

    p_values_matrix.append(p_values_row)

p_values_array = np.array(p_values_matrix).T

# -----------------------------
# Create Heatmap (T-Test p-values)
# -----------------------------
fig_heatmap = go.Figure(data=go.Heatmap(
    z=p_values_array,
    x=time_bins_unique,
    y=scenarios,
    colorscale="coolwarm",
    colorbar=dict(title="p-value"),
    zmin=0,
    zmax=1
))

fig_heatmap.update_layout(
    title="T-Test p-values Over Time (Comparing Scenarios to Control)",
    xaxis_title="Time Bins (s)",
    yaxis_title="Scenarios (excluding control)"
)

fig_heatmap.show()
