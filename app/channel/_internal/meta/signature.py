"""Verificación de la firma HMAC de los webhooks de Meta.

Meta firma cada entrega con `X-Hub-Signature-256`: HMAC-SHA256 del **cuerpo
crudo** con el app secret. Verificar sobre el JSON reserializado no funciona —
cualquier diferencia de espaciado o de orden de claves cambia el digest.
"""

from __future__ import annotations

import hashlib
import hmac

__all__ = ["sign_body", "verify_signature"]

_PREFIJO = "sha256="


def sign_body(body: bytes, app_secret: str) -> str:
    """Produce la cabecera tal como la manda Meta. Existe para las pruebas: sin
    esto habría que copiar digests a mano y nadie sabría si son correctos."""
    digest = hmac.new(app_secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return _PREFIJO + digest


def verify_signature(body: bytes, header: str | None, app_secret: str) -> bool:
    """Compara en tiempo constante.

    `compare_digest` en lugar de `==` porque una comparación que corta al primer
    byte distinto filtra, en el tiempo de respuesta, cuántos bytes acertó quien
    lo intenta. Con un endpoint público eso es un oráculo.
    """
    # Sin secreto no hay firma que verificar: con la clave vacia, cualquiera
    # calcula la HMAC valida. Pasa en un despliegue sin cuenta de Meta todavia.
    if not app_secret or not header or not header.startswith(_PREFIJO):
        return False
    esperado = sign_body(body, app_secret)
    return hmac.compare_digest(esperado, header)
