'use client';

import { useState, useEffect, useRef } from 'react';
import TrainList from './TrainList';
import StationSelector from './StationSelector';
import LiveDemoControls from './LiveDemoControls';
import SimulationMap from './SimulationMap';
import TrainScheduleTable from './TrainScheduleTable';
import DisruptionFactorsCompact from './DisruptionFactorsCompact';

interface Train {
  id: string;
  name: string;
  status: 'Running' | 'Delayed' | 'On Time' | 'Cancelled' | 'Critical';
  route: string;
  line: 'Western' | 'Central Main' | 'Trans-Harbour';
  current: string;
  next: string;
  currentStation: string;
  nextStation: string;
  estimatedTime: string;
  eta: Date;
  delay: number;
  passengers: number;
  speed: number;
  currentSpeed?: number;
  lat: number;
  lon: number;
  positionInSegment: number;
  startStation: string;
  direction: 'UP' | 'DOWN';
  startTime: Date;
  distanceToNext: number;
}

interface DisruptionFactors {
  rushHour: number;
  weather: number;
  junctionCongestion: number;
  equipmentReliability: number;
  festivalCrowds: number;
  platformStrain: number;
  staffEfficiency: number;
  externalDelays: number;
}

const MumbaiRailway = () => {
  const [trains, setTrains] = useState<Train[]>([]);
  const [selectedStation, setSelectedStation] = useState('CST');
  const [isLiveDemo, setIsLiveDemo] = useState(false);
  const [demoSpeed, setDemoSpeed] = useState(1);
  const [selectedTrain, setSelectedTrain] = useState<string | null>(null);
  
  // Simulation state
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);
  const [trainCount, setTrainCount] = useState(0);
  const [passengerCount, setPassengerCount] = useState(0);
  const [avgDelay, setAvgDelay] = useState(0);
  const [efficiency, setEfficiency] = useState(100);
  
  // Real-time animation state
  const [animationFrame, setAnimationFrame] = useState(0);
  const [lastUpdateTime, setLastUpdateTime] = useState(Date.now());
  const animationFrameRef = useRef<number | null>(null);
  
  // AI System state
  const [aiActive, setAiActive] = useState(false);
  const [aiDecisions, setAiDecisions] = useState(0);
  const [aiPreventedDelays, setAiPreventedDelays] = useState(0);
  const [aiOptimizations, setAiOptimizations] = useState(0);
  const [aiPerformance, setAiPerformance] = useState(0);
  const [aiDecisionLog, setAiDecisionLog] = useState<string[]>([
    '[SYSTEM] AI Optimization Suite Initialized',
    '[READY] Awaiting activation command...'
  ]);
  
  // Disruption factors
  const [disruptionFactors, setDisruptionFactors] = useState<DisruptionFactors>({
    rushHour: 0,
    weather: 0,
    junctionCongestion: 0,
    equipmentReliability: 0,
    festivalCrowds: 0,
    platformStrain: 0,
    staffEfficiency: 0,
    externalDelays: 0
  });

  // Advanced tracking state
  const [trackingSpeed, setTrackingSpeed] = useState(2000);
  const [trackingPaused, setTrackingPaused] = useState(false);
  
  const simulationIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const trackingIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const advancedSystemsIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const aiLogIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Real-time animation loop for millisecond updates
  const startRealTimeAnimation = () => {
    const animate = () => {
      const now = Date.now();
      setLastUpdateTime(now);
      setAnimationFrame(prev => prev + 1);
      
      // Update train positions more frequently for smooth animation
      if (isSimulationRunning) {
        updateTrainPositions();
      }
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };
    animationFrameRef.current = requestAnimationFrame(animate);
  };

  const stopRealTimeAnimation = () => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  };

  const stations = [
    'CST', 'Masjid', 'Sandhurst Road', 'Dockyard Road', 'Reay Road',
    'Cotton Green', 'Sewri', 'Wadala Road', 'Kings Circle', 'Mahim',
    'Bandra', 'Khar Road', 'Santacruz', 'Vile Parle', 'Andheri',
    'Jogeshwari', 'Ram Mandir', 'Goregaon', 'Malad', 'Kandivali',
    'Borivali', 'Dahisar', 'Mira Road', 'Bhayandar', 'Naigaon',
    'Vasai Road', 'Nallasopara', 'Virar'
  ];

  const stationData = [
    // Western Line
    {"name": "Churchgate", "lat": 18.9322, "lon": 72.8264, "line": "Western", "type": "Terminus"},
    {"name": "Marine Lines", "lat": 18.9434, "lon": 72.8234, "line": "Western", "type": "Regular"},
    {"name": "Charni Road", "lat": 18.9515, "lon": 72.8193, "line": "Western", "type": "Regular"},
    {"name": "Grant Road", "lat": 18.9659, "lon": 72.8153, "line": "Western", "type": "Regular"},
    {"name": "Mumbai Central", "lat": 18.9693, "lon": 72.8209, "line": "Western", "type": "Junction"},
    {"name": "Mahalaxmi", "lat": 18.9827, "lon": 72.8269, "line": "Western", "type": "Regular"},
    {"name": "Lower Parel", "lat": 18.9961, "lon": 72.8313, "line": "Western", "type": "Regular"},
    {"name": "Elphinstone Road", "lat": 19.0077, "lon": 72.8311, "line": "Western", "type": "Junction"},
    {"name": "Dadar", "lat": 19.0176, "lon": 72.8562, "line": "Western", "type": "Major Junction"},
    {"name": "Bandra", "lat": 19.0544, "lon": 72.8407, "line": "Western", "type": "Major"},
    {"name": "Khar Road", "lat": 19.0728, "lon": 72.8377, "line": "Western", "type": "Regular"},
    {"name": "Santacruz", "lat": 19.0815, "lon": 72.8404, "line": "Western", "type": "Regular"},
    {"name": "Vile Parle", "lat": 19.0989, "lon": 72.8472, "line": "Western", "type": "Regular"},
    {"name": "Andheri", "lat": 19.1197, "lon": 72.8462, "line": "Western", "type": "Major"},
    {"name": "Jogeshwari", "lat": 19.1344, "lon": 72.8514, "line": "Western", "type": "Regular"},
    {"name": "Ram Mandir", "lat": 19.1415, "lon": 72.8400, "line": "Western", "type": "Regular"},
    {"name": "Goregaon", "lat": 19.1540, "lon": 72.8503, "line": "Western", "type": "Regular"},
    {"name": "Malad", "lat": 19.1875, "lon": 72.8482, "line": "Western", "type": "Regular"},
    {"name": "Kandivali", "lat": 19.2084, "lon": 72.8527, "line": "Western", "type": "Regular"},
    {"name": "Borivali", "lat": 19.2307, "lon": 72.8567, "line": "Western", "type": "Major"},
    {"name": "Dahisar", "lat": 19.2544, "lon": 72.8610, "line": "Western", "type": "Regular"},
    {"name": "Mira Road", "lat": 19.2952, "lon": 72.8739, "line": "Western", "type": "Regular"},
    {"name": "Bhayandar", "lat": 19.3017, "lon": 72.8517, "line": "Western", "type": "Regular"},
    {"name": "Naigaon", "lat": 19.3589, "lon": 72.8644, "line": "Western", "type": "Regular"},
    {"name": "Vasai Road", "lat": 19.3919, "lon": 72.8397, "line": "Western", "type": "Junction"},
    {"name": "Nallasopara", "lat": 19.4170, "lon": 72.8119, "line": "Western", "type": "Regular"},
    {"name": "Virar", "lat": 19.4559, "lon": 72.8081, "line": "Western", "type": "Terminus"},
    
    // Central Line (Main)
    {"name": "CST", "lat": 18.9398, "lon": 72.8355, "line": "Central Main", "type": "Terminus"},
    {"name": "Masjid", "lat": 18.9472, "lon": 72.8317, "line": "Central Main", "type": "Regular"},
    {"name": "Sandhurst Road", "lat": 18.9566, "lon": 72.8415, "line": "Central Main", "type": "Regular"},
    {"name": "Dockyard Road", "lat": 18.9671, "lon": 72.8453, "line": "Central Main", "type": "Regular"},
    {"name": "Reay Road", "lat": 18.9743, "lon": 72.8467, "line": "Central Main", "type": "Regular"},
    {"name": "Cotton Green", "lat": 18.9885, "lon": 72.8511, "line": "Central Main", "type": "Regular"},
    {"name": "Sewri", "lat": 18.9968, "lon": 72.8566, "line": "Central Main", "type": "Regular"},
    {"name": "Wadala Road", "lat": 19.0144, "lon": 72.8577, "line": "Central Main", "type": "Regular"},
    {"name": "Kings Circle", "lat": 19.0269, "lon": 72.8590, "line": "Central Main", "type": "Regular"},
    {"name": "Mahim", "lat": 19.0441, "lon": 72.8397, "line": "Central Main", "type": "Junction"},
    {"name": "Bandra Central", "lat": 19.0544, "lon": 72.8407, "line": "Central Main", "type": "Major"},
    {"name": "Khar Road Central", "lat": 19.0728, "lon": 72.8377, "line": "Central Main", "type": "Regular"},
    {"name": "Kurla", "lat": 19.0653, "lon": 72.8789, "line": "Central Main", "type": "Major Junction"},
    {"name": "Vidyavihar", "lat": 19.0825, "lon": 72.8970, "line": "Central Main", "type": "Regular"},
    {"name": "Ghatkopar", "lat": 19.0864, "lon": 72.9081, "line": "Central Main", "type": "Major"},
    {"name": "Vikhroli", "lat": 19.1056, "lon": 72.9259, "line": "Central Main", "type": "Regular"},
    {"name": "Kanjurmarg", "lat": 19.1289, "lon": 72.9378, "line": "Central Main", "type": "Regular"},
    {"name": "Bhandup", "lat": 19.1444, "lon": 72.9378, "line": "Central Main", "type": "Regular"},
    {"name": "Nahur", "lat": 19.1547, "lon": 72.9556, "line": "Central Main", "type": "Regular"},
    {"name": "Mulund", "lat": 19.1722, "lon": 72.9561, "line": "Central Main", "type": "Regular"},
    {"name": "Thane", "lat": 19.1972, "lon": 72.9828, "line": "Central Main", "type": "Major"},
    {"name": "Kalwa", "lat": 19.2192, "lon": 73.0000, "line": "Central Main", "type": "Regular"},
    {"name": "Mumbra", "lat": 19.2194, "lon": 73.0342, "line": "Central Main", "type": "Regular"},
    {"name": "Diva", "lat": 19.2542, "lon": 73.0239, "line": "Central Main", "type": "Junction"},
    {"name": "Kopar", "lat": 19.2692, "lon": 73.0539, "line": "Central Main", "type": "Regular"},
    {"name": "Dombivli", "lat": 19.2164, "lon": 73.0864, "line": "Central Main", "type": "Major"},
    {"name": "Thakurli", "lat": 19.1972, "lon": 73.1122, "line": "Central Main", "type": "Regular"},
    {"name": "Kalyan", "lat": 19.2437, "lon": 73.1355, "line": "Central Main", "type": "Major Junction"},
    
    // Trans-Harbour Line
    {"name": "Thane Trans", "lat": 19.1972, "lon": 72.9828, "line": "Trans-Harbour", "type": "Junction"},
    {"name": "Airoli", "lat": 19.1586, "lon": 72.9972, "line": "Trans-Harbour", "type": "Regular"},
    {"name": "Ghansoli", "lat": 19.1197, "lon": 73.0142, "line": "Trans-Harbour", "type": "Regular"},
    {"name": "Rabale", "lat": 19.1289, "lon": 73.0203, "line": "Trans-Harbour", "type": "Regular"},
    {"name": "Belapur CBD", "lat": 19.0378, "lon": 73.0158, "line": "Trans-Harbour", "type": "Major"},
    {"name": "Kharghar", "lat": 19.0447, "lon": 73.0669, "line": "Trans-Harbour", "type": "Regular"},
    {"name": "Mansarovar", "lat": 19.0331, "lon": 73.0708, "line": "Trans-Harbour", "type": "Regular"},
    {"name": "Khandeshwar", "lat": 19.0275, "lon": 73.0847, "line": "Trans-Harbour", "type": "Regular"},
    {"name": "Panvel", "lat": 18.9894, "lon": 73.1169, "line": "Trans-Harbour", "type": "Terminus"},
    {"name": "Nerul", "lat": 19.0328, "lon": 73.0158, "line": "Trans-Harbour", "type": "Regular"},
    {"name": "Juinagar", "lat": 19.0447, "lon": 73.0067, "line": "Trans-Harbour", "type": "Regular"}
  ];

  // Initialize trains with comprehensive data
  const initializeTrains = () => {
    const lines = ['Western', 'Central Main', 'Trans-Harbour'] as const;
    const initialTrains: Train[] = [];
    
    lines.forEach((line, lineIndex) => {
      const lineStations = stationData.filter(s => s.line === line);
      const trainCount = line === 'Western' ? 15 : line === 'Central Main' ? 15 : 10;
      
      for (let i = 0; i < trainCount; i++) {
        const trainId = `${line.charAt(0)}${String(i + 1).padStart(3, '0')}`;
        const direction = (i % 2 === 0) ? 'UP' : 'DOWN';
        
        if (lineStations.length >= 2) {
          const progress = (Date.now() / 60000 + lineIndex * 20 + i * 15) % 60 / 60;
          const stationProgress = progress * (lineStations.length - 1);
          
          const currentIndex = Math.floor(stationProgress);
          const nextIndex = Math.min(currentIndex + 1, lineStations.length - 1);
          const current = lineStations[currentIndex];
          const next = lineStations[nextIndex];
          
          const positionInSegment = stationProgress - currentIndex;
          const lat = current.lat + (next.lat - current.lat) * positionInSegment;
          const lon = current.lon + (next.lon - current.lon) * positionInSegment;
          
          const basePassengers = Math.floor(Math.random() * 600 + 200);
          const baseDelay = Math.random() * 3;
          
          const train: Train = {
            id: trainId,
            name: `${line} Local`,
            status: baseDelay > 2 ? 'Delayed' : baseDelay > 5 ? 'Critical' : 'On Time',
            route: `${lineStations[0].name} - ${lineStations[lineStations.length - 1].name}`,
            line,
            current: current.name,
            next: next.name,
            currentStation: current.name,
            nextStation: next.name,
            estimatedTime: `${Math.floor(Math.random() * 8) + 2} mins`,
            eta: new Date(Date.now() + (Math.random() * 8 + 3) * 60000),
            delay: baseDelay,
            passengers: basePassengers,
            speed: 45 + Math.random() * 20,
            currentSpeed: 45 + Math.random() * 20,
            lat,
            lon,
            positionInSegment,
            startStation: lineStations[0].name,
            direction,
            startTime: new Date(Date.now() - Math.random() * 3600000),
            distanceToNext: Math.random() * 2 + 0.5
          };
          
          initialTrains.push(train);
        }
      }
    });
    
    return initialTrains;
  };

  // Start simulation
  const startSimulation = () => {
    console.log('🚂 Starting simulation...');
    setIsSimulationRunning(true);
    setTrains(initializeTrains());
    
    // Start real-time animation loop for smooth updates
    startRealTimeAnimation();
    
    // Start main simulation loop
    simulationIntervalRef.current = setInterval(() => {
      updateTrainPositions();
    }, 1000); // Reduced from 2000ms to 1000ms for smoother updates
    
    // Start tracking loop
    if (!trackingPaused) {
      trackingIntervalRef.current = setInterval(() => {
        updateDetailedTracking();
      }, trackingSpeed);
    }
    
    // Start advanced systems with more frequent AI updates
    advancedSystemsIntervalRef.current = setInterval(() => {
      updateAdvancedSystems();
    }, 6000); // Reduced from 15000ms to 6000ms for more frequent AI activity
  };

  // Stop simulation
  const stopSimulation = () => {
    console.log('🛑 Stopping simulation...');
    setIsSimulationRunning(false);
    setTrains([]);
    
    // Stop real-time animation
    stopRealTimeAnimation();
    
    // Clear intervals
    if (simulationIntervalRef.current) {
      clearInterval(simulationIntervalRef.current);
      simulationIntervalRef.current = null;
    }
    if (trackingIntervalRef.current) {
      clearInterval(trackingIntervalRef.current);
      trackingIntervalRef.current = null;
    }
    if (advancedSystemsIntervalRef.current) {
      clearInterval(advancedSystemsIntervalRef.current);
      advancedSystemsIntervalRef.current = null;
    }
    if (aiLogIntervalRef.current) {
      clearInterval(aiLogIntervalRef.current);
      aiLogIntervalRef.current = null;
    }
    
    // Reset metrics
    setTrainCount(0);
    setPassengerCount(0);
    setAvgDelay(0);
    setEfficiency(100);
  };

  // Update train positions
  const updateTrainPositions = () => {
    setTrains(prevTrains => {
      return prevTrains.map(train => {
        // Get line stations
        const lineStations = stationData.filter(s => s.line === train.line);
        if (lineStations.length < 2) return train;
        
        // Update position
        let newPositionInSegment = train.positionInSegment + 0.05; // Move along segment
        let currentIndex = lineStations.findIndex(s => s.name === train.current);
        let nextIndex = currentIndex + 1;
        
        // Check if reached next station
        if (newPositionInSegment >= 1.0) {
          newPositionInSegment = 0;
          currentIndex = nextIndex;
          nextIndex = Math.min(currentIndex + 1, lineStations.length - 1);
          
          // If reached end, reverse direction
          if (currentIndex >= lineStations.length - 1) {
            currentIndex = 0;
            nextIndex = 1;
          }
        }
        
        const current = lineStations[currentIndex];
        const next = lineStations[nextIndex];
        
        // Calculate new lat/lon
        const lat = current.lat + (next.lat - current.lat) * newPositionInSegment;
        const lon = current.lon + (next.lon - current.lon) * newPositionInSegment;
        
        // Apply disruption factors
        let delayMultiplier = 1.0;
        delayMultiplier += disruptionFactors.rushHour * 0.5;
        delayMultiplier += disruptionFactors.weather * 0.3;
        delayMultiplier += disruptionFactors.junctionCongestion * 0.4;
        delayMultiplier += disruptionFactors.equipmentReliability * 0.6;
        
        const newDelay = train.delay + (Math.random() * 0.5 * delayMultiplier);
        
        return {
          ...train,
          current: current.name,
          next: next.name,
          currentStation: current.name,
          nextStation: next.name,
          positionInSegment: newPositionInSegment,
          lat,
          lon,
          delay: newDelay,
          status: newDelay > 5 ? 'Critical' : newDelay > 2 ? 'Delayed' : 'On Time',
          estimatedTime: `${Math.floor(Math.random() * 8) + 2} mins`,
          passengers: Math.min(train.passengers + Math.floor(Math.random() * 50 - 20), 2000),
          eta: new Date(Date.now() + (Math.random() * 8 + 3) * 60000)
        };
      });
    });
  };

  // Update detailed tracking
  const updateDetailedTracking = () => {
    // Update metrics
    if (trains.length > 0) {
      setTrainCount(trains.length);
      setPassengerCount(trains.reduce((sum, train) => sum + train.passengers, 0));
      setAvgDelay(trains.reduce((sum, train) => sum + train.delay, 0) / trains.length);
      
      const onTimeTrains = trains.filter(train => train.status === 'On Time').length;
      setEfficiency((onTimeTrains / trains.length) * 100);
    }
  };

  // Update advanced systems
  const updateAdvancedSystems = () => {
    if (aiActive) {
      // Simulate AI making decisions
      const newDecisions = Math.floor(Math.random() * 5) + 1;
      setAiDecisions(prev => prev + newDecisions);
      
      // Generate realistic AI logs
      const aiActions = [
        'Analyzing passenger flow patterns at Dadar junction',
        'Optimizing signal timing for Western Line',
        'Detecting potential bottleneck at Kurla station',
        'Rerouting Train WR-401 to avoid congestion',
        'Implementing dynamic scheduling adjustments',
        'Monitoring weather impact on Central Line',
        'Predicting rush hour surge in 15 minutes',
        'Coordinating with traffic control systems',
        'Optimizing platform allocation at CST',
        'Reducing dwell time at high-traffic stations'
      ];
      
      // Generate multiple logs per cycle for active appearance
      const numLogs = Math.floor(Math.random() * 3) + 1;
      for (let i = 0; i < numLogs; i++) {
        setTimeout(() => {
          const action = aiActions[Math.floor(Math.random() * aiActions.length)];
          addAiDecisionLog(`[AI] ${action}`);
        }, i * 500);
      }
      
      // Randomly prevent some delays
      if (Math.random() > 0.6) {
        setAiPreventedDelays(prev => prev + 1);
        addAiDecisionLog('[ALERT] Prevented potential 4-min delay at junction');
      }
      
      // Optimize routes
      if (Math.random() > 0.7) {
        setAiOptimizations(prev => prev + 1);
        const savedTime = Math.floor(Math.random() * 8) + 2;
        addAiDecisionLog(`[OPTIMIZATION] Route optimized, saved ${savedTime} minutes`);
      }
      
      // Critical system alerts
      if (Math.random() > 0.9) {
        addAiDecisionLog('[CRITICAL] Emergency protocol activated for overcrowding');
      }
      
      // Update performance
      const performanceGain = Math.min(15, aiDecisions * 0.1 + aiOptimizations * 0.5);
      setAiPerformance(performanceGain);
    }
  };

  // Add AI decision to log
  const addAiDecisionLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setAiDecisionLog(prev => [
      `[${timestamp}] ${message}`,
      ...prev.slice(0, 9) // Keep only last 10 entries
    ]);
  };

  // Activate/Deactivate AI
  const toggleAI = () => {
    setAiActive(!aiActive);
    if (!aiActive) {
      // Immediate activation logs
      addAiDecisionLog('[SYSTEM] AI Optimization Suite Activated');
      addAiDecisionLog('[SYSTEM] Initializing neural networks...');
      addAiDecisionLog('[SYSTEM] Loading Mumbai Railway data patterns...');
      addAiDecisionLog('[SYSTEM] AI systems fully operational');
      
      // Start continuous AI log generation
      aiLogIntervalRef.current = setInterval(() => {
        if (Math.random() > 0.4) { // 60% chance every 2 seconds
          const systemLogs = [
            '[MONITOR] Scanning all active train positions',
            '[ANALYSIS] Processing passenger density data',
            '[PREDICT] Forecasting next 10-minute traffic flow',
            '[OPTIMIZE] Adjusting signal coordination',
            '[LEARN] Updating ML models with real-time data'
          ];
          const log = systemLogs[Math.floor(Math.random() * systemLogs.length)];
          addAiDecisionLog(log);
        }
      }, 2000);
      
      // Trigger immediate advanced systems update
      setTimeout(() => updateAdvancedSystems(), 1000);
    } else {
      addAiDecisionLog('[SYSTEM] AI Optimization Suite Deactivated');
      addAiDecisionLog('[SYSTEM] Switching to manual control mode');
      
      // Clear AI log generation
      if (aiLogIntervalRef.current) {
        clearInterval(aiLogIntervalRef.current);
        aiLogIntervalRef.current = null;
      }
    }
  };

  // Add disruption factor
  const addDisruptionFactor = (factor: keyof DisruptionFactors) => {
    setDisruptionFactors(prev => ({
      ...prev,
      [factor]: Math.min(prev[factor] + 1, 5)
    }));
  };

  // Select train for quick actions
  const selectTrain = (trainId: string) => {
    setSelectedTrain(trainId);
  };

  // Perform quick action on selected train
  const performQuickAction = (action: string, trainId: string) => {
    setTrains(prevTrains => 
      prevTrains.map(train => {
        if (train.id === trainId) {
          switch (action) {
            case 'hold':
              return { ...train, delay: train.delay + 3, status: 'Delayed' };
            case 'swap':
              return { ...train, delay: Math.max(0, train.delay - 2) };
            case 'reroute':
              return { ...train, delay: train.delay + 8, status: 'Critical' };
            default:
              return train;
          }
        }
        return train;
      })
    );
    addAiDecisionLog(`[ACTION] ${action.toUpperCase()} applied to ${trainId}`);
  };

  const filteredTrains = trains.filter(train => 
    train.currentStation === selectedStation || 
    train.nextStation === selectedStation ||
    train.route.includes(selectedStation)
  );

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      stopRealTimeAnimation();
      if (simulationIntervalRef.current) clearInterval(simulationIntervalRef.current);
      if (trackingIntervalRef.current) clearInterval(trackingIntervalRef.current);
      if (advancedSystemsIntervalRef.current) clearInterval(advancedSystemsIntervalRef.current);
      if (aiLogIntervalRef.current) clearInterval(aiLogIntervalRef.current);
    };
  }, []);

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #0D1164 0%, #1E40AF 35%, #3B82F6 65%, #F78D60 100%)' }}>
      <div className="container mx-auto px-4 py-4">
        {/* Header */}
        <header className="text-center mb-4">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
            🚂 Mumbai Railway Live Simulation
          </h1>
          <p className="text-sm md:text-base text-orange-200 max-w-3xl mx-auto mb-2">
            Real-time train movements and network performance monitoring with AI optimization
          </p>
          <div className="bg-white/10 backdrop-blur-lg rounded-lg p-2 inline-block">
            <span className="text-xs md:text-sm text-white">
              🚇 Interconnected Mumbai Railway Network • 3 Lines • 65+ Stations • Phase 1 Scaling
            </span>
          </div>
        </header>

        {/* Main Content Grid - Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Left Column - Map and Simulation */}
          <div className="space-y-4">
            <SimulationMap 
              trains={trains}
              stationData={stationData}
              onTrainSelect={selectTrain}
              selectedTrain={selectedTrain}
            />
            
            {/* Live Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              <div className="bg-white/10 backdrop-blur-lg rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-white">{trainCount}</div>
                <div className="text-xs text-orange-200">Active Trains</div>
              </div>
              <div className="bg-white/10 backdrop-blur-lg rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-white">{Math.floor(passengerCount / 1000)}K</div>
                <div className="text-xs text-orange-200">Passengers</div>
              </div>
              <div className="bg-white/10 backdrop-blur-lg rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-white">{avgDelay.toFixed(1)}m</div>
                <div className="text-xs text-orange-200">Avg Delay</div>
              </div>
              <div className="bg-white/10 backdrop-blur-lg rounded-lg p-3 text-center">
                <div className="text-xl font-bold text-white">{efficiency.toFixed(1)}%</div>
                <div className="text-xs text-orange-200">Efficiency</div>
              </div>
            </div>

            {/* Simulation Controls */}
            <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4">
              <h3 className="text-lg font-bold text-white mb-3">🚂 Live Train Simulation</h3>
              
              {/* Simulation Status */}
              <div className="mb-3 p-3 rounded-lg" style={{ backgroundColor: isSimulationRunning ? '#10B981' : '#6B7280' }}>
                <div className="text-white font-bold text-center flex items-center justify-center gap-2">
                  {isSimulationRunning ? (
                    <>
                      🟢 SIMULATION ACTIVE
                      <div className={`w-2 h-2 rounded-full ${animationFrame % 40 < 20 ? 'bg-yellow-400' : 'bg-yellow-600'} transition-all duration-100`}></div>
                    </>
                  ) : (
                    '🔴 SIMULATION STOPPED'
                  )}
                </div>
                <div className="text-xs text-center text-white/80 mt-1">
                  {isSimulationRunning ? (
                    <div className="flex items-center justify-center gap-4">
                      <span>{trains.length} trains moving</span>
                      <span>•</span>
                      <span className="font-mono">Frame: {animationFrame}</span>
                      <span>•</span>
                      <span className="font-mono">{(1000 / Math.max(1, Date.now() - lastUpdateTime)).toFixed(1)} FPS</span>
                    </div>
                  ) : (
                    'Click Start to begin train movements'
                  )}
                </div>
              </div>

              {/* Control Buttons */}
              <div className="grid grid-cols-2 gap-2 mb-3">
                <button
                  onClick={startSimulation}
                  disabled={isSimulationRunning}
                  style={{ backgroundColor: isSimulationRunning ? '#6B7280' : '#3B82F6' }}
                  className={`p-3 rounded-lg font-bold text-white text-sm transition-all ${
                    isSimulationRunning 
                      ? 'cursor-not-allowed opacity-50' 
                      : 'hover:opacity-90'
                  }`}
                >
                  ▶️ Start Simulation
                </button>
                <button
                  onClick={stopSimulation}
                  style={{ backgroundColor: '#EF4444' }}
                  className="p-3 rounded-lg font-bold text-white text-sm hover:opacity-90 transition-all"
                >
                  ⏹️ Stop Simulation
                </button>
              </div>

              {/* Real-time Status */}
              {isSimulationRunning && (
                <div className="bg-black/20 rounded-lg p-3">
                  <div className="text-xs text-orange-200 mb-2">📡 Live Updates</div>
                  <div className="space-y-1 text-xs text-white">
                    <div>• Trains updating every 2 seconds</div>
                    <div>• AI system monitoring delays</div>
                    <div>• Real-time passenger boarding</div>
                    <div>• Dynamic route optimization</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Controls and Phase Systems */}
          <div className="space-y-4">
            {/* Phase 1 Metrics */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-500 text-white p-4 rounded-lg text-center">
              <div className="font-bold text-lg">🎯 Phase 1: {trainCount} Trains</div>
              <div className="text-sm opacity-90">
                On-Time: {efficiency.toFixed(1)}% • Delayed: {trains.filter(t => t.status === 'Delayed').length} • Critical: {trains.filter(t => t.status === 'Critical').length}
              </div>
            </div>

            {/* Enhanced AI Optimization Suite */}
            <div className="bg-white/10 backdrop-blur-lg rounded-lg p-5 text-white shadow-xl">
              <h3 className="text-xl font-bold mb-4 text-center">
                🧠 ADVANCED AI OPTIMIZATION SUITE
              </h3>
              
              {/* AI Status Display */}
              <div className="bg-white/15 backdrop-blur-lg rounded-lg p-4 mb-4">
                <div className="flex justify-between items-center mb-3">
                  <div>
                    <h4 className="text-lg font-semibold">🤖 AI System Status</h4>
                    <div className="text-sm opacity-90">
                      {aiActive ? 'Neural Network Processing Active' : 'AI Standby - Ready for Deployment'}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-white">+{aiPerformance.toFixed(1)}%</div>
                    <div className="text-xs opacity-80">Efficiency Gain</div>
                  </div>
                </div>
                
                {/* AI Performance Metrics */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="text-center bg-white/10 rounded p-2">
                    <div className="text-lg font-bold">{aiDecisions}</div>
                    <div className="text-xs opacity-80">AI Decisions/min</div>
                  </div>
                  <div className="text-center bg-white/10 rounded p-2">
                    <div className="text-lg font-bold">{aiPreventedDelays}</div>
                    <div className="text-xs opacity-80">Delays Prevented</div>
                  </div>
                  <div className="text-center bg-white/10 rounded p-2">
                    <div className="text-lg font-bold">{aiOptimizations}</div>
                    <div className="text-xs opacity-80">Route Optimizations</div>
                  </div>
                </div>

                {/* AI Capabilities */}
                <div className="bg-black/20 rounded p-3 mb-4">
                  <h5 className="font-semibold mb-2 text-sm">🎯 AI Capabilities</h5>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>🧠 Deep Learning Analysis</div>
                    <div>📊 Predictive Modeling</div>
                    <div>🔄 Real-time Optimization</div>
                    <div>⚡ Dynamic Rerouting</div>
                    <div>📈 Traffic Pattern Recognition</div>
                    <div>🎯 Delay Prevention</div>
                  </div>
                </div>
              </div>
              
              {/* AI Control Buttons */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <button
                  onClick={toggleAI}
                  style={{ backgroundColor: aiActive ? '#6B7280' : '#10B981' }}
                  className={`p-3 rounded-lg font-bold text-sm transition-all ${
                    aiActive 
                      ? 'cursor-not-allowed opacity-50' 
                      : 'hover:opacity-90'
                  }`}
                  disabled={aiActive}
                >
                  🚀 ACTIVATE AI
                </button>
                <button
                  onClick={toggleAI}
                  style={{ backgroundColor: !aiActive ? '#6B7280' : '#EF4444' }}
                  className={`p-3 rounded-lg font-bold text-sm transition-all ${
                    !aiActive 
                      ? 'cursor-not-allowed opacity-50' 
                      : 'hover:opacity-90'
                  }`}
                  disabled={!aiActive}
                >
                  ⏹️ DEACTIVATE AI
                </button>
              </div>
              
              {/* AI Decision Log */}
              <div style={{ backgroundColor: '#0D1164' }} className="rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-sm opacity-90">🤖 AI Decision Log (Real-time)</h4>
                  <div className="flex items-center gap-2">
                    {/* Real-time animation indicator */}
                    <div className={`w-2 h-2 rounded-full ${animationFrame % 60 < 30 ? 'bg-green-400' : 'bg-green-600'} transition-all duration-75`}></div>
                    <span className="text-xs text-green-300 font-mono">
                      {(Date.now() - lastUpdateTime).toFixed(0)}ms
                    </span>
                  </div>
                </div>
                <div className="text-xs font-mono space-y-1 max-h-32 overflow-y-auto">
                  {aiDecisionLog.slice(0, 6).map((log, index) => (
                    <div 
                      key={index}
                      className={`${
                        log.includes('[SYSTEM]') ? 'text-green-300' :
                        log.includes('[AI]') ? 'text-blue-300' :
                        log.includes('[ACTION]') ? 'text-yellow-300' :
                        log.includes('[ALERT]') ? 'text-red-300' :
                        log.includes('[CRITICAL]') ? 'text-red-400 font-bold' :
                        log.includes('[OPTIMIZATION]') ? 'text-purple-300' :
                        log.includes('[MONITOR]') ? 'text-cyan-300' :
                        log.includes('[ANALYSIS]') ? 'text-orange-300' :
                        log.includes('[PREDICT]') ? 'text-pink-300' :
                        'text-gray-300'
                      } animate-pulse duration-1000`}
                    >
                      {log}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Phase 1 & 2 Disruption Factors */}
            <DisruptionFactorsCompact
              factors={disruptionFactors}
              onAddFactor={addDisruptionFactor}
            />

            {/* Advanced Controls - Temporarily disabled */}
            <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4">
              <h3 className="text-lg font-bold text-white mb-3">🎛️ Advanced Controls</h3>
              <div className="text-center text-orange-200 py-3">
                <div className="text-lg mb-1">🔧</div>
                <div className="text-xs">Advanced controls available after map loads</div>
              </div>
            </div>
          </div>
        </div>

        {/* Train Schedule Table - Compact */}
        <div className="mt-4">
          <TrainScheduleTable trains={trains} />
        </div>

        {/* Station Controls - Horizontal Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 mt-4">
          <StationSelector 
            stations={stations}
            selectedStation={selectedStation}
            onStationChange={setSelectedStation}
          />
          <LiveDemoControls
            isLiveDemo={isLiveDemo}
            demoSpeed={demoSpeed}
            onToggleDemo={setIsLiveDemo}
            onSpeedChange={setDemoSpeed}
          />
        </div>

        {/* Filtered Train Information - Compact */}
        <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4 shadow-xl mt-4">
          <h2 className="text-lg font-bold text-white mb-3">
            Trains at {selectedStation} Station
          </h2>
          <TrainList trains={filteredTrains} />
        </div>
      </div>
    </div>
  );
};

export default MumbaiRailway;