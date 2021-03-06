from dags_helper.is_sparkapp_terminated import main

from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
import os


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2019, 4, 1),
    "email": ["airflow@infin.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    "test_sparkapp_sensor",
    default_args=default_args,
    schedule_interval="@once",
    catchup=False,
    max_active_runs=1,
)

sensor = PythonOperator(
    dag=dag,
    task_id="client_bank_transaction_dedup",
    python_callable=main,
    op_kwargs={"yaml_config_path": f"{os.getenv('AIRFLOW_HOME')}/dags/config/trx-dedup-deploy.yaml"}
)
