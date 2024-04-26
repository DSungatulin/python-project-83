from dotenv import load_dotenv
from datetime import date
# from urllib.parse import urlparse
# from flask import request
from page_analyzer.normalization import normalize_url


import psycopg2
import os


load_dotenv()


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
            LEFT JOIN url_checks ON urls.id = url_checks.id
            GROUP BY urls.id
            ORDER BY urls.id DESC
        """
        cursor.execute(query)
        urls = cursor.fetchall()
        return urls


def retrieve_id():
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT id FROM urls WHERE name=%s', (normalize_url()[1],))
        id = cursor.fetchone()
        return id


def check_db_data():
    conn = connect_db()
    with conn.cursor() as cursor:
        id = retrieve_id()
        url = normalize_url()[1]
        cursor.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s);",
            (url, date.today())
        )
        cursor.execute('SELECT id FROM urls WHERE name=%s', (url,))
        id = cursor.fetchone()[0]
        conn.commit()
    return id


def get_url_details(id):
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute('SELECT name, created_at FROM urls WHERE id=%s', (id,))
        url_details = cursor.fetchone()
    return url_details


def get_url_checks(id):
    conn = connect_db()
    with conn.cursor() as cursor:
        cursor.execute("""SELECT id, status_code, h1, title, description, created_at
                          FROM url_checks WHERE id=%s ORDER BY id DESC""", (id,))
        checks = cursor.fetchall()
    return checks
