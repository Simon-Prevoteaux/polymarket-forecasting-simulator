/**
 * Polymarket Forecasting Simulator - Main JavaScript
 * 
 * This file provides client-side functionality for the web interface.
 * Includes parameter adjustment controls and simulation functionality.
 */

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Polymarket Forecasting Simulator initialized');
    
    // Initialize parameter controls
    initializeParameterControls();
    
    // Initialize temporal decay chart if data is available
    initializeTemporalDecayChart();
});

/**
 * Initialize parameter adjustment controls.
 * Sets up event listeners for sliders, number inputs, and buttons.
 */
function initializeParameterControls() {
    // Sync sliders with number inputs
    const sliders = document.querySelectorAll('.parameter-slider');
    sliders.forEach(slider => {
        const numberInput = document.getElementById(slider.id + '-value');
        if (numberInput) {
            // Update number input when slider changes
            slider.addEventListener('input', function() {
                numberInput.value = this.value;
            });
            
            // Update slider when number input changes
            numberInput.addEventListener('input', function() {
                slider.value = this.value;
            });
        }
    });
    
    // Reset to defaults button
    const resetButton = document.getElementById('reset-parameters');
    if (resetButton) {
        resetButton.addEventListener('click', resetParameters);
    }
    
    // Simulate button
    const simulateButton = document.getElementById('simulate-parameters');
    if (simulateButton) {
        simulateButton.addEventListener('click', simulateParameters);
    }
}

/**
 * Reset all parameters to their default values.
 */
function resetParameters() {
    // Reset sliders
    const sliders = document.querySelectorAll('.parameter-slider');
    sliders.forEach(slider => {
        const defaultValue = slider.getAttribute('data-default');
        if (defaultValue) {
            slider.value = defaultValue;
            
            // Update corresponding number input
            const numberInput = document.getElementById(slider.id + '-value');
            if (numberInput) {
                numberInput.value = defaultValue;
            }
        }
    });
    
    // Reset checkboxes
    const checkboxes = document.querySelectorAll('.parameter-checkbox');
    checkboxes.forEach(checkbox => {
        const defaultValue = checkbox.getAttribute('data-default');
        if (defaultValue) {
            checkbox.checked = (defaultValue === 'true' || defaultValue === 'True');
        }
    });
    
    // Hide simulation result
    const resultDiv = document.getElementById('simulation-result');
    if (resultDiv) {
        resultDiv.style.display = 'none';
    }
    
    console.log('Parameters reset to defaults');
}

/**
 * Collect current parameter values from the form.
 * 
 * @returns {Object} Dictionary of parameter names to values
 */
function collectParameterValues() {
    const params = {};
    
    // Collect slider values
    const sliders = document.querySelectorAll('.parameter-slider');
    sliders.forEach(slider => {
        const name = slider.getAttribute('name');
        const value = parseFloat(slider.value);
        params[name] = value;
    });
    
    // Collect checkbox values
    const checkboxes = document.querySelectorAll('.parameter-checkbox');
    checkboxes.forEach(checkbox => {
        const name = checkbox.getAttribute('name');
        params[name] = checkbox.checked;
    });
    
    return params;
}

/**
 * Simulate forecast with current parameter values.
 * Makes API call to recalculate probability with modified parameters.
 */
