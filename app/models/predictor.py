"""
Price prediction functionality for properties.
"""
from typing import Dict, Any
import numpy as np
import config


class PricePredictor:
    """Handles property price prediction using ML models or fallback methods."""
    
    def __init__(self, model: Any = None, model_loaded: bool = False):
        """
        Initialize the price predictor.
        
        Args:
            model: Loaded ML model (optional)
            model_loaded: Whether the model is loaded and ready
        """
        self.model = model
        self.model_loaded = model_loaded
    
    def predict_fallback(self, property_data: Dict[str, Any]) -> float:
        """
        Fallback price prediction when model is not available.
        
        Args:
            property_data: Dictionary containing property features
            
        Returns:
            float: Predicted price
        """
        base_price = 200000
        price = base_price
        
        # Adjust based on bedrooms
        price += property_data.get('bedrooms', 2) * 50000
        
        # Adjust based on bathrooms
        price += property_data.get('bathrooms', 1) * 30000
        
        # Adjust based on square footage
        sqft = property_data.get('square_feet', 1500)
        price += (sqft - 1500) * 100
        
        # Adjust based on location (zip code as proxy)
        zip_code = property_data.get('zip_code', 0)
        if zip_code:
            location_factor = 1 + (zip_code % 100) / 1000
            price *= location_factor
        
        # Add some randomness for realism
        price *= (0.9 + np.random.random() * 0.2)
        
        return max(price, 50000)  # Minimum price
    
    def predict(self, property_data: Dict[str, Any]) -> float:
        """
        Predict property price using the ML model or fallback.
        
        Args:
            property_data: Dictionary containing property features
            
        Returns:
            float: Predicted price
        """
        if self.model_loaded and self.model is not None:
            try:
                # Extract features in the order expected by the model
                features = [
                    property_data.get('bedrooms', 2),
                    property_data.get('bathrooms', 1),
                    property_data.get('square_feet', 1500),
                    property_data.get('year_built', 2000),
                    property_data.get('zip_code', 0),
                    property_data.get('lot_size', 5000),
                ]
                
                # Reshape for single prediction
                features_array = np.array(features).reshape(1, -1)
                
                # Make prediction
                prediction = self.model.predict(features_array)[0]
                return float(prediction)
            except Exception as e:
                print(f"Error in model prediction: {e}")
                return self.predict_fallback(property_data)
        else:
            return self.predict_fallback(property_data)

