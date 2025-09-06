"""
Train and Service Models for Mumbai Railway Simulation
Defines trains, services, and their operational characteristics.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
import uuid
from datetime import datetime, timedelta


class TrainType(Enum):
    """Types of trains in Mumbai suburban system"""
    LOCAL = "local"
    FAST = "fast"
    EXPRESS = "express"
    SUPER_FAST = "super_fast"


class TrainStatus(Enum):
    """Current status of a train"""
    SCHEDULED = "scheduled"
    BOARDING = "boarding"
    RUNNING = "running"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Direction(Enum):
    """Direction of travel"""
    UP = "up"        # Towards terminus (North/East)
    DOWN = "down"    # Away from terminus (South/West)


@dataclass
class TrainConfiguration:
    """Configuration for a train consist"""
    car_count: int = 12
    capacity_per_car: int = 350
    max_speed_kmh: int = 100
    acceleration: float = 1.2  # m/s²
    deceleration: float = 1.5  # m/s²
    door_opening_time: float = 20.0  # seconds
    door_closing_time: float = 15.0  # seconds


@dataclass
class Train:
    """Represents a physical train in the simulation"""
    id: str
    train_type: TrainType
    line: str
    direction: Direction
    config: TrainConfiguration
    current_station: Optional[str] = None
    next_station: Optional[str] = None
    current_position_km: float = 0.0
    current_speed_kmh: float = 0.0
    passenger_count: int = 0
    status: TrainStatus = TrainStatus.SCHEDULED
    delay_minutes: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]
    
    @property
    def total_capacity(self) -> int:
        """Total passenger capacity of the train"""
        return self.config.car_count * self.config.capacity_per_car
    
    @property
    def occupancy_ratio(self) -> float:
        """Current occupancy as a ratio of total capacity"""
        return self.passenger_count / self.total_capacity if self.total_capacity > 0 else 0.0
    
    @property
    def is_overcrowded(self) -> bool:
        """Check if train is overcrowded (>100% capacity)"""
        return self.occupancy_ratio > 1.0
    
    def board_passengers(self, count: int) -> int:
        """
        Board passengers onto the train
        Returns: actual number of passengers boarded
        """
        available_space = max(0, int(self.total_capacity * 1.3) - self.passenger_count)  # Allow 130% capacity
        actual_boarding = min(count, available_space)
        self.passenger_count += actual_boarding
        return actual_boarding
    
    def alight_passengers(self, count: int) -> int:
        """
        Passengers alighting from the train
        Returns: actual number of passengers alighted
        """
        actual_alighting = min(count, self.passenger_count)
        self.passenger_count -= actual_alighting
        return actual_alighting
    
    def update_position(self, position_km: float, speed_kmh: float):
        """Update train's current position and speed"""
        self.current_position_km = position_km
        self.current_speed_kmh = speed_kmh
        self.last_updated = datetime.now()
    
    def add_delay(self, minutes: float):
        """Add delay to the train"""
        self.delay_minutes += minutes
        if self.delay_minutes > 0:
            self.status = TrainStatus.DELAYED


@dataclass
class StationStop:
    """Represents a scheduled stop at a station"""
    station_id: str
    scheduled_arrival: datetime
    scheduled_departure: datetime
    actual_arrival: Optional[datetime] = None
    actual_departure: Optional[datetime] = None
    platform: Optional[int] = None
    boarding_count: int = 0
    alighting_count: int = 0
    dwell_time_seconds: float = 30.0  # default dwell time
    
    @property
    def arrival_delay_minutes(self) -> float:
        """Calculate arrival delay in minutes"""
        if self.actual_arrival:
            delay = (self.actual_arrival - self.scheduled_arrival).total_seconds() / 60
            return max(0, delay)
        return 0.0
    
    @property
    def departure_delay_minutes(self) -> float:
        """Calculate departure delay in minutes"""
        if self.actual_departure:
            delay = (self.actual_departure - self.scheduled_departure).total_seconds() / 60
            return max(0, delay)
        return 0.0


