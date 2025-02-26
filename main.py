from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from sqlalchemy import create_engine
import pymongo
import pandas as pd

username = 'postgres'
password = 'postgres'
host = 'localhost'
port = '5432' 
# функция для выполнения запроса
def read_postgres():

    database = 'test'

    conn = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{database}').raw_connection()
    df1 = pd.read_sql('SELECT * FROM план;',conn)
    df2 = pd.read_sql('SELECT * FROM туризм;',conn)

    df1.to_csv('/tmp/df1.csv',index = False)
    df2.to_csv('/tmp/df2.csv',index = False)

def read_mongo():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["test"]
    df3 = pd.DataFrame(list(mydb[mydb.list_collection_names()[1]].find()))
    df4 = pd.DataFrame(list(mydb[mydb.list_collection_names()[2]].find()))

    df3.to_csv('/tmp/df3.csv',index = False)
    df4.to_csv('/tmp/df4.csv',index = False)

def process_data():

    keys = ['план','факт','туризм','статистика']
    data = {}
    data['план'] = pd.read_csv('/tmp/df1.csv')
    data['туризм'] = pd.read_csv('/tmp/df2.csv')
    data['факт'] = pd.read_csv('/tmp/df3.csv')
    data['статистика'] = pd.read_csv('/tmp/df4.csv')


    data['план'].to_csv('/tmp/df1.csv',index = False)
    data['туризм'].to_csv('/tmp/df2.csv',index = False)
    data['факт'].to_csv('/tmp/df3.csv',index = False)
    data['статистика'].to_csv('/tmp/df4.csv',index = False)


def save_data():
    keys = ['план','факт','туризм','статистика']
    data = {}
    
    data['план'] = pd.read_csv('/tmp/df1.csv')
    data['туризм'] = pd.read_csv('/tmp/df2.csv')
    data['факт'] = pd.read_csv('/tmp/df3.csv')
    data['статистика'] = pd.read_csv('/tmp/df4.csv')

    database = 'main_db'

    conn = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{database}')

    for key in keys:
        try:
            data[key].to_sql(key,con = conn, if_exists = 'replace',index = False)
        except Exception as err:
            print(err)


# определение dag
with DAG(
    dag_id="main",
    start_date=datetime(2025, 2, 26),
    schedule_interval="@daily",  # запускать ежедневно
    catchup=False,
) as dag:

# таск для выполнения запроса
    read_postgres_t = PythonOperator(
        task_id="read_postgres",
        python_callable=read_postgres,
    )

    read_mongo_t = PythonOperator(
        task_id="read_mongo",
        python_callable=read_mongo,
    )
#
    process_data_t = PythonOperator(
        task_id="process_data",
        python_callable=process_data,
    )
    save_data_t = PythonOperator(
        task_id="save_results",
        python_callable=save_data,
    )

    [read_postgres_t, read_mongo_t] >> process_data_t >> save_data_t