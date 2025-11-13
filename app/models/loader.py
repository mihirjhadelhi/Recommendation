"""
Model loading functionality for the Property Recommendation System.
"""
import os
import sys
from typing import Optional, Any
import config

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

from app.models.model_wrapper import ComplexTrapModelRenamed


class ModelLoader:
    """Handles loading of ML models with multiple fallback strategies."""
    
    def __init__(self):
        """Initialize the model loader."""
        self.model: Optional[Any] = None
        self.model_loaded: bool = False
    
    def load_model(self) -> bool:
        """
        Load the ML model using multiple strategies.
        
        Returns:
            bool: True if model was loaded successfully, False otherwise
        """
        model_path = config.MODEL_PATH
        
        if not os.path.exists(model_path):
            print(f"Model file {model_path} not found. Using fallback prediction.")
            self.model_loaded = False
            return False
        
        # Try multiple loading methods
        loading_methods = []
        
        # Method 1: Try joblib (common for scikit-learn models)
        if JOBLIB_AVAILABLE:
            loading_methods.append(('joblib', lambda: joblib.load(model_path)))
        
        # Method 2: Try pickle with custom class handling
        def load_with_pickle():
            # Register the class in sys.modules so pickle can find it
            if '__main__' in sys.modules:
                main_module = sys.modules['__main__']
                if not hasattr(main_module, 'ComplexTrapModelRenamed'):
                    setattr(main_module, 'ComplexTrapModelRenamed', ComplexTrapModelRenamed)
            
            # Also make sure it's available in the current module and model_wrapper
            current_module = sys.modules[__name__]
            if not hasattr(current_module, 'ComplexTrapModelRenamed'):
                setattr(current_module, 'ComplexTrapModelRenamed', ComplexTrapModelRenamed)
            
            # Register in model_wrapper module as well
            import app.models.model_wrapper as model_wrapper_module
            if not hasattr(model_wrapper_module, 'ComplexTrapModelRenamed'):
                setattr(model_wrapper_module, 'ComplexTrapModelRenamed', ComplexTrapModelRenamed)
            
            import pickle
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        
        loading_methods.append(('pickle with class workaround', load_with_pickle))
        
        # Method 3: Try standard pickle
        import pickle
        loading_methods.append(('pickle', lambda: pickle.load(open(model_path, 'rb'))))
        
        # Try each method
        for method_name, load_func in loading_methods:
            try:
                print(f"Attempting to load model using {method_name}...")
                model = load_func()
                
                # Verify the model has a predict method
                if hasattr(model, 'predict'):
                    self.model = model
                    self.model_loaded = True
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
        self.model_loaded = False
        return False

