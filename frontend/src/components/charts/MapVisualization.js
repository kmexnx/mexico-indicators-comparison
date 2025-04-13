import React, { useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

const MapWrapper = styled.div`
  width: 100%;
  height: 500px;
  margin-bottom: 2rem;

  .leaflet-container {
    height: 100%;
    width: 100%;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .city-marker {
    cursor: pointer;
  }
`;

const Legend = styled.div`
  position: absolute;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  background: white;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.4);
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 5px;
`;

const LegendColor = styled.div`
  width: 15px;
  height: 15px;
  border-radius: 50%;
  margin-right: 8px;
  background-color: ${(props) => props.color};
`;

const MapVisualization = ({ cities, selectedIndicator, indicatorData }) => {
  const { t } = useTranslation();
  const [selectedCity, setSelectedCity] = useState(null);
  const mexicoCenter = [23.6345, -102.5528]; // Mexico's center coordinates

  // Function to determine marker size based on indicator value
  const getMarkerSize = (cityId) => {
    if (!indicatorData || !selectedIndicator) return 8;
    
    const cityData = indicatorData.find(item => 
      item.city_id === cityId && item.indicator_id === selectedIndicator
    );
    
    if (!cityData) return 8;
    
    // Scale the marker size based on the value
    // Assuming values range from 0-100
    const baseSize = 8;
    const maxSize = 20;
    return baseSize + (cityData.value / 100) * (maxSize - baseSize);
  };

  // Function to determine marker color based on indicator value
  const getMarkerColor = (cityId) => {
    if (!indicatorData || !selectedIndicator) return '#3388ff';
    
    const cityData = indicatorData.find(item => 
      item.city_id === cityId && item.indicator_id === selectedIndicator
    );
    
    if (!cityData) return '#3388ff';
    
    // Color scale from red (low) to yellow (mid) to green (high)
    const value = cityData.value;
    
    if (value < 33) return '#ff3b3b';
    if (value < 66) return '#ffaa3b';
    return '#4caf50';
  };

  // Process indicator range for legend
  const getLegendItems = () => {
    return [
      { color: '#ff3b3b', label: t('map.low') + ' (0-33)' },
      { color: '#ffaa3b', label: t('map.medium') + ' (34-66)' },
      { color: '#4caf50', label: t('map.high') + ' (67-100)' }
    ];
  };

  return (
    <MapWrapper>
      <MapContainer center={mexicoCenter} zoom={5} scrollWheelZoom={true}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {cities.map((city) => (
          <CircleMarker
            key={city.id}
            center={[city.lat, city.lng]}
            radius={getMarkerSize(city.id)}
            fillColor={getMarkerColor(city.id)}
            color="#fff"
            weight={1}
            opacity={1}
            fillOpacity={0.7}
            className="city-marker"
            eventHandlers={{
              click: () => setSelectedCity(city),
            }}
          >
            <Tooltip>{city.name}</Tooltip>
            <Popup>
              <div>
                <h3>{city.name}, {city.state}</h3>
                <p>
                  {selectedIndicator 
                    ? `${t('indicators.' + selectedIndicator)}: ${
                        indicatorData.find(
                          item => item.city_id === city.id && item.indicator_id === selectedIndicator
                        )?.value || t('map.no_data')
                      }`
                    : t('map.select_indicator')}
                </p>
                <button onClick={() => window.location.href = `/cities/${city.id}`}>
                  {t('map.details')}
                </button>
              </div>
            </Popup>
          </CircleMarker>
        ))}
        
        {selectedIndicator && (
          <Legend>
            <h4>{t('indicators.' + selectedIndicator)}</h4>
            {getLegendItems().map((item, index) => (
              <LegendItem key={index}>
                <LegendColor color={item.color} />
                <span>{item.label}</span>
              </LegendItem>
            ))}
          </Legend>
        )}
      </MapContainer>
    </MapWrapper>
  );
};

export default MapVisualization;
