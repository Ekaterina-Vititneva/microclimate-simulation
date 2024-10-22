import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Initialize the Dash app
app = dash.Dash(__name__)

# Expose the Flask server (for Gunicorn)
server = app.server

# Sample data (replace with your actual data or visualizations)
df = pd.DataFrame({
    "Category": ["A", "B", "C"],
    "Values": [10, 20, 30]
})

# Layout for the Dash app
app.layout = html.Div(children=[
    html.H1(children='Microclimate Simulation Dashboard'),

    html.Div(children='''
        Status Quo vs. Optimized Scenario Comparison
    '''),

    # Example Graph (replace this with your visualizations)
    dcc.Graph(
        id='example-graph',
        figure=px.bar(df, x="Category", y="Values", title="Sample Data Visualization")
    ),

    # Dropdown for interaction (if needed)
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Option 1', 'value': '1'},
            {'label': 'Option 2', 'value': '2'}
        ],
        value='1'
    ),
])

# Callback (replace with your actual interactive functionality)
@app.callback(
    Output('example-graph', 'figure'),
    [Input('dropdown', 'value')]
)
def update_graph(selected_option):
    # Example update logic (use real data/logic for your task)
    if selected_option == '1':
        return px.bar(df, x="Category", y="Values", title="Option 1 Data")
    else:
        return px.bar(df, x="Category", y="Values", title="Option 2 Data")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
