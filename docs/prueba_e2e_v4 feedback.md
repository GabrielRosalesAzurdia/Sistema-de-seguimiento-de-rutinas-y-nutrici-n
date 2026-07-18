# Feedback V4

## Correciones

CORRECCIÓN: definición operacional de VD2 + indicadores secundarios aprobados

Contexto: la definición operacional de VD2 en el Anteproyecto (Capítulo I, ya
aprobado y defendido) especifica el denominador como "días activos en el
sistema" del usuario, NO como una meta fija. Actualmente
`compute_study_metrics` en `backend/apps/tracking/services.py` calcula VD2
usando `Member.planned_nutrition_days` — la misma lógica de meta individual
que usa VD1 — lo cual ya no coincide con lo documentado académicamente. Hay
que corregir esto SIN tocar VD1 (VD1 sí debe seguir usando
`Member.planned_training_days`, su definición aprobada no exige días
activos, solo VD2 cambia).

CAMBIO 1 — Redefinir el denominador de VD2:
Para cada miembro con `participates_in_study=True`, el denominador de VD2
debe ser el número de días activos del miembro en el sistema dentro del
rango de fechas solicitado (`start`/`end` del export), no
`planned_nutrition_days`. "Día activo" = cada día calendario transcurrido
desde la fecha en que el miembro se activó (usar `Member.start_date`, o la
fecha de creación del `Member` si es posterior al inicio del rango) hasta
la fecha de corte (`end` del rango, o hoy si `end` es futuro), acotado
siempre al rango `start`–`end` solicitado. Si el miembro fue desactivado
(`is_active=False`) en algún punto, se sigue excluyendo por completo del
cálculo (regla ya vigente de la ronda 4, no cambia). El numerador de VD2 no
cambia: sigue siendo el conteo de `DailyNutritionLog` del miembro dentro
del mismo rango. Fórmula resultante:
VD2 = días con DailyNutritionLog en el rango / días activos del miembro en
el rango.
Actualizar también el label ya usado en la tabla VD2 de `/panel/estudio/`
("Días planificados") para que vuelva a decir "Días activos", reflejando
el cambio.

CAMBIO 2 — Indicadores secundarios de VD1 y VD2 (ya están en la matriz
operacional aprobada, pero el sistema hoy solo entrega el % principal de
forma agregada mensual; deben calcularse y exponerse también):

VD1:
  (a) Frecuencia semanal de registro: promedio de WorkoutSessionLog
      registrados por semana del miembro, dentro del rango.
  (b) Duración promedio registrada: promedio del campo de duración total
      de la rutina (el tiempo total que se ingresa al registrar) de los
      WorkoutSessionLog del miembro, dentro del rango.
  (c) Variación de constancia en el período: % de VD1 calculado sobre la
      segunda mitad del rango de fechas, menos % de VD1 calculado sobre la
      primera mitad (dividir el rango en dos mitades iguales por fecha).

VD2:
  (a) Frecuencia semanal de registro nutricional: promedio de
      DailyNutritionLog registrados por semana del miembro, dentro del
      rango.
  (b) % de semanas con registro mínimo: proporción de semanas del rango en
      que el miembro tiene al menos 3 DailyNutritionLog, respecto al total
      de semanas del rango.
  (c) Variación de constancia en el período: misma lógica que VD1(c),
      aplicada a VD2.

Estos 6 indicadores deben agregarse como columnas nuevas en el CSV de
GET /api/tracking/study-export/ (uno por miembro, junto a las columnas de
VD1/VD2 ya existentes) — es lo que se usa para el análisis de resultados
de tesis, así que prioriza que salgan ahí. Si además es sencillo mostrar un
resumen agregado (promedio de todos los miembros) en /panel/estudio/,
mejor, pero no es obligatorio si el CSV ya los cubre.

Antes de implementar, si algo no queda claro (por ejemplo cómo definir
"semana" exactamente dentro del rango si no es múltiplo exacto de 7 días,
o qué pasa si un miembro tiene menos de 2 semanas activas para calcular
"variación"), hazme preguntas puntuales antes de tocar código.


## Tablero KANBAN ( usar tablero ya creado en github projects )
TAREA: reconstruir el tablero Kanban del proyecto en GitHub Projects (gh CLI)

