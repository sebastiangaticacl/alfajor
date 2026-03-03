"""Servicio de configuración."""

from alfajor.extensions import db
from alfajor.models import Setting, Branch


def get_setting(key, default=None):
    s = Setting.query.filter_by(key=key).first()
    return s.value if s else default


def set_setting(key, value, description=None):
    s = Setting.query.filter_by(key=key).first()
    if s:
        s.value = value
        if description is not None:
            s.description = description
    else:
        s = Setting(key=key, value=value, description=description)
        db.session.add(s)
    db.session.commit()
    return s


def get_branches():
    return Branch.query.filter_by(active=True).order_by(Branch.name).all()
