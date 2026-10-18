// frontend/static/js/main.js
// JavaScript for client-side interactions

document.addEventListener('DOMContentLoaded', function() {
    // Preset destination coordinates
    const presetDestinations = {
        kiit: { lat: 20.3050, lon: 85.8150 },
        railway: { lat: 20.2920, lon: 85.8280 },
        airport: { lat: 20.2700, lon: 85.8200 },
        master_canteen: { lat: 20.2920, lon: 85.8280 },
        patia: { lat: 20.3000, lon: 85.8200 }
    };
    
    // Handle preset destination selection (if on dashboard)
    const presetSelect = document.getElementById('preset_destination');
    if (presetSelect) {
        presetSelect.addEventListener('change', function() {
            const selected = this.value;
            const selectedOption = this.options[this.selectedIndex];
            
            if (selected && presetDestinations[selected]) {
                document.getElementById('dest_lat').value = presetDestinations[selected].lat;
                document.getElementById('dest_lon').value = presetDestinations[selected].lon;
                
                // Auto-fill destination name if empty
                const destNameInput = document.getElementById('dest_name');
                if (!destNameInput.value) {
                    destNameInput.value = selectedOption.text.split('—')[0].trim();
                }
            }
        });
    }
    
    // Get user's location using geolocation API
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                const carLatInput = document.getElementById('car_lat');
                const carLonInput = document.getElementById('car_lon');
                
                if (carLatInput && carLonInput) {
                    carLatInput.value = position.coords.latitude;
                    carLonInput.value = position.coords.longitude;
                }
            },
            function(error) {
                console.log('Geolocation denied or failed, using default City Center coordinates');
                // Default City Center (Bhubaneswar) values are already in the HTML
            }
        );
    }
    
    // Form validation for trip form
    const tripForm = document.getElementById('trip-form');
    if (tripForm) {
        tripForm.addEventListener('submit', function(e) {
            const batteryPct = parseFloat(document.getElementById('battery_pct').value);
            const distanceKm = parseFloat(document.getElementById('distance_km').value);
            
            // Client-side validation (server-side is primary)
            if (isNaN(batteryPct) || batteryPct < 1 || batteryPct > 100) {
                e.preventDefault();
                alert('Battery % must be between 1 and 100');
                return;
            }
            
            if (isNaN(distanceKm) || distanceKm <= 0) {
                e.preventDefault();
                alert('Distance must be greater than 0');
                return;
            }
            
            // Disable submit button and show loading state
            const submitBtn = document.getElementById('submit-btn');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Finding stations…';
            }
        });
    }
    
    // Form validation for login
    const loginForm = document.querySelector('form[action="/login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!email || !password) {
                e.preventDefault();
                alert('Please fill in all fields');
            }
        });
    }
    
    // Form validation for registration
    const registerForm = document.querySelector('form[action="/register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if (!username || !email || !password) {
                e.preventDefault();
                alert('Please fill in all fields');
                return;
            }
            
            if (password.length < 8) {
                e.preventDefault();
                alert('Password must be at least 8 characters');
                return;
            }
        });
    }
});
