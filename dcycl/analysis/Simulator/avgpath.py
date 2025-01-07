import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from OneEuroFilter import OneEuroFilter

def calculate_traveled_distance(x, y):
    """
    Calculate the traveled distance based on X and Y positions, accounting for curvature.
    """
    distances = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
    return np.insert(np.cumsum(distances), 0, 0)

def calculate_lateral_deviation(car_x, car_y, cyclist_x, cyclist_y):
    """
    Calculate the lateral deviation between car and cyclist positions.
    """
    # Ensure both arrays have the same length by interpolating cyclist data
    cyclist_x_resampled = np.interp(np.linspace(0, len(cyclist_x)-1, len(car_x)), np.arange(len(cyclist_x)), cyclist_x)
    cyclist_y_resampled = np.interp(np.linspace(0, len(cyclist_y)-1, len(car_y)), np.arange(len(cyclist_y)), cyclist_y)

    return np.sqrt((car_x - cyclist_x_resampled)**2 + (car_y - cyclist_y_resampled)**2)

# Define the main folder path containing all scenario CSV files
main_folder = "Avrage_path"  # Replace with the path to your main folder
cyclist_file = "CyclistDistanceData_1.csv"  # Replace with the path to the cyclist data CSV

# Get all scenario files from the main folder
scenario_files = [os.path.join(main_folder, file) for file in os.listdir(main_folder) if file.endswith(".csv")]

# Load cyclist data
cyclist_data = pd.read_csv(cyclist_file)
cyclist_x = cyclist_data["cyclist_dataX"].values
cyclist_y = cyclist_data["cyclist_dataY"].values
cyclist_traveled_distance = calculate_traveled_distance(cyclist_x, cyclist_y)

# Placeholder for storing paths across scenarios
all_paths = []

# Initialize OneEuroFilter for smoothing
freq = 120.0  # Frequency of updates (adjust as needed)
x_filter = OneEuroFilter(freq=freq)
y_filter = OneEuroFilter(freq=freq)

# Process scenario data and prepare for plotting
for i, file_path in enumerate(scenario_files):
    # Load scenario data from CSV
    scenario_data = pd.read_csv(file_path)
    car_x = scenario_data["X"].values
    car_y = scenario_data["Y"].values

    # Calculate traveled distance for the car
    car_traveled_distance = calculate_traveled_distance(car_x, car_y)

    # Calculate lateral deviation between car and cyclist
    lateral_deviation = calculate_lateral_deviation(car_x, car_y, cyclist_x, cyclist_y)

    # Smooth the data using OneEuroFilter
    smoothed_distance = []
    smoothed_deviation = []
    for d, l in zip(car_traveled_distance, lateral_deviation):
        smoothed_distance.append(x_filter(d))
        smoothed_deviation.append(y_filter(l))

    all_paths.append((smoothed_distance, smoothed_deviation))

# Plot the OneEuroFilter smoothed curves for all scenarios
fig_filtered = go.Figure()
for i, (smoothed_distance, smoothed_deviation) in enumerate(all_paths):
    fig_filtered.add_trace(go.Scatter(
        x=smoothed_distance,
        y=smoothed_deviation,
        mode='lines',
        line=dict(width=3),
        name=f'Scenario {i+1} Smoothed Path'
    ))

fig_filtered.update_layout(
    title="Smoothed Overtaking Paths Across Scenarios",
    xaxis_title="Traveled Distance (m)",
    yaxis_title="Lateral Deviation (m)",
    legend_title="Legend",
    template="plotly_white"
)

# Save the plot for OneEuroFilter smoothed paths
filtered_html_path = "OneEuroFilter_Smoothed_Overtaking_Paths.html"
fig_filtered.write_html(filtered_html_path)
print(f"Smoothed paths plot saved: {filtered_html_path}")
