"""
DAG para extraer indicadores de educación de México desde la Secretaría de Educación
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
    'education_indicators_etl_dag',
    default_args=default_args,
    description='ETL para extraer indicadores de educación de ciudades mexicanas',
    schedule_interval='@monthly',
    start_date=datetime(2025, 4, 1),
    catchup=False,
    tags=['mexico', 'education', 'indicators', 'etl'],
)

# Comprobar disponibilidad de la API de Secretaría de Educación
check_api = HttpSensor(
    task_id='check_education_api',
    http_conn_id='educacion_api',
    endpoint='/',
    request_params={},
    response_check=lambda response: response.status_code == 200,
    poke_interval=5,
    timeout=20,
    dag=dag,
)

# Crear tabla de indicadores de educación si no existe
create_education_indicators_table = PostgresOperator(
    task_id='create_education_indicators_table',
    postgres_conn_id='postgres_default',
    sql="""
    CREATE TABLE IF NOT EXISTS education_indicators (
        id SERIAL PRIMARY KEY,
        city_id INTEGER REFERENCES cities(id),
        indicator_id VARCHAR(50) NOT NULL,
        year INTEGER NOT NULL,
        value DECIMAL(10, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(city_id, indicator_id, year)
    );
    
    -- Insertar o actualizar catálogo de indicadores de educación
    INSERT INTO indicators_catalog (id, name, description, category, unit, source)
    VALUES 
        ('literacy_rate', 'Tasa de alfabetización', 'Porcentaje de la población que sabe leer y escribir', 'educacion', '%', 'SEP'),
        ('primary_enrollment', 'Matrícula primaria', 'Tasa de matrícula escolar en educación primaria', 'educacion', '%', 'SEP'),
        ('secondary_enrollment', 'Matrícula secundaria', 'Tasa de matrícula escolar en educación secundaria', 'educacion', '%', 'SEP'),
        ('higher_enrollment', 'Matrícula superior', 'Tasa de matrícula escolar en educación superior', 'educacion', '%', 'SEP'),
        ('education_exp_capita', 'Gasto en educación per cápita', 'Gasto total en educación por habitante', 'educacion', 'MXN', 'SEP'),
        ('student_teacher_ratio', 'Ratio estudiante-profesor', 'Número de estudiantes por profesor', 'educacion', 'ratio', 'SEP')
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        description = EXCLUDED.description,
        category = EXCLUDED.category,
        unit = EXCLUDED.unit,
        source = EXCLUDED.source;
    """,
    dag=dag,
)

def extract_education_indicators():
    """
    Extrae indicadores de educación de la Secretaría de Educación.
    En una implementación real, utilizaríamos la API completa 
    pero para este ejemplo simulamos con datos ficticios.
    """
    # Simulación de datos - En producción esto sería una llamada a la API
    # URL base: https://www.planeacion.sep.gob.mx/estadisticaeindicadores.aspx
    
    # Obtener listado de ciudades de la base de datos
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    cities_df = pg_hook.get_pandas_df("SELECT id, name, state FROM cities")
    
    # Indicadores a extraer
    indicators = [
        'literacy_rate',
        'primary_enrollment',
        'secondary_enrollment',
        'higher_enrollment',
        'education_exp_capita',
        'student_teacher_ratio'
    ]
    
    # Crear datos ficticios para cada ciudad e indicador
    education_data = []
    
    for _, city in cities_df.iterrows():
        for indicator in indicators:
            # Generar un valor ficticio para cada indicador
            if indicator == 'literacy_rate':
                # Tasa de alfabetización (porcentaje)
                value = round(90.0 + (city['id'] * 0.5), 2)
                if value > 99.5:
                    value = 99.5
            elif indicator == 'primary_enrollment':
                # Tasa de matrícula primaria (porcentaje)
                value = round(95.0 + (city['id'] * 0.2), 2)
                if value > 99.5:
                    value = 99.5
            elif indicator == 'secondary_enrollment':
                # Tasa de matrícula secundaria (porcentaje)
                value = round(85.0 + (city['id'] * 0.6), 2)
                if value > 98.0:
                    value = 98.0
            elif indicator == 'higher_enrollment':
                # Tasa de matrícula superior (porcentaje)
                value = round(35.0 + (city['id'] * 1.5), 2)
                if value > 60.0:
                    value = 60.0
            elif indicator == 'education_exp_capita':
                # Gasto en educación per cápita (en pesos mexicanos)
                value = round(3000 + (city['id'] * 400), 2)
            elif indicator == 'student_teacher_ratio':
                # Ratio estudiante-profesor
                value = round(25.0 - (city['id'] * 0.5), 2)
                if value < 12.0:
                    value = 12.0
            else:
                value = 0.0
            
            # Año actual
            year = 2024
            
            education_data.append({
                'city_id': city['id'],
                'indicator_id': indicator,
                'year': year,
                'value': value
            })
    
    # Guardar en archivo CSV temporal
    df = pd.DataFrame(education_data)
    output_path = '/tmp/education_indicators.csv'
    df.to_csv(output_path, index=False)
    return output_path

def load_education_indicators(**kwargs):
    """
    Carga los indicadores de educación en PostgreSQL
    """
    ti = kwargs['ti']
    csv_path = ti.xcom_pull(task_ids='extract_education_indicators')
    
    # Leer el CSV
    df = pd.read_csv(csv_path)
    
    # Conectarse a la base de datos
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    # Para cada indicador, insertar o actualizar
    for _, row in df.iterrows():
        cursor.execute("""
        INSERT INTO education_indicators (city_id, indicator_id, year, value)
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
    task_id='extract_education_indicators',
    python_callable=extract_education_indicators,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_education_indicators',
    python_callable=load_education_indicators,
    provide_context=True,
    dag=dag,
)

# Definir dependencias
check_api >> create_education_indicators_table >> extract_task >> load_task
