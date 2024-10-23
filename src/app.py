import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import xarray as xr
import os
import requests
import tqdm

# Initialize the Dash app
app = dash.Dash(__name__)

# Expose the Flask server (for Gunicorn)
server = app.server

# File download function
def download_file_from_dropbox(dropbox_url, dest_path, chunk_size=1024):
    dropbox_url = dropbox_url.replace('?dl=0', '?dl=1')
    response = requests.get(dropbox_url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    with open(dest_path, 'wb') as file, tqdm.tqdm(
        desc=dest_path, total=total_size, unit='B', unit_scale=True
    ) as progress_bar:
        for chunk in response.iter_content(chunk_size=chunk_size):
            file.write(chunk)
            progress_bar.update(len(chunk))
    print(f"File downloaded successfully to {dest_path}")

# File path for the netCDF file
nc_file_path = "data/statusquo/Playground_2024-07-06_04.00.00.nc"

# Dropbox link
dropbox_url = "https://www.dropbox.com/scl/fi/rh1ut0xug2cs0obkbyw1x/Playground_2024-07-06_04.00.00.nc?rlkey=e1y3knxpe3ilbv94jul5whvs2&st=x8t7herm&dl=0"

# Download the file if it doesn't exist locally
if not os.path.exists(nc_file_path):
    download_file_from_dropbox(dropbox_url, nc_file_path)

# Initialize the dataset as None
ds = None

# Load the netCDF file and verify it
try:
    ds = xr.open_dataset(nc_file_path, engine='netcdf4')
    print(f"Dataset structure: {ds}")
except Exception as e:
    print(f"Error opening file {nc_file_path}: {e}")

# Layout for the Dash app
app.layout = html.Div(children=[
    html.H1(children='Microclimate Simulation Dashboard'),

    html.Div(children='''
        Surface Temperature Visualization
    '''),

    # Dropdown for selecting time step
    dcc.Dropdown(
        id='time-dropdown',
        options=[{'label': str(time_val), 'value': str(time_val)} for time_val in ds['Time'].values] if ds and 'Time' in ds else [],
        value=str(ds['Time'].values[0]) if ds and 'Time' in ds else None,
        placeholder="Select..."
    ),

    # Graph for displaying the surface temperature
    dcc.Graph(id='surface-temp-graph'),

    # Button to manually trigger data load
    html.Button('Load Data', id='load-button', n_clicks=0)
])

# Callback for updating the surface temperature plot based on the selected time step
@app.callback(
    Output('surface-temp-graph', 'figure'),
    [Input('time-dropdown', 'value')]
)
def update_surface_temp_graph(selected_time):
    if selected_time is None or ds is None:
        return go.Figure()

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
