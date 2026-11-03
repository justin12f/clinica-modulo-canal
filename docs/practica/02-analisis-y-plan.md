# Paso 2 · Análisis técnico previo

| Aspecto a revisar | Resultado / notas |
|---|---|
| El plan respeta el alcance y el diseño modular | Sí. Solo se toma la parte de M1 que no requiere infraestructura. Se conserva la regla `__init__.py` público / `_internal` privado. |
| Los archivos propuestos son razonables | Sí: 3 archivos de lógica copiados tal cual, 1 de errores recortado y 1 de interfaz pública nuevo. |
| Se identificaron riesgos o dudas relevantes | (1) Los fixtures de Meta son provisionales. (2) El `wa_id` real está por confirmar. (3) El proyecto pide Python 3.12+ y la evidencia se corrió en 3.13. (4) Extraer la pieza separa el código del repositorio original: los cambios futuros hay que llevarlos a mano a los dos lados. |
| Se requiere ajustar la orden de implementación | No. |

| Propuesta del asistente | Decisión del equipo | Justificación |
|---|---|---|
| Extraer solo firma, traductor e identidad telefónica (no la escritura en `inbound_event`) | [Aceptada / modificada / rechazada] | [Completar]. Motivo técnico: `inbox.py`, `ingest.py`, `window.py` y `planner.py` requieren PostgreSQL con RLS y no se pueden probar aislados. |
| Agregar `test_firma_casos_practica.py` con casos normal, límite y error | [Aceptada / modificada / rechazada] | [Completar]. Motivo: la práctica exige los tres tipos de caso por CA, y la firma solo tenía dos pruebas sueltas. |
