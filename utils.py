import math
import numpy as np
from config import MATERIAL_PROPERTIES, BEAM_PROPERTIES, COLUMN_PROPERTIES

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

def calculate_seismic_load(zone_factor, total_weight, total_height, importance_factor=1.0, response_reduction=3.0):
    """Calculate seismic base shear using equivalent static method."""
    height_factor = 0.075  # for RC frame building
    time_period = height_factor * (total_height ** 0.75)
    
    if time_period <= 0.5:
        sa_by_g = 2.5
    else:
        sa_by_g = 1.25 / max(time_period, 0.01)  # Avoid division by zero
    
    ah = (zone_factor * importance_factor * sa_by_g) / (2 * response_reduction)
    base_shear = ah * total_weight
    return base_shear

def calculate_wind_load(radius, height, wind_speed, shape_factor=1.2, gust_factor=1.0):
    """Calculate wind load on the building."""
    if wind_speed < 0:
        return 0
    if radius <= 0 or height <= 0:
        return 0
    air_density = 1.225  # kg/m^3
    area = 2 * np.pi * radius * height
    dynamic_pressure = 0.5 * air_density * wind_speed**2
    wind_force = dynamic_pressure * area * shape_factor * gust_factor
    return wind_force

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