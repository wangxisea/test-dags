from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.bash_operator import  BashOperator
from airflow.operators.dummy_operator import DummyOperator


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2019, 4, 1),
    "email": ["airflow@infin.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    "risk_score_batch",
    default_args=default_args,
    schedule_interval="* 10 * * *",
    catchup=False,
    max_active_runs=1,
)

start = DummyOperator(task_id="START", dag=dag)


# templated_command = """
# kubectl apply -f config/trx-dedup-deploy-svc.yaml
# """
templated_command = "kubectl get pods -n {{ params.namespace }}"

tsk_dedup = BashOperator(
    dag=dag,
    task_id="client_bank_transaction_dedup",
    bash_command=templated_command,
    params={'namespace': 'airflow'},
)

end = DummyOperator(task_id="END", dag=dag)

tsk_dedup.set_upstream(start)
end.set_upstream(tsk_dedup)
