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
import os
from plotly.subplots import make_subplots

# Get the absolute path to the config folder based on the current script directory
config_dir = os.path.join(os.path.dirname(__file__), 'config')
json_config_path = os.path.join(config_dir, 'kpi_config.json')

with open(json_config_path, 'r') as f:
    kpi_config = json.load(f)

# Get the project root directory (one level up from src)
#base_dir = os.path.dirname(os.getcwd())

# Get one level up from the current directory
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Access the options and descriptions
kpi_options = kpi_config['kpi_options']
kpi_descriptions = kpi_config['kpi_descriptions']

#print("Current working directory:", os.getcwd())
#print("Files in current directory:", os.listdir())

# Paths to the datasets
statusquo_file_path = os.path.join(base_dir, 'data', 'statusquo', 'Playground_2024-07-06_04.00.00_light.nc')
optimized_file_path = os.path.join(base_dir, 'data', 'opti', 'Playground_2024-07-06_04.00.00_light.nc')

# Load the datasets
ds_statusquo = xr.open_dataset(statusquo_file_path)
ds_optimized = xr.open_dataset(optimized_file_path)

# Get the time dimension and vertical levels
time_steps = ds_statusquo['Time'].values
vertical_levels = list(ds_statusquo['GridsK'].values)

# Heatmap size control
heatmap_size = 500  # Variable to control heatmap size (height and width)

app = dash.Dash(__name__, external_stylesheets=['/assets/custom.css'])

# Expose the underlying Flask server instance for Gunicorn
server = app.server

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

    # Row with dropdowns, slider, KPI description, and hourly plot
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
            html.Label("Select Vertical Level (GridsK):"),
            dcc.Dropdown(
                id='vertical-level-dropdown',
                options=[{'label': f'Level {int(level)}', 'value': level} for level in vertical_levels],
                value=vertical_levels[0],  # Default level
                clearable=False,
                style={'display': 'none'}
            ),
        ], style={'width': '33%'}),  # 1/3 width for controls

        # Description area
        html.Div([
            html.H3("KPI Description"),
            html.P(id='kpi-description', style={'white-space': 'pre-wrap'})
        ], style={'width': '33%', 'margin-left': '10px'}),  # 1/3 width for description

        # Hourly plot placed in the top-right corner
        html.Div([
            dcc.Graph(id='hourly-plot', style={'width': '100%', 'height': '225px'})
        ], style={'width': '33%', 'margin-left': '10px'})  # 1/3 width for hourly plot
    ], style={'display': 'flex', 'flex-direction': 'row'}),  # Flexbox for layout

    # Row for heatmaps
    html.Div([
    dcc.Graph(
        id='heatmap-graphs',
        style={'width': '100%', 'height': '55vh', 'padding': '0', 'margin': '0'},
        config={'responsive': True}
    )
    ], style={'padding': '0', 'margin': '0'})

])


