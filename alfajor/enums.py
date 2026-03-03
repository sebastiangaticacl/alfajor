"""
Enums centralizados para ALFAJOR.
"""

from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    ENCARGADO = "ENCARGADO"
    CONTABILIDAD = "CONTABILIDAD"
    TRABAJADOR = "TRABAJADOR"


class WeekStatus(str, Enum):
    BORRADOR = "BORRADOR"
    PUBLICADA = "PUBLICADA"
    CERRADA = "CERRADA"


class ShiftStatus(str, Enum):
    PLANIFICADO = "PLANIFICADO"
    CONFIRMADO = "CONFIRMADO"
    COMPLETADO = "COMPLETADO"
    AUSENTE = "AUSENTE"
    ANULADO = "ANULADO"


class PayPeriodStatus(str, Enum):
    ABIERTO = "ABIERTO"
    EN_REVISION = "EN_REVISION"
    APROBADO = "APROBADO"
    PAGADO = "PAGADO"
    CERRADO = "CERRADO"


class PayPeriodType(str, Enum):
    SEMANAL = "SEMANAL"
    QUINCENAL = "QUINCENAL"
    MENSUAL = "MENSUAL"


class ReconciliationStatus(str, Enum):
    PENDIENTE = "PENDIENTE"
    PARCIAL = "PARCIAL"
    PAGADO = "PAGADO"
    DIFERENCIA = "DIFERENCIA"


class PayLineType(str, Enum):
    BASE_HOURS = "BASE_HOURS"
    OVERTIME = "OVERTIME"
    SURCHARGE = "SURCHARGE"
    BONUS = "BONUS"
    DEDUCTION = "DEDUCTION"


class PaymentMethod(str, Enum):
    TRANSFER = "TRANSFER"
    CASH = "CASH"
    CHECK = "CHECK"


class RequestType(str, Enum):
    CAMBIO_TURNO = "CAMBIO_TURNO"
    DIA_LIBRE = "DIA_LIBRE"
    SWAP = "SWAP"


class RequestStatus(str, Enum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"


class AttendanceEventType(str, Enum):
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    LATE = "LATE"
    ABSENT = "ABSENT"
    INCIDENT = "INCIDENT"


class ScorePreset(str, Enum):
    BALANCEADO = "BALANCEADO"
    PUNTUALIDAD = "PUNTUALIDAD"
    ESTABILIDAD = "ESTABILIDAD"


class EmployeeStatus(str, Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
