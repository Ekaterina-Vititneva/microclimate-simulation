import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import xarray as xr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import r2_score
import json

# Load the KPI configuration from JSON file
with open('./config/kpi_config.json') as f:
    kpi_config = json.load(f)

# Access the options and descriptions
kpi_options = kpi_config['kpi_options']
kpi_descriptions = kpi_config['kpi_descriptions']

# Paths to the datasets
statusquo_file_path = '../data/statusquo/Playground_2024-07-06_04.00.00_light.nc'
optimized_file_path = '../data/opti/Playground_2024-07-06_04.00.00_light.nc'

# Load the datasets
ds_statusquo = xr.open_dataset(statusquo_file_path)
ds_optimized = xr.open_dataset(optimized_file_path)

# Get the time dimension and vertical levels
time_steps = ds_statusquo['Time'].values
vertical_levels = list(ds_statusquo['GridsK'].values)

# Heatmap size control
heatmap_size = 500  # Variable to control heatmap size (height and width)

app = dash.Dash(__name__, external_stylesheets=['/assets/custom.css'])

# Function to calculate global min and max for a KPI across all times and heights
def get_global_range(kpi):
    statusquo_min = float(ds_statusquo[kpi].min().values)
    statusquo_max = float(ds_statusquo[kpi].max().values)
    optimized_min = float(ds_optimized[kpi].min().values)
    optimized_max = float(ds_optimized[kpi].max().values)
    global_min = min(statusquo_min, optimized_min)
    global_max = max(statusquo_max, optimized_max)
    return global_min, global_max

