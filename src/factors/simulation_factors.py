"""
Simulation Factors for Mumbai Railway Network
Modular factors that can be enabled/disabled to test their impact on network performance.
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable
import random
import numpy as np
from datetime import datetime, timedelta


class FactorCategory(Enum):
    """Categories of factors affecting railway operations"""
    INFRASTRUCTURE = "infrastructure"
    PASSENGER_DEMAND = "passenger_demand"
    WEATHER = "weather"
    OPERATIONAL = "operational"
    EXTERNAL_EVENTS = "external_events"
    TECHNICAL = "technical"


class FactorSeverity(Enum):
    """Severity levels for factors"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FactorImpact:
    """Represents the impact of a factor on the simulation"""
    delay_multiplier: float = 1.0
    capacity_multiplier: float = 1.0
    speed_multiplier: float = 1.0
    demand_multiplier: float = 1.0
    failure_probability: float = 0.0
    duration_minutes: Optional[int] = None


class SimulationFactor(ABC):
    """Base class for all simulation factors"""
    
    def __init__(self, name: str, category: FactorCategory, severity: FactorSeverity, 
                 enabled: bool = False):
        self.name = name
        self.category = category
        self.severity = severity
        self.enabled = enabled
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.affected_lines: List[str] = []
        self.affected_stations: List[str] = []
    
    @abstractmethod
    def calculate_impact(self, current_time: datetime, context: Dict[str, Any]) -> FactorImpact:
        """Calculate the current impact of this factor"""
        pass
    
    @abstractmethod
    def is_active(self, current_time: datetime) -> bool:
        """Check if the factor is currently active"""
        pass
    
    def enable(self, start_time: Optional[datetime] = None, duration_minutes: Optional[int] = None):
        """Enable the factor"""
        self.enabled = True
        self.start_time = start_time or datetime.now()
        if duration_minutes:
            self.end_time = self.start_time + timedelta(minutes=duration_minutes)
    
    def disable(self):
        """Disable the factor"""
        self.enabled = False
        self.end_time = datetime.now()


class RushHourDemand(SimulationFactor):
    """Rush hour passenger demand factor"""
    
    def __init__(self, peak_multiplier: float = 2.5):
        super().__init__("Rush Hour Demand", FactorCategory.PASSENGER_DEMAND, FactorSeverity.HIGH)
        self.peak_multiplier = peak_multiplier
        self.morning_peak = (7, 10)  # 7 AM to 10 AM
        self.evening_peak = (17, 20)  # 5 PM to 8 PM
    
    def calculate_impact(self, current_time: datetime, context: Dict[str, Any]) -> FactorImpact:
        if not self.is_active(current_time):
            return FactorImpact()
        
        hour = current_time.hour
        demand_multiplier = 1.0
        
        # Morning peak
        if self.morning_peak[0] <= hour <= self.morning_peak[1]:
            demand_multiplier = self.peak_multiplier
        # Evening peak
        elif self.evening_peak[0] <= hour <= self.evening_peak[1]:
            demand_multiplier = self.peak_multiplier
        
        # Increased dwell time due to crowding
        delay_multiplier = 1.0 + (demand_multiplier - 1.0) * 0.3
        
        return FactorImpact(
            delay_multiplier=delay_multiplier,
            demand_multiplier=demand_multiplier
        )
    
    def is_active(self, current_time: datetime) -> bool:
        return self.enabled


class WeatherConditions(SimulationFactor):
    """Weather-related disruptions"""
    
    def __init__(self, weather_type: str = "heavy_rain", intensity: float = 0.8):
        severity = FactorSeverity.HIGH if intensity > 0.7 else FactorSeverity.MEDIUM
        super().__init__(f"Weather: {weather_type}", FactorCategory.WEATHER, severity)
        self.weather_type = weather_type
        self.intensity = intensity  # 0.0 to 1.0
    
    def calculate_impact(self, current_time: datetime, context: Dict[str, Any]) -> FactorImpact:
        if not self.is_active(current_time):
            return FactorImpact()
        
        impact = FactorImpact()
        
        if self.weather_type == "heavy_rain":
            impact.speed_multiplier = 1.0 - (self.intensity * 0.4)  # Up to 40% speed reduction
            impact.delay_multiplier = 1.0 + (self.intensity * 0.6)  # Up to 60% more delays
            impact.failure_probability = self.intensity * 0.1  # Up to 10% failure chance
        
        elif self.weather_type == "fog":
            impact.speed_multiplier = 1.0 - (self.intensity * 0.3)  # Up to 30% speed reduction
            impact.delay_multiplier = 1.0 + (self.intensity * 0.4)  # Up to 40% more delays
        
        elif self.weather_type == "extreme_heat":
            impact.speed_multiplier = 1.0 - (self.intensity * 0.2)  # Up to 20% speed reduction
            impact.failure_probability = self.intensity * 0.05  # Up to 5% failure chance
        
        return impact
    
    def is_active(self, current_time: datetime) -> bool:
        if not self.enabled:
            return False
        if self.start_time and current_time < self.start_time:
            return False
        if self.end_time and current_time > self.end_time:
            return False
        return True