Contexto: la metodología de desarrollo del anteproyecto (defendida y
aprobada) especifica un tablero Kanban de 3 columnas — Por hacer, En
progreso, Terminado — organizado en 5 fases: diagnóstico y análisis de
requerimientos, diseño visual de interfaces, programación de backend
(Django), programación de frontend (Flutter), integración de modelos de
ML, y despliegue (Render). Hasta ahora ese tablero nunca se materializó
en GitHub — necesito que exista como evidencia real para el capítulo de
metodología de la tesis, no como un board vacío de adorno.

CAMBIO 1 — Verificar antes de crear nada:
Antes de crear un Project nuevo, corre `gh project list` (y revisa
`gh repo view` / `git remote -v` para confirmar en qué repo(s) estamos:
si backend y mobile viven en el mismo repo o en repos separados) para
confirmar que no exista ya un tablero de este proyecto. Si ya existe uno,
usa ese en vez de duplicar. Si necesitas el scope de projects en la CLI y
no lo tienes, avísame en vez de intentar workarounds — puede requerir
`gh auth refresh -s project` de mi parte.

CAMBIO 2 — Crear el tablero:
Un GitHub Project (v2) con exactamente 3 columnas/estados: "Todo",
"Working", "Done" (usa esos nombres exactos, no los traduzcas). Vincúlalo
al repo del proyecto.

CAMBIO 3 — Reconstruir el historial completo de tareas:
No me pidas que yo te dicte cada tarea una por una — tienes acceso a
`git log`, a los commits de cada fase, a `docs/mockups/`, a
`docs/prueba_e2e*.md` y sus `*_feedback.md` (rondas 1 a 4), y al
historial de decisiones resumido en `CLAUDE.md`. Usa todo eso como fuente
para reconstruir las tareas reales del proyecto, agrupadas por las 5
fases del anteproyecto, por ejemplo (ilustrativo, no exhaustivo — tú
generas la lista real a partir del historial):
  - Fase 1 (diagnóstico y análisis): Acta de reunión 1, Cuestionario de
    requerimientos 1, Cuestionario de requerimientos 2 (presentación de
    diseño).
  - Fase 2 (diseño visual): mockups de la app (9 pantallas), mockups del
    panel admin (8 pantallas), identidad visual.
  - Fase 3 (backend): cada app de Django (members, routines, nutrition,
    tracking, ml_predictions, panel) como tareas separadas si el
    historial de commits lo justifica.
  - Fase 3 (frontend): cada pantalla de la app Flutter, cada pantalla del
    panel admin.
  - Fase 4 (ML): heurística de generación de plan nutricional, modelo de
    predicción de días-a-meta con datos sintéticos.
  - Rondas de prueba E2E v1, v2, v3 con sus fixes correspondientes (ya
    verificadas y cerradas).
  - Tareas pendientes/planeadas: prueba E2E v4 (por hacer), la corrección
    de VD2 + indicadores secundarios que acabamos de definir, carga del
    catálogo real de ejercicios (bloqueada en el coach), carga de
    miembros reales, despliegue en Render, reentrenamiento del modelo de
    ML con datos reales post-estudio (oct-nov 2026).
Crea cada tarea como issue o draft item (lo que sea más práctico dado el
volumen) y agrégalas todas al Project.

CAMBIO 4 — Estado inicial y reconciliación:
Por ahora, agrega TODAS las tareas a la columna "Todo" primero (carga
completa). Después, en una segunda pasada, recorre la lista en orden
cronológico inverso (de lo más reciente/actual hacia atrás) y mueve a
"Done" todo lo que ya está verificado y cerrado según el historial real
(fases 1-3, ML inicial, rondas E2E v1-v3 con sus fixes ya confirmados).
Deja en "Working" únicamente lo que está activo ahora mismo (prueba E2E
v4 pendiente de correr, la corrección de VD2). Todo lo demás (catálogo
real, miembros reales, despliegue, reentrenamiento ML) se queda en
"Todo" como trabajo planeado a futuro.

Antes de mover en bloque cualquier cosa a "Done", muéstrame primero la
lista completa de tareas que planeas crear (puede ser en un archivo
markdown temporal o en la consola) para que la revise, en vez de crear y
reconciliar todo de una sola pasada sin que yo la vea antes.

## Prueba E2E
Todos los puntos de la prueba E2E pasaron satisfactoriamente y no se han encontrado mas bugs.
