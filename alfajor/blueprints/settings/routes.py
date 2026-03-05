"""Rutas configuración."""

from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required
from alfajor.utils.decorators import admin_required
from alfajor.blueprints.settings import bp
from alfajor.extensions import db
from alfajor.models import Setting, Branch
from alfajor.services.settings_service import get_setting, set_setting


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
    import json
    val = request.form.get("value", "").strip()
    try:
        if val.startswith("{") or val.startswith("["):
            value = json.loads(val)
        elif val.isdigit():
            value = int(val)
        elif val.replace(".", "", 1).replace("-", "", 1).isdigit():
            value = float(val)
        else:
            value = val
    except json.JSONDecodeError as e:
        flash(f"JSON inválido en {key}: {e}", "danger")
        return redirect(url_for("settings.index"))
    except Exception:
        value = val
    set_setting(key, value)
    flash("Configuración actualizada.", "success")
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
