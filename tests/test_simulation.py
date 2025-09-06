"""
Test suite for Mumbai Railway Simulation
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.network.mumbai_network import MumbaiRailwayNetwork, LineType, Station, StationType
from src.simulation.trains import Train, TrainType, Direction, TrainConfiguration
from src.factors.simulation_factors import RushHourDemand, WeatherConditions, FactorManager


class TestMumbaiNetwork:
    """Test cases for Mumbai Railway Network"""
    
    def test_network_initialization(self):
        """Test that the network initializes correctly"""
        network = MumbaiRailwayNetwork()
        
        assert len(network.stations) > 0
        assert len(network.tracks) > 0
        assert network.network_graph.number_of_nodes() > 0
        assert network.network_graph.number_of_edges() > 0
    
    def test_station_creation(self):
        """Test station creation and properties"""
        station = Station(
            id="TEST",
            name="Test Station",
            line=LineType.WESTERN,
            station_type=StationType.REGULAR,
            coordinates=(19.0, 72.8),
            platforms=4
        )
        
        assert station.id == "TEST"
        assert station.name == "Test Station"
        assert station.line == LineType.WESTERN
        assert station.platforms == 4
        assert not station.interchange
    
    def test_route_finding(self):
        """Test route finding between stations"""
        network = MumbaiRailwayNetwork()
        
        # Test route from CST to DAD (should exist)
        route = network.get_route("CST", "DAD")
        assert route is not None
        assert "CST" in route
        assert "DAD" in route
    
    def test_line_stations(self):
        """Test getting stations by line"""
        network = MumbaiRailwayNetwork()
        
        western_stations = network.get_stations_by_line(LineType.WESTERN)
        assert len(western_stations) > 0
        
        # Check that all stations are on Western line or are interchanges
        for station in western_stations:
            assert (station.line == LineType.WESTERN or 
                   LineType.WESTERN in station.interchange_lines)


class TestTrains:
    """Test cases for train operations"""
    
    def test_train_creation(self):
        """Test train creation and configuration"""
        config = TrainConfiguration(car_count=12, capacity_per_car=350)
        train = Train(
            id="TEST001",
            train_type=TrainType.LOCAL,
            line="western",
            direction=Direction.UP,
            config=config
        )
        
        assert train.id == "TEST001"
        assert train.total_capacity == 4200  # 12 * 350
        assert train.occupancy_ratio == 0.0
        assert not train.is_overcrowded
    
    def test_passenger_boarding(self):
        """Test passenger boarding and alighting"""
        config = TrainConfiguration(car_count=4, capacity_per_car=100)
        train = Train(
            id="TEST002",
            train_type=TrainType.LOCAL,
            line="western",
            direction=Direction.UP,
            config=config
        )
        
        # Test boarding
        boarded = train.board_passengers(200)
        assert boarded == 200
        assert train.passenger_count == 200
        assert train.occupancy_ratio == 0.5
        
        # Test alighting
        alighted = train.alight_passengers(50)
        assert alighted == 50
        assert train.passenger_count == 150
        
        # Test overcrowding (allow up to 130% capacity)
        boarded = train.board_passengers(400)
        assert boarded == 370  # 520 (130% of 400) - 150 = 370
        assert train.is_overcrowded
    
    def test_train_delay(self):
        """Test delay tracking"""
        train = Train(
            id="TEST003",
            train_type=TrainType.LOCAL,
            line="western",
            direction=Direction.UP,
            config=TrainConfiguration()
        )
        
        assert train.delay_minutes == 0.0
        
        train.add_delay(5.0)
        assert train.delay_minutes == 5.0
        assert train.status.value == "delayed"


class TestFactors:
    """Test cases for simulation factors"""
    
    def test_rush_hour_factor(self):
        """Test rush hour demand factor"""
        factor = RushHourDemand(peak_multiplier=2.0)
        
        # Test during rush hour (8 AM)
        rush_time = datetime.now().replace(hour=8, minute=0)
        factor.enable()
        
        impact = factor.calculate_impact(rush_time, {})
        assert impact.demand_multiplier == 2.0
        assert impact.delay_multiplier > 1.0
        
        # Test during non-rush hour (2 PM)
        non_rush_time = datetime.now().replace(hour=14, minute=0)
        impact = factor.calculate_impact(non_rush_time, {})
        assert impact.demand_multiplier == 1.0
    
    def test_weather_factor(self):
        """Test weather conditions factor"""
        factor = WeatherConditions("heavy_rain", intensity=0.8)
        factor.enable()
        
        current_time = datetime.now()
        impact = factor.calculate_impact(current_time, {})
        
        assert impact.speed_multiplier < 1.0  # Speed should be reduced
        assert impact.delay_multiplier > 1.0  # Delays should increase
        assert impact.failure_probability > 0.0  # Some failure probability
    
    def test_factor_manager(self):
        """Test factor management"""
        manager = FactorManager()
        
        # Add factors
        rush_hour = RushHourDemand()
        weather = WeatherConditions("heavy_rain", 0.6)
        
        manager.add_factor(rush_hour)
        manager.add_factor(weather)
        
        assert len(manager.factors) >= 2
        
        # Enable factors
        manager.enable_factor(rush_hour.name)
        manager.enable_factor(weather.name)
        
        # Test combined impact
        current_time = datetime.now().replace(hour=8, minute=0)  # Rush hour
        combined_impact = manager.calculate_combined_impact(current_time, {})
        
        # Combined effects should be multiplicative
        assert combined_impact.delay_multiplier > 1.0
        assert combined_impact.speed_multiplier < 1.0


class TestSimulationIntegration:
    """Integration tests for the full simulation"""
    
    def test_simulation_setup(self):
        """Test that simulation can be set up correctly"""
        from src.simulation.engine import SimulationConfig, MumbaiRailwaySimulation
        
        config = SimulationConfig(
            start_time=datetime.now(),
            duration_hours=1,
            time_step_seconds=60
        )
        
        sim = MumbaiRailwaySimulation(config)
        
        assert sim.network is not None
        assert sim.scheduler is not None
        assert sim.factor_manager is not None
        assert len(sim.passengers_waiting) > 0
    
    def test_service_creation(self):
        """Test train service creation"""
        from src.simulation.engine import SimulationConfig, MumbaiRailwaySimulation
        
        config = SimulationConfig(
            start_time=datetime.now(),
            duration_hours=1
        )
        
        sim = MumbaiRailwaySimulation(config)
        sim.create_train_services(LineType.WESTERN, 2, 15)
        
        assert len(sim.active_services) >= 2
        
        # Check that services have proper routes
        for service in sim.active_services:
            assert len(service.route) > 1
            assert len(service.stops) > 1


# Performance benchmarks
class TestPerformance:
    """Performance tests to ensure simulation runs efficiently"""
    
    def test_network_performance(self):
        """Test network operations performance"""
        import time
        
        start_time = time.time()
        network = MumbaiRailwayNetwork()
        creation_time = time.time() - start_time
        
        # Network creation should be fast
        assert creation_time < 1.0  # Less than 1 second
        
        # Route finding should be fast
        start_time = time.time()
        for _ in range(100):
            route = network.get_route("CST", "VR")
        route_time = time.time() - start_time
        
        assert route_time < 1.0  # 100 route calculations in less than 1 second
    
    def test_simulation_step_performance(self):
        """Test simulation step performance"""
        from src.simulation.engine import SimulationConfig, MumbaiRailwaySimulation
        import time
        
        config = SimulationConfig(
            start_time=datetime.now(),
            duration_hours=1,
            enable_logging=False  # Disable logging for performance test
        )
        
        sim = MumbaiRailwaySimulation(config)
        sim.create_train_services(LineType.WESTERN, 5, 15)
        
        # Measure time for 60 simulation steps (1 hour of simulation)
        start_time = time.time()
        current_time = config.start_time
        
        for _ in range(60):
            sim.run_simulation_step(current_time)
            current_time += timedelta(minutes=1)
        
        step_time = time.time() - start_time
        
        # 60 simulation steps should complete in reasonable time
        assert step_time < 10.0  # Less than 10 seconds


if __name__ == "__main__":
    # Run specific test if called directly
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "network":
            pytest.main(["-v", "test_simulation.py::TestMumbaiNetwork"])
        elif test_name == "trains":
            pytest.main(["-v", "test_simulation.py::TestTrains"])
        elif test_name == "factors":
            pytest.main(["-v", "test_simulation.py::TestFactors"])
        elif test_name == "integration":
            pytest.main(["-v", "test_simulation.py::TestSimulationIntegration"])
        elif test_name == "performance":
            pytest.main(["-v", "test_simulation.py::TestPerformance"])
        else:
            print("Available tests: network, trains, factors, integration, performance")
    else:
        # Run all tests
        pytest.main(["-v", "test_simulation.py"])
