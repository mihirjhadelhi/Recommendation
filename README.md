# Property Recommendation System MVP

A full-stack property recommendation system that uses machine learning to predict property prices and provides personalized recommendations based on user preferences.

## Features

- **User Preference Input**: Enter budget, location, minimum bedrooms/bathrooms, square footage, and property type
- **ML Model Integration**: Uses `complex_price_model_v2.pkl` to predict property prices (with fallback if model not available)
- **Smart Recommendations**: Returns top 2-3 property matches with detailed reasoning
- **Weighted Match Scoring**: Advanced scoring algorithm considering price, bedrooms, school ratings, commute time, property age, and amenities
- **Property Images**: Visual property listings with high-quality images
- **Modern UI**: Clean, responsive interface with beautiful design and smooth animations

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Upgrade pip, setuptools, and wheel** (important for Python 3.13):
```bash
python -m pip install --upgrade pip setuptools wheel
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note for Python 3.13 users**: If you encounter `BackendUnavailable: Cannot import 'setuptools.build_meta'` errors, make sure to run step 1 first. Python 3.13 virtual environments don't include setuptools by default.

3. Place your ML model file:
   - **Location**: Place `complex_price_model_v2.pkl` in the **root directory** (same folder as `app.py`)
   - **File structure should be:**
     ```
     NewChatbot/
     ├── app.py
     ├── complex_price_model_v2.pkl    ← Place model here
     ├── requirements.txt
     └── static/
         └── ...
     ```
   - **Note**: The system will work with a fallback prediction method if the model file is not present, but for best results, include your trained model.

4. Run the backend server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

5. Open the frontend:
   - Open `static/index.html` in your web browser
   - Or serve it using a simple HTTP server:
     ```bash
     cd static
     python -m http.server 8000
     ```
     Then open `http://localhost:8000` in your browser

## Usage

1. Fill in your home-buying preferences:
   - Budget
   - Preferred location (optional)
   - Minimum bedrooms and bathrooms
   - Minimum square footage
   - Note: All properties are houses

2. Click "Get Recommendations"

3. Review the top 2-3 property recommendations with:
   - **Property images** for visual appeal
   - **Predicted price** (using ML model)
   - **Match score** (0-100%) showing how well it fits your needs
   - **Detailed reasoning** explaining why it was recommended
   - **Full property details** including:
     - Bedrooms, bathrooms, square footage
     - School rating (out of 10)
     - Commute time (minutes)
     - Property age and amenities (pool, garage, garden)

## API Endpoints

### `POST /api/recommend`
Get property recommendations based on preferences.

