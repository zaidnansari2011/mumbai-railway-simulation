'use client';

import { useState } from 'react';

interface StationSelectorProps {
  stations: string[];
  selectedStation: string;
  onStationChange: (station: string) => void;
}

const StationSelector = ({ stations, selectedStation, onStationChange }: StationSelectorProps) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const filteredStations = stations.filter(station =>
    station.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleStationSelect = (station: string) => {
    onStationChange(station);
    setIsDropdownOpen(false);
    setSearchTerm('');
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4">🚉 Select Station</h3>
      
      <div className="relative">
        <input
          type="text"
          placeholder="Search stations..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setIsDropdownOpen(true);
          }}
          onFocus={() => setIsDropdownOpen(true)}
          className="w-full px-4 py-3 rounded-lg bg-white/20 text-white placeholder-orange-200 border border-white/30 focus:border-orange-300 focus:outline-none focus:ring-2 focus:ring-orange-300/50"
        />
        
        {isDropdownOpen && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-xl max-h-60 overflow-y-auto z-10 border border-gray-200">
            {filteredStations.length > 0 ? (
              filteredStations.map((station, index) => (
                <button
                  key={station}
                  onClick={() => handleStationSelect(station)}
                  className={`w-full text-left px-4 py-3 hover:bg-gray-100 transition-colors ${
                    station === selectedStation ? 'bg-purple-100 text-purple-900 font-semibold' : 'text-gray-900'
                  } ${index === 0 ? 'rounded-t-lg' : ''} ${index === filteredStations.length - 1 ? 'rounded-b-lg' : ''}`}
                >
                  <div className="flex items-center justify-between">
                    <span>{station}</span>
                    {station === selectedStation && (
                      <span className="text-purple-600">✓</span>
                    )}
                  </div>
                </button>
              ))
            ) : (
              <div className="px-4 py-3 text-gray-500 text-center">
                No stations found
              </div>
            )}
          </div>
        )}
      </div>

      {/* Current Selection */}
      <div className="mt-4 p-3 bg-white/20 rounded-lg border border-white/30">
        <div className="text-orange-200 text-sm mb-1">Currently Selected:</div>
        <div className="text-white font-bold text-lg">{selectedStation}</div>
      </div>

      {/* Quick Selection Buttons */}
      <div className="mt-4">
        <div className="text-orange-200 text-sm mb-2">Quick Select:</div>
        <div className="flex flex-wrap gap-2">
          {['CST', 'Bandra', 'Andheri', 'Borivali', 'Virar'].map((station) => (
            <button
              key={station}
              onClick={() => handleStationSelect(station)}
              className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
                station === selectedStation
                  ? 'bg-white text-purple-900'
                  : 'bg-white/20 text-white hover:bg-white/30'
              }`}
            >
              {station}
            </button>
          ))}
        </div>
      </div>

      {/* Close dropdown when clicking outside */}
      {isDropdownOpen && (
        <div
          className="fixed inset-0 z-0"
          onClick={() => setIsDropdownOpen(false)}
        />
      )}
    </div>
  );
};

export default StationSelector;