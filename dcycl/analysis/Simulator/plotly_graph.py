import pandas as pd
import plotly.graph_objects as go

# Load the dataset
file_path = 'Distance result.xlsx'  # Replace with the path to your Excel file
data = pd.ExcelFile(file_path)
sheet_data = data.parse('Sheet1')

# Extract relevant columns and clean the data
scenarios = ['Laser Projection', 'Vertical Signage', 'Road Markings', 'Car Projection System', 'Centre Line and Side-Line Markings', 'Unprotected Cycle Path', 'No Road Markings']
distances = {}

for i, scenario in enumerate(scenarios, start=1):
    col_name = f'Unnamed: {2 + (i - 1) * 6}'  # Adjust based on the pattern in your data
    distances[scenario] = pd.to_numeric(sheet_data[col_name], errors='coerce')

# Combine data into a DataFrame for easy plotting
distance_data = pd.DataFrame(distances).dropna()

# Create a box plot for comparison
fig = go.Figure()

for scenario in scenarios:
    fig.add_trace(go.Box(y=distance_data[scenario], name=scenario))

# Update the layout for better readability
fig.update_layout(
    title="Comparison of Simulator Distances Across Scenarios",
    xaxis_title="Scenario",
    yaxis_title="Distance",
    boxmode="group",
    template="plotly_white"
)

# Show the plot
fig.show()