@dataclass
class Service:
    """Represents a train service (scheduled journey)"""
    id: str
    train: Train
    route: List[str]  # List of station IDs
    stops: List[StationStop]
    start_time: datetime
    end_time: datetime
    frequency_minutes: int = 15  # Service frequency
    is_active: bool = True
    
    def __post_init__(self):
        if not self.id:
            self.id = f"{self.train.line}_{self.train.direction.value}_{self.start_time.strftime('%H%M')}"
    
    @property
    def total_journey_time(self) -> timedelta:
        """Total scheduled journey time"""
        return self.end_time - self.start_time
    
    @property
    def current_delay(self) -> float:
        """Current overall delay in minutes"""
        return self.train.delay_minutes
    
    def get_next_stop(self) -> Optional[StationStop]:
        """Get the next scheduled stop"""
        current_time = datetime.now()
        for stop in self.stops:
            if stop.actual_departure is None and stop.scheduled_departure > current_time:
                return stop
        return None
    
    def get_current_stop(self) -> Optional[StationStop]:
        """Get the current stop if train is at a station"""
        if self.train.current_station:
            for stop in self.stops:
                if stop.station_id == self.train.current_station:
                    return stop
        return None
    
    def complete_stop(self, station_id: str, boarding: int, alighting: int):
        """Mark a stop as completed with passenger movements"""
        for stop in self.stops:
            if stop.station_id == station_id and stop.actual_departure is None:
                stop.actual_arrival = datetime.now()
                stop.boarding_count = boarding
                stop.alighting_count = alighting
                
                # Calculate dwell time based on passenger movements
                base_dwell = 30  # base 30 seconds
                passenger_time = (boarding + alighting) * 0.5  # 0.5 seconds per passenger
                stop.dwell_time_seconds = max(base_dwell, passenger_time)
                
                stop.actual_departure = stop.actual_arrival + timedelta(seconds=stop.dwell_time_seconds)
                break


class ServiceScheduler:
    """Manages train service schedules and frequencies"""
    
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.train_fleet: Dict[str, Train] = {}
    
    def create_train(self, train_type: TrainType, line: str, direction: Direction, 
                    config: Optional[TrainConfiguration] = None) -> Train:
        """Create a new train"""
        if config is None:
            config = TrainConfiguration()
        
        train = Train(
            id="",  # Will be auto-generated
            train_type=train_type,
            line=line,
            direction=direction,
            config=config
        )
        
        self.train_fleet[train.id] = train
        return train
    
    def create_service(self, train: Train, route: List[str], start_time: datetime, 
                      frequency_minutes: int = 15) -> Service:
        """Create a new service for a train"""
        # Generate station stops
        stops = []
        current_time = start_time
        
        for i, station_id in enumerate(route):
            # Estimate travel time between stations (simplified)
            if i > 0:
                current_time += timedelta(minutes=3)  # Average 3 minutes between stations
            
            stop = StationStop(
                station_id=station_id,
                scheduled_arrival=current_time,
                scheduled_departure=current_time + timedelta(seconds=30)  # 30 second stop
            )
            stops.append(stop)
            current_time = stop.scheduled_departure
        
        service = Service(
            id="",  # Will be auto-generated
            train=train,
            route=route,
            stops=stops,
            start_time=start_time,
            end_time=current_time,
            frequency_minutes=frequency_minutes
        )
        
        self.services[service.id] = service
        return service
    
    def get_active_services(self, current_time: datetime) -> List[Service]:
        """Get all currently active services"""
        active = []
        for service in self.services.values():
            if (service.is_active and 
                service.start_time <= current_time <= service.end_time):
                active.append(service)
        return active
    
    def get_services_by_line(self, line: str) -> List[Service]:
        """Get all services for a specific line"""
        return [service for service in self.services.values() 
                if service.train.line == line]
    
    def update_service_delays(self, service_id: str, delay_minutes: float):
        """Update delays for a specific service"""
        if service_id in self.services:
            service = self.services[service_id]
            service.train.add_delay(delay_minutes)
            
            # Propagate delay to future stops
            for stop in service.stops:
                if stop.actual_departure is None:
                    stop.scheduled_arrival += timedelta(minutes=delay_minutes)
                    stop.scheduled_departure += timedelta(minutes=delay_minutes)
