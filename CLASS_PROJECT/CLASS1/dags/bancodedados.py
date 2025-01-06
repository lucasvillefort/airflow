# Domine Apache Airflow. https://www.eia.ai/
# we need to have docker-compose.yaml and .env -> docker-compose up -d -> docker-compose ps 
# docker exec -it class_airflow_webserver_1 bash -> at opt/airflow terminal -> airflow dags list -> airflow dags trigger -e 2023-03-05 hook
from datetime import datetime

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# fisrt of all, we need to create a connection in the Airflow UI:
# Admin -> Connections -> Create -> Conn Id: postgres conn Type: Postgres Host: postgres User: airflow Password: airflow 

dag =  DAG('bancodedados', description="bancodedados",
        schedule_interval=None,start_date=datetime(2023,3,5),
        catchup=False)

def print_result(ti):
    task_instance = ti.xcom_pull(task_ids='query_data')
    print("Resultado da consulta:")
    for row in task_instance:
        print(row)



create_table = PostgresOperator(task_id='create_table',
                                postgres_conn_id='postgres',
                                sql='create table if not exists teste(id int);',
                                dag=dag)

insert_data = PostgresOperator(task_id='insert_data',
                                postgres_conn_id='postgres',
                                sql='insert into teste values(1);',
                                dag=dag)

query_data = PostgresOperator(task_id='query_data',
                                postgres_conn_id='postgres',
                                sql='select * from teste;',
                                dag=dag)

print_result_task = PythonOperator(
                              task_id='print_result_task',
                              python_callable=print_result,
                              provide_context=True,
                              dag=dag   
                                )
create_table >> insert_data >> query_data >> print_result_task