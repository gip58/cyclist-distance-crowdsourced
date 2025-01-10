import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from OneEuroFilter import OneEuroFilter

from scipy.interpolate import interp1d

def calculate_traveled_distance(x, y):
    """
    Calculate the cumulative traveled distance along a path given X and Y coordinates.
    """
    # Calculate the differences between consecutive points
    dx = np.diff(x)
    dy = np.diff(y)
    # Calculate the distance for each segment and sum it up
    distances = np.sqrt(dx**2 + dy**2)
    traveled_distance = np.cumsum(distances)
    # Add a starting point of zero
    return np.insert(traveled_distance, 0, 0)

def calculate_lateral_deviation(car_y, cyclist_y):
    """
    Calculate the lateral deviation as the absolute Y difference between the car and cyclist.
    """
    return np.abs(car_y - cyclist_y)

def align_cyclist_to_car(car_x, car_y, cyclist_x, cyclist_y):
    """
    Interpolate cyclist data to align its length with car data.
    """
    # Create interpolation functions for cyclist Y based on cyclist X
    interp_func_y = interp1d(cyclist_x, cyclist_y, kind='linear', fill_value="extrapolate")

    # Interpolate cyclist Y to match car X positions
    aligned_cyclist_y = interp_func_y(car_x)

    return aligned_cyclist_y

# Define the main folder path containing all scenario CSV files
main_folder = "Avrage_path"  # Replace with the path to your main folder
cyclist_file = "CyclistDistanceData_1.csv"  # Replace with the path to the cyclist data CSV

# Get all scenario files from the main folder
scenario_files = [os.path.join(main_folder, file) for file in os.listdir(main_folder) if file.endswith(".csv")]

# Load cyclist data
cyclist_data = pd.read_csv(cyclist_file)
cyclist_x = cyclist_data["cyclist_dataX"].values
cyclist_y = cyclist_data["cyclist_dataY"].values

# Flip cyclist X-axis and Y-axis
cyclist_x = -cyclist_x
cyclist_y = -cyclist_y

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

    # Flip car X-axis and Y-axis
    car_x = -car_x
    car_y = -car_y

    # Align cyclist data to match car data
    aligned_cyclist_y = align_cyclist_to_car(car_x, car_y, cyclist_x, cyclist_y)

    # Calculate traveled distance for the car
    car_traveled_distance = calculate_traveled_distance(car_x, car_y)

    # Calculate lateral deviation (absolute difference in Y)
    lateral_deviation = calculate_lateral_deviation(car_y, aligned_cyclist_y)

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
        name=f'Scenario {i+1} Smoothed Deviation'
    ))

fig_filtered.update_layout(
    title="Lateral Deviation from Cyclist During Overtaking",
    xaxis_title="Traveled Distance (m)",
    yaxis_title="Lateral Deviation (m)",
    legend_title="Legend",
    template="plotly_white"
)

# Save the plot for OneEuroFilter smoothed paths
filtered_html_path = "OneEuroFilter_Smoothed_Lateral_Deviation.html"
fig_filtered.write_html(filtered_html_path)
print(f"Smoothed lateral deviation plot saved: {filtered_html_path}")