app.layout = html.Div([
    html.H1("Microclimate Simulation Dashboard - ENVI-met Playground Project"),
    
    # Row with dropdowns, slider, and KPI description
    html.Div([
        # Controls (dropdowns and slider)
        html.Div([
            html.Label("Select a KPI to compare:"),
            dcc.Dropdown(
                id='kpi-dropdown',
                options=[{'label': kpi, 'value': kpi} for kpi in kpi_options],
                value=kpi_options[0],  # Default value
                clearable=False
            ),

            html.Label("Select Time Step:"),
            dcc.Slider(
                id='time-slider',
                min=0,
                max=len(time_steps) - 1,
                value=12,  # Default to hour 12 (noon)
                marks={i: str(i) for i in range(len(time_steps))},
                step=1
            ),

            html.Label("Select Vertical Level (GridsK) for WindSpd:"),
            dcc.Dropdown(
                id='vertical-level-dropdown',
                options=[{'label': f'Level {int(level)}', 'value': level} for level in vertical_levels],
                value=vertical_levels[0],  # Default level
                clearable=False,
                style={'display': 'none'}
            ),
        ], style={'width': '33%'}),  # 1/3 width for controls, reduced padding

        # Description area
        html.Div([
            html.H3("KPI Description"),
            html.P(id='kpi-description', style={'white-space': 'pre-wrap'})
        ], style={'width': '67%', 'margin-left': '50px'})  # 2/3 width for description, reduced padding
    ], style={'display': 'flex', 'flex-direction': 'row'}),  # Flexbox for layout

    # Three graphs to show the comparison side by side
    html.Div([
        dcc.Graph(id='statusquo-graph', style={'flex': 1}),
        dcc.Graph(id='optimized-graph', style={'flex': 1}),
        dcc.Graph(id='difference-graph', style={'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'row', 'height': '55vh'}),

    # Hourly plot showing the min-max range and mean over time for both scenarios
    html.Div([
        dcc.Graph(id='hourly-plot', style={'width': '100%'})
    ], style={'height': '40vh'})
])

@app.callback(
    [Output('statusquo-graph', 'figure'),
     Output('optimized-graph', 'figure'),
     Output('difference-graph', 'figure'),
     Output('hourly-plot', 'figure'),
     Output('vertical-level-dropdown', 'style'),
     Output('kpi-description', 'children')],
    [Input('kpi-dropdown', 'value'),
     Input('time-slider', 'value'),
     Input('vertical-level-dropdown', 'value')]
)
def update_graphs(selected_kpi, selected_time, selected_level):
    global_min, global_max = get_global_range(selected_kpi)

    # Check if the selected KPI has 'GridsK' dimension
    if 'GridsK' in ds_statusquo[selected_kpi].dims:
        # 3D KPIs with GridsK
        if selected_kpi == 'WindSpd':
            selected_level = int(selected_level)
            statusquo_data = ds_statusquo[selected_kpi].isel(Time=selected_time, GridsK=selected_level).values
            optimized_data = ds_optimized[selected_kpi].isel(Time=selected_time, GridsK=selected_level).values
            dropdown_style = {'display': 'block'}
        else:
            # For other 3D KPIs, take the mean across the 'GridsK' dimension
            statusquo_data = ds_statusquo[selected_kpi].isel(Time=selected_time).mean(dim='GridsK').values
            optimized_data = ds_optimized[selected_kpi].isel(Time=selected_time).mean(dim='GridsK').values
            dropdown_style = {'display': 'none'}
    else:
        # 2D KPIs (no 'GridsK' dimension)
        statusquo_data = ds_statusquo[selected_kpi].isel(Time=selected_time).values
        optimized_data = ds_optimized[selected_kpi].isel(Time=selected_time).values
        dropdown_style = {'display': 'none'}

    # Flatten the data and remove NaN values before calculating R²
    statusquo_flat = statusquo_data.flatten()
    optimized_flat = optimized_data.flatten()

    # Remove NaN values from both arrays
    mask = ~np.isnan(statusquo_flat) & ~np.isnan(optimized_flat)
    statusquo_filtered = statusquo_flat[mask]
    optimized_filtered = optimized_flat[mask]

    # Calculate R² only on the filtered (non-NaN) data
    if len(statusquo_filtered) > 0 and len(optimized_filtered) > 0:
        r2 = r2_score(statusquo_filtered, optimized_filtered)
    else:
        r2 = float('nan')  # If no valid data remains after filtering

    difference_data = statusquo_data - optimized_data
    color_scale = 'RdBu_r'

    # Create the heatmaps with controlled size
    statusquo_fig = px.imshow(
        statusquo_data,
        color_continuous_scale=color_scale,
        title=f"Status Quo: {selected_kpi} (Time: {selected_time})",
        zmin=global_min, zmax=global_max,
        width=heatmap_size, height=heatmap_size,
        labels={"color": f"{selected_kpi} Value"}
    )

    optimized_fig = px.imshow(
        optimized_data,
        color_continuous_scale=color_scale,
        title=f"Optimized: {selected_kpi} (Time: {selected_time})",
        zmin=global_min, zmax=global_max,
        width=heatmap_size, height=heatmap_size,
        labels={"color": f"{selected_kpi} Value"}
    )

    difference_fig = px.imshow(
        difference_data,
        color_continuous_scale=color_scale,
        title=f"Difference (Status Quo - Optimized): {selected_kpi} (Time: {selected_time}) R² = {r2:.2f}",
        zmin=-abs(global_max - global_min), zmax=abs(global_max - global_min),
        width=heatmap_size, height=heatmap_size,
        labels={"color": "Difference"}
    )

    # Calculate hourly mean, min, and max for the selected KPI (both status quo and optimized)
    statusquo_hourly_mean = ds_statusquo[selected_kpi].mean(dim=['GridsI', 'GridsJ']).values
    statusquo_hourly_min = ds_statusquo[selected_kpi].min(dim=['GridsI', 'GridsJ']).values
    statusquo_hourly_max = ds_statusquo[selected_kpi].max(dim=['GridsI', 'GridsJ']).values

    optimized_hourly_mean = ds_optimized[selected_kpi].mean(dim=['GridsI', 'GridsJ']).values
    optimized_hourly_min = ds_optimized[selected_kpi].min(dim=['GridsI', 'GridsJ']).values
    optimized_hourly_max = ds_optimized[selected_kpi].max(dim=['GridsI', 'GridsJ']).values

    time_hours = [str(t)[11:13] for t in ds_statusquo['Time'].values]  # Extract hour for x-axis

    # Create the hourly plot with mean, min-max range
    hourly_fig = go.Figure()

    # Min-max range shaded area for status quo
    hourly_fig.add_trace(go.Scatter(
        x=time_hours, y=statusquo_hourly_max,
        mode='lines', line=dict(width=0), showlegend=False,
        hoverinfo='skip', name='Max Status Quo'
    ))
    hourly_fig.add_trace(go.Scatter(
        x=time_hours, y=statusquo_hourly_min,
        mode='lines', fill='tonexty', fillcolor='rgba(0, 100, 250, 0.2)',
        line=dict(width=0), name='Min-Max Range Status Quo', hoverinfo='skip'
    ))

    # Mean line for status quo
    hourly_fig.add_trace(go.Scatter(
        x=time_hours, y=statusquo_hourly_mean, mode='lines+markers', line=dict(color='blue', width=2),
        name='Mean Status Quo', hoverinfo='x+y'
    ))

    # Min-max range shaded area for optimized
    hourly_fig.add_trace(go.Scatter(
        x=time_hours, y=optimized_hourly_max,
        mode='lines', line=dict(width=0), showlegend=False,
        hoverinfo='skip', name='Max Optimized'
    ))
    hourly_fig.add_trace(go.Scatter(
        x=time_hours, y=optimized_hourly_min,
        mode='lines', fill='tonexty', fillcolor='rgba(250, 100, 0, 0.2)',
        line=dict(width=0), name='Min-Max Range Optimized', hoverinfo='skip'
    ))

    # Mean line for optimized
    hourly_fig.add_trace(go.Scatter(
        x=time_hours, y=optimized_hourly_mean, mode='lines+markers', line=dict(color='red', width=2),
        name='Mean Optimized', hoverinfo='x+y'
    ))

    hourly_fig.update_layout(
        title=f'Mean {selected_kpi} with Min-Max Range (Status Quo vs Optimized)',
        xaxis_title='Hour of the Day',
        yaxis_title=f'{selected_kpi} Value',
        height=500
    )

    description = kpi_descriptions.get(selected_kpi, "No description available.")

    return (statusquo_fig, optimized_fig, difference_fig, hourly_fig, dropdown_style, description)

if __name__ == '__main__':
    app.run_server(debug=True)
