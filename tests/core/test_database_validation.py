"""
Validation tests for database utilities.

Simple test script to verify database file creation, table creation,
and basic insert/retrieve operations.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib import database


def test_database_file_creation():
    """Verify that the database file is created."""
    print("Testing database file creation...")
    
    # The database file should be created when we import the module
    assert database.DB_PATH.exists(), f"Database file not found at {database.DB_PATH}"
    print(f"✓ Database file exists at: {database.DB_PATH}")


def test_metadata_table_exists():
    """Verify that the forecast_metadata table exists."""
    print("\nTesting metadata table existence...")
    
    with database.get_connection_context() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='forecast_metadata'"
        )
        result = cursor.fetchone()
        assert result is not None, "forecast_metadata table not found"
        print("✓ forecast_metadata table exists")


def test_create_test_table():
    """Test creating a test forecast table."""
    print("\nTesting table creation...")
    
    test_forecast_name = "test_validation"
    schema = {
        'test_value': 'REAL',
        'test_string': 'TEXT'
    }
    
    database.create_forecast_table(test_forecast_name, schema=schema)
    
    # Verify table was created
    table_name = f"forecast_{test_forecast_name}"
    with database.get_connection_context() as conn:
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        result = cursor.fetchone()
        assert result is not None, f"Table {table_name} was not created"
        print(f"✓ Table {table_name} created successfully")
        
        # Verify columns
        cursor = conn.execute(f"PRAGMA table_info({table_name})")
        columns = {row['name'] for row in cursor.fetchall()}
        
        expected_columns = {'id', 'probability', 'parameters', 'data_snapshot', 
                          'calculated_at', 'test_value', 'test_string'}
        assert expected_columns.issubset(columns), f"Missing columns. Expected {expected_columns}, got {columns}"
        print(f"✓ All expected columns present: {columns}")


def test_insert_and_retrieve_data():
    """Test inserting and retrieving forecast data."""
    print("\nTesting data insertion and retrieval...")
    
    test_forecast_name = "test_validation"
    
    # Insert test data
    probability = 0.75
    parameters = {'weight': 0.5, 'threshold': 10}
    data_snapshot = {'indicator1': 100, 'indicator2': 200}
    additional_data = {'test_value': 42.5, 'test_string': 'test'}
    
    row_id = database.save_forecast_result(
        forecast_name=test_forecast_name,
        probability=probability,
        parameters=parameters,
        data_snapshot=data_snapshot,
        additional_data=additional_data
    )
    
    assert row_id > 0, "Failed to insert data"
    print(f"✓ Data inserted with row ID: {row_id}")
    
    # Retrieve the data
    history = database.get_forecast_history(test_forecast_name, limit=1)
    
    assert len(history) == 1, f"Expected 1 result, got {len(history)}"
    result = history[0]
    
    # Verify data
    assert result['probability'] == probability, f"Probability mismatch: {result['probability']} != {probability}"
    assert result['parameters'] == parameters, f"Parameters mismatch: {result['parameters']} != {parameters}"
    assert result['data_snapshot'] == data_snapshot, f"Data snapshot mismatch"
    assert result['test_value'] == 42.5, f"test_value mismatch"
    assert result['test_string'] == 'test', f"test_string mismatch"
    assert result['calculated_at'] is not None, "Timestamp is None"
    
    print("✓ Data retrieved successfully")
    print(f"  - Probability: {result['probability']}")
    print(f"  - Parameters: {result['parameters']}")
    print(f"  - Data snapshot: {result['data_snapshot']}")
    print(f"  - Timestamp: {result['calculated_at']}")


def test_multiple_inserts():
    """Test inserting multiple records and retrieving history."""
    print("\nTesting multiple inserts...")
    
    test_forecast_name = "test_validation"
    
    # Insert multiple records
    for i in range(3):
        database.save_forecast_result(
            forecast_name=test_forecast_name,
            probability=0.5 + (i * 0.1),
            parameters={'iteration': i},
            data_snapshot={'value': i * 10}
        )
    
    # Retrieve all records
    history = database.get_forecast_history(test_forecast_name)
    
    # We should have at least 4 records (1 from previous test + 3 new ones)
    assert len(history) >= 4, f"Expected at least 4 records, got {len(history)}"
    print(f"✓ Multiple inserts successful. Total records: {len(history)}")
    
    # Verify they're ordered by most recent first
    print("  Recent records:")
    for i, record in enumerate(history[:3]):
        print(f"    {i+1}. Probability: {record['probability']}, Timestamp: {record['calculated_at']}")


def run_all_tests():
    """Run all validation tests."""
    print("=" * 70)
    print("DATABASE UTILITIES VALIDATION")
    print("=" * 70)
    
    try:
        test_database_file_creation()
        test_metadata_table_exists()
        test_create_test_table()
        test_insert_and_retrieve_data()
        test_multiple_inserts()
        
        print("\n" + "=" * 70)
        print("ALL VALIDATION TESTS PASSED ✓")
        print("=" * 70)
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
