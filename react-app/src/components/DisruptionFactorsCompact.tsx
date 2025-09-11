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

const DisruptionFactorsCompact = ({ factors, onAddFactor }: DisruptionFactorsProps) => {
  
  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-lg p-5">
      <h3 className="text-xl font-bold text-white mb-4">⚠️ Mumbai Railway Disruption Factors</h3>
      
      {/* Phase 1 Factors */}
      <div className="mb-5">
        <h4 className="text-lg font-semibold text-orange-200 mb-3 flex items-center gap-2">
          📊 Phase 1: Core Disruption Factors
          <span className="text-xs bg-orange-500 text-white px-2 py-1 rounded">ACTIVE</span>
        </h4>
        
        <div className="space-y-4">
          {/* Rush Hour */}
          <div className="bg-white/20 rounded-lg p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-white">🕐 Rush Hour Surge</span>
              <button
                onClick={() => onAddFactor('rushHour')}
                style={{ backgroundColor: '#F78D60' }}
                className="px-3 py-2 rounded-lg text-sm font-bold text-white hover:opacity-90 transition-all"
              >
                Add +1 Level
              </button>
            </div>
            <div className="flex items-center gap-3 mb-2">
              <div className="flex-1 bg-gray-600 rounded-full h-3">
                <div 
                  className="h-3 rounded-full transition-all"
                  style={{ 
                    width: `${(factors.rushHour / 5) * 100}%`,
                    backgroundColor: factors.rushHour > 3 ? '#EF4444' : factors.rushHour > 1 ? '#F59E0B' : '#10B981'
                  }}
                ></div>
              </div>
              <span className="text-white font-bold text-lg">{factors.rushHour}/5</span>
            </div>
            <div className="text-xs text-orange-200 bg-black/20 rounded p-2">
              <strong>Current Impact:</strong> {factors.rushHour === 0 ? 'Normal passenger volume (800-1200 passengers/train)' :
               factors.rushHour <= 2 ? 'Moderate overcrowding - Extended boarding time (+2min delay)' :
               factors.rushHour <= 4 ? 'Severe crowding - Platform congestion (+5min delay, safety concerns)' :
               'Critical congestion - Emergency protocols activated (+10min delay)'}
            </div>
            <div className="text-xs text-gray-300 mt-1">
              💡 <strong>Real Data:</strong> Mumbai trains carry 4,500+ passengers during peak hours (150% capacity)
            </div>
          </div>

          {/* Weather */}
          <div className="bg-white/20 rounded-lg p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-white">🌧️ Weather Disruption</span>
              <button
                onClick={() => onAddFactor('weather')}
                style={{ backgroundColor: '#3B82F6' }}
                className="px-3 py-2 rounded-lg text-sm font-bold text-white hover:opacity-90 transition-all"
              >
                Add +1 Level
              </button>
            </div>
            <div className="flex items-center gap-3 mb-2">
              <div className="flex-1 bg-gray-600 rounded-full h-3">
                <div 
                  className="h-3 rounded-full transition-all"
                  style={{ 
                    width: `${(factors.weather / 5) * 100}%`,
                    backgroundColor: factors.weather > 3 ? '#EF4444' : factors.weather > 1 ? '#F59E0B' : '#10B981'
                  }}
                ></div>
              </div>
              <span className="text-white font-bold text-lg">{factors.weather}/5</span>
            </div>
            <div className="text-xs text-orange-200 bg-black/20 rounded p-2">
              <strong>Current Impact:</strong> {factors.weather === 0 ? 'Clear weather - Normal speed operation (65-80 km/h)' :
               factors.weather <= 2 ? 'Light rain - Reduced visibility, cautious driving (+3min delay)' :
               factors.weather <= 4 ? 'Heavy monsoon - Flooding risk, speed restrictions (+8min delay)' :
               'Extreme weather - Service suspension in affected areas (+25min delay)'}
            </div>
            <div className="text-xs text-gray-300 mt-1">
              💡 <strong>Real Data:</strong> Mumbai receives 2,400mm annual rainfall, causing 150+ service disruptions
            </div>
          </div>
        </div>
      </div>

      {/* Phase 2 Factors */}
      <div>
        <h4 className="text-lg font-semibold text-orange-200 mb-3 flex items-center gap-2">
          🔥 Phase 2: Advanced Operational Factors
          <span className="text-xs bg-purple-500 text-white px-2 py-1 rounded">ENHANCED</span>
        </h4>
        
        <div className="space-y-3">
          {/* Junction Congestion */}
          <div className="bg-white/20 rounded-lg p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-white">🚦 Junction Bottleneck (Dadar/Kurla)</span>
              <button
                onClick={() => onAddFactor('junctionCongestion')}
                style={{ backgroundColor: '#0D1164' }}
                className="px-2 py-1 rounded font-bold text-white hover:opacity-90 text-xs"
              >
                +1
              </button>
            </div>
            <div className="flex items-center gap-2 mb-1">
              <div className="flex-1 bg-gray-600 rounded-full h-2">
                <div 
                  className="h-2 rounded-full"
                  style={{ 
                    width: `${(factors.junctionCongestion / 5) * 100}%`,
                    backgroundColor: '#F78D60'
                  }}
                ></div>
              </div>
              <span className="text-white text-sm">{factors.junctionCongestion}/5</span>
            </div>
            <div className="text-xs text-orange-200">
              Impact: +{factors.junctionCongestion * 2.5}min delay per train • Affects 42 trains/hour at Dadar
            </div>
          </div>

          {/* Equipment */}
          <div className="bg-white/20 rounded-lg p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-white">⚙️ Equipment Failure (EMU/Signal)</span>
              <button
                onClick={() => onAddFactor('equipmentReliability')}
                style={{ backgroundColor: '#0D1164' }}
                className="px-2 py-1 rounded font-bold text-white hover:opacity-90 text-xs"
              >
                +1
              </button>
            </div>
            <div className="flex items-center gap-2 mb-1">
              <div className="flex-1 bg-gray-600 rounded-full h-2">
                <div 
                  className="h-2 rounded-full"
                  style={{ 
                    width: `${(factors.equipmentReliability / 5) * 100}%`,
                    backgroundColor: '#EF4444'
                  }}
                ></div>
              </div>
              <span className="text-white text-sm">{factors.equipmentReliability}/5</span>
            </div>
            <div className="text-xs text-orange-200">
              60% of Mumbai's EMU fleet is 20+ years old • +{factors.equipmentReliability * 4}min delay
            </div>
          </div>

          {/* Festival Crowds */}
          <div className="bg-white/20 rounded-lg p-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-white">🎉 Festival Crowds (Ganpati/Navratri)</span>
              <button
                onClick={() => onAddFactor('festivalCrowds')}
                style={{ backgroundColor: '#0D1164' }}
                className="px-2 py-1 rounded font-bold text-white hover:opacity-90 text-xs"
              >
                +1
              </button>
            </div>
            <div className="flex items-center gap-2 mb-1">
              <div className="flex-1 bg-gray-600 rounded-full h-2">
                <div 
                  className="h-2 rounded-full"
                  style={{ 
                    width: `${(factors.festivalCrowds / 5) * 100}%`,
                    backgroundColor: '#8B5CF6'
                  }}
                ></div>
              </div>
              <span className="text-white text-sm">{factors.festivalCrowds}/5</span>
            </div>
            <div className="text-xs text-orange-200">
              Festival seasons: 200-300% passenger increase • Extended station stops
            </div>
          </div>
        </div>
      </div>

      {/* Total Impact Summary */}
      <div className="mt-4 bg-gradient-to-r from-red-500/20 to-orange-500/20 rounded-lg p-3 border border-red-400/30">
        <div className="text-center">
          <div className="text-sm font-bold text-white mb-1">📊 Total System Impact</div>
          <div className="text-lg font-bold text-orange-200">
            +{((factors.rushHour + factors.weather + factors.junctionCongestion + factors.equipmentReliability + factors.festivalCrowds) * 1.5).toFixed(1)} min average delay
          </div>
          <div className="text-xs text-gray-300 mt-1">
            Compound effect of all active disruption factors
          </div>
        </div>
      </div>
    </div>
  );
};

export default DisruptionFactorsCompact;