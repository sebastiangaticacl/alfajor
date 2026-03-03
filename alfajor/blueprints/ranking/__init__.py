from flask import Blueprint
bp = Blueprint("ranking", __name__, url_prefix="/admin/ranking")
from alfajor.blueprints.ranking import routes  # noqa: E402, F401
