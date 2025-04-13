import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';
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

// Custom Bar Chart created with D3.js directly
const CustomBarChart = ({ data, cities, title, selectedIndicator }) => {
  const { t } = useTranslation();
  const chartRef = useRef(null);

  useEffect(() => {
    if (!data || !cities || cities.length === 0) return;

    // Clear any existing SVG
    d3.select(chartRef.current).selectAll('*').remove();

    // Dimensions and margins
    const margin = { top: 40, right: 80, bottom: 60, left: 60 };
    const width = chartRef.current.clientWidth - margin.left - margin.right;
    const height = chartRef.current.clientHeight - margin.top - margin.bottom;

    // Create SVG element
    const svg = d3
      .select(chartRef.current)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Filter data to show only one indicator if selected
    const filteredData = selectedIndicator
      ? data.filter(d => d.indicator_id === selectedIndicator)
      : data;

    // Data restructuring for D3
    const chartData = [];
    filteredData.forEach(item => {
      cities.forEach(city => {
        if (item[city.id] !== undefined) {
          chartData.push({
            indicator: t(`indicators.${item.indicator_id}`),
            city: city.name,
            value: item[city.id] || 0
          });
        }
      });
    });

    // Scales
    const indicators = [...new Set(chartData.map(d => d.indicator))];
    const cityNames = [...new Set(chartData.map(d => d.city))];
    
    // X scale (indicators)
    const x0 = d3.scaleBand()
      .domain(indicators)
      .rangeRound([0, width])
      .paddingInner(0.1);
    
    // X1 scale (cities within each indicator)
    const x1 = d3.scaleBand()
      .domain(cityNames)
      .rangeRound([0, x0.bandwidth()])
      .padding(0.05);
    
    // Y scale
    const y = d3.scaleLinear()
      .domain([0, d3.max(chartData, d => d.value) * 1.1]) // 10% padding at top
      .nice()
      .range([height, 0]);
    
    // Color scale
    const color = d3.scaleOrdinal()
      .domain(cityNames)
      .range(['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#a4de6c']);
    
    // Add X axis
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x0).tickSize(0))
      .call(g => g.select('.domain').remove())
      .selectAll('text')
      .attr('y', 10)
      .attr('x', 0)
      .attr('dy', '.35em')
      .attr('transform', 'rotate(-25)')
      .attr('text-anchor', 'start');
    
    // Add Y axis
    svg.append('g')
      .call(d3.axisLeft(y))
      .call(g => g.select('.domain').remove());
    
    // Add grid lines
    svg.append('g')
      .attr('class', 'grid')
      .call(d3.axisLeft(y)
        .tickSize(-width)
        .tickFormat('')
      )
      .call(g => g.select('.domain').remove())
      .call(g => g.selectAll('.tick line')
        .attr('stroke', '#e0e0e0')
        .attr('stroke-opacity', 0.7));
    
    // Add bars
    const barGroups = svg.append('g')
      .selectAll('g')
      .data(indicators)
      .join('g')
      .attr('transform', d => `translate(${x0(d)},0)`);
    
    barGroups.selectAll('rect')
      .data(indicator => {
        return chartData.filter(d => d.indicator === indicator);
      })
      .join('rect')
      .attr('x', d => x1(d.city))
      .attr('y', d => y(d.value))
      .attr('width', x1.bandwidth())
      .attr('height', d => height - y(d.value))
      .attr('fill', d => color(d.city))
      .attr('rx', 2) // Rounded corners
      .on('mouseover', function(event, d) {
        d3.select(this).attr('opacity', 0.8);
        
        // Show tooltip
        tooltip
          .html(`
            <strong>${d.city}</strong><br/>
            ${d.indicator}: ${d.value}
          `)
          .style('visibility', 'visible')
          .style('left', `${event.pageX + 10}px`)
          .style('top', `${event.pageY - 28}px`);
      })
      .on('mouseout', function() {
        d3.select(this).attr('opacity', 1);
        tooltip.style('visibility', 'hidden');
      });
    
    // Add legend
    const legend = svg.append('g')
      .attr('font-family', 'sans-serif')
      .attr('font-size', 10)
      .attr('text-anchor', 'end')
      .selectAll('g')
      .data(cityNames)
      .join('g')
      .attr('transform', (d, i) => `translate(${width + 70},${i * 20})`);
    
    legend.append('rect')
      .attr('x', -19)
      .attr('width', 19)
      .attr('height', 19)
      .attr('fill', color);
    
    legend.append('text')
      .attr('x', -24)
      .attr('y', 9.5)
      .attr('dy', '0.32em')
      .text(d => d);
    
    // Add tooltip
    const tooltip = d3.select(chartRef.current)
      .append('div')
      .attr('class', 'd3-tooltip')
      .style('position', 'absolute')
      .style('visibility', 'hidden')
      .style('background-color', 'white')
      .style('border', '1px solid #ddd')
      .style('padding', '10px')
      .style('border-radius', '4px')
      .style('pointer-events', 'none')
      .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)');
    
    // Chart title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', -margin.top / 2)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('font-weight', 'bold')
      .text(title || t('charts.bar_chart_title'));
    
  }, [data, cities, title, selectedIndicator, t]);

  return (
    <ChartContainer>
      <ChartTitle>{title || t('charts.bar_chart_title')}</ChartTitle>
      <div 
        ref={chartRef} 
        style={{ width: '100%', height: 'calc(100% - 30px)' }}
      ></div>
    </ChartContainer>
  );
};

export default CustomBarChart;
