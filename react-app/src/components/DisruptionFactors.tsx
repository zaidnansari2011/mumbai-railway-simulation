'use client';

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

interface DisruptionFactorsProps {
  factors: DisruptionFactors;
  onAddFactor: (factor: keyof DisruptionFactors) => void;
}

const DisruptionFactors = ({ factors, onAddFactor }: DisruptionFactorsProps) => {
  
  const getProgressPercentage = (value: number, max: number = 5) => {
    return (value / max) * 100;
  };

  const getFactorLevel = (value: number) => {
    if (value === 0) return { label: 'Normal', color: 'bg-green-500' };
    if (value <= 2) return { label: `Level ${value}`, color: 'bg-yellow-500' };
    if (value <= 4) return { label: `Level ${value}`, color: 'bg-orange-500' };
    return { label: `Level ${value}`, color: 'bg-red-500' };
  };

  const factorConfigs = [
    {
      key: 'rushHour' as keyof DisruptionFactors,
      title: '🚶‍♂️ Rush Hour Surge',
      description: 'Simulates peak hour passenger overcrowding. Increases passenger load by 50% per level and adds 1.5min delay per level.',
      impact: 'Mumbai rush hours see 120-150% capacity loads (4,000+ passengers per train)',
      buttonText: '🚶‍♂️ Add Rush Hour',
      color: 'bg-orange-500'
    },
    {
      key: 'weather' as keyof DisruptionFactors,
      title: '🌧️ Weather Disruption',
      description: 'Mumbai monsoon effects: Light rain (+3min), Heavy rain (+8min), Severe flooding (+25min).',
      impact: 'Mumbai receives 2,400mm annual rainfall, causing frequent service disruptions',
      buttonText: '🌧️ Add Rain Delay',
      color: 'bg-blue-500'
    },
    {
      key: 'junctionCongestion' as keyof DisruptionFactors,
      title: '🔗 Junction Bottleneck',
      description: 'Major junction congestion at Dadar (42 trains/hr), Kurla (36 trains/hr). Adds 2.5min delay per level.',
      impact: 'Dadar handles 700+ trains daily across 3 lines - critical bottleneck',
      buttonText: '🔗 Add Junction Issue',
      color: 'bg-red-500'
    },
    {
      key: 'equipmentReliability' as keyof DisruptionFactors,
      title: '⚙️ Equipment Failure',
      description: 'Train breakdowns, signal failures, overhead line issues. Based on Mumbai\'s 25-year old EMU fleet.',
      impact: '60% of Mumbai\'s EMU fleet is over 20 years old, causing frequent mechanical issues',
      buttonText: '⚙️ Trigger Failure',
      color: 'bg-yellow-600'
    },
    {
      key: 'festivalCrowds' as keyof DisruptionFactors,
      title: '🎭 Festival Surge',
      description: 'Ganpati, Navratri, cricket match crowds causing platform overcrowding and boarding delays.',
      impact: 'Festival seasons see 200-300% increase in passenger traffic',
      buttonText: '🎭 Add Festival Rush',
      color: 'bg-purple-500'
    },
    {
      key: 'platformStrain' as keyof DisruptionFactors,
      title: '🏗️ Platform Strain',
      description: 'Physical platform capacity exceeded, causing boarding delays and safety concerns.',
      impact: 'Many Mumbai platforms built for 1,000 passengers handle 4,000+ during peak hours',
      buttonText: '🏗️ Add Platform Issue',
      color: 'bg-indigo-500'
    }
  ];

  return (
    <div className="space-y-4">
      {/* Phase 1: Core Disruption Factors */}
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-5">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          📈 Phase 1: Core Disruption Factors
        </h3>
        
        <div className="space-y-4">
          {factorConfigs.slice(0, 2).map((config) => {
            const factorValue = factors[config.key];
            const level = getFactorLevel(factorValue);
            
            return (
              <div key={config.key} className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-800 flex items-center gap-2 mb-2">
                      {config.title}
                      <span className={`${level.color} text-white px-2 py-1 rounded-full text-xs`}>
                        {level.label}
                      </span>
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {config.description}
                    </p>
                    <div className="text-xs text-gray-500">
                      💡 <strong>Real Impact:</strong> {config.impact}
                    </div>
                  </div>
                  <button
                    onClick={() => onAddFactor(config.key)}
                    disabled={factorValue >= 5}
                    className={`ml-3 px-3 py-2 rounded-lg text-white font-medium text-sm transition-all ${
                      factorValue >= 5 
                        ? 'bg-gray-400 cursor-not-allowed' 
                        : `${config.color} hover:opacity-80`
                    }`}
                  >
                    {config.buttonText}
                  </button>
                </div>
                <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className={`${config.color} h-full transition-all duration-300`}
                    style={{ width: `${getProgressPercentage(factorValue)}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Phase 2: Advanced Operational Intelligence */}
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-5">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          🎯 Phase 2: Operational Intelligence Factors
          <span className="bg-purple-600 text-white px-2 py-1 rounded-full text-xs">AI OPTIMIZATION</span>
        </h3>
        
        <div className="space-y-4">
          {factorConfigs.slice(2).map((config) => {
            const factorValue = factors[config.key];
            const level = getFactorLevel(factorValue);
            
            return (
              <div key={config.key} className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-800 flex items-center gap-2 mb-2">
                      {config.title}
                      <span className={`${level.color} text-white px-2 py-1 rounded-full text-xs`}>
                        {level.label}
                      </span>
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {config.description}
                    </p>
                    <div className="text-xs text-gray-500">
                      💡 <strong>Real Impact:</strong> {config.impact}
                    </div>
                  </div>
                  <button
                    onClick={() => onAddFactor(config.key)}
                    disabled={factorValue >= 5}
                    className={`ml-3 px-3 py-2 rounded-lg text-white font-medium text-sm transition-all ${
                      factorValue >= 5 
                        ? 'bg-gray-400 cursor-not-allowed' 
                        : `${config.color} hover:opacity-80`
                    }`}
                  >
                    {config.buttonText}
                  </button>
                </div>
                <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div 
                    className={`${config.color} h-full transition-all duration-300`}
                    style={{ width: `${getProgressPercentage(factorValue)}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Summary Panel */}
      <div className="bg-white/15 backdrop-blur-lg rounded-lg p-4">
        <h4 className="font-bold text-white mb-3">📊 Disruption Summary</h4>
        <div className="grid grid-cols-2 gap-4 text-sm text-white">
          <div>
            <span className="opacity-80">Active Factors:</span>
            <span className="ml-2 font-bold">
              {Object.values(factors).filter(v => v > 0).length}
            </span>
          </div>
          <div>
            <span className="opacity-80">Total Impact:</span>
            <span className="ml-2 font-bold">
              {Object.values(factors).reduce((sum, val) => sum + val, 0)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DisruptionFactors;