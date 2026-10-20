// frontend/static/js/dashboard.js
// Dashboard-specific interactions for VoltRoute v2.0

document.addEventListener('DOMContentLoaded', function() {
    // Preset destination coordinates
    const presetDestinations = {
        kiit: { lat: 20.3050, lon: 85.8150 },
        railway: { lat: 20.2920, lon: 85.8280 },
        airport: { lat: 20.2700, lon: 85.8200 },
        master_canteen: { lat: 20.2920, lon: 85.8280 },
        patia: { lat: 20.3000, lon: 85.8200 }
    };

    // Chip selection
    const chips = document.querySelectorAll('.chip');
    chips.forEach(chip => {
        chip.addEventListener('click', function() {
            // Remove selected class from all chips
            chips.forEach(c => c.classList.remove('selected'));
            // Add selected class to clicked chip
            this.classList.add('selected');

            // Get preset data
            const preset = this.dataset.preset;
            const lat = this.dataset.lat;
            const lon = this.dataset.lon;

            if (preset && lat && lon) {
                // Fill destination name with chip text
                const destNameInput = document.getElementById('dest_name');
                destNameInput.value = this.textContent;

                // Fill hidden coordinates
                document.getElementById('dest_lat').value = lat;
                document.getElementById('dest_lon').value = lon;

                // Auto-calculate distance (straight line approximation)
                calculateDistance();
            }
        });
    });

    // GPS button
    const useGpsBtn = document.getElementById('use-gps');
    if (useGpsBtn) {
        useGpsBtn.addEventListener('click', function() {
            if (navigator.geolocation) {
                useGpsBtn.disabled = true;
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        document.getElementById('car_lat').value = position.coords.latitude;
                        document.getElementById('car_lon').value = position.coords.longitude;

                        // Optionally fill start name with coordinates or reverse geocode
                        const startNameInput = document.getElementById('start_name');
                        if (!startNameInput.value) {
                            startNameInput.value = `${position.coords.latitude.toFixed(4)}, ${position.coords.longitude.toFixed(4)}`;
                        }

                        calculateDistance();
                        useGpsBtn.disabled = false;
                    },
                    function(error) {
                        console.log('Geolocation denied or failed, using default City Center coordinates');
                        useGpsBtn.disabled = false;
                    }
                );
            } else {
                alert('Geolocation is not supported by your browser');
            }
        });
    }

    // Swap waypoints
    const swapBtn = document.getElementById('swap-waypoints');
    if (swapBtn) {
        swapBtn.addEventListener('click', function() {
            const startName = document.getElementById('start_name');
            const destName = document.getElementById('dest_name');
            const destLat = document.getElementById('dest_lat');
            const destLon = document.getElementById('dest_lon');

            // Swap names
            const tempName = startName.value;
            startName.value = destName.value;
            destName.value = tempName;

            // If destination has coordinates, move them to start
            if (destLat.value && destLon.value) {
                // For simplicity, we'll just clear destination coordinates
                // In a full implementation, you'd store start coordinates too
                destLat.value = '';
                destLon.value = '';
            }

            // Clear selected chip
            chips.forEach(c => c.classList.remove('selected'));

            calculateDistance();
        });
    }

    // Clear destination
    const clearDestBtn = document.getElementById('clear-dest');
    if (clearDestBtn) {
        clearDestBtn.addEventListener('click', function() {
            document.getElementById('dest_name').value = '';
            document.getElementById('dest_lat').value = '';
            document.getElementById('dest_lon').value = '';
            chips.forEach(c => c.classList.remove('selected'));
        });
    }

    // Battery slider
    const batterySlider = document.getElementById('battery_pct');
    const batteryValue = document.getElementById('battery-value');
    const batteryGauge = document.getElementById('battery-gauge');
    const batteryBar = document.getElementById('battery-bar');
    const batteryBadge = document.getElementById('battery-badge');
    const batteryIcon = document.getElementById('battery-icon');

    if (batterySlider) {
        batterySlider.addEventListener('input', function() {
            const value = this.value;
            batteryValue.textContent = value + '%';
            batteryBar.style.width = value + '%';

            // Update gauge color and badge based on battery level
            if (value > 40) {
                batteryGauge.dataset.level = 'ok';
                batteryBadge.className = 'badge badge-ok';
                batteryBadge.textContent = 'Good';
                batteryIcon.textContent = 'battery_charging_full';
            } else if (value >= 20) {
                batteryGauge.dataset.level = 'mid';
                batteryBadge.className = 'badge badge-warn';
                batteryBadge.textContent = 'Low';
                batteryIcon.textContent = 'battery_3_bar';
            } else {
                batteryGauge.dataset.level = 'low';
                batteryBadge.className = 'badge badge-bad';
                batteryBadge.textContent = 'Critical';
                batteryIcon.textContent = 'battery_alert';
            }

            updateLivePreview();
        });
    }

    // Speed slider
    const speedSlider = document.getElementById('speed_kmh');
    const speedValue = document.getElementById('speed-value');

    if (speedSlider) {
        speedSlider.addEventListener('input', function() {
            speedValue.textContent = this.value + ' km/h';
            updateLivePreview();
        });
    }

    // AC switch
    const acSwitch = document.getElementById('ac_on');
    if (acSwitch) {
        acSwitch.addEventListener('change', updateLivePreview);
    }

    // Temperature input
    const tempInput = document.getElementById('temp_celsius');
    if (tempInput) {
        tempInput.addEventListener('input', updateLivePreview);
    }

    // Distance input
    const distanceInput = document.getElementById('distance_km');
    if (distanceInput) {
        distanceInput.addEventListener('input', updateLivePreview);
    }

    // Live preview update function
    function updateLivePreview() {
        const battery = parseInt(batterySlider ? batterySlider.value : 50);
        const distance = parseFloat(distanceInput ? distanceInput.value : 0);
        const previewText = document.getElementById('preview-text');
        const previewIcon = document.getElementById('preview-icon');

        if (!distance || distance <= 0) {
            previewText.textContent = 'Enter distance to see preview';
            previewIcon.textContent = 'help';
            return;
        }

        // Simple rule: battery % divided by km below 0.45 means charge
        // This is a hint only; the ML model decides the real verdict
        const ratio = battery / distance;

        if (ratio < 0.45) {
            previewText.textContent = 'Charging recommended';
            previewIcon.textContent = 'warning';
            previewIcon.style.color = 'var(--tertiary)';
        } else {
            previewText.textContent = 'Battery looks sufficient';
            previewIcon.textContent = 'check_circle';
            previewIcon.style.color = 'var(--primary)';
        }
    }

    // Calculate distance (straight line approximation)
    function calculateDistance() {
        const carLat = parseFloat(document.getElementById('car_lat').value);
        const carLon = parseFloat(document.getElementById('car_lon').value);
        const destLat = parseFloat(document.getElementById('dest_lat').value);
        const destLon = parseFloat(document.getElementById('dest_lon').value);

        if (carLat && carLon && destLat && destLon) {
            // Haversine formula for distance calculation
            const R = 6371; // Earth's radius in km
            const dLat = (destLat - carLat) * Math.PI / 180;
            const dLon = (destLon - carLon) * Math.PI / 180;
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                      Math.cos(carLat * Math.PI / 180) * Math.cos(destLat * Math.PI / 180) *
                      Math.sin(dLon/2) * Math.sin(dLon/2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            const distance = R * c;

            const distanceInput = document.getElementById('distance_km');
            if (distanceInput) {
                distanceInput.value = distance.toFixed(1);
            }

            updateLivePreview();
        }
    }

    // Form submission
    const tripForm = document.getElementById('trip-form');
    if (tripForm) {
        tripForm.addEventListener('submit', function(e) {
            const batteryPct = parseFloat(document.getElementById('battery_pct').value);
            const distanceKm = parseFloat(document.getElementById('distance_km').value);

            // Client-side validation
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
                submitBtn.innerHTML = '<span class="material-symbols-outlined">hourglass_empty</span> Finding stations…';
            }
        });
    }

    // Get user's location on page load
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
            }
        );
    }

    // Initialize live preview on load
    updateLivePreview();
});
