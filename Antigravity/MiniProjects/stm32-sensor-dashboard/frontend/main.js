document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const statusDot = document.getElementById('connection-dot');
    const statusText = document.getElementById('connection-text');
    const currentValueEl = document.getElementById('current-value');
    const currentUnitEl = document.getElementById('current-unit');
    const sensorIdEl = document.getElementById('sensor-id');
    const lastUpdateEl = document.getElementById('last-update');
    const btnPause = document.getElementById('btn-pause');
    const btnClear = document.getElementById('btn-clear');
    
    // State
    let isPaused = false;
    const maxDataPoints = 300; // Keep last 30 seconds of data at 10Hz

    // Initialize Chart.js
    const ctx = document.getElementById('sensorChart').getContext('2d');
    
    // Create gradient for the line
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(6, 182, 212, 0.5)'); // Cyan transparent
    gradient.addColorStop(1, 'rgba(6, 182, 212, 0.0)');

    const chartConfig = {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperature',
                data: [],
                borderColor: '#06b6d4', // Cyan
                backgroundColor: gradient,
                borderWidth: 2,
                pointBackgroundColor: '#ffffff', // White
                pointBorderColor: '#06b6d4',
                pointBorderWidth: 2,
                pointRadius: 1, // smaller points since there are more of them
                pointHoverRadius: 4,
                fill: true,
                tension: 0.4 // Smooth curves
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 100, // Faster animation for 10Hz
                easing: 'linear'
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    titleColor: '#1e293b',
                    bodyColor: '#475569',
                    borderColor: 'rgba(0,0,0,0.05)',
                    borderWidth: 1,
                    padding: 10,
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y} °C`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#64748b',
                        maxTicksLimit: 10,
                        maxRotation: 0
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#64748b',
                        padding: 10
                    },
                    // Suggesting a range based on typical room temp, 
                    // Chart.js adapts automatically if values go outside
                    suggestedMin: 15,
                    suggestedMax: 35
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    };

    const sensorChart = new Chart(ctx, chartConfig);

    // Update UI Function
    function updateDashboard(data) {
        if (isPaused) return;

        // Update Stats
        currentValueEl.textContent = data.value.toFixed(1);
        if (data.unit === "Celsius") {
            currentUnitEl.textContent = "°C";
        } else {
            currentUnitEl.textContent = data.unit;
        }
        sensorIdEl.textContent = data.sensor_id;
        
        // Format timestamp
        const date = new Date(); // Use local time for received data
        lastUpdateEl.textContent = date.toLocaleTimeString([], { hour12: false });

        // Update Chart
        const timeStr = date.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' });
        const msStr = date.getMilliseconds().toString().padStart(3, '0');
        const timeLabel = `${timeStr}.${msStr}`;
        
        sensorChart.data.labels.push(timeLabel);
        sensorChart.data.datasets[0].data.push(data.value);

        // Keep array length bounded
        if (sensorChart.data.labels.length > maxDataPoints) {
            sensorChart.data.labels.shift();
            sensorChart.data.datasets[0].data.shift();
        }

        sensorChart.update('none'); // Update without full animation for smoother real-time feel
    }

    // Set Connection Status UI
    function setConnectionStatus(isConnected) {
        if (isConnected) {
            statusDot.className = 'dot connected';
            statusText.textContent = 'Connected (Live)';
            statusText.style.color = 'var(--accent-green)';
        } else {
            statusDot.className = 'dot disconnected';
            statusText.textContent = 'Reconnecting...';
            statusText.style.color = 'var(--accent-red)';
            currentValueEl.textContent = '--';
        }
    }

    // WebSocket Connection handling
    let ws;
    let reconnectInterval;

    function connectWebSocket() {
        // Since we are likely opening this via file:// protocol directly, window.location.hostname is empty.
        // We MUST force connection to localhost or 127.0.0.1 where the backend is running.
        let hostname = window.location.hostname;
        if (!hostname || hostname === '') {
            hostname = 'localhost';
        }
        
        const wsUrl = `ws://${hostname}:8000/ws`;
        console.log("Connecting to WebSocket at:", wsUrl);
        
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log("WebSocket connected");
            setConnectionStatus(true);
            if (reconnectInterval) {
                clearInterval(reconnectInterval);
                reconnectInterval = null;
            }
        };

        ws.onmessage = (event) => {
            console.log("WebSocket message received:", event.data);
            try {
                // If it's already an object, use it directly (some WebSocket wrappers might auto-parse)
                const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
                updateDashboard(data);
            } catch (e) {
                console.error("Error parsing websocket JSON:", e, "Raw data:", event.data);
            }
        };

        ws.onclose = () => {
            console.log("WebSocket disconnected");
            setConnectionStatus(false);
            
            // Try to reconnect every 3 seconds
            if (!reconnectInterval) {
                reconnectInterval = setInterval(() => {
                    console.log("Attempting to reconnect...");
                    connectWebSocket();
                }, 3000);
            }
        };

        ws.onerror = (error) => {
            console.error("WebSocket error:", error);
            ws.close();
        };
    }

    // Start connection
    connectWebSocket();

    // Event Listeners for Buttons
    btnPause.addEventListener('click', () => {
        isPaused = !isPaused;
        if (isPaused) {
            btnPause.textContent = 'Resume';
            btnPause.classList.add('active');
            statusText.textContent = 'Paused';
        } else {
            btnPause.textContent = 'Pause';
            btnPause.classList.remove('active');
            if (ws.readyState === WebSocket.OPEN) {
                statusText.textContent = 'Connected (Live)';
            }
        }
    });

    btnClear.addEventListener('click', () => {
        sensorChart.data.labels = [];
        sensorChart.data.datasets[0].data = [];
        sensorChart.update();
        currentValueEl.textContent = '--';
        lastUpdateEl.textContent = 'Never';
    });
});
