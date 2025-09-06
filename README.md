# 🚂 Mumbai Railway Live Simulation

A comprehensive real-time simulation of Mumbai's Suburban Railway network with live train tracking, delay analysis, and interactive visualization.

## 🌟 Features

### 🗺️ Interactive Map Visualization
- Real-time train movement on Mumbai railway map
- 4 major railway lines: Western, Central Main, Central Harbour, Trans-Harbour
- 26+ accurate station locations
- Color-coded line representation

### 🚂 Live Train Tracking
- Individual train cards with detailed information
- Linear progress bars showing exact position between stations
- Real-time speed, distance, and ETA calculations
- Customizable update speeds (0.5s to 5s intervals)
- Pause/resume functionality for detailed analysis

### 📊 Comprehensive Data Display
- Live train schedule table with 9 data columns
- Train ID, line, current/next stations, ETA, passengers, delays
- Real-time status updates (On Time, Delayed, Critical)
- Performance metrics and efficiency tracking

### 🔍 Delay Analysis & Root Cause Detection
- Intelligent delay classification system
- Root cause analysis (Weather, Rush Hour, Technical, Cascade)
- Impact assessment with severity levels
- Recommended actions for each delay scenario
- Active disruption monitoring

### ⚡ Interactive Controls
- Start/Stop simulation
- Add Rush Hour effects
- Add Weather disruptions
- Speed control for tracking updates
- Auto-follow train movements

## 🚀 Quick Start

### Option 1: Direct HTML Demo (Recommended)
1. Clone the repository
2. Open `mumbai_railway_live_demo.html` in your browser
3. Click "Start Simulation" to see live train movements

### Option 2: Python Simulation
```bash
# Install dependencies
pip install -r requirements.txt

# Run quick demo
python mumbai_railway_sim.py --mode quick --duration 1

# Run with specific factors
python mumbai_railway_sim.py --mode factor-test --factors "rush_hour_only_Rush Hour Demand" --duration 2

# Compare scenarios
python mumbai_railway_sim.py --mode compare --duration 1
```

### Option 3: Live Server Demo
```bash
# Start HTTP server
python -m http.server 8000

# Access demo at
http://localhost:8000/mumbai_railway_live_demo.html
```

## 📁 Project Structure

```
aitrain/
├── mumbai_railway_live_demo.html    # Main live demo (recommended)
├── mumbai_railway_sim.py            # CLI simulation tool
├── requirements.txt                 # Python dependencies
├── src/
│   ├── network/
│   │   └── mumbai_network.py        # Railway network topology
│   ├── simulation/
│   │   ├── engine.py                # Core simulation engine
│   │   └── trains.py                # Train models
│   └── factors/
│       └── simulation_factors.py    # Disruption factors
├── config/
│   └── simulation_config.yaml       # Configuration settings
├── examples/
│   └── examples.py                  # Usage examples
├── tests/
│   └── test_simulation.py           # Test suite
└── visualization/
    ├── dashboard.py                 # Dashboard components
    ├── live_simulation.py           # Live simulation logic
    └── network_map.py               # Map visualization
```

## 🎯 Use Cases

### For Railway Operations
- **Real-time Monitoring**: Track train positions and delays
- **Performance Analysis**: Identify bottlenecks and efficiency issues
- **Incident Management**: Understand delay causes and impacts
- **Capacity Planning**: Analyze passenger loads and demand patterns

### For Education & Research
- **Transportation Studies**: Understand urban railway systems
- **Data Visualization**: Learn interactive dashboard design
- **Simulation Modeling**: Study complex system interactions
- **Machine Learning**: Generate training data for predictive models

### For Development & Demonstration
- **Portfolio Projects**: Showcase full-stack development skills
- **Client Presentations**: Interactive demos for stakeholders
- **System Prototyping**: Test ideas before full implementation
- **Training Material**: Teach simulation and visualization concepts

## 🛠️ Technical Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Mapping**: Leaflet.js for interactive maps
- **Backend**: Python 3.8+ with SimPy for discrete event simulation
- **Data**: NetworkX for graph-based network modeling
- **Visualization**: Custom CSS animations and responsive design
- **Architecture**: Modular, event-driven simulation system

## 📈 Key Metrics Tracked

- **Operational**: Train count, average delays, efficiency percentages
- **Performance**: Speed variations, distance calculations, ETA accuracy
- **Passenger**: Load factors, affected passenger counts, satisfaction indices
- **Network**: Line performance, station throughput, cascade delay patterns

## 🔧 Customization Options

### Simulation Parameters
- Update frequencies (0.5s to 5s)
- Number of trains per line
- Delay factor intensities
- Weather impact scenarios

### Visual Settings
- Line colors and styling
- Map zoom and center points
- Dashboard layout and themes
- Data refresh intervals

### Data Sources
- Station coordinates and names
- Route definitions and distances
- Realistic timing parameters
- Mumbai-specific operational data

## 🌐 Live Demo Access

You can share your simulation with others using:

1. **Local Network**: `http://your-ip:8000/mumbai_railway_live_demo.html`
2. **ngrok Tunnel**: For external access
3. **GitHub Pages**: Deploy HTML demo for public access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Mumbai Railway network data and station information
- Leaflet.js for excellent mapping capabilities
- SimPy for discrete event simulation framework
- The transportation research community for insights and inspiration

---

**Built with ❤️ for Mumbai's Railway Network**

*Bringing transparency and insights to one of the world's busiest suburban railway systems*
