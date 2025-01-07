import os
import glob
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def generate_sinusoidal_fit(x_values, amplitude=0.001, frequency=0.05, phase=0, offset=-0.058):
    """
    Generates a sinusoidal curve as a best fit for the given x_values.
    """
    return amplitude * np.sin(frequency * x_values + phase) + offset

# Define the folder paths for all scenarios
base_folder = 'path'  # Replace with the path to the base folder
scenario_folders = sorted([os.path.join(base_folder, folder) for folder in os.listdir(base_folder)])

# Placeholder for storing paths across scenarios
all_paths = []

# Iterate through each scenario folder to create individual plots
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
    all_paths.append((np.array(avg_x), np.array(avg_y)))

# Plot the sinusoidal fit for all scenarios
fig_sinusoidal = go.Figure()
for i, (avg_x, avg_y) in enumerate(all_paths):
    # Remove duplicates and sort by X values
    unique_indices = np.unique(avg_x, return_index=True)[1]
    avg_x = avg_x[unique_indices]
    avg_y = avg_y[unique_indices]

    # Generate sinusoidal fit for the scenario
    x_smooth = np.linspace(min(avg_x), max(avg_x), 1000)
    y_sinusoidal = generate_sinusoidal_fit(x_smooth)

    fig_sinusoidal.add_trace(go.Scatter(
        x=x_smooth,
        y=y_sinusoidal,
        mode='lines',
        line=dict(width=3),
        name=f'Scenario {i+1} Sinusoidal Fit'
    ))

fig_sinusoidal.update_layout(
    title="Sinusoidal Fit for Overtaking Paths Across Scenarios",
    xaxis_title="Car Position X (m)",
    yaxis_title="Car Position Y (m)",
    legend_title="Legend",
    template="plotly_white",
    xaxis=dict(range=[-250, -50]),
    yaxis=dict(range=[-0.0595, -0.056])
)

# Save the plot for sinusoidal fits
sinusoidal_html_path = "Sinusoidal_Fit_Overtaking_Paths.html"
fig_sinusoidal.write_html(sinusoidal_html_path)
print(f"Sinusoidal fit paths plot saved: {sinusoidal_html_path}")
