from datetime import timedelta, datetime
from airflow import DAG
from dilbert import Dilbert
from main import update_dilbert
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2020, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}
dag = DAG(
    'cartoons_etl',
    default_args=default_args,
    description='A DAG to run the dilbert scrape',
    schedule_interval='0 12 * * *',
    # run daily at noon
)

filepath = '/Users/Andrew/Documents/data_engineering/database/comics.db'


dummy = DummyOperator(
    task_id='Dummy',
    default_args=default_args
)
execution_date = '{{ ds }}'

dilbert_dag = PythonOperator(
    task_id='Dilbert',
    python_callable=update_dilbert,
    op_args=[execution_date, filepath],
    dag=dag
)


dummy >> dilbert_dag
