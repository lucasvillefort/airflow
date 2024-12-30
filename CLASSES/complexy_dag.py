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
    "complexity_dag",
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
task4 = BashOperator(task_id="task4", bash_command='echo "Hello World"', dag=dag)
task5 = BashOperator(task_id="task5", bash_command='echo "Hello World"', dag=dag)
task6 = BashOperator(task_id="task6", bash_command='echo "Hello World"', dag=dag)
task7 = BashOperator(task_id="task7", bash_command='echo "Hello World"', dag=dag)
task8 = BashOperator(task_id="task8", bash_command='echo "Hello World"', dag=dag)

task9 = BashOperator(
    task_id="task9",
    bash_command='echo "Hello World"',
    dag=dag,
    trigger_rule="one_failed",  # it will trigger the task3 if any of the previous tasks fails
)


# order of tasks execution:
task1 >> task2
task3 >> task4
[task2, task4] >> task5 >> task6
task6 >> [task7, task8, task9]
