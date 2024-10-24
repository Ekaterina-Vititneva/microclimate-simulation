import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import xarray as xr
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from kpi_config import kpi_options, kpi_descriptions

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
    statusquo_min = float(ds_statusquo[kpi].min().values)
    statusquo_max = float(ds_statusquo[kpi].max().values)
    optimized_min = float(ds_optimized[kpi].min().values)
    optimized_max = float(ds_optimized[kpi].max().values)
    global_min = min(statusquo_min, optimized_min)
    global_max = max(statusquo_max, optimized_max)
    return global_min, global_max

app.layout = html.Div([
    html.H1("Microclimate Simulation Dashboard"),
    
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
        ], style={'width': '33%', 'padding': '5px'}),  # 1/3 width for controls

        # Description area
        html.Div([
            html.H3("KPI Description"),
            html.P(id='kpi-description', style={'white-space': 'pre-wrap'})
        ], style={'width': '66%', 'padding': '10px'})  # 2/3 width for description
    ], style={'display': 'flex', 'flex-direction': 'row'}),  # Flexbox for layout

    # Three graphs to show the comparison side by side
    html.Div([
        dcc.Graph(id='statusquo-graph', style={'flex': 1, 'margin-right': '5px'}),
        dcc.Graph(id='optimized-graph', style={'flex': 1, 'margin-right': '5px'}),
        dcc.Graph(id='difference-graph', style={'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'row', 'height': '75vh', 'padding': '0px', 'margin': '0px'}),

    # Boxplot section
    html.Div([
        dcc.Graph(id='statusquo-boxplot', style={'flex': 1, 'margin-right': '5px'}),
        dcc.Graph(id='optimized-boxplot', style={'flex': 1, 'margin-right': '5px'}),
        dcc.Graph(id='difference-boxplot', style={'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'row', 'height': '40vh', 'padding': '0px', 'margin': '0px'})
])

@app.callback(
    [Output('statusquo-graph', 'figure'),
     Output('optimized-graph', 'figure'),
     Output('difference-graph', 'figure'),
     Output('statusquo-boxplot', 'figure'),
     Output('optimized-boxplot', 'figure'),
     Output('difference-boxplot', 'figure'),
     Output('vertical-level-dropdown', 'style'),
     Output('kpi-description', 'children')],
    [Input('kpi-dropdown', 'value'),
     Input('time-slider', 'value'),
     Input('vertical-level-dropdown', 'value')]
)
def update_graphs(selected_kpi, selected_time, selected_level):
    global_min, global_max = get_global_range(selected_kpi)

    if selected_kpi == 'WindSpd':
        selected_level = int(selected_level)
        statusquo_data = ds_statusquo[selected_kpi].isel(Time=selected_time, GridsK=selected_level).values
        optimized_data = ds_optimized[selected_kpi].isel(Time=selected_time, GridsK=selected_level).values
        dropdown_style = {'display': 'block'}
    else:
        statusquo_data = ds_statusquo[selected_kpi].isel(Time=selected_time).values
        optimized_data = ds_optimized[selected_kpi].isel(Time=selected_time).values
        dropdown_style = {'display': 'none'}

    difference_data = statusquo_data - optimized_data
    color_scale = 'RdBu_r'
    plot_height = 500
    plot_width = 500

    # Create the heatmaps
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

    # Create the boxplots
    statusquo_boxplot = px.box(pd.DataFrame(statusquo_data.flatten(), columns=[f"{selected_kpi} Value"]),
                               title=f"Status Quo {selected_kpi} Boxplot (Time: {selected_time})",
                               height=200)
    
    optimized_boxplot = px.box(pd.DataFrame(optimized_data.flatten(), columns=[f"{selected_kpi} Value"]),
                               title=f"Optimized {selected_kpi} Boxplot (Time: {selected_time})",
                               height=200)
    
    difference_boxplot = px.box(pd.DataFrame(difference_data.flatten(), columns=["Difference"]),
                                title=f"Difference (Status Quo - Optimized) Boxplot (Time: {selected_time})",
                                height=200)

    description = kpi_descriptions.get(selected_kpi, "No description available.")

    return (statusquo_fig, optimized_fig, difference_fig,
            statusquo_boxplot, optimized_boxplot, difference_boxplot,
            dropdown_style, description)


if __name__ == '__main__':
    app.run_server(debug=True)
