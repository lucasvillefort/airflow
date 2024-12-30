from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.base_operator import (
    BashOperator,  # it is a class (type of task) that we can use to create a task
)

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# it only a object that we can use to create a task
dag = DAG(
    "my_dag",
    default_args=default_args,
    description="A simple tutorial DAG",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
)
# BashOperator is a type of task
task1 = BashOperator(task_id="task1", bash_command='echo "Hello World"', dag=dag)

task2 = BashOperator(task_id="task2", bash_command='echo "Hello World"', dag=dag)

task3 = BashOperator(task_id="task3", bash_command='echo "Hello World"', dag=dag)

# order of tasks execution:
task1 >> task2 >> task3
