#!/usr/bin/env python3
"""
Popula las descripciones de los settings existentes para ALFAJOR.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from alfajor import create_app
from alfajor.extensions import db
from alfajor.models import Setting

DESCRIPTIONS = {
    "rules.max_weekly_hours": "Máximo de horas semanales permitidas por empleado.",
    "rules.min_rest_hours": "Mínimo de horas de descanso entre turnos.",
    "rules.max_consecutive_days": "Máximo de días consecutivos de trabajo permitidos.",
    "rules.overtime_threshold_hours": "Umbral de horas diarias para considerar sobretiempo.",
    "rules.overtime_multiplier": "Multiplicador para el pago de horas extra.",
    "schedule.hours": "Horarios de apertura y cierre por cada día de la semana.",
    "shift_roles": "Cargos/roles disponibles para asignar en los turnos."
}

def update_descriptions():
    app = create_app()
    with app.app_context():
        for key, desc in DESCRIPTIONS.items():
            s = Setting.query.filter_by(key=key).first()
            if s:
                s.description = desc
                print(f"Actualizado: {key}")
            else:
                print(f"No encontrado: {key}")
        db.session.commit()
        print("Finalizado.")

if __name__ == "__main__":
    update_descriptions()
