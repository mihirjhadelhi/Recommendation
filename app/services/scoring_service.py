"""
Scoring service for calculating property match scores.
"""
from typing import Dict, Any
from datetime import datetime
import config


class ScoringService:
    """Service for calculating property match scores."""
    
    @staticmethod
    def calculate_price_match_score(predicted_price: float, user_budget: float) -> float:
        """Calculate price match score (0-100)."""
        if predicted_price <= user_budget:
            return 100.0
        else:
            penalty = ((predicted_price - user_budget) / user_budget) * 100
            return max(0.0, 100.0 - penalty)
    
    @staticmethod
    def calculate_bedroom_score(property_bedrooms: int, user_min_bedrooms: int) -> float:
        """Calculate bedroom score (0-100)."""
        if property_bedrooms >= user_min_bedrooms:
            return 100.0
        else:
            return (property_bedrooms / user_min_bedrooms) * 100
    
    @staticmethod
    def calculate_school_rating_score(school_rating: float) -> float:
        """Calculate school rating score (0-100)."""
        return (school_rating / 10) * 100
    
    @staticmethod
    def calculate_commute_score(commute_time: int) -> float:
        """Calculate commute score (0-100)."""
        if commute_time <= 15:
            return 100.0
        elif commute_time <= 30:
            return 80.0
        elif commute_time <= 45:
            return 50.0
        else:
            return 20.0
    
    @staticmethod
    def calculate_property_age_score(year_built: int) -> float:
        """Calculate property age score (0-100)."""
        current_year = datetime.now().year
        age = current_year - year_built
        
        if age <= 5:
            return 100.0
        elif age <= 15:
            return 80.0
        elif age <= 30:
            return 60.0
        else:
            return 40.0
    
    @staticmethod
    def calculate_amenities_score(has_pool: bool, has_garage: bool, has_garden: bool) -> float:
        """Calculate amenities score (0-100)."""
        features = [has_pool, has_garage, has_garden]
        return (sum(features) / 3) * 100
    
    def calculate_match_score(self, property: Dict[str, Any], preferences: Dict[str, Any]) -> float:
        """
        Calculate total match score using weighted formula (0-100).
        
        Args:
            property: Property data dictionary
            preferences: User preferences dictionary
            
        Returns:
            float: Total match score (0-100)
        """
        weights = config.SCORING_WEIGHTS
        user_budget = preferences.get('budget', config.DEFAULT_BUDGET)
        predicted_price = property.get('predicted_price', 0)
        property_bedrooms = property.get('bedrooms', 0)
        user_min_bedrooms = preferences.get('min_bedrooms', config.DEFAULT_MIN_BEDROOMS)
        school_rating = property.get('school_rating', 5.0)
        commute_time = property.get('commute_time', 30)
        year_built = property.get('year_built', 2000)
        has_pool = property.get('has_pool', False)
        has_garage = property.get('has_garage', False)
        has_garden = property.get('has_garden', False)
        
        # Calculate component scores
        price_match_score = self.calculate_price_match_score(predicted_price, user_budget)
        bedroom_score = self.calculate_bedroom_score(property_bedrooms, user_min_bedrooms)
        school_rating_score = self.calculate_school_rating_score(school_rating)
        commute_score = self.calculate_commute_score(commute_time)
        property_age_score = self.calculate_property_age_score(year_built)
        amenities_score = self.calculate_amenities_score(has_pool, has_garage, has_garden)
        
        # Calculate weighted total score
        total_score = (
            weights['price_match'] * price_match_score +
            weights['bedroom'] * bedroom_score +
            weights['school_rating'] * school_rating_score +
            weights['commute'] * commute_score +
            weights['property_age'] * property_age_score +
            weights['amenities'] * amenities_score
        )
        
        return round(total_score, 2)
    
    def generate_reasoning(self, property: Dict[str, Any], preferences: Dict[str, Any], score: float) -> str:
        """
        Generate human-readable reasoning for why a property was recommended.
        
        Args:
            property: Property data dictionary
            preferences: User preferences dictionary
            score: Match score
            
        Returns:
            str: Human-readable reasoning
        """
        reasons = []
        budget = preferences.get('budget', config.DEFAULT_BUDGET)
        price = property.get('predicted_price', 0)
        
        # Budget reasoning
        if price <= budget:
            if price <= budget * 0.9:
                reasons.append(f"Excellent value at ${price:,.0f}, well under your ${budget:,.0f} budget")
            else:
                reasons.append(f"Fits comfortably within your ${budget:,.0f} budget at ${price:,.0f}")
        elif price <= budget * 1.1:
            reasons.append(f"Slightly above budget at ${price:,.0f}, but offers great features")
        else:
            reasons.append(f"Price: ${price:,.0f} (above budget)")
        
        # Bedrooms
        bedrooms = property.get('bedrooms', 0)
        min_bedrooms = preferences.get('min_bedrooms', config.DEFAULT_MIN_BEDROOMS)
        if bedrooms >= min_bedrooms:
            reasons.append(f"Meets your {min_bedrooms}+ bedroom requirement ({bedrooms} bedrooms)")
        
        # School rating
        school_rating = property.get('school_rating', 5.0)
        if school_rating >= 8.0:
            reasons.append(f"Excellent school rating of {school_rating}/10")
        elif school_rating >= 6.0:
            reasons.append(f"Good school rating of {school_rating}/10")
        
        # Commute time
        commute_time = property.get('commute_time', 30)
        if commute_time <= 15:
            reasons.append(f"Short commute time of {commute_time} minutes")
        elif commute_time <= 30:
            reasons.append(f"Reasonable commute time of {commute_time} minutes")
        
        # Property age
        year_built = property.get('year_built', 2000)
        current_year = datetime.now().year
        age = current_year - year_built
        if age <= 5:
            reasons.append(f"Recently built in {year_built} (very modern)")
        elif age <= 15:
            reasons.append(f"Modern home built in {year_built}")
        elif age <= 30:
            reasons.append(f"Established property from {year_built}")
        
        # Amenities
        amenities = []
        if property.get('has_pool', False):
            amenities.append("pool")
        if property.get('has_garage', False):
            amenities.append("garage")
        if property.get('has_garden', False):
            amenities.append("garden")
        
        if amenities:
            amenities_str = ", ".join(amenities)
            reasons.append(f"Features: {amenities_str}")
        
        # Location
        city = property.get('city', '')
        state = property.get('state', '')
        if city and state:
            reasons.append(f"Location: {city}, {state}")
        
        return "; ".join(reasons) if reasons else "Good match based on your preferences"

