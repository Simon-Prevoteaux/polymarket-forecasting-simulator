# Election 2028 Forecast Model

## Overview

This forecast model predicts the probability of Democratic victory in the 2028 US Presidential Election.

**IMPORTANT: This is a DEMONSTRATION model using randomly generated data. It is NOT a real election forecast.**

## Purpose

This model exists to demonstrate that the Polymarket Forecasting Simulator can handle:
- Multiple different types of forecasts
- Different data sources
- Different indicators
- Different calculation methods

## Data Sources (In Production)

In a real implementation, this model would fetch data from:

1. **Polling Data**
   - RealClearPolitics polling averages
   - FiveThirtyEight polling aggregation
   - Individual state polls

2. **Economic Indicators**
   - GDP growth rate
   - Unemployment rate
   - Consumer confidence
   - Stock market performance

3. **Approval Ratings**
   - Gallup presidential approval
   - Generic ballot polling

4. **Campaign Metrics**
   - FEC fundraising data
   - Campaign spending
   - Ground game metrics

5. **Historical Patterns**
   - Past election results
   - Incumbent party performance
   - Midterm election results

## Current Implementation

The current implementation generates random data for demonstration purposes:
- Polling: 43-53% (centered around 48%)
- Economic Index: 85-115 (centered around 100)
- Approval: 37-53% (centered around 45%)
- Fundraising: $350-650M (centered around $500M)
- Historical Advantage: -3 to +3 points

## Model Parameters

Users can adjust the following weights:

- **polling_weight** (default: 0.40): Weight for polling data
- **economic_weight** (default: 0.25): Weight for economic indicators
- **approval_weight** (default: 0.20): Weight for approval ratings
- **fundraising_weight** (default: 0.10): Weight for fundraising data
- **historical_weight** (default: 0.05): Weight for historical patterns

## Calculation Method

The model:
1. Fetches all indicator values
2. Converts each to a probability signal using logistic transformation
3. Combines signals using weighted average
4. Normalizes to ensure result is in [0, 1]

## Usage

This model is automatically discovered by the web interface and can be accessed at:
- Web: http://localhost:5001/forecast/election_2028
- API: http://localhost:5001/api/forecast/election_2028/simulate

## Future Enhancements

To make this a real forecast model:
1. Replace dummy data with real API calls
2. Add state-by-state electoral college modeling
3. Incorporate primary results and candidate-specific factors
4. Add uncertainty quantification
5. Include expert predictions and prediction markets
