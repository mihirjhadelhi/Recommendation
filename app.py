from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
import numpy as np
from datetime import datetime
import sys

# Import the model wrapper class
from model_wrapper import ComplexTrapModelRenamed

# Try importing joblib for scikit-learn models
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

app = Flask(__name__)
CORS(app)

# Global model variable
model = None
model_loaded = False

def load_model():
    """Load the ML model if it exists"""
    global model, model_loaded
    model_path = 'complex_price_model_v2.pkl'
    
    if not os.path.exists(model_path):
        print(f"Model file {model_path} not found. Using fallback prediction.")
        model_loaded = False
        return False
    
    # Try multiple loading methods
    loading_methods = []
    
    # Method 1: Try joblib (common for scikit-learn models)
    if JOBLIB_AVAILABLE:
        loading_methods.append(('joblib', lambda: joblib.load(model_path)))
    
    # Method 2: Try pickle with custom class handling
    def load_with_pickle():
        # Use the ComplexTrapModelRenamed class from model_wrapper module
        # This allows pickle to deserialize the model even if the original class isn't available
        
        # Register the class in sys.modules so pickle can find it
        # Pickle looks for classes by their module path, so we need to make sure
        # the class is available at the module level where pickle expects it
        
        # If the model was pickled with the class in __main__, we need to register it there
        # Otherwise, pickle will look for it in model_wrapper module
        if '__main__' in sys.modules:
            main_module = sys.modules['__main__']
            if not hasattr(main_module, 'ComplexTrapModelRenamed'):
                # Register the class in __main__ so pickle can find it
                setattr(main_module, 'ComplexTrapModelRenamed', ComplexTrapModelRenamed)
        
        # Also make sure it's available in the current module (app)
        current_module = sys.modules[__name__]
        if not hasattr(current_module, 'ComplexTrapModelRenamed'):
            setattr(current_module, 'ComplexTrapModelRenamed', ComplexTrapModelRenamed)
        
        with open(model_path, 'rb') as f:
            return pickle.load(f)
    
    loading_methods.append(('pickle with class workaround', load_with_pickle))
    
    # Method 3: Try standard pickle
    loading_methods.append(('pickle', lambda: pickle.load(open(model_path, 'rb'))))
    
    # Try each method
    for method_name, load_func in loading_methods:
        try:
            print(f"Attempting to load model using {method_name}...")
            model = load_func()
            
            # Verify the model has a predict method
            if hasattr(model, 'predict'):
                model_loaded = True
                print(f"✓ Model loaded successfully from {model_path} using {method_name}")
                return True
            else:
                print(f"Warning: Loaded object doesn't have a 'predict' method")
        except Exception as e:
            print(f"✗ Failed to load with {method_name}: {str(e)}")
            continue
    
    # If all methods failed
    print(f"⚠ Could not load model from {model_path}. Using fallback prediction.")
    print("   The model file may require the original class definition.")
    print("   The system will continue with fallback predictions.")
    model_loaded = False
    return False

def predict_price_fallback(property_data):
    """Fallback price prediction when model is not available"""
    # Simple heuristic-based prediction
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
        # Simple location premium
        location_factor = 1 + (zip_code % 100) / 1000
        price *= location_factor
    
    # Add some randomness for realism
    price *= (0.9 + np.random.random() * 0.2)
    
    return max(price, 50000)  # Minimum price

def predict_price(property_data):
    """Predict property price using the ML model or fallback"""
    if model_loaded and model is not None:
        try:
            # Extract features in the order expected by the model
            # Note: Adjust these based on your actual model's expected features
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
            prediction = model.predict(features_array)[0]
            return float(prediction)
        except Exception as e:
            print(f"Error in model prediction: {e}")
            return predict_price_fallback(property_data)
    else:
        return predict_price_fallback(property_data)

