# Paso 6 · Revisión final y decisión del equipo

## Prompt 5 (ChatGPT): contraste final

> **Nota:** este contraste lo hizo Claude, no ChatGPT, con el mismo prompt y contra los mismos documentos (`13-plan-v2.md` Tareas 1.3–1.5, `CLAUDE.md` invariantes 2 y 11, resultados de `04-pruebas.md`). No se generó código ni se inventó evidencia.

Checklist priorizado:

1. **[Alta] Idempotencia y tope de cuerpo (CA-1.4) fuera de este repo.** El RF M1.1 pide "idempotencia por ID de mensaje y acuse rápido". Aquí solo están la firma y la traducción. Mientras no se integre con `InboxWriter`, el RF queda cubierto *parcialmente*.
2. **[Alta] Fixtures provisionales.** Las 21 pruebas de contrato comprueban la coherencia interna del traductor, no la fidelidad al formato real de Meta. Hay que reemplazarlas por capturas reales (Tarea 1.10, bloqueada por H0).
3. **[Media] `wa_id` real sin confirmar.** Si Meta entrega otra forma que `+521…`, hay que corregir `PhoneNumber` antes de integrar (Tarea 1.3, paso 5).
4. **[Media] Copia separada del repositorio original.** Cualquier corrección en `clinic-managment-agent` hay que llevarla a mano a este repo, o al revés.
5. **[Baja] Versión de Python.** El proyecto pide 3.12+ y la evidencia se corrió en 3.13.18. Conviene repetirla en 3.12.
6. **[OK] Invariante 11.** `InvalidMetaPayload` y `verify_signature` no exponen contenido del payload ni el motivo del rechazo.
7. **[OK] Separación de responsabilidades.** La prueba estructural confirma que solo `_internal/meta` conoce el JSON de Meta.

## Decisión del equipo

**Módulo aceptado con pendientes.** La parte de recepción (firma, traducción e identidad telefónica) cumple sus criterios de aceptación con 50 pruebas ejecutadas en verde y está publicada en GitHub. Se conservan como pendientes los puntos 1 a 3 del checklist. El siguiente ajuste es integrarlo con la ruta `POST /webhooks/whatsapp` e `InboxWriter` para cerrar la idempotencia, y después cambiar los fixtures por capturas reales cuando exista la cuenta de Meta.

Pendientes conocidos al cierre:
- Los fixtures de Meta son provisionales: hay que reemplazarlos por capturas reales (Tarea 1.10).
- Hay que confirmar la forma del `wa_id` real (Tarea 1.3, paso 5).
- La idempotencia por `body_sha256` y el tope de 2 MB del cuerpo viven en `InboxWriter` y en la ruta del webhook, fuera de este repo.

## Definición de terminado (DoD)

Propuesta con la evidencia disponible. El equipo la confirma.

| Checklist | Estado |
|---|---|
| El módulo cumple el RF y conserva las entradas y salidas previstas. | [x] Sí, para la parte de verificación y traducción. La idempotencia sigue en el repositorio original. |
| Las validaciones y errores definidos están contemplados. | [x] Sí |
| Se ejecutaron pruebas normal, límite y error con resultados anotados. | [x] Sí (`04-pruebas.md`, 50/50) |
| El código se entiende y cada integrante puede explicar una parte. | [x] Sí (reparto en `04-pruebas.md`) |
| Cada commit de código tiene push y está publicado en GitHub. | [x] Sí (`7f8702c`, verificado en GitHub) |
| Se actualizó trazabilidad y bitácora de IA. | [x] Sí (`05-github-y-trazabilidad.md`, `bitacora-ia.md`) |

## Reflexión individual

| Integrante | ¿Qué parte del módulo puede explicar? | ¿Qué aprendió al comparar diseño y ejecución? |
|---|---|---|
| Justin Emiliano Rodríguez Franco | La verificación de firma: por qué se firma el cuerpo crudo y no el JSON reserializado, por qué se usa `compare_digest` en lugar de `==` y por qué un secreto vacío se rechaza. También el traductor: cómo separa mensajes y acuses y por qué lanza `InvalidMetaPayload` en vez de `KeyError`. | El diseño ponía la recepción del webhook como una sola tarea, pero al ejecutarla se vio que tiene dos mitades. La parte pura (firma y traducción) se prueba aislada; la idempotencia depende de la base de datos. Separarlas dejó claro qué se puede entregar ya y qué depende de infraestructura. |
| Santiago Solís | La identidad telefónica: cómo `PhoneNumber.parse` quita los prefijos 044/045/01, por qué la regla del `1` mexicano es por longitud y no por tipo de línea, y por qué solo se aplica a México. También cómo se organizaron las pruebas normal, límite y error. | Los criterios de aceptación del plan ya traían los datos de prueba (las 12 variantes de un mismo número), y eso hizo que verificar fuera directo. A la vez, las pruebas con fixtures provisionales pueden pasar sin demostrar que el sistema funciona con Meta real: un "pasa" solo vale tanto como los datos con que se probó. |
