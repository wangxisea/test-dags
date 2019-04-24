from helper import is_spark_app_terminated

from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator


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
    "risk_score_batch",
    default_args=default_args,
    schedule_interval="1 10 * * *",
    catchup=False,
    max_active_runs=1,
)

sensor = PythonOperator(
    dag=dag,
    task_id="client_bank_transaction_dedup",
    python_callable=is_spark_app_terminated,
    op_kwargs={"--k8s_config": "trx-dedup-deploy.yaml"}
)
