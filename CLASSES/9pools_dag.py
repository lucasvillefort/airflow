# Domine Apache Airflow. https://www.eia.ai/
from datetime import datetime, timedelta
from multiprocessing import pool

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator

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
    "pool_test",
    description="pool_test",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
    default_view="graph",
    tags=["processo", "tag", "pipeline"],
)

task1 = BashOperator(task_id="tsk1", bash_command="sleep 1", dag=dag, pool="pool_created")
task2 = BashOperator(task_id="tsk2", bash_command="sleep 1", dag=dag, pool="pool_created", priority_weight=5)
task3 = BashOperator(task_id="tsk3", bash_command="sleep 1", dag=dag, pool="pool_created")
task4 = BashOperator(task_id="tsk4", bash_command="sleep 1", dag=dag, pool="pool_created")
task5 = BashOperator(task_id="tsk5", bash_command="sleep 1", dag=dag, pool="pool_created", priority_weight=10)

# to limit the number of pool i need to go to the localhost:8080/admin/pool/ and set it up