"""
Unit tests for recession forecast database integration.

Tests the database table creation, insertion, and retrieval functionality.
"""

import pytest
from datetime import datetime
from lib.database import (
    create_forecast_table,
    save_forecast_result,
    get_forecast_history,
    get_connection
)


def test_recession_table_exists():
    """Test that the us_recession_2025 table exists."""
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='forecast_us_recession_2025'"
        )
        result = cursor.fetchone()
    
    assert result is not None, "forecast_us_recession_2025 table should exist"
    assert result[0] == 'forecast_us_recession_2025'


def test_recession_table_schema():
    """Test that the us_recession_2025 table has the correct schema."""
    with get_connection() as conn:
        cursor = conn.execute("PRAGMA table_info(forecast_us_recession_2025)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    # Check required columns exist
    required_columns = {
        'id': 'INTEGER',
        'probability': 'REAL',
        'parameters': 'TEXT',
        'data_snapshot': 'TEXT',
        'calculated_at': 'TIMESTAMP',
        'yield_curve_value': 'REAL',
        'unemployment_rate': 'REAL',
        'gdp_growth': 'REAL',
        'consumer_confidence': 'REAL',
        'leading_indicators': 'REAL',
        'jobless_claims': 'REAL'
    }
    
    for col_name, col_type in required_columns.items():
        assert col_name in columns, f"Column {col_name} should exist"
        assert columns[col_name] == col_type, f"Column {col_name} should be {col_type}"


def test_insert_and_retrieve_forecast():
    """Test inserting and retrieving a forecast result."""
    # Prepare test data
    test_probability = 0.42
    test_params = {
        'yield_curve_weight': 0.35,
        'unemployment_weight': 0.25,
        'gdp_weight': 0.20,
        'confidence_weight': 0.10,
        'leading_indicators_weight': 0.10,
        'lookback_days': 365
    }
    test_indicators = {
        'yield_curve': 0.5,
        'unemployment': 4.2,
        'gdp': 2.8,
        'consumer_confidence': 88.0,
        'leading_indicators': 0.3,
        'jobless_claims': 215000.0
    }
    test_additional = {
        'yield_curve_value': 0.5,
        'unemployment_rate': 4.2,
        'gdp_growth': 2.8,
        'consumer_confidence': 88.0,
        'leading_indicators': 0.3,
        'jobless_claims': 215000.0
    }
    
    # Insert test record
    row_id = save_forecast_result(
        forecast_name='us_recession_2025',
        probability=test_probability,
        parameters=test_params,
        data_snapshot={'indicators': test_indicators},
        additional_data=test_additional
    )
    
    assert row_id > 0, "Should return valid row ID"
    
    # Retrieve the record
    history = get_forecast_history('us_recession_2025', limit=1)
    
    assert len(history) > 0, "Should retrieve at least one record"
    
    latest = history[0]
    
    # Verify the data
    assert latest['id'] == row_id, "Should retrieve the correct record"
    assert latest['probability'] == test_probability, "Probability should match"
    assert latest['parameters'] == test_params, "Parameters should match"
    assert 'indicators' in latest['data_snapshot'], "Data snapshot should contain indicators"
    assert latest['yield_curve_value'] == 0.5, "Yield curve value should match"
    assert latest['unemployment_rate'] == 4.2, "Unemployment rate should match"
    assert latest['calculated_at'] is not None, "Should have timestamp"


def test_probability_constraint():
    """Test that probability constraint is enforced."""
    # Test invalid probability > 1
    with pytest.raises(ValueError, match="Probability must be between 0 and 1"):
        save_forecast_result(
            forecast_name='us_recession_2025',
            probability=1.5,
            parameters={},
            data_snapshot={},
            additional_data={
                'yield_curve_value': 0.5,
                'unemployment_rate': 4.2,
                'gdp_growth': 2.8,
                'consumer_confidence': 88.0,
                'leading_indicators': 0.3,
                'jobless_claims': 215000.0
            }
        )
    
    # Test invalid probability < 0
    with pytest.raises(ValueError, match="Probability must be between 0 and 1"):
        save_forecast_result(
            forecast_name='us_recession_2025',
            probability=-0.1,
            parameters={},
            data_snapshot={},
            additional_data={
                'yield_curve_value': 0.5,
                'unemployment_rate': 4.2,
                'gdp_growth': 2.8,
                'consumer_confidence': 88.0,
                'leading_indicators': 0.3,
                'jobless_claims': 215000.0
            }
        )


def test_query_multiple_results():
    """Test querying multiple historical results."""
    # Insert multiple test records
    for i in range(3):
        save_forecast_result(
            forecast_name='us_recession_2025',
            probability=0.3 + i * 0.1,
            parameters={'test_run': i},
            data_snapshot={'test': True},
            additional_data={
                'yield_curve_value': 0.5,
                'unemployment_rate': 4.2,
                'gdp_growth': 2.8,
                'consumer_confidence': 88.0,
                'leading_indicators': 0.3,
                'jobless_claims': 215000.0
            }
        )
    
    # Query results
    history = get_forecast_history('us_recession_2025', limit=5)
    
    assert len(history) >= 3, "Should retrieve at least 3 records"
    
    # Verify they're ordered by most recent first
    timestamps = [h['calculated_at'] for h in history]
    assert timestamps == sorted(timestamps, reverse=True), "Should be ordered by timestamp descending"


def test_timestamp_auto_generation():
    """Test that timestamp is automatically generated if not provided."""
    row_id = save_forecast_result(
        forecast_name='us_recession_2025',
        probability=0.5,
        parameters={},
        data_snapshot={},
        additional_data={
            'yield_curve_value': 0.5,
            'unemployment_rate': 4.2,
            'gdp_growth': 2.8,
            'consumer_confidence': 88.0,
            'leading_indicators': 0.3,
            'jobless_claims': 215000.0
        }
    )
    
    # Retrieve the specific record by ID
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM forecast_us_recession_2025 WHERE id = ?",
            (row_id,)
        )
        row = cursor.fetchone()
    
    assert row is not None, "Should find the inserted record"
    
    # Verify timestamp exists and is parseable
    timestamp_str = row['calculated_at']
    assert timestamp_str is not None, "Timestamp should be auto-generated"
    
    # Parse timestamp to verify it's valid
    try:
        if 'T' in timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        
        # Verify it's a reasonable timestamp (within last day and not too far in future)
        now = datetime.now()
        time_diff = abs((now - timestamp.replace(tzinfo=None)).total_seconds())
        assert time_diff < 86400, f"Timestamp should be recent (within 24 hours), got {time_diff}s difference"
    except Exception as e:
        pytest.fail(f"Failed to parse timestamp: {e}")
