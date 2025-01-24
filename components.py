from dash import dcc, html
import dash_bootstrap_components as dbc
from config import MATERIAL_PROPERTIES, SEISMIC_ZONES, BEAM_PROPERTIES, COLUMN_PROPERTIES

# Use Dash Bootstrap Components for improved styling
layout = html.Div(
    className="main-container",
    children=[
        html.H2("Circular Building Structural Analysis"),
        
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Building Radius (m)"),
                    dbc.Input(id='building-radius', type='number', value=20, min=1, step=0.1, className='mb-2'),
                ], width=6, md=3),
                
                dbc.Col([
                    dbc.Label("Number of Columns"),
                    dbc.Input(id='num-columns', type='number', value=12, min=4, max=24, step=1, className='mb-2'),
                ], width=6, md=3),
                
                dbc.Col([
                    dbc.Label("Number of Floors"),
                    dbc.Input(id='num-floors', type='number', value=5, min=1, step=1, className='mb-2'),
                ], width=6, md=3),
                
                dbc.Col([
                    dbc.Label("Floor Height (m)"),
                    dbc.Input(id='floor-height', type='number', value=3, min=1, step=0.1, className='mb-2'),
                ], width=6, md=3),
            ], className='mb-3'),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Material for Structural Elements"),
                    dbc.Select(
                        id='material-type',
                        options=[
                            {'label': 'Concrete', 'value': 'concrete'},
                            {'label': 'Steel', 'value': 'steel'}
                        ],
                        value='concrete',
                        className='mb-2'
                    ),
                ], width=6, md=3),
                
                dbc.Col([
                    dbc.Label("Live Load (kN/m²)"),
                    dbc.Input(id='live-load', type='number', value=2, min=0, step=0.1, className='mb-2'),
                ], width=6, md=3),
                
                dbc.Col([
                    dbc.Label("Wind Speed (m/s)"),
                    dbc.Input(id='wind-speed', type='number', value=15, min=0, step=0.1, className='mb-2'),
                ], width=6, md=3),
                
                dbc.Col([
                    dbc.Label("Load Intensity (kN)"),
                    dcc.Slider(
                        id='load-intensity',
                        min=0,
                        max=100,
                        step=1,
                        value=50,
                        marks={i: str(i) for i in range(0, 101, 10)},
                        className='mb-2'
                    ),
                ], width=6, md=3),
            ], className='mb-3'),
            
            dbc.Row([
                dbc.Col([
                    dbc.Label("Beam Design"),
                    dbc.Select(
                        id='beam-design',
                        options=[
                            {'label': 'Rectangular', 'value': 'rectangular'},
                            {'label': 'T-Beam', 'value': 't-beam'},
                            {'label': 'I-Beam', 'value': 'i-beam'},
                            {'label': 'Circular', 'value': 'circular'}
                        ],
                        value='rectangular',
                        className='mb-2'
                    ),
                ], width=6, md=3),
                
                dbc.Col([
                    dbc.Label("Column Design"),
                    dbc.Select(
                        id='column-design',
                        options=[
                            {'label': 'Rectangular', 'value': 'rectangular'},
                            {'label': 'Circular', 'value': 'circular'},
                            {'label': 'Square', 'value': 'square'},
                            {'label': 'L-Shaped', 'value': 'l-shaped'}
                        ],
                        value='circular',
                        className='mb-2'
                    ),
                ], width=6, md=3),
                
                dbc.Col([
                    dbc.Button(
                        "Analyze", 
                        id='analyze-button', 
                        color="primary", 
                        className='w-100 mt-4'
                    ),
                ], width=12, md=6),
            ], className='mb-3'),
        ]),

        html.Div(
            id='analysis-results',
            className="results-container",
        ),

        html.Div(
            className="graph-container",
            children=[
                dcc.Graph(id='building-visualization')
            ]
        )
    ]
)