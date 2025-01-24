import dash
from dash import Input, Output, State, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import math
from config import MATERIAL_PROPERTIES, BEAM_PROPERTIES, COLUMN_PROPERTIES, SEISMIC_ZONES
from utils import calculate_seismic_load, calculate_wind_load, calculate_beam_properties, calculate_column_properties, get_material_standards
import logging

# Initialize logging
logging.basicConfig(filename='circular_building_analysis.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def register_callbacks(app):
    @app.callback(
        [Output('building-visualization', 'figure'),
         Output('analysis-results', 'children')],
        [Input('analyze-button', 'n_clicks'),
         Input('deformation-toggle', 'value')],  # Toggle for deformation
        [State('building-radius', 'value'),
         State('num-columns', 'value'),
         State('num-floors', 'value'),
         State('floor-height', 'value'),
         State('material-type', 'value'),
         State('live-load', 'value'),
         State('wind-speed', 'value'),
         State('seismic-zone', 'value'),
         State('beam-design', 'value'),
         State('column-design', 'value'),
         State('load-intensity', 'value')]
    )
    def analyze_structure(n_clicks, show_deformation, radius, num_columns, num_floors, floor_height, material_type, 
                         live_load, wind_speed, seismic_zone, beam_design, column_design, load_intensity):
        # Validate inputs
        if None in [radius, num_columns, num_floors, floor_height, material_type, live_load, 
                    wind_speed, seismic_zone, beam_design, column_design, load_intensity]:
            return dash.no_update, "Please fill in all fields."
        
        if radius <= 0 or num_columns <= 0 or num_floors <= 0 or floor_height <= 0 or live_load < 0 or wind_speed < 0:
            return dash.no_update, "Invalid input values: radius, num_columns, num_floors, floor_height must be positive, and live_load, wind_speed must be non-negative."
        
        try:
            # Fetch material properties
            material = MATERIAL_PROPERTIES[material_type]
            
            # Calculate total height and live load
            total_height = num_floors * floor_height
            total_live_load = live_load * math.pi * radius**2 * num_floors
            
            # Calculate wind force
            wind_force = calculate_wind_load(radius, total_height, wind_speed)
            
            # Calculate seismic load
            zone_factor = SEISMIC_ZONES[seismic_zone]['zone_factor']
            total_weight = total_live_load + (material['density'] * math.pi * radius**2 * total_height)  # Total weight = live load + self-weight
            seismic_load = calculate_seismic_load(zone_factor, total_weight, total_height)
            
            # Calculate beam span length based on number of columns
            beam_span = 2 * radius * math.sin(math.pi / num_columns)
            
            # Calculate beam and column properties
            beam_props = calculate_beam_properties(beam_design, beam_span, material)
            column_props = calculate_column_properties(column_design, floor_height, material)
            
            # Create 3D visualization
            fig = go.Figure()

            # Add columns with hover information and stress distribution
            theta_columns = np.linspace(0, 2 * np.pi, num_columns, endpoint=False)
            for angle in theta_columns:
                x_col = radius * np.cos(angle)
                y_col = radius * np.sin(angle)
                
                # Calculate stress based on load intensity and angle
                stress = load_intensity * (1 + np.sin(angle))  # Example stress calculation
                strain = stress / material['elastic_modulus']  # Calculate strain
                color_scale = stress / 100  # Normalize stress for color gradient

                hover_text = f"""
                Column Properties:<br>
                {column_props['dimensions']}<br>
                Cross-sectional Area: {column_props['area']}<br>
                Moment of Inertia: {column_props['moment_of_inertia']}<br>
                Maximum Axial Load: {column_props['max_axial_load']}<br>
                Slenderness Ratio: {column_props['slenderness_ratio']}<br>
                Material: {material_type.capitalize()}<br>
                Height: {floor_height}m<br>
                Stress: {stress:.2f} kN/m²<br>
                Strain: {strain:.6f}
                """

                fig.add_trace(go.Scatter3d(
                    x=[x_col, x_col],
                    y=[y_col, y_col],
                    z=[0, total_height],
                    mode='lines',
                    line=dict(color=color_scale, width=5, colorscale='Viridis'),  # Use color gradient
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

                    # Calculate stress based on load intensity and angle
                    stress = load_intensity * (1 + np.cos(angle1))  # Example stress calculation
                    strain = stress / material['elastic_modulus']  # Calculate strain
                    color_scale = stress / 100  # Normalize stress for color gradient

                    hover_text = f"""
                    Beam Properties:<br>
                    {beam_props['dimensions']}<br>
                    Cross-sectional Area: {beam_props['area']}<br>
                    Moment of Inertia: {beam_props['moment_of_inertia']}<br>
                    Maximum Bending Moment: {beam_props['max_bending_moment']}<br>
                    Span Length: {beam_props['span_length']}<br>
                    Material: {material_type.capitalize()}<br>
                    Floor Level: {z_beam}m<br>
                    Stress: {stress:.2f} kN/m²<br>
                    Strain: {strain:.6f}
                    """

                    fig.add_trace(go.Scatter3d(
                        x=[x_beam_start, x_beam_end],
                        y=[y_beam_start, y_beam_end],
                        z=[z_beam, z_beam],
                        mode='lines',
                        line=dict(color=color_scale, width=5, colorscale='Viridis'),  # Use color gradient
                        name=f'{beam_design.capitalize()} Beam',
                        hovertemplate=hover_text,
                        showlegend=False
                    ))

            # Add transparent surfaces for floors
            for floor in range(num_floors + 1):  # +1 to include roof
                z_floor = floor * floor_height
                theta = np.linspace(0, 2*np.pi, 100)
                x_floor = np.concatenate([radius * np.cos(theta), [0]])  # Add center point
                y_floor = np.concatenate([radius * np.sin(theta), [0]])  # Add center point
                z_floor_array = np.array([z_floor] * (len(theta) + 1))  # Adjust array length
                
                fig.add_trace(go.Mesh3d(
                    x=x_floor,
                    y=y_floor,
                    z=[z_floor] * len(theta),
                    opacity=0.3,
                    color='lightgray',
                    hoverinfo='skip',
                    showlegend=False
                ))

            # Add a color bar legend for stress
            fig.update_layout(
                coloraxis=dict(
                    colorscale='Viridis',
                    colorbar=dict(
                        title='Stress (kN/m²)',
                        thickness=20,
                        len=0.75,
                        x=0.9,
                        y=0.5,
                    )
                )
            )

            # Deformation visualization
            if show_deformation:
                deformation_factor = 0.1  # Scale factor for deformation
                for angle in theta_columns:
                    x_col = radius * np.cos(angle)
                    y_col = radius * np.sin(angle)
                    displacement = deformation_factor * np.sin(angle)  # Example deformation
                    
                    fig.add_trace(go.Scatter3d(
                        x=[x_col + displacement, x_col + displacement],
                        y=[y_col + displacement, y_col + displacement],
                        z=[0, total_height],
                        mode='lines',
                        line=dict(color='orange', width=5),
                        name=f'Deformed {column_design.capitalize()} Column',
                        hovertemplate="Deformed Column",
                        showlegend=False
                    ))

                for floor in range(num_floors):
                    z_beam = floor * floor_height
                    for i in range(len(theta_columns)):
                        angle1 = theta_columns[i]
                        angle2 = theta_columns[(i + 1) % len(theta_columns)]
                        
                        x1 = radius * np.cos(angle1) + deformation_factor * np.sin(angle1)
                        y1 = radius * np.sin(angle1) + deformation_factor * np.sin(angle1)
                        x2 = radius * np.cos(angle2) + deformation_factor * np.sin(angle2)
                        y2 = radius * np.sin(angle2) + deformation_factor * np.sin(angle2)
                        
                        fig.add_trace(go.Scatter3d(
                            x=[x1, x2],
                            y=[y1, y2],
                            z=[z_beam, z_beam],
                            mode='lines',
                            line=dict(color='orange', width=5),
                            name=f'Deformed {beam_design.capitalize()} Beam',
                            hovertemplate="Deformed Beam",
                            showlegend=False
                        ))

            # Animation logic (same as before)
            frames = []
            for t in np.linspace(0, 2 * np.pi, 30):
                frame_data = []
                
                # Animate columns
                for angle in theta_columns:
                    x_col = radius * np.cos(angle)
                    y_col = radius * np.sin(angle)
                    displacement = 0.05 * np.sin(t) * radius  # Small lateral displacement
                    
                    frame_data.append(
                        go.Scatter3d(
                            x=[x_col + displacement * np.cos(angle), x_col + displacement * np.cos(angle)],
                            y=[y_col + displacement * np.sin(angle), y_col + displacement * np.sin(angle)],
                            z=[0, total_height],
                            mode='lines',
                            line=dict(color='blue', width=5),
                            showlegend=False
                        )
                    )
                
                # Add beams for each floor
                for floor in range(num_floors):
                    z_beam = floor * floor_height
                    for i in range(len(theta_columns)):
                        angle1 = theta_columns[i]
                        angle2 = theta_columns[(i + 1) % len(theta_columns)]
                        
                        x1 = radius * np.cos(angle1) + displacement * np.cos(angle1)
                        y1 = radius * np.sin(angle1) + displacement * np.sin(angle1)
                        x2 = radius * np.cos(angle2) + displacement * np.cos(angle2)
                        y2 = radius * np.sin(angle2) + displacement * np.sin(angle2)
                        
                        frame_data.append(
                            go.Scatter3d(
                                x=[x1, x2],
                                y=[y1, y2],
                                z=[z_beam, z_beam],
                                mode='lines',
                                line=dict(color='red', width=5),
                                showlegend=False
                            )
                        )
                
                frames.append(go.Frame(data=frame_data, name=f'frame_{t}'))

            # Update animation settings
            fig.update_layout(
                updatemenus=[{
                    'type': 'buttons',
                    'showactive': False,
                    'buttons': [{
                        'label': 'Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 50, 'redraw': True},
                            'fromcurrent': True,
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }, {
                        'label': 'Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }]
                }],
                sliders=[{
                    'currentvalue': {'prefix': 'Time: '},
                    'pad': {'t': 50},
                    'len': 0.9,
                    'x': 0.1,
                    'xanchor': 'left',
                    'y': 0,
                    'yanchor': 'top',
                    'steps': [{
                        'args': [[f.name], {
                            'frame': {'duration': 0, 'redraw': True},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }],
                        'label': str(k),
                        'method': 'animate'
                    } for k, f in enumerate(frames)]
                }]
            )

            fig.frames = frames

            # Get material standards recommendation
            standards_recommendation = get_material_standards(radius, num_floors, floor_height, wind_speed, live_load)

            results = dbc.Container([
                html.H3("Analysis Results", className="mb-4"),
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Building Parameters"),
                            dbc.CardBody([
                                html.P(f"Total Height: {total_height:.2f} m"),
                                html.P(f"Number of Floors: {num_floors}"),
                                html.P(f"Number of Columns: {num_columns}"),
                                html.P(f"Floor Height: {floor_height} m"),
                                html.P(f"Building Radius: {radius} m"),
                            ])
                        ], className="mb-3")
                    ], width=6, md=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Loading Information"),
                            dbc.CardBody([
                                html.P(f"Total Live Load: {total_live_load/1000:.2f} kN"),
                                html.P(f"Live Load per Floor: {live_load} kN/m²"),
                                html.P(f"Total Wind Force: {wind_force/1000:.2f} kN"),
                                html.P(f"Wind Speed: {wind_speed} m/s"),
                                html.P(f"Seismic Load: {seismic_load/1000:.2f} kN"),
                                html.P(f"Seismic Zone: {seismic_zone}"),
                            ])
                        ], className="mb-3")
                    ], width=6, md=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Structural Details"),
                            dbc.CardBody([
                                html.P(f"Material: {material_type.capitalize()}"),
                                html.P(f"Beam Type: {beam_design.capitalize()}"),
                                html.P(f"Column Type: {column_design.capitalize()}"),
                                dbc.Alert(
                                    "Hover over beams and columns in the 3D model to see detailed structural properties", 
                                    color="info", 
                                    className="mt-3"
                                )
                            ])
                        ], className="mb-3")
                    ], width=6, md=3),
                    
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader("Material Standards Analysis"),
                            dbc.CardBody([
                                html.Pre(standards_recommendation)
                            ])
                        ], className="mb-3")
                    ], width=6, md=3)
                ])
            ], fluid=True)

            return fig, results

        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            return dash.no_update, f"Error: {str(e)}"