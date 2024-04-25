import os
import requests
import validators
import page_analyzer.db as db
import page_analyzer.normalization as norm


from datetime import date
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    flash,
    get_flashed_messages,
    redirect,
    url_for
)



conn = db.conn


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route("/")
def index_page():
    return render_template('index.html')


@app.get('/urls')
def render_add_page():
    urls = db.retrieve_page()
    normalized_urls = norm.normalize_data(urls)
    return render_template('urls.html', urls=normalized_urls)


@app.post('/urls')
def add_page():
    url = norm.normalise_url()[0]
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
    url, date, normalized_checks = db.get_url_details(conn, id)
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
    url = db.get_url_by_id(conn, id)
    if url:
        try:
            r = requests.get(url)
            r.raise_for_status()
            html = BeautifulSoup(r.text, 'html.parser')
            db.insert_url_check(
                conn,
                id,
                r.status_code,
                html.h1.string if html.h1 else None,
                html.title.string if html.title else None,
                html.find(attrs={"name": "description"})['content'] if html.find(attrs={"name": "description"}) else None,
                date.today()
            )
            flash('Страница успешно проверена', 'success')
        except requests.exceptions.HTTPError:
            flash('Произошла ошибка при проверке', 'danger')
        except Exception:
            flash('Произошла ошибка при проверке', 'danger')
    else:
        flash('URL not found', 'danger')
    return redirect(url_for('render_url_page', id=id))
