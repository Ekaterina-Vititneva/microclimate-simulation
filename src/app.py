import dash  
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import xarray as xr
import os
import requests

# Dropbox direct download link (with ?dl=1 for direct download)
dropbox_url = "https://www.dropbox.com/scl/fi/rh1ut0xug2cs0obkbyw1x/Playground_2024-07-06_04.00.00.nc?dl=1"

# Define chunk size (1 MB per chunk)
chunk_size = 1024 * 1024  # 1 MB

# Path to save the file
nc_file_path = "data/statusquo/Playground_2024-07-06_04.00.00.nc"

# Stream download and save the file in chunks
def download_file_in_chunks(url, dest_path, chunk_size):
    with requests.get(url, stream=True) as response:
        response.raise_for_status()  # Check for request errors
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # filter out keep-alive chunks
                    f.write(chunk)
            print(f"File downloaded successfully to {dest_path}")

# Download the file in chunks if it doesn't already exist
if not os.path.exists(nc_file_path):
    download_file_in_chunks(dropbox_url, nc_file_path, chunk_size)

# Load the netCDF file
def load_nc_file(file_path):
    try:
        ds = xr.open_dataset(file_path, engine='netcdf4')
        return ds
    except Exception as e:
        print(f"Error opening file {file_path}: {e}")
        return None

ds = load_nc_file(nc_file_path)

# Check if the dataset was loaded successfully
if ds is not None:
    print(f"Dataset loaded with dimensions: {ds.dims}")

# Initialize the Dash app
app = dash.Dash(__name__)

# Expose the Flask server (for Gunicorn)
server = app.server

# Layout for the Dash app
app.layout = html.Div(children=[
    html.H1(children='Microclimate Simulation Dashboard'),

    html.Div(children='''
        Surface Temperature Visualization
    '''),

    # Dropdown for selecting time step
    dcc.Dropdown(
        id='time-dropdown',
        options=[{'label': str(time_val), 'value': str(time_val)} for time_val in ds['Time'].values] if ds else [],
        value=str(ds['Time'].values[0]) if ds else '',  # Default value is the first time step
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
    if ds is not None:
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
    else:
        return go.Figure()

# Run the app
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
