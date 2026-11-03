"""Interfaz pública del módulo `channel` (M1 · recepción de webhooks).

Nada fuera de `app.channel` importa `app.channel._internal.*`: todo pasa por
aquí. Este repositorio contiene sólo la parte de recepción del primer
incremento (H1): verificar la firma de Meta y traducir su payload a objetos
de dominio.
"""

from __future__ import annotations

from app.channel._internal.meta.signature import sign_body, verify_signature
from app.channel._internal.meta.translator import (
    InboundMessage,
    ParsedWebhook,
    StatusUpdate,
    to_domain,
)

__all__ = [
    "InboundMessage",
    "ParsedWebhook",
    "StatusUpdate",
    "sign_body",
    "to_domain",
    "verify_signature",
]
