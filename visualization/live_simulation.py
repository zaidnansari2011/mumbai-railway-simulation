"""
Real-Time Mumbai Railway Simulation Visualization
Shows live train movements, passenger flows, and network status
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import time
import threading
import queue
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.simulation.engine import MumbaiRailwaySimulation
from src.network.mumbai_network import MumbaiRailwayNetwork
from src.factors.simulation_factors import FactorManager

class RealTimeVisualization:
    """Real-time visualization controller for the simulation"""
    
    def __init__(self):
        self.simulation = None
        self.network = MumbaiRailwayNetwork()
        self.is_running = False
        self.simulation_thread = None
        self.data_queue = queue.Queue()
        self.train_positions = {}
        self.metrics_history = []
        self.passenger_flows = {}
        
    def start_simulation(self, factors=None, duration_hours=2.0):
        """Start the simulation with real-time data collection"""
        if self.is_running:
            return False
            
        # Initialize simulation
        config = {
            'duration_hours': duration_hours,
            'time_step_minutes': 1,
            'start_time': '07:00',
            'collect_detailed_metrics': True
        }
        
        self.simulation = MumbaiRailwaySimulation(config)
        
        # Enable factors
        if factors:
            factor_manager = FactorManager()
            for factor_name in factors:
                factor_manager.enable_factor(factor_name)
            self.simulation.factor_manager = factor_manager
        
        # Start simulation in separate thread
        self.is_running = True
        self.simulation_thread = threading.Thread(
            target=self._run_simulation_with_callbacks,
            daemon=True
        )
        self.simulation_thread.start()
        return True
    
    def stop_simulation(self):
        """Stop the running simulation"""
        self.is_running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=2)
    
    def _run_simulation_with_callbacks(self):
        """Run simulation with real-time data callbacks"""
        try:
            # Add callback for real-time updates
            def update_callback(sim_time, metrics):
                if not self.is_running:
                    return False  # Stop simulation
                
                # Update train positions
                self._update_train_positions(sim_time, metrics)
                
                # Update metrics
                self._update_metrics(sim_time, metrics)
                
                # Update passenger flows
                self._update_passenger_flows(sim_time, metrics)
                
                # Put data in queue for UI updates
                self.data_queue.put({
                    'timestamp': sim_time,
                    'metrics': metrics,
                    'train_positions': self.train_positions.copy(),
                    'passenger_flows': self.passenger_flows.copy()
                })
                
                return True  # Continue simulation
            
            # Run simulation with callback
            self.simulation.add_update_callback(update_callback)
            self.simulation.run()
            
        except Exception as e:
            st.error(f"Simulation error: {e}")
        finally:
            self.is_running = False
    
    def _update_train_positions(self, sim_time, metrics):
        """Update train positions on the network"""
        # Get active services from metrics
        active_services = metrics.get('active_services', [])
        
        self.train_positions = {}
        
        for i, service in enumerate(active_services):
            # Calculate position based on time and route
            line_name = service.get('line', 'Western')
            direction = service.get('direction', 'UP')
            
            # Get stations for this line
            stations = self.network.get_line_stations(line_name)
            if len(stations) < 2:
                continue
            
            # Simulate position along route
            progress = (sim_time.minute % 30) / 30.0  # Cycle every 30 minutes
            if direction == 'DOWN':
                progress = 1.0 - progress
            
            # Interpolate position between stations
            station_index = int(progress * (len(stations) - 1))
            next_station_index = min(station_index + 1, len(stations) - 1)
            
            if station_index < len(stations) and next_station_index < len(stations):
                current_station = stations[station_index]
                next_station = stations[next_station_index]
                
                # Linear interpolation between stations
                t = (progress * (len(stations) - 1)) - station_index
                lat = current_station['lat'] + t * (next_station['lat'] - current_station['lat'])
                lon = current_station['lon'] + t * (next_station['lon'] - current_station['lon'])
                
                train_id = f"T{i+1:03d}"
                self.train_positions[train_id] = {
                    'lat': lat,
                    'lon': lon,
                    'line': line_name,
                    'direction': direction,
                    'current_station': current_station['name'],
                    'next_station': next_station['name'],
                    'passengers': service.get('passenger_count', 0),
                    'delay': service.get('delay_minutes', 0),
                    'status': 'Running' if service.get('delay_minutes', 0) < 5 else 'Delayed'
                }
    
    def _update_metrics(self, sim_time, metrics):
        """Update performance metrics history"""
        metric_point = {
            'time': sim_time,
            'passengers_transported': metrics.get('total_passengers_transported', 0),
            'active_services': len(metrics.get('active_services', [])),
            'average_delay': metrics.get('average_delay_minutes', 0),
            'on_time_performance': metrics.get('on_time_performance', 100),
            'network_efficiency': metrics.get('network_efficiency', 100),
            'total_waiting': metrics.get('total_waiting_passengers', 0)
        }
        
        self.metrics_history.append(metric_point)
        
        # Keep only recent history (last 60 points)
        if len(self.metrics_history) > 60:
            self.metrics_history = self.metrics_history[-60:]
    
    def _update_passenger_flows(self, sim_time, metrics):
        """Update passenger flow data at stations"""
        station_data = metrics.get('station_metrics', {})
        
        for station_name, data in station_data.items():
            self.passenger_flows[station_name] = {
                'waiting_passengers': data.get('waiting_passengers', 0),
                'passengers_boarded': data.get('passengers_boarded_last_interval', 0),
                'passengers_alighted': data.get('passengers_alighted_last_interval', 0),
                'congestion_level': self._calculate_congestion_level(data.get('waiting_passengers', 0))
            }
    
    def _calculate_congestion_level(self, waiting_passengers):
        """Calculate congestion level based on waiting passengers"""
        if waiting_passengers < 50:
            return 'Low'
        elif waiting_passengers < 150:
            return 'Medium'
        elif waiting_passengers < 300:
            return 'High'
        else:
            return 'Critical'
    
    def get_latest_data(self):
        """Get latest simulation data from queue"""
        latest_data = None
        
        # Get all available data (keep only the latest)
        while not self.data_queue.empty():
            try:
                latest_data = self.data_queue.get_nowait()
            except queue.Empty:
                break
        
        return latest_data

def create_live_network_map(train_positions, passenger_flows, network):
    """Create live network map with moving trains"""
    
    # Create base map centered on Mumbai
    m = folium.Map(
        location=[19.0760, 72.8777],
        zoom_start=11,
        tiles='OpenStreetMap'
    )
    
    # Define line colors
    line_colors = {
        'Western': '#FF6B35',
        'Central Main': '#4ECDC4',
        'Central Harbour': '#45B7D1', 
        'Trans-Harbour': '#96CEB4'
    }
    
    # Add station markers with passenger flow info
    stations = network.get_all_stations()
    for station in stations:
        station_name = station['name']
        flow_data = passenger_flows.get(station_name, {})
        
        # Determine marker color based on congestion
        congestion = flow_data.get('congestion_level', 'Low')
        if congestion == 'Critical':
            marker_color = 'red'
        elif congestion == 'High':
            marker_color = 'orange'
        elif congestion == 'Medium':
            marker_color = 'yellow'
        else:
            marker_color = 'green'
        
        # Create popup with passenger information
        waiting = flow_data.get('waiting_passengers', 0)
        boarded = flow_data.get('passengers_boarded', 0)
        alighted = flow_data.get('passengers_alighted', 0)
        
        popup_text = f"""
        <b>{station_name}</b><br>
        Line: {station.get('line', 'Unknown')}<br>
        <hr>
        Waiting: {waiting} passengers<br>
        Boarded: {boarded}<br>
        Alighted: {alighted}<br>
        Congestion: {congestion}
        """
        
        folium.CircleMarker(
            location=[station['lat'], station['lon']],
            radius=8 + (waiting / 50),  # Size based on waiting passengers
            popup=popup_text,
            color='black',
            fillColor=marker_color,
            fillOpacity=0.8,
            weight=2
        ).add_to(m)
    
    # Add moving trains
    for train_id, train_data in train_positions.items():
        # Train marker
        train_color = line_colors.get(train_data['line'], '#000000')
        
        # Create train popup
        popup_text = f"""
        <b>Train {train_id}</b><br>
        Line: {train_data['line']}<br>
        Direction: {train_data['direction']}<br>
        <hr>
        Current: {train_data['current_station']}<br>
        Next: {train_data['next_station']}<br>
        Passengers: {train_data['passengers']}<br>
        Delay: {train_data['delay']:.1f} min<br>
        Status: {train_data['status']}
        """
        
        # Add train marker
        folium.Marker(
            location=[train_data['lat'], train_data['lon']],
            popup=popup_text,
            icon=folium.Icon(
                color='blue' if train_data['status'] == 'Running' else 'red',
                icon='train',
                prefix='fa'
            )
        ).add_to(m)
        
        # Add train trail (last few positions)
        # This would be enhanced with actual position history
    
    return m

def create_live_metrics_charts(metrics_history):
    """Create live updating metrics charts"""
    
    if not metrics_history:
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(metrics_history)
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            'Passengers Transported', 'Active Services',
            'Average Delay (minutes)', 'On-Time Performance (%)'
        ],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Passengers transported
    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=df['passengers_transported'],
            mode='lines+markers',
            name='Passengers',
            line=dict(color='blue', width=3),
            marker=dict(size=6)
        ),
        row=1, col=1
    )
    
    # Active services
    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=df['active_services'],
            mode='lines+markers',
            name='Services',
            line=dict(color='green', width=3),
            marker=dict(size=6)
        ),
        row=1, col=2
    )
    
    # Average delay
    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=df['average_delay'],
            mode='lines+markers',
            name='Delay',
            line=dict(color='orange', width=3),
            marker=dict(size=6)
        ),
        row=2, col=1
    )
    
    # On-time performance
    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=df['on_time_performance'],
            mode='lines+markers',
            name='On-Time %',
            line=dict(color='purple', width=3),
            marker=dict(size=6)
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=600,
        showlegend=False,
        title_text="Live Performance Metrics",
        title_x=0.5
    )
    
    return fig

def main():
    """Main Streamlit application"""
    
    st.set_page_config(
        page_title="Mumbai Railway Live Simulation",
        page_icon="🚂",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚂 Mumbai Railway Live Simulation")
    st.markdown("**Real-time train movements and network performance**")
    
    # Initialize visualization controller
    if 'viz_controller' not in st.session_state:
        st.session_state.viz_controller = RealTimeVisualization()
    
    viz = st.session_state.viz_controller
    
    # Sidebar controls
    st.sidebar.header("🎮 Simulation Controls")
    
    # Factor selection
    st.sidebar.subheader("Factors to Test")
    available_factors = [
        'rush_hour_demand',
        'heavy_rain',
        'track_maintenance',
        'signal_failure',
        'passenger_incident',
        'power_outage'
    ]
    
    selected_factors = st.sidebar.multiselect(
        "Select factors to enable:",
        available_factors,
        help="Choose which factors to include in the simulation"
    )
    
    # Duration setting
    duration = st.sidebar.slider(
        "Simulation Duration (hours)",
        min_value=0.25,
        max_value=4.0,
        value=1.0,
        step=0.25
    )
    
    # Control buttons
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        if st.button("▶️ Start", use_container_width=True, type="primary"):
            if not viz.is_running:
                success = viz.start_simulation(selected_factors, duration)
                if success:
                    st.sidebar.success("Simulation started!")
                else:
                    st.sidebar.error("Failed to start simulation")
            else:
                st.sidebar.warning("Simulation already running")
    
    with col2:
        if st.button("⏹️ Stop", use_container_width=True):
            viz.stop_simulation()
            st.sidebar.success("Simulation stopped")
    
    # Status indicator
    if viz.is_running:
        st.sidebar.success("🟢 Simulation Running")
    else:
        st.sidebar.info("🔴 Simulation Stopped")
    
    # Main content area
    if viz.is_running or viz.train_positions or viz.metrics_history:
        
        # Get latest data
        latest_data = viz.get_latest_data()
        
        # Create two columns for layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🗺️ Live Network Map")
            
            # Create and display live map
            live_map = create_live_network_map(
                viz.train_positions,
                viz.passenger_flows,
                viz.network
            )
            
            # Display map
            map_data = st_folium(live_map, width=700, height=500)
        
        with col2:
            st.subheader("📊 Current Status")
            
            if latest_data:
                metrics = latest_data.get('metrics', {})
                
                # Display key metrics
                st.metric(
                    "Active Trains",
                    len(viz.train_positions),
                    delta=None
                )
                
                st.metric(
                    "Passengers Transported",
                    f"{metrics.get('total_passengers_transported', 0):,}"
                )
                
                st.metric(
                    "Average Delay",
                    f"{metrics.get('average_delay_minutes', 0):.1f} min"
                )
                
                st.metric(
                    "On-Time Performance",
                    f"{metrics.get('on_time_performance', 100):.1f}%"
                )
                
                # Current time
                current_time = latest_data.get('timestamp', datetime.now())
                st.info(f"⏰ Simulation Time: {current_time.strftime('%H:%M:%S')}")
        
        # Live charts section
        st.subheader("📈 Live Performance Charts")
        
        if viz.metrics_history:
            live_charts = create_live_metrics_charts(viz.metrics_history)
            if live_charts:
                st.plotly_chart(live_charts, use_container_width=True)
        
        # Train positions table
        if viz.train_positions:
            st.subheader("🚂 Train Status")
            
            train_df = pd.DataFrame([
                {
                    'Train ID': train_id,
                    'Line': data['line'],
                    'Direction': data['direction'],
                    'Current Station': data['current_station'],
                    'Next Station': data['next_station'],
                    'Passengers': data['passengers'],
                    'Delay (min)': f"{data['delay']:.1f}",
                    'Status': data['status']
                }
                for train_id, data in viz.train_positions.items()
            ])
            
            st.dataframe(train_df, use_container_width=True)
        
        # Auto-refresh
        if viz.is_running:
            time.sleep(2)  # Refresh every 2 seconds
            st.rerun()
    
    else:
        # Show instructions when not running
        st.info("""
        👆 **Start the simulation** using the controls in the sidebar to see:
        
        🚂 **Live train movements** across Mumbai's railway network
        
        📍 **Real-time positions** of trains between stations
        
        👥 **Passenger flows** and congestion at each station
        
        📊 **Live performance metrics** updated every minute
        
        🎯 **Factor impacts** showing how different conditions affect the network
        
        Select factors to test and click **Start** to begin the live visualization!
        """)

if __name__ == "__main__":
    main()
