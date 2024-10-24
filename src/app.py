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
import plotly.graph_objects as go
from kpi_config import kpi_options

# Paths to the datasets
statusquo_file_path = '../data/statusquo/Playground_2024-07-06_04.00.00_light.nc'
optimized_file_path = '../data/opti/Playground_2024-07-06_04.00.00_light.nc'

# Load the datasets
ds_statusquo = xr.open_dataset(statusquo_file_path)
ds_optimized = xr.open_dataset(optimized_file_path)

# Get the range of GridsK (vertical levels) for WindSpd
vertical_levels = list(ds_statusquo['GridsK'].values)

app = dash.Dash(__name__, external_stylesheets=['/assets/custom.css'])

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
    
    # Two graphs to show the comparison side by side
    
    # In the layout:
    html.Div([
        dcc.Graph(id='statusquo-graph', style={'flex': 1}),  # Make the graphs flexible
        dcc.Graph(id='optimized-graph', style={'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'row'})

])

# Update callback for the two graphs
@app.callback(
    [Output('statusquo-graph', 'figure'),
     Output('optimized-graph', 'figure')],
    [Input('kpi-dropdown', 'value'),
     Input('vertical-level-dropdown', 'value')]
)
def update_graphs(selected_kpi, selected_level):
    if selected_kpi == 'WindSpd':
        selected_level = int(selected_level)
        
        # For WindSpd, get the data for the selected vertical level
        statusquo_data = ds_statusquo[selected_kpi].isel(Time=0, GridsK=selected_level).values
        optimized_data = ds_optimized[selected_kpi].isel(Time=0, GridsK=selected_level).values
    else:
        # For other KPIs, get the 2D data without vertical dimension
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
    statusquo_df = pd.DataFrame({
        'Value': statusquo_data_flat,
        'Grid X': grid_x_vals,
        'Grid Y': grid_y_vals
    })

    optimized_df = pd.DataFrame({
        'Value': optimized_data_flat,
        'Grid X': grid_x_vals,
        'Grid Y': grid_y_vals
    })
    
    color_scale = 'RdBu'
    plot_size = 700

    # Create the figures for Status Quo and Optimized scenarios
    statusquo_fig = px.scatter(statusquo_df, x='Grid X', y='Grid Y', color='Value',
                               title=f"Status Quo: {selected_kpi}",
                               color_continuous_scale=color_scale, height=plot_size, width=plot_size)
    
    optimized_fig = px.scatter(optimized_df, x='Grid X', y='Grid Y', color='Value',
                               title=f"Optimized: {selected_kpi}",
                               color_continuous_scale=color_scale, height=plot_size, width=plot_size)

    return statusquo_fig, optimized_fig


if __name__ == '__main__':
    app.run_server(debug=True)
