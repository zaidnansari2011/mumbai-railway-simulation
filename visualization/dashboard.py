"""
Real-time Simulation Dashboard using Streamlit
Creates an interactive web dashboard for demonstrating the Mumbai Railway simulation to non-technical users.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys
import os
from datetime import datetime, timedelta
import time
import numpy as np

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.network.mumbai_network import MumbaiRailwayNetwork, LineType
from src.simulation.engine import MumbaiRailwaySimulation, SimulationConfig
from src.factors.simulation_factors import (
    RushHourDemand, WeatherConditions, TrackMaintenance, 
    SignalFailure, PassengerIncident, PowerSupplyIssue
)


class SimulationDashboard:
    """Interactive dashboard for Mumbai Railway simulation"""
    
    def __init__(self):
        self.setup_page()
        self.network = MumbaiRailwayNetwork()
        
    def setup_page(self):
        """Setup Streamlit page configuration"""
        st.set_page_config(
            page_title="Mumbai Railway Simulation Dashboard",
            page_icon="🚂",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 50%, #45B7D1 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: #f0f2f6;
            padding: 1rem;
            border-radius: 10px;
            border-left: 5px solid #4ECDC4;
        }
        .factor-card {
            background: #fff;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #ddd;
            margin: 0.5rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def run(self):
        """Main dashboard interface"""
        
        # Header
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; text-align: center; margin: 0;">
                🚂 Mumbai Railway Simulation Dashboard
            </h1>
            <p style="color: white; text-align: center; margin: 0;">
                Interactive visualization of Mumbai's suburban railway network
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar controls
        self.create_sidebar()
        
        # Main dashboard
        if st.session_state.get('simulation_running', False):
            self.show_live_dashboard()
        else:
            self.show_setup_interface()
    
    def create_sidebar(self):
        """Create sidebar with simulation controls"""
        
        st.sidebar.markdown("## 🎛️ Simulation Controls")
        
        # Simulation parameters
        st.sidebar.markdown("### ⚙️ Basic Settings")
        duration = st.sidebar.slider("Simulation Duration (hours)", 1, 12, 2)
        start_hour = st.sidebar.selectbox("Start Hour", list(range(24)), index=7)
        time_speed = st.sidebar.selectbox("Simulation Speed", 
                                        [("Real-time", 1), ("2x Speed", 2), ("5x Speed", 5), ("10x Speed", 10)],
                                        index=2)
        
        # Factor selection
        st.sidebar.markdown("### 🔧 Disruption Factors")
        st.sidebar.markdown("*Select factors to test their impact:*")
        
        factors = {}
        factors['rush_hour'] = st.sidebar.checkbox("🕐 Rush Hour Demand", value=True)
        factors['heavy_rain'] = st.sidebar.checkbox("🌧️ Heavy Rain")
        factors['signal_failure'] = st.sidebar.checkbox("🚦 Signal Failure")
        factors['track_maintenance'] = st.sidebar.checkbox("🔧 Track Maintenance")
        factors['power_outage'] = st.sidebar.checkbox("⚡ Power Outage")
        factors['passenger_incident'] = st.sidebar.checkbox("👥 Passenger Incident")
        
        # Store in session state
        st.session_state['duration'] = duration
        st.session_state['start_hour'] = start_hour
        st.session_state['time_speed'] = time_speed[1]
        st.session_state['selected_factors'] = factors
        
        # Control buttons
        st.sidebar.markdown("### 🎮 Controls")
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("▶️ Start", type="primary"):
                self.start_simulation()
        
        with col2:
            if st.button("⏹️ Stop"):
                self.stop_simulation()
        
        if st.sidebar.button("🔄 Reset"):
            self.reset_simulation()
    
    def show_setup_interface(self):
        """Show simulation setup interface"""
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("## 🗺️ Network Overview")
            self.show_network_stats()
            
            st.markdown("## 📊 Available Scenarios")
            self.show_scenario_selection()
        
        with col2:
            st.markdown("## 🎯 Quick Start Guide")
            st.markdown("""
            **How to use this dashboard:**
            
            1. **Select factors** in the sidebar to test
            2. **Adjust settings** (duration, start time)
            3. **Click Start** to begin simulation
            4. **Watch real-time metrics** update
            5. **Compare scenarios** by changing factors
            
            **Understanding the factors:**
            - 🕐 **Rush Hour**: 2.5x passenger demand
            - 🌧️ **Heavy Rain**: Slower speeds, more delays
            - 🚦 **Signal Failure**: Network bottlenecks
            - 🔧 **Maintenance**: Reduced capacity
            - ⚡ **Power Outage**: Service disruptions
            - 👥 **Incidents**: Localized delays
            """)
            
            st.markdown("## 📈 Expected Results")
            st.info("""
            **Normal Operations**: 95% on-time, 1.5min avg delay
            **Rush Hour Only**: 88% on-time, 4.2min avg delay  
            **Heavy Rain**: 75% on-time, 8.5min avg delay
            **Multiple Factors**: 45% on-time, 15+ min delay
            """)
    
    def show_network_stats(self):
        """Display network statistics"""
        
        stats = self.network.get_network_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🚉 Total Stations", stats['total_stations'])
        
        with col2:
            st.metric("🛤️ Railway Lines", stats['lines'])
        
        with col3:
            st.metric("🔄 Interchange Stations", stats['interchange_stations'])
        
        with col4:
            st.metric("📏 Track Segments", stats['total_tracks'])
        
        # Network map would go here (simplified for now)
        st.markdown("### Railway Network Layout")
        
        # Create a simple network diagram
        lines_data = []
        for line in LineType:
            stations = self.network.get_stations_by_line(line)
            lines_data.append({
                'Line': line.value.title(),
                'Stations': len(stations),
                'Color': {'western': '#FF6B6B', 'central_main': '#4ECDC4', 
                         'central_harbour': '#45B7D1', 'trans_harbour': '#96CEB4'}[line.value]
            })
        
        df_lines = pd.DataFrame(lines_data)
        
        fig = px.bar(df_lines, x='Line', y='Stations', 
                    color='Line',
                    color_discrete_map={row['Line']: row['Color'] for _, row in df_lines.iterrows()},
                    title="Stations per Railway Line")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    def show_scenario_selection(self):
        """Show predefined scenario selection"""
        
        scenarios = {
            "Normal Day": {"factors": [], "description": "Baseline operations without disruptions"},
            "Rush Hour Peak": {"factors": ["rush_hour"], "description": "High passenger demand during peak hours"},
            "Monsoon Day": {"factors": ["rush_hour", "heavy_rain"], "description": "Rain + rush hour combination"},
            "Technical Issues": {"factors": ["signal_failure", "power_outage"], "description": "Infrastructure failures"},
            "Emergency Response": {"factors": ["track_maintenance", "passenger_incident"], "description": "Emergency maintenance scenario"},
            "Perfect Storm": {"factors": ["rush_hour", "heavy_rain", "signal_failure"], "description": "Multiple simultaneous disruptions"}
        }
        
        selected_scenario = st.selectbox("Choose a predefined scenario:", list(scenarios.keys()))
        
        if selected_scenario:
            scenario = scenarios[selected_scenario]
            st.markdown(f"**{selected_scenario}**: {scenario['description']}")
            
            if st.button(f"Load {selected_scenario} Scenario"):
                # Update session state with scenario factors
                factors = st.session_state.get('selected_factors', {})
                for factor in factors:
                    factors[factor] = factor in scenario['factors']
                st.session_state['selected_factors'] = factors
                st.experimental_rerun()
    
    def start_simulation(self):
        """Start the simulation"""
        
        st.session_state['simulation_running'] = True
        
        # Create simulation config
        config = SimulationConfig(
            start_time=datetime.now().replace(
                hour=st.session_state['start_hour'], 
                minute=0, second=0, microsecond=0
            ),
            duration_hours=st.session_state['duration'],
            time_step_seconds=60,
            enable_logging=False
        )
        
        # Initialize simulation
        sim = MumbaiRailwaySimulation(config)
        sim.create_train_services(LineType.WESTERN, 8, 8)
        sim.create_train_services(LineType.CENTRAL_MAIN, 6, 10)
        sim.create_train_services(LineType.CENTRAL_HARBOUR, 4, 15)
        
        # Add selected factors
        factors = st.session_state.get('selected_factors', {})
        if factors.get('rush_hour'):
            rush_hour = RushHourDemand(peak_multiplier=2.5)
            sim.factor_manager.add_factor(rush_hour)
            sim.factor_manager.enable_factor(rush_hour.name)
        
        if factors.get('heavy_rain'):
            rain = WeatherConditions("heavy_rain", intensity=0.8)
            sim.factor_manager.add_factor(rain)
            sim.factor_manager.enable_factor(rain.name)
        
        if factors.get('signal_failure'):
            signal = SignalFailure("temporary")
            sim.factor_manager.add_factor(signal)
            sim.factor_manager.enable_factor(signal.name)
        
        if factors.get('track_maintenance'):
            maintenance = TrackMaintenance("scheduled")
            sim.factor_manager.add_factor(maintenance)
            sim.factor_manager.enable_factor(maintenance.name)
        
        if factors.get('power_outage'):
            power = PowerSupplyIssue("partial")
            sim.factor_manager.add_factor(power)
            sim.factor_manager.enable_factor(power.name)
        
        if factors.get('passenger_incident'):
            incident = PassengerIncident("medical_emergency")
            sim.factor_manager.add_factor(incident)
            sim.factor_manager.enable_factor(incident.name)
        
        st.session_state['simulation'] = sim
        st.session_state['metrics_history'] = []
        st.experimental_rerun()
    
    def stop_simulation(self):
        """Stop the simulation"""
        st.session_state['simulation_running'] = False
        if 'simulation' in st.session_state:
            st.session_state['simulation'].stop()
    
    def reset_simulation(self):
        """Reset the simulation"""
        st.session_state['simulation_running'] = False
        for key in ['simulation', 'metrics_history']:
            if key in st.session_state:
                del st.session_state[key]
    
    def show_live_dashboard(self):
        """Show the live simulation dashboard"""
        
        sim = st.session_state.get('simulation')
        if not sim:
            st.error("No simulation found. Please start a new simulation.")
            return
        
        # Run simulation step
        sim.run_simulation_step(sim.current_time)
        sim.current_time += timedelta(minutes=1)
        
        # Update metrics history
        if 'metrics_history' not in st.session_state:
            st.session_state['metrics_history'] = []
        
        current_metrics = {
            'time': sim.current_time,
            'avg_delay': sim.metrics.average_delay_minutes,
            'on_time_performance': sim.metrics.on_time_performance,
            'network_efficiency': sim.metrics.network_efficiency,
            'capacity_utilization': sim.metrics.capacity_utilization,
            'total_passengers': sim.metrics.total_passengers_transported,
            'active_services': len([s for s in sim.active_services if s.is_active]),
            'total_waiting': sum(sim.passengers_waiting.values())
        }
        
        st.session_state['metrics_history'].append(current_metrics)
        
        # Display dashboard
        self.display_live_metrics(current_metrics)
        self.display_time_series_charts()
        self.display_network_status(sim)
        self.display_factor_impacts(sim)
        
        # Auto-refresh
        time.sleep(1 / st.session_state['time_speed'])
        st.experimental_rerun()
    
    def display_live_metrics(self, metrics):
        """Display current simulation metrics"""
        
        st.markdown("## 📊 Live Performance Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "⏱️ On-Time Performance", 
                f"{metrics['on_time_performance']:.1f}%",
                delta=f"{metrics['on_time_performance'] - 85:.1f}%" if len(st.session_state['metrics_history']) > 1 else None
            )
        
        with col2:
            st.metric(
                "⏰ Average Delay", 
                f"{metrics['avg_delay']:.1f} min",
                delta=f"{metrics['avg_delay'] - 5:.1f} min" if len(st.session_state['metrics_history']) > 1 else None
            )
        
        with col3:
            st.metric(
                "📈 Network Efficiency", 
                f"{metrics['network_efficiency']:.1f}%",
                delta=f"{metrics['network_efficiency'] - 90:.1f}%" if len(st.session_state['metrics_history']) > 1 else None
            )
        
        with col4:
            st.metric(
                "🚂 Active Trains", 
                metrics['active_services']
            )
        
        with col5:
            st.metric(
                "👥 Passengers Waiting", 
                f"{metrics['total_waiting']:,}"
            )
    
    def display_time_series_charts(self):
        """Display time series charts of key metrics"""
        
        if len(st.session_state['metrics_history']) < 2:
            return
        
        df = pd.DataFrame(st.session_state['metrics_history'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=df['time'], 
                y=df['on_time_performance'],
                mode='lines+markers',
                name='On-Time Performance',
                line=dict(color='#4ECDC4')
            ))
            fig1.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="Target: 85%")
            fig1.update_layout(title="On-Time Performance Over Time", yaxis_title="Percentage")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df['time'], 
                y=df['avg_delay'],
                mode='lines+markers',
                name='Average Delay',
                line=dict(color='#FF6B6B')
            ))
            fig2.add_hline(y=5, line_dash="dash", line_color="green", annotation_text="Target: <5 min")
            fig2.update_layout(title="Average Delay Over Time", yaxis_title="Minutes")
            st.plotly_chart(fig2, use_container_width=True)
    
    def display_network_status(self, sim):
        """Display current network status"""
        
        st.markdown("## 🗺️ Network Status")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Station passenger counts
            station_data = []
            for station_id, waiting in sim.passengers_waiting.items():
                station = sim.network.stations.get(station_id)
                if station and waiting > 0:
                    station_data.append({
                        'Station': station.name,
                        'Waiting': waiting,
                        'Line': station.line.value.title()
                    })
            
            if station_data:
                df_stations = pd.DataFrame(station_data).sort_values('Waiting', ascending=False).head(10)
                
                fig = px.bar(df_stations, x='Waiting', y='Station', orientation='h',
                           color='Line', title="Top 10 Stations by Passenger Queue")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Train status summary
            status_counts = {}
            for service in sim.active_services:
                status = service.train.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            if status_counts:
                fig = px.pie(values=list(status_counts.values()), 
                           names=list(status_counts.keys()),
                           title="Train Status Distribution")
                st.plotly_chart(fig, use_container_width=True)
    
    def display_factor_impacts(self, sim):
        """Display current factor impacts"""
        
        st.markdown("## 🔧 Active Disruption Factors")
        
        active_factors = sim.factor_manager.get_active_factors(sim.current_time)
        
        if active_factors:
            for factor in active_factors:
                impact = factor.calculate_impact(sim.current_time, {})
                
                with st.expander(f"{factor.name} - {factor.severity.value.title()} Impact"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Delay Multiplier", f"{impact.delay_multiplier:.2f}x")
                    
                    with col2:
                        st.metric("Speed Impact", f"{impact.speed_multiplier:.2f}x")
                    
                    with col3:
                        st.metric("Capacity Impact", f"{impact.capacity_multiplier:.2f}x")
        else:
            st.info("No active disruption factors - normal operations")


def main():
    """Main function to run the dashboard"""
    dashboard = SimulationDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
