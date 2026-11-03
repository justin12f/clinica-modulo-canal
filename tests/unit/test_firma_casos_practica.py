"""Casos normal, límite y error de la verificación de firma (Paso 4 de la práctica).

CA-1.4: un webhook con firma válida se acepta; uno con firma inválida, sin
firma o con el cuerpo alterado se rechaza. La comparación es sobre el cuerpo
crudo, en tiempo constante.
"""

from __future__ import annotations

import json

from app.channel import sign_body, verify_signature

SECRETO = "secreto-de-prueba"


def test_normal_firma_valida_se_acepta() -> None:
    cuerpo = json.dumps({"object": "whatsapp_business_account", "entry": []}).encode()
    assert verify_signature(cuerpo, sign_body(cuerpo, SECRETO), SECRETO)


def test_limite_cuerpo_vacio_con_firma_correcta_se_acepta() -> None:
    assert verify_signature(b"", sign_body(b"", SECRETO), SECRETO)


def test_limite_mismo_json_reserializado_no_verifica() -> None:
    """La firma es del cuerpo crudo: un espacio de diferencia cambia el digest."""
    original = b'{"a":1,"b":2}'
    reserializado = b'{"a": 1, "b": 2}'
    assert not verify_signature(reserializado, sign_body(original, SECRETO), SECRETO)


def test_error_cuerpo_alterado_se_rechaza() -> None:
    firma = sign_body(b'{"monto":1}', SECRETO)
    assert not verify_signature(b'{"monto":9}', firma, SECRETO)


def test_error_sin_cabecera_se_rechaza() -> None:
    assert not verify_signature(b"{}", None, SECRETO)


def test_error_cabecera_sin_prefijo_se_rechaza() -> None:
    digest = sign_body(b"{}", SECRETO).removeprefix("sha256=")
    assert not verify_signature(b"{}", digest, SECRETO)


def test_error_secreto_distinto_se_rechaza() -> None:
    assert not verify_signature(b"{}", sign_body(b"{}", "otro"), SECRETO)
