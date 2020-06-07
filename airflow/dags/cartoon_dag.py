from datetime import timedelta
from airflow import DAG
from dilbert import Dilbert
from main import update_dilbert
from datetime import date
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': '2020-01-01',
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

fp = '/Users/Andrew/Documents/data_engineering/database/comics.db'


dummy = DummyOperator(
    task_id='Dummy',
    default_args=default_args
)

dilbert_dag = PythonOperator(
    task_id='Dilbert',
    provide_context=True,
    python_callable=update_dilbert,
    op_args=[date.today(), fp],
    dag=dag
)


dummy >> dilbert_dag
