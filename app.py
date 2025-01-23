import dash
from dash import html
from components import layout
from callbacks import register_callbacks
app = dash.Dash(__name__, external_stylesheets=['styles.css'])

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the layout of the app
app.layout = layout

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)