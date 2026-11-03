# Paso 5 · Commit, push y verificación en GitHub

| Evidencia | Dato |
|---|---|
| URL del repositorio / rama | https://github.com/justin12f/clinica-modulo-canal · `main` |
| Hash o referencia del commit | `7f8702c21ac958da0355804f1944d676414ec0a8` (código, pruebas y pasos 1 a 4). Este documento va en el commit siguiente. |
| Rama local y remota en GitHub | Local `main` → remota `origin/main` (*tracking* configurado con `git push -u origin main`). |
| Resultado del push | `* [new branch] main -> main`. Verificado con la API de GitHub: `GET repos/justin12f/clinica-modulo-canal/commits/main` devuelve el mismo SHA `7f8702c…`. |
| URL del commit visible en GitHub | https://github.com/justin12f/clinica-modulo-canal/commit/7f8702c21ac958da0355804f1944d676414ec0a8 |
| RF y módulo implementado | RF M1.1 (recepción de webhooks con verificación de firma) · módulo `app.channel`, parte de recepción (Tareas H1 1.3, 1.4 y 1.5). |
| Pruebas que pasan y pruebas pendientes | **Pasan**: 50 de 50 (`pytest -v`), más `ruff` y `mypy --strict` limpios. **Pendientes**: contraste con payloads reales de Meta y con la forma real del `wa_id` (Tareas 1.3 paso 5 y 1.10, bloqueadas por H0). La idempotencia por `body_sha256` y el tope de 2 MB del webhook (CA de la Tarea 1.4) siguen en el repositorio original, porque requieren PostgreSQL. |
| Ubicación de la evidencia de ejecución | `docs/practica/evidencia/pytest-salida.txt` |
| Siguiente tarea o dependencia | Integrar este módulo con la ruta `POST /webhooks/whatsapp` y con `InboxWriter` (escritura idempotente en `inbound_event`), y después con la ingesta del worker (Tarea 1.7). |

Sin secretos en el repositorio: el `.gitignore` excluye `.env*` y `.venv/`. Las pruebas usan secretos de juguete (`"secreto-de-prueba"`).

## Matriz de trazabilidad

| Necesidad | RF | HU / CA | Diseño (doc) | Código | Prueba(s) | Estado |
|---|---|---|---|---|---|---|
| N6 Todo auditable / seguridad del canal | M1.1 Recepción de webhooks con verificación de firma | CA-1.4 firma válida se acepta; inválida, ausente o alterada se rechaza | `13-plan-v2.md` Tarea 1.4; `CLAUDE.md` invariante 2 | `app/channel/_internal/meta/signature.py` | `tests/unit/test_firma_casos_practica.py` (7), `tests/unit/test_firma_meta_secreto_vacio.py` (2) | Implementado y probado |
| N1 La agenda opera sin intervención humana (entender lo que llega) | M1.1 + M1.5 Soporte de texto, botones, imágenes, documentos, audio | CA-1.5 payload malformado → `InvalidMetaPayload`; mensajes y acuses separados; formato de Meta aislado | `13-plan-v2.md` Tarea 1.5; `06-patrones-de-diseno.md` (anticorrupción) | `app/channel/_internal/meta/translator.py`, `app/core/errors.py` | `tests/contract/test_payloads_meta.py` (21) | Implementado y probado (fixtures provisionales) |
| N1 / N6 Identificar al paciente sin duplicados | M1.3 Estado por paciente (identidad por `wa_id`) | CA-1.3 12 variantes → `+5214793066911`; la regla del `1` es solo MX; lo inválido lanza error | `13-plan-v2.md` Tarea 1.3; `CLAUDE.md` §Teléfonos | `app/core/types.py` | `tests/unit/test_phone.py` (20) | Implementado y probado; falta confirmar el `wa_id` real |
| N6 | M1.1 Idempotencia y acuse rápido | CA-1.4 reintento no duplica; cuerpo > 2 MB → 413 | `13-plan-v2.md` Tarea 1.4 | Fuera de este repo (`InboxWriter`, ruta del webhook) | `tests/channel/test_webhook.py` del repositorio original | Pendiente de integrar |
