"""
Simple Live Train Movement Visualization
Shows real-time train positions and metrics without complex dependencies
"""

import sys
import os
import time
import threading
import queue
from datetime import datetime, timedelta
from pathlib import Path
import json
import webbrowser

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.simulation.engine import MumbaiRailwaySimulation, SimulationConfig
from src.network.mumbai_network import MumbaiRailwayNetwork
from src.factors.simulation_factors import FactorManager

class SimpleLiveVisualization:
    """Simple live visualization without heavy dependencies"""
    
    def __init__(self):
        self.network = MumbaiRailwayNetwork()
        self.simulation = None
        self.is_running = False
        self.train_positions = {}
        self.metrics_history = []
        self.html_file = "live_train_tracking.html"
        
    def start_simulation(self, factors=None, duration_hours=2.0):
        """Start simulation with live updates"""
        print(f"🚂 Starting live simulation for {duration_hours} hours...")
        print(f"📍 Factors enabled: {factors if factors else 'None'}")
        
        # Configure simulation
        config = SimulationConfig(
            start_time=datetime.now().replace(hour=7, minute=0, second=0, microsecond=0),
            duration_hours=duration_hours,
            time_step_seconds=30,  # 30-second steps for smooth visualization
            enable_logging=True
        )
        
        self.simulation = MumbaiRailwaySimulation(config)
        
        # Enable factors
        if factors:
            factor_manager = FactorManager()
            for factor_name in factors:
                factor_manager.enable_factor(factor_name)
            self.simulation.factor_manager = factor_manager
        
        # Add real-time update callback
        self.simulation.add_update_callback(self.update_visualization)
        
        # Create initial HTML
        self.create_live_html()
        
        # Start simulation in thread
        self.is_running = True
        simulation_thread = threading.Thread(target=self._run_simulation, daemon=True)
        simulation_thread.start()
        
        # Open browser
        html_path = Path(self.html_file).absolute()
        webbrowser.open(f'file://{html_path}')
        
        print(f"✅ Live visualization opened in browser: {self.html_file}")
        print("📊 Simulation data will update every 30 seconds")
        print("⏹️  Press Ctrl+C to stop")
        
        try:
            # Keep main thread alive and update HTML periodically
            while self.is_running:
                time.sleep(10)  # Update HTML every 10 seconds
                self.update_html_file()
        except KeyboardInterrupt:
            print("\n⏹️ Stopping simulation...")
            self.is_running = False
    
    def _run_simulation(self):
        """Run simulation in background thread"""
        try:
            self.simulation.run()
        except Exception as e:
            print(f"❌ Simulation error: {e}")
        finally:
            self.is_running = False
    
    def update_visualization(self, sim_time, metrics):
        """Update callback from simulation"""
        if not self.is_running:
            return False
        
        # Update train positions
        self._update_train_positions(sim_time, metrics)
        
        # Update metrics
        metric_point = {
            'time': sim_time.strftime('%H:%M:%S'),
            'passengers': metrics.get('total_passengers_transported', 0),
            'active_trains': len(metrics.get('active_services', [])),
            'avg_delay': metrics.get('average_delay_minutes', 0),
            'on_time_perf': metrics.get('on_time_performance', 100)
        }
        
        self.metrics_history.append(metric_point)
        
        # Keep only recent history
        if len(self.metrics_history) > 50:
            self.metrics_history = self.metrics_history[-50:]
        
        print(f"⏰ {sim_time.strftime('%H:%M:%S')} - "
              f"Trains: {len(self.train_positions)}, "
              f"Passengers: {metric_point['passengers']:,}, "
              f"Avg Delay: {metric_point['avg_delay']:.1f}min")
        
        return True  # Continue simulation
    
    def _update_train_positions(self, sim_time, metrics):
        """Update train positions based on simulation data"""
        active_services = metrics.get('active_services', [])
        
        self.train_positions = {}
        
        # Get all stations for reference
        all_stations = self.network.get_all_stations()
        station_dict = {s['name']: s for s in all_stations}
        
        for i, service in enumerate(active_services):
            train_id = f"T{i+1:03d}"
            line = service.get('line', 'Western')
            direction = service.get('direction', 'UP')
            
            # Get stations for this line
            line_stations = [s for s in all_stations if s.get('line') == line]
            if len(line_stations) < 2:
                continue
            
            # Calculate position based on time
            minutes_elapsed = sim_time.minute + (sim_time.hour - 7) * 60
            cycle_time = 60  # 60 minutes for full cycle
            progress = (minutes_elapsed % cycle_time) / cycle_time
            
            if direction == 'DOWN':
                progress = 1.0 - progress
            
            # Find position between stations
            station_index = int(progress * (len(line_stations) - 1))
            next_index = min(station_index + 1, len(line_stations) - 1)
            
            if station_index < len(line_stations):
                current_station = line_stations[station_index]
                next_station = line_stations[next_index]
                
                # Interpolate position
                t = (progress * (len(line_stations) - 1)) - station_index
                lat = current_station['lat'] + t * (next_station['lat'] - current_station['lat'])
                lon = current_station['lon'] + t * (next_station['lon'] - current_station['lon'])
                
                self.train_positions[train_id] = {
                    'lat': lat,
                    'lon': lon,
                    'line': line,
                    'direction': direction,
                    'current_station': current_station['name'],
                    'next_station': next_station['name'],
                    'passengers': service.get('passenger_count', 0),
                    'delay': service.get('delay_minutes', 0),
                    'status': 'Running' if service.get('delay_minutes', 0) < 5 else 'Delayed'
                }
    
    def create_live_html(self):
        """Create the initial HTML file for live tracking"""
        stations = self.network.get_all_stations()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mumbai Railway Live Tracking</title>
            <meta charset="utf-8">
            <meta http-equiv="refresh" content="10">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .header {{ text-align: center; background: #2C3E50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .container {{ display: flex; gap: 20px; }}
                .map-container {{ flex: 2; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .metrics-container {{ flex: 1; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                #map {{ height: 600px; border-radius: 10px; }}
                .metric {{ background: #ECF0F1; padding: 15px; margin: 10px 0; border-radius: 8px; text-align: center; }}
                .metric h3 {{ margin: 0 0 10px 0; color: #2C3E50; }}
                .metric .value {{ font-size: 24px; font-weight: bold; color: #3498DB; }}
                .status {{ background: #2ECC71; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 20px 0; }}
                .train-list {{ max-height: 300px; overflow-y: auto; }}
                .train-item {{ background: #F8F9FA; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #3498DB; }}
                .legend {{ background: #34495E; color: white; padding: 15px; border-radius: 8px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚂 Mumbai Railway Live Tracking</h1>
                <p>Real-time train positions and network performance</p>
                <p id="last-update">Last Updated: {datetime.now().strftime('%H:%M:%S')}</p>
            </div>
            
            <div class="container">
                <div class="map-container">
                    <h2>🗺️ Live Network Map</h2>
                    <div id="map"></div>
                </div>
                
                <div class="metrics-container">
                    <h2>📊 Live Metrics</h2>
                    
                    <div class="metric">
                        <h3>Active Trains</h3>
                        <div class="value" id="active-trains">0</div>
                    </div>
                    
                    <div class="metric">
                        <h3>Passengers Transported</h3>
                        <div class="value" id="passengers">0</div>
                    </div>
                    
                    <div class="metric">
                        <h3>Average Delay</h3>
                        <div class="value" id="avg-delay">0.0 min</div>
                    </div>
                    
                    <div class="metric">
                        <h3>On-Time Performance</h3>
                        <div class="value" id="on-time">100%</div>
                    </div>
                    
                    <div class="status" id="status">
                        🟢 Simulation Running
                    </div>
                    
                    <h3>🚂 Active Trains</h3>
                    <div class="train-list" id="train-list">
                        <p>Loading train data...</p>
                    </div>
                    
                    <div class="legend">
                        <h4>Legend</h4>
                        <p>🔵 Running on time</p>
                        <p>🔴 Delayed service</p>
                        <p>🟡 Station with passengers</p>
                        <p>Page auto-refreshes every 10 seconds</p>
                    </div>
                </div>
            </div>
            
            <script>
                // Initialize map
                var map = L.map('map').setView([19.0760, 72.8777], 11);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
                
                // Line colors
                var lineColors = {{
                    'Western': '#FF6B35',
                    'Central Main': '#4ECDC4',
                    'Central Harbour': '#45B7D1', 
                    'Trans-Harbour': '#96CEB4'
                }};
                
                // Add stations
                var stations = {json.dumps(stations, indent=16)};
                stations.forEach(function(station) {{
                    var color = lineColors[station.line] || '#000000';
                    L.circleMarker([station.lat, station.lon], {{
                        radius: 6,
                        fillColor: color,
                        color: '#000',
                        weight: 2,
                        fillOpacity: 0.8
                    }}).bindPopup('<b>' + station.name + '</b><br>Line: ' + station.line).addTo(map);
                }});
                
                // Train positions will be updated by JavaScript injection
                var trainMarkers = {{}};
                
                // Function to update train positions (called by page refresh)
                function updateTrainPositions(positions) {{
                    // Clear existing train markers
                    Object.values(trainMarkers).forEach(marker => map.removeLayer(marker));
                    trainMarkers = {{}};
                    
                    // Add new train markers
                    Object.entries(positions).forEach(([trainId, data]) => {{
                        var color = data.status === 'Running' ? 'blue' : 'red';
                        var marker = L.marker([data.lat, data.lon], {{
                            icon: L.divIcon({{
                                className: 'train-marker',
                                html: '🚂',
                                iconSize: [20, 20]
                            }})
                        }}).bindPopup(`
                            <b>${{trainId}}</b><br>
                            Line: ${{data.line}}<br>
                            Direction: ${{data.direction}}<br>
                            Current: ${{data.current_station}}<br>
                            Next: ${{data.next_station}}<br>
                            Passengers: ${{data.passengers}}<br>
                            Delay: ${{data.delay}} min<br>
                            Status: ${{data.status}}
                        `).addTo(map);
                        
                        trainMarkers[trainId] = marker;
                    }});
                }}
                
                // Auto-refresh notification
                console.log('Live tracking initialized. Page will refresh every 10 seconds.');
            </script>
        </body>
        </html>
        """
        
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def update_html_file(self):
        """Update the HTML file with current data"""
        if not self.metrics_history:
            return
        
        # Get latest metrics
        latest = self.metrics_history[-1] if self.metrics_history else {}
        
        # Create updated HTML with current data injected
        stations = self.network.get_all_stations()
        
        # Generate train list HTML
        train_list_html = ""
        for train_id, data in self.train_positions.items():
            status_color = "🔵" if data['status'] == 'Running' else "🔴"
            train_list_html += f"""
            <div class="train-item">
                {status_color} <strong>{train_id}</strong> ({data['line']})<br>
                <small>Current: {data['current_station']}</small><br>
                <small>Passengers: {data['passengers']}, Delay: {data['delay']:.1f}min</small>
            </div>
            """
        
        if not train_list_html:
            train_list_html = "<p>No active trains</p>"
        
        # Update HTML content with current metrics
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mumbai Railway Live Tracking</title>
            <meta charset="utf-8">
            <meta http-equiv="refresh" content="10">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .header {{ text-align: center; background: #2C3E50; color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .container {{ display: flex; gap: 20px; }}
                .map-container {{ flex: 2; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .metrics-container {{ flex: 1; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                #map {{ height: 600px; border-radius: 10px; }}
                .metric {{ background: #ECF0F1; padding: 15px; margin: 10px 0; border-radius: 8px; text-align: center; }}
                .metric h3 {{ margin: 0 0 10px 0; color: #2C3E50; }}
                .metric .value {{ font-size: 24px; font-weight: bold; color: #3498DB; }}
                .status {{ background: #2ECC71; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 20px 0; }}
                .train-list {{ max-height: 300px; overflow-y: auto; }}
                .train-item {{ background: #F8F9FA; padding: 10px; margin: 5px 0; border-radius: 5px; border-left: 4px solid #3498DB; }}
                .legend {{ background: #34495E; color: white; padding: 15px; border-radius: 8px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚂 Mumbai Railway Live Tracking</h1>
                <p>Real-time train positions and network performance</p>
                <p id="last-update">Last Updated: {datetime.now().strftime('%H:%M:%S')}</p>
            </div>
            
            <div class="container">
                <div class="map-container">
                    <h2>🗺️ Live Network Map</h2>
                    <div id="map"></div>
                </div>
                
                <div class="metrics-container">
                    <h2>📊 Live Metrics</h2>
                    
                    <div class="metric">
                        <h3>Active Trains</h3>
                        <div class="value">{len(self.train_positions)}</div>
                    </div>
                    
                    <div class="metric">
                        <h3>Passengers Transported</h3>
                        <div class="value">{latest.get('passengers', 0):,}</div>
                    </div>
                    
                    <div class="metric">
                        <h3>Average Delay</h3>
                        <div class="value">{latest.get('avg_delay', 0):.1f} min</div>
                    </div>
                    
                    <div class="metric">
                        <h3>On-Time Performance</h3>
                        <div class="value">{latest.get('on_time_perf', 100):.1f}%</div>
                    </div>
                    
                    <div class="status">
                        {'🟢 Simulation Running' if self.is_running else '🔴 Simulation Stopped'}
                    </div>
                    
                    <h3>🚂 Active Trains</h3>
                    <div class="train-list">
                        {train_list_html}
                    </div>
                    
                    <div class="legend">
                        <h4>Legend</h4>
                        <p>🔵 Running on time</p>
                        <p>🔴 Delayed service</p>
                        <p>🟡 Station with passengers</p>
                        <p>Page auto-refreshes every 10 seconds</p>
                    </div>
                </div>
            </div>
            
            <script>
                // Initialize map
                var map = L.map('map').setView([19.0760, 72.8777], 11);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
                
                // Line colors
                var lineColors = {{
                    'Western': '#FF6B35',
                    'Central Main': '#4ECDC4',
                    'Central Harbour': '#45B7D1', 
                    'Trans-Harbour': '#96CEB4'
                }};
                
                // Add stations
                var stations = {json.dumps(stations, indent=16)};
                stations.forEach(function(station) {{
                    var color = lineColors[station.line] || '#000000';
                    L.circleMarker([station.lat, station.lon], {{
                        radius: 6,
                        fillColor: color,
                        color: '#000',
                        weight: 2,
                        fillOpacity: 0.8
                    }}).bindPopup('<b>' + station.name + '</b><br>Line: ' + station.line).addTo(map);
                }});
                
                // Add current train positions
                var trainPositions = {json.dumps(self.train_positions, indent=16)};
                Object.entries(trainPositions).forEach(([trainId, data]) => {{
                    var color = data.status === 'Running' ? 'blue' : 'red';
                    L.marker([data.lat, data.lon], {{
                        icon: L.divIcon({{
                            className: 'train-marker',
                            html: '🚂',
                            iconSize: [20, 20]
                        }})
                    }}).bindPopup(`
                        <b>${{trainId}}</b><br>
                        Line: ${{data.line}}<br>
                        Direction: ${{data.direction}}<br>
                        Current: ${{data.current_station}}<br>
                        Next: ${{data.next_station}}<br>
                        Passengers: ${{data.passengers}}<br>
                        Delay: ${{data.delay}} min<br>
                        Status: ${{data.status}}
                    `).addTo(map);
                }});
                
                console.log('Live tracking updated at {datetime.now().strftime('%H:%M:%S')}');
            </script>
        </body>
        </html>
        """
        
        with open(self.html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

def main():
    """Main function to run the live visualization"""
    print("🚂 Mumbai Railway Live Simulation")
    print("=" * 50)
    
    viz = SimpleLiveVisualization()
    
    # Ask user for configuration
    print("\nAvailable factors to test:")
    factors = ['rush_hour_demand', 'heavy_rain', 'track_maintenance', 'signal_failure']
    for i, factor in enumerate(factors, 1):
        print(f"  {i}. {factor}")
    
    print("\nSelect factors (comma-separated numbers, or press Enter for none):")
    factor_input = input("> ").strip()
    
    selected_factors = []
    if factor_input:
        try:
            indices = [int(x.strip()) - 1 for x in factor_input.split(',')]
            selected_factors = [factors[i] for i in indices if 0 <= i < len(factors)]
        except:
            print("Invalid input, proceeding without factors")
    
    duration = input("\\nSimulation duration in hours (default 1.0): ").strip()
    try:
        duration = float(duration) if duration else 1.0
    except:
        duration = 1.0
    
    print(f"\\n🚀 Starting live simulation...")
    print(f"📍 Factors: {selected_factors if selected_factors else 'None'}")
    print(f"⏱️  Duration: {duration} hours")
    print("\\n📊 Watch the live tracking in your browser!")
    
    viz.start_simulation(selected_factors, duration)

if __name__ == "__main__":
    main()
