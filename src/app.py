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
def download_file_in_chunks(url, dest_path, chunk_size=1024*1024):
    response = requests.get(url, stream=True)
    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
    print(f"File downloaded successfully to {dest_path}")

# The path where to save the .nc file
nc_file_path = "data/statusquo/Playground_2024-07-06_04.00.00.nc"

# Layout for the Dash app
app.layout = html.Div(children=[
    html.H1(children='Microclimate Simulation Dashboard'),

    html.Div(children='''Surface Temperature Visualization'''),

    dcc.Dropdown(
        id='time-dropdown',
        options=[],  # Will be updated after file is loaded
        value=None,
    ),
    dcc.Graph(id='surface-temp-graph'),

    # Button to trigger file download and processing
    html.Button("Load Data", id="load-data-button", n_clicks=0)
])

# Callback to load and process the data
@app.callback(
    [Output('time-dropdown', 'options'), Output('time-dropdown', 'value')],
    [Input('load-data-button', 'n_clicks')]
)
def load_data(n_clicks):
    if n_clicks > 0:
        # Download the file in chunks if it doesn't exist
        if not os.path.exists(nc_file_path):
            dropbox_url = "https://www.dropbox.com/scl/fi/rh1ut0xug2cs0obkbyw1x/Playground_2024-07-06_04.00.00.nc?dl=1"
            download_file_in_chunks(dropbox_url, nc_file_path)

        # Load the NetCDF file using Xarray
        ds = xr.open_dataset(nc_file_path, engine='netcdf4', chunks={'Time': 10})
        
        # Get time steps for dropdown
        time_options = [{'label': str(time_val), 'value': str(time_val)} for time_val in ds['Time'].values]
        
        return time_options, time_options[0]['value']  # Set the first time step as default

    return [], None

# Callback for updating the surface temperature plot
@app.callback(
    Output('surface-temp-graph', 'figure'),
    [Input('time-dropdown', 'value')]
)
def update_surface_temp_graph(selected_time):
    if selected_time:
        ds = xr.open_dataset(nc_file_path, engine='netcdf4', chunks={'Time': 10})
        surface_temperature = ds['TSurf'].sel(Time=selected_time)
        fig = go.Figure(data=go.Heatmap(
            z=surface_temperature.values,
            colorscale=[[0, 'blue'], [0.5, 'white'], [1, 'red']]
        ))
        fig.update_layout(
            title=f'Surface Temperature at {selected_time}',
            width=600,  # Set the width
            height=600,  # Set the height (same as width to make it square)
        )
        return fig
    return go.Figure()

# Run the app
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
