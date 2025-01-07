# Domine Apache Airflow. https://www.eia.ai/
# creating variable at ui airflow: key = path_file and value = /opt/airflow/data/data.json
# creating connection at ui airflow: connection id = fs_default and host = /opt/airflow/data/data.json


import json
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable
from airflow.operators.email_operator import EmailOperator
from airflow.operators.python_operator import BranchPythonOperator, PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.task_group import TaskGroup

default_args = {
    "depends_on_past": False,
    "email": ["aws@evoluth.com.br"],  # for send email if error
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=10),
}

# schedule_interval="*/3 * * * * "
dag = DAG(
    "windturbine",
    description="Dados da Turbina",
    schedule_interval=None,
    start_date=datetime(2023, 3, 5),
    catchup=False,
    default_args=default_args,
    default_view="graph",
    doc_md="## Dag para registrar dados de turbina eólica",
)

# to put some task into this group
group_check_temp = TaskGroup(
    "group_check_temp", dag=dag
)  # to ckeck the temperature of the turbine
group_database = TaskGroup(
    "group_database", dag=dag
)  # to save the data in the database postgres


file_sensor_task = FileSensor(
    task_id="file_sensor_task",
    filepath=Variable.get(
        "path_file"
    ),  # "/opt/airflow/data/data.json", it will read the variable
    fs_conn_id="fs_default",  # it will read the connection id from airflow ui
    poke_interval=10,
    dag=dag,
)


# kwarg["ti"] will read the task instance
def process_file(**kwarg):
    with open(Variable.get("path_file")) as f:
        data = json.load(f)  # it will read the file
        kwarg["ti"].xcom_push(
            key="idtemp", value=data["idtemp"]
        )  # it will save the data in xcom
        kwarg["ti"].xcom_push(key="powerfactor", value=data["powerfactor"])
        kwarg["ti"].xcom_push(key="hydraulicpressure", value=data["hydraulicpressure"])
        kwarg["ti"].xcom_push(key="temperature", value=data["temperature"])
        kwarg["ti"].xcom_push(key="timestamp", value=data["timestamp"])
    os.remove(Variable.get("path_file"))


# to get the data from the sensor and save in xcom
get_data = PythonOperator(
    task_id="get_data", python_callable=process_file, provide_context=True, dag=dag
)

create_table = PostgresOperator(
    task_id="create_table",
    postgres_conn_id="postgres",  # it will read the connection id from airflow ui
    sql="""create table if not exists
                                sensors (idtemp varchar, powerfactor varchar,
                                hydraulicpressure varchar, temperature varchar,
                                timestamp varchar);
                                """,
    task_group=group_database,
    dag=dag,
)

insert_data = PostgresOperator(
    task_id="insert_data",
    postgres_conn_id="postgres",
    parameters=(
        '{{ ti.xcom_pull(task_ids="get_data",key="idtemp") }}',  # it will read the data from xcom
        '{{ ti.xcom_pull(task_ids="get_data",key="powerfactor") }}',
        '{{ ti.xcom_pull(task_ids="get_data",key="hydraulicpressure") }}',
        '{{ ti.xcom_pull(task_ids="get_data",key="temperature") }}',
        '{{ ti.xcom_pull(task_ids="get_data",key="timestamp") }}',
    ),
    sql="""INSERT INTO sensors (idtemp, powerfactor,
                               hydraulicpressure, temperature, timestamp)
                               VALUES (%s, %s, %s, %s, %s);""",
    task_group=group_database,
    dag=dag,
)

send_email_alert = EmailOperator(
    task_id="send_email_alert",
    to="aws@evoluth.com.br",
    subject="Airlfow alert",
    html_content="""<h3>Alerta de Temperatrura. </h3>
                                <p> Dag: windturbine </p>
                                """,
    task_group=group_check_temp,
    dag=dag,
)

send_email_normal = EmailOperator(
    task_id="send_email_normal",
    to="aws@evoluth.com.br",
    subject="Airlfow advise",
    html_content="""<h3>Temperaturas normais. </h3>
                                <p> Dag: windturbine </p>
                                """,
    task_group=group_check_temp,
    dag=dag,
)


def avalia_temp(**context):
    number = float(context["ti"].xcom_pull(task_ids="get_data", key="temperature"))
    if number >= 24:
        return "group_check_temp.send_email_alert"  # it will send the email
    else:
        return "group_check_temp.send_email_normal"


# to check the temperature of the turbine and send an email to the user if the temperature is in danger  or not
check_temp_branc = BranchPythonOperator(
    task_id="check_temp_branc",
    python_callable=avalia_temp,
    provide_context=True,
    dag=dag,
    task_group=group_check_temp,
)

# create relationship between tasks inside task group
with group_check_temp:
    check_temp_branc >> [send_email_alert, send_email_normal]

with group_database:
    create_table >> insert_data

# create precedence relationship between tasks
file_sensor_task >> get_data
get_data >> group_check_temp
get_data >> group_database
