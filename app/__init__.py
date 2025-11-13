"""
Property Recommendation System Application Package.

This package contains the Flask application and all its components.
"""
from flask import Flask, send_from_directory
from flask_cors import CORS
from pathlib import Path

from app.models.loader import ModelLoader
from app.routes.api import register_routes
import config

# Global model loader instance
_model_loader = None

# Base directory (parent of app package)
BASE_DIR = Path(__file__).parent.parent


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    global _model_loader
    
    # Configure Flask with static folder in the root directory
    app = Flask(
        __name__,
        static_folder=str(BASE_DIR / 'static'),
        static_url_path='/static'
    )
    CORS(app)
    
    # Initialize model loader
    _model_loader = ModelLoader()
    _model_loader.load_model()
    
    # Register routes
    register_routes(app, _model_loader)
    
    # Serve index.html at root
    @app.route('/')
    def index():
        """Serve the main index.html page."""
        return send_from_directory(app.static_folder, 'index.html')
    
    return app


def get_model_loader() -> ModelLoader:
    """
    Get the global model loader instance.
    
    Returns:
        ModelLoader: The model loader instance
    """
    return _model_loader

