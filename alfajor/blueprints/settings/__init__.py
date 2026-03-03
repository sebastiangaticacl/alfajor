from flask import Blueprint
bp = Blueprint("settings", __name__, url_prefix="/admin/config")
from alfajor.blueprints.settings import routes  # noqa: E402, F401
