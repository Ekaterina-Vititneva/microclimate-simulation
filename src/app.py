import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import xarray as xr
import pandas as pd
import numpy as np  # <- Already imported for NumPy
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import plotly.express as px  # <- Add this import for Plotly Express
from kpi_config import kpi_options

# Paths to the datasets
statusquo_file_path = '../data/statusquo/Playground_2024-07-06_04.00.00_light.nc'
optimized_file_path = '../data/opti/Playground_2024-07-06_04.00.00_light.nc'

# Load the datasets
ds_statusquo = xr.open_dataset(statusquo_file_path)
ds_optimized = xr.open_dataset(optimized_file_path)

# Get the range of GridsK (vertical levels) for WindSpd
vertical_levels = list(ds_statusquo['GridsK'].values)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Microclimate Simulation Dashboard"),
    
    # Dropdown for selecting KPI
    html.Label("Select a KPI to compare:"),
    dcc.Dropdown(
        id='kpi-dropdown',
        options=[{'label': kpi, 'value': kpi} for kpi in kpi_options],
        value=kpi_options[0],  # Default value
        clearable=False
    ),
    
    # Dropdown for selecting vertical level (for 3D KPIs like WindSpd)
    html.Label("Select Vertical Level (GridsK) for WindSpd:"),
    dcc.Dropdown(
        id='vertical-level-dropdown',
        options=[{'label': f'Level {int(level)}', 'value': level} for level in vertical_levels],
        value=vertical_levels[0],  # Default level
        clearable=False,
        style={'display': 'none'}  # Initially hidden, only shown when WindSpd is selected
    ),
    
    # Graph to show the comparison (make sure this is dcc.Graph, not html.Img)
    dcc.Graph(id='kpi-graph')  # Here is the dcc.Graph component
])


@app.callback(
    Output('vertical-level-dropdown', 'style'),
    Input('kpi-dropdown', 'value')
)
def show_hide_vertical_level_dropdown(kpi):
    # Show the vertical level dropdown only if 'WindSpd' is selected
    if kpi == 'WindSpd':
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('kpi-graph', 'figure'),
    [Input('kpi-dropdown', 'value'),
     Input('vertical-level-dropdown', 'value')]
)
def update_graph(selected_kpi, selected_level):
    if selected_kpi == 'WindSpd':
        # Convert selected_level to an integer
        selected_level = int(selected_level)
        
        # If WindSpd is selected, show the data for the selected vertical level
        statusquo_data = ds_statusquo[selected_kpi].isel(Time=0, GridsK=selected_level).values
        optimized_data = ds_optimized[selected_kpi].isel(Time=0, GridsK=selected_level).values
    else:
        # For other KPIs, there is no vertical dimension, just show the 2D data
        statusquo_data = ds_statusquo[selected_kpi].isel(Time=0).values
        optimized_data = ds_optimized[selected_kpi].isel(Time=0).values
    
    # Flatten the data arrays for both Status Quo and Optimized scenarios
    statusquo_data_flat = statusquo_data.flatten()
    optimized_data_flat = optimized_data.flatten()

    # Generate grid points for X and Y dimensions
    grid_x, grid_y = statusquo_data.shape[-2], statusquo_data.shape[-1]
    grid_x_vals = np.tile(np.arange(grid_x), grid_y)
    grid_y_vals = np.repeat(np.arange(grid_y), grid_x)

    # Ensure the lengths match
    assert len(statusquo_data_flat) == len(optimized_data_flat) == len(grid_x_vals) == len(grid_y_vals)

    # Create a DataFrame for plotting
    data = pd.DataFrame({
        'Status Quo': statusquo_data_flat,
        'Optimized': optimized_data_flat,
        'Grid X': grid_x_vals,
        'Grid Y': grid_y_vals
    })

    # Create a figure using Plotly
    # Create a figure using Plotly
    fig = px.scatter(data, x='Grid X', y='Grid Y', color='Status Quo',
                 title=f"Comparison of {selected_kpi} between Status Quo and Optimized",
                 color_continuous_scale='RdBu',  # Replace 'coolwarm' with a valid colorscale
                 height=700, width=700)


    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
