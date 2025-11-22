"""
Backtesting engine for US Recession 2025 Forecast V2

Runs model on historical data to evaluate performance.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
from lib.database import get_connection
import json
import logging
import numpy as np


logger = logging.getLogger(__name__)


class BacktestEngine:
    """Engine for running historical backtests."""
    
    def __init__(self, model_version: str = 'v2'):
        """
        Initialize with model version to test.
        
        Args:
            model_version: 'v1' or 'v2'
        """
        self.model_version = model_version
        self.forecast_deadline = datetime(2025, 12, 31)
        self._create_backtest_table()
    
    def _create_backtest_table(self):
        """Create backtesting table if it doesn't exist."""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forecast_us_recession_2025_backtest (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backtest_date DATE NOT NULL,
                forecast_date DATE NOT NULL,
                model_version TEXT NOT NULL,
                base_probability REAL,
                adjusted_probability REAL,
                days_remaining INTEGER,
                parameters TEXT,
                indicators TEXT,
                features TEXT,
                temporal_metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(backtest_date, model_version)
            )
        ''')
        
        # Create indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_backtest_date 
            ON forecast_us_recession_2025_backtest(backtest_date)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_model_version 
            ON forecast_us_recession_2025_backtest(model_version)
        ''')
        
        conn.commit()
        conn.close()
    
    def run_backtest(
        self,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'weekly',
        model_instance = None,
        params: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Run model on historical dates.
        
        Args:
            start_date: First date to backtest
            end_date: Last date to backtest
            frequency: 'daily', 'weekly', or 'monthly'
            model_instance: Instance of the model to backtest (v1 or v2)
            params: Optional parameters to pass to the model
        
        Returns:
            List of backtest results with probabilities and metadata
        """
        if model_instance is None:
            raise ValueError("model_instance is required for backtesting")
        
        # Generate backtest dates based on frequency
        backtest_dates = self._generate_backtest_dates(start_date, end_date, frequency)
        
        logger.info(
            f"Running backtest for {self.model_version} from {start_date.date()} "
            f"to {end_date.date()} with {frequency} frequency ({len(backtest_dates)} dates)"
        )
        
        results = []
        successful = 0
        failed = 0
        
        for backtest_date in backtest_dates:
            try:
                # Calculate days remaining until forecast deadline
                days_remaining = (self.forecast_deadline - backtest_date).days
                
                # Run model as of this historical date
                if self.model_version == 'v2':
                    # V2 model supports as_of_date parameter
                    probability = model_instance.calculate_probability(
                        params=params,
                        as_of_date=backtest_date,
                        apply_temporal_decay=True
                    )
                    
                    # Get breakdown for v2
                    breakdown = model_instance.get_probability_breakdown(params=params)
                    base_probability = breakdown.get('base_probability', probability)
                    adjusted_probability = breakdown.get('adjusted_probability', probability)
                    indicators = breakdown.get('indicators', {})
                    features = breakdown.get('features', {})
                    temporal_metadata = breakdown.get('temporal_metadata', {})
                else:
                    # V1 model doesn't support as_of_date, so we can't truly backtest it
                    # This is a limitation - we'd need to modify v1 or use current data
                    logger.warning(
                        f"V1 model doesn't support historical backtesting at {backtest_date.date()}"
                    )
                    continue
                
                # Store result
                result = {
                    'backtest_date': backtest_date,
                    'forecast_date': self.forecast_deadline,
                    'model_version': self.model_version,
                    'base_probability': base_probability,
                    'adjusted_probability': adjusted_probability,
                    'days_remaining': days_remaining,
                    'parameters': params or {},
                    'indicators': indicators,
                    'features': features,
                    'temporal_metadata': temporal_metadata
                }
                
                # Save to database
                self._save_backtest_result(result)
                results.append(result)
                successful += 1
                
                logger.debug(
                    f"Backtest {backtest_date.date()}: "
                    f"base={base_probability:.4f}, adjusted={adjusted_probability:.4f}"
                )
                
            except Exception as e:
                logger.error(f"Failed to backtest {backtest_date.date()}: {e}")
                failed += 1
                continue
        
        logger.info(
            f"Backtest complete: {successful} successful, {failed} failed"
        )
        
        return results
    
    def _generate_backtest_dates(
        self,
        start_date: datetime,
        end_date: datetime,
        frequency: str
    ) -> List[datetime]:
        """
        Generate list of dates to backtest based on frequency.
        
        Args:
            start_date: First date
            end_date: Last date
            frequency: 'daily', 'weekly', or 'monthly'
        
        Returns:
            List of datetime objects
        """
        dates = []
        current_date = start_date
        
        if frequency == 'daily':
            delta = timedelta(days=1)
        elif frequency == 'weekly':
            delta = timedelta(weeks=1)
        elif frequency == 'monthly':
            # Approximate monthly as 30 days
            delta = timedelta(days=30)
        else:
            raise ValueError(f"Invalid frequency: {frequency}. Must be 'daily', 'weekly', or 'monthly'")
        
        while current_date <= end_date:
            dates.append(current_date)
            current_date += delta
        
        return dates
    
    def _save_backtest_result(self, result: Dict[str, Any]) -> None:
        """
        Save backtest result to database.
        
        Args:
            result: Backtest result dictionary
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO forecast_us_recession_2025_backtest
                (backtest_date, forecast_date, model_version, base_probability,
                 adjusted_probability, days_remaining, parameters, indicators,
                 features, temporal_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result['backtest_date'].strftime('%Y-%m-%d'),
                result['forecast_date'].strftime('%Y-%m-%d'),
                result['model_version'],
                result['base_probability'],
                result['adjusted_probability'],
                result['days_remaining'],
                json.dumps(result['parameters']),
                json.dumps(result['indicators']),
                json.dumps(result['features']),
                json.dumps(result['temporal_metadata'])
            ))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to save backtest result: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def get_backtest_results(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        model_version: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve backtest results from database.
        
        Args:
            start_date: Optional filter for start date
            end_date: Optional filter for end date
            model_version: Optional filter for model version
        
        Returns:
            List of backtest results
        """
        conn = get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT backtest_date, forecast_date, model_version, base_probability,
                   adjusted_probability, days_remaining, parameters, indicators,
                   features, temporal_metadata, created_at
            FROM forecast_us_recession_2025_backtest
            WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += ' AND backtest_date >= ?'
            params.append(start_date.strftime('%Y-%m-%d'))
        
        if end_date:
            query += ' AND backtest_date <= ?'
            params.append(end_date.strftime('%Y-%m-%d'))
        
        if model_version:
            query += ' AND model_version = ?'
            params.append(model_version)
        
        query += ' ORDER BY backtest_date ASC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'backtest_date': datetime.strptime(row[0], '%Y-%m-%d'),
                'forecast_date': datetime.strptime(row[1], '%Y-%m-%d'),
                'model_version': row[2],
                'base_probability': row[3],
                'adjusted_probability': row[4],
                'days_remaining': row[5],
                'parameters': json.loads(row[6]) if row[6] else {},
                'indicators': json.loads(row[7]) if row[7] else {},
                'features': json.loads(row[8]) if row[8] else {},
                'temporal_metadata': json.loads(row[9]) if row[9] else {},
                'created_at': row[10]
            })
        
        return results
    
    def calculate_performance_metrics(
        self,
        backtest_results: List[Dict],
        actual_recession_periods: List[Tuple[datetime, datetime]]
    ) -> Dict[str, float]:
        """
        Calculate performance metrics.
        
        Args:
            backtest_results: List of backtest results
            actual_recession_periods: List of (start, end) tuples for recessions
        
        Returns:
            Dictionary with metrics:
            - brier_score: Mean squared error of probability forecasts
            - calibration_slope: Calibration slope (ideally 1.0)
            - calibration_intercept: Calibration intercept (ideally 0.0)
            - sharpness: Standard deviation of forecasts
            - mean_probability: Average forecast probability
            - num_forecasts: Number of forecasts evaluated
        """
        if not backtest_results:
            logger.warning("No backtest results provided for metrics calculation")
            return {
                'brier_score': None,
                'calibration_slope': None,
                'calibration_intercept': None,
                'sharpness': None,
                'mean_probability': None,
                'num_forecasts': 0
            }
        
        # Extract probabilities (use adjusted_probability if available, else base)
        probabilities = []
        outcomes = []
        
        for result in backtest_results:
            prob = result.get('adjusted_probability') or result.get('base_probability')
            if prob is not None:
                probabilities.append(prob)
                
                # Determine if there was a recession at the backtest date
                backtest_date = result['backtest_date']
                in_recession = self._is_in_recession(backtest_date, actual_recession_periods)
                outcomes.append(1.0 if in_recession else 0.0)
        
        if not probabilities:
            logger.warning("No valid probabilities found in backtest results")
            return {
                'brier_score': None,
                'calibration_slope': None,
                'calibration_intercept': None,
                'sharpness': None,
                'mean_probability': None,
                'num_forecasts': 0
            }
        
        probabilities = np.array(probabilities)
        outcomes = np.array(outcomes)
        
        # Calculate Brier score: mean squared error
        brier_score = np.mean((probabilities - outcomes) ** 2)
        
        # Calculate sharpness: standard deviation of forecasts
        sharpness = np.std(probabilities)
        
        # Calculate mean probability
        mean_probability = np.mean(probabilities)
        
        # Calculate calibration (linear regression of outcomes on probabilities)
        # This requires at least some variation in probabilities
        calibration_slope = None
        calibration_intercept = None
        
        if len(probabilities) > 1 and np.std(probabilities) > 0:
            try:
                # Simple linear regression: outcome = intercept + slope * probability
                # Using numpy's polyfit
                coeffs = np.polyfit(probabilities, outcomes, 1)
                calibration_slope = coeffs[0]
                calibration_intercept = coeffs[1]
            except Exception as e:
                logger.warning(f"Failed to calculate calibration: {e}")
        
        return {
            'brier_score': float(brier_score),
            'calibration_slope': float(calibration_slope) if calibration_slope is not None else None,
            'calibration_intercept': float(calibration_intercept) if calibration_intercept is not None else None,
            'sharpness': float(sharpness),
            'mean_probability': float(mean_probability),
            'num_forecasts': len(probabilities)
        }
    
    def _is_in_recession(
        self,
        date: datetime,
        recession_periods: List[Tuple[datetime, datetime]]
    ) -> bool:
        """
        Check if a date falls within any recession period.
        
        Args:
            date: Date to check
            recession_periods: List of (start, end) tuples
        
        Returns:
            True if date is in a recession period
        """
        for start, end in recession_periods:
            if start <= date <= end:
                return True
        return False
    
    def compare_models(
        self,
        v1_results: List[Dict],
        v2_results: List[Dict],
        actual_recession_periods: List[Tuple[datetime, datetime]]
    ) -> Dict[str, Any]:
        """
        Compare performance of v1 vs v2 models.
        
        Args:
            v1_results: V1 backtest results
            v2_results: V2 backtest results
            actual_recession_periods: List of (start, end) tuples for recessions
        
        Returns:
            Dictionary with comparison metrics including:
            - v1_metrics: Performance metrics for v1
            - v2_metrics: Performance metrics for v2
            - brier_score_improvement: Difference in Brier scores (negative is better for v2)
            - relative_improvement: Percentage improvement in Brier score
        """
        # Calculate metrics for each model
        v1_metrics = self.calculate_performance_metrics(v1_results, actual_recession_periods)
        v2_metrics = self.calculate_performance_metrics(v2_results, actual_recession_periods)
        
        # Calculate improvement
        brier_improvement = None
        relative_improvement = None
        
        if (v1_metrics['brier_score'] is not None and 
            v2_metrics['brier_score'] is not None):
            brier_improvement = v1_metrics['brier_score'] - v2_metrics['brier_score']
            
            # Relative improvement as percentage
            if v1_metrics['brier_score'] > 0:
                relative_improvement = (brier_improvement / v1_metrics['brier_score']) * 100
        
        return {
            'v1_metrics': v1_metrics,
            'v2_metrics': v2_metrics,
            'brier_score_improvement': brier_improvement,
            'relative_improvement_pct': relative_improvement,
            'v2_is_better': brier_improvement > 0 if brier_improvement is not None else None
        }
