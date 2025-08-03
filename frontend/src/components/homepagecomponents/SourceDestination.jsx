import { useState } from 'react';

const SourceDestination = ({ onPortSelection, onFindRoute, ports = [] }) => {
  const [sourceValue, setSourceValue] = useState('');
  const [destValue, setDestValue] = useState('');
  const [showSourceDropdown, setShowSourceDropdown] = useState(false);
  const [showDestDropdown, setShowDestDropdown] = useState(false);
  const [selectedSourcePort, setSelectedSourcePort] = useState(null);
  const [selectedDestPort, setSelectedDestPort] = useState(null);

  const filteredSourcePorts = ports.filter(port =>
    port.portName && port.portName.toLowerCase().includes(sourceValue.toLowerCase())
  );

  const filteredDestPorts = ports.filter(port =>
    port.portName && port.portName.toLowerCase().includes(destValue.toLowerCase())
  );

  const handleFindRoute = () => {
    if (selectedSourcePort && selectedDestPort) {
      onFindRoute && onFindRoute(selectedSourcePort, selectedDestPort);
    }
  };

  return (
    <div className="fixed bottom-4 left-4 right-4 sm:bottom-6 sm:left-1/2 sm:transform sm:-translate-x-1/2 bg-gray-900 rounded-xl shadow-2xl p-4 sm:p-6 sm:w-[600px] max-w-full z-[1000] border border-gray-700">
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 mb-4">
        <div className="flex-1 relative">
          <div className="flex items-center border border-gray-600 rounded-lg px-3 sm:px-4 py-2 sm:py-3 bg-gray-800 focus-within:border-blue-400 transition-colors">
            <svg className="w-4 h-4 sm:w-5 sm:h-5 text-gray-400 mr-2 sm:mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <input
              type="text"
              placeholder="Source Port"
              value={sourceValue}
              onChange={(e) => setSourceValue(e.target.value)}
              onFocus={() => setShowSourceDropdown(true)}
              onBlur={() => setTimeout(() => setShowSourceDropdown(false), 200)}
              className="flex-1 outline-none text-white bg-transparent placeholder-gray-400 text-sm min-w-0"
            />
          </div>
          {showSourceDropdown && sourceValue && filteredSourcePorts.length > 0 && (
            <div className="absolute top-full left-0 right-0 bg-gray-800 border border-gray-600 rounded-lg mt-1 max-h-40 sm:max-h-48 overflow-y-auto shadow-xl z-20">
              {filteredSourcePorts.slice(0, 10).map((port, index) => (
                <div
                  key={port._id || index}
                  className="px-3 sm:px-4 py-2 sm:py-3 hover:bg-gray-700 cursor-pointer text-white text-sm border-b border-gray-700 last:border-b-0 transition-colors"
                  onMouseDown={() => {
                    setSourceValue(port.portName);
                    setShowSourceDropdown(false);
                    setSelectedSourcePort(port);
                    onPortSelection && onPortSelection('source', port);
                  }}
                >
                  <div className="font-medium truncate">{port.portName}</div>
                  <div className="text-xs text-gray-400 truncate">{port.countryName}</div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex-1 relative">
          <div className="flex items-center border border-gray-600 rounded-lg px-3 sm:px-4 py-2 sm:py-3 bg-gray-800 focus-within:border-blue-400 transition-colors">
            <svg className="w-4 h-4 sm:w-5 sm:h-5 text-gray-400 mr-2 sm:mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
            <input
              type="text"
              placeholder="Destination Port"
              value={destValue}
              onChange={(e) => setDestValue(e.target.value)}
              onFocus={() => setShowDestDropdown(true)}
              onBlur={() => setTimeout(() => setShowDestDropdown(false), 200)}
              className="flex-1 outline-none text-white bg-transparent placeholder-gray-400 text-sm min-w-0"
            />
          </div>
          {showDestDropdown && destValue && filteredDestPorts.length > 0 && (
            <div className="absolute top-full left-0 right-0 bg-gray-800 border border-gray-600 rounded-lg mt-1 max-h-40 sm:max-h-48 overflow-y-auto shadow-xl z-20">
              {filteredDestPorts.slice(0, 10).map((port, index) => (
                <div
                  key={port._id || index}
                  className="px-3 sm:px-4 py-2 sm:py-3 hover:bg-gray-700 cursor-pointer text-white text-sm border-b border-gray-700 last:border-b-0 transition-colors"
                  onMouseDown={() => {
                    setDestValue(port.portName);
                    setShowDestDropdown(false);
                    setSelectedDestPort(port);
                    onPortSelection && onPortSelection('destination', port);
                  }}
                >
                  <div className="font-medium truncate">{port.portName}</div>
                  <div className="text-xs text-gray-400 truncate">{port.countryName}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <button 
        onClick={handleFindRoute}
        disabled={!selectedSourcePort || !selectedDestPort}
        className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed text-white py-2 sm:py-3 px-4 sm:px-6 rounded-lg transition-all duration-200 font-medium text-sm shadow-lg"
      >
        {selectedSourcePort && selectedDestPort ? 'Find Route' : 'Select Source and Destination'}
      </button>
    </div>
  );
};

export default SourceDestination;