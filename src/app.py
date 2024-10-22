import dash  
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import xarray as xr
import os
import requests

# Initialize the Dash app
app = dash.Dash(__name__)

# Expose the Flask server (for Gunicorn)
server = app.server

# Download function definition
def download_file_from_google_drive(url, dest_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        print(f"File downloaded successfully to {dest_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

# Direct download URL for the file
google_drive_url = "https://drive.google.com/uc?export=download&id=1WoosJY9mvntGX46i-2daZmJKvXt_vWed"

# The path where to save the .nc file
nc_file_path = "data/statusquo/Playground_2024-07-06_04.00.00.nc"

# Download the file if it doesn't exist locally
if not os.path.exists(nc_file_path):
    download_file_from_google_drive(google_drive_url, nc_file_path)

# Load the netCDF file
ds = xr.open_dataset(nc_file_path)

# Layout for the Dash app
app.layout = html.Div(children=[
    html.H1(children='Microclimate Simulation Dashboard'),

    html.Div(children='''
        Surface Temperature Visualization
    '''),

    # Dropdown for selecting time step
    dcc.Dropdown(
        id='time-dropdown',
        options=[{'label': str(time_val), 'value': str(time_val)} for time_val in ds['Time'].values],
        value=str(ds['Time'].values[0]),  # Default value is the first time step
    ),

    # Example Graph (replace with your visualizations)
    dcc.Graph(id='surface-temp-graph'),
])

# Callback for updating the surface temperature plot based on the selected time step
@app.callback(
    Output('surface-temp-graph', 'figure'),
    [Input('time-dropdown', 'value')]
)
def update_surface_temp_graph(selected_time):
    # Extract the surface temperature data for the selected time step
    surface_temperature = ds['TSurf'].sel(Time=selected_time)
    
    # Create a heatmap of the surface temperature
    fig = go.Figure(data=go.Heatmap(
        z=surface_temperature.values,
        colorscale='coolwarm',
        colorbar=dict(title='Temperature (°C)')
    ))

    fig.update_layout(
        title=f'Surface Temperature at {selected_time}',
        xaxis_title='Grid X',
        yaxis_title='Grid Y'
    )

    return fig

# Run the app
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
