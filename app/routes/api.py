"""
API routes for the Property Recommendation System.
"""
from flask import Flask, request, jsonify
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.loader import ModelLoader

from app.models.predictor import PricePredictor
from app.services.property_service import PropertyService
from app.services.scoring_service import ScoringService
from app.services.recommendation_service import RecommendationService


def register_routes(app: Flask, model_loader: 'ModelLoader') -> None:
    """
    Register all API routes with the Flask application.
    
    Args:
        app: Flask application instance
        model_loader: ModelLoader instance
    """
    # Initialize services
    price_predictor = PricePredictor(
        model=model_loader.model,
        model_loaded=model_loader.model_loaded
    )
    property_service = PropertyService(price_predictor)
    scoring_service = ScoringService()
    recommendation_service = RecommendationService(property_service, scoring_service)
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'model_loaded': model_loader.model_loaded
        })
    
    @app.route('/api/recommend', methods=['POST'])
    def recommend():
        """Get property recommendations based on user preferences."""
        try:
            data = request.json
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            preferences = data.get('preferences', {})
            
            # Get recommendations
            result = recommendation_service.get_recommendations(preferences)
            return jsonify(result)
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/properties', methods=['GET'])
    def get_properties():
        """Get all available properties (for testing)."""
        try:
            properties = property_service.generate_properties()
            return jsonify({
                'success': True,
                'properties': properties,
                'count': len(properties)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

