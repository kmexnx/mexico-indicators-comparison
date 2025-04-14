#!/bin/bash

# Initialize the Airflow database if it doesn't exist
if [ ! -f "/opt/airflow/airflow.db" ]; then
    airflow db init
fi

# Create an Airflow user if it doesn't exist
airflow users list | grep -q "admin" || \
    airflow users create \
        --username admin \
        --password admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com

# Start Airflow based on the command passed
exec airflow "$@"