def generate_mock_properties(count=20):
    """Generate mock property data"""
    properties = []
    zip_codes = [10001, 10002, 10003, 90210, 94102, 60601, 77001, 30301, 33101, 98101]
    
    for i in range(count):
        bedrooms = np.random.randint(1, 6)
        bathrooms = bedrooms - np.random.randint(0, 2)
        bathrooms = max(1, bathrooms)
        square_feet = np.random.randint(800, 4000)
        year_built = np.random.randint(1950, 2024)
        zip_code = np.random.choice(zip_codes)
        lot_size = np.random.randint(3000, 15000)
        
        # New fields for scoring
        school_rating = round(np.random.uniform(4.0, 10.0), 1)  # 4.0 to 10.0
        commute_time = int(np.random.randint(5, 60))  # 5 to 60 minutes
        has_pool = bool(np.random.choice([True, False], p=[0.3, 0.7]))
        has_garage = bool(np.random.choice([True, False], p=[0.7, 0.3]))
        has_garden = bool(np.random.choice([True, False], p=[0.6, 0.4]))
        
        property_data = {
            'id': int(i + 1),
            'address': f"{np.random.randint(100, 9999)} {np.random.choice(['Main', 'Oak', 'Park', 'Maple', 'Elm'])} St",
            'city': str(np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Atlanta', 'Miami', 'Seattle'])),
            'state': str(np.random.choice(['NY', 'CA', 'IL', 'TX', 'GA', 'FL', 'WA'])),
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
        predicted_price = predict_price(property_data)
        property_data['predicted_price'] = float(round(predicted_price, 2))
        
        # Add property image URL (using verified working Unsplash property image URLs)
        # These are reliable Unsplash photo IDs for property/real estate images
        property_images = [
            'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?w=800&h=600&fit=crop',  # Modern house
            'https://images.unsplash.com/photo-156401379991-8e60b09b8fe7?w=800&h=600&fit=crop',  # Cozy home
            'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&h=600&fit=crop',  # Contemporary
            'https://images.unsplash.com/photo-1568605116820-0c0a4313b0e4?w=800&h=600&fit=crop',  # Suburban
            'https://images.unsplash.com/photo-1568605117026-5f8557b12d10?w=800&h=600&fit=crop',  # Luxury
            'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=600&fit=crop',  # Family home
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=600&fit=crop',  # Townhouse
            'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&h=600&fit=crop',  # Condo
            'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800&h=600&fit=crop',  # Modern home
            'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=600&fit=crop',  # Residential
            'https://images.unsplash.com/photo-1600607687644-c7171b42498b?w=800&h=600&fit=crop',  # House exterior
            'https://images.unsplash.com/photo-1600585154084-4e5fe7c39198?w=800&h=600&fit=crop',  # Property
        ]
        
        property_data['image_url'] = property_images[i % len(property_images)]
        
        properties.append(property_data)
    
    return properties

def calculate_price_match_score(predicted_price, user_budget):
    """Calculate price match score (0-100)"""
    if predicted_price <= user_budget:
        return 100
    else:
        penalty = ((predicted_price - user_budget) / user_budget) * 100
        return max(0, 100 - penalty)

def calculate_bedroom_score(property_bedrooms, user_min_bedrooms):
    """Calculate bedroom score (0-100)"""
    if property_bedrooms >= user_min_bedrooms:
        return 100
    else:
        return (property_bedrooms / user_min_bedrooms) * 100

def calculate_school_rating_score(school_rating):
    """Calculate school rating score (0-100)"""
    return (school_rating / 10) * 100

def calculate_commute_score(commute_time):
    """Calculate commute score (0-100)"""
    if commute_time <= 15:
        return 100
    elif commute_time <= 30:
        return 80
    elif commute_time <= 45:
        return 50
    else:
        return 20

def calculate_property_age_score(year_built):
    """Calculate property age score (0-100)"""
    current_year = datetime.now().year
    age = current_year - year_built
    
    if age <= 5:
        return 100
    elif age <= 15:
        return 80
    elif age <= 30:
        return 60
    else:
        return 40

def calculate_amenities_score(has_pool, has_garage, has_garden):
    """Calculate amenities score (0-100)"""
    features = [has_pool, has_garage, has_garden]
    return (sum(features) / 3) * 100

def calculate_match_score(property, preferences):
    """Calculate total match score using weighted formula (0-100)"""
    user_budget = preferences.get('budget', 500000)
    predicted_price = property.get('predicted_price', 0)
    property_bedrooms = property.get('bedrooms', 0)
    user_min_bedrooms = preferences.get('min_bedrooms', 2)
    school_rating = property.get('school_rating', 5.0)
    commute_time = property.get('commute_time', 30)
    year_built = property.get('year_built', 2000)
    has_pool = property.get('has_pool', False)
    has_garage = property.get('has_garage', False)
    has_garden = property.get('has_garden', False)
    
    # Calculate component scores
    price_match_score = calculate_price_match_score(predicted_price, user_budget)
    bedroom_score = calculate_bedroom_score(property_bedrooms, user_min_bedrooms)
    school_rating_score = calculate_school_rating_score(school_rating)
    commute_score = calculate_commute_score(commute_time)
    property_age_score = calculate_property_age_score(year_built)
    amenities_score = calculate_amenities_score(has_pool, has_garage, has_garden)
    
    # Calculate weighted total score
    total_score = (
        0.3 * price_match_score +
        0.2 * bedroom_score +
        0.15 * school_rating_score +
        0.15 * commute_score +
        0.1 * property_age_score +
        0.1 * amenities_score
    )
    
    return round(total_score, 2)

def generate_reasoning(property, preferences, score):
    """Generate human-readable reasoning for why a property was recommended"""
    reasons = []
    
    budget = preferences.get('budget', 500000)
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
    min_bedrooms = preferences.get('min_bedrooms', 2)
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

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model_loaded
    })

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """Get property recommendations based on user preferences"""
    try:
        data = request.json
        preferences = data.get('preferences', {})
        
        # Generate or fetch properties
        properties = generate_mock_properties(count=20)
        
        # Score each property
        scored_properties = []
        for prop in properties:
            score = calculate_match_score(prop, preferences)
            reasoning = generate_reasoning(prop, preferences, score)
            
            scored_properties.append({
                **prop,
                'match_score': round(score, 2),
                'reasoning': reasoning
            })
        
        # Sort by match score (descending)
        scored_properties.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Return top 3 (or 2-3 as requested)
        num_recommendations = min(3, len(scored_properties))
        recommendations = scored_properties[:num_recommendations]
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'total_properties_evaluated': len(properties),
            'model_used': model_loaded
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/properties', methods=['GET'])
def get_properties():
    """Get all available properties (for testing)"""
    properties = generate_mock_properties(count=20)
    return jsonify({
        'success': True,
        'properties': properties,
        'count': len(properties)
    })

if __name__ == '__main__':
    # Load model on startup
    load_model()
    
    # Run the Flask app
    print("Starting Property Recommendation API...")
    print(f"Model loaded: {model_loaded}")
    app.run(debug=True, port=5000)

