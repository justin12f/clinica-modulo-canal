# Paso 1 · Selección del módulo y orden de implementación

Fuente de verdad: `clinic-managment-agent` en el commit `2cbaba2941d07d26499246a323c771bd6dfc41f3`
(`docs/01-necesidades-y-requerimientos.md` §6 M1, `docs/13-plan-v2.md` H1, `CLAUDE.md` invariantes 2 y 11).

## Ficha

| Campo | Respuesta |
|---|---|
| RF / HU / CA vinculados | **RF M1.1**: "Recepción de webhooks con verificación de firma, idempotencia por ID de mensaje y acuse rápido". **HU**: *Como clínica, quiero que solo se acepten mensajes que realmente envió Meta y que lleguen en una forma que el sistema entienda, para no procesar mensajes falsos ni romperme ante un formato inesperado.* **CA-1.3** (Tarea 1.3): las 12 variantes de un móvil mexicano resuelven a `+5214793066911`; la regla del `1` es solo para MX; lo que no parsea lanza `ValueError`. **CA-1.4**: firma inválida o ausente → rechazo; firma válida → aceptada. **CA-1.5**: un payload desconocido o malformado lanza `InvalidMetaPayload`, nunca `KeyError`; mensajes y acuses se separan; ningún módulo fuera del traductor conoce el JSON de Meta. |
| Nombre y propósito del módulo | **Canal · recepción** (`app.channel`). Verifica que el webhook viene de Meta y traduce su payload a objetos de dominio (`InboundMessage`, `StatusUpdate`), con teléfonos canonicalizados. |
| Entradas y datos que recibe | Cuerpo crudo del webhook (`bytes`), cabecera `X-Hub-Signature-256`, `app_secret`; payload JSON decodificado (`dict`); teléfono en texto libre y región por defecto. |
| Salidas y mensajes esperados | `bool` de la firma; `ParsedWebhook(messages, statuses)`; `PhoneNumber(e164, is_mx)`. |
| Validaciones y casos de error | Firma en tiempo constante sobre el cuerpo crudo; secreto vacío → rechazo; cabecera sin prefijo `sha256=` → rechazo. Payload sin `entry`, `changes`, `value`, `metadata`, `phone_number_id`, `id`, `text.body`, con tipo desconocido o timestamp inválido → `InvalidMetaPayload`. Acuse con estado desconocido → se ignora sin tumbar el payload. Teléfono vacío, texto o fuera de rango → `ValueError`. |
| Dependencias con otros módulos | Solo `app.core` (`errors`, `types`). Librerías: `pydantic`, `phonenumbers`. Lo consumirán `api` (ruta del webhook) y el worker de ingesta, que quedan fuera. |
| Archivos que puede crear o modificar | `app/channel/__init__.py`, `app/channel/_internal/meta/{signature,translator}.py`, `app/core/{types,errors}.py`, `tests/**`, `docs/practica/**`, `pyproject.toml`, `README.md`. |
| Restricciones: qué no debe cambiar | La lógica de los tres archivos extraídos (se copian sin cambios funcionales). No se agrega base de datos, HTTP, envío, ventana de 24 h ni LLM. El webhook **no procesa** (invariante 2): este módulo solo verifica y traduce. Ningún error ni log lleva contenido del paciente (invariante 11). |
| Pruebas mínimas requeridas | Al menos un caso normal, uno límite y uno de error por CA. Las pruebas originales de las Tareas 1.3 y 1.5 y de la firma, más casos de firma de la práctica. |

## Pregunta de control

> ¿La implementación propuesta conserva el alcance y la separación de responsabilidades previstas?

Sí. El módulo hace lo que el diseño asigna a la recepción del canal y nada más:

- **Firma:** ocurre antes de cualquier lectura.
- **Traducción:** está aislada en `_internal/meta`, la única carpeta que conoce el formato de Meta (lo verifica `test_ningun_modulo_fuera_del_traductor_conoce_el_formato_de_meta`).
- **Identidad telefónica:** vive en `core`, porque la comparten varios módulos.
- **Fuera:** la persistencia y el procesamiento quedan fuera, igual que en el diseño original, donde dependen de PostgreSQL y del worker.

## Orden de implementación

1. Extraer, sin cambios funcionales, `signature.py`, `translator.py` y `types.py` del repositorio del proyecto.
2. Reducir `errors.py` a `DomainError` e `InvalidMetaPayload`, los únicos que usa el módulo.
3. Exponer la interfaz pública en `app/channel/__init__.py`: `verify_signature`, `sign_body`, `to_domain` y los modelos.
4. Traer las pruebas existentes (`test_phone.py`, `test_firma_meta_secreto_vacio.py`, `tests/contract/` con sus fixtures).
5. Agregar casos normal, límite y error de la firma (`tests/unit/test_firma_casos_practica.py`).
6. Correr `pytest`, `ruff` y `mypy --strict`, y guardar la salida en `docs/practica/evidencia/`.
7. Hacer commit y push al repositorio nuevo, verificar el commit en GitHub y llenar la matriz de trazabilidad.

**Ambigüedades pendientes:**
- Los fixtures de Meta son *provisionales*: no son capturas reales, porque H0 sigue pendiente.
- La forma exacta del `wa_id` real (Tarea 1.3, paso 5) está por confirmar contra Meta.

**Decisión del equipo sobre la orden:** [aceptada / modificada / rechazada] — justificación: [Completar por el equipo].
