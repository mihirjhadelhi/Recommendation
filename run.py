"""
Main entry point for the Property Recommendation System.

This script initializes and runs the Flask application.
"""
from app import create_app
import config

if __name__ == '__main__':
    app = create_app()
    
    print("Starting Property Recommendation API...")
    print(f"Server will run on http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )

