#!/usr/bin/env python3
"""Check what temporal metadata is actually returned by the model"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from forecasts.us_recession_2025.model_v2 import RecessionModelV2
import json

def main():
    print("Fetching breakdown data from RecessionModelV2...")
    
    model = RecessionModelV2()
    breakdown = model.get_probability_breakdown()
    
    print("\nTemporal Metadata:")
    print("=" * 60)
    print(json.dumps(breakdown.get('temporal_metadata', {}), indent=2))
    
    print("\n\nFull Breakdown Keys:")
    print("=" * 60)
    for key in breakdown.keys():
        print(f"  - {key}")
    
    print("\n\nBase vs Adjusted:")
    print("=" * 60)
    print(f"Base Probability: {breakdown.get('base_probability', 'N/A')}")
    print(f"Adjusted Probability: {breakdown.get('adjusted_probability', 'N/A')}")
    print(f"Days Remaining: {breakdown.get('days_remaining', 'N/A')}")

if __name__ == '__main__':
    main()
