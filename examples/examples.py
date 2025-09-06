"""
Example Usage Scripts for Mumbai Railway Simulation
Demonstrates how to use the simulation for different testing scenarios.
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.simulation.engine import MumbaiRailwaySimulation, SimulationConfig
from src.network.mumbai_network import LineType
from src.factors.simulation_factors import (
    RushHourDemand, WeatherConditions, TrackMaintenance, 
    SignalFailure, PassengerIncident, PowerSupplyIssue
)


def example_1_basic_simulation():
    """
    Example 1: Basic simulation without any disruption factors
    This shows normal railway operations
    """
    print("=== Example 1: Basic Simulation ===")
    
    # Create configuration
    config = SimulationConfig(
        start_time=datetime.now().replace(hour=6, minute=0, second=0, microsecond=0),
        duration_hours=4,
        time_step_seconds=60,
        enable_logging=True,
        log_level="INFO"
    )
    
    # Create simulation
    sim = MumbaiRailwaySimulation(config)
    
    # Add train services
    sim.create_train_services(LineType.WESTERN, 8, 10)      # 8 services, every 10 minutes
    sim.create_train_services(LineType.CENTRAL_MAIN, 6, 12) # 6 services, every 12 minutes
    
    # Run simulation
    print("Running basic simulation for 4 hours...")
    metrics = sim.run()
    
    # Print results
    print(f"Results:")
    print(f"  - Total passengers transported: {metrics.total_passengers_transported}")
    print(f"  - Average delay: {metrics.average_delay_minutes:.1f} minutes")
    print(f"  - On-time performance: {metrics.on_time_performance:.1f}%")
    print(f"  - Network efficiency: {metrics.network_efficiency:.1f}%")
    print(f"  - Capacity utilization: {metrics.capacity_utilization:.1f}%")
    
    return sim, metrics


def example_2_rush_hour_impact():
    """
    Example 2: Testing impact of rush hour demand
    Compares normal operations vs rush hour conditions
    """
    print("\n=== Example 2: Rush Hour Impact ===")
    
    # Test 1: Normal operations
    print("Test 1: Normal operations")
    config = SimulationConfig(
        start_time=datetime.now().replace(hour=11, minute=0, second=0, microsecond=0),  # 11 AM
        duration_hours=2,
        time_step_seconds=60
    )
    
    sim_normal = MumbaiRailwaySimulation(config)
    sim_normal.create_train_services(LineType.WESTERN, 6, 10)
    metrics_normal = sim_normal.run()
    
    # Test 2: Rush hour operations
    print("\nTest 2: Rush hour operations")
    config_rush = SimulationConfig(
        start_time=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),  # 8 AM
        duration_hours=2,
        time_step_seconds=60
    )
    
    sim_rush = MumbaiRailwaySimulation(config_rush)
    sim_rush.create_train_services(LineType.WESTERN, 6, 10)
    
    # Enable rush hour factor
    rush_factor = RushHourDemand(peak_multiplier=2.5)
    sim_rush.factor_manager.add_factor(rush_factor)
    sim_rush.factor_manager.enable_factor(rush_factor.name)
    
    metrics_rush = sim_rush.run()
    
    # Compare results
    print(f"\nComparison:")
    print(f"Metric                    | Normal    | Rush Hour | Difference")
    print(f"--------------------------|-----------|-----------|----------")
    print(f"Passengers transported    | {metrics_normal.total_passengers_transported:8} | {metrics_rush.total_passengers_transported:8} | {metrics_rush.total_passengers_transported - metrics_normal.total_passengers_transported:+8}")
    print(f"Average delay (min)       | {metrics_normal.average_delay_minutes:8.1f} | {metrics_rush.average_delay_minutes:8.1f} | {metrics_rush.average_delay_minutes - metrics_normal.average_delay_minutes:+8.1f}")
    print(f"On-time performance (%)   | {metrics_normal.on_time_performance:8.1f} | {metrics_rush.on_time_performance:8.1f} | {metrics_rush.on_time_performance - metrics_normal.on_time_performance:+8.1f}")
    print(f"Network efficiency (%)    | {metrics_normal.network_efficiency:8.1f} | {metrics_rush.network_efficiency:8.1f} | {metrics_rush.network_efficiency - metrics_normal.network_efficiency:+8.1f}")


def example_3_weather_disruption():
    """
    Example 3: Testing weather disruption impact
    Tests heavy rain impact on railway operations
    """
    print("\n=== Example 3: Weather Disruption ===")
    
    config = SimulationConfig(
        start_time=datetime.now().replace(hour=7, minute=0, second=0, microsecond=0),
        duration_hours=3,
        time_step_seconds=60
    )
    
    sim = MumbaiRailwaySimulation(config)
    sim.create_train_services(LineType.WESTERN, 8, 8)
    sim.create_train_services(LineType.CENTRAL_MAIN, 6, 10)
    
    # Add weather disruption after 1 hour
    weather_factor = WeatherConditions("heavy_rain", intensity=0.9)
    sim.factor_manager.add_factor(weather_factor)
    
    # Enable weather factor to start after 1 hour and last for 1 hour
    start_time = config.start_time + timedelta(hours=1)
    sim.factor_manager.enable_factor(
        weather_factor.name, 
        start_time=start_time, 
        duration_minutes=60
    )
    
    print("Running simulation with weather disruption starting at 8 AM...")
    metrics = sim.run()
    
    print(f"Results with weather disruption:")
    print(f"  - Total delays: {metrics.total_delays}")
    print(f"  - Average delay: {metrics.average_delay_minutes:.1f} minutes")
    print(f"  - On-time performance: {metrics.on_time_performance:.1f}%")
    
    # Show factor impact report
    factor_report = sim.factor_manager.get_factor_report(sim.current_time)
    print(f"  - Active factors during simulation: {factor_report['active_factor_names']}")


def example_4_cascading_failures():
    """
    Example 4: Testing cascading failures
    Multiple factors occurring simultaneously
    """
    print("\n=== Example 4: Cascading Failures ===")
    
    config = SimulationConfig(
        start_time=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),
        duration_hours=2,
        time_step_seconds=60
    )
    
    sim = MumbaiRailwaySimulation(config)
    sim.create_train_services(LineType.WESTERN, 10, 6)
    sim.create_train_services(LineType.CENTRAL_MAIN, 8, 8)
    
    # Create multiple factors
    rush_hour = RushHourDemand(peak_multiplier=2.5)
    signal_failure = SignalFailure("temporary")
    power_issue = PowerSupplyIssue("partial")
    passenger_incident = PassengerIncident("medical_emergency")
    
    # Add all factors
    for factor in [rush_hour, signal_failure, power_issue, passenger_incident]:
        sim.factor_manager.add_factor(factor)
    
    # Enable factors at different times
    # Rush hour: entire duration
    sim.factor_manager.enable_factor(rush_hour.name)
    
    # Signal failure: starts 30 minutes in, lasts 45 minutes
    sim.factor_manager.enable_factor(
        signal_failure.name,
        start_time=config.start_time + timedelta(minutes=30),
        duration_minutes=45
    )
    
    # Power issue: starts 60 minutes in, lasts 30 minutes
    sim.factor_manager.enable_factor(
        power_issue.name,
        start_time=config.start_time + timedelta(minutes=60),
        duration_minutes=30
    )
    
    # Passenger incident: starts 90 minutes in, lasts 15 minutes
    sim.factor_manager.enable_factor(
        passenger_incident.name,
        start_time=config.start_time + timedelta(minutes=90),
        duration_minutes=15
    )
    
    print("Running simulation with cascading failures...")
    print("Timeline:")
    print("  0:00 - Rush hour begins")
    print("  0:30 - Signal failure occurs")
    print("  1:00 - Power supply issue begins")
    print("  1:30 - Passenger incident occurs")
    
    metrics = sim.run()
    
    print(f"\nResults with cascading failures:")
    print(f"  - Total passengers transported: {metrics.total_passengers_transported}")
    print(f"  - Total delays: {metrics.total_delays}")
    print(f"  - Average delay: {metrics.average_delay_minutes:.1f} minutes")
    print(f"  - On-time performance: {metrics.on_time_performance:.1f}%")
    print(f"  - Network efficiency: {metrics.network_efficiency:.1f}%")
    print(f"  - Cancelled services: {metrics.cancelled_services}")


def example_5_maintenance_planning():
    """
    Example 5: Testing maintenance impact
    Compares scheduled vs emergency maintenance
    """
    print("\n=== Example 5: Maintenance Planning ===")
    
    # Test 1: Scheduled maintenance during off-peak hours
    print("Test 1: Scheduled maintenance (off-peak)")
    config1 = SimulationConfig(
        start_time=datetime.now().replace(hour=13, minute=0, second=0, microsecond=0),  # 1 PM
        duration_hours=2,
        time_step_seconds=60
    )
    
    sim1 = MumbaiRailwaySimulation(config1)
    sim1.create_train_services(LineType.WESTERN, 6, 15)
    
    scheduled_maintenance = TrackMaintenance("scheduled")
    sim1.factor_manager.add_factor(scheduled_maintenance)
    sim1.factor_manager.enable_factor(scheduled_maintenance.name, duration_minutes=90)
    
    metrics1 = sim1.run()
    
    # Test 2: Emergency maintenance during peak hours
    print("\nTest 2: Emergency maintenance (peak hour)")
    config2 = SimulationConfig(
        start_time=datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),  # 8 AM
        duration_hours=2,
        time_step_seconds=60
    )
    
    sim2 = MumbaiRailwaySimulation(config2)
    sim2.create_train_services(LineType.WESTERN, 10, 8)
    
    emergency_maintenance = TrackMaintenance("emergency")
    rush_hour = RushHourDemand()
    
    sim2.factor_manager.add_factor(emergency_maintenance)
    sim2.factor_manager.add_factor(rush_hour)
    
    sim2.factor_manager.enable_factor(emergency_maintenance.name, duration_minutes=60)
    sim2.factor_manager.enable_factor(rush_hour.name)
    
    metrics2 = sim2.run()
    
    # Compare results
    print(f"\nMaintenance Impact Comparison:")
    print(f"Scenario                  | Scheduled | Emergency | Impact")
    print(f"--------------------------|-----------|-----------|----------")
    print(f"Average delay (min)       | {metrics1.average_delay_minutes:8.1f} | {metrics2.average_delay_minutes:8.1f} | {(metrics2.average_delay_minutes / metrics1.average_delay_minutes if metrics1.average_delay_minutes > 0 else 0):6.1f}x")
    print(f"On-time performance (%)   | {metrics1.on_time_performance:8.1f} | {metrics2.on_time_performance:8.1f} | {metrics2.on_time_performance - metrics1.on_time_performance:+8.1f}")
    print(f"Network efficiency (%)    | {metrics1.network_efficiency:8.1f} | {metrics2.network_efficiency:8.1f} | {metrics2.network_efficiency - metrics1.network_efficiency:+8.1f}")


def example_6_factor_sensitivity_analysis():
    """
    Example 6: Factor sensitivity analysis
    Tests how different factor intensities affect performance
    """
    print("\n=== Example 6: Factor Sensitivity Analysis ===")
    
    # Test weather conditions at different intensities
    intensities = [0.2, 0.4, 0.6, 0.8, 1.0]
    results = []
    
    print("Testing weather impact at different intensities...")
    
    for intensity in intensities:
        config = SimulationConfig(
            start_time=datetime.now().replace(hour=7, minute=0, second=0, microsecond=0),
            duration_hours=1,
            time_step_seconds=60,
            enable_logging=False  # Disable logging for cleaner output
        )
        
        sim = MumbaiRailwaySimulation(config)
        sim.create_train_services(LineType.WESTERN, 6, 10)
        
        weather = WeatherConditions("heavy_rain", intensity=intensity)
        sim.factor_manager.add_factor(weather)
        sim.factor_manager.enable_factor(weather.name)
        
        metrics = sim.run()
        
        results.append({
            'intensity': intensity,
            'delay': metrics.average_delay_minutes,
            'efficiency': metrics.network_efficiency,
            'on_time': metrics.on_time_performance
        })
        
        print(f"  Intensity {intensity:.1f}: Delay {metrics.average_delay_minutes:.1f}min, "
              f"Efficiency {metrics.network_efficiency:.1f}%, "
              f"On-time {metrics.on_time_performance:.1f}%")
    
    print(f"\nSensitivity Analysis Results:")
    print(f"Intensity | Avg Delay | Network Eff | On-Time Perf")
    print(f"----------|-----------|-------------|-------------")
    for result in results:
        print(f"{result['intensity']:8.1f} | {result['delay']:8.1f} | {result['efficiency']:10.1f} | {result['on_time']:11.1f}")


def run_all_examples():
    """Run all examples in sequence"""
    print("Mumbai Railway Simulation - Example Usage")
    print("=========================================")
    
    try:
        example_1_basic_simulation()
        example_2_rush_hour_impact()
        example_3_weather_disruption()
        example_4_cascading_failures()
        example_5_maintenance_planning()
        example_6_factor_sensitivity_analysis()
        
        print("\n=== All Examples Completed Successfully ===")
        print("You can now:")
        print("1. Modify factor parameters to test different scenarios")
        print("2. Add new factors by extending the SimulationFactor class")
        print("3. Create custom test scenarios using the factor combinations")
        print("4. Export results for detailed analysis")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_number = sys.argv[1]
        
        examples = {
            "1": example_1_basic_simulation,
            "2": example_2_rush_hour_impact,
            "3": example_3_weather_disruption,
            "4": example_4_cascading_failures,
            "5": example_5_maintenance_planning,
            "6": example_6_factor_sensitivity_analysis,
            "all": run_all_examples
        }
        
        if example_number in examples:
            examples[example_number]()
        else:
            print("Available examples:")
            print("  1 - Basic simulation")
            print("  2 - Rush hour impact")
            print("  3 - Weather disruption")
            print("  4 - Cascading failures")
            print("  5 - Maintenance planning")
            print("  6 - Factor sensitivity analysis")
            print("  all - Run all examples")
            print(f"\nUsage: python examples.py [1-6|all]")
    else:
        run_all_examples()
