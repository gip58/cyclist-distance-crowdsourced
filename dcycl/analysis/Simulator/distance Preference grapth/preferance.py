import pandas as pd
import plotly.graph_objects as go

# Load the data
preferences_df = pd.read_excel("Preferences_and_avrage.xlsx")
distance_df = pd.read_excel("simulator_distace.xlsx")

# Calculate the average distance for each scenario from the distance dataset
average_distances = distance_df.drop(columns=["Participant"]).mean()

# Prepare the data for the bar chart (preferences)
scenarios = preferences_df["Scenarios"]
preferences = preferences_df["Preference"]

# Define colors for each scenario
bar_colors = [
    '#6384FF',  # Laser Projection (blue)
    '#FF6244',  # Vertical Signage (red)
    '#45D4C0',  # Road Markings (teal)
    '#A17EFF',  # Car Projection System (purple)
    '#FFA842',  # Centre Line and Side-Line Markings (orange)
    '#54DFFF',  # Unprotected Cycle Path (cyan)
    '#FF71A8'   # No Road Markings (pink)
]

# Create the figure
fig = go.Figure()


def adjust_shade(color, factor=0.9):
    # Convert hex to RGB
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    # Adjust the brightness factor
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    # Convert back to hex
    return f'#{r:02X}{g:02X}{b:02X}'


# Add bar chart for preferences with slightly adjusted border colors
for scenario, preference, color in zip(scenarios, preferences, bar_colors):
    border_color = adjust_shade(color, factor=0.95)  # Subtly adjust shade
    fig.add_trace(go.Bar(
        x=[scenario],
        y=[preference],
        name=f"{scenario}",
        marker=dict(
            color=color,
            line=dict(color=border_color, width=2)  # Slightly different shade for border
        ),
        legendgroup=scenario,  # Group legend items by scenario
        showlegend=True  # Ensure legend items are displayed 
    ))
# Update the width of all bar traces
fig.update_traces(width=0.5, selector=dict(type='bar'))    

# Add line chart for average distances
fig.add_trace(go.Scatter(
    x=scenarios,
    y=average_distances,
    name="Average Distance (m)",
    mode='lines+markers',
    line=dict(color="black", width=2),
    legendgroup="Average Distance",  # Group legend for consistency
    showlegend=True
))

# Update layout with font settings
fig.update_layout(
    title=dict(
        text="Preferences and Average Distances Across Scenarios Simulator Results",
        font=dict(
            family="Times New Roman",
            size=16
        ),
        x=0.5  # Center the title
    ),
    xaxis=dict(
        title=dict(
            text="Scenario",
            font=dict(
                family="Times New Roman",
                size=14
            )
        ),
        tickfont=dict(
            family="Times New Roman",
            size=12
        )
    ),
    yaxis=dict(
        title=dict(
            text="Value",
            font=dict(
                family="Times New Roman",
                size=14
            )
        ),
        tickfont=dict(
            family="Times New Roman",
            size=12
        )
    ),
    legend=dict(
        title=dict(
            text="Legend",
            font=dict(
                family="Times New Roman",
                size=14
            )
        ),
        font=dict(
            family="Times New Roman",
            size=12
        ),
        orientation="v",  # Vertical alignment of legend items
        x=1.05,  # Positioning on the right side
        y=1,     # Align top
        xanchor="left",
        yanchor="top",
        tracegroupgap=5,  # Adjust gap between groups in the legend
        itemwidth=50      # Adjust spacing between legend items
    ),
    template="plotly_white",
    width=1600,  # Set figure width for PNG
    height=1080   # Set figure height for PNG
)

# Save the figure as PNG and HTML
fig.write_image("preferences_distances.png")
fig.write_html("preferences_distances.html")
