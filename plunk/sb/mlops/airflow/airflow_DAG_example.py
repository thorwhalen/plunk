from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 28),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'airflow_sms_dag', default_args=default_args, schedule_interval=timedelta(days=1),
)


def func_1():
    print('Function 1 executed')


def func_2():
    print('Function 2 executed')


def func_3():
    print('Function 3 executed')


func_1 = PythonOperator(task_id='func_1', python_callable=func_1, dag=dag,)

func_2 = PythonOperator(task_id='func_2', python_callable=func_2, dag=dag,)

func_3 = PythonOperator(task_id='func_3', python_callable=func_3, dag=dag,)

func_1 >> func_2 >> func_3
