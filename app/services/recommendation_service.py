"""
Recommendation service for generating property recommendations.
"""
from typing import List, Dict, Any
import config
from app.services.property_service import PropertyService
from app.services.scoring_service import ScoringService


class RecommendationService:
    """Service for generating property recommendations."""
    
    def __init__(self, property_service: PropertyService, scoring_service: ScoringService):
        """
        Initialize the recommendation service.
        
        Args:
            property_service: PropertyService instance
            scoring_service: ScoringService instance
        """
        self.property_service = property_service
        self.scoring_service = scoring_service
    
    def get_recommendations(
        self, 
        preferences: Dict[str, Any], 
        property_count: int = None,
        num_recommendations: int = None
    ) -> Dict[str, Any]:
        """
        Get property recommendations based on user preferences.
        
        Args:
            preferences: User preferences dictionary
            property_count: Number of properties to evaluate (defaults to config)
            num_recommendations: Number of recommendations to return (defaults to config)
            
        Returns:
            Dictionary containing recommendations and metadata
        """
        if property_count is None:
            property_count = config.DEFAULT_PROPERTY_COUNT
        if num_recommendations is None:
            num_recommendations = config.DEFAULT_RECOMMENDATIONS
        
        # Generate properties
        properties = self.property_service.generate_properties(count=property_count)
        
        # Score each property
        scored_properties = []
        for prop in properties:
            score = self.scoring_service.calculate_match_score(prop, preferences)
            reasoning = self.scoring_service.generate_reasoning(prop, preferences, score)
            
            scored_properties.append({
                **prop,
                'match_score': round(score, 2),
                'reasoning': reasoning
            })
        
        # Sort by match score (descending)
        scored_properties.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return top recommendations
        recommendations = scored_properties[:num_recommendations]
        
        return {
            'success': True,
            'recommendations': recommendations,
            'total_properties_evaluated': len(properties),
            'model_used': self.property_service.price_predictor.model_loaded
        }

