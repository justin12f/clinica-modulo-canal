"""Un despliegue sin `META_APP_SECRET` no acepta webhooks: con la clave vacia
cualquiera calcula la HMAC valida."""

from __future__ import annotations

from app.channel._internal.meta.signature import sign_body, verify_signature


def test_secreto_vacio_rechaza_la_firma_hecha_con_el() -> None:
    cuerpo = b'{"entry":[]}'
    assert not verify_signature(cuerpo, sign_body(cuerpo, ""), "")


def test_con_secreto_la_firma_propia_verifica() -> None:
    cuerpo = b'{"entry":[]}'
    assert verify_signature(cuerpo, sign_body(cuerpo, "secreto"), "secreto")
