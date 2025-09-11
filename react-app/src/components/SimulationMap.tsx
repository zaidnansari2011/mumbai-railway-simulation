'use client';

import { useEffect, useRef } from 'react';

interface Station {
  name: string;
  lat: number;
  lon: number;
  line: string;
  type: string;
}

interface Train {
  id: string;
  name: string;
  lat: number;
  lon: number;
  status: string;
  line: string;
  current: string;
  next: string;
  passengers: number;
  delay: number;
  speed?: number;
}

interface SimulationMapProps {
  trains: Train[];
  stationData: Station[];
  onTrainSelect: (trainId: string) => void;
  selectedTrain: string | null;
}

// Extend Window interface for Leaflet
declare global {
  interface Window {
    L: any;
    selectTrain: (trainId: string) => void;
  }
}

const SimulationMap = ({ trains, stationData, onTrainSelect, selectedTrain }: SimulationMapProps) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<{ [key: string]: any }>({});

  useEffect(() => {
    // Function to initialize map once Leaflet is loaded
    const initializeMap = () => {
      if (typeof window !== 'undefined' && window.L && mapRef.current && !mapInstanceRef.current) {
        try {
          console.log('Initializing Leaflet map...');
          
          // Initialize map
          mapInstanceRef.current = window.L.map(mapRef.current, {
            zoomControl: true,
            scrollWheelZoom: true,
            doubleClickZoom: true,
            touchZoom: true
          }).setView([19.0760, 72.8777], 10);

          // Add tile layer with better error handling
          const tileLayer = window.L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18,
            errorTileUrl: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjU2IiBoZWlnaHQ9IjI1NiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjU2IiBoZWlnaHQ9IjI1NiIgZmlsbD0iI2VlZSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBkb21pbmFudC1iYXNlbGluZT0iY2VudHJhbCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1mYW1pbHk9Im1vbm9zcGFjZSIgZm9udC1zaXplPSIxOHB4IiBmaWxsPSIjYWFhIj5ObyBUaWxlPC90ZXh0Pjwvc3ZnPg=='
          });
          
          tileLayer.addTo(mapInstanceRef.current);

          // Add railway lines with your color palette
          const lineColors = {
            'Western': '#F78D60',     // Orange from your palette
            'Central Main': '#3B82F6', // Blue
            'Trans-Harbour': '#10B981' // Green
          };

          // Draw railway lines
          Object.keys(lineColors).forEach(line => {
            const lineStations = stationData.filter(s => s.line === line);
            if (lineStations.length > 1) {
              const coordinates = lineStations.map(s => [s.lat, s.lon]);
              window.L.polyline(coordinates, {
                color: lineColors[line as keyof typeof lineColors],
                weight: 4,
                opacity: 0.8,
                className: 'railway-line'
              }).addTo(mapInstanceRef.current);
            }
          });

          // Add station markers
          stationData.forEach(station => {
            const icon = station.type === 'Major Junction' ? '🚇' : 
                        station.type === 'Junction' ? '🚉' : 
                        station.type === 'Major' ? '🏢' : '⭕';
            
            const marker = window.L.marker([station.lat, station.lon], {
              icon: window.L.divIcon({
                html: `<div style="font-size: 16px; text-align: center;">${icon}</div>`,
                className: 'station-marker',
                iconSize: [20, 20],
                iconAnchor: [10, 10]
              })
            }).addTo(mapInstanceRef.current);

            marker.bindPopup(`
              <div style="text-align: center; min-width: 150px;">
                <strong>${station.name}</strong><br>
                <span style="color: ${lineColors[station.line as keyof typeof lineColors]};">
                  ${station.line} Line
                </span><br>
                Type: ${station.type}
              </div>
            `);
          });

          console.log('Map initialized successfully');
        } catch (error) {
          console.error('Error initializing map:', error);
        }
      }
    };

    // Check if Leaflet is already loaded
    if (window.L) {
      initializeMap();
    } else {
      // Wait for Leaflet to load
      const checkLeaflet = setInterval(() => {
        if (window.L) {
          clearInterval(checkLeaflet);
          setTimeout(initializeMap, 100); // Small delay to ensure DOM is ready
        }
      }, 100);

      // Cleanup interval after 10 seconds if Leaflet doesn't load
      setTimeout(() => {
        clearInterval(checkLeaflet);
      }, 10000);
    }

    // Cleanup function
    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, [stationData]);

  useEffect(() => {
    if (mapInstanceRef.current && window.L) {
      // Clear existing train markers
      Object.values(markersRef.current).forEach(marker => {
        mapInstanceRef.current.removeLayer(marker);
      });
      markersRef.current = {};

      // Add train markers
      trains.forEach(train => {
        if (train.lat && train.lon) {
          const trainIcon = getTrainIcon(train);
          const isSelected = selectedTrain === train.id;
          
          const marker = window.L.marker([train.lat, train.lon], {
            icon: window.L.divIcon({
              html: `<div style="font-size: 20px; ${isSelected ? 'transform: scale(1.3); filter: drop-shadow(0 0 10px #3498db);' : ''}">${trainIcon}</div>`,
              className: `train-icon ${isSelected ? 'selected-train' : ''}`,
              iconSize: [24, 24],
              iconAnchor: [12, 12]
            })
          }).addTo(mapInstanceRef.current);

          marker.bindPopup(`
            <div style="text-align: center; min-width: 200px;">
              <strong>${train.name}</strong><br>
              <span style="color: #666;">${train.id}</span><br><br>
              <strong>Route:</strong> ${train.current} → ${train.next}<br>
              <strong>Passengers:</strong> ${train.passengers}<br>
              <strong>Status:</strong> <span style="color: ${getStatusColor(train.status)};">${train.status}</span><br>
              <strong>Delay:</strong> ${train.delay.toFixed(1)} min<br>
              <strong>Speed:</strong> ${train.speed?.toFixed(0) || 'N/A'} km/h<br><br>
              <button onclick="window.selectTrain('${train.id}')" 
                style="background: #3498db; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">
                Select for Actions
              </button>
            </div>
          `);

          marker.on('click', () => {
            onTrainSelect(train.id);
          });

          markersRef.current[train.id] = marker;
        }
      });
    }
  }, [trains, selectedTrain, onTrainSelect]);

  // Make selectTrain available globally for popup buttons
  useEffect(() => {
    window.selectTrain = onTrainSelect;
  }, [onTrainSelect]);

  const getTrainIcon = (train: Train) => {
    if (train.speed === 0) return '🚉'; // Stopped at station
    if (train.delay > 10) return '🚃'; // Delayed train
    if (train.passengers > 1500) return '🚋'; // Overcrowded
    if ((train.speed || 0) > 50) return '🚄'; // Fast train
    return '🚂'; // Normal train
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'On Time': return '#27ae60';
      case 'Delayed': return '#f39c12';
      case 'Critical': return '#e74c3c';
      case 'Running': return '#3498db';
      default: return '#95a5a6';
    }
  };

  return (
    <div className="bg-white/95 rounded-lg p-4 shadow-xl">
      <h2 className="text-xl font-bold mb-3 text-gray-800">🗺️ Live Network Map & Real-Time Simulation</h2>
      
      {/* Network Info Banner */}
      <div style={{ background: 'linear-gradient(to right, #3B82F6, #F78D60)' }} className="text-white p-3 rounded-lg mb-3 text-center">
        <div className="font-bold text-sm">🚇 Mumbai Railway Network - Live Train Movements</div>
        <div className="text-xs opacity-90">
          {trains.length > 0 
            ? `${trains.length} trains moving in real-time • AI-powered optimization` 
            : 'Start simulation to see live train movements'
          }
        </div>
      </div>

      {/* Real-time Status */}
      {trains.length > 0 && (
        <div className="bg-green-100 border border-green-400 rounded p-2 mb-3">
          <div className="flex justify-between items-center text-xs">
            <div className="text-green-800">
              <span className="font-bold">🟢 LIVE:</span> Trains updating every 2 seconds
            </div>
            <div className="text-green-600">
              On-Time: {trains.filter(t => t.status === 'On Time').length} | 
              Delayed: {trains.filter(t => t.status === 'Delayed').length} | 
              Critical: {trains.filter(t => t.status === 'Critical').length}
            </div>
          </div>
        </div>
      )}

      {/* Map Container */}
      <div 
        ref={mapRef} 
        className="w-full h-80 md:h-96 rounded-lg border-2 border-gray-300"
        style={{ minHeight: '400px' }}
      >
        {/* Enhanced Fallback content */}
        <div className="w-full h-full bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg flex items-center justify-center">
          <div className="text-center text-gray-600">
            <div className="text-4xl mb-2">🗺️</div>
            <div className="font-bold mb-2">Interactive Railway Map</div>
            <div className="text-sm mb-3">
              {trains.length > 0 
                ? `${trains.length} trains active - Real-time positions updating`
                : 'Start simulation to see live train movements'
              }
            </div>
            {trains.length === 0 && (
              <div className="text-xs text-gray-500 bg-white/70 rounded p-2 inline-block">
                Map loads with internet connection • Click "Start Simulation" above
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Enhanced Map Legend */}
      <div style={{ backgroundColor: '#0D1164' }} className="text-white p-3 rounded-lg mt-3">
        <h4 className="font-bold mb-2 text-sm">🎯 Live Map Legend</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-1 text-xs mb-2">
          <div>🚂 Normal Train</div>
          <div>🚄 Fast Train (&gt;50km/h)</div>
          <div>🚋 Crowded Train (&gt;1500)</div>
          <div>🚃 Delayed Train (&gt;10min)</div>
          <div>🚉 Station Stop (0 speed)</div>
          <div>🚇 Major Junction</div>
        </div>
        <div className="grid grid-cols-3 gap-1 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded" style={{ backgroundColor: '#F78D60' }}></div>
            Western Line
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-teal-400 rounded"></div>
            Central Main
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 bg-green-400 rounded"></div>
            Trans-Harbour
          </div>
        </div>
        {trains.length > 0 && (
          <div className="mt-2 pt-2 border-t border-white/20 text-xs">
            <div className="text-orange-200">🔄 Real-time Updates:</div>
            <div>• Train positions update every 2 seconds</div>
            <div>• Click any train for detailed information</div>
            <div>• AI system monitors and optimizes routes</div>
          </div>
        )}
      </div>
    </div>
  );
};

// Load Leaflet CSS and JS if not already loaded
if (typeof window !== 'undefined' && !window.L) {
  // Load CSS first
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
  link.integrity = 'sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=';
  link.crossOrigin = '';
  document.head.appendChild(link);

  // Load JS after CSS
  const script = document.createElement('script');
  script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
  script.integrity = 'sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=';
  script.crossOrigin = '';
  script.async = false; // Load synchronously to ensure proper initialization
  document.head.appendChild(script);
}

export default SimulationMap;