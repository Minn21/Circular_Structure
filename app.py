import dash
import dash_bootstrap_components as dbc
from dash import html
from components import layout
from callbacks import register_callbacks

# Enhanced Inline CSS with more refined styling
CUSTOM_CSS = '''
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --accent-color: #2ecc71;
    --background-light: #f4f6f9;
    --text-dark: #2c3e50;
    --text-muted: #7f8c8d;
    --card-shadow: 0 8px 16px rgba(0, 0, 0, 0.08);
}

body {
    background: linear-gradient(135deg, var(--background-light) 0%, #ecf0f1 100%);
    font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
    color: var(--text-dark);
    line-height: 1.8;
}

.main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
    background-color: white;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
    border-radius: 12px;
}

h2 {
    text-align: center;
    color: var(--primary-color);
    font-weight: 700;
    margin-bottom: 2rem;
    background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.card {
    border: none;
    border-radius: 10px;
    transition: all 0.3s ease;
    box-shadow: var(--card-shadow);
    margin-bottom: 1rem;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.card-header {
    background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
    color: white;
    font-weight: 600;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}

.btn-primary {
    background: linear-gradient(to right, var(--secondary-color), var(--accent-color));
    border: none;
    transition: all 0.3s ease;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.btn-primary:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.graph-container {
    background-color: white;
    border-radius: 12px;
    box-shadow: var(--card-shadow);
    padding: 1rem;
    margin-top: 1rem;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.results-container {
    animation: fadeIn 0.6s ease-out;
    margin-top: 1rem;
}

.form-label {
    color: var(--text-muted);
    font-weight: 500;
}

@media (max-width: 768px) {
    .main-container {
        padding: 1rem;
    }
}
'''

# Initialize the Dash app with Bootstrap and custom CSS
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                index_string=f'''
                <!DOCTYPE html>
                <html>
                    <head>
                        {{%metas%}}
                        <title>Circular Building Structural Analysis</title>
                        {{%favicon%}}
                        {{%css%}}
                        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
                        <style>{CUSTOM_CSS}</style>
                    </head>
                    <body>
                        {{%app_entry%}}
                        <footer>
                            {{%config%}}
                            {{%scripts%}}
                            {{%renderer%}}
                        </footer>
                    </body>
                </html>
                ''')

# Set the layout of the app
app.layout = layout

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)