import os
import glob
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from OneEuroFilter import OneEuroFilter

# Define the folder paths for all scenarios
base_folder = 'path'  # Replace with the path to the base folder
scenario_folders = sorted([os.path.join(base_folder, folder) for folder in os.listdir(base_folder)])

# Placeholder for storing paths across scenarios
all_paths = []

# Initialize OneEuroFilter for smoothing
freq = 120.0  # Frequency of updates (adjust as needed)
x_filter = OneEuroFilter(freq=freq)
y_filter = OneEuroFilter(freq=freq)

# Function to filter outliers in Y-axis values
def filter_outliers(y_values, y_min=-0.06, y_max=-0.055):
    """
    Filters out Y values that are not within the specified range.
    """
    return np.array([y if y_min <= y <= y_max else np.nan for y in y_values])

# Function to filter out points before a valid X range
def filter_points_by_valid_path(avg_x, avg_y, start_x=-257):
    """
    Removes points before the specified start_x in the valid path
    and ensures both X and Y values are valid.
    """
    # Ensure X and Y are valid
    valid_indices = (avg_x >= start_x) & ~np.isnan(avg_y)
    return avg_x[valid_indices], avg_y[valid_indices]

# Function to sort and clean data points
def sort_and_clean(avg_x, avg_y):
    """
    Ensures X values are strictly increasing and sorts both X and Y accordingly.
    Removes points with missing X or Y values (NaN).
    """
    valid_indices = ~np.isnan(avg_x) & ~np.isnan(avg_y)
    avg_x = avg_x[valid_indices]
    avg_y = avg_y[valid_indices]

    sorted_indices = np.argsort(avg_x)
    avg_x = avg_x[sorted_indices]
    avg_y = avg_y[sorted_indices]

    # Remove duplicate X values
    unique_indices = np.unique(avg_x, return_index=True)[1]
    avg_x = avg_x[unique_indices]
    avg_y = avg_y[unique_indices]

    return avg_x, avg_y

# Process scenario data and save to CSV files
for i, scenario_path in enumerate(scenario_folders):
    csv_files = glob.glob(os.path.join(scenario_path, "*.csv"))
    
    # Combine data for the scenario
    scenario_data = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)
    scenario_data.columns = scenario_data.columns.str.strip()

    # Extract the path (average trajectory) for the scenario
    time_values = scenario_data["Time"].unique()
    avg_x = []
    avg_y = []
    for time in time_values:
        subset = scenario_data[scenario_data["Time"] == time]
        avg_x.append(subset["CarPositionX"].mean())
        avg_y.append(subset["CarPositionY"].mean())
    
    # Filter out points before the valid path starts
    avg_x, avg_y = filter_points_by_valid_path(np.array(avg_x), filter_outliers(np.array(avg_y)))

    # Sort and clean the data
    avg_x, avg_y = sort_and_clean(avg_x, avg_y)

    # Save X and Y values for the scenario to a CSV file
    scenario_output_path = f"Scenario_{i+1}_X_Y_Values.csv"
    pd.DataFrame({"X": avg_x, "Y": avg_y}).to_csv(scenario_output_path, index=False)
    print(f"Scenario {i+1} X and Y values saved to {scenario_output_path}")

    # Append to all_paths for plotting
    all_paths.append((avg_x, avg_y))

# Debugging: Print first few X and Y values for each scenario
for i, (avg_x, avg_y) in enumerate(all_paths):
    print(f"Scenario {i+1} filtered X values: {avg_x[:5]}")
    print(f"Scenario {i+1} filtered Y values: {avg_y[:5]}")

# Plot the OneEuroFilter smoothed curves for all scenarios
fig_filtered = go.Figure()
for i, (avg_x, avg_y) in enumerate(all_paths):
    # Apply OneEuroFilter to smooth the paths
    filtered_x = [x_filter(x) for x in avg_x]
    filtered_y = [y_filter(y) for y in avg_y]

    fig_filtered.add_trace(go.Scatter(
        x=filtered_x,
        y=filtered_y,
        mode='lines',
        line=dict(width=3),
        name=f'Scenario {i+1} Smoothed Path (OneEuroFilter)'
    ))

fig_filtered.update_layout(
    title="OneEuroFilter Smoothed Overtaking Paths Across Scenarios",
    xaxis_title="Car Position X (m)",
    yaxis_title="Car Position Y (m)",
    legend_title="Legend",
    template="plotly_white",
    xaxis=dict(range=[-257, -50]),
    yaxis=dict(range=[-0.0595, -0.056])
)

# Save the plot for OneEuroFilter smoothed paths
filtered_html_path = "OneEuroFilter_Smoothed_Overtaking_Paths.html"
fig_filtered.write_html(filtered_html_path)
print(f"OneEuroFilter smoothed paths plot saved: {filtered_html_path}")
