from dotenv import load_dotenv
from datetime import date
from urllib.parse import urlparse
from flask import request


import psycopg2
import os



load_dotenv()


def normalise_url():
    url = request.form.get('url', '')
    parsed_url = urlparse(url)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.hostname}"
    return url, normalized_url


def connect_db():
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
        cursor.execute('SELECT id FROM urls WHERE name=%s', (normalise_url[1],))
        id = cursor.fetchone()
        return cursor, id


def check_db_data():
    cursor, id = retrieve_id()
    conn = connect_db()
    url = normalise_url[1]

    cursor.execute(
        "INSERT INTO urls (name, created_at) VALUES (%s, %s);",
        (url, date.today())
    )
    cursor.execute('SELECT id FROM urls WHERE name=%s', (url,))

    id = cursor.fetchone()[0]
    conn.commit()
    return id
