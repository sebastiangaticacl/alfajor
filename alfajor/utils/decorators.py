"""Decoradores para RBAC."""

from functools import wraps
from flask import abort
from flask_login import current_user


def role_required(*roles):
    """Exige que el usuario tenga uno de los roles indicados."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def admin_required(f):
    return role_required("ADMIN")(f)


def encargado_or_admin(f):
    return role_required("ADMIN", "ENCARGADO")(f)


def contabilidad_or_admin(f):
    return role_required("ADMIN", "CONTABILIDAD")(f)
