"""
Polymarket Forecasting Simulator - Forecast Models

This package contains individual forecast models, each in its own directory.
Each forecast model implements the ForecastModel interface.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional, List
import os
import sys
import importlib
import logging


logger = logging.getLogger(__name__)


class ForecastModel(ABC):
    """Base interface for all forecast models"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return human-readable forecast name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return forecast description"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict:
        """Return adjustable parameters with metadata"""
        pass
    
    @abstractmethod
    def calculate_probability(self, params: Optional[Dict] = None) -> float:
        """Calculate and return probability (0-1)"""
        pass
    
    @abstractmethod
    def get_last_updated(self) -> datetime:
        """Return timestamp of last data update"""
        pass
    
    @abstractmethod
    def get_data_sources(self) -> List[str]:
        """Return list of data sources used by this forecast"""
        pass


class ForecastRegistry:
    """
    Registry for discovered forecast models.
    
    Maintains a collection of discovered and instantiated forecast models,
    providing methods to access them by name.
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._forecasts: Dict[str, ForecastModel] = {}
    
    def register(self, directory_name: str, model_instance: ForecastModel) -> None:
        """
        Register a forecast model instance.
        
        Args:
            directory_name: The directory name (used as key)
            model_instance: The instantiated ForecastModel
        """
        self._forecasts[directory_name] = model_instance
        logger.info(f"Registered forecast: {directory_name}")
    
    def get(self, directory_name: str) -> Optional[ForecastModel]:
        """
        Get a forecast model by directory name.
        
        Args:
            directory_name: The directory name
            
        Returns:
            ForecastModel instance or None if not found
        """
        return self._forecasts.get(directory_name)
    
    def get_all(self) -> Dict[str, ForecastModel]:
        """
        Get all registered forecast models.
        
        Returns:
            Dictionary mapping directory names to ForecastModel instances
        """
        return self._forecasts.copy()
    
    def list_names(self) -> List[str]:
        """
        Get list of all registered forecast directory names.
        
        Returns:
            List of directory names
        """
        return list(self._forecasts.keys())
    
    def clear(self) -> None:
        """Clear all registered forecasts."""
        self._forecasts.clear()


def discover_forecasts(forecasts_dir: Optional[str] = None) -> ForecastRegistry:
    """
    Discover and load all valid forecast models from the forecasts directory.
    
    Scans the forecasts/ directory for subdirectories containing valid forecast
    models. A valid forecast model must:
    1. Be a subdirectory in forecasts/
    2. Contain a model.py file
    3. Have a class that inherits from ForecastModel
    
    Args:
        forecasts_dir: Optional path to forecasts directory. If None, uses
                      the forecasts/ directory relative to this file.
    
    Returns:
        ForecastRegistry containing all discovered and instantiated models
    """
    registry = ForecastRegistry()
    
    # Determine forecasts directory
    if forecasts_dir is None:
        forecasts_dir = os.path.dirname(os.path.abspath(__file__))
    
    logger.info(f"Scanning for forecast models in: {forecasts_dir}")
    
    # Check if directory exists
    if not os.path.isdir(forecasts_dir):
        logger.warning(f"Forecasts directory not found: {forecasts_dir}")
        return registry
    
    # Scan directory for subdirectories
    try:
        entries = os.listdir(forecasts_dir)
    except OSError as e:
        logger.error(f"Failed to list forecasts directory: {e}")
        return registry
    
    for entry in entries:
        # Skip special files and directories
        if entry.startswith('_') or entry.startswith('.'):
            continue
        
        entry_path = os.path.join(forecasts_dir, entry)
        
        # Only process directories
        if not os.path.isdir(entry_path):
            continue
        
        # Try to load the forecast model
        model = _load_forecast_model(entry, entry_path)
        if model is not None:
            registry.register(entry, model)
    
    logger.info(f"Discovered {len(registry.list_names())} forecast models")
    
    return registry


def _load_forecast_model(directory_name: str, directory_path: str) -> Optional[ForecastModel]:
    """
    Load a forecast model from a directory.
    
    Args:
        directory_name: Name of the directory
        directory_path: Full path to the directory
        
    Returns:
        Instantiated ForecastModel or None if loading fails
    """
    # Check for model.py file
    model_file = os.path.join(directory_path, 'model.py')
    if not os.path.isfile(model_file):
        logger.debug(f"Skipping {directory_name}: no model.py found")
        return None
    
    # Try to import the module
    try:
        module_name = f"forecasts.{directory_name}.model"
        module = None
        
        # Try standard import first (for installed forecasts)
        try:
            if module_name in sys.modules:
                # Reload if already imported
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)
        except (ImportError, ModuleNotFoundError):
            # If standard import fails, try loading from file path directly
            # This handles cases where the forecast is not in the Python path
            import importlib.util as util
            spec = util.spec_from_file_location(module_name, model_file)
            if spec is None or spec.loader is None:
                logger.warning(f"Skipping {directory_name}: could not create module spec")
                return None
            module = util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        
        if module is None:
            logger.warning(f"Skipping {directory_name}: module could not be loaded")
            return None
        
        # Find ForecastModel subclass in the module
        model_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            # Check if it's a class, subclass of ForecastModel, and not ForecastModel itself
            if (isinstance(attr, type) and 
                issubclass(attr, ForecastModel) and 
                attr is not ForecastModel):
                model_class = attr
                break
        
        if model_class is None:
            logger.warning(f"Skipping {directory_name}: no ForecastModel subclass found")
            return None
        
        # Instantiate the model
        model_instance = model_class()
        logger.info(f"Loaded forecast model: {directory_name} ({model_instance.get_name()})")
        
        return model_instance
        
    except Exception as e:
        logger.error(f"Failed to load forecast model from {directory_name}: {e}")
        return None
