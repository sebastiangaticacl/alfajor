# ALFAJOR - Comandos de desarrollo
.PHONY: run migrate seed install

install:
	pip install -r requirements.txt

migrate:
	FLASK_APP=alfajor flask db upgrade

seed:
	python scripts/seed.py

run:
	FLASK_APP=alfajor flask run

run-prod:
	gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
