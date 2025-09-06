"""
Interactive Network Map Visualization for Mumbai Railway Simulation
Creates an interactive map showing the railway network, stations, and real-time train positions.
"""

import folium
import sys
import os
from typing import Dict, List, Optional
import json
from datetime import datetime
import random

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.network.mumbai_network import MumbaiRailwayNetwork, LineType
from src.simulation.engine import MumbaiRailwaySimulation, SimulationConfig
from src.simulation.trains import TrainStatus


class NetworkMapVisualizer:
    """Creates interactive maps of the Mumbai railway network"""
    
    def __init__(self):
        self.network = MumbaiRailwayNetwork()
        self.line_colors = {
            LineType.WESTERN: '#FF6B6B',           # Red
            LineType.CENTRAL_MAIN: '#4ECDC4',     # Teal  
            LineType.CENTRAL_HARBOUR: '#45B7D1',   # Blue
            LineType.TRANS_HARBOUR: '#96CEB4'      # Green
        }
        
    def create_network_map(self, show_trains=False, simulation=None) -> folium.Map:
        """Create an interactive map of the Mumbai railway network"""
        
        # Center map on Mumbai
        mumbai_center = [19.0760, 72.8777]
        m = folium.Map(
            location=mumbai_center,
            zoom_start=11,
            tiles='OpenStreetMap'
        )
        
        # Add title
        title_html = '''
        <h3 align="center" style="font-size:20px"><b>Mumbai Suburban Railway Network</b></h3>
        '''
        m.get_root().html.add_child(folium.Element(title_html))
        
        # Add railway lines
        self._add_railway_lines(m)
        
        # Add stations
        self._add_stations(m)
        
        # Add trains if simulation is provided
        if show_trains and simulation:
            self._add_trains(m, simulation)
        
        # Add legend
        self._add_legend(m)
        
        return m
    
    def _add_railway_lines(self, m: folium.Map):
        """Add railway lines to the map"""
        
        # Group tracks by line for cleaner visualization
        line_routes = {line: [] for line in LineType}
        
        for track in self.network.tracks.values():
            from_station = self.network.stations.get(track.from_station)
            to_station = self.network.stations.get(track.to_station)
            
            if from_station and to_station:
                line_routes[track.line].append([
                    list(from_station.coordinates),
                    list(to_station.coordinates)
                ])
        
        # Draw lines for each railway line
        for line_type, routes in line_routes.items():
            if routes:
                # Create a feature group for this line
                line_group = folium.FeatureGroup(name=f"{line_type.value.title()} Line")
                
                for route in routes:
                    folium.PolyLine(
                        locations=route,
                        color=self.line_colors[line_type],
                        weight=4,
                        opacity=0.8,
                        popup=f"{line_type.value.title()} Line"
                    ).add_to(line_group)
                
                line_group.add_to(m)
    
    def _add_stations(self, m: folium.Map):
        """Add station markers to the map"""
        
        for station in self.network.stations.values():
            # Choose icon based on station type
            if station.interchange:
                icon_color = 'red'
                icon = 'transfer'
                icon_prefix = 'fa'
            elif station.station_type.value == 'terminal':
                icon_color = 'blue'
                icon = 'stop'
                icon_prefix = 'fa'
            else:
                icon_color = 'green'
                icon = 'circle'
                icon_prefix = 'fa'
            
            # Create popup with station information
            popup_html = f"""
            <div style="font-family: Arial; width: 200px;">
                <h4>{station.name}</h4>
                <b>Station ID:</b> {station.id}<br>
                <b>Line:</b> {station.line.value.title()}<br>
                <b>Platforms:</b> {station.platforms}<br>
                <b>Type:</b> {station.station_type.value.title()}<br>
                {f'<b>Interchange:</b> {", ".join([l.value for l in station.interchange_lines])}<br>' if station.interchange else ''}
            </div>
            """
            
            folium.Marker(
                location=station.coordinates,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=station.name,
                icon=folium.Icon(
                    color=icon_color,
                    icon=icon,
                    prefix=icon_prefix
                )
            ).add_to(m)
    
    def _add_trains(self, m: folium.Map, simulation: MumbaiRailwaySimulation):
        """Add train markers showing current positions"""
        
        train_group = folium.FeatureGroup(name="Active Trains")
        
        for service in simulation.active_services:
            if service.is_active and service.train.current_station:
                station = simulation.network.stations.get(service.train.current_station)
                if station:
                    # Choose color based on train status
                    if service.train.status == TrainStatus.DELAYED:
                        color = 'red'
                    elif service.train.status == TrainStatus.BOARDING:
                        color = 'orange'
                    else:
                        color = 'blue'
                    
                    # Create popup with train information
                    popup_html = f"""
                    <div style="font-family: Arial; width: 200px;">
                        <h4>Train {service.train.id}</h4>
                        <b>Line:</b> {service.train.line.title()}<br>
                        <b>Direction:</b> {service.train.direction.value.title()}<br>
                        <b>Status:</b> {service.train.status.value.title()}<br>
                        <b>Passengers:</b> {service.train.passenger_count}/{service.train.total_capacity}<br>
                        <b>Occupancy:</b> {service.train.occupancy_ratio:.1%}<br>
                        <b>Delay:</b> {service.train.delay_minutes:.1f} minutes<br>
                        <b>Current Station:</b> {station.name}
                    </div>
                    """
                    
                    folium.CircleMarker(
                        location=station.coordinates,
                        radius=8,
                        popup=folium.Popup(popup_html, max_width=250),
                        tooltip=f"Train {service.train.id}",
                        color='black',
                        fillColor=color,
                        fillOpacity=0.8
                    ).add_to(train_group)
        
        train_group.add_to(m)
    
    def _add_legend(self, m: folium.Map):
        """Add legend to the map"""
        
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 160px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>Legend</h4>
        <p><i class="fa fa-circle" style="color:red"></i> Interchange Stations</p>
        <p><i class="fa fa-circle" style="color:blue"></i> Terminal Stations</p>
        <p><i class="fa fa-circle" style="color:green"></i> Regular Stations</p>
        <p><span style="color:red; font-weight:bold;">——</span> Western Line</p>
        <p><span style="color:teal; font-weight:bold;">——</span> Central Main</p>
        <p><span style="color:blue; font-weight:bold;">——</span> Central Harbour</p>
        <p><span style="color:green; font-weight:bold;">——</span> Trans-Harbour</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
    
    def create_live_simulation_map(self, simulation: MumbaiRailwaySimulation) -> folium.Map:
        """Create a map that shows live simulation data"""
        
        m = self.create_network_map(show_trains=True, simulation=simulation)
        
        # Add passenger waiting indicators
        self._add_passenger_indicators(m, simulation)
        
        return m
    
    def _add_passenger_indicators(self, m: folium.Map, simulation: MumbaiRailwaySimulation):
        """Add indicators showing passenger waiting at stations"""
        
        max_waiting = max(simulation.passengers_waiting.values()) if simulation.passengers_waiting.values() else 1
        
        for station_id, waiting_count in simulation.passengers_waiting.items():
            station = simulation.network.stations.get(station_id)
            if station and waiting_count > 0:
                # Size circle based on waiting passengers
                radius = max(5, min(20, (waiting_count / max_waiting) * 20))
                
                folium.CircleMarker(
                    location=station.coordinates,
                    radius=radius,
                    popup=f"{waiting_count} passengers waiting at {station.name}",
                    tooltip=f"{waiting_count} waiting",
                    color='purple',
                    fillColor='purple',
                    fillOpacity=0.4
                ).add_to(m)
    
    def save_map(self, map_obj: folium.Map, filename: str):
        """Save map to HTML file"""
        map_obj.save(filename)
        print(f"Map saved to {filename}")


