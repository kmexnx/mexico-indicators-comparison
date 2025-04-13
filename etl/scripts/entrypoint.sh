#!/bin/bash

# Initialize the Airflow database
airflow db init

# Create an Airflow user if it doesn't exist
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Start Airflow based on the command passed
exec airflow "$@"
