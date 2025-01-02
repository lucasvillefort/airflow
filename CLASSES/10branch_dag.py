# Domine Apache Airflow. https://www.eia.ai/
import random
from datetime import datetime, timedelta
from multiprocessing import pool
from venv import create

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator

default_args = {
    "depends_on_past": False,
    "start_date": datetime(2023, 3, 5),
    "email": ["aws@evoluth.com.br"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1, # it will retry 1 time in case of failure
    "retry_delay": timedelta(seconds=10), # it will wait 10 seconds before retrying
}

dag = DAG(
    "BranchPythonOperator",
    description="BranchPythonOperator",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    default_view="graph",
    tags=["processo", "tag", "pipeline", "branch", "python operator"],
)

def random_number():
    return random.randint(1, 100)

create_number_random_task = PythonOperator(
    task_id="create_number_random_task",
    python_callable=random_number,
    dag=dag,
)

def check_number(**kwargs):
    value = kwargs.get("task_instance").xcom_pull(task_ids="create_number_random_task")
    
    # number is par or not:
    if value % 2 == 0:
        return "par_task"
    else:
        return "impar_task"

branch_task = BranchPythonOperator(
    task_id="branch_task",
    python_callable=check_number,
    provide_context=True,
    dag=dag,
)


par_task = BashOperator(task_id="par_task", bash_command="echo 'par'", dag=dag)
impar_task = BashOperator(task_id="impar_task", bash_command="echo 'impar'", dag=dag)

create_number_random_task >> branch_task
branch_task >> [par_task, impar_task]

# to limit the number of pool i need to go to the localhost:8080/admin/pool/ and set it up