def create_network_overview():
    """Create a static network overview map"""
    visualizer = NetworkMapVisualizer()
    m = visualizer.create_network_map()
    visualizer.save_map(m, "mumbai_railway_network.html")
    return m


def create_simulation_demo():
    """Create a demo simulation with live visualization"""
    from datetime import datetime
    
    # Create simulation
    config = SimulationConfig(
        start_time=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),
        duration_hours=1,
        time_step_seconds=60,
        enable_logging=False
    )
    
    sim = MumbaiRailwaySimulation(config)
    sim.create_train_services(LineType.WESTERN, 5, 10)
    sim.create_train_services(LineType.CENTRAL_MAIN, 4, 12)
    
    # Add some factors for demonstration
    from src.factors.simulation_factors import RushHourDemand, WeatherConditions
    
    rush_hour = RushHourDemand(peak_multiplier=2.0)
    sim.factor_manager.add_factor(rush_hour)
    sim.factor_manager.enable_factor(rush_hour.name)
    
    # Run simulation for a few steps to generate some data
    for i in range(30):  # 30 minutes of simulation
        sim.run_simulation_step(sim.current_time)
        sim.current_time = sim.current_time + sim.config.time_step_seconds / 60  # Add 1 minute
    
    # Create visualization
    visualizer = NetworkMapVisualizer()
    m = visualizer.create_live_simulation_map(sim)
    visualizer.save_map(m, "simulation_demo.html")
    
    return m, sim


if __name__ == "__main__":
    print("Creating Mumbai Railway Network Visualizations...")
    
    # Create static network map
    print("1. Creating network overview map...")
    create_network_overview()
    
    # Create simulation demo
    print("2. Creating simulation demo map...")
    create_simulation_demo()
    
    print("\nVisualization files created:")
    print("- mumbai_railway_network.html (Static network overview)")
    print("- simulation_demo.html (Live simulation demo)")
    print("\nOpen these files in your web browser to view the interactive maps!")