@app.callback(
    [Output('heatmap-graphs', 'figure'),
     Output('hourly-plot', 'figure'),
     Output('vertical-level-dropdown', 'style'),
     Output('kpi-description', 'children')],
    [Input('kpi-dropdown', 'value'),
     Input('time-slider', 'value'),
     Input('vertical-level-dropdown', 'value')]
)
def update_graphs(selected_kpi, selected_time, selected_level):
    global_min, global_max = get_global_range(selected_kpi)
    # Initialize the dropdown_style as hidden (default)
    dropdown_style = {'display': 'none'}

    # Function to compute mean, min, and max for hourly plot dynamically
    def compute_hourly_stats(ds, kpi, has_grids_k):
        if has_grids_k:
            mean = ds[kpi].mean(dim=['GridsI', 'GridsJ', 'GridsK']).values
            min_val = ds[kpi].min(dim=['GridsI', 'GridsJ', 'GridsK']).values
            max_val = ds[kpi].max(dim=['GridsI', 'GridsJ', 'GridsK']).values
        else:
            mean = ds[kpi].mean(dim=['GridsI', 'GridsJ']).values
            min_val = ds[kpi].min(dim=['GridsI', 'GridsJ']).values
            max_val = ds[kpi].max(dim=['GridsI', 'GridsJ']).values
        return mean, min_val, max_val

    # Determine if the KPI has a GridsK dimension (i.e., it's 3D)
    has_grids_k = 'GridsK' in ds_statusquo[selected_kpi].dims

    # If GridsK exists (i.e., 3D data like WindSpd), adjust accordingly
    if has_grids_k:
        # Find the index of the closest GridsK level
        selected_level_idx = int(np.argmin(np.abs(ds_statusquo['GridsK'].values - float(selected_level))))

        # Assign data for the heatmaps using the nearest GridsK index
        statusquo_data = ds_statusquo[selected_kpi].isel(Time=selected_time, GridsK=selected_level_idx).values
        optimized_data = ds_optimized[selected_kpi].isel(Time=selected_time, GridsK=selected_level_idx).values

        # Show vertical level dropdown if GridsK dimension exists
        dropdown_style = {'display': 'block'}
    else:
        # For 2D KPIs, no need to handle GridsK
        statusquo_data = ds_statusquo[selected_kpi].isel(Time=selected_time).values
        optimized_data = ds_optimized[selected_kpi].isel(Time=selected_time).values

    # Compute hourly statistics (mean, min, max) for both status quo and optimized scenarios
    statusquo_hourly_mean, statusquo_hourly_min, statusquo_hourly_max = compute_hourly_stats(ds_statusquo, selected_kpi, has_grids_k)
    optimized_hourly_mean, optimized_hourly_min, optimized_hourly_max = compute_hourly_stats(ds_optimized, selected_kpi, has_grids_k)

    # Calculate R² for the heatmap difference plot
    statusquo_flat = statusquo_data.flatten()
    optimized_flat = optimized_data.flatten()
    mask = ~np.isnan(statusquo_flat) & ~np.isnan(optimized_flat)
    statusquo_filtered = statusquo_flat[mask]
    optimized_filtered = optimized_flat[mask]
    
    r2 = r2_score(statusquo_filtered, optimized_filtered) if len(statusquo_filtered) > 0 else float('nan')

    difference_data = statusquo_data - optimized_data
    color_scale = 'RdBu_r'

    # Create the subplots figure
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=(
            f"Status Quo: {selected_kpi} (Time: {selected_time})",
            f"Optimized: {selected_kpi} (Time: {selected_time})",
            f"Difference (Status Quo - Optimized): {selected_kpi} (Time: {selected_time}) R² = {r2:.2f}"
        ),
        shared_xaxes=True,
        shared_yaxes=True,
        horizontal_spacing=0.05,
        column_widths=[0.3333, 0.3333, 0.3334]  # Equal widths
    )

    # Prepare data
    x = np.arange(statusquo_data.shape[1])
    y = np.arange(statusquo_data.shape[0])

    # Common colorbar properties
    colorbar_common = dict(
        thickness=15,
        len=0.75,        # Length of the colorbar (adjust as needed)
        y=1.0,          # Position at the top
        yanchor='top',  # Anchor the colorbar's top to y
        ticks='outside',
        ticklen=3,
        tickfont=dict(size=10)
    )


    # Add Status Quo heatmap
    fig.add_trace(
        go.Heatmap(
            z=statusquo_data,
            x=x,
            y=y,
            colorscale=color_scale,
            zmin=global_min,
            zmax=global_max,
            colorbar=dict(
                title=f"{selected_kpi} Value"
            ) | colorbar_common,
            showscale=True
        ),
        row=1, col=1
    )

    # Add Optimized heatmap
    fig.add_trace(
        go.Heatmap(
            z=optimized_data,
            x=x,
            y=y,
            colorscale=color_scale,
            zmin=global_min,
            zmax=global_max,
            colorbar=dict(
                title=f"{selected_kpi} Value"
            ) | colorbar_common,
            showscale=True
        ),
        row=1, col=2
    )

    # Add Difference heatmap
    fig.add_trace(
        go.Heatmap(
            z=difference_data,
            x=x,
            y=y,
            colorscale=color_scale,
            zmin=-abs(global_max - global_min),
            zmax=abs(global_max - global_min),
            colorbar=dict(
                title="Difference"
            ) | colorbar_common,
            showscale=True
        ),
        row=1, col=3
    )

    # Retrieve x-axis domains
    x_domain1 = fig.layout.xaxis.domain
    x_domain2 = fig.layout.xaxis2.domain
    x_domain3 = fig.layout.xaxis3.domain

    # Define a small offset for colorbars
    colorbar_offset = -0.01  # Adjust as needed

    # Set colorbar positions
    fig.data[0].colorbar.x = x_domain1[1] + colorbar_offset
    fig.data[1].colorbar.x = x_domain2[1] + colorbar_offset
    fig.data[2].colorbar.x = x_domain3[1] + colorbar_offset

    # Adjust subplot titles
    fig.layout.annotations = [
        dict(
            text=title['text'],
            x=(domain[0] + domain[1]) / 2,
            y=1.05,
            xref='paper',
            yref='paper',
            showarrow=False,
            font=dict(size=14),
            xanchor='center',
            yanchor='top'
        )
        for title, domain in zip(
            fig.layout.annotations,
            [x_domain1, x_domain2, x_domain3]
        )
    ]

    # Update the layout
    fig.update_layout(
        autosize=True,
        margin=dict(l=25, r=25, t=50, b=25),
        font=dict(size=12)
    )

    # Update axes
    fig.update_xaxes(
        showticklabels=True,
        scaleanchor='y',
        scaleratio=1,
        constrain='domain'
    )
    fig.update_yaxes(
        showticklabels=True,
        constrain='domain'
    )


    # Generate the hourly plot (mean, min, max) for all KPIs
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
        height=250,
        legend=dict(
            font=dict(size=10), orientation='h', yanchor='top',
            y=-0.4, xanchor='center', x=0.5
        ),
        font=dict(size=10),
        xaxis=dict(title='Hour of the Day', side='top', title_font=dict(size=12), tickfont=dict(size=9)),
        yaxis=dict(title_font=dict(size=12), tickfont=dict(size=9)),
        margin=dict(t=100, b=0)
    )

    # Set KPI description
    description = kpi_descriptions.get(selected_kpi, "No description available.")

    return (fig, hourly_fig, dropdown_style, description)


if __name__ == '__main__':
    app.run_server(debug=True)