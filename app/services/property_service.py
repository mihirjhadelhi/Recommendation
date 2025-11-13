"""
Property data generation and management service.
"""
from typing import List, Dict, Any
import numpy as np
import config
from app.models.predictor import PricePredictor


class PropertyService:
    """Service for generating and managing property data."""
    
    def __init__(self, price_predictor: PricePredictor):
        """
        Initialize the property service.
        
        Args:
            price_predictor: PricePredictor instance for price predictions
        """
        self.price_predictor = price_predictor
    
    def generate_properties(self, count: int = None) -> List[Dict[str, Any]]:
        """
        Generate mock property data.
        
        Args:
            count: Number of properties to generate (defaults to config value)
            
        Returns:
            List of property dictionaries
        """
        if count is None:
            count = config.DEFAULT_PROPERTY_COUNT
        
        properties = []
        ranges = config.PROPERTY_RANGES
        
        for i in range(count):
            bedrooms = np.random.randint(*ranges['bedrooms'])
            bathrooms = bedrooms - np.random.randint(0, 2)
            bathrooms = max(1, bathrooms)
            square_feet = np.random.randint(*ranges['square_feet'])
            year_built = np.random.randint(*ranges['year_built'])
            zip_code = int(np.random.choice(config.ZIP_CODES))
            lot_size = np.random.randint(*ranges['lot_size'])
            
            # Additional fields for scoring
            school_rating = round(np.random.uniform(*ranges['school_rating']), 1)
            commute_time = int(np.random.randint(*ranges['commute_time']))
            has_pool = bool(np.random.choice([True, False], p=[0.3, 0.7]))
            has_garage = bool(np.random.choice([True, False], p=[0.7, 0.3]))
            has_garden = bool(np.random.choice([True, False], p=[0.6, 0.4]))
            
            property_data = {
                'id': int(i + 1),
                'address': f"{np.random.randint(100, 9999)} {np.random.choice(config.STREET_NAMES)} St",
                'city': str(np.random.choice(config.CITIES)),
                'state': str(np.random.choice(config.STATES)),
                'zip_code': int(zip_code),
                'bedrooms': int(bedrooms),
                'bathrooms': int(bathrooms),
                'square_feet': int(square_feet),
                'year_built': int(year_built),
                'lot_size': int(lot_size),
                'property_type': 'House',  # All properties are houses
                'school_rating': float(school_rating),
                'commute_time': int(commute_time),
                'has_pool': bool(has_pool),
                'has_garage': bool(has_garage),
                'has_garden': bool(has_garden),
            }
            
            # Predict price using model
            predicted_price = self.price_predictor.predict(property_data)
            property_data['predicted_price'] = float(round(predicted_price, 2))
            
            # Add property image URL
            property_data['image_url'] = config.PROPERTY_IMAGES[i % len(config.PROPERTY_IMAGES)]
            
            properties.append(property_data)
        
        return properties

