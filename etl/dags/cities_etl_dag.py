"""
DAG para extraer información de ciudades mexicanas del INEGI
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.postgres.hooks.postgres import PostgresHook

import json
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración por defecto
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Crear DAG
dag = DAG(
    'cities_etl_dag',
    default_args=default_args,
    description='ETL para extraer datos de ciudades mexicanas',
    schedule_interval='@monthly',
    start_date=datetime(2025, 4, 1),
    catchup=False,
    tags=['mexico', 'cities', 'etl'],
)

# Comprobar disponibilidad de la API de INEGI
check_api = HttpSensor(
    task_id='check_inegi_api',
    http_conn_id='inegi_api',
    endpoint='/',
    request_params={},
    response_check=lambda response: response.status_code == 200,
    poke_interval=5,
    timeout=20,
    dag=dag,
)

# Crear tabla de ciudades si no existe
create_cities_table = PostgresOperator(
    task_id='create_cities_table',
    postgres_conn_id='postgres_default',
    sql="""
    CREATE TABLE IF NOT EXISTS cities (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        state VARCHAR(50) NOT NULL,
        population INTEGER,
        lat DECIMAL(9, 6),
        lng DECIMAL(9, 6),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,
    dag=dag,
)

def extract_cities_data():
    """
    Extrae datos de ciudades de México de la API de INEGI.
    En una implementación real, utilizaríamos la API completa 
    pero para este ejemplo simulamos con datos.
    """
    # Simulación de datos - En producción esto sería una llamada a la API
    # URL base: https://www.inegi.org.mx/app/api/indicadores/...
    
    cities_data = [
        {
            'name': 'Ciudad de México',
            'state': 'Ciudad de México',
            'population': 9209944,
            'lat': 19.4326,
            'lng': -99.1332
        },
        {
            'name': 'Guadalajara',
            'state': 'Jalisco',
            'population': 1495182,
            'lat': 20.6597,
            'lng': -103.3496
        },
        {
            'name': 'Monterrey',
            'state': 'Nuevo León',
            'population': 1142994,
            'lat': 25.6866,
            'lng': -100.3161
        },
        {
            'name': 'Puebla',
            'state': 'Puebla',
            'population': 1692181,
            'lat': 19.0414,
            'lng': -98.2063
        },
        {
            'name': 'Tijuana',
            'state': 'Baja California',
            'population': 1810645,
            'lat': 32.5149,
            'lng': -117.0382
        }
    ]
    
    # Guardar en archivo CSV temporal
    df = pd.DataFrame(cities_data)
    output_path = '/tmp/cities_data.csv'
    df.to_csv(output_path, index=False)
    return output_path

def load_cities_data(**kwargs):
    """
    Carga los datos de ciudades en PostgreSQL
    """
    ti = kwargs['ti']
    csv_path = ti.xcom_pull(task_ids='extract_cities_data')
    
    # Leer el CSV
    df = pd.read_csv(csv_path)
    
    # Conectarse a la base de datos
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    # Para cada ciudad, insertar o actualizar
    for _, row in df.iterrows():
        cursor.execute("""
        INSERT INTO cities (name, state, population, lat, lng)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (name, state)
        DO UPDATE SET
            population = EXCLUDED.population,
            lat = EXCLUDED.lat,
            lng = EXCLUDED.lng,
            updated_at = CURRENT_TIMESTAMP
        """, (
            row['name'],
            row['state'],
            row['population'],
            row['lat'],
            row['lng']
        ))
    
    conn.commit()
    cursor.close()
    conn.close()

# Definir tareas
extract_task = PythonOperator(
    task_id='extract_cities_data',
    python_callable=extract_cities_data,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_cities_data',
    python_callable=load_cities_data,
    provide_context=True,
    dag=dag,
)

# Definir dependencias
check_api >> create_cities_table >> extract_task >> load_task
