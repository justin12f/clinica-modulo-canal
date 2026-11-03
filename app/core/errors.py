"""Excepciones base del dominio.

Extraído de `clinic-managment-agent/app/core/errors.py`. Sólo se conservan
los tipos que usa el módulo de recepción del canal.

Invariante 11: ningún mensaje de excepción lleva contenido clínico ni texto
de paciente; sólo identificadores y tipos de evento.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base de las excepciones de dominio de la aplicación."""


class InvalidMetaPayload(DomainError):
    """Un payload de webhook de Meta no tiene la forma esperada.

    Lo lanza únicamente `app/channel/_internal/meta/translator.py`, el único
    módulo que conoce la forma del JSON de Meta. `reason` describe qué campo
    faltaba; nunca lleva el contenido del payload.
    """

    def __init__(self, reason: str) -> None:
        super().__init__(f"payload de Meta inválido: {reason}")
        self.reason = reason
