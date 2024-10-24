import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import xarray as xr
import pandas as pd
import numpy as np  # Already imported for NumPy
import plotly.express as px  # Import for Plotly Express
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
    html.Div([
        dcc.Graph(id='statusquo-graph', style={'flex': 1}),
        dcc.Graph(id='optimized-graph', style={'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'row'})
])

# Update callback for the two heatmaps
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

    color_scale = 'RdBu_r'
    plot_size = 700

    # Create the heatmaps using Plotly's imshow function
    statusquo_fig = px.imshow(
        statusquo_data,
        color_continuous_scale=color_scale,
        title=f"Status Quo: {selected_kpi}",
        aspect='auto',
        labels={"color": f"{selected_kpi} Value"},
        height=plot_size, width=plot_size
    )

    optimized_fig = px.imshow(
        optimized_data,
        color_continuous_scale=color_scale,
        title=f"Optimized: {selected_kpi}",
        aspect='auto',
        labels={"color": f"{selected_kpi} Value"},
        height=plot_size, width=plot_size
    )

    return statusquo_fig, optimized_fig


if __name__ == '__main__':
    app.run_server(debug=True)
