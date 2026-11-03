"""Pruebas de contrato del traductor anticorrupción de Meta.

docs/13-plan-v2.md → Tarea 1.5. Una prueba de contrato por fixture
(texto, imagen, documento, audio, interactivo, acuses sueltos), la
prueba del payload mixto que verifica la separación mensajes/acuses
(hallazgo F12) y la prueba estructural, verbatim del plan, que
verifica que ningún módulo fuera del traductor conoce el formato de
Meta.

**Los fixtures son PROVISIONALES.** La cuenta de Meta de H0 todavía no
existe (ver docs/13-plan-v2.md → H0), así que no hay payloads reales
que capturar todavía. Cada archivo en `tests/contract/fixtures/` lleva
el sufijo `_provisional` en el nombre y un campo `"_note"` en el JSON
explicándolo. Se construyeron a partir de la forma documentada por
Meta para los webhooks de WhatsApp Cloud API (confirmada vía Context7
contra `/dogalyir/whatsapp-cloud-api-types`, que sigue la estructura
`object`/`entry[]`/`changes[]`/`value` de developers.facebook.com), no
de una invención propia ni de una captura real. **Se reemplazan por
capturas reales en la Tarea 1.10**; hasta entonces estas pruebas
verifican coherencia interna del traductor, no fidelidad byte a byte
al formato real de Meta.

Estas pruebas importan `app.channel._internal.meta.translator`
directamente en vez de pasar por `app.channel` (la interfaz pública
del módulo): `to_domain` es un detalle interno de la ingesta
(consumido por `app/channel/_internal/inbox.py` en la Tarea 1.7, que
vive en el mismo árbol `_internal`) y no necesita cruzar la frontera
pública del módulo todavía. `import-linter` no vigila `tests/`
(`root_package = app`), así que este import directo no viola el
contrato de capas.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.channel._internal.meta.translator import (
    InboundMessage,
    ParsedWebhook,
    StatusUpdate,
    to_domain,
)
from app.core.errors import InvalidMetaPayload

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def _ts(epoch: int) -> datetime:
    return datetime.fromtimestamp(epoch, tz=UTC)


# ---------------------------------------------------------------------------
# Una prueba de contrato por payload.
# ---------------------------------------------------------------------------


def test_mensaje_de_texto():
    """POSITIVA."""
    parsed = to_domain(_load("mensaje_texto_provisional.json"))
    assert isinstance(parsed, ParsedWebhook)
    assert parsed.statuses == []
    assert len(parsed.messages) == 1

    msg = parsed.messages[0]
    assert isinstance(msg, InboundMessage)
    assert msg.wa_message_id == "wamid.texto_0001"
    assert msg.wa_id == "5214793066911"
    assert msg.phone_number_id == "277011111111111"
    assert msg.kind == "text"
    assert msg.text == "Hola, quiero confirmar mi cita"
    assert msg.media_id is None
    assert msg.interactive_reply is None
    assert msg.sent_at == _ts(1738000000)


def test_mensaje_de_imagen():
    """POSITIVA."""
    parsed = to_domain(_load("mensaje_imagen_provisional.json"))
    assert len(parsed.messages) == 1

    msg = parsed.messages[0]
    assert msg.kind == "image"
    assert msg.media_id == "2754859441498128"
    assert msg.text is None
    assert msg.interactive_reply is None


def test_mensaje_de_documento():
    """POSITIVA."""
    parsed = to_domain(_load("mensaje_documento_provisional.json"))
    assert len(parsed.messages) == 1

    msg = parsed.messages[0]
    assert msg.kind == "document"
    assert msg.media_id == "3865970552609239"


def test_mensaje_de_audio():
    """POSITIVA."""
    parsed = to_domain(_load("mensaje_audio_provisional.json"))
    assert len(parsed.messages) == 1

    msg = parsed.messages[0]
    assert msg.kind == "audio"
    assert msg.media_id == "4976081663710340"


def test_mensaje_interactivo_de_boton():
    """POSITIVA."""
    parsed = to_domain(_load("mensaje_interactivo_boton_provisional.json"))
    assert len(parsed.messages) == 1

    msg = parsed.messages[0]
    assert msg.kind == "interactive"
    assert msg.interactive_reply == "confirmar_cita"
    assert msg.text is None
    assert msg.media_id is None


def test_acuses_sueltos_sent_y_read():
    """POSITIVA. Payload de solo acuses, sin messages[]."""
    parsed = to_domain(_load("acuses_sent_read_provisional.json"))
    assert parsed.messages == []
    assert len(parsed.statuses) == 2

    sent, read = parsed.statuses
    assert isinstance(sent, StatusUpdate)
    assert sent.wa_message_id == "wamid.acuse_sent_0001"
    assert sent.status == "sent"
    assert sent.error_code is None
    assert sent.occurred_at == _ts(1738000200)

    assert read.wa_message_id == "wamid.acuse_read_0001"
    assert read.status == "read"


# ---------------------------------------------------------------------------
# El caso crítico (F12): 3 mensajes y 2 acuses en el mismo payload.
# ---------------------------------------------------------------------------


def test_payload_mixto_separa_mensajes_y_acuses():
    """POSITIVA. Hallazgo F12 -- el caso que rompe implementaciones ingenuas.

    `entry[].changes[].value.messages[]` y
    `entry[].changes[].value.statuses[]` vienen juntos en el mismo
    `value`. El traductor debe repartirlos: 3 mensajes a `.messages`,
    2 acuses a `.statuses`, sin mezclarlos ni descartar ninguno.
    """
    parsed = to_domain(_load("mixto_3_mensajes_2_acuses_provisional.json"))

    assert len(parsed.messages) == 3
    assert len(parsed.statuses) == 2

    kinds = [m.kind for m in parsed.messages]
    assert kinds == ["text", "image", "interactive"]
    assert parsed.messages[0].text == "Se me movio la cita?"
    assert parsed.messages[1].media_id == "2754859441498129"
    assert parsed.messages[2].interactive_reply == "reagendar_manana"

    statuses = [s.status for s in parsed.statuses]
    assert statuses == ["delivered", "failed"]
    assert parsed.statuses[0].error_code is None
    assert parsed.statuses[1].error_code == 131047

    # Ningun mensaje se coló entre los acuses ni viceversa.
    assert {m.wa_message_id for m in parsed.messages}.isdisjoint(
        {s.wa_message_id for s in parsed.statuses}
    )


# ---------------------------------------------------------------------------
# Payload desconocido o malformado -> excepción tipada, nunca KeyError.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param([], id="no_es_un_objeto"),
        pytest.param({"object": "whatsapp_business_account"}, id="falta_entry"),
        pytest.param({"entry": "no_soy_una_lista"}, id="entry_no_es_lista"),
        pytest.param({"entry": [{"id": "1"}]}, id="falta_changes"),
        pytest.param({"entry": [{"id": "1", "changes": [{}]}]}, id="falta_value"),
        pytest.param(
            {"entry": [{"id": "1", "changes": [{"value": {"messaging_product": "whatsapp"}}]}]},
            id="falta_metadata",
        ),
        pytest.param(
            {
                "entry": [
                    {
                        "id": "1",
                        "changes": [
                            {
                                "value": {
                                    "messaging_product": "whatsapp",
                                    "metadata": {"display_phone_number": "1"},
                                }
                            }
                        ],
                    }
                ]
            },
            id="falta_phone_number_id",
        ),
        pytest.param(
            {
                "entry": [
                    {
                        "id": "1",
                        "changes": [
                            {
                                "value": {
                                    "metadata": {"phone_number_id": "277011111111111"},
                                    "messages": [
                                        {
                                            "from": "5214793066911",
                                            "id": "wamid.x",
                                            "timestamp": "1738000000",
                                            "type": "sticker",
                                        }
                                    ],
                                }
                            }
                        ],
                    }
                ]
            },
            id="tipo_de_mensaje_desconocido",
        ),
        pytest.param(
            {
                "entry": [
                    {
                        "id": "1",
                        "changes": [
                            {
                                "value": {
                                    "metadata": {"phone_number_id": "277011111111111"},
                                    "messages": [
                                        {
                                            "from": "5214793066911",
                                            "timestamp": "1738000000",
                                            "type": "text",
                                            "text": {"body": "hola"},
                                        }
                                    ],
                                }
                            }
                        ],
                    }
                ]
            },
            id="falta_id_del_mensaje",
        ),
        pytest.param(
            {
                "entry": [
                    {
                        "id": "1",
                        "changes": [
                            {
                                "value": {
                                    "metadata": {"phone_number_id": "277011111111111"},
                                    "messages": [
                                        {
                                            "from": "5214793066911",
                                            "id": "wamid.x",
                                            "timestamp": "1738000000",
                                            "type": "text",
                                        }
                                    ],
                                }
                            }
                        ],
                    }
                ]
            },
            id="falta_text_body",
        ),
        pytest.param(
            {
                "entry": [
                    {
                        "id": "1",
                        "changes": [
                            {
                                "value": {
                                    "metadata": {"phone_number_id": "277011111111111"},
                                    "statuses": [
                                        {
                                            "id": "wamid.x",
                                            "status": "sent",
                                            "timestamp": "no-es-numero",
                                        }
                                    ],
                                }
                            }
                        ],
                    }
                ]
            },
            id="timestamp_invalido",
        ),
    ],
)
def test_payload_desconocido_o_malformado_lanza_excepcion_tipada(payload):
    """NEGATIVA. Nunca un `KeyError`: siempre `InvalidMetaPayload`."""
    with pytest.raises(InvalidMetaPayload):
        to_domain(payload)


def test_la_excepcion_tipada_no_es_un_keyerror():
    """NEGATIVA. Refuerza explícitamente lo que pide la tarea."""
    try:
        to_domain({})
    except InvalidMetaPayload as exc:
        assert not isinstance(exc, KeyError)
    else:
        pytest.fail("to_domain({}) debió lanzar InvalidMetaPayload")


# ---------------------------------------------------------------------------
# Prueba estructural -- verbatim de docs/13-plan-v2.md, Tarea 1.5, Paso 3.
# ---------------------------------------------------------------------------


def test_ningun_modulo_fuera_del_traductor_conoce_el_formato_de_meta():
    """NEGATIVA."""
    prohibido = ("entry", "changes", "messaging_product", "statuses")
    for ruta in Path("app").rglob("*.py"):
        if "channel/_internal/meta" in str(ruta).replace("\\", "/"):
            continue
        texto = ruta.read_text(encoding="utf-8")
        for clave in prohibido:
            assert f'"{clave}"' not in texto, f"{ruta} manipula el JSON de Meta"


def test_un_acuse_desconocido_se_ignora_sin_tumbar_el_payload() -> None:
    """NEGATIVA. Meta emite estados que no modelamos (p. ej. 'deleted') y puede
    anadir mas sin avisar. Como los acuses viajan en el mismo payload que los
    mensajes, lanzar ante uno desconocido descartaria mensajes validos y dejaria
    la ingesta caida ante trafico legitimo."""
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WABA_ID",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15550001111",
                                "phone_number_id": "PNID_1",
                            },
                            "statuses": [
                                {
                                    "id": "wamid.CONOCIDO",
                                    "status": "delivered",
                                    "timestamp": "1755000000",
                                    "recipient_id": "5214793066911",
                                },
                                {
                                    "id": "wamid.DESCONOCIDO",
                                    "status": "deleted",
                                    "timestamp": "1755000001",
                                    "recipient_id": "5214793066911",
                                },
                            ],
                        },
                    }
                ],
            }
        ],
    }

    resultado = to_domain(payload)

    assert len(resultado.statuses) == 1
    assert resultado.statuses[0].wa_message_id == "wamid.CONOCIDO"
    assert resultado.statuses[0].status == "delivered"
