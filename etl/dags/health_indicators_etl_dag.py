"""
DAG para extraer indicadores de salud de México desde la Secretaría de Salud
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook

import pandas as pd
import requests
import os
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración por defecto
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Crear DAG
dag = DAG(
    'health_indicators_etl_dag',
    default_args=default_args,
    description='ETL para extraer indicadores de salud de ciudades mexicanas',
    schedule_interval='@monthly',
    start_date=datetime(2025, 4, 1),
    catchup=False,
    tags=['mexico', 'health', 'indicators', 'etl'],
)

# Comprobar disponibilidad de la API de Secretaría de Salud
check_api = HttpSensor(
    task_id='check_health_api',
    http_conn_id='salud_api',
    endpoint='/',
    request_params={},
    response_check=lambda response: response.status_code == 200,
    poke_interval=5,
    timeout=20,
    dag=dag,
)

# Crear tabla de indicadores de salud si no existe
create_health_indicators_table = PostgresOperator(
    task_id='create_health_indicators_table',
    postgres_conn_id='postgres_default',
    sql="""
    CREATE TABLE IF NOT EXISTS health_indicators (
        id SERIAL PRIMARY KEY,
        city_id INTEGER REFERENCES cities(id),
        indicator_id VARCHAR(50) NOT NULL,
        year INTEGER NOT NULL,
        value DECIMAL(10, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(city_id, indicator_id, year)
    );
    
    -- Tabla de catálogo de indicadores
    CREATE TABLE IF NOT EXISTS indicators_catalog (
        id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        category VARCHAR(50) NOT NULL,
        unit VARCHAR(20),
        source VARCHAR(100)
    );
    
    -- Insertar o actualizar catálogo de indicadores de salud
    INSERT INTO indicators_catalog (id, name, description, category, unit, source)
    VALUES 
        ('health_exp_capita', 'Gasto en salud per cápita', 'Gasto total en salud por habitante', 'salud', 'MXN', 'Secretaría de Salud'),
        ('hospital_beds', 'Camas de hospital', 'Camas de hospital por cada 1,000 habitantes', 'salud', 'por 1000', 'Secretaría de Salud'),
        ('doctors_density', 'Densidad de médicos', 'Médicos por cada 1,000 habitantes', 'salud', 'por 1000', 'Secretaría de Salud'),
        ('child_mortality', 'Mortalidad infantil', 'Tasa de mortalidad infantil por cada 1,000 nacidos vivos', 'salud', 'por 1000', 'Secretaría de Salud'),
        ('life_expectancy', 'Esperanza de vida', 'Esperanza de vida al nacer en años', 'salud', 'años', 'Secretaría de Salud')
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        description = EXCLUDED.description,
        category = EXCLUDED.category,
        unit = EXCLUDED.unit,
        source = EXCLUDED.source;
    """,
    dag=dag,
)

def extract_health_indicators():
    """
    Extrae indicadores de salud de la Secretaría de Salud.
    En una implementación real, utilizaríamos la API completa 
    pero para este ejemplo simulamos con datos ficticios.
    """
    # Simulación de datos - En producción esto sería una llamada a la API
    # URL base: http://www.dgis.salud.gob.mx/contenidos/basesdedatos/...
    
    # Obtener listado de ciudades de la base de datos
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    cities_df = pg_hook.get_pandas_df("SELECT id, name, state FROM cities")
    
    # Indicadores a extraer
    indicators = [
        'health_exp_capita',
        'hospital_beds',
        'doctors_density',
        'child_mortality',
        'life_expectancy'
    ]
    
    # Crear datos ficticios para cada ciudad e indicador
    health_data = []
    
    for _, city in cities_df.iterrows():
        for indicator in indicators:
            # Generar un valor ficticio para cada indicador
            if indicator == 'health_exp_capita':
                # Gasto en salud per cápita (en pesos mexicanos)
                value = round(5000 + (city['id'] * 500), 2)
            elif indicator == 'hospital_beds':
                # Camas de hospital por cada 1,000 habitantes
                value = round(1.5 + (city['id'] * 0.2), 2)
            elif indicator == 'doctors_density':
                # Médicos por cada 1,000 habitantes
                value = round(2.0 + (city['id'] * 0.15), 2)
            elif indicator == 'child_mortality':
                # Tasa de mortalidad infantil (por 1,000 nacidos vivos)
                value = round(15.0 - (city['id'] * 0.5), 2)
                if value < 5.0:
                    value = 5.0
            elif indicator == 'life_expectancy':
                # Esperanza de vida (en años)
                value = round(75.0 + (city['id'] * 0.25), 2)
                if value > 82.0:
                    value = 82.0
            else:
                value = 0.0
            
            # Año actual
            year = 2024
            
            health_data.append({
                'city_id': city['id'],
                'indicator_id': indicator,
                'year': year,
                'value': value
            })
    
    # Guardar en archivo CSV temporal
    df = pd.DataFrame(health_data)
    output_path = '/tmp/health_indicators.csv'
    df.to_csv(output_path, index=False)
    return output_path

def load_health_indicators(**kwargs):
    """
    Carga los indicadores de salud en PostgreSQL
    """
    ti = kwargs['ti']
    csv_path = ti.xcom_pull(task_ids='extract_health_indicators')
    
    # Leer el CSV
    df = pd.read_csv(csv_path)
    
    # Conectarse a la base de datos
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    # Para cada indicador, insertar o actualizar
    for _, row in df.iterrows():
        cursor.execute("""
        INSERT INTO health_indicators (city_id, indicator_id, year, value)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (city_id, indicator_id, year)
        DO UPDATE SET
            value = EXCLUDED.value,
            created_at = CURRENT_TIMESTAMP
        """, (
            row['city_id'],
            row['indicator_id'],
            row['year'],
            row['value']
        ))
    
    conn.commit()
    cursor.close()
    conn.close()

# Definir tareas
extract_task = PythonOperator(
    task_id='extract_health_indicators',
    python_callable=extract_health_indicators,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_health_indicators',
    python_callable=load_health_indicators,
    provide_context=True,
    dag=dag,
)

# Definir dependencias
check_api >> create_health_indicators_table >> extract_task >> load_task
