"""
Quick test to verify the recession model can calculate a probability.
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from forecasts.us_recession_2025.model import RecessionModel

def test_model_calculation():
    """Test that the model can calculate a probability."""
    print("Testing recession model calculation...")
    
    model = RecessionModel()
    print(f"✓ Model initialized: {model.get_name()}")
    
    # Try to calculate probability
    probability = model.calculate_probability()
    print(f"✓ Probability calculated: {probability:.4f}")
    
    # Verify it's in valid range
    assert 0 <= probability <= 1, f"Probability {probability} not in range [0, 1]"
    print(f"✓ Probability is in valid range [0, 1]")
    
    print("\n✓ Model calculation test passed!")

if __name__ == '__main__':
    success = test_model_calculation()
    sys.exit(0 if success else 1)
