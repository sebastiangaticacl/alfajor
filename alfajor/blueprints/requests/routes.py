"""Rutas solicitudes."""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from alfajor.utils.decorators import encargado_or_admin
from alfajor.blueprints.requests import bp
from alfajor.extensions import db
from alfajor.models import ShiftRequest, Shift, Employee
from alfajor.enums import RequestType, RequestStatus
from datetime import datetime


@bp.route("/")
@login_required
def list():
    if current_user.role in ("ADMIN", "ENCARGADO"):
        requests = ShiftRequest.query.order_by(ShiftRequest.created_at.desc()).all()
    else:
        requests = ShiftRequest.query.filter_by(employee_id=current_user.employee_id).order_by(ShiftRequest.created_at.desc()).all() if current_user.employee_id else []
    return render_template("requests/list.html", requests=requests)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if not current_user.employee_id:
        flash("Debes estar vinculado a un empleado.", "danger")
        return redirect(url_for("requests.list"))
    if request.method == "POST":
        req_type = request.form.get("request_type", RequestType.DIA_LIBRE.value)
        requested_date = request.form.get("requested_date")
        reason = request.form.get("reason", "")
        try:
            dt = datetime.strptime(requested_date, "%Y-%m-%d").date() if requested_date else None
        except ValueError:
            dt = None
        r = ShiftRequest(
            employee_id=current_user.employee_id,
            request_type=req_type,
            requested_date=dt,
            reason=reason,
            status=RequestStatus.PENDIENTE.value,
        )
        db.session.add(r)
        db.session.commit()
        flash("Solicitud creada.", "success")
        return redirect(url_for("requests.list"))
    return render_template("requests/form.html", request_obj=None)


@bp.route("/<id>/approve", methods=["POST"])
@login_required
@encargado_or_admin
def approve(id):
    r = ShiftRequest.query.get_or_404(id)
    r.status = RequestStatus.APROBADO.value
    r.reviewed_by = current_user.id
    r.reviewed_at = datetime.utcnow()
    r.review_comment = request.form.get("comment", "")
    db.session.commit()
    flash("Solicitud aprobada.", "success")
    return redirect(url_for("requests.list"))


@bp.route("/<id>/reject", methods=["POST"])
@login_required
@encargado_or_admin
def reject(id):
    r = ShiftRequest.query.get_or_404(id)
    r.status = RequestStatus.RECHAZADO.value
    r.reviewed_by = current_user.id
    r.reviewed_at = datetime.utcnow()
    r.review_comment = request.form.get("comment", "")
    db.session.commit()
    flash("Solicitud rechazada.", "success")
    return redirect(url_for("requests.list"))
