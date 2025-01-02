import sched
import statistics as sts
from datetime import datetime

import pandas as pd
from airflow import DAG, Dataset
from airflow.operators.python_operator import PythonOperator

mydataset = Dataset("/opt/airflow/data/Churn_new.csv")

dag = DAG(
    dag_id="13consumer",
    start_date=datetime(2020, 1, 1),
    schedule=[mydataset],
    catchup=False,
)


def my_file():
    dataset = pd.read_csv("/opt/airflow/data/Churn_new.csv", sep=";")
    dataset.to_csv("/opt/airflow/data/Churn_new2.csv", sep=";")


task1 = PythonOperator(
    task_id="my_file",
    python_callable=my_file,
    dag=dag,
    provide_context=True,  # this will check if the dataset is updated
)

task1
