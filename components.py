from dash import dcc, html
from config import MATERIAL_PROPERTIES, SEISMIC_ZONES, BEAM_PROPERTIES, COLUMN_PROPERTIES

layout = html.Div([
    html.H1("Circular Building Structural Analysis", style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '30px'}),
    
    html.Div([
        html.Div([
            html.Div([
                html.Label("Building Radius (m)"),
                dcc.Input(id='building-radius', type='number', value=20, min=1, step=0.1, className='dash-input'),

                html.Label("Number of Columns"),
                dcc.Input(id='num-columns', type='number', value=12, min=4, max=24, step=1, className='dash-input'),

                html.Label("Number of Floors"),
                dcc.Input(id='num-floors', type='number', value=5, min=1, step=1, className='dash-input'),

                html.Label("Floor Height (m)"),
                dcc.Input(id='floor-height', type='number', value=3, min=1, step=0.1, className='dash-input'),

                html.Label("Material for Structural Elements"),
                dcc.Dropdown(
                    id='material-type',
                    options=[
                        {'label': 'Concrete', 'value': 'concrete'},
                        {'label': 'Steel', 'value': 'steel'}
                    ],
                    value='concrete',
                    className='dash-dropdown'
                ),

                html.Label("Live Load (kN/m²)"),
                dcc.Input(id='live-load', type='number', value=2, min=0, step=0.1, className='dash-input'),

                html.Label("Wind Speed (m/s)"),
                dcc.Input(id='wind-speed', type='number', value=15, min=0, step=0.1, className='dash-input'),

                html.Label("Beam Design"),
                dcc.Dropdown(
                    id='beam-design',
                    options=[
                        {'label': 'Rectangular', 'value': 'rectangular'},
                        {'label': 'T-Beam', 'value': 't-beam'},
                        {'label': 'I-Beam', 'value': 'i-beam'},
                        {'label': 'Circular', 'value': 'circular'}
                    ],
                    value='rectangular',
                    className='dash-dropdown'
                ),

                html.Label("Column Design"),
                dcc.Dropdown(
                    id='column-design',
                    options=[
                        {'label': 'Rectangular', 'value': 'rectangular'},
                        {'label': 'Circular', 'value': 'circular'},
                        {'label': 'Square', 'value': 'square'},
                        {'label': 'L-Shaped', 'value': 'l-shaped'}
                    ],
                    value='circular',
                    className='dash-dropdown'
                ),

                html.Label("Load Intensity (kN)"),
                dcc.Slider(
                    id='load-intensity',
                    min=0,
                    max=100,
                    step=1,
                    value=50,
                    marks={i: str(i) for i in range(0, 101, 10)},
                    className='dash-slider'
                ),

                html.Button("Analyze", id='analyze-button', n_clicks=0, className='analyze-button')
            ], className='input-container'),
        ], style={'width': '45%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        html.Div(id='analysis-results', style={'width': '50%', 'display': 'inline-block', 'paddingLeft': '20px'})
    ]),

    html.Div([
        dcc.Graph(id='building-visualization', style={'marginTop': '20px'})
    ], className='graph-container')
])