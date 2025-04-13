import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useTheme } from './contexts/ThemeContext';
import styled, { ThemeProvider } from 'styled-components';

// Components
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import Sidebar from './components/layout/Sidebar';

// Pages
import HomePage from './pages/HomePage';
import ComparisonPage from './pages/ComparisonPage';
import CityDetailsPage from './pages/CityDetailsPage';
import AboutPage from './pages/AboutPage';
import NotFoundPage from './pages/NotFoundPage';

// Themes
import { lightTheme, darkTheme } from './styles/themes';
import GlobalStyles from './styles/GlobalStyles';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`;

const MainContent = styled.main`
  display: flex;
  flex: 1;
`;

const ContentArea = styled.div`
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
`;

function App() {
  const { t } = useTranslation();
  const { theme } = useTheme();
  const currentTheme = theme === 'dark' ? darkTheme : lightTheme;

  return (
    <ThemeProvider theme={currentTheme}>
      <GlobalStyles />
      <AppContainer>
        <Navbar />
        <MainContent>
          <Sidebar />
          <ContentArea>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/comparison" element={<ComparisonPage />} />
              <Route path="/cities/:cityId" element={<CityDetailsPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </ContentArea>
        </MainContent>
        <Footer />
      </AppContainer>
    </ThemeProvider>
  );
}

export default App;
