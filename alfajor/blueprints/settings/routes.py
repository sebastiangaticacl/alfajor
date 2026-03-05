"""Rutas configuración."""

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from alfajor.utils.decorators import admin_required
from alfajor.blueprints.settings import bp
from alfajor.extensions import db
from alfajor.models import Setting, Branch
from alfajor.services.settings_service import get_setting, set_setting

SETTING_SCHEMA = {
    "rules.max_weekly_hours": {"type": int, "min": 0, "max": 200},
    "rules.min_rest_hours": {"type": int, "min": 0, "max": 24},
    "rules.max_consecutive_days": {"type": int, "min": 0, "max": 31},
    "rules.overtime_threshold_hours": {"type": int, "min": 0, "max": 24},
    "rules.overtime_multiplier": {"type": int, "min": 1, "max": 10},
    "shift_roles": {"type": list},
    "schedule.hours": {"type": dict},
}


def _parse_setting_value(key, val):
    import json
    if key in SETTING_SCHEMA:
        schema = SETTING_SCHEMA[key]
        expected_type = schema["type"]
        if expected_type in (dict, list):
            value = json.loads(val)
            if not isinstance(value, expected_type):
                raise ValueError(f"Formato inválido para {key}")
            return value
        if expected_type is int:
            if not val.lstrip("-").isdigit():
                raise ValueError(f"{key} debe ser un entero")
            value = int(val)
            min_v = schema.get("min")
            max_v = schema.get("max")
            if min_v is not None and value < min_v:
                raise ValueError(f"{key} debe ser >= {min_v}")
            if max_v is not None and value > max_v:
                raise ValueError(f"{key} debe ser <= {max_v}")
            return value
    if val.startswith("{") or val.startswith("["):
        return json.loads(val)
    if val.isdigit():
        return int(val)
    return val


@bp.route("/")
@login_required
@admin_required
def index():
    settings = {s.key: s for s in Setting.query.all()}
    branches = Branch.query.order_by(Branch.name).all()
    return render_template("admin/config.html", settings=settings, branches=branches)


@bp.route("/setting/<key>", methods=["POST"])
@login_required
@admin_required
def update_setting(key):
    val = request.form.get("value", "").strip()
    try:
        value = _parse_setting_value(key, val)
    except Exception as e:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"status": "error", "message": f"Valor inválido en {key}: {e}"}, 400
        flash(f"Valor inválido en {key}: {e}", "danger")
        return redirect(url_for("settings.index"))
    
    set_setting(key, value)
    
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return {"status": "success", "message": "Configuración actualizada."}
        
    flash("Configuración actualizada.", "success")
    return redirect(url_for("settings.index"))


@bp.route("/bulk-settings", methods=["POST"])
@login_required
@admin_required
def bulk_settings():
    """Actualiza múltiples configuraciones a la vez."""
    settings_data = request.form.to_dict()
    errors = []
    
    for key, val in settings_data.items():
        if key == "csrf_token":
            continue
        val = val.strip()
        try:
            value = _parse_setting_value(key, val)
            set_setting(key, value)
        except Exception as e:
            errors.append(f"{key}: {str(e)}")
            
    if errors:
        msg = "Algunos errores: " + ", ".join(errors)
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"status": "error", "message": msg}, 400
        flash(msg, "warning")
    else:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return {"status": "success", "message": "Configuraciones actualizadas."}
        flash("Configuraciones actualizadas.", "success")
        
    return redirect(url_for("settings.index"))


@bp.route("/branch/new", methods=["GET", "POST"])
@login_required
@admin_required
def branch_new():
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code") or None
        address = request.form.get("address") or None
        if name:
            b = Branch(name=name, code=code, address=address)
            db.session.add(b)
            db.session.commit()
            flash("Sucursal creada.", "success")
            return redirect(url_for("settings.index"))
    return render_template("admin/branch_form.html", branch=None)


@bp.route("/branch/<id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def branch_edit(id):
    branch = Branch.query.get_or_404(id)
    if request.method == "POST":
        branch.name = request.form.get("name", branch.name)
        branch.code = request.form.get("code") or None
        branch.address = request.form.get("address") or None
        branch.active = request.form.get("active") == "on"
        db.session.commit()
        flash("Sucursal actualizada.", "success")
        return redirect(url_for("settings.index"))
    return render_template("admin/branch_form.html", branch=branch)
