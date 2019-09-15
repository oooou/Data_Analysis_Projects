import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries


def load_staging_tables(cur, conn):
    """
    Description: This function can be used to load data from S3 into staging tables in redshift.

    Arguments:
        cur: the cursor object. 
        coon: this connection object. 

    Returns:
    None
    """
    print('start load_staging_tables' + '='*10 + '>')
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    """
    Description: This function can be used to update data analysis tables from staging tables.

    Arguments:
        cur: the cursor object. 
        coon: this connection object. 

    Returns:
    None
    """
    print('start insert_tables' + '='*10 + '>')
    for query in insert_table_queries:
        
        print(query)
        cur.execute(query)
        conn.commit()


def main():
    """
    Description: This function can be used to start ETL.

    Arguments:
    None

    Returns:
    None
    """
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    load_staging_tables(cur, conn)
    insert_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()