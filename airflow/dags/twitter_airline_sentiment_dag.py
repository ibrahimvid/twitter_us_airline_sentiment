import os
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def download_dataset(**kwargs):
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    data_path = '/opt/airflow/data'
    os.makedirs(data_path, exist_ok=True)
    api.dataset_download_files('toddwschneider/twitter-airline-sentiment', path=data_path, unzip=True)
    logging.info('Dataset downloaded to %s', data_path)

def stage_to_s3(**kwargs):
    import boto3
    from botocore.client import Config
    local_csv = '/opt/airflow/data/Tweets.csv'
    bucket = 'raw'
    s3 = boto3.client(
        's3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin',
        config=Config(signature_version='s3v4')
    )
    # Create bucket if it doesn't exist
    try:
        s3.head_bucket(Bucket=bucket)
    except Exception:
        s3.create_bucket(Bucket=bucket)
    # Upload raw CSV
    s3.upload_file(local_csv, bucket, 'Tweets.csv')
    logging.info('Uploaded %s to S3 bucket %s', local_csv, bucket)

# Define the DAG
with DAG(
    'twitter_airline_sentiment',
    default_args=default_args,
    description='Download, stage, and transform airline sentiment dataset',
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    download_task = PythonOperator(
        task_id='download_dataset',
        python_callable=download_dataset,
        provide_context=True,
    )

    stage_task = PythonOperator(
        task_id='stage_to_s3',
        python_callable=stage_to_s3,
        provide_context=True,
    )

    etl_task = BashOperator(
        task_id='run_spark_etl',
        bash_command='python3 /opt/airflow/scripts/etl.py',
    )

    download_task >> stage_task >> etl_task