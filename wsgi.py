"""
Entry point para Gunicorn.
"""

import os
from alfajor import create_app

app = create_app(os.environ.get("FLASK_ENV", "production"))
