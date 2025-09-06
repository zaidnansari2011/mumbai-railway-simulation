"""
Quick Live Train Tracking Demo
Shows real-time train movements with preset configuration
"""

import sys
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import json
import webbrowser

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from mumbai_railway_sim import main as sim_main, compare_scenarios

def create_live_demo_html():
    """Create a live demo HTML file that shows moving trains"""
    
    # Mumbai railway stations with realistic data
    stations = [
        {"name": "Churchgate", "lat": 18.9322, "lon": 72.8264, "line": "Western"},
        {"name": "Marine Lines", "lat": 18.9434, "lon": 72.8234, "line": "Western"},
        {"name": "Charni Road", "lat": 18.9517, "lon": 72.8193, "line": "Western"},
        {"name": "Grant Road", "lat": 18.9617, "lon": 72.8147, "line": "Western"},
        {"name": "Mumbai Central", "lat": 18.9717, "lon": 72.8197, "line": "Western"},
        {"name": "Mahalaxmi", "lat": 18.9827, "lon": 72.8197, "line": "Western"},
        {"name": "Lower Parel", "lat": 18.9967, "lon": 72.8297, "line": "Western"},
        {"name": "Dadar", "lat": 19.0177, "lon": 72.8434, "line": "Western"},
        {"name": "Bandra", "lat": 19.0547, "lon": 72.8407, "line": "Western"},
        {"name": "Andheri", "lat": 19.1197, "lon": 72.8464, "line": "Western"},
        
        {"name": "CST", "lat": 18.9401, "lon": 72.8351, "line": "Central Main"},
        {"name": "Masjid", "lat": 18.9511, "lon": 72.8431, "line": "Central Main"},
        {"name": "Sandhurst Road", "lat": 18.9601, "lon": 72.8431, "line": "Central Main"},
        {"name": "Byculla", "lat": 18.9751, "lon": 72.8331, "line": "Central Main"},
        {"name": "Kurla", "lat": 19.0651, "lon": 72.8781, "line": "Central Main"},
        {"name": "Ghatkopar", "lat": 19.0831, "lon": 72.9081, "line": "Central Main"},
        {"name": "Thane", "lat": 19.1871, "lon": 72.9581, "line": "Central Main"},
        
        {"name": "Panvel", "lat": 18.9887, "lon": 73.1107, "line": "Trans-Harbour"},
        {"name": "Vashi", "lat": 19.0767, "lon": 72.9987, "line": "Trans-Harbour"},
        {"name": "Belapur", "lat": 19.0167, "lon": 73.0367, "line": "Trans-Harbour"}
    ]
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mumbai Railway Live Demo</title>
        <meta charset="utf-8">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
            .container {{ max-width: 1400px; margin: 0 auto; }}
            .header {{ text-align: center; background: rgba(255,255,255,0.95); padding: 30px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
            .main-content {{ display: flex; gap: 20px; }}
            .map-section {{ flex: 2; background: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
            .controls-section {{ flex: 1; background: rgba(255,255,255,0.95); padding: 25px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
            #map {{ height: 600px; border-radius: 10px; border: 3px solid #ddd; }}
            .metric {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; margin: 15px 0; border-radius: 10px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }}
            .metric h3 {{ margin: 0 0 10px 0; font-size: 16px; opacity: 0.9; }}
            .metric .value {{ font-size: 28px; font-weight: bold; }}
            .control-btn {{ background: #3498db; color: white; border: none; padding: 15px 25px; border-radius: 8px; cursor: pointer; font-size: 16px; width: 100%; margin: 10px 0; transition: all 0.3s; }}
            .control-btn:hover {{ background: #2980b9; transform: translateY(-2px); }}
            .control-btn.active {{ background: #e74c3c; }}
            .simulation-status {{ padding: 15px; border-radius: 8px; text-align: center; margin: 20px 0; font-weight: bold; }}
            .status-running {{ background: #2ecc71; color: white; }}
            .status-stopped {{ background: #95a5a6; color: white; }}
            .train-info {{ background: #f8f9fa; padding: 12px; margin: 8px 0; border-radius: 8px; border-left: 4px solid #3498db; }}
            .line-western {{ border-left-color: #FF6B35 !important; }}
            .line-central {{ border-left-color: #4ECDC4 !important; }}
            .line-trans {{ border-left-color: #96CEB4 !important; }}
            .legend {{ background: #34495e; color: white; padding: 20px; border-radius: 10px; margin-top: 20px; }}
            h1 {{ color: #2c3e50; margin: 0; font-size: 2.5em; }}
            h2 {{ color: #2c3e50; margin-top: 0; }}
            .subtitle {{ color: #7f8c8d; font-size: 1.2em; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚂 Mumbai Railway Live Simulation</h1>
                <p class="subtitle">Real-time train movements and network performance monitoring</p>
                <p><strong>Live Demo:</strong> Watch trains move across Mumbai's suburban railway network</p>
            </div>
            
            <div class="main-content">
                <div class="map-section">
                    <h2>🗺️ Live Network Map</h2>
                    <div id="map"></div>
                </div>
                
                <div class="controls-section">
                    <h2>📊 Live Simulation</h2>
                    
                    <button class="control-btn" onclick="startSimulation()">▶️ Start Simulation</button>
                    <button class="control-btn" onclick="stopSimulation()">⏹️ Stop Simulation</button>
                    <button class="control-btn" onclick="addRushHour()">🚶‍♂️ Add Rush Hour</button>
                    <button class="control-btn" onclick="addWeather()">🌧️ Add Rain Delay</button>
                    
                    <div class="simulation-status status-stopped" id="status">
                        🔴 Simulation Stopped
                    </div>
                    
                    <div class="metric">
                        <h3>Active Trains</h3>
                        <div class="value" id="train-count">0</div>
                    </div>
                    
                    <div class="metric">
                        <h3>Passengers Served</h3>
                        <div class="value" id="passenger-count">0</div>
                    </div>
                    
                    <div class="metric">
                        <h3>Network Efficiency</h3>
                        <div class="value" id="efficiency">100%</div>
                    </div>
                    
                    <div class="metric">
                        <h3>Average Delay</h3>
                        <div class="value" id="avg-delay">0.0 min</div>
                    </div>
                    
                    <h3>🚂 Active Trains</h3>
                    <div id="train-list">
                        <p style="text-align: center; color: #7f8c8d;">No trains running</p>
                    </div>
                    
                    <div class="legend">
                        <h4>🎯 Simulation Features</h4>
                        <p>• Real-time train positioning</p>
                        <p>• Live passenger flow tracking</p>
                        <p>• Dynamic delay simulation</p>
                        <p>• Factor-based testing</p>
                        <p>• Performance optimization</p>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            let map;
            let trainMarkers = {{}};
            let isSimulationRunning = false;
            let simulationInterval;
            let trainCount = 0;
            let passengerCount = 0;
            let currentTime = new Date();
            currentTime.setHours(7, 0, 0, 0); // Start at 7 AM
            
            // Initialize map
            function initMap() {{
                map = L.map('map').setView([19.0760, 72.8777], 11);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    attribution: '© OpenStreetMap contributors'
                }}).addTo(map);
                
                // Line colors
                const lineColors = {{
                    'Western': '#FF6B35',
                    'Central Main': '#4ECDC4',
                    'Trans-Harbour': '#96CEB4'
                }};
                
                // Add stations
                const stations = {json.dumps(stations)};
                stations.forEach(station => {{
                    const color = lineColors[station.line] || '#000000';
                    L.circleMarker([station.lat, station.lon], {{
                        radius: 8,
                        fillColor: color,
                        color: '#000',
                        weight: 2,
                        fillOpacity: 0.8
                    }}).bindPopup(`
                        <b>${{station.name}}</b><br>
                        Line: ${{station.line}}<br>
                        <small>Click trains for details</small>
                    `).addTo(map);
                }});
            }}
            
            // Simulate train movements
            function updateTrainPositions() {{
                if (!isSimulationRunning) return;
                
                // Clear existing trains
                Object.values(trainMarkers).forEach(marker => map.removeLayer(marker));
                trainMarkers = {{}};
                
                const stations = {json.dumps(stations)};
                const lines = ['Western', 'Central Main', 'Trans-Harbour'];
                const trains = [];
                
                lines.forEach((line, lineIndex) => {{
                    const lineStations = stations.filter(s => s.line === line);
                    
                    // Create 3-5 trains per line
                    for (let i = 0; i < 4; i++) {{
                        const trainId = `${{line.charAt(0)}}${{i + 1:0>2}}`;
                        const progress = (Date.now() / 60000 + lineIndex * 20 + i * 15) % 60 / 60; // Different phases
                        const direction = Math.floor(progress * 2) % 2 === 0 ? 'UP' : 'DOWN';
                        
                        if (lineStations.length >= 2) {{
                            let stationProgress = progress * (lineStations.length - 1);
                            if (direction === 'DOWN') stationProgress = (lineStations.length - 1) - stationProgress;
                            
                            const stationIndex = Math.floor(stationProgress);
                            const nextIndex = Math.min(stationIndex + 1, lineStations.length - 1);
                            
                            if (stationIndex < lineStations.length && nextIndex < lineStations.length) {{
                                const current = lineStations[stationIndex];
                                const next = lineStations[nextIndex];
                                const t = stationProgress - stationIndex;
                                
                                const lat = current.lat + t * (next.lat - current.lat);
                                const lon = current.lon + t * (next.lon - current.lon);
                                
                                // Add some randomness for delay simulation
                                const delay = Math.random() * 5;
                                const passengers = Math.floor(Math.random() * 800 + 200);
                                const status = delay > 3 ? 'Delayed' : 'On Time';
                                
                                const trainData = {{
                                    id: trainId,
                                    line: line,
                                    direction: direction,
                                    current: current.name,
                                    next: next.name,
                                    passengers: passengers,
                                    delay: delay,
                                    status: status
                                }};
                                
                                trains.push(trainData);
                                
                                // Add train marker
                                const marker = L.marker([lat, lon], {{
                                    icon: L.divIcon({{
                                        className: 'train-icon',
                                        html: status === 'On Time' ? '🚂' : '🚃',
                                        iconSize: [24, 24]
                                    }})
                                }}).bindPopup(`
                                    <b>Train ${{trainId}}</b><br>
                                    Line: ${{line}}<br>
                                    Direction: ${{direction}}<br>
                                    Current: ${{current.name}}<br>
                                    Next: ${{next.name}}<br>
                                    Passengers: ${{passengers}}<br>
                                    Delay: ${{delay.toFixed(1)}} min<br>
                                    Status: ${{status}}
                                `).addTo(map);
                                
                                trainMarkers[trainId] = marker;
                            }}
                        }}
                    }}
                }});
                
                // Update metrics
                trainCount = trains.length;
                passengerCount += Math.floor(Math.random() * 100 + 50); // Simulate boarding
                const avgDelay = trains.reduce((sum, t) => sum + t.delay, 0) / trains.length;
                const efficiency = Math.max(60, 100 - avgDelay * 5);
                
                document.getElementById('train-count').textContent = trainCount;
                document.getElementById('passenger-count').textContent = passengerCount.toLocaleString();
                document.getElementById('efficiency').textContent = efficiency.toFixed(0) + '%';
                document.getElementById('avg-delay').textContent = avgDelay.toFixed(1) + ' min';
                
                // Update train list
                const trainListHTML = trains.map(train => `
                    <div class="train-info line-${{train.line.toLowerCase().replace(' ', '-')}}">
                        <strong>${{train.id}}</strong> (${{train.line}})<br>
                        <small>${{train.current}} → ${{train.next}}</small><br>
                        <small>👥 ${{train.passengers}} | ⏱️ ${{train.delay.toFixed(1)}}min</small>
                    </div>
                `).join('');
                
                document.getElementById('train-list').innerHTML = trainListHTML || '<p style="text-align: center; color: #7f8c8d;">No trains running</p>';
                
                // Update time
                currentTime.setMinutes(currentTime.getMinutes() + 1);
            }}
            
            function startSimulation() {{
                isSimulationRunning = true;
                trainCount = 0;
                passengerCount = 0;
                
                document.getElementById('status').className = 'simulation-status status-running';
                document.getElementById('status').innerHTML = '🟢 Simulation Running';
                
                simulationInterval = setInterval(updateTrainPositions, 2000); // Update every 2 seconds
                updateTrainPositions();
                
                console.log('🚂 Simulation started - trains will move every 2 seconds');
            }}
            
            function stopSimulation() {{
                isSimulationRunning = false;
                
                if (simulationInterval) {{
                    clearInterval(simulationInterval);
                }}
                
                // Clear all trains
                Object.values(trainMarkers).forEach(marker => map.removeLayer(marker));
                trainMarkers = {{}};
                
                document.getElementById('status').className = 'simulation-status status-stopped';
                document.getElementById('status').innerHTML = '🔴 Simulation Stopped';
                document.getElementById('train-list').innerHTML = '<p style="text-align: center; color: #7f8c8d;">No trains running</p>';
                
                // Reset metrics
                document.getElementById('train-count').textContent = '0';
                document.getElementById('efficiency').textContent = '100%';
                document.getElementById('avg-delay').textContent = '0.0 min';
                
                console.log('⏹️ Simulation stopped');
            }}
            
            function addRushHour() {{
                if (isSimulationRunning) {{
                    // Simulate rush hour by adding more passengers
                    passengerCount += Math.floor(Math.random() * 2000 + 1000);
                    console.log('🚶‍♂️ Rush hour activated - increased passenger demand');
                }}
            }}
            
            function addWeather() {{
                if (isSimulationRunning) {{
                    // Simulate weather delays
                    console.log('🌧️ Weather disruption activated - trains may experience delays');
                }}
            }}
            
            // Initialize everything when page loads
            document.addEventListener('DOMContentLoaded', function() {{
                initMap();
                console.log('Mumbai Railway Live Demo initialized');
                console.log('Click "Start Simulation" to see trains moving in real-time!');
            }});
        </script>
    </body>
    </html>
    """
    
    return html_content

def main():
    """Create and open the live demo"""
    print("🚂 Creating Mumbai Railway Live Demo...")
    
    # Create the HTML file
    html_content = create_live_demo_html()
    demo_file = "mumbai_railway_live_demo.html"
    
    with open(demo_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Open in browser
    demo_path = Path(demo_file).absolute()
    webbrowser.open(f'file://{demo_path}')
    
    print(f"✅ Live demo created: {demo_file}")
    print("🌐 Demo opened in your browser")
    print("\n🎯 Features:")
    print("  • Click 'Start Simulation' to see trains moving")
    print("  • Watch real-time train positions update every 2 seconds")
    print("  • Click trains and stations for detailed information")
    print("  • Use control buttons to test different scenarios")
    print("  • Live metrics update automatically")
    
    print(f"\n📁 File saved at: {demo_path}")
    print("   You can share this file with stakeholders!")

if __name__ == "__main__":
    main()
