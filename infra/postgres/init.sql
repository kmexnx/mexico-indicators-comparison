-- Inicialización de Base de Datos para México Indicators App

-- Crear la base de datos principal
CREATE DATABASE mexico_indicators;
\c mexico_indicators;

-- Crear extensiones
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- Para búsquedas de texto
CREATE EXTENSION IF NOT EXISTS unaccent; -- Para búsquedas sin acentos

-- Crear tablas principales
CREATE TABLE cities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    population INTEGER,
    lat DECIMAL(9, 6),
    lng DECIMAL(9, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, state)
);

-- Tabla para almacenar información geo
CREATE TABLE city_geometries (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    geom GEOMETRY(MULTIPOLYGON, 4326),
    UNIQUE(city_id)
);

-- Tabla de catálogo de indicadores
CREATE TABLE indicators_catalog (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    unit VARCHAR(20),
    source VARCHAR(100)
);

-- Tabla para indicadores de salud
CREATE TABLE health_indicators (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    indicator_id VARCHAR(50) REFERENCES indicators_catalog(id),
    year INTEGER NOT NULL,
    value DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, indicator_id, year)
);

-- Tabla para indicadores de educación
CREATE TABLE education_indicators (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    indicator_id VARCHAR(50) REFERENCES indicators_catalog(id),
    year INTEGER NOT NULL,
    value DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, indicator_id, year)
);

-- Tabla para indicadores económicos
CREATE TABLE economic_indicators (
    id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
    indicator_id VARCHAR(50) REFERENCES indicators_catalog(id),
    year INTEGER NOT NULL,
    value DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, indicator_id, year)
);

-- Índices para mejorar rendimiento
CREATE INDEX idx_health_city ON health_indicators(city_id);
CREATE INDEX idx_health_indicator ON health_indicators(indicator_id);
CREATE INDEX idx_health_year ON health_indicators(year);

CREATE INDEX idx_education_city ON education_indicators(city_id);
CREATE INDEX idx_education_indicator ON education_indicators(indicator_id);
CREATE INDEX idx_education_year ON education_indicators(year);

CREATE INDEX idx_economic_city ON economic_indicators(city_id);
CREATE INDEX idx_economic_indicator ON economic_indicators(indicator_id);
CREATE INDEX idx_economic_year ON economic_indicators(year);

-- Índice para búsqueda de texto en ciudades
CREATE INDEX idx_city_name_trgm ON cities USING GIN (name gin_trgm_ops);
CREATE INDEX idx_city_state_trgm ON cities USING GIN (state gin_trgm_ops);

-- Crear airflow database (para la administración de ETL)
CREATE DATABASE airflow;

-- Otorgar permisos
GRANT ALL PRIVILEGES ON DATABASE mexico_indicators TO mexico_app;
GRANT ALL PRIVILEGES ON DATABASE airflow TO mexico_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mexico_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mexico_app;

-- Insertar algunos datos iniciales (catálogo de indicadores)
INSERT INTO indicators_catalog (id, name, description, category, unit, source)
VALUES 
    -- Salud
    ('health_exp_capita', 'Gasto en salud per cápita', 'Gasto total en salud por habitante', 'salud', 'MXN', 'Secretaría de Salud'),
    ('hospital_beds', 'Camas de hospital', 'Camas de hospital por cada 1,000 habitantes', 'salud', 'por 1000', 'Secretaría de Salud'),
    ('doctors_density', 'Densidad de médicos', 'Médicos por cada 1,000 habitantes', 'salud', 'por 1000', 'Secretaría de Salud'),
    ('child_mortality', 'Mortalidad infantil', 'Tasa de mortalidad infantil por cada 1,000 nacidos vivos', 'salud', 'por 1000', 'Secretaría de Salud'),
    ('life_expectancy', 'Esperanza de vida', 'Esperanza de vida al nacer en años', 'salud', 'años', 'Secretaría de Salud'),

    -- Educación
    ('literacy_rate', 'Tasa de alfabetización', 'Porcentaje de la población que sabe leer y escribir', 'educacion', '%', 'SEP'),
    ('primary_enrollment', 'Matrícula primaria', 'Tasa de matrícula escolar en educación primaria', 'educacion', '%', 'SEP'),
    ('secondary_enrollment', 'Matrícula secundaria', 'Tasa de matrícula escolar en educación secundaria', 'educacion', '%', 'SEP'),
    ('higher_enrollment', 'Matrícula superior', 'Tasa de matrícula escolar en educación superior', 'educacion', '%', 'SEP'),
    ('education_exp_capita', 'Gasto en educación per cápita', 'Gasto total en educación por habitante', 'educacion', 'MXN', 'SEP'),
    ('student_teacher_ratio', 'Ratio estudiante-profesor', 'Número de estudiantes por profesor', 'educacion', 'ratio', 'SEP'),

    -- Economía
    ('gdp_per_capita', 'PIB per cápita', 'Producto interno bruto por habitante', 'economia', 'MXN', 'INEGI'),
    ('unemployment_rate', 'Tasa de desempleo', 'Porcentaje de la población activa que está desempleada', 'economia', '%', 'INEGI'),
    ('poverty_rate', 'Tasa de pobreza', 'Porcentaje de población por debajo de la línea de pobreza', 'economia', '%', 'CONEVAL'),
    ('gini_index', 'Índice de Gini', 'Medida de desigualdad económica', 'economia', 'índice', 'INEGI');
