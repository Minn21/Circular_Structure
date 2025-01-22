import dash
from dash import dcc, html, Input, Output, State
import math
import numpy as np
import pandas as pd
import logging
import plotly.graph_objects as go

# Initialize logging
logging.basicConfig(filename='circular_building_analysis.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = dash.Dash(__name__)

# Enhanced Material Properties with costs
MATERIAL_PROPERTIES = {
    'concrete': {
        'density': 2400,  # kg/m^3
        'elastic_modulus': 25e9,  # Pa
        'yield_strength': 30e6,  # Pa
        'poisson_ratio': 0.2,
        'cost_per_m3': 100  # USD/m^3
    },
    'steel': {
        'density': 7850,  # kg/m^3
        'elastic_modulus': 200e9,  # Pa
        'yield_strength': 250e6,  # Pa
        'poisson_ratio': 0.3,
        'cost_per_m3': 2000  # USD/m^3
    },
    'composite': {
        'density': 3000,  # kg/m^3
        'elastic_modulus': 30e9,  # Pa
        'yield_strength': 40e6,  # Pa
        'poisson_ratio': 0.25,
        'cost_per_m3': 150  # USD/m^3
    }
}

# Add seismic zone parameters
SEISMIC_ZONES = {
    'Zone I': {'zone_factor': 0.1, 'description': 'Very Low Damage Risk Zone'},
    'Zone II': {'zone_factor': 0.16, 'description': 'Low Damage Risk Zone'},
    'Zone III': {'zone_factor': 0.24, 'description': 'Moderate Damage Risk Zone'},
    'Zone IV': {'zone_factor': 0.36, 'description': 'High Damage Risk Zone'},
    'Zone V': {'zone_factor': 0.48, 'description': 'Very High Damage Risk Zone'}
}

# Define structural element properties based on design type
BEAM_PROPERTIES = {
    'rectangular': {
        'min_width': 0.2,  # m
        'min_height': 0.4,  # m
        'max_width': 0.5,  # m
        'max_height': 0.8,  # m
        'area': lambda w, h: w * h,
        'moment_of_inertia': lambda w, h: (w * h**3) / 12,
        'get_dimensions': lambda span: {
            'width': min(0.2 + span/20, 0.5),
            'height': min(0.4 + span/15, 0.8)
        }
    },
    't-beam': {
        'min_web_width': 0.2,
        'max_web_width': 0.4,
        'min_web_height': 0.4,
        'max_web_height': 0.7,
        'min_flange_width': 0.4,
        'max_flange_width': 0.8,
        'min_flange_height': 0.15,
        'max_flange_height': 0.25,
        'area': lambda ww, wh, fw, fh: ww * wh + fw * fh,
        'moment_of_inertia': lambda ww, wh, fw, fh: (ww * wh**3) / 12 + fw * fh**3 / 12,
        'get_dimensions': lambda span: {
            'web_width': min(0.2 + span/30, 0.4),
            'web_height': min(0.4 + span/15, 0.7),
            'flange_width': min(0.4 + span/15, 0.8),
            'flange_height': min(0.15 + span/40, 0.25)
        }
    },
    'i-beam': {
        'min_web_width': 0.15,
        'max_web_width': 0.3,
        'min_web_height': 0.3,
        'max_web_height': 0.6,
        'min_flange_width': 0.3,
        'max_flange_width': 0.6,
        'min_flange_height': 0.12,
        'max_flange_height': 0.2,
        'area': lambda ww, wh, fw, fh: ww * wh + 2 * fw * fh,
        'moment_of_inertia': lambda ww, wh, fw, fh: (ww * wh**3) / 12 + 2 * (fw * fh**3) / 12,
        'get_dimensions': lambda span: {
            'web_width': min(0.15 + span/35, 0.3),
            'web_height': min(0.3 + span/15, 0.6),
            'flange_width': min(0.3 + span/20, 0.6),
            'flange_height': min(0.12 + span/45, 0.2)
        }
    },
    'circular': {
        'min_diameter': 0.3,
        'max_diameter': 0.6,
        'area': lambda d: math.pi * (d/2)**2,
        'moment_of_inertia': lambda d: math.pi * d**4 / 64,
        'get_dimensions': lambda span: {
            'diameter': min(0.3 + span/20, 0.6)
        }
    }
}

COLUMN_PROPERTIES = {
    'rectangular': {
        'width': 0.4,  # m
        'depth': 0.4,  # m
        'area': lambda w, d: w * d,
        'moment_of_inertia': lambda w, d: (w * d**3) / 12
    },
    'circular': {
        'diameter': 0.5,  # m
        'area': lambda d: math.pi * (d/2)**2,
        'moment_of_inertia': lambda d: math.pi * d**4 / 64
    },
    'square': {
        'width': 0.45,  # m
        'area': lambda w: w**2,
        'moment_of_inertia': lambda w: w**4 / 12
    },
    'l-shaped': {
        'width': 0.4,  # m
        'depth': 0.4,  # m
        'thickness': 0.1,  # m
        'area': lambda w, d, t: (w + d - t) * t,
        'moment_of_inertia': lambda w, d, t: (t * (w**3 + d**3)) / 3
    }
}

def calculate_seismic_load(zone_factor, total_weight, total_height, importance_factor=1.0, response_reduction=3.0):
    """Calculate seismic base shear using equivalent static method."""
    # Approximate fundamental period
    height_factor = 0.075  # for RC frame building
    time_period = height_factor * (total_height ** 0.75)
    
    # Design horizontal seismic coefficient
    if time_period <= 0.5:
        sa_by_g = 2.5
    else:
        sa_by_g = 1.25 / max(time_period, 0.01)  # Avoid division by zero
    
    ah = (zone_factor * importance_factor * sa_by_g) / (2 * response_reduction)
    
    # Base shear calculation
    base_shear = ah * total_weight
    return base_shear

def calculate_wind_load(radius, height, wind_speed, shape_factor=1.2, gust_factor=1.0):
    """Calculate wind load on the building."""
    air_density = 1.225  # kg/m^3
    area = 2 * np.pi * radius * height
    dynamic_pressure = 0.5 * air_density * wind_speed**2
    wind_force = dynamic_pressure * area * shape_factor * gust_factor
    return wind_force

def get_material_standards(radius, num_floors, floor_height, wind_speed, live_load):
    """Determine suitable materials and their standards based on structural parameters."""
    if radius <= 0 or num_floors <= 0 or floor_height <= 0:
        return "Invalid input parameters: radius, num_floors, and floor_height must be positive."

    # Define standard codes and material properties for different regions
    STANDARDS = {
        'United_States': {
            'concrete': {
                'code': 'ACI 318',
                'strength_range': (20, 80),  # MPa
                'typical_strength': 30
            },
            'steel': {
                'code': 'AISC 360',
                'grades': {'ASTM A36': 250, 'ASTM A992': 345}  # MPa
            }
        },
        'Europe': {
            'concrete': {
                'code': 'EN 1992',
                'strength_classes': ['C20/25', 'C30/37', 'C40/50'],
                'typical_strength': 30
            },
            'steel': {
                'code': 'EN 1993',
                'grades': {'S235': 235, 'S355': 355}
            }
        }
    }

    # Calculate basic structural parameters
    total_height = num_floors * floor_height
    span_length = 2 * radius * np.sin(np.pi / 12)  # Assuming 12 columns
    wind_force = calculate_wind_load(radius, total_height, wind_speed)

    def analyze_requirements():
        # Structural requirement analysis
        requirements = {
            'high_strength_needed': False,
            'large_spans': False,
            'high_wind_load': False
        }
        
        # Check for high strength requirements
        if num_floors > 10 or live_load > 5:
            requirements['high_strength_needed'] = True
            
        # Check for large spans
        if radius > 15:
            requirements['large_spans'] = True
            
        # Check for high wind loads
        if wind_force > 100000:  # 100 kN threshold
            requirements['high_wind_load'] = True
            
        return requirements

    def recommend_material_and_standard(reqs):
        recommendations = []
        
        if reqs['large_spans'] or reqs['high_wind_load']:
            # Recommend steel for large spans or high wind loads
            steel_rec = {
                'material': 'Steel',
                'primary_standard': STANDARDS['United_States']['steel']['code'],
                'alternative_standard': STANDARDS['Europe']['steel']['code'],
                'recommended_grades': []
            }
            
            if reqs['high_strength_needed']:
                steel_rec['recommended_grades'].extend(['ASTM A992', 'S355'])
            else:
                steel_rec['recommended_grades'].extend(['ASTM A36', 'S235'])
                
            recommendations.append(steel_rec)
            
        else:
            # Recommend concrete for normal conditions
            concrete_rec = {
                'material': 'Concrete',
                'primary_standard': STANDARDS['United_States']['concrete']['code'],
                'alternative_standard': STANDARDS['Europe']['concrete']['code'],
                'strength_class': []
            }
            
            if reqs['high_strength_needed']:
                concrete_rec['strength_class'].extend(['C40/50', 'M40'])
            else:
                concrete_rec['strength_class'].extend(['C30/37', 'M30'])
                
            recommendations.append(concrete_rec)
            
        return recommendations

    def format_recommendations(recommendations):
        output = []
        output.append("\nSTRUCTURAL ANALYSIS RESULTS")
        output.append("=" * 50)
        
        for rec in recommendations:
            output.append(f"\nRecommended Material: {rec.get('material', 'N/A')}")
            output.append(f"Primary Standard Code: {rec.get('primary_standard', 'N/A')}")
            output.append(f"Alternative Standard: {rec.get('alternative_standard', 'N/A')}")
            
            if 'recommended_grades' in rec:
                output.append("Recommended Grades:")
                for grade in rec['recommended_grades']:
                    output.append(f"  - {grade}")
            
            if 'strength_class' in rec:
                output.append("Recommended Strength Classes:")
                for strength in rec['strength_class']:
                    output.append(f"  - {strength}")
                    
        return "\n".join(output)

    # Execute analysis and get recommendations
    requirements = analyze_requirements()
    recommendations = recommend_material_and_standard(requirements)
    return format_recommendations(recommendations)

def calculate_beam_properties(beam_design, span_length, material):
    """Calculate beam properties based on design type and span length."""
    if span_length <= 0:
        return "Invalid span length: must be positive."
    
    props = BEAM_PROPERTIES[beam_design]
    dims = props['get_dimensions'](span_length)
    
    if beam_design == 'rectangular':
        width = dims['width']
        height = dims['height']
        if width < props['min_width'] or width > props['max_width'] or height < props['min_height'] or height > props['max_height']:
            return "Invalid beam dimensions: width or height out of range."
        area = props['area'](width, height)
        inertia = props['moment_of_inertia'](width, height)
        dims_str = f"Width: {width:.2f}m x Height: {height:.2f}m"
        max_moment = material['yield_strength'] * inertia / (height/2)
    elif beam_design in ['t-beam', 'i-beam']:
        web_width = dims['web_width']
        web_height = dims['web_height']
        flange_width = dims['flange_width']
        flange_height = dims['flange_height']
        if web_width < props['min_web_width'] or web_width > props['max_web_width'] or web_height < props['min_web_height'] or web_height > props['max_web_height'] or flange_width < props['min_flange_width'] or flange_width > props['max_flange_width'] or flange_height < props['min_flange_height'] or flange_height > props['max_flange_height']:
            return "Invalid beam dimensions: web or flange dimensions out of range."
        area = props['area'](web_width, web_height, flange_width, flange_height)
        inertia = props['moment_of_inertia'](web_width, web_height, flange_width, flange_height)
        dims_str = f"Web: {web_width:.2f}x{web_height:.2f}m, Flange: {flange_width:.2f}x{flange_height:.2f}m"
        max_moment = material['yield_strength'] * inertia / (web_height/2)
    else:  # circular
        diameter = dims['diameter']
        if diameter < props['min_diameter'] or diameter > props['max_diameter']:
            return "Invalid beam dimensions: diameter out of range."
        area = props['area'](diameter)
        inertia = props['moment_of_inertia'](diameter)
        dims_str = f"Diameter: {diameter:.2f}m"
        max_moment = material['yield_strength'] * inertia / (diameter/2)
    
    return {
        'dimensions': dims_str,
        'area': f"{area:.3f} m²",
        'moment_of_inertia': f"{inertia:.6f} m⁴",
        'max_bending_moment': f"{max_moment/1000:.1f} kN·m",
        'span_length': f"{span_length:.2f} m"
    }

def calculate_column_properties(column_design, height, material):
    """Calculate column properties based on design type and height."""
    if height <= 0:
        return "Invalid height: must be positive."
    
    props = COLUMN_PROPERTIES[column_design]
    if column_design == 'rectangular':
        width = props['width']
        depth = props['depth']
        area = props['area'](width, depth)
        inertia = props['moment_of_inertia'](width, depth)
        dims = f"Width: {width}m x Depth: {depth}m"
        min_dim = min(width, depth)
    elif column_design == 'circular':
        diameter = props['diameter']
        area = props['area'](diameter)
        inertia = props['moment_of_inertia'](diameter)
        dims = f"Diameter: {diameter}m"
        min_dim = diameter
    elif column_design == 'square':
        width = props['width']
        area = props['area'](width)
        inertia = props['moment_of_inertia'](width)
        dims = f"Width: {width}m"
        min_dim = width
    else:  # l-shaped
        width = props['width']
        depth = props['depth']
        thickness = props['thickness']
        area = props['area'](width, depth, thickness)
        inertia = props['moment_of_inertia'](width, depth, thickness)
        dims = f"Width: {width}m x Depth: {depth}m x Thickness: {thickness}m"
        min_dim = thickness
    
    max_load = material['yield_strength'] * area
    slenderness = height / min_dim
    
    return {
        'dimensions': dims,
        'area': f"{area:.3f} m²",
        'moment_of_inertia': f"{inertia:.6f} m⁴",
        'max_axial_load': f"{max_load/1000:.1f} kN",
        'slenderness_ratio': f"{slenderness:.1f}"
    }

app.layout = html.Div([
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

# Modify the callback to include load intensity and stress distribution
@app.callback(
    [Output('building-visualization', 'figure'),
     Output('analysis-results', 'children')],
    [Input('analyze-button', 'n_clicks')],
    [State('building-radius', 'value'),
     State('num-columns', 'value'),
     State('num-floors', 'value'),
     State('floor-height', 'value'),
     State('material-type', 'value'),
     State('live-load', 'value'),
     State('wind-speed', 'value'),
     State('beam-design', 'value'),
     State('column-design', 'value'),
     State('load-intensity', 'value')]
)
def analyze_structure(n_clicks, radius, num_columns, num_floors, floor_height, material_type, 
                     live_load, wind_speed, beam_design, column_design, load_intensity):
    if None in [radius, num_columns, num_floors, floor_height, material_type, live_load, 
                wind_speed, beam_design, column_design, load_intensity]:
        return dash.no_update, "Please fill in all fields."
    
    if radius <= 0 or num_columns <= 0 or num_floors <= 0 or floor_height <= 0 or live_load < 0 or wind_speed < 0:
        return dash.no_update, "Invalid input values: radius, num_columns, num_floors, floor_height must be positive, and live_load, wind_speed must be non-negative."
    
    try:
        material = MATERIAL_PROPERTIES[material_type]
        total_height = num_floors * floor_height
        total_live_load = live_load * math.pi * radius**2 * num_floors
        wind_force = calculate_wind_load(radius, total_height, wind_speed)

        # Get material standards recommendations
        standards_recommendation = get_material_standards(
            radius, num_floors, floor_height, wind_speed, live_load
        )

        # Calculate beam span length based on number of columns
        beam_span = 2 * radius * math.sin(math.pi / num_columns)
        beam_props = calculate_beam_properties(beam_design, beam_span, material)
        column_props = calculate_column_properties(column_design, floor_height, material)

        fig = go.Figure()

        # Add columns with hover information and stress distribution
        theta_columns = np.linspace(0, 2 * np.pi, num_columns, endpoint=False)
        for angle in theta_columns:
            x_col = radius * np.cos(angle)
            y_col = radius * np.sin(angle)
            
            # Calculate stress based on load intensity
            stress = load_intensity * (1 + np.sin(angle))  # Example stress calculation

            hover_text = f"""
            Column Properties:<br>
            {column_props['dimensions']}<br>
            Cross-sectional Area: {column_props['area']}<br>
            Moment of Inertia: {column_props['moment_of_inertia']}<br>
            Maximum Axial Load: {column_props['max_axial_load']}<br>
            Slenderness Ratio: {column_props['slenderness_ratio']}<br>
            Material: {material_type.capitalize()}<br>
            Height: {floor_height}m<br>
            Stress: {stress:.2f} kN/m²
            """

            fig.add_trace(go.Scatter3d(
                x=[x_col, x_col],
                y=[y_col, y_col],
                z=[0, total_height],
                mode='lines',
                line=dict(color='blue', width=5),
                name=f'{column_design.capitalize()} Column',
                hovertemplate=hover_text,
                showlegend=False
            ))

        # Add beams with hover information and stress distribution
        for floor in range(num_floors):
            z_beam = floor * floor_height
            for i in range(len(theta_columns)):
                angle1 = theta_columns[i]
                angle2 = theta_columns[(i + 1) % len(theta_columns)]

                x_beam_start, y_beam_start = radius * np.cos(angle1), radius * np.sin(angle1)
                x_beam_end, y_beam_end = radius * np.cos(angle2), radius * np.sin(angle2)

                # Calculate stress based on load intensity
                stress = load_intensity * (1 + np.cos(angle1))  # Example stress calculation

                hover_text = f"""
                Beam Properties:<br>
                {beam_props['dimensions']}<br>
                Cross-sectional Area: {beam_props['area']}<br>
                Moment of Inertia: {beam_props['moment_of_inertia']}<br>
                Maximum Bending Moment: {beam_props['max_bending_moment']}<br>
                Span Length: {beam_props['span_length']}<br>
                Material: {material_type.capitalize()}<br>
                Floor Level: {z_beam}m<br>
                Stress: {stress:.2f} kN/m²
                """

                fig.add_trace(go.Scatter3d(
                    x=[x_beam_start, x_beam_end],
                    y=[y_beam_start, y_beam_end],
                    z=[z_beam, z_beam],
                    mode='lines',
                    line=dict(color='red', width=5),
                    name=f'{beam_design.capitalize()} Beam',
                    hovertemplate=hover_text,
                    showlegend=False
                ))

        # Add transparent surfaces for floors
        for floor in range(num_floors + 1):  # +1 to include roof
            z_floor = floor * floor_height
            theta = np.linspace(0, 2*np.pi, 100)
            x_floor = radius * np.cos(theta)
            y_floor = radius * np.sin(theta)
            
            fig.add_trace(go.Mesh3d(
                x=x_floor,
                y=y_floor,
                z=[z_floor] * len(theta),
                opacity=0.3,
                color='lightgray',
                hoverinfo='skip',
                showlegend=False
            ))

        # Add animation for wind/seismic effects
        frames = []
        for t in np.linspace(0, 2 * np.pi, 30):
            frame = go.Frame(
                data=[
                    go.Scatter3d(
                        x=[x_col, x_col],
                        y=[y_col, y_col],
                        z=[0, total_height * (1 + 0.1 * np.sin(t))],  # Example deformation
                        mode='lines',
                        line=dict(color='blue', width=5),
                        showlegend=False
                    )
                    for angle in theta_columns
                ],
                name=f'frame_{t}'
            )
            frames.append(frame)

        fig.update_layout(
            title="Circular Building Visualization with Structural Properties",
            scene=dict(
                xaxis_title='X (m)',
                yaxis_title='Y (m)',
                zaxis_title='Height (m)',
                aspectmode='data',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=0.8)  # Adjust the camera view for better perspective
                ),
                bgcolor='#f0f2f5'  # Light background for better contrast
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Arial"
            ),
            showlegend=True,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            updatemenus=[dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 100, "redraw": True}, "fromcurrent": True}]
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate", "transition": {"duration": 0}}]
                    )
                ]
            )]
        )

        fig.frames = frames

        results = html.Div([
            html.H3("Analysis Results"),
            html.Div([
                html.Div([
                    html.H4("Building Parameters"),
                    html.P(f"Total Height: {total_height:.2f} m"),
                    html.P(f"Number of Floors: {num_floors}"),
                    html.P(f"Number of Columns: {num_columns}"),
                    html.P(f"Floor Height: {floor_height} m"),
                    html.P(f"Building Radius: {radius} m"),
                    html.P(f"Beam Span Length: {beam_span:.2f} m"),
                ], className='results-section'),
                
                html.Div([
                    html.H4("Loading Information"),
                    html.P(f"Total Live Load: {total_live_load/1000:.2f} kN"),
                    html.P(f"Live Load per Floor: {live_load} kN/m²"),
                    html.P(f"Total Wind Force: {wind_force/1000:.2f} kN"),
                    html.P(f"Wind Speed: {wind_speed} m/s"),
                ], className='results-section'),
                
                html.Div([
                    html.H4("Structural Details"),
                    html.P(f"Material: {material_type.capitalize()}"),
                    html.P(f"Beam Type: {beam_design.capitalize()}"),
                    html.P(f"Column Type: {column_design.capitalize()}"),
                    html.Hr(),
                    html.P("Hover over beams and columns in the 3D model to see detailed structural properties", 
                          style={'fontStyle': 'italic', 'color': '#666'})
                ], className='results-section'),

                html.Div([
                    html.H4("Material Standards Analysis"),
                    html.Pre(standards_recommendation)
                ], className='results-section')
            ], style={'display': 'flex', 'justifyContent': 'space-between', 'flexWrap': 'wrap'})
        ], style={'backgroundColor': '#f5f5f5', 'padding': '20px', 'borderRadius': '5px'})

        return fig, results

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        return dash.no_update, f"Error: {str(e)}"

# Add custom CSS for better styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Circular Building Structural Analysis</title>
        {%favicon%}
        {%css%}
        <style>
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin: 0;
        padding: 20px;
        background-color: #f0f2f5;
    }
    .results-section {
        flex: 1;
        min-width: 300px;
        margin: 10px;
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .results-section:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    h1, h3, h4 {
        color: #2c3e50;
        margin-bottom: 15px;
    }
    h1 {
        font-size: 2.5em;
        font-weight: 600;
    }
    h3 {
        font-size: 1.8em;
        font-weight: 500;
    }
    h4 {
        font-size: 1.4em;
        font-weight: 500;
    }
    .dash-dropdown {
        margin-bottom: 20px;
    }
    .dash-input {
        margin-bottom: 20px;
    }
    label {
        color: #34495e;
        font-weight: bold;
        margin-top: 15px;
        display: block;
        font-size: 1.1em;
    }
    button {
        background-color: #3498db;
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        margin-top: 25px;
        font-size: 1.1em;
        transition: background-color 0.3s;
    }
    button:hover {
        background-color: #2980b9;
    }
    .input-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .graph-container {
        margin-top: 30px;
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=False, port=8052)