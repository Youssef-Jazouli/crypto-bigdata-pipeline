from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# Arguments par défaut du DAG
default_args = {
    'owner': 'Youssef Jazouli',
    'depends_on_past': False,
    'start_date': datetime(2026, 6, 15), # Airflow va rattraper automatiquement l'historique depuis le 15 juin !
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'crypto_medallion_pipeline',
    default_args=default_args,
    description='Pipeline Big Data complet avec gestion dynamique et historique des dates',
    schedule_interval='@daily',
    catchup=True, # Indispensable pour exécuter les jours passés et remplir MinIO !
    max_active_runs=1 # Exécute les jours un par un proprement pour éviter de surcharger l'API
) as dag:

    # Tâche 1 : Ingestion de la couche Bronze en passant la date d'exécution formatée (Ex: 2026/06/15)
    task_ingest_bronze = BashOperator(
        task_id='ingest_bronze_layer',
        bash_command='EXEC_DATE=$(echo "{{ ds }}" | tr "-" "/") && python3 /opt/airflow/project/src/ingestion/ingest_bronze.py $EXEC_DATE',
    )

    # Tâche 2 : Transformation et nettoyage (Couche Silver)
    task_transform_silver = BashOperator(
        task_id='transform_silver_layer',
        bash_command='python3 /opt/airflow/project/src/transformation/transform_silver.py',
    )

    # Tâche 3 : Modélisation en tables de Faits et Dimensions (Couche Gold)
    task_build_gold = BashOperator(
        task_id='build_gold_layer',
        bash_command='python3 /opt/airflow/project/src/modeling/build_gold_model.py',
    )

    # Tâche 4 : Chargement final et automatique dans Snowflake
    task_load_snowflake = BashOperator(
        task_id='load_to_snowflake',
        bash_command='python3 /opt/airflow/project/loading/load_snowflake.py',
    )

    # Ordonnancement des tâches du pipeline
    task_ingest_bronze >> task_transform_silver >> task_build_gold >> task_load_snowflake