from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.base_operator import (
    BashOperator,  # it is a class (type of task) that we can use to create a task
)
from airflow.operators.python_operator import PythonOperator

# it only a object that we can use to create a task
dag = DAG(
    "xcom dag",
    description="A simple tutorial DAG",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
)


def task_write(**kwargs):
    ti = kwargs["ti"]
    ti.xcom_push(key="my_key", value=10200)


task1 = PythonOperator(task_id="task1", dag=dag, python_callable=task_write)


def task_read(**kwargs):
    ti = kwargs["ti"]
    value = ti.xcom_pull(key="my_key")
    print(value)


task2 = PythonOperator(task_id="task2", dag=dag, python_callable=task_read)

# order of tasks execution:
task1 >> task2
