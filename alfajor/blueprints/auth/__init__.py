from flask import Blueprint
bp = Blueprint("auth", __name__, url_prefix="/auth")
from alfajor.blueprints.auth import routes  # noqa: E402, F401
