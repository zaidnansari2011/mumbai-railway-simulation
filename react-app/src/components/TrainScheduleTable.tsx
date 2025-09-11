'use client';

interface Train {
  id: string;
  name: string;
  line: string;
  current: string;
  next: string;
  eta: Date;
  passengers: number;
  delay: number;
  status: string;
}

interface TrainScheduleTableProps {
  trains: Train[];
}

const TrainScheduleTable = ({ trains }: TrainScheduleTableProps) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'On Time':
        return 'text-green-600';
      case 'Delayed':
        return 'text-yellow-600';
      case 'Critical':
        return 'text-red-600';
      case 'Running':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  const getLineColor = (line: string) => {
    switch (line) {
      case 'Western':
        return 'border-l-orange-500 bg-orange-50';
      case 'Central Main':
        return 'border-l-teal-400 bg-teal-50';
      case 'Trans-Harbour':
        return 'border-l-green-400 bg-green-50';
      default:
        return 'border-l-gray-400 bg-gray-50';
    }
  };

  const getLineIcon = (line: string) => {
    switch (line) {
      case 'Western':
        return '🟠';
      case 'Central Main':
        return '🔵';
      case 'Trans-Harbour':
        return '🟢';
      default:
        return '⚪';
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-IN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const sortedTrains = [...trains].sort((a, b) => {
    // First sort by line, then by train ID
    if (a.line !== b.line) {
      return a.line.localeCompare(b.line);
    }
    return a.id.localeCompare(b.id);
  });

  if (trains.length === 0) {
    return (
      <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6">
        <h3 className="text-xl font-bold text-white mb-4">📋 Live Train Schedule</h3>
        <div className="bg-white rounded-lg overflow-hidden">
          <div className="p-8 text-center text-gray-500">
            <div className="text-4xl mb-3">🚂</div>
            <div className="font-bold text-lg mb-2">No trains currently running</div>
            <div className="text-sm">Start simulation to see live data</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-lg p-6">
      <h3 className="text-xl font-bold text-white mb-4">📋 Live Train Schedule</h3>
      
      <div className="bg-white rounded-lg overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
              <tr>
                <th className="px-4 py-3 text-left font-semibold">Train ID</th>
                <th className="px-4 py-3 text-left font-semibold">Line</th>
                <th className="px-4 py-3 text-left font-semibold">Current Station</th>
                <th className="px-4 py-3 text-left font-semibold">Next Station</th>
                <th className="px-4 py-3 text-left font-semibold">ETA</th>
                <th className="px-4 py-3 text-left font-semibold">Passengers</th>
                <th className="px-4 py-3 text-left font-semibold">Delay</th>
                <th className="px-4 py-3 text-left font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {sortedTrains.map((train, index) => (
                <tr 
                  key={train.id}
                  className={`${getLineColor(train.line)} border-l-4 hover:bg-gray-100 transition-colors ${
                    index % 2 === 0 ? 'bg-gray-50' : 'bg-white'
                  }`}
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span>{getLineIcon(train.line)}</span>
                      <span className="font-mono font-semibold text-gray-800">{train.id}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm font-medium text-gray-700">{train.line}</span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="font-medium text-gray-800">{train.current}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="text-gray-600">→</span>
                      <span className="font-medium text-gray-800">{train.next}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="text-sm font-mono text-gray-700">
                      {formatTime(train.eta)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">👥</span>
                      <span className="font-medium text-gray-800">
                        {train.passengers.toLocaleString()}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span 
                      className={`font-medium ${
                        train.delay > 5 ? 'text-red-600' : 
                        train.delay > 2 ? 'text-yellow-600' : 
                        'text-green-600'
                      }`}
                    >
                      {train.delay > 0 ? `+${train.delay.toFixed(1)}m` : '0m'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(train.status)}`}>
                      <span className="mr-1">
                        {train.status === 'On Time' && '🟢'}
                        {train.status === 'Delayed' && '🟡'}
                        {train.status === 'Critical' && '🔴'}
                        {train.status === 'Running' && '🔵'}
                      </span>
                      {train.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Table Summary */}
        <div className="bg-gray-100 px-4 py-3 border-t">
          <div className="flex flex-wrap gap-4 text-sm text-gray-600">
            <span>
              <strong>Total Trains:</strong> {trains.length}
            </span>
            <span>
              <strong>On Time:</strong> {trains.filter(t => t.status === 'On Time').length}
            </span>
            <span>
              <strong>Delayed:</strong> {trains.filter(t => t.status === 'Delayed').length}
            </span>
            <span>
              <strong>Critical:</strong> {trains.filter(t => t.status === 'Critical').length}
            </span>
            <span>
              <strong>Total Passengers:</strong> {trains.reduce((sum, t) => sum + t.passengers, 0).toLocaleString()}
            </span>
          </div>
        </div>
      </div>
      
      {/* Live Update Indicator */}
      <div className="mt-3 text-center">
        <div className="inline-flex items-center gap-2 text-sm text-orange-200">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span>Live updates every 2 seconds</span>
        </div>
      </div>
    </div>
  );
};

export default TrainScheduleTable;