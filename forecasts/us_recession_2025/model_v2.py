"""
US Recession 2025 Forecast Model V2

Enhanced recession forecast model with:
- Additional economic indicators
- Feature engineering
- Temporal decay adjustment
- Backtesting support
"""

from datetime import datetime
from typing import Dict, Optional, Any, Tuple
from forecasts import ForecastModel
from lib.database import get_connection
import json


class RecessionModelV2(ForecastModel):
    """
    Enhanced recession forecast model with temporal decay.
    
    Extends v1 model with:
    - Additional economic indicators
    - Feature engineering
    - Temporal decay adjustment
    - Backtesting support
    """
    
    def __init__(self):
        """Initialize v2 model."""
        self.table_name = 'forecast_us_recession_2025_v2'
        self._create_table()
    
    def _create_table(self):
        """Create v2 forecast table if it doesn't exist."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                base_probability REAL NOT NULL CHECK(base_probability >= 0 AND base_probability <= 1),
                adjusted_probability REAL NOT NULL CHECK(adjusted_probability >= 0 AND adjusted_probability <= 1),
                days_remaining INTEGER,
                parameters TEXT,
                indicators TEXT,
                features TEXT,
                temporal_metadata TEXT,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_name(self) -> str:
        """Return human-readable forecast name."""
        return "us_recession_2025_v2"
    
    def get_description(self) -> str:
        """Return forecast description."""
        return "Enhanced US Recession 2025 forecast with temporal decay modeling and additional economic indicators"
    
    def get_parameters(self) -> Dict:
        """Return adjustable parameters with metadata."""
        # Will be implemented in later tasks
        return {}
    
    def calculate_probability(
        self,
        params: Optional[Dict] = None,
        as_of_date: Optional[datetime] = None,
        apply_temporal_decay: bool = True
    ) -> float:
        """
        Calculate recession probability with optional temporal adjustment.
        
        Args:
            params: Model parameters
            as_of_date: Date to calculate as of (for backtesting)
            apply_temporal_decay: Whether to apply temporal adjustment
        
        Returns:
            Final adjusted probability
        """
        # Will be implemented in later tasks
        return 0.0
    
    def calculate_base_probability(
        self,
        indicators: Dict,
        features: Dict,
        params: Dict
    ) -> float:
        """Calculate base probability before temporal adjustment."""
        # Will be implemented in later tasks
        return 0.0
    
    def get_probability_breakdown(
        self,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get detailed breakdown of probability calculation.
        
        Returns:
            - base_probability: Before temporal adjustment
            - adjusted_probability: After temporal adjustment
            - indicator_signals: Individual indicator contributions
            - feature_contributions: Feature importance
            - temporal_metadata: Decay adjustment details
        """
        # Will be implemented in later tasks
        return {}
    
    def get_last_updated(self) -> datetime:
        """Return timestamp of last data update."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT calculated_at FROM {self.table_name}
            ORDER BY calculated_at DESC LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return datetime.fromisoformat(result[0])
        return datetime.now()
    
    def get_data_sources(self) -> list:
        """Return list of data sources used by this forecast."""
        return [
            "Federal Reserve Economic Data (FRED)",
            "US Treasury Yield Curve",
            "Bureau of Labor Statistics",
            "Bureau of Economic Analysis",
            "University of Michigan Consumer Sentiment",
            "ISM Manufacturing PMI",
            "CBOE Volatility Index (VIX)"
        ]
