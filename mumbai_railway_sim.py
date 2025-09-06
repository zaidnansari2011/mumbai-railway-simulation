"""
Main entry point for Mumbai Railway Simulation
Provides command-line interface and easy-to-use functions for running simulations.
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
from typing import List, Optional
import yaml

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.simulation.engine import MumbaiRailwaySimulation, SimulationConfig, run_quick_test
from src.network.mumbai_network import LineType
from src.factors.simulation_factors import FactorManager


def load_config(config_path: str = "config/simulation_config.yaml") -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Config file {config_path} not found. Using defaults.")
        return {}
    except Exception as e:
        print(f"Error loading config: {e}. Using defaults.")
        return {}


def create_simulation_from_config(config_dict: dict = None) -> MumbaiRailwaySimulation:
    """Create simulation instance from configuration"""
    if config_dict is None:
        config_dict = load_config()
    
    # Extract simulation config
    sim_config = config_dict.get('simulation', {})
    
    # Create simulation configuration
    config = SimulationConfig(
        start_time=datetime.now().replace(hour=6, minute=0, second=0, microsecond=0),
        duration_hours=sim_config.get('default_duration_hours', 24),
        time_step_seconds=sim_config.get('time_step_seconds', 60),
        real_time_factor=sim_config.get('real_time_factor', 1.0),
        enable_logging=sim_config.get('logging', {}).get('enabled', True),
        log_level=sim_config.get('logging', {}).get('level', 'INFO'),
        collect_metrics=sim_config.get('metrics', {}).get('enabled', True)
    )
    
    # Create simulation
    simulation = MumbaiRailwaySimulation(config)
    
    # Setup train services based on config
    service_config = config_dict.get('services', {})
    patterns = service_config.get('patterns', {})
    
    # Create services for each line
    lines_to_create = {
        'western': LineType.WESTERN,
        'central_main': LineType.CENTRAL_MAIN,
        'central_harbour': LineType.CENTRAL_HARBOUR,
        'trans_harbour': LineType.TRANS_HARBOUR
    }
    
    for line_name, line_type in lines_to_create.items():
        frequency = service_config.get('frequency', {}).get('normal_hours', 6)
        service_count = 24 // (frequency // 60) if frequency < 60 else 10  # Calculate based on frequency
        simulation.create_train_services(line_type, service_count, frequency)
    
    return simulation


def run_factor_test(factor_names: List[str], duration_hours: int = 2, 
                   start_hour: int = 7) -> dict:
    """
    Run a simulation test with specific factors enabled
    
    Args:
        factor_names: List of factor names to enable
        duration_hours: How long to run the simulation
        start_hour: What hour to start the simulation (0-23)
    
    Returns:
        Dictionary with simulation results
    """
    print(f"Running factor test with factors: {factor_names}")
    print(f"Duration: {duration_hours} hours, Starting at: {start_hour}:00")
    
    # Create simulation
    config = SimulationConfig(
        start_time=datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0),
        duration_hours=duration_hours,
        time_step_seconds=60,
        enable_logging=True,
        log_level="INFO"
    )
    
    simulation = MumbaiRailwaySimulation(config)
    
    # Create train services
    simulation.create_train_services(LineType.WESTERN, 8, 10)
    simulation.create_train_services(LineType.CENTRAL_MAIN, 8, 12)
    simulation.create_train_services(LineType.CENTRAL_HARBOUR, 4, 15)
    
    # Enable specified factors
    for factor_name in factor_names:
        if factor_name in simulation.factor_manager.factors:
            simulation.factor_manager.enable_factor(
                factor_name, 
                duration_minutes=duration_hours * 60
            )
            print(f"Enabled factor: {factor_name}")
        else:
            print(f"Warning: Factor '{factor_name}' not found")
    
    # Run simulation
    print("Starting simulation...")
    metrics = simulation.run()
    
    # Generate results
    results = {
        "test_config": {
            "factors_enabled": factor_names,
            "duration_hours": duration_hours,
            "start_hour": start_hour
        },
        "metrics": {
            "total_passengers_transported": metrics.total_passengers_transported,
            "average_delay_minutes": metrics.average_delay_minutes,
            "total_delays": metrics.total_delays,
            "on_time_performance": metrics.on_time_performance,
            "network_efficiency": metrics.network_efficiency,
            "capacity_utilization": metrics.capacity_utilization,
            "cancelled_services": metrics.cancelled_services
        },
        "final_state": simulation.get_simulation_state(),
        "factor_impact": simulation.factor_manager.get_factor_report(simulation.current_time)
    }
    
    return results


def compare_scenarios(scenarios: dict, duration_hours: int = 2) -> dict:
    """
    Compare multiple scenarios with different factor combinations
    
    Args:
        scenarios: Dict of scenario_name -> list_of_factors
        duration_hours: Duration for each test
    
    Returns:
        Comparison results
    """
    print(f"Comparing {len(scenarios)} scenarios...")
    
    results = {}
    
    for scenario_name, factors in scenarios.items():
        print(f"\nRunning scenario: {scenario_name}")
        scenario_results = run_factor_test(factors, duration_hours)
        results[scenario_name] = scenario_results
        
        # Print quick summary
        metrics = scenario_results["metrics"]
        print(f"  - Passengers transported: {metrics['total_passengers_transported']}")
        print(f"  - Average delay: {metrics['average_delay_minutes']:.1f} minutes")
        print(f"  - On-time performance: {metrics['on_time_performance']:.1f}%")
        print(f"  - Network efficiency: {metrics['network_efficiency']:.1f}%")
    
    # Generate comparison summary
    summary = {
        "scenario_comparison": {},
        "best_performance": {},
        "worst_performance": {}
    }
    
    # Compare key metrics
    for metric in ["average_delay_minutes", "on_time_performance", "network_efficiency", 
                   "total_passengers_transported"]:
        metric_values = {name: result["metrics"][metric] for name, result in results.items()}
        
        if metric == "average_delay_minutes":
            best = min(metric_values.items(), key=lambda x: x[1])
            worst = max(metric_values.items(), key=lambda x: x[1])
        else:
            best = max(metric_values.items(), key=lambda x: x[1])
            worst = min(metric_values.items(), key=lambda x: x[1])
        
        summary["scenario_comparison"][metric] = metric_values
        summary["best_performance"][metric] = best
        summary["worst_performance"][metric] = worst
    
    results["summary"] = summary
    return results


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Mumbai Railway Network Simulation")
    
    parser.add_argument("--mode", choices=["quick", "factor-test", "compare", "full"], 
                       default="quick", help="Simulation mode")
    parser.add_argument("--factors", nargs="*", default=[], 
                       help="Factors to enable (for factor-test mode)")
    parser.add_argument("--duration", type=int, default=2, 
                       help="Simulation duration in hours")
    parser.add_argument("--start-hour", type=int, default=7, 
                       help="Start hour (0-23)")
    parser.add_argument("--config", default="config/simulation_config.yaml", 
                       help="Configuration file path")
    parser.add_argument("--export", help="Export results to file")
    
    args = parser.parse_args()
    
    if args.mode == "quick":
        print("Running quick test simulation...")
        sim, metrics = run_quick_test(args.factors, args.duration)
        
        print("\n=== QUICK TEST RESULTS ===")
        print(f"Total passengers transported: {metrics.total_passengers_transported}")
        print(f"Average delay: {metrics.average_delay_minutes:.1f} minutes")
        print(f"On-time performance: {metrics.on_time_performance:.1f}%")
        print(f"Network efficiency: {metrics.network_efficiency:.1f}%")
        
        if args.export:
            sim.export_results(args.export)
    
    elif args.mode == "factor-test":
        if not args.factors:
            print("No factors specified. Available factors:")
            # Show available factors
            sim = create_simulation_from_config()
            for factor_name in sim.factor_manager.factors.keys():
                print(f"  - {factor_name}")
            return
        
        results = run_factor_test(args.factors, args.duration, args.start_hour)
        
        print("\n=== FACTOR TEST RESULTS ===")
        metrics = results["metrics"]
        for key, value in metrics.items():
            print(f"{key}: {value}")
        
        if args.export:
            import json
            with open(args.export, 'w') as f:
                json.dump(results, f, indent=2, default=str)
    
    elif args.mode == "compare":
        # Define some common scenarios to compare
        scenarios = {
            "normal_operations": [],
            "rush_hour_only": ["rush_hour_only_Rush Hour Demand"],
            "weather_disruption": ["normal_day_Weather: heavy_rain"],
            "technical_issues": ["normal_day_Signal Failure: temporary"],
            "perfect_storm": [
                "perfect_storm_Weather: heavy_rain",
                "perfect_storm_Signal Failure: complete", 
                "perfect_storm_Rush Hour Demand"
            ]
        }
        
        results = compare_scenarios(scenarios, args.duration)
        
        print("\n=== SCENARIO COMPARISON RESULTS ===")
        summary = results["summary"]
        
        for metric, comparison in summary["scenario_comparison"].items():
            print(f"\n{metric}:")
            for scenario, value in comparison.items():
                print(f"  {scenario}: {value}")
        
        if args.export:
            import json
            with open(args.export, 'w') as f:
                json.dump(results, f, indent=2, default=str)
    
    elif args.mode == "full":
        print("Running full simulation...")
        simulation = create_simulation_from_config()
        
        # Enable some default factors for realism
        simulation.factor_manager.enable_factor("rush_hour_only_Rush Hour Demand")
        
        metrics = simulation.run(args.duration)
        
        print("\n=== FULL SIMULATION RESULTS ===")
        state = simulation.get_simulation_state()
        
        print(f"Simulation completed!")
        print(f"Total passengers transported: {metrics.total_passengers_transported}")
        print(f"Average delay: {metrics.average_delay_minutes:.1f} minutes")
        print(f"Total delays: {metrics.total_delays}")
        print(f"On-time performance: {metrics.on_time_performance:.1f}%")
        print(f"Network efficiency: {metrics.network_efficiency:.1f}%")
        print(f"Capacity utilization: {metrics.capacity_utilization:.1f}%")
        
        if args.export:
            simulation.export_results(args.export)


if __name__ == "__main__":
    main()