class TrackMaintenance(SimulationFactor):
    """Scheduled or emergency track maintenance"""
    
    def __init__(self, maintenance_type: str = "scheduled", affected_tracks: List[str] = None):
        severity = FactorSeverity.CRITICAL if maintenance_type == "emergency" else FactorSeverity.MEDIUM
        super().__init__(f"Track Maintenance: {maintenance_type}", 
                        FactorCategory.INFRASTRUCTURE, severity)
        self.maintenance_type = maintenance_type
        self.affected_tracks = affected_tracks or []
    
    def calculate_impact(self, current_time: datetime, context: Dict[str, Any]) -> FactorImpact:
        if not self.is_active(current_time):
            return FactorImpact()
        
        if self.maintenance_type == "emergency":
            # Emergency maintenance causes severe disruptions
            return FactorImpact(
                capacity_multiplier=0.5,  # 50% capacity reduction
                delay_multiplier=2.0,     # Double delays
                speed_multiplier=0.7      # 30% speed reduction
            )
        else:
            # Scheduled maintenance has moderate impact
            return FactorImpact(
                capacity_multiplier=0.8,  # 20% capacity reduction
                delay_multiplier=1.3,     # 30% more delays
                speed_multiplier=0.9      # 10% speed reduction
            )
    
    def is_active(self, current_time: datetime) -> bool:
        if not self.enabled:
            return False
        if self.start_time and current_time < self.start_time:
            return False
        if self.end_time and current_time > self.end_time:
            return False
        return True


class SignalFailure(SimulationFactor):
    """Signal system failures"""
    
    def __init__(self, failure_type: str = "temporary", affected_signals: List[str] = None):
        severity = FactorSeverity.CRITICAL if failure_type == "complete" else FactorSeverity.HIGH
        super().__init__(f"Signal Failure: {failure_type}", 
                        FactorCategory.TECHNICAL, severity)
        self.failure_type = failure_type
        self.affected_signals = affected_signals or []
    
    def calculate_impact(self, current_time: datetime, context: Dict[str, Any]) -> FactorImpact:
        if not self.is_active(current_time):
            return FactorImpact()
        
        if self.failure_type == "complete":
            return FactorImpact(
                capacity_multiplier=0.3,  # 70% capacity reduction
                delay_multiplier=3.0,     # Triple delays
                speed_multiplier=0.4      # 60% speed reduction
            )
        else:
            return FactorImpact(
                capacity_multiplier=0.7,  # 30% capacity reduction
                delay_multiplier=1.8,     # 80% more delays
                speed_multiplier=0.6      # 40% speed reduction
            )
    
    def is_active(self, current_time: datetime) -> bool:
        if not self.enabled:
            return False
        if self.start_time and current_time < self.start_time:
            return False
        if self.end_time and current_time > self.end_time:
            return False
        return True


class PassengerIncident(SimulationFactor):
    """Passenger-related incidents (medical emergency, unruly behavior, etc.)"""
    
    def __init__(self, incident_type: str = "medical_emergency"):
        severity = FactorSeverity.MEDIUM
        super().__init__(f"Passenger Incident: {incident_type}", 
                        FactorCategory.OPERATIONAL, severity)
        self.incident_type = incident_type
        self.typical_duration = {
            "medical_emergency": 15,
            "unruly_passenger": 10,
            "luggage_issue": 5,
            "door_malfunction": 8
        }
    
    def calculate_impact(self, current_time: datetime, context: Dict[str, Any]) -> FactorImpact:
        if not self.is_active(current_time):
            return FactorImpact()
        
        # Incidents typically cause localized delays
        return FactorImpact(
            delay_multiplier=1.5,     # 50% more delays
            duration_minutes=self.typical_duration.get(self.incident_type, 10)
        )
    
    def is_active(self, current_time: datetime) -> bool:
        if not self.enabled:
            return False
        if self.start_time and current_time < self.start_time:
            return False
        if self.end_time and current_time > self.end_time:
            return False
        return True


