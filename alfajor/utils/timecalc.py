"""Utilidades de cálculo de tiempo."""

from decimal import Decimal, ROUND_HALF_UP


def shift_hours(start_time, end_time) -> Decimal:
    """Calcula horas decimales entre dos tiempos.

    Soporta turnos que cruzan medianoche (si end < start, suma 24h).
    Retorna Decimal con 2 decimales.
    """
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    if end_minutes < start_minutes:
        end_minutes += 24 * 60
    minutes = end_minutes - start_minutes
    hours = Decimal(minutes) / Decimal(60)
    return hours.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
