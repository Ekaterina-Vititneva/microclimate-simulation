import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import xarray as xr
import pandas as pd
import numpy as np
import plotly.express as px
#from kpi_config import kpi_options

kpi_options = ['TSurf', 'WindSpd']

# Paths to the datasets
statusquo_file_path = '../data/statusquo/Playground_2024-07-06_04.00.00_light.nc'
optimized_file_path = '../data/opti/Playground_2024-07-06_04.00.00_light.nc'

# Load the datasets
ds_statusquo = xr.open_dataset(statusquo_file_path)
ds_optimized = xr.open_dataset(optimized_file_path)

# Get the time dimension and vertical levels
time_steps = ds_statusquo['Time'].values
vertical_levels = list(ds_statusquo['GridsK'].values)

app = dash.Dash(__name__, external_stylesheets=['/assets/custom.css'])

# Function to calculate global min and max for a KPI across all times and heights
def get_global_range(kpi):
    statusquo_min = float(ds_statusquo[kpi].min().values)  # Ensure Python float
    statusquo_max = float(ds_statusquo[kpi].max().values)  # Ensure Python float
    optimized_min = float(ds_optimized[kpi].min().values)  # Ensure Python float
    optimized_max = float(ds_optimized[kpi].max().values)  # Ensure Python float
    global_min = min(statusquo_min, optimized_min)
    global_max = max(statusquo_max, optimized_max)
    print(f"Global range for {kpi}: min={global_min}, max={global_max}")
    return global_min, global_max

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

    # Time slider for selecting the time step
    html.Label("Select Time Step:"),
    dcc.Slider(
        id='time-slider',
        min=0,
        max=len(time_steps) - 1,
        value=12,  # Default to the first time step
        marks={i: str(i) for i in range(len(time_steps))},  # Display time steps
        step=1
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
    
    # Three graphs to show the comparison side by side
    html.Div([
        dcc.Graph(id='statusquo-graph', style={'flex': 1, 'margin-right': '5px'}),
        dcc.Graph(id='optimized-graph', style={'flex': 1, 'margin-right': '5px'}),
        dcc.Graph(id='difference-graph', style={'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'row', 'height': '75vh', 'padding': '0px', 'margin': '0px'})
])

# Update callback for the three heatmaps with time selection
@app.callback(
    [Output('statusquo-graph', 'figure'),
     Output('optimized-graph', 'figure'),
     Output('difference-graph', 'figure'),
     Output('vertical-level-dropdown', 'style')],
    [Input('kpi-dropdown', 'value'),
     Input('time-slider', 'value'),
     Input('vertical-level-dropdown', 'value')]
)
def update_graphs(selected_kpi, selected_time, selected_level):
    # Get global min and max values for the selected KPI
    global_min, global_max = get_global_range(selected_kpi)

    if selected_kpi == 'WindSpd':
        selected_level = int(selected_level)
        
        # For WindSpd, get the data for the selected vertical level and time step
        statusquo_data = ds_statusquo[selected_kpi].isel(Time=selected_time, GridsK=selected_level).values
        optimized_data = ds_optimized[selected_kpi].isel(Time=selected_time, GridsK=selected_level).values
        dropdown_style = {'display': 'block'}
    else:
        # For other KPIs, get the 2D data without vertical dimension but with time selection
        statusquo_data = ds_statusquo[selected_kpi].isel(Time=selected_time).values
        optimized_data = ds_optimized[selected_kpi].isel(Time=selected_time).values
        dropdown_style = {'display': 'none'}

    # Calculate the difference between Status Quo and Optimized
    difference_data = statusquo_data - optimized_data

    color_scale = 'RdBu_r'
    
    plot_height = 500
    plot_width = 500

    # Create the heatmaps using Plotly's imshow function with constant color range
    statusquo_fig = px.imshow(
        statusquo_data,
        color_continuous_scale=color_scale,
        title=f"Status Quo: {selected_kpi} (Time: {selected_time})",
        zmin=global_min, zmax=global_max,
        aspect='auto',
        labels={"color": f"{selected_kpi} Value"},
        height=plot_height, width=plot_width
    )

    optimized_fig = px.imshow(
        optimized_data,
        color_continuous_scale=color_scale,
        title=f"Optimized: {selected_kpi} (Time: {selected_time})",
        zmin=global_min, zmax=global_max,
        aspect='auto',
        labels={"color": f"{selected_kpi} Value"},
        height=plot_height, width=plot_width
    )

    difference_fig = px.imshow(
        difference_data,
        color_continuous_scale=color_scale,
        title=f"Difference (Status Quo - Optimized): {selected_kpi} (Time: {selected_time})",
        zmin=-abs(global_max - global_min), zmax=abs(global_max - global_min),
        aspect='auto',
        labels={"color": "Difference"},
        height=plot_height, width=plot_width
    )

    return statusquo_fig, optimized_fig, difference_fig, dropdown_style


if __name__ == '__main__':
    app.run_server(debug=True)