**Request Body:**
```json
{
  "preferences": {
    "budget": 500000,
    "location": "New York",
    "min_bedrooms": 2,
    "min_bathrooms": 1,
    "min_square_feet": 1000
  }
}
```

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "id": 1,
      "address": "123 Main St",
      "city": "New York",
      "state": "NY",
      "zip_code": 10001,
      "bedrooms": 3,
      "bathrooms": 2,
      "square_feet": 2000,
      "year_built": 2010,
      "lot_size": 5000,
      "property_type": "House",
      "school_rating": 8.5,
      "commute_time": 20,
      "has_pool": true,
      "has_garage": true,
      "has_garden": false,
      "image_url": "https://images.unsplash.com/photo-...",
      "predicted_price": 450000,
      "match_score": 87.3,
      "reasoning": "Excellent value at $450,000, well under your $500,000 budget; Meets your 2+ bedroom requirement with 3 bedrooms and 2 bathrooms; Excellent school rating of 8.5/10; Reasonable commute time of 20 minutes; Modern home built in 2010; Features: pool, garage"
    }
  ],
  "total_properties_evaluated": 20,
  "model_used": true
}
```

### `GET /api/health`
Health check endpoint.

### `GET /api/properties`
Get all available properties (for testing).

## How It Works

1. **Property Generation**: The system generates mock property data (20 properties by default)

2. **Price Prediction**: Each property's price is predicted using:
   - The ML model (`complex_price_model_v2.pkl`) if available
   - A fallback heuristic-based prediction if model is not loaded

3. **Scoring**: Properties are scored using a weighted formula (0-100):
   - **Price Match Score (30%)**: How well the price fits your budget
   - **Bedroom Score (20%)**: Whether it meets your minimum bedroom requirement
   - **School Rating Score (15%)**: Quality of nearby schools (0-10 scale)
   - **Commute Score (15%)**: Commute time to work/center (shorter = better)
   - **Property Age Score (10%)**: Age of the property (newer = better)
   - **Amenities Score (10%)**: Presence of pool, garage, and garden
   
   **Total Score Formula:**
   ```
   total_score = (
       0.3 × price_match_score +
       0.2 × bedroom_score +
       0.15 × school_rating_score +
       0.15 × commute_score +
       0.1 × property_age_score +
       0.1 × amenities_score
   )
   ```

4. **Ranking**: Properties are sorted by match score and top 2-3 are returned

5. **Reasoning**: Each recommendation includes human-readable reasoning explaining why it was selected

## Model Integration

### Model Loading

The model is loaded automatically when the Flask app starts. The system tries multiple loading methods:
1. **joblib** (preferred for scikit-learn models)
2. **pickle with class workaround** (handles custom classes using `ComplexTrapModelRenamed` from `model_wrapper.py`)
3. **standard pickle**

The `ComplexTrapModelRenamed` class is defined in `model_wrapper.py` and acts as a wrapper for pickled models that use custom class definitions. This allows the model to be loaded even when the original class definition is not available.

### Model Prediction

The model is called in the `predict_price()` function (located at `app.py` line 150). 

**Model Call Location:** `app.py` line 169
```python
prediction = model.predict(features_array)[0]
```

**Expected Features (in order):**
- Bedrooms
- Bathrooms
- Square feet
- Year built
- Zip code
- Lot size

If your model uses different features, modify the `predict_price()` function in `app.py` (lines 156-163).

## Project Structure

```
.
├── app.py                 # Flask backend API
├── model_wrapper.py       # Model wrapper class for custom model loading
├── static/
│   ├── index.html        # Frontend HTML
│   ├── style.css         # Styling
│   └── app.js            # Frontend JavaScript
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── complex_price_model_v2.pkl  # ML model (optional)
```

## Troubleshooting

### Model Loading Issues

If you see an error like `Can't get attribute 'ComplexTrapModelRenamed'`:

1. **The system will automatically try multiple loading methods:**
   - First tries `joblib` (common for scikit-learn models)
   - Then tries `pickle` with a class workaround
   - Finally tries standard `pickle`

2. **If all methods fail:**
   - The system will continue using fallback predictions
   - Your application will still work, but without ML-based price predictions
   - Check the console output for detailed error messages

3. **To fix the model loading:**
   - If you have the original model training code, include the `ComplexTrapModelRenamed` class definition in `app.py`
   - Alternatively, re-save the model using `joblib.dump()` instead of `pickle.dump()` for better compatibility
   - Or provide the original class definition and we can integrate it

4. **Install joblib** (if not already installed):
   ```bash
   pip install joblib>=1.3.0
   ```

## Scoring Details

### Component Score Calculations

1. **Price Match Score:**
   - 100 if price ≤ budget
   - Decreases proportionally if price > budget

2. **Bedroom Score:**
   - 100 if bedrooms ≥ minimum required
   - Proportional score if below minimum

3. **School Rating Score:**
   - Calculated as (rating / 10) × 100

4. **Commute Score:**
   - ≤15 min: 100
   - ≤30 min: 80
   - ≤45 min: 50
   - >45 min: 20

5. **Property Age Score:**
   - ≤5 years: 100
   - ≤15 years: 80
   - ≤30 years: 60
   - >30 years: 40

6. **Amenities Score:**
   - Calculated as (pool + garage + garden) / 3 × 100

## Notes

- The system uses mock property data for demonstration. In production, you would connect to a real property database.
- If the ML model file is not present or cannot be loaded, the system uses a fallback prediction method.
- The recommendation algorithm can be customized by modifying the `calculate_match_score()` function in `app.py`.
- Property images are sourced from Unsplash and include automatic fallback handling for broken images.

