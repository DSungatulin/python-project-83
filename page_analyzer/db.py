from dotenv import load_dotenv
from datetime import date


import psycopg2
import os
import page_analyzer.normalization as norm


load_dotenv()


def connect_db():
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    return conn


conn = connect_db()


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
        cursor.execute('SELECT id FROM urls WHERE name=%s', (norm.normalise_url()[1],))
        id = cursor.fetchone()
        return id


def check_db_data():
    conn = connect_db()
    with conn.cursor() as cursor:
        id = retrieve_id(conn)
        url = norm.normalise_url()[1]

        cursor.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s);",
            (url, date.today())
        )
        cursor.execute('SELECT id FROM urls WHERE name=%s', (url,))

        id = cursor.fetchone()[0]
        conn.commit()
    return id


def get_url_details(conn, id):
    with conn.cursor() as cursor:
        cursor.execute('SELECT name, created_at FROM urls WHERE id=%s', (id,))
        url, date = cursor.fetchone()
        cursor.execute("""SELECT id, status_code, h1, title, description,
                          created_at FROM url_checks WHERE id=%s
                          ORDER BY id DESC""", (id,))
        checks = cursor.fetchall()
    normalized_checks = norm.normalize_data(checks)
    return url, date, normalized_checks


def get_url_by_id(conn, id):
    with conn.cursor() as cursor:
        cursor.execute('SELECT name FROM urls WHERE id=%s', (id,))
        url = cursor.fetchone()
        return url[0] if url else None


def insert_url_check(conn, id, status_code, h1, title, description, created_at):
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO url_checks
            (url_id, status_code, h1, title, description, created_at)
            VALUES (%s, %s, %s, %s, %s, %s);""",
            (id, status_code, h1, title, description, created_at)
        )
        conn.commit()
