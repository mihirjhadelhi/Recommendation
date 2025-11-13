"""
Configuration settings for the Property Recommendation System.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Model configuration
MODEL_PATH = BASE_DIR / 'complex_price_model_v2.pkl'
MODEL_FILE_NAME = 'complex_price_model_v2.pkl'

# Server configuration
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Property generation defaults
DEFAULT_PROPERTY_COUNT = 20
DEFAULT_RECOMMENDATIONS = 3

# Scoring weights
SCORING_WEIGHTS = {
    'price_match': 0.3,
    'bedroom': 0.2,
    'school_rating': 0.15,
    'commute': 0.15,
    'property_age': 0.1,
    'amenities': 0.1
}

# Default property values
DEFAULT_BUDGET = 500000
DEFAULT_MIN_BEDROOMS = 2
DEFAULT_MIN_BATHROOMS = 1
DEFAULT_MIN_SQUARE_FEET = 1000

# Property data ranges
PROPERTY_RANGES = {
    'bedrooms': (1, 6),
    'bathrooms': (1, 5),
    'square_feet': (800, 4000),
    'year_built': (1950, 2024),
    'lot_size': (3000, 15000),
    'school_rating': (4.0, 10.0),
    'commute_time': (5, 60)
}

# Zip codes for mock data
ZIP_CODES = [10001, 10002, 10003, 90210, 94102, 60601, 77001, 30301, 33101, 98101]

# Cities and states for mock data
CITIES = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Atlanta', 'Miami', 'Seattle']
STATES = ['NY', 'CA', 'IL', 'TX', 'GA', 'FL', 'WA']
STREET_NAMES = ['Main', 'Oak', 'Park', 'Maple', 'Elm']

# Property images (Unsplash URLs)
PROPERTY_IMAGES = [
    'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-156401379991-8e60b09b8fe7?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1568605116820-0c0a4313b0e4?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1568605117026-5f8557b12d10?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1600607687644-c7171b42498b?w=800&h=600&fit=crop',
    'https://images.unsplash.com/photo-1600585154084-4e5fe7c39198?w=800&h=600&fit=crop',
]

FALLBACK_IMAGE_URL = 'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800&h=600&fit=crop'

