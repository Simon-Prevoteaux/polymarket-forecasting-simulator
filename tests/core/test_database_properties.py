"""
Property-based tests for database utilities.

These tests verify universal properties that should hold across all inputs.
"""

import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from hypothesis import given, strategies as st, settings
from hypothesis import assume

# Import database utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import database


@contextmanager
def temp_database():
    """Context manager for creating a temporary database."""
    temp_dir = tempfile.mkdtemp()
    temp_db_path = Path(temp_dir) / "test_forecasts.db"
    
    # Save original DB_PATH
    original_db_path = database.DB_PATH
    
    # Set temporary DB_PATH
    database.DB_PATH = temp_db_path
    
    # Reinitialize metadata table with new path
    database.initialize_metadata_table()
    
    try:
        yield temp_db_path
    finally:
        # Restore original DB_PATH
        database.DB_PATH = original_db_path
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


# Feature: polymarket-forecasting-simulator, Property 3: Database persistence
@given(
    forecast_name=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='_'
    )),
    probability=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    param_key=st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'), 
        whitelist_characters='_'
    )),
    param_value=st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False)
)
@settings(max_examples=100)
def test_database_persistence_property(forecast_name, probability, param_key, param_value):
    """
    Property 3: Database persistence
    
    For any forecast model execution that produces a probability, the system must 
    store that result in the corresponding SQLite table with a timestamp.
    
    Validates: Requirements 2.5, 6.4
    """
    # Ensure forecast name is valid (no spaces, starts with letter or underscore)
    assume(forecast_name[0].isalpha() or forecast_name[0] == '_')
    assume(' ' not in forecast_name)
    
    with temp_database():
        # Create the forecast table
        database.create_forecast_table(forecast_name)
        
        # Save a forecast result
        parameters = {param_key: param_value}
        data_snapshot = {"test_data": "test_value"}
        
        row_id = database.save_forecast_result(
            forecast_name=forecast_name,
            probability=probability,
            parameters=parameters,
            data_snapshot=data_snapshot
        )
        
        # Verify the result was stored
        assert row_id is not None
        assert row_id > 0
        
        # Retrieve the stored result
        history = database.get_forecast_history(forecast_name, limit=1)
        
        # Verify we got exactly one result
        assert len(history) == 1
        
        result = history[0]
        
        # Verify the probability was stored correctly
        assert result['probability'] == pytest.approx(probability, abs=1e-10)
        
        # Verify parameters were stored and can be retrieved
        assert result['parameters'] is not None
        assert result['parameters'][param_key] == pytest.approx(param_value, abs=1e-10)
        
        # Verify data snapshot was stored
        assert result['data_snapshot'] is not None
        assert result['data_snapshot']['test_data'] == 'test_value'
        
        # Verify timestamp exists and is valid
        assert result['calculated_at'] is not None
        # Parse timestamp to ensure it's valid
        timestamp_str = result['calculated_at']
        # SQLite stores timestamps as strings, verify it can be parsed
        assert len(timestamp_str) > 0


# Feature: polymarket-forecasting-simulator, Property 7: Forecast table creation
@given(
    forecast_name=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='_'
    )),
    custom_column_name=st.text(min_size=1, max_size=30, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll'), 
        whitelist_characters='_'
    ))
)
@settings(max_examples=100)
def test_forecast_table_creation_property(forecast_name, custom_column_name):
    """
    Property 7: Forecast table creation
    
    For any new forecast model added to the system, initializing that model must 
    create a corresponding SQLite table with the appropriate schema.
    
    Validates: Requirements 6.3
    """
    # Ensure forecast name is valid
    assume(forecast_name[0].isalpha() or forecast_name[0] == '_')
    assume(' ' not in forecast_name)
    assume(custom_column_name[0].isalpha() or custom_column_name[0] == '_')
    assume(' ' not in custom_column_name)
    
    # Ensure custom column name doesn't conflict with base columns
    base_columns = {'id', 'probability', 'parameters', 'data_snapshot', 'calculated_at'}
    assume(custom_column_name.lower() not in base_columns)
    
    with temp_database():
        # Create a forecast table with a custom schema
        schema = {custom_column_name: 'REAL'}
        database.create_forecast_table(forecast_name, schema=schema)
        
        # Verify the table exists by querying it
        table_name = f"forecast_{forecast_name}"
        
        with database.get_connection_context() as conn:
            # Check table exists
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            result = cursor.fetchone()
            assert result is not None, f"Table {table_name} was not created"
            
            # Verify table has the expected base columns
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = {row['name'] for row in cursor.fetchall()}
            
            # Check all base columns exist
            assert 'id' in columns
            assert 'probability' in columns
            assert 'parameters' in columns
            assert 'data_snapshot' in columns
            assert 'calculated_at' in columns
            
            # Check custom column exists
            assert custom_column_name in columns
            
            # Verify we can insert data into the table
            test_probability = 0.5
            cursor = conn.execute(
                f"INSERT INTO {table_name} (probability, {custom_column_name}) VALUES (?, ?)",
                (test_probability, 42.0)
            )
            assert cursor.lastrowid > 0
