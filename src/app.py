import dash  
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import xarray as xr
import os
from kpi_config import kpi_options

# Initialize the Dash app
app = dash.Dash(__name__)

# Expose the Flask server (for Gunicorn)
server = app.server

# Get the project root directory (one level up from src)
base_dir = os.path.dirname(os.getcwd())

# Paths to the light versions of the datasets
statusquo_file_path = os.path.join(base_dir, 'data', 'statusquo', 'Playground_2024-07-06_04.00.00_light.nc')
optimized_file_path = os.path.join(base_dir, 'data', 'opti', 'Playground_2024-07-06_04.00.00_light.nc')

# Load the light NetCDF files
ds_statusquo = xr.open_dataset(statusquo_file_path)
ds_optimized = xr.open_dataset(optimized_file_path)

# List of available KPIs
#kpi_options = ['TSurf', 'AirTempAtVeg', 'Albedo']

# Layout for the Dash app
app.layout = html.Div(children=[
    html.H1(children='Microclimate Simulation Dashboard'),

    html.Div(children='''Select a KPI to compare:'''),

    # Dropdown for selecting KPI
    dcc.Dropdown(
        id='kpi-dropdown',
        options=[{'label': kpi, 'value': kpi} for kpi in kpi_options],
        value='TSurf'  # Default selected KPI
    ),

    # Graph to display the KPI comparison
    dcc.Graph(id='kpi-comparison-graph'),
])

# Callback to update the graph based on selected KPI
@app.callback(
    Output('kpi-comparison-graph', 'figure'),
    [Input('kpi-dropdown', 'value')]
)
def update_kpi_comparison(selected_kpi):
    # Extract the KPI data for both scenarios
    kpi_statusquo = ds_statusquo[selected_kpi].isel(Time=0).values
    kpi_optimized = ds_optimized[selected_kpi].isel(Time=0).values

    # Create the figure
    fig = go.Figure()

    # Add traces for both status quo and optimized scenarios
    fig.add_trace(go.Heatmap(
        z=kpi_statusquo,
        colorscale='Blues',
        name='Status Quo',
        zmin=kpi_statusquo.min(),
        zmax=kpi_statusquo.max()
    ))

    fig.add_trace(go.Heatmap(
        z=kpi_optimized,
        colorscale='Reds',
        name='Optimized',
        zmin=kpi_optimized.min(),
        zmax=kpi_optimized.max()
    ))

    # Update layout
    fig.update_layout(
        title=f'Comparison of {selected_kpi} between Status Quo and Optimized',
        xaxis_title='Grid X',
        yaxis_title='Grid Y',
        width=700,
        height=700
    )

    return fig

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
