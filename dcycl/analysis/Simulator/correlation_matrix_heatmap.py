import numpy as np
import plotly.graph_objects as go
import pandas as pd

# Load your data from an Excel file
file_path = "matrix.xlsx"  # Replace with your file path
data = pd.read_excel(file_path)

# Calculate the correlation matrix for numeric columns
correlation_matrix = data.corr()

# Calculate absolute values of the correlation matrix
correlation_matrix_abs = correlation_matrix.abs()

# Create a mask for the upper triangle, including diagonal
mask_upper_white = np.triu(np.ones_like(correlation_matrix_abs, dtype=bool))

# Prepare text values for display
text_values = np.where(mask_upper_white, "", correlation_matrix_abs.round(2).astype(str))  # Display rounded correlation values

# Create the heatmap
fig = go.Figure(data=go.Heatmap(
    z=np.where(mask_upper_white, np.nan, correlation_matrix_abs.values),  # Apply mask with absolute values
    x=correlation_matrix_abs.columns,  # Use original X-axis order
    y=correlation_matrix_abs.columns[::-1],  # Reverse Y-axis for proper alignment
    colorscale='RdBu_r',  # Reverse the RdBu color scale
    colorbar=dict(title="Correlation (0 to 1)"),
    zmin=0,
    zmax=1,
    text=text_values,  # Add the correlation values as text
    texttemplate="%{text}",  # Format text to show in cells
    textfont=dict(color="white"),  # Set the text color to white
    hoverongaps=False,
    showscale=True
))

# Update layout for Times New Roman font and proper axes alignment
fig.update_layout(
    title="Correlation Matrix Heatmap with Values",
    xaxis=dict(title="Variables", tickangle=-45),
    yaxis=dict(title="Variables"),
    font=dict(size=12, family="Times New Roman"),  # Times New Roman font
    width=1600,
    height=1080,
    template="plotly_white"  # Use white background template
)

# Save the figure as PNG and HTML
fig.write_image("correlation_matrix_heatmap_with_values.png")
fig.write_html("correlation_matrix_heatmap_with_values.html")
