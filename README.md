# clinica-modulo-canal

Primer módulo del **agente de WhatsApp para clínicas** (`justin12f/clinic-managment-agent`), extraído como
entrega de la práctica *DASV · Implementación del primer módulo*.

**Módulo:** M1 · Canal y mensajería, parte de **recepción de webhooks de Meta** del primer incremento (H1).

| Pieza | Archivo | Tarea del plan |
|---|---|---|
| Verificación de firma HMAC-SHA256 | `app/channel/_internal/meta/signature.py` | H1 · 1.4 |
| Traductor anticorrupción del payload de Meta | `app/channel/_internal/meta/translator.py` | H1 · 1.5 |
| Identidad telefónica (`PhoneNumber`) | `app/core/types.py` | H1 · 1.3 |
| Interfaz pública del módulo | `app/channel/__init__.py` | — |

Fuera de este repo (dependen de PostgreSQL, RLS y del worker): escritura en `inbound_event`, ingesta,
ventana de 24 h, planner y envío. Ver `docs/practica/01-orden-de-implementacion.md` §Restricciones.

## Ejecutar

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -v        # 50 pruebas
.venv/bin/ruff check app tests && .venv/bin/ruff format --check app tests
.venv/bin/mypy                       # modo estricto
```

## Uso

```python
from app.channel import verify_signature, to_domain
from app.core.types import PhoneNumber

if not verify_signature(cuerpo_crudo, cabecera_x_hub_signature_256, app_secret):
    ...  # 403, no se persiste nada
webhook = to_domain(json.loads(cuerpo_crudo))   # lanza InvalidMetaPayload si la forma no es la esperada
for m in webhook.messages:
    PhoneNumber.parse(m.wa_id).e164             # +5214793066911
```

## Documentos de la práctica

- [`docs/practica/01-orden-de-implementacion.md`](docs/practica/01-orden-de-implementacion.md): ficha del Paso 1 y orden
- [`docs/practica/02-analisis-y-plan.md`](docs/practica/02-analisis-y-plan.md): Paso 2
- [`docs/practica/03-implementacion.md`](docs/practica/03-implementacion.md): Paso 3
- [`docs/practica/04-pruebas.md`](docs/practica/04-pruebas.md): Paso 4, con la salida real en `evidencia/`
- [`docs/practica/05-github-y-trazabilidad.md`](docs/practica/05-github-y-trazabilidad.md): Paso 5 y matriz de trazabilidad
- [`docs/practica/06-revision-final.md`](docs/practica/06-revision-final.md): Paso 6, DoD y reflexión
- [`docs/practica/bitacora-ia.md`](docs/practica/bitacora-ia.md): bitácora de IA