async function simulateParameters() {
    const simulateButton = document.getElementById('simulate-parameters');
    const resultDiv = document.getElementById('simulation-result');
    const resultValue = document.getElementById('simulated-probability');
    
    // Disable button during simulation
    if (simulateButton) {
        simulateButton.disabled = true;
        const originalText = simulateButton.textContent;
        simulateButton.innerHTML = 'Simulating... <span class="loading-spinner"></span>';
    }
    
    try {
        // Collect parameter values
        const params = collectParameterValues();
        console.log('Simulating with parameters:', params);
        
        // Get forecast name from URL
        const pathParts = window.location.pathname.split('/');
        const forecastName = pathParts[pathParts.length - 1];
        
        // Make API call
        const response = await fetch(`/api/forecast/${forecastName}/simulate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display result
        if (data.probability !== undefined) {
            resultValue.textContent = formatProbability(data.probability, 1) + '%';
            resultDiv.style.display = 'block';
            console.log('Simulation complete:', data.probability);
        } else if (response.status === 501) {
            // API not implemented yet - this is expected for task 13
            throw new Error('Simulation API not yet implemented (coming in task 14)');
        } else {
            throw new Error('No probability in response');
        }
        
    } catch (error) {
        console.error('Simulation error:', error);
        resultValue.textContent = 'Error: ' + error.message;
        resultDiv.style.display = 'block';
    } finally {
        // Re-enable button
        if (simulateButton) {
            simulateButton.disabled = false;
            simulateButton.textContent = 'Simulate';
        }
    }
}

/**
 * Format a probability value as a percentage string.
 * 
 * @param {number} probability - Probability value between 0 and 1
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted percentage string
 */
function formatProbability(probability, decimals = 1) {
    return (probability * 100).toFixed(decimals);
}

/**
 * Format a timestamp for display.
 * 
 * @param {string|Date} timestamp - Timestamp to format
 * @returns {string} Formatted timestamp string
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

/**
 * Calculate decayed probability using power-law decay formula.
 * Implements the temporal decay logic matching the Python backend.
 * 
 * This matches the simple_decay/theta_decay formula from lib/temporal_adjustment.py:
 * time_ratio = days_remaining / total_days
 * time_factor = (time_ratio)^decay_power
 * adjusted = base * time_factor
 * 
 * @param {number} baseProbability - Base probability before adjustment (0-1)
 * @param {number} daysRemaining - Days until deadline
 * @param {number} decayPower - Power factor for decay (higher = faster decay)
 * @param {number} totalDays - Total forecast window (default: 365)
 * @param {number} threshold - Threshold below which decay is applied (optional)
 * @returns {number} Adjusted probability after decay (0-1)
 */
function calculateDecayedProbability(baseProbability, daysRemaining, decayPower, totalDays = 365, threshold = null, lowerThreshold = null, upperThreshold = null, amplificationPower = null) {
    // Validate inputs
    if (baseProbability < 0 || baseProbability > 1) {
        console.error('baseProbability must be in [0, 1]');
        return baseProbability;
    }
    
    // If we're at or past the deadline, return very small probability
    if (daysRemaining <= 0) {
        return Math.max(0.0, baseProbability * 0.001);
    }
    
    // If we're at or beyond the total forecast window, no adjustment
    if (daysRemaining >= totalDays) {
        return baseProbability;
    }
    
    // Calculate time ratio (how much time has passed)
    const timeRatio = daysRemaining / totalDays;
    
    // Adaptive method: decay low probabilities, amplify high probabilities
    if (lowerThreshold !== null && upperThreshold !== null && amplificationPower !== null) {
        if (baseProbability < lowerThreshold) {
            // Below lower threshold: apply full decay
            const timeFactor = Math.pow(timeRatio, decayPower);
            return baseProbability * timeFactor;
        } else if (baseProbability > upperThreshold) {
            // Above upper threshold: apply amplification toward 1.0
            const timePressure = 1 - Math.pow(timeRatio, amplificationPower);
            const distanceFromThreshold = baseProbability - upperThreshold;
            const maxDistance = 1.0 - upperThreshold;
            const strength = distanceFromThreshold / maxDistance;
            const target = 1.0;
            const adjustment = (target - baseProbability) * strength * timePressure * 0.5;
            return Math.min(1.0, baseProbability + adjustment);
        } else {
            // In the uncertain zone (between thresholds): apply gentle decay
            const timeFactor = Math.pow(timeRatio, decayPower * 0.5);
            return baseProbability * timeFactor;
        }
    }
    
    // Legacy threshold-based decay
    if (threshold !== null && baseProbability >= threshold) {
        return baseProbability;
    }
    
    // Apply power-law decay formula
    const timeFactor = Math.pow(timeRatio, decayPower);
    return baseProbability * timeFactor;
}

/**
 * Render temporal decay chart showing probability projection over time.
 * Creates an interactive Chart.js visualization showing how probability
 * would evolve from now until the deadline.
 * 
 * @param {string} canvasId - ID of the canvas element
 * @param {Object} breakdown - Breakdown data from the model containing:
 *   - base_probability: Base probability before adjustment
 *   - adjusted_probability: Current adjusted probability
 *   - days_remaining: Days until deadline
 *   - temporal_metadata: Object with method, parameters, etc.
 */
function renderTemporalDecayChart(canvasId, breakdown) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        console.error(`Canvas element '${canvasId}' not found`);
        return;
    }
    
    const ctx = canvas.getContext('2d');
    const daysRemaining = breakdown.days_remaining;
    const baseProb = breakdown.base_probability;
    const currentAdjusted = breakdown.adjusted_probability;
    
    // Extract decay parameters from metadata
    const metadata = breakdown.temporal_metadata || {};
    const parameters = metadata.parameters || {};
    const method = metadata.method || 'adaptive';
    
    // Get parameters based on method
    const decayPower = parameters.decay_power || 1.5;
    const amplificationPower = parameters.amplification_power || 1.5;
    const totalDays = parameters.total_days || 365;
    const lowerThreshold = parameters.lower_threshold || null;
    const upperThreshold = parameters.upper_threshold || null;
    const threshold = parameters.threshold || lowerThreshold;
    
    // Generate projection data points
    // Show how probability would evolve from now (0 days from now) to deadline
    const projectionData = [];
    const numPoints = Math.min(50, daysRemaining + 1); // Max 50 points for performance
    const step = Math.max(1, Math.floor(daysRemaining / numPoints));
    
    for (let daysFromNow = 0; daysFromNow <= daysRemaining; daysFromNow += step) {
        const daysRemainingAtPoint = daysRemaining - daysFromNow;
        const adjustedProb = calculateDecayedProbability(
            baseProb,
            daysRemainingAtPoint,
            decayPower,
            totalDays,
            threshold,
            lowerThreshold,
            upperThreshold,
            amplificationPower
        );
        projectionData.push({
            x: daysFromNow,
            y: adjustedProb * 100  // Convert to percentage
        });
    }
    
    // Ensure we include the final point at deadline
    if (projectionData[projectionData.length - 1].x !== daysRemaining) {
        const finalProb = calculateDecayedProbability(baseProb, 0, decayPower, totalDays, threshold, lowerThreshold, upperThreshold, amplificationPower);
        projectionData.push({
            x: daysRemaining,
            y: finalProb * 100
        });
    }
    
    // Create Chart.js chart
    new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [
                {
                    label: 'Projected Adjusted Probability',
                    data: projectionData,
                    borderColor: '#45b7d1',
                    backgroundColor: 'rgba(69, 183, 209, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 5
                },
                {
                    label: 'Base Probability (No Decay)',
                    data: [
                        {x: 0, y: baseProb * 100},
                        {x: daysRemaining, y: baseProb * 100}
                    ],
                    borderColor: '#4ecdc4',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                    borderWidth: 2
                },
                {
                    label: 'Current Position',
                    data: [{x: 0, y: currentAdjusted * 100}],
                    pointRadius: 8,
                    pointBackgroundColor: '#ff6b6b',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    showLine: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                x: {
                    type: 'linear',
                    title: {
                        display: true,
                        text: 'Days from Now',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Probability (%)',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    min: 0,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    },
                    callbacks: {
                        title: function(context) {
                            const daysFromNow = context[0].parsed.x;
                            return `${daysFromNow} days from now`;
                        },
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y.toFixed(1);
                            return `${label}: ${value}%`;
                        }
                    }
                }
            }
        }
    });
    
    console.log('Temporal decay chart rendered successfully');
}

/**
 * Initialize temporal decay chart on page load.
 * Checks if breakdown data exists in the page and renders the chart.
 * Handles errors gracefully without breaking the page.
 */
function initializeTemporalDecayChart() {
    try {
        // Check if we're on a forecast page with temporal decay data
        const chartCanvas = document.getElementById('temporalDecayChart');
        if (!chartCanvas) {
            // No chart canvas on this page, skip initialization
            return;
        }
        
        // Check if breakdown data is available
        // The data should be embedded in the page by the template
        const breakdownElement = document.getElementById('breakdown-data');
        if (!breakdownElement) {
            console.log('No breakdown data found, skipping temporal chart');
            return;
        }
        
        // Parse breakdown data from data attribute or JSON
        let breakdown;
        try {
            const breakdownJson = breakdownElement.getAttribute('data-breakdown');
            if (breakdownJson) {
                breakdown = JSON.parse(breakdownJson);
            } else {
                console.log('No breakdown data attribute found');
                return;
            }
        } catch (parseError) {
            console.error('Error parsing breakdown data:', parseError);
            return;
        }
        
        // Validate required fields
        if (!breakdown.base_probability || 
            !breakdown.adjusted_probability || 
            breakdown.days_remaining === undefined) {
            console.error('Incomplete breakdown data:', breakdown);
            return;
        }
        
        // Render the chart
        renderTemporalDecayChart('temporalDecayChart', breakdown);
        
    } catch (error) {
        console.error('Error initializing temporal decay chart:', error);
        // Don't throw - fail gracefully
    }
}
