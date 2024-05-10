from dotenv import load_dotenv
from datetime import date
from page_analyzer.normalization import normalize_url


import psycopg2
import os


load_dotenv()


DATABASE_URL = os.getenv('DATABASE_URL')


def connect_db(database_url):
    with psycopg2.connect(database_url) as conn:
        return conn


def retrieve_page(conn):
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


def retrieve_id(conn):
    with conn.cursor() as cursor:
        query = 'SELECT id FROM urls WHERE name=%s'
        cursor.execute(query, (normalize_url()[1],))
        id = cursor.fetchone()
        return id


def check_db_data(conn):
    with conn.cursor() as cursor:
        url = normalize_url()[1]
        query = "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;"
        values = (url, date.today())
        cursor.execute(query, values)
        id = cursor.fetchone()[0]
        conn.commit()
    return id


def get_url_details(id, conn):
    with conn.cursor() as cursor:
        query = 'SELECT name, created_at FROM urls WHERE id=%s'
        cursor.execute(query, (id,))
        url_details = cursor.fetchone()
    return url_details


def get_url_checks(id, conn):
    with conn.cursor() as cursor:
        query = """
                SELECT id, status_code, h1, title, description, created_at
                FROM url_checks
                WHERE url_id = %s
                ORDER BY id DESC
                """
        cursor.execute(query, (id,))
        checks = cursor.fetchall()
    return checks


def get_url_by_id(id, conn):
    with conn.cursor() as cursor:
        query = 'SELECT name FROM urls WHERE id=%s'
        cursor.execute(query, (id,))
        result = cursor.fetchone()[0]
    return result


def insert_url_check(conn, id, status_code, h1, title, description):
    with conn.cursor() as cursor:
        query = """
            INSERT INTO url_checks
            (url_id, status_code, h1, title, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        values = (id, status_code, h1, title, description, date.today())
        cursor.execute(query, values)
    conn.commit()
