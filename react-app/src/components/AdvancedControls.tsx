'use client';

interface Train {
  id: string;
  name: string;
  line: string;
  current: string;
  next: string;
  delay: number;
  status: string;
  passengers: number;
}

interface AdvancedControlsProps {
  selectedTrain: string | null;
  trains: Train[];
  onSelectTrain: (trainId: string) => void;
  onQuickAction: (action: string, trainId: string) => void;
  trackingSpeed: number;
  trackingPaused: boolean;
  onSpeedChange: (speed: number) => void;
  onTogglePause: (paused: boolean) => void;
}

const AdvancedControls = ({
  selectedTrain,
  trains,
  onSelectTrain,
  onQuickAction,
  trackingSpeed,
  trackingPaused,
  onSpeedChange,
  onTogglePause
}: AdvancedControlsProps) => {

  const speedOptions = [
    { value: 500, label: '0.5s (Very Fast)' },
    { value: 1000, label: '1s (Fast)' },
    { value: 2000, label: '2s (Normal)' },
    { value: 5000, label: '5s (Slow)' }
  ];

  const quickActions = [
    { 
      id: 'hold', 
      label: 'Hold 2min', 
      description: '+3min delay',
      color: 'bg-yellow-500 hover:bg-yellow-600',
      icon: '⏸️'
    },
    { 
      id: 'swap', 
      label: 'Swap Platform', 
      description: 'saves 2min',
      color: 'bg-blue-500 hover:bg-blue-600',
      icon: '🔄'
    },
    { 
      id: 'reroute', 
      label: 'Loop Reroute', 
      description: '+8min',
      color: 'bg-red-500 hover:bg-red-600',
      icon: '🔀'
    }
  ];

  // Get high priority trains (delayed or critical)
  const priorityTrains = trains
    .filter(train => train.status === 'Delayed' || train.status === 'Critical')
    .sort((a, b) => b.delay - a.delay)
    .slice(0, 5);

  const conflictTrains = trains
    .filter(train => train.delay > 10 || train.passengers > 1500)
    .slice(0, 3);

  return (
    <div className="space-y-3">
      {/* Advanced Train Tracking Controls */}
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4">
        <h3 className="text-lg font-bold text-white mb-3">🎛️ Advanced Controls</h3>
        
        {/* Tracking Speed Control */}
        <div className="mb-3">
          <label className="block text-xs text-orange-200 mb-1">Update Speed</label>
          <select
            value={trackingSpeed}
            onChange={(e) => onSpeedChange(Number(e.target.value))}
            className="w-full px-2 py-1 bg-white/20 text-white rounded text-xs border border-white/30 focus:border-orange-300 focus:outline-none"
          >
            {speedOptions.map(option => (
              <option key={option.value} value={option.value} className="text-gray-800">
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Pause/Resume Button */}
        <button
          onClick={() => onTogglePause(!trackingPaused)}
          style={{ 
            backgroundColor: trackingPaused ? '#10B981' : '#F78D60'
          }}
          className="w-full py-2 px-3 rounded-lg font-medium text-white text-sm transition-all hover:opacity-90"
        >
          {trackingPaused ? '▶️ Resume' : '⏸️ Pause'}
        </button>
      </div>

      {/* Junction Priority Management */}
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4">
        <h3 className="text-lg font-bold text-white mb-3">🚦 Priority Trains</h3>
        
        {priorityTrains.length > 0 ? (
          <div className="space-y-2">
            {priorityTrains.slice(0, 3).map(train => (
              <div 
                key={train.id}
                className={`bg-white/20 rounded p-2 cursor-pointer transition-all text-xs ${
                  selectedTrain === train.id ? 'ring-1 ring-blue-400 bg-white/30' : 'hover:bg-white/25'
                }`}
                onClick={() => onSelectTrain(train.id)}
              >
                <div className="flex justify-between items-center">
                  <div>
                    <div className="font-semibold text-white">{train.id}</div>
                    <div className="text-orange-200">{train.current} → {train.next}</div>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold ${
                      train.status === 'Critical' ? 'text-red-300' : 'text-yellow-300'
                    }`}>
                      +{train.delay.toFixed(1)}m
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center text-orange-200 py-3">
            <div className="text-lg mb-1">✅</div>
            <div className="text-xs">No priority issues</div>
          </div>
        )}
      </div>

      {/* Quick Actions Panel */}
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4">
        <h3 className="text-lg font-bold text-white mb-3">⚡ Quick Actions</h3>
        
        {selectedTrain ? (
          <div>
            <div className="mb-2 text-center">
              <div className="text-orange-200 text-xs">Selected:</div>
              <div className="text-white font-bold text-sm">{selectedTrain}</div>
            </div>
            
            <div className="space-y-1">
              {quickActions.map(action => (
                <button
                  key={action.id}
                  onClick={() => onQuickAction(action.id, selectedTrain)}
                  style={{ backgroundColor: action.id === 'hold' ? '#F59E0B' : action.id === 'swap' ? '#3B82F6' : '#EF4444' }}
                  className="w-full p-2 rounded text-white font-medium text-xs transition-all hover:opacity-90"
                >
                  <div className="flex items-center justify-between">
                    <span>{action.icon} {action.label}</span>
                    <span className="opacity-80">({action.description})</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center text-orange-200 py-3">
            <div className="text-lg mb-1">👆</div>
            <div className="text-xs">Select a train above</div>
          </div>
        )}
      </div>

      {/* System Status */}
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4">
        <h3 className="text-lg font-bold text-white mb-3">📡 System Status</h3>
        
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-orange-200">Tracking:</span>
            <span className="text-white font-medium">
              {trackingPaused ? '⏸️ Paused' : '▶️ Active'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-orange-200">Update:</span>
            <span className="text-white font-medium">{trackingSpeed}ms</span>
          </div>
          <div className="flex justify-between">
            <span className="text-orange-200">Trains:</span>
            <span className="text-white font-medium">{trains.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-orange-200">Priority:</span>
            <span className="text-white font-medium">{priorityTrains.length}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-orange-200">Conflicts:</span>
            <span className="text-white font-medium">{conflictTrains.length}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedControls;