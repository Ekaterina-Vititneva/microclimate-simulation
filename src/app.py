import xarray as xr
import dash 
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import os

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Load the .nc files (replace with your file paths)
statusquo_file = 'data/statusquo/Playground_2024-07-06_04.00.00.nc'
optimized_file = 'data/opti/Playground_2024-07-06_04.00.00.nc'

ds_statusquo = xr.open_dataset(statusquo_file)
ds_optimized = xr.open_dataset(optimized_file)

# Sample code to extract and process data from .nc files
df_statusquo = ds_statusquo.to_dataframe().reset_index()
df_optimized = ds_optimized.to_dataframe().reset_index()

# Merge or compare the data as needed (custom logic)
df_comparison = pd.concat([df_statusquo, df_optimized])

# Layout for the Dash app
app.layout = html.Div(children=[
    html.H1(children='Microclimate Simulation Dashboard'),

    html.Div(children='''
        Status Quo vs. Optimized Scenario Comparison
    '''),

    # Example Graph
    dcc.Graph(
        id='comparison-graph',
        figure=px.line(df_comparison, x="Time", y="Temperature", color="Scenario", title="Temperature Over Time")
    ),
])

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))