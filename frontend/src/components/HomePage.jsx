import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { axiosInstance } from '../lib/axios';
import SourceDestination from './homepagecomponents/SourceDestination.jsx';
import logo from '../assets/logo.png';

const HomePage = () => {
  const mapRef = useRef(null);
  const [ports, setPorts] = useState([]);
  const [selectedSourcePort, setSelectedSourcePort] = useState(null);
  const [selectedDestPort, setSelectedDestPort] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const sourceRippleRef = useRef(null);
  const destRippleRef = useRef(null);
  const pathLayerRef = useRef(null);

  const createRippleEffect = (lat, lng, color) => {
    const ripple = L.circle([lat, lng], {
      color: color,
      fillColor: color,
      fillOpacity: 0.3,
      radius: 50000,
      weight: 3
    }).addTo(mapRef.current);

    let currentRadius = 50000;
    const maxRadius = 200000;
    const step = 5000;
    
    const animate = () => {
      currentRadius += step;
      if (currentRadius <= maxRadius) {
        ripple.setRadius(currentRadius);
        ripple.setStyle({
          fillOpacity: 0.3 - (currentRadius - 50000) / (maxRadius - 50000) * 0.3,
          opacity: 1 - (currentRadius - 50000) / (maxRadius - 50000) * 0.5
        });
        setTimeout(animate, 100);
      } else {
        currentRadius = 50000;
        setTimeout(animate, 100);
      }
    };
    
    animate();
    return ripple;
  };

  const animatePath = (pathCoordinates) => {
    if (pathLayerRef.current) {
      mapRef.current.removeLayer(pathLayerRef.current);
    }

    const bounds = L.latLngBounds(pathCoordinates);
    mapRef.current.fitBounds(bounds, { padding: [50, 50] });

    let animatedCoordinates = [];
    let currentIndex = 0;

    const addNextPoint = () => {
      if (currentIndex < pathCoordinates.length) {
        const step = Math.ceil(pathCoordinates.length / 200);
        for (let i = 0; i < step && currentIndex < pathCoordinates.length; i++) {
          animatedCoordinates.push(pathCoordinates[currentIndex]);
          currentIndex++;
        }
        
        if (pathLayerRef.current) {
          mapRef.current.removeLayer(pathLayerRef.current);
        }
        
        pathLayerRef.current = L.polyline(animatedCoordinates, {
          color: '#0F172A',
          weight: 4,
          opacity: 0.9,
          lineCap: 'round',
          lineJoin: 'round',
          dashArray: '10, 5',
          className: 'shipping-route'
        }).addTo(mapRef.current);

        const shadowLine = L.polyline(animatedCoordinates, {
          color: '#1E40AF',
          weight: 6,
          opacity: 0.3,
          lineCap: 'round',
          lineJoin: 'round'
        }).addTo(mapRef.current);
        shadowLine.bringToBack();
        
        if (currentIndex < pathCoordinates.length) {
          requestAnimationFrame(addNextPoint);
        }
      }
    };

    addNextPoint();
  };
  
  const fetchAndDrawPath = async (sourcePort, destPort) => {
    if (!sourcePort || !destPort || !sourcePort.code || !destPort.code) {
      return;
    }

    setIsLoading(true);
    try {
      const response = await axiosInstance.post(
        `/path/${sourcePort.code}/${destPort.code}/find-path`
      );
      
      if (response.data && response.data.path && Array.isArray(response.data.path)) {
        const pathCoordinates = response.data.path.map(point => [point[0], point[1]]);
        
        if (pathCoordinates.length > 0) {
          animatePath(pathCoordinates);
        }
      }
    } catch (error) {
      
    } finally {
      setIsLoading(false);
    }
  };

  const handlePortSelection = (type, port) => {
    if (port && port.latitude && port.longitude) {
      if (type === 'source') {
        if (sourceRippleRef.current) {
          mapRef.current.removeLayer(sourceRippleRef.current);
        }
        setSelectedSourcePort(port);
        sourceRippleRef.current = createRippleEffect(
          port.latitude, 
          port.longitude, 
          '#10B981'
        );
      } else if (type === 'destination') {
        if (destRippleRef.current) {
          mapRef.current.removeLayer(destRippleRef.current);
        }
        setSelectedDestPort(port);
        destRippleRef.current = createRippleEffect(
          port.latitude, 
          port.longitude, 
          '#EF4444'
        );
      }
    }
  };
  
  useEffect(() => {
    if (mapRef.current) return;
    
    mapRef.current = L.map('map', {
      center: [20, 10],
      zoom: 3,
      minZoom: 2,
      maxZoom: 10,
      worldCopyJump: true,
    });
    
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles &copy; Esri'
    }).addTo(mapRef.current);
    
    const markerOptions = {
      radius: 4,
      fillColor: "#ff7800",
      color: "#000",
      weight: 1,
      opacity: 1,
      fillOpacity: 0.8
    };
    
    const fetchAndDisplayPorts = async () => {
      try {
        const response = await axiosInstance.get('/port/display-ports');
        const fetchedPorts = response.data;
        
        fetchedPorts.forEach(port => {
          if (port.latitude && port.longitude && port.portName) {
            L.circleMarker([port.latitude, port.longitude], markerOptions)
              .addTo(mapRef.current)
              .bindTooltip(`${port.portName}<br/><small>${port.countryName || ''}</small>`, {
                permanent: false,
                direction: 'top',
                offset: [0, -8],
                className: 'port-tooltip'
              });
          }
        });
        
        setPorts(fetchedPorts);
      } catch (error) {
        
      }
    };
    
    fetchAndDisplayPorts();
   
    return () => {
      if (mapRef.current) {
        if (sourceRippleRef.current) {
          mapRef.current.removeLayer(sourceRippleRef.current);
        }
        if (destRippleRef.current) {
          mapRef.current.removeLayer(destRippleRef.current);
        }
        if (pathLayerRef.current) {
          mapRef.current.removeLayer(pathLayerRef.current);
        }
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);
  
  return (
    <div className="relative h-screen w-full bg-gray-900">
      <style jsx>{`
        .port-tooltip {
          background-color: rgba(17, 24, 39, 0.95) !important;
          border: 1px solid #374151 !important;
          border-radius: 6px !important;
          color: white !important;
          font-size: 12px !important;
          font-weight: 500 !important;
          padding: 6px 8px !important;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
        }
        .port-tooltip::before {
          border-top-color: #374151 !important;
        }
        .shipping-route {
          filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
        }
      `}</style>
      
      <div id="map" className="h-full w-full" />
      
      <div className="fixed bottom-4 left-4 z-[2000] flex items-center space-x-3">
        <img src={logo} alt="Logo" className="h-10 w-10" />
        <span className="text-black font-bold text-2xl">POSEIDON</span>
      </div>
      
      <SourceDestination 
        onPortSelection={handlePortSelection} 
        onFindRoute={fetchAndDrawPath}
        ports={ports}
      />
      
      {isLoading && (
        <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-[2000]">
          <div className="bg-gray-800 rounded-lg p-3 flex items-center space-x-3 shadow-lg border border-gray-600">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            <span className="text-white font-medium text-sm">Finding route...</span>
          </div>
        </div>
      )}
      
      {selectedSourcePort && (
        <div className="fixed top-4 left-4 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg z-[1000] border border-gray-600">
          <div className="text-xs text-gray-400">Source</div>
          <div className="font-medium">{selectedSourcePort.portName}</div>
          <div className="text-xs text-gray-300">{selectedSourcePort.countryName}</div>
        </div>
      )}
      
      {selectedDestPort && (
        <div className="fixed top-4 right-4 bg-gray-800 text-white px-4 py-2 rounded-lg shadow-lg z-[1000] border border-gray-600">
          <div className="text-xs text-gray-400">Destination</div>
          <div className="font-medium">{selectedDestPort.portName}</div>
          <div className="text-xs text-gray-300">{selectedDestPort.countryName}</div>
        </div>
      )}
    </div>
  );
};

export default HomePage;