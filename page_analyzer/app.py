import os
import validators
import requests
import page_analyzer.db as db


from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    flash,
    get_flashed_messages,
    redirect,
    url_for
)
from bs4 import BeautifulSoup
from page_analyzer.normalization import normalize_url, normalize_data


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def index_page():
    return render_template('index.html')


@app.get('/urls')
def render_add_page():
    conn = db.connect_db()
    urls = db.retrieve_page(conn)
    normalized_urls = normalize_data(urls)
    return render_template('urls.html', urls=normalized_urls)


@app.post('/urls')
def add_page():
    url = normalize_url()[0]
    url_max_len = 255
    id = db.retrieve_id()

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
    url_details = db.get_url_details(id, conn)
    url, date = url_details
    checks = db.get_url_checks(id, conn)
    normalized_checks = normalize_data(checks)
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
    try:
        url = db.get_url_by_id(id, conn)
        r = requests.get(url)
        r.raise_for_status()
        html = BeautifulSoup(r.text, 'html.parser')
        db.insert_url_check(
            conn,
            id,
            r.status_code,
            html.h1.string if html.h1 else None,
            html.title.string if html.title else None,
            html.find(attrs={"name": "description"}).get('content') if html.find(attrs={"name": "description"}) else None
        )
        flash('Страница успешно проверена', 'success')
    except requests.exceptions.HTTPError as e:
        flash(f'Произошла ошибка при проверке: {e}', 'danger')
    except Exception as e:
        flash(f'Произошла ошибка при проверке: {e}', 'danger')
    finally:
        conn.close()
        return redirect(url_for('render_url_page', id=id))
