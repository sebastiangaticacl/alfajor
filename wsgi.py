"""
Entry point para Gunicorn / producción.

Uso: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
"""

import os
from alfajor import create_app

app = create_app(os.environ.get("FLASK_ENV", "production"))
