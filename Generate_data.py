import numpy as np
import math
import pandas as pd
from config import MATERIAL_PROPERTIES, SEISMIC_ZONES, BEAM_PROPERTIES, COLUMN_PROPERTIES
from utils import calculate_seismic_load, calculate_wind_load, calculate_beam_properties, calculate_column_properties

def generate_dataset(num_samples=100000):
    # Initialize lists to store features and labels
    features = []
    labels = []

    # Randomly generate building parameters
    for _ in range(num_samples):
        # Randomly generate building parameters
        radius = np.random.uniform(10, 500)  # Building radius (m)
        num_columns = np.random.randint(4, 50)  # Number of columns
        num_floors = np.random.randint(1, 200)  # Number of floors
        floor_height = np.random.uniform(2.5, 4.0)  # Floor height (m)
        material_type = np.random.choice(list(MATERIAL_PROPERTIES.keys()))  # Material type
        live_load = np.random.uniform(1.0, 10.0)  # Live load (kN/m²)
        wind_speed = np.random.uniform(10, 500)  # Wind speed (m/s)
        seismic_zone = np.random.choice(list(SEISMIC_ZONES.keys()))  # Seismic zone
        beam_design = np.random.choice(list(BEAM_PROPERTIES.keys()))  # Beam design
        column_design = np.random.choice(list(COLUMN_PROPERTIES.keys()))  # Column design

        # Fetch material properties
        material = MATERIAL_PROPERTIES[material_type]

        # Calculate total height and live load
        total_height = num_floors * floor_height
        total_live_load = live_load * math.pi * radius**2 * num_floors

        # Calculate wind force
        wind_force = calculate_wind_load(radius, total_height, wind_speed)

        # Calculate seismic load
        zone_factor = SEISMIC_ZONES[seismic_zone]['zone_factor']
        total_weight = total_live_load + (material['density'] * math.pi * radius**2 * total_height)
        seismic_load = calculate_seismic_load(zone_factor, total_weight, total_height)

        # Calculate beam span length based on number of columns
        beam_span = 2 * radius * math.sin(math.pi / num_columns)

        # Calculate beam and column properties
        beam_props = calculate_beam_properties(beam_design, beam_span, material)
        column_props = calculate_column_properties(column_design, floor_height, material)

        # Example: Calculate stress (this is a placeholder, replace with actual stress calculation)
        # Ensure beam_props['area'] and column_props['area'] are floats
        # Remove units and convert to float
        beam_area = float(beam_props['area'].replace(' m²', ''))
        column_area = float(column_props['area'].replace(' m²', ''))
        stress = (wind_force + seismic_load) / (beam_area + column_area)

        # Store features and labels
        features.append([radius, num_columns, num_floors, floor_height, live_load, wind_speed, zone_factor, material['density'], material['elastic_modulus'], beam_span])
        labels.append(stress)

    # Convert to numpy arrays
    features = np.array(features)
    labels = np.array(labels)

    # Convert to pandas DataFrame
    data = pd.DataFrame(features, columns=['radius', 'num_columns', 'num_floors', 'floor_height', 'live_load', 'wind_speed', 'zone_factor', 'density', 'elastic_modulus', 'beam_span'])
    data['stress'] = labels

    # Save to CSV
    data.to_csv('structural_dataset.csv', index=False)

    return features, labels

# Generate and save the dataset
features, labels = generate_dataset(num_samples=100000)