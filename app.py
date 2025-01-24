import dash
import dash_bootstrap_components as dbc
from dash import html
from components import layout
from callbacks import register_callbacks

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Set the layout of the app
app.layout = html.Div(
    id="main-container",
    children=[
        layout,
    ]
)

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)