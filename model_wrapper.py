"""
Model wrapper class for loading pickled models with custom classes.

This module provides the ComplexTrapModelRenamed class which acts as a wrapper
for pickled models that use custom class definitions. This allows the model
to be loaded even when the original class definition is not available.
"""


class ComplexTrapModelRenamed:
    """
    Generic model wrapper class for handling pickled models with custom classes.
    
    This class allows pickle to deserialize models even when the original class
    definition is not available. It automatically detects and wraps the underlying
    model (e.g., scikit-learn estimators) and delegates prediction calls to it.
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the model wrapper.
        
        Args:
            *args: Positional arguments for the model
            **kwargs: Keyword arguments for the model
        """
        # Store any initialization data
        if args:
            self._args = args
        if kwargs:
            self._kwargs = kwargs
        # Try to extract underlying model if it exists
        for attr in ['model', '_model', 'estimator', '_estimator', 'base_estimator']:
            if hasattr(self, attr):
                underlying = getattr(self, attr)
                if hasattr(underlying, 'predict'):
                    self._underlying_model = underlying
                    break
    
    def predict(self, X):
        """
        Make predictions using the underlying model.
        
        Args:
            X: Feature array for prediction
            
        Returns:
            Model predictions
            
        Raises:
            NotImplementedError: If no underlying model with predict method is found
        """
        # Try to use underlying model if available
        if hasattr(self, '_underlying_model'):
            return self._underlying_model.predict(X)
        # Try to find any attribute with a predict method
        for attr_name in dir(self):
            if attr_name.startswith('_'):
                continue
            attr = getattr(self, attr_name)
            if hasattr(attr, 'predict'):
                return attr.predict(X)
        raise NotImplementedError("Model prediction not available - underlying model not found")
    
    def __getstate__(self):
        """Return the object's state for pickling."""
        return self.__dict__
    
    def __setstate__(self, state):
        """
        Restore the object's state from pickle.
        
        After unpickling, this method tries to find the actual underlying model
        that can perform predictions.
        
        Args:
            state: Dictionary containing the object's state
        """
        self.__dict__.update(state)
        # After unpickling, try to find the actual model
        for key, value in state.items():
            if hasattr(value, 'predict') and not key.startswith('__'):
                self._underlying_model = value
                break

