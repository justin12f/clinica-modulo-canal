# Bitácora de IA

| # | Fecha | Herramienta | Prompt / solicitud | Resultado | Decisión humana |
|---|---|---|---|---|---|
| 1 | 2026-11-03 | Claude Code | "Extrae el primer módulo y súbelo a una nueva repo de acuerdo a la práctica" (con el PDF de la práctica) | Claude leyó el PDF. Como es una plantilla sin código, pidió el contexto del proyecto. | El equipo indicó que el módulo está en `justin12f/clinic-managment-agent`. |
| 2 | 2026-11-03 | Claude Code | (continuación) | Identificó M1 · Canal (H1) como el primer módulo. Eligió la parte de recepción (Tareas 1.3, 1.4 y 1.5) porque es la que se puede probar sin PostgreSQL. Copió el código y las pruebas, agregó casos normal, límite y error de la firma, ejecutó 50 pruebas (todas pasan), `ruff` y `mypy`, y redactó estos documentos. | [Completar: aceptada / modificada / rechazada] |
| 3 | [fecha] | ChatGPT | Prompt 1 · orden de implementación | [Completar] | [Completar] |
| 4 | [fecha] | ChatGPT | Prompt 5 · contraste final | [Completar] | [Completar] |

Nota: Claude no ejecutó los Prompts 1 y 5 (ChatGPT). Las celdas de decisión del equipo y la reflexión individual las debe llenar el equipo.

| # | Fecha | Herramienta | Prompt / solicitud | Resultado | Decisión humana |
|---|---|---|---|---|---|
| 5 | 2026-11-03 | Claude Code | "Listo, ya está creado" (repositorio vacío en GitHub) | Push de `main` con el commit `7f8702c`, SHA verificado con la API de GitHub. Se redactaron los pasos 5 y 6 y la matriz de trazabilidad. | [Completar] |
