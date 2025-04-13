# México Indicators Comparison

Aplicación web para comparar indicadores de calidad de vida, educación y salud entre ciudades de México.

## Arquitectura

- **Frontend**: React + D3.js para visualizaciones interactivas
- **Backend**: FastAPI para la API REST
- **Base de datos**: PostgreSQL con extensión PostGIS para datos geoespaciales
- **ETL**: Apache Airflow para la extracción, transformación y carga de datos desde fuentes gubernamentales

## Estructura del Proyecto

```
/
├── frontend/          # Aplicación React
├── backend/           # API FastAPI
├── etl/               # Flujos de trabajo de Airflow
├── infra/             # Archivos de configuración Docker y Docker Compose
└── docs/              # Documentación
```

## Requisitos

- Docker y Docker Compose
- Node.js 18+
- Python 3.10+
- PostgreSQL 14+

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/kmexnx/mexico-indicators-comparison.git
cd mexico-indicators-comparison

# Levantar servicios con Docker Compose
docker-compose up -d
```

## Características

- Comparación visual de indicadores entre múltiples ciudades
- Visualizaciones con gráficos interactivos y mapas
- Análisis de tendencias temporales
- Exportación de datos y gráficos
- API documentada para acceso programático a los datos

## Fuentes de Datos

- INEGI (Instituto Nacional de Estadística y Geografía)
- CONEVAL (Consejo Nacional de Evaluación de la Política de Desarrollo Social)
- Secretaría de Salud
- Secretaría de Educación Pública
- Datos Abiertos México
