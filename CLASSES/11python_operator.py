# Domine Apache Airflow. https://www.eia.ai/
import statistics as sts
from datetime import datetime, timedelta

import pandas as pd
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

default_args = {
    "depends_on_past": False,
    "start_date": datetime(2023, 3, 5),
    "email": ["aws@evoluth.com.br"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,  # it will retry 1 time in case of failure
    "retry_delay": timedelta(seconds=10),  # it will wait 10 seconds before retrying
}

dag = DAG(
    "PythonOperator",
    description="PythonOperator with database",
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
)


def data_cleaning():
    dataset = pd.read_csv("/opt/airflow/data/Churn.csv", sep=";")
    dataset.columns = [
        "id",
        "score",
        "state",
        "gender",
        "age",
        "patrimony",
        "balance",
        "products",
        "credit_card",
        "active",
        "salary",
        "exited",
    ]

    # fill na of salary with median:
    dataset["salary"] = dataset["salary"].fillna(sts.median(dataset["salary"]))

    # fill gender with mode:
    dataset["gender"] = dataset["gender"].fillna(sts.mode(dataset["gender"]))
    
    # fill age with median:
    dataset["age"] = dataset["age"].fillna(sts.median(dataset["age"]))
    dataset.loc[dataset["age"] < 0 | dataset["age"] > 120 , "age"] = sts.median(dataset["age"])
    
    # drop duplicates:
    dataset = dataset.drop_duplicates(subset=["id"], keep="first")

    # to save the dataset:
    dataset.to_csv("/opt/airflow/data/Churn_cleaned.csv", sep=";", index=False)
    
task1 = PythonOperator(task_id="data_cleaning", python_callable=data_cleaning, dag=dag)
    
task1