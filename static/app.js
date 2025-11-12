const API_BASE_URL = 'http://localhost:5000/api';

document.getElementById('preferencesForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Hide previous results and errors
    document.getElementById('results').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');
    
    // Show loading
    document.getElementById('loading').classList.remove('hidden');
    
    // Collect form data
    const preferences = {
        budget: parseFloat(document.getElementById('budget').value),
        location: document.getElementById('location').value.trim(),
        min_bedrooms: parseInt(document.getElementById('min_bedrooms').value),
        min_bathrooms: parseInt(document.getElementById('min_bathrooms').value),
        min_square_feet: parseInt(document.getElementById('min_square_feet').value)
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ preferences })
        });
        
        const data = await response.json();
        
        // Hide loading
        document.getElementById('loading').classList.add('hidden');
        
        if (data.success) {
            displayRecommendations(data.recommendations);
        } else {
            showError(data.error || 'Failed to get recommendations');
        }
    } catch (error) {
        document.getElementById('loading').classList.add('hidden');
        showError(`Error: ${error.message}. Make sure the backend server is running on port 5000.`);
    }
});

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendationsContainer');
    container.innerHTML = '';
    
    if (recommendations.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: white; padding: 20px;">No recommendations found. Try adjusting your preferences.</p>';
        document.getElementById('results').classList.remove('hidden');
        return;
    }
    
    recommendations.forEach((property, index) => {
        const card = createRecommendationCard(property, index + 1);
        container.appendChild(card);
    });
    
    document.getElementById('results').classList.remove('hidden');
}

function createRecommendationCard(property, rank) {
    const card = document.createElement('div');
    card.className = 'recommendation-card';
    
    const price = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
    }).format(property.predicted_price);
    
    // Fallback image URL in case the primary image fails to load
    const fallbackImageUrl = 'https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?w=800&h=600&fit=crop';
    const imageUrl = property.image_url || fallbackImageUrl;
    
    card.innerHTML = `
        <div class="property-image-container">
            <img src="${imageUrl}" 
                 alt="${property.address}" 
                 class="property-image" 
                 loading="lazy"
                 onerror="this.onerror=null; this.src='${fallbackImageUrl}';">
            <div class="match-score-badge">Match: ${property.match_score.toFixed(1)}%</div>
        </div>
        
        <div class="recommendation-header">
            <div class="recommendation-title">
                <h3>Recommendation #${rank}</h3>
                <div class="address">${property.address}, ${property.city}, ${property.state} ${property.zip_code}</div>
            </div>
        </div>
        
        <div class="price">${price}</div>
        
        <div class="property-details">
            <div class="detail-item">
                <span class="icon">🛏️</span>
                <div>
                    <div class="label">Bedrooms</div>
                    <div class="value">${property.bedrooms}</div>
                </div>
            </div>
            <div class="detail-item">
                <span class="icon">🚿</span>
                <div>
                    <div class="label">Bathrooms</div>
                    <div class="value">${property.bathrooms}</div>
                </div>
            </div>
            <div class="detail-item">
                <span class="icon">📐</span>
                <div>
                    <div class="label">Square Feet</div>
                    <div class="value">${property.square_feet.toLocaleString()}</div>
                </div>
            </div>
            <div class="detail-item">
                <span class="icon">🏗️</span>
                <div>
                    <div class="label">Year Built</div>
                    <div class="value">${property.year_built}</div>
                </div>
            </div>
            <div class="detail-item">
                <span class="icon">📏</span>
                <div>
                    <div class="label">Lot Size</div>
                    <div class="value">${property.lot_size.toLocaleString()} sqft</div>
                </div>
            </div>
            <div class="detail-item">
                <span class="icon">🎓</span>
                <div>
                    <div class="label">School Rating</div>
                    <div class="value">${property.school_rating}/10</div>
                </div>
            </div>
            <div class="detail-item">
                <span class="icon">🚗</span>
                <div>
                    <div class="label">Commute</div>
                    <div class="value">${property.commute_time} min</div>
                </div>
            </div>
        </div>
        
        ${getAmenitiesHTML(property)}
        
        <div class="reasoning">
            <h4>Why this property?</h4>
            <p>${property.reasoning}</p>
        </div>
    `;
    
    return card;
}

function getAmenitiesHTML(property) {
    const amenities = [];
    if (property.has_pool) amenities.push('🏊 Pool');
    if (property.has_garage) amenities.push('🚗 Garage');
    if (property.has_garden) amenities.push('🌳 Garden');
    
    if (amenities.length > 0) {
        return `
        <div class="amenities-section">
            <strong>Amenities:</strong> ${amenities.join(' • ')}
        </div>
        `;
    }
    return '';
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
}

