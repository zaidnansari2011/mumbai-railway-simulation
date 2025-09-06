# Mumbai Suburban Railway Simulation

An advanced, modular railway simulation system designed to accurately model the complexities of the Mumbai Suburban Railway network. This simulation enables incremental testing of various factors that affect railway operations and serves as a platform for developing and testing traffic management strategies.

## 🎯 Project Overview

This simulation creates a realistic digital twin of Mumbai's railway network, allowing you to:

- **Test individual factors** - Add and test factors one by one to understand their impact
- **Model realistic operations** - Accurate representation of Mumbai's railway topology and operations
- **Analyze performance** - Comprehensive metrics and reporting system
- **Experiment safely** - Test scenarios without affecting real operations
- **Build understanding** - Incremental complexity to understand system behavior

## 🏗️ Architecture

The simulation is built with modularity in mind, consisting of several key components:

### Core Components

1. **Network Topology** (`src/network/`) - Accurate Mumbai railway network structure
2. **Train Operations** (`src/simulation/`) - Train movement, scheduling, and passenger handling
3. **Factor System** (`src/factors/`) - Modular factors that can be enabled/disabled
4. **Simulation Engine** (`src/simulation/engine.py`) - Main orchestration and time management
5. **Configuration** (`config/`) - YAML-based configuration system

### Project Structure

```
aitrain/
├── src/
│   ├── network/
│   │   └── mumbai_network.py       # Railway network topology
│   ├── simulation/
│   │   ├── trains.py               # Train and service models
│   │   └── engine.py               # Main simulation engine
│   ├── factors/
│   │   └── simulation_factors.py   # Modular factor system
│   └── rl_environment/             # Future RL integration
├── config/
│   └── simulation_config.yaml      # Configuration settings
├── examples/
│   └── examples.py                 # Usage examples and tutorials
├── tests/
│   └── test_simulation.py          # Comprehensive test suite
├── data/                           # Data storage directory
├── mumbai_railway_sim.py           # Main CLI entry point
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🚀 Quick Start

### Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run a quick test**:
   ```bash
   python mumbai_railway_sim.py --mode quick --duration 1
   ```

### Basic Usage

#### 1. Quick Test (No factors)
```bash
python mumbai_railway_sim.py --mode quick --duration 2
```

#### 2. Test Specific Factors
```bash
python mumbai_railway_sim.py --mode factor-test --factors "rush_hour_only_Rush Hour Demand" --duration 2
```

#### 3. Compare Multiple Scenarios
```bash
python mumbai_railway_sim.py --mode compare --duration 1
```

#### 4. Full Simulation
```bash
python mumbai_railway_sim.py --mode full --duration 24 --export results.json
```

## 🧪 Testing Framework

The simulation is designed for incremental testing. You can enable factors one by one to understand their individual and combined impacts.

### Available Factors

| Factor Category | Factor Name | Description |
|----------------|-------------|-------------|
| **Passenger Demand** | Rush Hour Demand | Increased passenger load during peak hours |
| **Weather** | Heavy Rain | Reduced speeds and increased delays |
| **Infrastructure** | Track Maintenance | Scheduled or emergency track work |
| **Technical** | Signal Failure | Signal system malfunctions |
| **Technical** | Power Supply Issue | Electrical supply disruptions |
| **Operational** | Passenger Incident | Medical emergencies, unruly passengers |

### Example Testing Scenarios

#### Scenario 1: Understanding Rush Hour Impact
```python
from examples.examples import example_2_rush_hour_impact
example_2_rush_hour_impact()
```

#### Scenario 2: Weather Disruption Analysis
```python
from examples.examples import example_3_weather_disruption
example_3_weather_disruption()
```

#### Scenario 3: Cascading Failure Testing
```python
from examples.examples import example_4_cascading_failures
example_4_cascading_failures()
```

## 📊 Metrics and Analysis

The simulation tracks comprehensive metrics:

- **Operational Metrics**: On-time performance, average delays, capacity utilization
- **Passenger Metrics**: Total passengers transported, waiting times, satisfaction
- **Network Metrics**: Network efficiency, bottleneck identification
- **Factor Impact**: Individual and combined factor effects

### Sample Output
```
=== SIMULATION RESULTS ===
Total passengers transported: 45,230
Average delay: 3.2 minutes
On-time performance: 87.3%
Network efficiency: 91.5%
Capacity utilization: 78.2%
Active factors: Rush Hour Demand, Weather: heavy_rain
```

## 🎮 Interactive Examples

Run the examples to see the simulation in action:

```bash
# Run all examples
python examples/examples.py all

# Run specific example
python examples/examples.py 1    # Basic simulation
python examples/examples.py 2    # Rush hour impact
python examples/examples.py 3    # Weather disruption
python examples/examples.py 4    # Cascading failures
python examples/examples.py 5    # Maintenance planning
python examples/examples.py 6    # Sensitivity analysis
```

## 🧪 Advanced Usage

### Creating Custom Factors

```python
from src.factors.simulation_factors import SimulationFactor, FactorCategory, FactorSeverity

class CustomFactor(SimulationFactor):
    def __init__(self):
        super().__init__("My Custom Factor", FactorCategory.OPERATIONAL, FactorSeverity.MEDIUM)
    
    def calculate_impact(self, current_time, context):
        # Your custom logic here
        return FactorImpact(delay_multiplier=1.2)
    
    def is_active(self, current_time):
        return self.enabled
```

## 🎯 Use Cases

### 1. Factor Impact Analysis
Test how individual factors affect network performance:
- Rush hour demand patterns
- Weather conditions (rain, fog, heat)
- Infrastructure maintenance
- Technical failures

### 2. Scenario Planning
Simulate realistic operational scenarios:
- Normal operations baseline
- Monsoon season disruptions
- Festival/event crowd management
- Emergency response procedures

### 3. Performance Optimization
Identify bottlenecks and optimization opportunities:
- Service frequency optimization
- Route planning
- Resource allocation
- Capacity management

### 4. Training and Education
Understand railway operations complexity:
- System interdependencies
- Cascading failure patterns
- Performance trade-offs
- Operational decision impact

## 📈 Performance Metrics

The simulation tracks key performance indicators:

| Metric | Description | Target |
|--------|-------------|---------|
| On-time Performance | % trains within 5 min of schedule | >85% |
| Average Delay | Mean delay across all services | <5 min |
| Network Efficiency | Overall system performance | >90% |
| Capacity Utilization | % of train capacity used | 75% |
| Passenger Satisfaction | Derived from delays and crowding | >80% |

## 🏁 Getting Started Checklist

- [x] ✅ Install dependencies (`pip install -r requirements.txt`)
- [ ] ✅ Run quick test (`python mumbai_railway_sim.py --mode quick`)
- [ ] ✅ Try examples (`python examples/examples.py 1`)
- [ ] ✅ Test a single factor (`python mumbai_railway_sim.py --mode factor-test --factors "rush_hour_only_Rush Hour Demand"`)
- [ ] ✅ Compare scenarios (`python mumbai_railway_sim.py --mode compare`)
- [ ] ✅ Analyze results and understand patterns
- [ ] ✅ Create your own test scenarios
- [ ] ✅ Extend with custom factors

## 📞 Support

For questions or issues:
1. Check the examples in `examples/examples.py`
2. Review the test cases in `tests/test_simulation.py`
3. Consult the configuration in `config/simulation_config.yaml`
4. Review the code documentation in each module

---

**Ready to start testing?** Run your first simulation:
```bash
python mumbai_railway_sim.py --mode quick --duration 1
```
