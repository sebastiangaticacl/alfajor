"""Rutas reportes / export."""

from datetime import date
from io import StringIO
import csv
from flask import Response, request
from flask_login import login_required
from alfajor.utils.decorators import contabilidad_or_admin
from alfajor.blueprints.reports import bp
from alfajor.models import PayStatement, PayLine, PerformanceSnapshot
from alfajor.services.ranking_calculator import build_ranking


@bp.route("/payroll/csv")
@login_required
@contabilidad_or_admin
def payroll_csv():
    period_id = request.args.get("period_id")
    if not period_id:
        return "period_id requerido", 400
    statements = PayStatement.query.filter_by(pay_period_id=period_id).all()
    si = StringIO()
    w = csv.writer(si)
    w.writerow(["Empleado", "Total base", "Total calculado", "Estado"])
    for st in statements:
        w.writerow([
            st.employee.full_name,
            float(st.total_base_hours),
            float(st.total_calculated),
            st.reconciliation_status,
        ])
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={
        "Content-Disposition": "attachment; filename=payroll.csv"
    })


@bp.route("/ranking/csv")
@login_required
@contabilidad_or_admin
def ranking_csv():
    start = request.args.get("start")
    end = request.args.get("end")
    preset = request.args.get("preset", "BALANCEADO")
    if not start or not end:
        return "start y end requeridos", 400
    try:
        start_d = date.fromisoformat(start)
        end_d = date.fromisoformat(end)
    except ValueError:
        return "Fechas inválidas", 400
    results = build_ranking(start_d, end_d, preset=preset)
    si = StringIO()
    w = csv.writer(si)
    w.writerow(["Posición", "Nombre", "Score", "Horas", "Turnos", "Atrasos", "Ausencias"])
    for i, r in enumerate(results, 1):
        w.writerow([i, r["employee"].full_name, r["score"], r["total_hours"], r["shifts_completed"], r["late_minutes"], r["absences"]])
    output = si.getvalue()
    return Response(output, mimetype="text/csv", headers={
        "Content-Disposition": "attachment; filename=ranking.csv"
    })
