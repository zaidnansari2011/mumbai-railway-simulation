'use client';

interface LiveDemoControlsProps {
  isLiveDemo: boolean;
  demoSpeed: number;
  onToggleDemo: (enabled: boolean) => void;
  onSpeedChange: (speed: number) => void;
}

const LiveDemoControls = ({ 
  isLiveDemo, 
  demoSpeed, 
  onToggleDemo, 
  onSpeedChange 
}: LiveDemoControlsProps) => {
  const speedOptions = [
    { value: 0.5, label: '0.5x (Slow)' },
    { value: 1, label: '1x (Normal)' },
    { value: 2, label: '2x (Fast)' },
    { value: 4, label: '4x (Very Fast)' }
  ];

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4">🎮 Live Demo Controls</h3>
      
      {/* Demo Toggle */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-white font-semibold mb-1">Live Simulation</h4>
            <p className="text-orange-200 text-sm">
              {isLiveDemo ? 'Trains are moving in real-time' : 'Static train positions'}
            </p>
          </div>
          <button
            onClick={() => onToggleDemo(!isLiveDemo)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              isLiveDemo ? 'bg-green-500' : 'bg-gray-600'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                isLiveDemo ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      {/* Speed Control */}
      <div className={`transition-opacity duration-300 ${isLiveDemo ? 'opacity-100' : 'opacity-50'}`}>
        <h4 className="text-white font-semibold mb-3">Simulation Speed</h4>
        <div className="space-y-2">
          {speedOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => onSpeedChange(option.value)}
              disabled={!isLiveDemo}
              className={`w-full text-left px-3 py-2 rounded-lg transition-all ${
                demoSpeed === option.value && isLiveDemo
                  ? 'bg-white text-purple-900 font-semibold'
                  : 'bg-white/20 text-white hover:bg-white/30'
              } ${!isLiveDemo ? 'cursor-not-allowed' : 'cursor-pointer'}`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Status Indicator */}
      <div className="mt-6 p-3 bg-white/20 rounded-lg border border-white/30">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${isLiveDemo ? 'bg-green-500 status-pulse' : 'bg-gray-500'}`}></div>
          <span className="text-white font-medium">
            {isLiveDemo ? `Live Demo Active (${demoSpeed}x speed)` : 'Demo Paused'}
          </span>
        </div>
      </div>

      {/* Demo Features */}
      <div className="mt-4">
        <h5 className="text-orange-200 text-sm mb-2">Demo Features:</h5>
        <ul className="text-white text-sm space-y-1">
          <li className="flex items-center gap-2">
            <span className={isLiveDemo ? 'text-green-400' : 'text-gray-400'}>•</span>
            Real-time train movement
          </li>
          <li className="flex items-center gap-2">
            <span className={isLiveDemo ? 'text-green-400' : 'text-gray-400'}>•</span>
            Dynamic delay simulation
          </li>
          <li className="flex items-center gap-2">
            <span className={isLiveDemo ? 'text-green-400' : 'text-gray-400'}>•</span>
            Station updates
          </li>
          <li className="flex items-center gap-2">
            <span className={isLiveDemo ? 'text-green-400' : 'text-gray-400'}>•</span>
            Status changes
          </li>
        </ul>
      </div>
    </div>
  );
};

export default LiveDemoControls;