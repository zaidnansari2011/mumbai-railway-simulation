"""
Main Simulation Engine for Mumbai Railway Network
Orchestrates the entire simulation with modular factor testing capability.
"""

import simpy
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import logging
from dataclasses import dataclass, field
import json

from src.network.mumbai_network import MumbaiRailwayNetwork, LineType
from src.simulation.trains import ServiceScheduler, Train, Service, TrainStatus
from src.factors.simulation_factors import FactorManager, FactorImpact


@dataclass
class SimulationMetrics:
    """Metrics collected during simulation"""
    total_passengers_transported: int = 0
    average_delay_minutes: float = 0.0
    total_delays: int = 0
    cancelled_services: int = 0
    passenger_satisfaction: float = 100.0
    network_efficiency: float = 100.0
    on_time_performance: float = 100.0
    capacity_utilization: float = 0.0
    incidents_count: int = 0
    
    # Time series data
    hourly_delays: List[float] = field(default_factory=list)
    hourly_passenger_counts: List[int] = field(default_factory=list)
    hourly_efficiency: List[float] = field(default_factory=list)


@dataclass
class SimulationConfig:
    """Configuration for the simulation"""
    start_time: datetime
    duration_hours: int = 24
    time_step_seconds: int = 60  # 1 minute time steps
    real_time_factor: float = 1.0  # 1.0 = real time, 60.0 = 1 hour per minute
    enable_logging: bool = True
    log_level: str = "INFO"
    collect_metrics: bool = True
    random_seed: Optional[int] = None


class MumbaiRailwaySimulation:
    """Main simulation engine for Mumbai Railway Network"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.env = simpy.Environment()
        self.network = MumbaiRailwayNetwork()
        self.scheduler = ServiceScheduler()
        self.factor_manager = FactorManager()
        self.metrics = SimulationMetrics()
        
        # Simulation state
        self.current_time = config.start_time
        self.is_running = False
        self.passengers_waiting: Dict[str, int] = {}  # station_id -> passenger_count
        self.active_services: List[Service] = []
        
        # Event callbacks
        self.event_callbacks: Dict[str, List[Callable]] = {
            "train_arrival": [],
            "train_departure": [],
            "passenger_boarding": [],
            "delay_occurred": [],
            "factor_activated": [],
            "incident_occurred": []
        }
        
        # Real-time update callbacks
        self.update_callbacks: List[Callable] = []
        
        self._setup_logging()
        self._initialize_passenger_demand()
        self._create_preset_factors()
    
    def _setup_logging(self):
        """Setup logging for the simulation"""
        if self.config.enable_logging:
            logging.basicConfig(
                level=getattr(logging, self.config.log_level),
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger("MumbaiRailwaySimulation")
        else:
            self.logger = logging.getLogger("MumbaiRailwaySimulation")
            self.logger.disabled = True
    
    def _initialize_passenger_demand(self):
        """Initialize passenger waiting at each station"""
        for station_id in self.network.stations.keys():
            self.passengers_waiting[station_id] = 0
    
    def _create_preset_factors(self):
        """Create and add preset factors to the simulation"""
        self.factor_manager.create_preset_scenarios()
    
    def add_event_callback(self, event_type: str, callback: Callable):
        """Add a callback function for specific simulation events"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    def add_update_callback(self, callback: Callable):
        """Add a callback function for real-time simulation updates"""
        self.update_callbacks.append(callback)
    
    def _trigger_update_callbacks(self, sim_time: datetime, metrics: Dict[str, Any]):
        """Trigger all real-time update callbacks"""
        for callback in self.update_callbacks:
            try:
                # If callback returns False, stop the simulation
                result = callback(sim_time, metrics)
                if result is False:
                    return False
            except Exception as e:
                self.logger.error(f"Error in update callback: {e}")
        return True
    
    def _trigger_event(self, event_type: str, data: Dict[str, Any]):
        """Trigger all callbacks for a specific event type"""
        for callback in self.event_callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"Error in event callback for {event_type}: {e}")
    
    def create_train_services(self, line: LineType, service_count: int = 10, 
                            frequency_minutes: int = 15):
        """Create train services for a specific line"""
        stations = self.network.get_stations_by_line(line)
        if len(stations) < 2:
            self.logger.warning(f"Not enough stations for line {line.value}")
            return
        
        station_ids = [station.id for station in stations]
        
        # Create services in both directions
        for direction in ["up", "down"]:
            route = station_ids if direction == "up" else station_ids[::-1]
            
            for i in range(service_count):
                # Create train
                from src.simulation.trains import TrainType, Direction
                train_direction = Direction.UP if direction == "up" else Direction.DOWN
                train = self.scheduler.create_train(
                    TrainType.LOCAL, 
                    line.value, 
                    train_direction
                )
                
                # Create service
                start_time = self.config.start_time + timedelta(minutes=i * frequency_minutes)
                service = self.scheduler.create_service(
                    train, route, start_time, frequency_minutes
                )
                
                self.active_services.append(service)
    
    def generate_passenger_demand(self, station_id: str, current_time: datetime) -> int:
        """Generate passenger demand for a station based on time and factors"""
        base_demand = 50  # Base passengers per time step
        
        # Time-based demand patterns
        hour = current_time.hour
        time_multiplier = 1.0
        
        # Rush hour patterns
        if 7 <= hour <= 10 or 17 <= hour <= 20:  # Rush hours
            time_multiplier = 2.5
        elif 11 <= hour <= 16:  # Mid-day
            time_multiplier = 1.2
        elif 21 <= hour <= 23 or 6 <= hour <= 6:  # Late evening/early morning
            time_multiplier = 0.8
        else:  # Night time
            time_multiplier = 0.3
        
        # Apply factor impacts
        factor_impact = self.factor_manager.calculate_combined_impact(current_time, {})
        demand_multiplier = factor_impact.demand_multiplier
        
        # Calculate final demand
        final_demand = int(base_demand * time_multiplier * demand_multiplier)
        
        # Add some randomness
        import random
        final_demand = max(0, final_demand + random.randint(-10, 10))
        
        return final_demand
    
    def simulate_train_movement(self, service: Service, current_time: datetime):
        """Simulate train movement and station operations"""
        if not service.is_active:
            return
        
        train = service.train
        next_stop = service.get_next_stop()
        
        if next_stop is None:
            # Service completed
            train.status = TrainStatus.COMPLETED
            service.is_active = False
            return
        
        # Check if train should be at the station
        if (next_stop.scheduled_arrival <= current_time and 
            next_stop.actual_arrival is None):
            
            # Train arrives at station
            station_id = next_stop.station_id
            train.current_station = station_id
            train.status = TrainStatus.BOARDING
            
            # Apply factor impacts
            factor_impact = self.factor_manager.calculate_combined_impact(current_time, {})
            
            # Calculate delays
            base_delay = 0
            if factor_impact.delay_multiplier > 1.0:
                base_delay = (factor_impact.delay_multiplier - 1.0) * 2  # 2 minutes per unit
            
            # Passenger movements
            passengers_waiting = self.passengers_waiting.get(station_id, 0)
            alighting = min(train.passenger_count, int(train.passenger_count * 0.3))  # 30% alight
            
            # Adjust boarding based on capacity and factor impacts
            max_boarding = min(passengers_waiting, 
                             int((train.total_capacity * factor_impact.capacity_multiplier) - 
                                 train.passenger_count + alighting))
            
            boarding = max(0, max_boarding)
            
            # Update passenger counts
            train.alight_passengers(alighting)
            actual_boarding = train.board_passengers(boarding)
            self.passengers_waiting[station_id] = max(0, passengers_waiting - actual_boarding)
            
            # Calculate dwell time
            base_dwell = 30  # seconds
            passenger_dwell = (boarding + alighting) * 0.5
            total_dwell = max(base_dwell, passenger_dwell) * factor_impact.delay_multiplier
            
            # Update stop information
            next_stop.actual_arrival = current_time
            next_stop.boarding_count = actual_boarding
            next_stop.alighting_count = alighting
            next_stop.dwell_time_seconds = total_dwell
            next_stop.actual_departure = current_time + timedelta(seconds=total_dwell)
            
            # Add delays
            if base_delay > 0:
                train.add_delay(base_delay)
                self.metrics.total_delays += 1
            
            # Update metrics
            self.metrics.total_passengers_transported += actual_boarding
            
            # Trigger events
            self._trigger_event("train_arrival", {
                "service_id": service.id,
                "station_id": station_id,
                "boarding": actual_boarding,
                "alighting": alighting,
                "delay": base_delay,
                "timestamp": current_time
            })
            
            self.logger.info(f"Train {train.id} arrived at {station_id}: "
                           f"Boarding: {actual_boarding}, Alighting: {alighting}, "
                           f"Delay: {base_delay:.1f}min")
        
        # Check if train should depart
        elif (next_stop.actual_departure and 
              current_time >= next_stop.actual_departure and 
              train.status == TrainStatus.BOARDING):
            
            # Train departs
            train.status = TrainStatus.RUNNING
            train.current_station = None
            
            self._trigger_event("train_departure", {
                "service_id": service.id,
                "station_id": next_stop.station_id,
                "passenger_count": train.passenger_count,
                "timestamp": current_time
            })
    
    def update_passenger_demand(self, current_time: datetime):
        """Update passenger demand at all stations"""
        for station_id in self.network.stations.keys():
            new_passengers = self.generate_passenger_demand(station_id, current_time)
            self.passengers_waiting[station_id] += new_passengers
    
    def update_metrics(self, current_time: datetime):
        """Update simulation metrics"""
        if not self.config.collect_metrics:
            return
        
        # Calculate delays
        total_delay = sum(service.current_delay for service in self.active_services)
        active_services_count = len([s for s in self.active_services if s.is_active])
        
        if active_services_count > 0:
            self.metrics.average_delay_minutes = total_delay / active_services_count
        
        # Calculate on-time performance
        on_time_services = len([s for s in self.active_services 
                               if s.current_delay <= 5.0])  # Within 5 minutes
        if len(self.active_services) > 0:
            self.metrics.on_time_performance = (on_time_services / len(self.active_services)) * 100
        
        # Calculate capacity utilization
        total_capacity = sum(service.train.total_capacity for service in self.active_services)
        total_passengers = sum(service.train.passenger_count for service in self.active_services)
        
        if total_capacity > 0:
            self.metrics.capacity_utilization = (total_passengers / total_capacity) * 100
        
        # Network efficiency (inverse of average delay)
        self.metrics.network_efficiency = max(0, 100 - self.metrics.average_delay_minutes * 2)
        
        # Store hourly data
        if current_time.minute == 0:  # At the start of each hour
            self.metrics.hourly_delays.append(self.metrics.average_delay_minutes)
            self.metrics.hourly_passenger_counts.append(
                sum(self.passengers_waiting.values())
            )
            self.metrics.hourly_efficiency.append(self.metrics.network_efficiency)
    
    def run_simulation_step(self, current_time: datetime):
        """Run a single simulation time step"""
        # Update passenger demand
        self.update_passenger_demand(current_time)
        
        # Simulate all active train services
        for service in self.active_services:
            self.simulate_train_movement(service, current_time)
        
        # Update metrics
        self.update_metrics(current_time)
        
        # Log status every 15 minutes
        if current_time.minute % 15 == 0:
            active_count = len([s for s in self.active_services if s.is_active])
            total_waiting = sum(self.passengers_waiting.values())
            self.logger.info(f"Time: {current_time.strftime('%H:%M')} - "
                           f"Active services: {active_count}, "
                           f"Total waiting: {total_waiting}, "
                           f"Avg delay: {self.metrics.average_delay_minutes:.1f}min")
    
    def run(self, duration_hours: Optional[int] = None) -> SimulationMetrics:
        """Run the simulation for the specified duration"""
        duration = duration_hours or self.config.duration_hours
        end_time = self.config.start_time + timedelta(hours=duration)
        
        self.logger.info(f"Starting simulation from {self.config.start_time} "
                        f"for {duration} hours")
        
        self.is_running = True
        current_time = self.config.start_time
        
        while current_time < end_time and self.is_running:
            self.current_time = current_time
            self.run_simulation_step(current_time)
            
            # Trigger real-time update callbacks
            if self.update_callbacks:
                metrics_data = self.get_current_metrics()
                should_continue = self._trigger_update_callbacks(current_time, metrics_data)
                if not should_continue:
                    self.logger.info("Simulation stopped by callback")
                    break
            
            # Advance time
            current_time += timedelta(seconds=self.config.time_step_seconds)
        
        self.is_running = False
        self.logger.info("Simulation completed")
        
        return self.metrics
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current simulation metrics for real-time updates"""
        active_services_data = []
        for service in self.active_services:
            if service.is_active:
                active_services_data.append({
                    'line': service.train.line,
                    'direction': service.train.direction.value,
                    'passenger_count': getattr(service, 'current_passengers', 0),
                    'delay_minutes': getattr(service, 'current_delay', 0),
                    'current_station': getattr(service, 'current_station', None)
                })
        
        station_metrics = {}
        for station_id, waiting_count in self.passengers_waiting.items():
            station_name = self.network.stations.get(station_id, {}).get('name', station_id)
            station_metrics[station_name] = {
                'waiting_passengers': waiting_count,
                'passengers_boarded_last_interval': 0,  # Would be tracked in full implementation
                'passengers_alighted_last_interval': 0
            }
        
        return {
            'total_passengers_transported': self.metrics.total_passengers_transported,
            'active_services': active_services_data,
            'average_delay_minutes': self.metrics.average_delay_minutes,
            'on_time_performance': self.metrics.on_time_performance,
            'network_efficiency': self.metrics.network_efficiency,
            'total_waiting_passengers': sum(self.passengers_waiting.values()),
            'station_metrics': station_metrics,
            'active_factors': [f.name for f in self.factor_manager.get_active_factors(self.current_time)]
        }
    
    def stop(self):
        """Stop the simulation"""
        self.is_running = False
        self.logger.info("Simulation stopped")
    
    def get_simulation_state(self) -> Dict[str, Any]:
        """Get current simulation state"""
        return {
            "current_time": self.current_time,
            "is_running": self.is_running,
            "active_services": len([s for s in self.active_services if s.is_active]),
            "total_passengers_waiting": sum(self.passengers_waiting.values()),
            "active_factors": [f.name for f in self.factor_manager.get_active_factors(self.current_time)],
            "metrics": self.metrics,
            "network_stats": self.network.get_network_stats()
        }
    
    def export_results(self, filename: str):
        """Export simulation results to JSON file"""
        results = {
            "config": {
                "start_time": self.config.start_time.isoformat(),
                "duration_hours": self.config.duration_hours,
                "time_step_seconds": self.config.time_step_seconds
            },
            "final_state": self.get_simulation_state(),
            "metrics": self.metrics.__dict__,
            "factor_report": self.factor_manager.get_factor_report(self.current_time)
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Results exported to {filename}")


# Convenience function for quick testing
def run_quick_test(factors_to_enable: List[str] = None, duration_hours: int = 2):
    """Run a quick test simulation with specified factors"""
    from datetime import datetime
    
    config = SimulationConfig(
        start_time=datetime.now().replace(hour=7, minute=0, second=0, microsecond=0),
        duration_hours=duration_hours,
        time_step_seconds=60
    )
    
    sim = MumbaiRailwaySimulation(config)
    
    # Create some services
    sim.create_train_services(LineType.WESTERN, 5, 15)
    sim.create_train_services(LineType.CENTRAL_MAIN, 5, 15)
    
    # Enable specified factors
    if factors_to_enable:
        for factor_name in factors_to_enable:
            sim.factor_manager.enable_factor(factor_name, duration_minutes=duration_hours*60)
    
    # Run simulation
    metrics = sim.run()
    
    print(f"Simulation completed!")
    print(f"Total passengers transported: {metrics.total_passengers_transported}")
    print(f"Average delay: {metrics.average_delay_minutes:.1f} minutes")
    print(f"On-time performance: {metrics.on_time_performance:.1f}%")
    print(f"Network efficiency: {metrics.network_efficiency:.1f}%")
    
    return sim, metrics
