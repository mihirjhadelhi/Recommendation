"""
Main entry point for the Property Recommendation System (backward compatibility).

This file maintains backward compatibility while using the new package structure.
For new deployments, use run.py instead.
"""
from app import create_app, get_model_loader
import config

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    model_loader = get_model_loader()
    print("Starting Property Recommendation API...")
    print(f"Model loaded: {model_loader.model_loaded if model_loader else False}")
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )
