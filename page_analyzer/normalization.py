from urllib.parse import urlparse
from flask import request


def normalize_url():
    url = request.form.get('url', '')
    parsed_url = urlparse(url)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.hostname}"
    return url, normalized_url


def normalize_data(item):
    return [val for val in (val if val else '' for val in item) if val != '']
