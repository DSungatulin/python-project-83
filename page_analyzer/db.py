from dotenv import load_dotenv
from datetime import date


import psycopg2
import os
import app


def connect_db():
    load_dotenv()
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def retrieve_page():
    conn = connect_db()
    with conn.cursor() as cursor:
        query = """
            SELECT urls.id, urls.name, MAX(url_checks.created_at), MAX(status_code)
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id
            ORDER BY urls.id DESC
        """
        cursor.execute(query)
        urls = cursor.fetchall()
        return urls

def retrieve_id():
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT id FROM urls WHERE name=%s', (app.normalise_url[1],))
        id = cursor.fetchone()
        return cursor, id

def check_db_data():
    cursor = retrieve_id()[0]
    id = retrieve_id()[1]
    conn = connect_db()
    cursor.execute(
    "INSERT INTO urls (name, created_at) VALUES (%s, %s);",
    (app.normalise_url[1], date.today()))
    cursor.execute('SELECT id FROM urls WHERE name=%s',
                (app.normalise_url[1],))
    id = cursor.fetchone()[0]
    conn.commit()
    return id
