"""
Database utilities for the Polymarket Forecasting Simulator.

Provides SQLite connection management and common database operations
for storing and retrieving forecast results.
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


# Database file path
DB_PATH = Path(__file__).parent.parent / "data" / "forecasts.db"

# Ensure data directory exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """
    Get a SQLite database connection.
    
    Creates the database file if it doesn't exist and enables foreign keys.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable column access by name
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn


@contextmanager
def get_connection_context():
    """
    Context manager for database connections.
    
    Automatically commits on success and rolls back on error.
    
    Yields:
        sqlite3.Connection: Database connection object
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def create_forecast_table(forecast_name: str, schema: Optional[Dict[str, str]] = None) -> None:
    """
    Create a dedicated table for a forecast model.
    
    Creates a table following the standard pattern with probability, parameters,
    data_snapshot, and calculated_at columns. Additional columns can be specified
    via the schema parameter.
    
    Args:
        forecast_name: Name of the forecast (used as table name with 'forecast_' prefix)
        schema: Optional dict of additional column definitions (column_name: SQL_type)
    
    Example:
        create_forecast_table('us_recession_2025', {
            'yield_curve_value': 'REAL',
            'unemployment_rate': 'REAL'
        })
    """
    table_name = f"forecast_{forecast_name}"
    
    # Base columns that every forecast table has
    base_columns = """
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        probability REAL NOT NULL CHECK(probability >= 0 AND probability <= 1),
        parameters TEXT,
        data_snapshot TEXT,
        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """
    
    # Add custom columns if provided
    if schema:
        custom_columns = ",\n        ".join([f"{col} {dtype}" for col, dtype in schema.items()])
        columns = f"{base_columns},\n        {custom_columns}"
    else:
        columns = base_columns
    
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {columns}
    )
    """
    
    with get_connection_context() as conn:
        conn.execute(create_table_sql)
        logger.info(f"Created or verified table: {table_name}")


def save_forecast_result(
    forecast_name: str,
    probability: float,
    parameters: Optional[Dict[str, Any]] = None,
    data_snapshot: Optional[Dict[str, Any]] = None,
    additional_data: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> int:
    """
    Save a forecast result to the database.
    
    Args:
        forecast_name: Name of the forecast (table name without 'forecast_' prefix)
        probability: Calculated probability value (must be between 0 and 1)
        parameters: Optional dict of parameters used in calculation
        data_snapshot: Optional dict of input data used
        additional_data: Optional dict of additional columns to save
        timestamp: Optional timestamp (defaults to current time)
    
    Returns:
        int: ID of the inserted row
    
    Raises:
        ValueError: If probability is not between 0 and 1
    """
    if not 0 <= probability <= 1:
        raise ValueError(f"Probability must be between 0 and 1, got {probability}")
    
    table_name = f"forecast_{forecast_name}"
    
    # Prepare base data
    columns = ["probability", "parameters", "data_snapshot"]
    values = [
        probability,
        json.dumps(parameters) if parameters else None,
        json.dumps(data_snapshot) if data_snapshot else None
    ]
    
    # Add timestamp if provided
    if timestamp:
        columns.append("calculated_at")
        values.append(timestamp.isoformat())
    
    # Add additional columns if provided
    if additional_data:
        for col, val in additional_data.items():
            columns.append(col)
            values.append(val)
    
    # Build INSERT statement
    placeholders = ", ".join(["?" for _ in values])
    columns_str = ", ".join(columns)
    insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
    
    with get_connection_context() as conn:
        cursor = conn.execute(insert_sql, values)
        row_id = cursor.lastrowid
        logger.info(f"Saved forecast result to {table_name} with ID {row_id}")
        return row_id


def get_forecast_history(
    forecast_name: str,
    limit: Optional[int] = None,
    order_by: str = "calculated_at DESC"
) -> List[Dict[str, Any]]:
    """
    Retrieve historical forecast results.
    
    Args:
        forecast_name: Name of the forecast (table name without 'forecast_' prefix)
        limit: Optional maximum number of results to return
        order_by: SQL ORDER BY clause (default: most recent first)
    
    Returns:
        List of dicts containing forecast results
    """
    table_name = f"forecast_{forecast_name}"
    
    query = f"SELECT * FROM {table_name} ORDER BY {order_by}"
    if limit:
        query += f" LIMIT {limit}"
    
    with get_connection_context() as conn:
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        
        # Convert rows to dicts and parse JSON fields
        results = []
        for row in rows:
            result = dict(row)
            # Parse JSON fields
            if result.get('parameters'):
                try:
                    result['parameters'] = json.loads(result['parameters'])
                except json.JSONDecodeError:
                    pass
            if result.get('data_snapshot'):
                try:
                    result['data_snapshot'] = json.loads(result['data_snapshot'])
                except json.JSONDecodeError:
                    pass
            results.append(result)
        
        return results


def initialize_metadata_table() -> None:
    """
    Create the forecast_metadata table if it doesn't exist.
    
    This table stores metadata about all forecast models in the system.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS forecast_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        display_name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_updated TIMESTAMP
    )
    """
    
    with get_connection_context() as conn:
        conn.execute(create_table_sql)
        logger.info("Created or verified forecast_metadata table")


def execute_query(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """
    Execute an arbitrary SQL query.
    
    Args:
        query: SQL query string
        params: Optional tuple of parameters for parameterized queries
    
    Returns:
        List of dicts containing query results
    """
    with get_connection_context() as conn:
        cursor = conn.execute(query, params or ())
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# Initialize metadata table on module import
initialize_metadata_table()
