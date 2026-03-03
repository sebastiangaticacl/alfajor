"""Rutas ranking."""

from datetime import date, timedelta
from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from alfajor.blueprints.ranking import bp
from alfajor.services.ranking_calculator import build_ranking, calculate_score


@bp.route("/")
@login_required
def index():
    if current_user.role == "TRABAJADOR":
        return redirect(url_for("ranking.my_score"))
    period_start = request.args.get("start")
    period_end = request.args.get("end")
    preset = request.args.get("preset", "BALANCEADO")
    branch_id = request.args.get("branch") or None
    shift_role = request.args.get("role") or None
    if not period_start or not period_end:
        today = date.today()
        period_start = (today - timedelta(days=30)).isoformat()
        period_end = today.isoformat()
    try:
        start_d = date.fromisoformat(period_start)
        end_d = date.fromisoformat(period_end)
    except ValueError:
        start_d = date.today() - timedelta(days=30)
        end_d = date.today()
    results = build_ranking(start_d, end_d, branch_id, shift_role, preset)
    return render_template(
        "admin/ranking.html",
        results=results,
        period_start=start_d,
        period_end=end_d,
        preset=preset,
    )


@bp.route("/my")
@login_required
def my_score():
    if not current_user.employee_id:
        return render_template("admin/my_score.html", data=None)
    today = date.today()
    start_d = today - timedelta(days=30)
    data = calculate_score(current_user.employee_id, start_d, today, "BALANCEADO")
    data["employee"] = current_user.employee
    return render_template("admin/my_score.html", data=data)
