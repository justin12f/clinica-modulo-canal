"""Tipos de valor compartidos del núcleo.

`PhoneNumber` es el objeto de valor para identidad telefónica. Ver
CLAUDE.md → convención "Teléfonos" y docs/13-plan-v2.md → Tarea 1.3.

Decisión vinculante (⟨Q⟩ opción 3, ronda de corrección 1): la forma
canónica de un número mexicano LLEVA el `1` tras `+52`
(`+5214793066911`), porque así es como WhatsApp entrega el `wa_id` —
aunque el E.164 "puro" posterior a la reforma de numeración de 2019 no
lo lleve.

Mecanismo (ronda de corrección 1 — reemplaza el intento original
basado en `phonenumbers.number_type`): la canonicalización es por
**longitud**, no por tipo de línea, y es **exclusiva de México**:

- Número mexicano con 10 dígitos nacionales → canónico `+521` + esos
  10 dígitos.
- Número mexicano que ya trae los 11 dígitos empezando en `1` → se
  deja como está (el resultado es el mismo, por idempotencia de la
  normalización de abajo).
- Cualquier otro país → E.164 estándar, sin tocar.

Por qué no por tipo de línea: desde la reforma del plan de numeración
mexicano de 2019, `phonenumbers` ya no puede distinguir fijo de móvil
para México por patrón de dígitos — casi todo número de 10 dígitos
resuelve al tipo ambiguo `FIXED_LINE_OR_MOBILE` (confirmado incluso
contra el propio número de ejemplo "móvil" oficial de la librería;
detalle y evidencia completa en
`.superpowers/sdd/13-plan-v2/task-1.3-report.md`). Intentar decidir por
tipo de línea es indeterminista. La regla por longitud es determinista
y depende solo de México — nunca de si `phonenumbers` logra o no
clasificar la línea.

Por qué es inocuo que un fijo mexicano reciba un `1` que no le
corresponde: un fijo no puede tener WhatsApp, así que la forma
"+521..." resultante nunca colisiona con un `wa_id` real de otro
paciente, y ese número tampoco es alcanzable por este canal de todos
modos. El campo `is_mx` refleja exactamente eso — "es un número
mexicano, se le aplicó la regla del 1" — y NO afirma nada sobre si la
línea es móvil o fija, porque `phonenumbers` no puede determinarlo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat

# Prefijos históricos de troncal mexicana que WhatsApp y los Excel de
# las clínicas todavía traen: "01" (larga distancia), "044" (móvil
# local) y "045" (móvil larga distancia). Se despojan antes de
# normalizar.
_MX_TRUNK_PREFIXES = ("044", "045", "01")

_MX_COUNTRY_CODE = 52

_E164_PATTERN = re.compile(r"\+[1-9]\d{6,14}")


def _normalize_mx_candidate(raw: str, default_region: str) -> str:
    """Despoja marcadores históricos mexicanos antes de parsear.

    `phonenumbers` no reconoce "044"/"045"/"01" como prefijos de
    troncal, ni un "1" pegado tras "52", como formas válidas del mismo
    número de 10 dígitos. Aquí se detectan y se devuelve un candidato
    "+52" + 10 dígitos listo para `phonenumbers.parse`. Despojar el "1"
    de antemano (si ya venía) hace que la reinserción incondicional en
    `PhoneNumber.parse` sea idempotente: da igual si el `raw` original
    ya traía los 11 dígitos o no, el resultado es el mismo.
    """
    if default_region != "MX":
        return raw

    had_plus = raw.strip().startswith("+")
    digits = re.sub(r"\D", "", raw)

    # "+52 1 XXXXXXXXXX" / "+5214793066911" / "5214793066911": el "1"
    # es el marcador histórico que WhatsApp todavía entrega.
    if digits.startswith("52") and len(digits) == 13 and digits[2] == "1":
        return f"+52{digits[3:]}"

    # "044"/"045"/"01" + 10 dígitos, sin "+" (troncal doméstica).
    if not had_plus:
        for prefix in _MX_TRUNK_PREFIXES:
            if digits.startswith(prefix) and len(digits) == len(prefix) + 10:
                return f"+52{digits[len(prefix) :]}"

    return raw


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    """Identidad telefónica normalizada.

    No se instancia directamente: se construye con `PhoneNumber.parse`.
    `__post_init__` valida que `e164` ya esté en forma canónica — un
    valor no normalizado no puede representarse.
    """

    e164: str
    is_mx: bool

    def __post_init__(self) -> None:
        if not _E164_PATTERN.fullmatch(self.e164):
            raise ValueError(f"'{self.e164}' no es un E.164 canónico normalizado")

        # Todo número mexicano válido tiene 10 dígitos nacionales
        # (México no tiene prefijo de larga distancia en su plan de
        # numeración actual), así que la regla del 1 se le aplica
        # siempre: is_mx=True implica "+521...", y "+52..." implica
        # is_mx=True. "+52" es exclusivo de México a nivel mundial, así
        # que un e164 fuera de México jamás debería empezar así.
        if self.is_mx and not self.e164.startswith("+521"):
            raise ValueError(f"'{self.e164}' con is_mx=True debe llevar el prefijo +521")
        if self.e164.startswith("+52") and not self.is_mx:
            raise ValueError(f"'{self.e164}' empieza con +52 pero is_mx=False")

    @classmethod
    def parse(cls, raw: str, default_region: str = "MX") -> PhoneNumber:
        """Parsea `raw` y devuelve la forma canónica de identidad.

        Para números mexicanos, la forma canónica lleva el `1` tras
        `+52` (decisión ⟨Q⟩ opción 3, ronda de corrección 1) —
        independientemente de si la línea es móvil o fija; ver
        docstring del módulo. Lanza `ValueError` si `raw` no es un
        número de teléfono válido.
        """
        candidate = _normalize_mx_candidate(raw, default_region)

        try:
            parsed = phonenumbers.parse(candidate, default_region)
        except NumberParseException as exc:
            raise ValueError(f"'{raw}' no es un número de teléfono válido") from exc

        if not phonenumbers.is_valid_number(parsed):
            raise ValueError(f"'{raw}' no es un número de teléfono válido")

        e164 = phonenumbers.format_number(parsed, PhoneNumberFormat.E164)

        is_mx = parsed.country_code == _MX_COUNTRY_CODE
        if is_mx:
            e164 = f"+{_MX_COUNTRY_CODE}1{e164.removeprefix(f'+{_MX_COUNTRY_CODE}')}"

        return cls(e164=e164, is_mx=is_mx)
