# Paso 4 · Pruebas

Las pruebas se **ejecutaron**. La salida completa está en [`evidencia/pytest-salida.txt`](evidencia/pytest-salida.txt).

| Caso | Datos de entrada | Resultado esperado | Resultado real obtenido | Estado |
|---|---|---|---|---|
| Normal / CA-1.4 | `{"object":"whatsapp_business_account","entry":[]}` firmado con el secreto correcto | `verify_signature` → `True` | `True` (`test_normal_firma_valida_se_acepta` PASSED) | Pasa |
| Normal / CA-1.5 | Fixture `mensaje_texto_provisional.json` | 1 `InboundMessage` de tipo `text` con su `wa_id` y su cuerpo | Coincide (`test_mensaje_de_texto` PASSED) | Pasa |
| Normal / CA-1.3 | 12 variantes de `479 306 6911` (`044…`, `+52 1…`, `(479) 306-6911`…) | Todas → `+5214793066911` | Las 12 coinciden (12 casos PASSED) | Pasa |
| Límite / CA-1.4 | Cuerpo vacío `b""` con firma correcta; mismo JSON reserializado con espacios | Vacío → `True`; reserializado → `False` | `True` / `False` (2 PASSED) | Pasa |
| Límite / CA-1.5 | Payload mixto: 3 mensajes y 2 acuses; acuse con estado desconocido | Se separan 3 y 2; el desconocido se ignora sin excepción | Coincide (2 PASSED) | Pasa |
| Límite / CA-1.3 | `+52 55 5555 5555` (fijo CDMX); `+1 415…`, `+34 612…` | MX → `+5215555555555`; otros países sin `1` | Coincide (2 PASSED) | Pasa |
| Error / CA-1.4 | Cuerpo alterado, sin cabecera, sin prefijo, secreto distinto, secreto vacío | `False` en todos | `False` en todos (5 PASSED) | Pasa |
| Error / CA-1.5 | 11 payloads malformados (sin `entry`, sin `changes`, tipo desconocido, timestamp inválido…) | `InvalidMetaPayload`, nunca `KeyError` | `InvalidMetaPayload` en los 11 (12 PASSED) | Pasa |
| Error / CA-1.3 | `""`, `"hola"`, `"12"`, `"+999999999999999999"` | `ValueError` | `ValueError` en los 4 (4 PASSED) | Pasa |

| Elemento de evidencia | Registro |
|---|---|
| Comando o forma de ejecución | `.venv/bin/python -m pytest -v`. Además `ruff check app tests`, `ruff format --check app tests` y `mypy` (estricto). |
| Salida observada | `50 passed in 0.15s` (Python 3.13.18, pytest 9.2.0). `ruff`: sin errores, 13 archivos formateados. `mypy`: `Success: no issues found in 9 source files`. |
| Error y corrección realizada (si aplica) | `ruff` reportó `RUF022` (`__all__` sin ordenar) en `signature.py`. Se corrigió con `ruff check --fix` sin cambiar la lógica. |
| Funciones o partes que cada integrante puede explicar | [Completar por el equipo] |

**Pendiente:** contrastar los fixtures provisionales y la forma del `wa_id` con payloads reales de Meta (Tarea 1.10, bloqueada por H0).
