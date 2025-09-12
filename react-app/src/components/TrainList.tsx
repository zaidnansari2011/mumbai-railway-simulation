'use client';

import { useState } from 'react';

interface Train {
  id: string;
  name: string;
  status: 'Running' | 'Delayed' | 'On Time' | 'Cancelled' | 'Critical';
  route: string;
  currentStation: string;
  nextStation: string;
  estimatedTime: string;
  delay: number;
}

interface TrainListProps {
  trains: Train[];
}

const TrainList = ({ trains }: TrainListProps) => {
  const [sortBy, setSortBy] = useState<'name' | 'status' | 'time'>('time');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'On Time':
        return 'bg-green-500';
      case 'Delayed':
        return 'bg-yellow-500';
      case 'Critical':
        return 'bg-red-500';
      case 'Running':
        return 'bg-blue-500';
      case 'Cancelled':
        return 'bg-gray-500';
      default:
        return 'bg-gray-400';
    }
  };

  const sortedTrains = [...trains].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'status':
        return a.status.localeCompare(b.status);
      case 'time':
        return parseInt(a.estimatedTime) - parseInt(b.estimatedTime);
      default:
        return 0;
    }
  });

  if (trains.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-6xl mb-4">🚂</div>
        <h3 className="text-xl font-semibold text-white mb-2">No trains currently at this station</h3>
        <p className="text-orange-200">Select a different station or wait for trains to arrive</p>
      </div>
    );
  }

  return (
    <div>
      {/* Sort Controls */}
      <div className="flex flex-wrap gap-2 mb-6">
        <span className="text-white font-medium mr-4">Sort by:</span>
        {[
          { key: 'time', label: 'Arrival Time' },
          { key: 'name', label: 'Train Name' },
          { key: 'status', label: 'Status' }
        ].map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setSortBy(key as 'name' | 'status' | 'time')}
            className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
              sortBy === key
                ? 'bg-white text-purple-900'
                : 'bg-white/20 text-white hover:bg-white/30'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Train Cards */}
      <div className="grid gap-4">
        {sortedTrains.map((train) => (
          <div
            key={train.id}
            className="bg-white/15 backdrop-blur-sm rounded-lg p-4 hover:bg-white/20 transition-all duration-300 border border-white/10"
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-xl font-bold text-white">{train.name}</h3>
                  <span
                    className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium text-white ${getStatusColor(
                      train.status
                    )}`}
                  >
                    {train.status}
                    {train.delay > 0 && ` (+${train.delay}m)`}
                  </span>
                </div>
                <p className="text-orange-200 text-sm mb-1">{train.route}</p>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-white">
                    <strong>Current:</strong> {train.currentStation}
                  </span>
                  <span className="text-orange-200">→</span>
                  <span className="text-white">
                    <strong>Next:</strong> {train.nextStation}
                  </span>
                </div>
              </div>
              
              <div className="mt-4 md:mt-0 md:text-right">
                <div className="text-2xl font-bold text-white">{train.estimatedTime}</div>
                <div className="text-orange-200 text-sm">Estimated Arrival</div>
              </div>
            </div>
            
            {/* Progress Bar */}
            <div className="mt-4">
              <div className="w-full bg-white/20 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-1000 ${
                    train.status === 'Delayed' 
                      ? 'bg-gradient-to-r from-red-400 to-red-600' 
                      : 'bg-gradient-to-r from-green-400 to-green-600'
                  }`}
                  style={{ width: `${Math.random() * 70 + 20}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default TrainList;