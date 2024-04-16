import os
import psycopg2
import validators
import requests


from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import date
from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    redirect,
    url_for
)
from bs4 import BeautifulSoup as bs


load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def index_page():
    return render_template('index.html')


def normalize_data(item):
    return [value if value else '' for value in item]


@app.get('/urls')
def render_add_new_page():
    conn = psycopg2.connect(DATABASE_URL)
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
        normalized_urls = [normalize_data(url) for url in urls]
    return render_template('urls.html', urls=normalized_urls)


@app.post('/urls')
def add_new_page():
    url = request.form.get('url', '')
    url_max_len = 255
    parsed_url = urlparse(url)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.hostname}"
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute('SELECT id FROM urls WHERE name=%s', (normalized_url,))
        id = cursor.fetchone()

        if not validators.url(url) or len(url) > url_max_len:
            if len(url) > url_max_len:
                flash('URL превышает 255 символов', 'error')
            else:
                flash('Некорректный URL', 'error')
            messages = get_flashed_messages(with_categories=True)
            return render_template('index.html', messages=messages), 422

        if not id:
            cursor.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s);",
                (normalized_url, date.today()))
            cursor.execute('SELECT id FROM urls WHERE name=%s', (normalized_url,))
            id = cursor.fetchone()[0]
            conn.commit()
            flash('Страница добавлена', 'success')
            return redirect(url_for('render_url_page', id=id))

        flash('Страница уже существует', 'info')
        return redirect(url_for('render_url_page', id=id[0]))


@app.route('/urls/<int:id>')
def render_url_page(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute('SELECT name, created_at FROM urls WHERE id=%s', (id,))
        url, date = cursor.fetchone()
        cursor.execute("""SELECT id, status_code, h1, title, description,
                    created_at FROM url_checks WHERE url_id=%s
                    ORDER BY id DESC""", (id,))
        checks = cursor.fetchall()
        normalized_checks = list(map(normalize_data, checks))
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'url.html',
            messages=messages,
            url=url,
            id=id,
            date=date,
            checks=normalized_checks
        )


@app.post('/urls/<int:id>/checks')
def check_page(id):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True

        with conn.cursor() as cursor:
            cursor.execute('SELECT name FROM urls WHERE id=%s', (id,))
            url = cursor.fetchone()[0]

        response = requests.get(url)
        response.raise_for_status()

        html = bs(response.text, 'html.parser')
        h1 = html.h1.string
        title = html.title.string
        description = html.find(attrs={"name": "description"})['content']

        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO url_checks
                (url_id, status_code, h1, title, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s);""",
                (id, response.status_code, h1, title, description, date.today()))

        flash('Страница успешно проверена', 'success')

    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')

    except psycopg2.Error:
        flash('Произошла ошибка при проверке', 'danger')

    finally:
        return redirect(url_for('render_url_page', id=id))
