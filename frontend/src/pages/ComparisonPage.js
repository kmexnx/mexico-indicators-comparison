import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import styled from 'styled-components';
import { useTranslation } from 'react-i18next';

// Components
import ComparisonChart from '../components/charts/ComparisonChart';
import CustomBarChart from '../components/charts/CustomBarChart';
import IndicatorTable from '../components/tables/IndicatorTable';
import ComparisonSelector from '../components/selectors/ComparisonSelector';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ErrorMessage from '../components/ui/ErrorMessage';

// Services
import { fetchCities, fetchIndicators, generateComparison } from '../services/api';

const PageContainer = styled.div`
  padding: 1rem;
`;

const Title = styled.h1`
  margin-bottom: 2rem;
  text-align: center;
`;

const ChartContainer = styled.div`
  display: flex;
  flex-direction: column;
  margin-top: 2rem;
  gap: 2rem;

  @media (min-width: 992px) {
    flex-direction: row;
  }
`;

const ChartWrapper = styled.div`
  flex: 1;
  min-width: 0;
`;

const ComparisonPage = () => {
  const { t } = useTranslation();
  const [selectedCities, setSelectedCities] = useState([]);
  const [selectedIndicators, setSelectedIndicators] = useState([]);
  const [year, setYear] = useState(new Date().getFullYear() - 1); // Default to previous year
  const [comparisonData, setComparisonData] = useState(null);

  // Fetch cities
  const {
    data: cities,
    isLoading: citiesLoading,
    error: citiesError,
  } = useQuery('cities', fetchCities);

  // Fetch indicators
  const {
    data: indicators,
    isLoading: indicatorsLoading,
    error: indicatorsError,
  } = useQuery('indicators', fetchIndicators);

  // Generate comparison data
  const {
    data: comparison,
    isLoading: comparisonLoading,
    error: comparisonError,
    refetch: fetchComparison,
  } = useQuery(
    ['comparison', selectedCities, selectedIndicators, year],
    () => generateComparison(selectedCities, selectedIndicators, year),
    {
      enabled: false, // Don't run automatically
      onSuccess: (data) => {
        setComparisonData(data);
      },
    }
  );

  // Handle form submission
  const handleCompare = () => {
    if (selectedCities.length >= 2 && selectedIndicators.length > 0) {
      fetchComparison();
    }
  };

  const isLoading = citiesLoading || indicatorsLoading || comparisonLoading;
  const error = citiesError || indicatorsError || comparisonError;

  return (
    <PageContainer>
      <Title>{t('comparison.title')}</Title>

      {isLoading && <LoadingSpinner />}
      {error && <ErrorMessage message={error.message} />}

      <ComparisonSelector
        cities={cities || []}
        indicators={indicators || []}
        selectedCities={selectedCities}
        selectedIndicators={selectedIndicators}
        year={year}
        onCitiesChange={setSelectedCities}
        onIndicatorsChange={setSelectedIndicators}
        onYearChange={setYear}
        onCompare={handleCompare}
      />

      {comparisonData && (
        <>
          <ChartContainer>
            <ChartWrapper>
              <ComparisonChart
                data={comparisonData.indicators}
                cities={comparisonData.cities}
                title={t('comparison.radar_chart_title')}
              />
            </ChartWrapper>
            <ChartWrapper>
              <CustomBarChart
                data={comparisonData.indicators}
                cities={comparisonData.cities}
                title={t('comparison.bar_chart_title')}
              />
            </ChartWrapper>
          </ChartContainer>

          <IndicatorTable
            data={comparisonData.indicators}
            cities={comparisonData.cities}
          />
        </>
      )}
    </PageContainer>
  );
};

export default ComparisonPage;
