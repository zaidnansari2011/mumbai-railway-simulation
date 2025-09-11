'use client';

interface AIOptimizationSuiteProps {
  aiActive: boolean;
  aiDecisions: number;
  aiPreventedDelays: number;
  aiOptimizations: number;
  aiPerformance: number;
  aiDecisionLog: string[];
  onToggleAI: () => void;
}

const AIOptimizationSuite = ({
  aiActive,
  aiDecisions,
  aiPreventedDelays,
  aiOptimizations,
  aiPerformance,
  aiDecisionLog,
  onToggleAI
}: AIOptimizationSuiteProps) => {
  
  const demonstrateAIOptimization = () => {
    // This would trigger a demo of AI optimization
    console.log('AI Demo triggered');
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-lg p-4 text-white shadow-xl">
      <h3 className="text-lg font-bold mb-3 text-center">
        🧠 AI OPTIMIZATION SUITE
      </h3>
      
      {/* AI Status Display */}
      <div className="bg-white/15 backdrop-blur-lg rounded-lg p-3 mb-3">
        <div className="flex justify-between items-center mb-2">
          <div>
            <h4 className="text-sm font-semibold">🤖 AI Status</h4>
            <div className="text-xs opacity-90">
              {aiActive ? 'Active' : 'Standby'}
            </div>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-white">+{aiPerformance.toFixed(1)}%</div>
            <div className="text-xs opacity-80">Efficiency</div>
          </div>
        </div>
        
        {/* AI Metrics Dashboard */}
        <div className="grid grid-cols-3 gap-2 text-xs">
          <div className="text-center">
            <div className="font-bold">{aiDecisions}</div>
            <div className="opacity-80">Decisions</div>
          </div>
          <div className="text-center">
            <div className="font-bold">{aiPreventedDelays}</div>
            <div className="opacity-80">Prevented</div>
          </div>
          <div className="text-center">
            <div className="font-bold">{aiOptimizations}</div>
            <div className="opacity-80">Optimized</div>
          </div>
        </div>
      </div>
      
      {/* AI Control Buttons */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <button
          onClick={onToggleAI}
          style={{ backgroundColor: aiActive ? '#6B7280' : '#3B82F6' }}
          className={`p-2 rounded-lg font-bold text-xs transition-all ${
            aiActive 
              ? 'cursor-not-allowed opacity-50' 
              : 'hover:opacity-90'
          }`}
          disabled={aiActive}
        >
          🚀 ACTIVATE
        </button>
        <button
          onClick={onToggleAI}
          style={{ backgroundColor: !aiActive ? '#6B7280' : '#EF4444' }}
          className={`p-2 rounded-lg font-bold text-xs transition-all ${
            !aiActive 
              ? 'cursor-not-allowed opacity-50' 
              : 'hover:opacity-90'
          }`}
          disabled={!aiActive}
        >
          ⏹️ STOP
        </button>
      </div>
      
      {/* AI Decision Log */}
      <div style={{ backgroundColor: '#0D1164' }} className="rounded-lg p-3 max-h-20 overflow-y-auto">
        <h4 className="font-semibold mb-1 text-xs opacity-90">🤖 AI Log</h4>
        <div className="text-xs font-mono space-y-1">
          {aiDecisionLog.slice(0, 3).map((log, index) => (
            <div 
              key={index}
              className={`${
                log.includes('[SYSTEM]') ? 'text-green-300' :
                log.includes('[AI]') ? 'text-blue-300' :
                log.includes('[ACTION]') ? 'text-yellow-300' :
                'text-gray-300'
              }`}
            >
              {log}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AIOptimizationSuite;