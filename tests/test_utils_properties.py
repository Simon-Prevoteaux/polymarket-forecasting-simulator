"""
Property-based tests for general utilities.

These tests verify universal properties that should hold across all inputs.
"""

import pytest
import sys
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.utils import validate_parameters, ParameterSchema


# Feature: polymarket-forecasting-simulator, Property 5: Parameter validation
@given(
    value=st.floats(
        min_value=0.0,
        max_value=1.0,
        allow_nan=False,
        allow_infinity=False
    )
)
@settings(max_examples=100)
def test_parameter_validation_accepts_valid_float_in_range(value):
    """
    Property 5: Parameter validation (valid float inputs)
    
    For any float parameter with defined constraints (min/max values),
    the system must accept inputs within those constraints.
    
    Validates: Requirements 5.4
    """
    schema = {
        'test_param': ParameterSchema(
            name='test_param',
            type='float',
            default=0.5,
            min_value=0.0,
            max_value=1.0
        )
    }
    
    params = {'test_param': value}
    errors = validate_parameters(params, schema)
    
    assert 'test_param' not in errors, \
        f"Valid value {value} in range [0.0, 1.0] was rejected: {errors.get('test_param')}"


# Feature: polymarket-forecasting-simulator, Property 5: Parameter validation
@given(
    value=st.one_of(
        st.floats(min_value=-1000.0, max_value=-0.01, allow_nan=False, allow_infinity=False),
        st.floats(min_value=1.01, max_value=1000.0, allow_nan=False, allow_infinity=False)
    )
)
@settings(max_examples=100)
def test_parameter_validation_rejects_invalid_float_out_of_range(value):
    """
    Property 5: Parameter validation (invalid float inputs)
    
    For any float parameter with defined constraints (min/max values),
    the system must reject inputs outside those constraints.
    
    Validates: Requirements 5.4
    """
    schema = {
        'test_param': ParameterSchema(
            name='test_param',
            type='float',
            default=0.5,
            min_value=0.0,
            max_value=1.0
        )
    }
    
    params = {'test_param': value}
    errors = validate_parameters(params, schema)
    
    assert 'test_param' in errors, \
        f"Invalid value {value} outside range [0.0, 1.0] was accepted"


# Feature: polymarket-forecasting-simulator, Property 5: Parameter validation
@given(
    value=st.integers(min_value=1, max_value=100)
)
@settings(max_examples=100)
def test_parameter_validation_accepts_valid_int_in_range(value):
    """
    Property 5: Parameter validation (valid int inputs)
    
    For any int parameter with defined constraints (min/max values),
    the system must accept inputs within those constraints.
    
    Validates: Requirements 5.4
    """
    schema = {
        'test_param': ParameterSchema(
            name='test_param',
            type='int',
            default=50,
            min_value=1,
            max_value=100
        )
    }
    
    params = {'test_param': value}
    errors = validate_parameters(params, schema)
    
    assert 'test_param' not in errors, \
        f"Valid value {value} in range [1, 100] was rejected: {errors.get('test_param')}"


# Feature: polymarket-forecasting-simulator, Property 5: Parameter validation
@given(
    value=st.one_of(
        st.integers(min_value=-1000, max_value=0),
        st.integers(min_value=101, max_value=1000)
    )
)
@settings(max_examples=100)
def test_parameter_validation_rejects_invalid_int_out_of_range(value):
    """
    Property 5: Parameter validation (invalid int inputs)
    
    For any int parameter with defined constraints (min/max values),
    the system must reject inputs outside those constraints.
    
    Validates: Requirements 5.4
    """
    schema = {
        'test_param': ParameterSchema(
            name='test_param',
            type='int',
            default=50,
            min_value=1,
            max_value=100
        )
    }
    
    params = {'test_param': value}
    errors = validate_parameters(params, schema)
    
    assert 'test_param' in errors, \
        f"Invalid value {value} outside range [1, 100] was accepted"


# Feature: polymarket-forecasting-simulator, Property 5: Parameter validation
@given(
    value=st.booleans()
)
@settings(max_examples=100)
def test_parameter_validation_accepts_valid_bool(value):
    """
    Property 5: Parameter validation (valid bool inputs)
    
    For any bool parameter, the system must accept boolean inputs.
    
    Validates: Requirements 5.4
    """
    schema = {
        'test_param': ParameterSchema(
            name='test_param',
            type='bool',
            default=True
        )
    }
    
    params = {'test_param': value}
    errors = validate_parameters(params, schema)
    
    assert 'test_param' not in errors, \
        f"Valid boolean value {value} was rejected: {errors.get('test_param')}"


# Feature: polymarket-forecasting-simulator, Property 5: Parameter validation
@given(
    value=st.sampled_from(['option_a', 'option_b', 'option_c'])
)
@settings(max_examples=100)
def test_parameter_validation_accepts_valid_select_option(value):
    """
    Property 5: Parameter validation (valid select inputs)
    
    For any select parameter with allowed options, the system must accept
    inputs that are in the allowed options list.
    
    Validates: Requirements 5.4
    """
    schema = {
        'test_param': ParameterSchema(
            name='test_param',
            type='select',
            default='option_a',
            options=['option_a', 'option_b', 'option_c']
        )
    }
    
    params = {'test_param': value}
    errors = validate_parameters(params, schema)
    
    assert 'test_param' not in errors, \
        f"Valid option '{value}' was rejected: {errors.get('test_param')}"


