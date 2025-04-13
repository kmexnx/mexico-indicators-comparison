import React from 'react';
import { 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  Legend, 
  ResponsiveContainer,
  Tooltip
} from 'recharts';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

const ChartContainer = styled.div`
  width: 100%;
  height: 500px;
  margin-bottom: 2rem;
`;

const ChartTitle = styled.h3`
  margin-bottom: 1rem;
  text-align: center;
`;

const CustomTooltip = ({ active, payload }) => {
  const { t } = useTranslation();
  
  if (active && payload && payload.length) {
    return (
      <div className="custom-tooltip" style={{ 
        backgroundColor: '#fff', 
        padding: '10px', 
        border: '1px solid #ccc',
        borderRadius: '4px'
      }}>
        <p><strong>{payload[0].payload.indicator}</strong></p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }}>
            {entry.name}: {entry.value.toFixed(2)}
          </p>
        ))}
      </div>
    );
  }

  return null;
};

const ComparisonChart = ({ data, cities, title }) => {
  const { t } = useTranslation();
  
  // Transform data for radar chart
  const transformedData = data.map(item => {
    const transformedItem = {
      indicator: t(`indicators.${item.indicator_id}`),
      fullMark: 100, // Maximum value for scale
    };
    
    cities.forEach(city => {
      transformedItem[city.name] = item[city.id] || 0;
    });
    
    return transformedItem;
  });
  
  // Generate colors for each city
  const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#a4de6c'];
  
  return (
    <ChartContainer>
      <ChartTitle>{title || t('comparison.chart_title')}</ChartTitle>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart 
          cx="50%" 
          cy="50%" 
          outerRadius="80%" 
          data={transformedData}
        >
          <PolarGrid />
          <PolarAngleAxis dataKey="indicator" />
          <PolarRadiusAxis angle={30} domain={[0, 100]} />
          <Tooltip content={<CustomTooltip />} />
          
          {cities.map((city, index) => (
            <Radar
              key={city.id}
              name={city.name}
              dataKey={city.name}
              stroke={COLORS[index % COLORS.length]}
              fill={COLORS[index % COLORS.length]}
              fillOpacity={0.3}
            />
          ))}
          
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </ChartContainer>
  );
};

export default ComparisonChart;
