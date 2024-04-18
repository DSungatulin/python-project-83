# Page Analyzer
[![Actions Status](https://github.com/DSungatulin/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/DSungatulin/python-project-83/actions)
[![Actions Status](https://github.com/DSungatulin/python-project-83/actions/workflows/pyci.yml/badge.svg)](https://github.com/DSungatulin/python-project-83/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/817bd0d383c10a2beca3/maintainability)](https://codeclimate.com/github/DSungatulin/python-project-83/maintainability)


## Description
This is a web application built using Python on the Flask framework. 
It allows users to add websites and perform basic "SEO checks" on them.

[**Page Analyzer Example**](https://python-project-83-poti.onrender.com)


## Requirements

* Python 3.10+
* Poetry 1.7+
* Flask 3.0+
* psycopg2-binary 2.9+
* Bootstrap 5.3+


## Dependencies

- [Flask](https://github.com/pallets/flask/)
- [gunicorn](https://github.com/benoitc/gunicorn)
- [psycopg2](https://github.com/psycopg/psycopg2)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [validators](https://github.com/python-validators/validators)
- [requests](https://github.com/psf/requests)
- [beautifulsoup](https://code.launchpad.net/beautifulsoup)


## Installation
1. Clone the repo
2. Create a PostgreSQL database using the provided cheatsheet (database.sql)
3. Create a .env file and add the necessary variables or add them directly to your environment using the export command
4. Run `make dev` for debugging (with WSGI debug set to 'True'), or `make start` for production (using gunicorn)
