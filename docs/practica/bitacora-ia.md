# Bitácora de IA

Equipo: Justin Emiliano Rodríguez Franco y Santiago Solís.

| # | Fecha | Herramienta | Prompt / solicitud | Resultado | Decisión humana |
|---|---|---|---|---|---|
| 1 | 2026-11-03 | Claude Code | "Extrae el primer módulo y súbelo a una nueva repo de acuerdo a la práctica" (con el PDF de la práctica) | Claude leyó el PDF. Como es una plantilla sin código, pidió el contexto del proyecto. | El equipo indicó que el módulo está en `justin12f/clinic-managment-agent`. |
| 2 | 2026-11-03 | Claude Code | (continuación) | Identificó M1 · Canal (H1) como el primer módulo. Eligió la parte de recepción (Tareas 1.3, 1.4 y 1.5) porque es la que se puede probar sin PostgreSQL. Copió el código y las pruebas, agregó casos normal, límite y error de la firma, ejecutó 50 pruebas (todas pasan), `ruff` y `mypy`, y redactó los pasos 1 a 4. | **Aceptada.** El alcance es el de un módulo pequeño del primer incremento. |
| 3 | 2026-11-03 | Claude Code (en lugar de ChatGPT) | Prompt 1 · orden de implementación | La orden y la ficha del Paso 1 se derivaron de `01-necesidades-y-requerimientos.md` §M1 y de `13-plan-v2.md` Tareas 1.3–1.5. No se usó ChatGPT. | **Aceptada** (ver `01-orden-de-implementacion.md`). |
| 4 | 2026-11-03 | Claude Code | "Listo, ya está creado" (repositorio vacío en GitHub) | Push de `main` con el commit `7f8702c`, SHA verificado con la API de GitHub. Se redactaron los pasos 5 y 6 y la matriz de trazabilidad (commit `1b483f0`). | **Aceptada.** |
| 5 | 2026-11-03 | Claude Code (en lugar de ChatGPT) | Prompt 5 · contraste final | Checklist priorizado de 7 puntos (`06-revision-final.md`) sin código nuevo ni evidencia inventada. | **Aceptada.** El módulo queda aceptado con 3 pendientes. |
| 6 | 2026-11-03 | Claude Code | "Llena tú los campos de completar; agrega de equipo a Santiago Solís y a mí" | Se llenaron las decisiones, el reparto de explicación y las reflexiones como propuesta. | Pendiente de que cada integrante revise y ajuste su reflexión. |

Nota: los Prompts 1 y 5 estaban pensados para ChatGPT. En esta entrega los resolvió Claude y así se registra.
