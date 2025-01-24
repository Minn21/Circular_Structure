import streamlit as st
import numpy as np
import plotly.graph_objects as go
from config import MATERIAL_PROPERTIES, SEISMIC_ZONES, BEAM_PROPERTIES, COLUMN_PROPERTIES
from utils import calculate_seismic_load, calculate_wind_load, calculate_beam_properties, calculate_column_properties, get_material_standards

# Streamlit app
st.title("Circular Building Structural Analysis")

# Input fields
st.sidebar.header("Building Parameters")
radius = st.sidebar.number_input("Building Radius (m)", min_value=1.0, value=20.0, step=0.1)
num_columns = st.sidebar.number_input("Number of Columns", min_value=4, max_value=24, value=12, step=1)
num_floors = st.sidebar.number_input("Number of Floors", min_value=1, value=5, step=1)
floor_height = st.sidebar.number_input("Floor Height (m)", min_value=1.0, value=3.0, step=0.1)

st.sidebar.header("Material and Load Parameters")
material_type = st.sidebar.selectbox("Material for Structural Elements", options=list(MATERIAL_PROPERTIES.keys()), index=0)
live_load = st.sidebar.number_input("Live Load (kN/m²)", min_value=0.0, value=2.0, step=0.1)
wind_speed = st.sidebar.number_input("Wind Speed (m/s)", min_value=0.0, value=15.0, step=0.1)
seismic_zone = st.sidebar.selectbox("Seismic Zone", options=list(SEISMIC_ZONES.keys()), index=0)
load_intensity = st.sidebar.slider("Load Intensity (kN)", min_value=0, max_value=100, value=50, step=1)
beam_design = st.sidebar.selectbox("Beam Design", options=list(BEAM_PROPERTIES.keys()), index=0)
column_design = st.sidebar.selectbox("Column Design", options=list(COLUMN_PROPERTIES.keys()), index=1)
show_deformation = st.sidebar.checkbox("Show Deformation", value=False)

# Analyze button
if st.sidebar.button("Analyze"):
    # Fetch material properties
    material = MATERIAL_PROPERTIES[material_type]
    
    # Calculate total height and live load
    total_height = num_floors * floor_height
    total_live_load = live_load * np.pi * radius**2 * num_floors
    
    # Calculate wind force
    wind_force = calculate_wind_load(radius, total_height, wind_speed)
    
    # Calculate seismic load
    zone_factor = SEISMIC_ZONES[seismic_zone]['zone_factor']
    total_weight = total_live_load + (material['density'] * np.pi * radius**2 * total_height)  # Total weight = live load + self-weight
    seismic_load = calculate_seismic_load(zone_factor, total_weight, total_height)
    
    # Calculate beam span length based on number of columns
    beam_span = 2 * radius * np.sin(np.pi / num_columns)
    
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

    # Display the 3D plot
    st.plotly_chart(fig, use_container_width=True)

    # Display analysis results
    st.header("Analysis Results")
    st.subheader("Building Parameters")
    st.write(f"Total Height: {total_height:.2f} m")
    st.write(f"Number of Floors: {num_floors}")
    st.write(f"Number of Columns: {num_columns}")
    st.write(f"Floor Height: {floor_height} m")
    st.write(f"Building Radius: {radius} m")

    st.subheader("Loading Information")
    st.write(f"Total Live Load: {total_live_load/1000:.2f} kN")
    st.write(f"Live Load per Floor: {live_load} kN/m²")
    st.write(f"Total Wind Force: {wind_force/1000:.2f} kN")
    st.write(f"Wind Speed: {wind_speed} m/s")
    st.write(f"Seismic Load: {seismic_load/1000:.2f} kN")
    st.write(f"Seismic Zone: {seismic_zone}")

    st.subheader("Structural Details")
    st.write(f"Material: {material_type.capitalize()}")
    st.write(f"Beam Type: {beam_design.capitalize()}")
    st.write(f"Column Type: {column_design.capitalize()}")
    st.info("Hover over beams and columns in the 3D model to see detailed structural properties")

    # Get material standards recommendation
    standards_recommendation = get_material_standards(radius, num_floors, floor_height, wind_speed, live_load)
    st.subheader("Material Standards Analysis")
    st.text(standards_recommendation)