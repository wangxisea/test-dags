from kubernetes import config as kube_config
from kubernetes.client.apis.custom_objects_api import CustomObjectsApi
import time
import yaml
import argparse
from datetime import datetime

# kube_config.load_incluster_config()
kube_config.load_kube_config()
crd = CustomObjectsApi()


def get_sparkapp_status_obj(crd_name: str):
    sparkapp_obj = crd.get_namespaced_custom_object(
        group="sparkoperator.k8s.io",
        version="v1beta1",
        namespace="airflow",
        plural="sparkapplications",
        name=crd_name,
    )
    return sparkapp_obj


def is_sparkapp_terminated(crd_name: str):
    sparkapp_obj = get_sparkapp_status_obj(crd_name)

    sparkapp_state = sparkapp_obj["status"]["applicationState"]["state"]
    if sparkapp_state == "COMPLETED":
        is_terminated = True
    else:
        is_terminated = False
    return is_terminated


def time_sparkapp_elapse(crd_name: str):
    sparkapp_obj = get_sparkapp_status_obj(crd_name)

    spark_app_submission_time = datetime.strptime(
        sparkapp_obj["status"]["lastSubmissionAttemptTime"], "%Y-%m-%dT%H:%M:%SZ"
    )
    spark_app_termination_time = datetime.strptime(
        sparkapp_obj["status"]["terminationTime"], "%Y-%m-%dT%H:%M:%SZ"
    )
    time_elapse = spark_app_termination_time - spark_app_submission_time
    return time_elapse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--k8s_config",
        type=str,
        help="config file path",
        default="../config/trx-dedup-deploy.yaml",
    )
    args = parser.parse_args()

    with open(args.k8s_config, "r") as manifest:
        try:
            crd_name = yaml.load(manifest, Loader=yaml.FullLoader)["metadata"]["name"]
        except yaml.YAMLError as exc:
            print(exc)

    while True:
        if is_sparkapp_terminated(crd_name):
            # logging
            print(f"sparkapp {crd_name} completed!")
            print(f"sparkapp elapsed {time_sparkapp_elapse(crd_name)}")
            break
        time.sleep(10)

"""
sample output of the ['status'] section of the manifest result
{
    "applicationState": {
        "errorMessage": "",
        "state": "RUNNING"
    },
    "driverInfo": {
        "podName": "trx-dedup-driver",
        "webUIPort": 30242,
        "webUIServiceName": "trx-dedup-ui-svc"
    },
    "executionAttempts": 1,
    "executorState": {
        "trx-dedup-1556105612720-exec-1": "RUNNING"
    },
    "lastSubmissionAttemptTime": "2019-04-24T11:33:34Z",
    "sparkApplicationId": "spark-application-1556105635209",
    "submissionAttempts": 1,
    "terminationTime": null
}

{
    "applicationState": {
        "errorMessage": "",
        "state": "COMPLETED"
    },
    "driverInfo": {
        "podName": "trx-dedup-driver",
        "webUIPort": 30242,
        "webUIServiceName": "trx-dedup-ui-svc"
    },
    "executionAttempts": 1,
    "executorState": {
        "trx-dedup-1556105612720-exec-1": "RUNNING"
    },
    "lastSubmissionAttemptTime": "2019-04-24T11:33:34Z",
    "sparkApplicationId": "spark-application-1556105635209",
    "submissionAttempts": 1,
    "terminationTime": "2019-04-24T11:41:58Z"
}
"""
