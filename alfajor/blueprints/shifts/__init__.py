from flask import Blueprint
bp = Blueprint("shifts", __name__, url_prefix="/shifts")
from alfajor.blueprints.shifts import routes  # noqa: E402, F401
