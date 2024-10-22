import dash  
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd
import xarray as xr
import os
import gdown  # Import gdown

print(xr.backends.list_engines())  # Should include 'netcdf4'

# Initialize the Dash app
app = dash.Dash(__name__)

# Expose the Flask server (for Gunicorn)
server = app.server

# Direct download URL for the file (you can use either format)
google_drive_url = 'https://drive.google.com/uc?id=1WoosJY9mvntGX46i-2daZmJKvXt_vWed'
# Alternatively, you can use the shareable link
# google_drive_url = 'https://drive.google.com/uc?export=download&id=1WoosJY9mvntGX46i-2daZmJKvXt_vWed'

# The path where to save the .nc file
nc_file_path = "data/statusquo/Playground_2024-07-06_04.00.00.nc"

# Download the file if it doesn't exist locally
if not os.path.exists(nc_file_path):
    os.makedirs(os.path.dirname(nc_file_path), exist_ok=True)  # Ensure directory exists
    print(f"Downloading file from {google_drive_url} to {nc_file_path}")
    gdown.download(url=google_drive_url, output=nc_file_path, quiet=False)
    file_size = os.path.getsize(nc_file_path)
    print(f"Downloaded file size: {file_size} bytes")
    if file_size < 1000000:  # Arbitrary threshold for checking size (1MB here)
        print("Warning: The downloaded file seems too small. It may be incomplete.")
else:
    print(f"File {nc_file_path} already exists locally.")

# Check if the file was downloaded successfully
if not os.path.exists(nc_file_path) or os.path.getsize(nc_file_path) < 1000000:
    raise Exception(f"File {nc_file_path} was not downloaded correctly or is incomplete.")

# Load the netCDF file
try:
    ds = xr.open_dataset(nc_file_path, engine='netcdf4')
except Exception as e:
    print(f"Error loading the netCDF file: {e}")
    raise e

print(f"Path to .nc file: {nc_file_path}")
print(os.path.exists(nc_file_path))  # Should return True if the file exists

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

    # Graph for the surface temperature
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

    fig = go.Figure(data=go.Heatmap(
        z=surface_temperature.values,
        colorscale=[[0, 'blue'], [0.5, 'white'], [1, 'red']]
    ))

    fig.update_layout(
        title=f'Surface Temperature at {selected_time}',
        xaxis_title='Grid X',
        yaxis_title='Grid Y',
        width=600,  # Set the width
        height=600,  # Set the height (same as width to make it square)
    )

    return fig

# Run the app
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
