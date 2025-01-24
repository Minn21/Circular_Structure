import streamlit as st
from config import MATERIAL_PROPERTIES, SEISMIC_ZONES, BEAM_PROPERTIES, COLUMN_PROPERTIES

# Title of the app
st.title("Circular Building Structural Analysis")

# Sidebar for input fields
with st.sidebar:
    st.header("Building Parameters")
    radius = st.number_input("Building Radius (m)", min_value=1.0, value=20.0, step=0.1)
    num_columns = st.number_input("Number of Columns", min_value=4, max_value=24, value=12, step=1)
    num_floors = st.number_input("Number of Floors", min_value=1, value=5, step=1)
    floor_height = st.number_input("Floor Height (m)", min_value=1.0, value=3.0, step=0.1)

    st.header("Material and Load Parameters")
    material_type = st.selectbox("Material for Structural Elements", options=list(MATERIAL_PROPERTIES.keys()), index=0)
    live_load = st.number_input("Live Load (kN/m²)", min_value=0.0, value=2.0, step=0.1)
    wind_speed = st.number_input("Wind Speed (m/s)", min_value=0.0, value=15.0, step=0.1)
    seismic_zone = st.selectbox("Seismic Zone", options=list(SEISMIC_ZONES.keys()), index=0)
    load_intensity = st.slider("Load Intensity (kN)", min_value=0, max_value=100, value=50, step=1)
    beam_design = st.selectbox("Beam Design", options=list(BEAM_PROPERTIES.keys()), index=0)
    column_design = st.selectbox("Column Design", options=list(COLUMN_PROPERTIES.keys()), index=1)
    show_deformation = st.checkbox("Show Deformation", value=False)

    # Analyze button
    if st.button("Analyze"):
        # Placeholder for analysis logic
        st.session_state.analyze = True
    else:
        st.session_state.analyze = False

# Main content area
if st.session_state.get("analyze", False):
    st.header("Analysis Results")
    
    # Display building parameters
    st.subheader("Building Parameters")
    st.write(f"Building Radius: {radius} m")
    st.write(f"Number of Columns: {num_columns}")
    st.write(f"Number of Floors: {num_floors}")
    st.write(f"Floor Height: {floor_height} m")

    # Display material and load parameters
    st.subheader("Material and Load Parameters")
    st.write(f"Material: {material_type.capitalize()}")
    st.write(f"Live Load: {live_load} kN/m²")
    st.write(f"Wind Speed: {wind_speed} m/s")
    st.write(f"Seismic Zone: {seismic_zone}")
    st.write(f"Load Intensity: {load_intensity} kN")
    st.write(f"Beam Design: {beam_design.capitalize()}")
    st.write(f"Column Design: {column_design.capitalize()}")
    st.write(f"Show Deformation: {'Yes' if show_deformation else 'No'}")

    # Placeholder for 3D visualization
    st.subheader("3D Visualization")
    st.write("3D visualization will be displayed here.")