class PowerSupplyIssue(SimulationFactor):
    """Power supply disruptions"""
    
    def __init__(self, outage_type: str = "partial", affected_sections: List[str] = None):
        severity = FactorSeverity.CRITICAL if outage_type == "complete" else FactorSeverity.HIGH
        super().__init__(f"Power Outage: {outage_type}", 
                        FactorCategory.INFRASTRUCTURE, severity)
        self.outage_type = outage_type
        self.affected_sections = affected_sections or []
    
    def calculate_impact(self, current_time: datetime, context: Dict[str, Any]) -> FactorImpact:
        if not self.is_active(current_time):
            return FactorImpact()
        
        if self.outage_type == "complete":
            return FactorImpact(
                capacity_multiplier=0.0,  # Complete shutdown
                delay_multiplier=10.0,    # Massive delays
                speed_multiplier=0.0      # No movement
            )
        else:
            return FactorImpact(
                capacity_multiplier=0.6,  # 40% capacity reduction
                delay_multiplier=2.5,     # 150% more delays
                speed_multiplier=0.5      # 50% speed reduction
            )
    
    def is_active(self, current_time: datetime) -> bool:
        if not self.enabled:
            return False
        if self.start_time and current_time < self.start_time:
            return False
        if self.end_time and current_time > self.end_time:
            return False
        return True


class FactorManager:
    """Manages all simulation factors and their interactions"""
    
    def __init__(self):
        self.factors: Dict[str, SimulationFactor] = {}
        self.factor_history: List[Dict[str, Any]] = []
    
    def add_factor(self, factor: SimulationFactor):
        """Add a new factor to the simulation"""
        self.factors[factor.name] = factor
    
    def enable_factor(self, factor_name: str, start_time: Optional[datetime] = None, 
                     duration_minutes: Optional[int] = None):
        """Enable a specific factor"""
        if factor_name in self.factors:
            self.factors[factor_name].enable(start_time, duration_minutes)
    
    def disable_factor(self, factor_name: str):
        """Disable a specific factor"""
        if factor_name in self.factors:
            self.factors[factor_name].disable()
    
    def get_active_factors(self, current_time: datetime) -> List[SimulationFactor]:
        """Get all currently active factors"""
        return [factor for factor in self.factors.values() 
                if factor.is_active(current_time)]
    
    def calculate_combined_impact(self, current_time: datetime, 
                                context: Dict[str, Any]) -> FactorImpact:
        """Calculate the combined impact of all active factors"""
        active_factors = self.get_active_factors(current_time)
        
        if not active_factors:
            return FactorImpact()
        
        # Start with baseline impact
        combined = FactorImpact()
        
        # Combine impacts from all active factors
        for factor in active_factors:
            impact = factor.calculate_impact(current_time, context)
            
            # Multiply the multipliers (cumulative effect)
            combined.delay_multiplier *= impact.delay_multiplier
            combined.capacity_multiplier *= impact.capacity_multiplier
            combined.speed_multiplier *= impact.speed_multiplier
            combined.demand_multiplier *= impact.demand_multiplier
            
            # Take maximum failure probability
            combined.failure_probability = max(combined.failure_probability, 
                                             impact.failure_probability)
        
        return combined
    
    def get_factor_report(self, current_time: datetime) -> Dict[str, Any]:
        """Generate a report of current factor status"""
        active_factors = self.get_active_factors(current_time)
        
        return {
            "timestamp": current_time,
            "total_factors": len(self.factors),
            "active_factors": len(active_factors),
            "active_factor_names": [f.name for f in active_factors],
            "factors_by_category": {
                category.value: len([f for f in active_factors if f.category == category])
                for category in FactorCategory
            },
            "combined_impact": self.calculate_combined_impact(current_time, {})
        }
    
    def create_preset_scenarios(self):
        """Create common factor scenarios for testing"""
        scenarios = {
            "normal_day": [],
            "rush_hour": [RushHourDemand()],
            "monsoon_disruption": [
                WeatherConditions("heavy_rain", 0.9),
                RushHourDemand()
            ],
            "technical_failure": [
                SignalFailure("temporary"),
                PowerSupplyIssue("partial")
            ],
            "emergency_maintenance": [
                TrackMaintenance("emergency"),
                PassengerIncident("medical_emergency")
            ],
            "perfect_storm": [
                WeatherConditions("heavy_rain", 1.0),
                SignalFailure("complete"),
                RushHourDemand(),
                PowerSupplyIssue("partial")
            ]
        }
        
        for scenario_name, factor_list in scenarios.items():
            for factor in factor_list:
                factor_key = f"{scenario_name}_{factor.name}"
                self.factors[factor_key] = factor
        
        return scenarios
