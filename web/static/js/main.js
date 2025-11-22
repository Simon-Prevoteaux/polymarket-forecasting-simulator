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
