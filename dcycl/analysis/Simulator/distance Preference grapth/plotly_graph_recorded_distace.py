import pandas as pd
import plotly.graph_objects as go

# Load data from Excel
file_path = 'simulator_distace.xlsx'  # Replace with your file path
df = pd.read_excel(file_path)

df.set_index('Participant', inplace=True)

# Use columns (scenarios) directly for plotting
scenarios = df.columns  # Get the scenario names
distances = df  # Distances are now organized by columns

# Create the figure
fig = go.Figure()

# Add box plots and compute mean values
mean_values = []
for scenario in scenarios:
    values = distances[scenario].dropna()  # Ensure no missing data
    mean = values.mean()
    mean_values.append(mean)
    fig.add_trace(go.Box(
        y=values,
        name=scenario,
        boxmean=True  # Include mean line and marker
    ))

# Add mean values as annotations
for i, mean in enumerate(mean_values):
    fig.add_trace(go.Scatter(
        x=[scenarios[i]],  # Place the mean value on the corresponding scenario
        y=[mean],  # Mean value
        mode='text',
        text=f"{mean:.2f}",  # Format mean value to two decimal places
        textposition="top center",
        showlegend=False  # Avoid adding to the legend
    ))

# Add legend entries for median and mean
fig.add_trace(go.Scatter(
    x=[None], y=[None],  # Invisible trace for legend
    mode='lines',  # Lines only for the median
    line=dict(dash='dot', color='black'),
    name='Median'
))

fig.add_trace(go.Scatter(
    x=[None], y=[None],  # Invisible trace for legend
    mode='lines',  # Line with marker for mean
    line=dict(color='black'),
    name='Mean (m)'
))

# Update layout with font settings
fig.update_layout(
    title=dict(
        text="Comparison of Distances Across Scenarios (Mean Displayed)",
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
            text="Distance",
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
    height=1080  
     # Set figure height for PNG
)
# Save the figure as PNG and HTML
fig.write_image("plotly_graph_recorded_distace.png")
fig.write_html("plotly_graph_recorded_distace.html")

