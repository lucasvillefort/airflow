import statistics as sts
from datetime import datetime

import pandas as pd
from airflow import DAG, Dataset
from airflow.operators.python_operator import PythonOperator

dag = DAG(
    dag_id="12producer",
    start_date=datetime(2020, 1, 1),
    schedule_interval="@daily",
    catchup=False,
)

mydataset = Dataset("/opt/airflow/data/Churn_new.csv")


def my_file():
    dataset = pd.read_csv("/opt/airflow/data/Churn.csv", sep=";")
    dataset.to_csv("/opt/airflow/data/Churn_new.csv", sep=";")


task1 = PythonOperator(
    task_id="my_file",
    python_callable=my_file,
    dag=dag,
    outlets=[mydataset],  # this will check if the dataset is updated
)

task1
