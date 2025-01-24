# config.py remains the same
import math
import numpy as np

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

# Seismic zone parameters
SEISMIC_ZONES = {
    'Zone I': {'zone_factor': 0.1, 'description': 'Very Low Damage Risk Zone'},
    'Zone II': {'zone_factor': 0.16, 'description': 'Low Damage Risk Zone'},
    'Zone III': {'zone_factor': 0.24, 'description': 'Moderate Damage Risk Zone'},
    'Zone IV': {'zone_factor': 0.36, 'description': 'High Damage Risk Zone'},
    'Zone V': {'zone_factor': 0.48, 'description': 'Very High Damage Risk Zone'}
}

# Structural element properties based on design type
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