"""Capa anticorrupción del formato de Meta.

CLAUDE.md → "Por qué existe esta capa": el JSON de los webhooks de
Meta es anidado, ambiguo y cambia sin avisar. Este módulo es el
**único** sitio del sistema que conoce esa forma, y ahí muere. Fuera
de `app/channel/_internal/meta/`, nadie ve un diccionario de Meta: el
dominio solo conoce `ParsedWebhook`, `InboundMessage` y `StatusUpdate`.
Lo vigila la prueba estructural
`test_ningun_modulo_fuera_del_traductor_conoce_el_formato_de_meta` en
`tests/contract/test_payloads_meta.py`.

docs/13-plan-v2.md → Tarea 1.5, hallazgo F12: un solo payload de Meta
trae **N mensajes y M acuses a la vez** —
`entry[].changes[].value.messages[]` y
`entry[].changes[].value.statuses[]` son arreglos hermanos dentro del
mismo `value`, no ramas mutuamente excluyentes. `to_domain` recorre
cada `value` una sola vez y reparte cada arreglo a su lista de salida
(`.messages` / `.statuses`); no asume que un payload trae solo uno de
los dos.

Un payload desconocido o malformado lanza `InvalidMetaPayload`
(`app/core/errors.py`), nunca un `KeyError` — de ahí que todo acceso a
una clave opcional o de forma incierta pase por `dict.get(...)` con
validación explícita del tipo, en vez de indexado directo (`payload["entry"]`).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from app.core.errors import InvalidMetaPayload

MessageKind = Literal["text", "image", "document", "audio", "interactive"]
MessageStatus = Literal["sent", "delivered", "read", "failed"]

_KNOWN_MESSAGE_KINDS: frozenset[str] = frozenset(
    {"text", "image", "document", "audio", "interactive"}
)
_KNOWN_STATUSES: frozenset[str] = frozenset({"sent", "delivered", "read", "failed"})
_MEDIA_KINDS: frozenset[str] = frozenset({"image", "document", "audio"})


class InboundMessage(BaseModel):
    """Un mensaje entrante, ya traducido a la forma que conoce el dominio.

    El contenido va en el campo que corresponde a `kind`: `text` para
    `kind="text"`, `media_id` para `image`/`document`/`audio`,
    `interactive_reply` para `interactive` (el `id` del botón o de la
    fila de lista elegida — nunca el título, que es texto libre
    redactado por el paciente/médico, no un identificador estable).
    """

    model_config = ConfigDict(frozen=True)

    wa_message_id: str
    wa_id: str
    phone_number_id: str
    kind: MessageKind
    sent_at: datetime
    text: str | None = None
    media_id: str | None = None
    interactive_reply: str | None = None


class StatusUpdate(BaseModel):
    """Un acuse de entrega/lectura de un mensaje saliente."""

    model_config = ConfigDict(frozen=True)

    wa_message_id: str
    phone_number_id: str
    status: MessageStatus
    occurred_at: datetime
    error_code: int | None = None


class ParsedWebhook(BaseModel):
    """Resultado de `to_domain`: mensajes y acuses ya separados.

    Un mismo payload puede traer ambas listas a la vez (F12) — ninguna
    implica la ausencia de la otra.
    """

    model_config = ConfigDict(frozen=True)

    messages: list[InboundMessage] = Field(default_factory=list)
    statuses: list[StatusUpdate] = Field(default_factory=list)


def to_domain(payload: dict[str, Any]) -> ParsedWebhook:
    """Traduce un payload crudo de webhook de Meta a `ParsedWebhook`.

    Recorre `entry[].changes[].value` y, por cada `value`, separa
    `messages[]` en `.messages` y `statuses[]` en `.statuses` — ambos
    pueden venir juntos en el mismo `value` (F12). Lanza
    `InvalidMetaPayload` ante cualquier forma que no reconoce; nunca
    deja escapar un `KeyError`/`TypeError` de acceso a diccionario.
    """
    if not isinstance(payload, dict):
        raise InvalidMetaPayload("el payload no es un objeto JSON")

    entries = payload.get("entry")
    if not isinstance(entries, list):
        raise InvalidMetaPayload("falta 'entry' o no es una lista")

    messages: list[InboundMessage] = []
    statuses: list[StatusUpdate] = []

    for entry in entries:
        if not isinstance(entry, dict):
            raise InvalidMetaPayload("un elemento de 'entry[]' no es un objeto")

        changes = entry.get("changes")
        if not isinstance(changes, list):
            raise InvalidMetaPayload("falta 'entry[].changes' o no es una lista")

        for change in changes:
            if not isinstance(change, dict):
                raise InvalidMetaPayload("un elemento de 'changes[]' no es un objeto")

            value = change.get("value")
            if not isinstance(value, dict):
                raise InvalidMetaPayload("falta 'changes[].value' o no es un objeto")

            phone_number_id = _extract_phone_number_id(value)

            raw_messages = value.get("messages", [])
            if raw_messages is None:
                raw_messages = []
            if not isinstance(raw_messages, list):
                raise InvalidMetaPayload("'value.messages' no es una lista")
            for raw_message in raw_messages:
                messages.append(_parse_message(raw_message, phone_number_id))

            raw_statuses = value.get("statuses", [])
            if raw_statuses is None:
                raw_statuses = []
            if not isinstance(raw_statuses, list):
                raise InvalidMetaPayload("'value.statuses' no es una lista")
            for raw_status in raw_statuses:
                parsed_status = _parse_status(raw_status, phone_number_id)
                if parsed_status is not None:
                    statuses.append(parsed_status)

    return ParsedWebhook(messages=messages, statuses=statuses)


def _extract_phone_number_id(value: dict[str, Any]) -> str:
    metadata = value.get("metadata")
    if not isinstance(metadata, dict):
        raise InvalidMetaPayload("falta 'value.metadata' o no es un objeto")

    phone_number_id = metadata.get("phone_number_id")
    if not isinstance(phone_number_id, str) or not phone_number_id:
        raise InvalidMetaPayload("falta 'value.metadata.phone_number_id'")

    return phone_number_id


def _parse_message(raw: object, phone_number_id: str) -> InboundMessage:
    if not isinstance(raw, dict):
        raise InvalidMetaPayload("un elemento de 'messages[]' no es un objeto")

    wa_message_id = raw.get("id")
    if not isinstance(wa_message_id, str) or not wa_message_id:
        raise InvalidMetaPayload("falta 'messages[].id'")

    wa_id = raw.get("from")
    if not isinstance(wa_id, str) or not wa_id:
        raise InvalidMetaPayload("falta 'messages[].from'")

    raw_kind = raw.get("type")
    if raw_kind not in _KNOWN_MESSAGE_KINDS:
        raise InvalidMetaPayload(f"tipo de mensaje desconocido: {raw_kind!r}")
    kind: MessageKind = raw_kind  # ya validado contra _KNOWN_MESSAGE_KINDS

    sent_at = _parse_timestamp(raw.get("timestamp"))

    text: str | None = None
    media_id: str | None = None
    interactive_reply: str | None = None

    if kind == "text":
        body = raw.get("text")
        if not isinstance(body, dict) or not isinstance(body.get("body"), str):
            raise InvalidMetaPayload("falta 'messages[].text.body'")
        text = body["body"]
    elif kind in _MEDIA_KINDS:
        media = raw.get(kind)
        if not isinstance(media, dict) or not isinstance(media.get("id"), str):
            raise InvalidMetaPayload(f"falta 'messages[].{kind}.id'")
        media_id = media["id"]
    elif kind == "interactive":
        interactive = raw.get("interactive")
        if not isinstance(interactive, dict):
            raise InvalidMetaPayload("falta 'messages[].interactive'")
        interactive_reply = _extract_interactive_reply(interactive)

    return InboundMessage(
        wa_message_id=wa_message_id,
        wa_id=wa_id,
        phone_number_id=phone_number_id,
        kind=kind,
        sent_at=sent_at,
        text=text,
        media_id=media_id,
        interactive_reply=interactive_reply,
    )


def _extract_interactive_reply(interactive: dict[str, Any]) -> str:
    sub_kind = interactive.get("type")
    if sub_kind == "button_reply":
        reply = interactive.get("button_reply")
    elif sub_kind == "list_reply":
        reply = interactive.get("list_reply")
    else:
        raise InvalidMetaPayload(f"subtipo interactivo desconocido: {sub_kind!r}")

    if not isinstance(reply, dict) or not isinstance(reply.get("id"), str):
        raise InvalidMetaPayload(f"falta el 'id' de '{sub_kind}'")

    reply_id: str = reply["id"]
    return reply_id


def _parse_status(raw: object, phone_number_id: str) -> StatusUpdate | None:
    """`phone_number_id` viaja tambien en el acuse.

    Sin el, un payload que trae solo `statuses[]` —lo normal para los acuses de
    un mensaje saliente— no se puede enrutar a ninguna clinica: el worker
    resuelve el tenant por ese identificador y `StatusUpdate` era el unico
    objeto del traductor que lo tiraba a la basura teniendolo a mano.
    """
    if not isinstance(raw, dict):
        raise InvalidMetaPayload("un elemento de 'statuses[]' no es un objeto")

    wa_message_id = raw.get("id")
    if not isinstance(wa_message_id, str) or not wa_message_id:
        raise InvalidMetaPayload("falta 'statuses[].id'")

    raw_status = raw.get("status")
    if raw_status not in _KNOWN_STATUSES:
        # Meta emite estados que este traductor no modela (p. ej. "deleted") y
        # puede anadir mas sin avisar. Un acuse desconocido se IGNORA en lugar
        # de romper: los acuses viajan en el mismo payload que los mensajes, asi
        # que lanzar aqui descartaria tambien mensajes validos y dejaria la
        # ingesta caida ante trafico legitimo de Meta.
        return None
    status: MessageStatus = raw_status  # ya validado contra _KNOWN_STATUSES

    occurred_at = _parse_timestamp(raw.get("timestamp"))

    error_code: int | None = None
    if status == "failed":
        errors = raw.get("errors")
        if isinstance(errors, list) and errors:
            first_error = errors[0]
            if isinstance(first_error, dict) and isinstance(first_error.get("code"), int):
                error_code = first_error["code"]

    return StatusUpdate(
        wa_message_id=wa_message_id,
        phone_number_id=phone_number_id,
        status=status,
        occurred_at=occurred_at,
        error_code=error_code,
    )


def _parse_timestamp(raw: object) -> datetime:
    if isinstance(raw, str) and raw.isdigit():
        return datetime.fromtimestamp(int(raw), tz=UTC)
    raise InvalidMetaPayload("falta un 'timestamp' numérico válido")
