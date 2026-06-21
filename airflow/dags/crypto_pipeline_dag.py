from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'Youssef Jazouli',
    'depends_on_past': False,
    'start_date': datetime(2026, 6, 15),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'crypto_medallion_pipeline',
    default_args=default_args,
    description='Pipeline Big Data complet : CoinGecko -> MinIO -> Snowflake',
    schedule_interval='@daily',
    catchup=False
) as dag:

    task_ingest_bronze = BashOperator(
        task_id='ingest_bronze_layer',
        bash_command='python3 /opt/airflow/project/src/ingestion/ingest_bronze.py',
    )

    task_transform_silver = BashOperator(
        task_id='transform_silver_layer',
        bash_command='python3 /opt/airflow/project/src/transformation/transform_silver.py',
    )

    task_build_gold = BashOperator(
        task_id='build_gold_layer',
        bash_command='python3 /opt/airflow/project/src/modeling/build_gold_model.py',
    )

    task_load_snowflake = BashOperator(
        task_id='load_to_snowflake',
        bash_command='python3 /opt/airflow/project/loading/load_snowflake.py',
    )

    task_ingest_bronze >> task_transform_silver >> task_build_gold >> task_load_snowflake