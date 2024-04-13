import os
from flask import Flask
from dotenv import load_dotenv

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
