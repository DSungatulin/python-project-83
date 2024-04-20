import os
import validators
import requests
import page_analyzer.db as db


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
from bs4 import BeautifulSoup


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def index_page():
    return render_template('index.html')


def normalize_data(item):
    return list(map(lambda val: (val if val else ''), item))


@app.get('/urls')
def render_add_page():
    urls = db.retrieve_page()
    non_empty_urls = [url for url in urls if url[1]]
    normalized_urls = [normalize_data(url) for url in non_empty_urls]
    return render_template('urls.html', urls=normalized_urls)


def normalise_url():
    url = request.form.get('url', '')
    parsed_url = urlparse(url)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.hostname}"
    return url, normalized_url


@app.post('/urls')
def add_page():
    url = normalise_url[0]
    url_max_len = 255
    id = db.retrieve_id()[1]
    
    if not validators.url(url) or len(url) > url_max_len:
        if len(url) > url_max_len:
            flash('URL превышает 255 символов', 'error')
        else:
            flash('Некорректный URL', 'error')
            
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', messages=messages), 422
    
    if not id:
        id = db.check_db_data()
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('render_url_page', id=id))
    else:
        flash('Страница уже существует', 'info')
        return redirect(url_for('render_url_page', id=id[0]))


@app.route('/urls/<int:id>')
def render_url_page(id):
    conn = db.connect_db()
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
    conn = db.connect_db()
    conn.autocommit = True
    with conn.cursor() as cursor:
        cursor.execute('SELECT name FROM urls WHERE id=%s', (id,))
        url = cursor.fetchone()[0]
        try:
            r = requests.get(url)
            r.raise_for_status()
            html = BeautifulSoup(r.text, 'html.parser')
            cursor.execute(
                """INSERT INTO url_checks
                (url_id, status_code, h1, title, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s);""",
                (id,
                 r.status_code,
                 html.h1.string if html.h1 else None,
                 html.title.string if html.title else None,
                 html.find(attrs={"name": "description"})['content'] if html.find(attrs={"name": "description"}) else None,
                 date.today()
                 )
            )
            flash('Страница успешно проверена', 'success')
            return redirect(url_for('render_url_page', id=id))
        except requests.exceptions.HTTPError:
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('render_url_page', id=id))
        except Exception:
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('render_url_page', id=id))