# Feature: polymarket-forecasting-simulator, Property 5: Parameter validation
@given(
    value=st.text(min_size=1, max_size=20).filter(
        lambda x: x not in ['option_a', 'option_b', 'option_c']
    )
)
@settings(max_examples=100)
def test_parameter_validation_rejects_invalid_select_option(value):
    """
    Property 5: Parameter validation (invalid select inputs)
    
    For any select parameter with allowed options, the system must reject
    inputs that are not in the allowed options list.
    
    Validates: Requirements 5.4
    """
    schema = {
        'test_param': ParameterSchema(
            name='test_param',
            type='select',
            default='option_a',
            options=['option_a', 'option_b', 'option_c']
        )
    }
    
    params = {'test_param': value}
    errors = validate_parameters(params, schema)
    
    assert 'test_param' in errors, \
        f"Invalid option '{value}' not in allowed list was accepted"


# Feature: polymarket-forecasting-simulator, Property 5: Parameter validation
@given(
    value=st.text(min_size=0, max_size=100)
)
@settings(max_examples=100)
def test_parameter_validation_accepts_valid_string(value):
    """
    Property 5: Parameter validation (valid string inputs)
    
    For any string parameter, the system must accept string inputs.
    
    Validates: Requirements 5.4
    """
    schema = {
        'test_param': ParameterSchema(
            name='test_param',
            type='str',
            default='default_value'
        )
    }
    
    params = {'test_param': value}
    errors = validate_parameters(params, schema)
    
    assert 'test_param' not in errors, \
        f"Valid string value '{value}' was rejected: {errors.get('test_param')}"


# Feature: polymarket-forecasting-simulator, Property 5: Parameter validation
@given(
    wrong_type_value=st.one_of(
        st.integers(),
        st.booleans(),
        st.lists(st.integers())
    )
)
@settings(max_examples=100)
def test_parameter_validation_rejects_wrong_type_for_float(wrong_type_value):
    """
    Property 5: Parameter validation (type checking for float)
    
    For any float parameter, the system must reject inputs that are not
    numeric types (excluding int which can be converted to float).
    
    Validates: Requirements 5.4
    """
    # Skip if value is int (which is acceptable for float parameters)
    assume(not isinstance(wrong_type_value, int) or isinstance(wrong_type_value, bool))
    
    schema = {
        'test_param': ParameterSchema(
            name='test_param',
            type='float',
            default=0.5
        )
    }
    
    params = {'test_param': wrong_type_value}
    errors = validate_parameters(params, schema)
    
    assert 'test_param' in errors, \
        f"Wrong type value {wrong_type_value} ({type(wrong_type_value).__name__}) was accepted for float parameter"


# Feature: polymarket-forecasting-simulator, Property 5: Parameter validation
@given(
    wrong_type_value=st.one_of(
        st.floats(allow_nan=False, allow_infinity=False),
        st.text(),
        st.booleans()
    )
)
@settings(max_examples=100)
def test_parameter_validation_rejects_wrong_type_for_int(wrong_type_value):
    """
    Property 5: Parameter validation (type checking for int)
    
    For any int parameter, the system must reject inputs that are not
    integer types.
    
    Validates: Requirements 5.4
    """
    schema = {
        'test_param': ParameterSchema(
            name='test_param',
            type='int',
            default=50
        )
    }
    
    params = {'test_param': wrong_type_value}
    errors = validate_parameters(params, schema)
    
    assert 'test_param' in errors, \
        f"Wrong type value {wrong_type_value} ({type(wrong_type_value).__name__}) was accepted for int parameter"


# Additional property: Required parameters must be present
@given(
    param_name=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))
)
@settings(max_examples=100)
def test_parameter_validation_rejects_missing_required_parameter(param_name):
    """
    Property: Required parameters must be present
    
    For any required parameter, validation must fail if the parameter is missing.
    """
    schema = {
        param_name: ParameterSchema(
            name=param_name,
            type='float',
            default=0.5,
            required=True
        )
    }
    
    params = {}  # Empty params - missing required parameter
    errors = validate_parameters(params, schema)
    
    assert param_name in errors, \
        f"Missing required parameter '{param_name}' was not flagged as an error"


# Additional property: Optional parameters can be omitted
@given(
    param_name=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))
)
@settings(max_examples=100)
def test_parameter_validation_accepts_missing_optional_parameter(param_name):
    """
    Property: Optional parameters can be omitted
    
    For any optional parameter, validation must succeed if the parameter is missing.
    """
    schema = {
        param_name: ParameterSchema(
            name=param_name,
            type='float',
            default=0.5,
            required=False
        )
    }
    
    params = {}  # Empty params - missing optional parameter
    errors = validate_parameters(params, schema)
    
    assert param_name not in errors, \
        f"Missing optional parameter '{param_name}' was flagged as an error: {errors.get(param_name)}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
