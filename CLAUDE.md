# CLAUDE.md — Club Fitness App

Contexto para retomar el desarrollo en Claude Code. Este archivo resume
todo lo definido durante el anteproyecto de graduación para que no se
pierda al pasar de la fase de documentación a la fase de desarrollo.

> 🖼️ **Antes de tocar UI (Flutter o panel admin), revisa
> `docs/mockups/app/` y `docs/mockups/admin_panel/`.** Son capturas
> reales del diseño ya aprobado por el gimnasio, no bocetos — colores,
> textos y layout son la referencia exacta a seguir.

## 1. Qué es este proyecto

Trabajo de graduación de **Gabriel Alejandro Rosales Azurdia**,
Ingeniería en Sistemas de Información, Universidad Mariano Gálvez de
Guatemala (UMG). Título de investigación: *"Sistema de seguimiento de
rutinas y nutrición para mejorar la constancia al entrenamiento y al
plan nutricional en gimnasio de Jocotenango"*.

Se implementa en el gimnasio **Fitness Club** (Jocotenango,
Sacatepéquez), propiedad de **Alex Ovando** (coach/dueño, colaborador
principal, debe aprobar todo plan nutricional antes de que llegue al
usuario). Período de implementación del estudio: **octubre–noviembre
2026**. Diseño de investigación: cuantitativo, pre-experimental,
antes/después.

### Variables de investigación
- **VI**: Implementación del sistema de seguimiento de rutinas y nutrición.
- **VD1**: Constancia al plan de entrenamiento = % sesiones completadas / sesiones planificadas.
- **VD2**: Constancia al plan nutricional = % días con registro / días activos en el sistema.

La definición exacta de "sesiones planificadas" para VD1 aún debe
cerrarse con el asesor; el código actual deja esto marcado con TODO
(ver `backend/apps/tracking/views.py::StudyExportView`).

## 2. Componentes del sistema

1. **App móvil (Android, Flutter)** — `mobile/` — para los ~85-186
   usuarios del gimnasio.
2. **Panel de administración web (Django)** — `backend/` — para el
   coach: gestión de miembros, rutinas/ejercicios, revisión y
   aprobación de planes nutricionales, exportación de datos del
   estudio.
3. **API REST (Django REST Framework)** — mismo backend, consumida por
   la app Flutter.
4. **Modelos de Machine Learning (scikit-learn)** — `ml/` para
   entrenamiento, `backend/apps/ml_predictions/` para inferencia —
   predicen días para alcanzar la meta de peso del usuario.

Stack confirmado en el anteproyecto (no cambiar sin razón de peso, ya
fue defendido en la viabilidad técnica): **Flutter (Android) + Django
REST Framework + PostgreSQL + scikit-learn + Render** (hosting).

## 3. Decisiones de negocio clave (NO son suposiciones del scaffold, ya están acordadas)

- **El peso y las medidas corporales del usuario los ingresa
  ÚNICAMENTE el coach**, desde el panel admin, con frecuencia mensual.
  La app móvil **nunca** debe tener un campo editable de peso/medidas
  para el usuario final (se hizo así explícitamente "para evitar datos
  erróneos"). El sistema calcula % de grasa y % de agua corporal a
  partir de esas medidas.
- **Correo y teléfono del usuario son datos de panel admin, NO
  visibles en la app.**
- **Meta "Tonificar"** se trata internamente igual que "Perder peso"
  (mismo tratamiento en cálculo de macros/predicción), pero se muestra
  como opción separada en la UI.
- **Semáforo nutricional diario único**: HECHO / PARCIALMENTE / SE ME
  FUE, un solo registro por día en el dashboard. El marcado por comida
  individual (Desayuno ✓, Almuerzo ✓, etc.) se descartó explícitamente
  para v1 por alcance ("no se puede ofrecer un plan nutricional tan
  complejo... se puede ver en una versión 2").
- **5 tiempos de comida**: Desayuno, Refacción I, Almuerzo, Refacción
  II, Cena (se agregó una refacción de tarde a los 4 originales).
- **La app solo maneja macros** (proteína/carbohidratos/grasas +
  calorías), sin listas de alimentos guatemaltecos ni recetas
  específicas — "No aplica, la app solo maneja macros".
- **7 categorías de rutina**: Pierna-Cuádriceps, Pecho, Brazos y
  Espalda, Cardio, ABS, Pierna-Glúteos, Hombro.
- **Las rutinas ya están creadas**; lo que se actualiza semanalmente
  son los EJERCICIOS que integran cada rutina (vía panel admin,
  seleccionando de un catálogo predefinido con ícono/foto ya
  mapeados). El coach explícitamente pidió evitar tener que subir
  fotos repetidamente.
- **La app NO marca completado por ejercicio individual**, solo
  muestra el orden. El usuario marca la rutina completa como
  terminada ingresando, por cada ejercicio: peso inicial (lb), peso
  final (lb) y repeticiones hechas, más el tiempo total de la rutina.
- **Notificaciones push**: fuera de alcance v1, posible v2.
- **Solo español.** Sin soporte multi-idioma.
- **Solo Android** en v1 (iOS quedó "tentativo si da tiempo y recurso").
- **Sin comparaciones entre usuarios ni datos de otros miembros**
  visibles en la app.

## 4. Identidad visual (ya aprobada, no iterar sin motivo)

- Fondo negro, acentos **amarillo #FFD600**, verde y naranja
  "chintón" (vivo/saturado). Confirmado dos veces por el coach como
  "Todo está bien".
- Flujo de navegación de la app (bottom nav): **Inicio → Rutinas →
  Nutrición → Perfil**.
- Paleta implementada en `mobile/lib/core/theme.dart`
  (`AppColors.yellow`, `AppColors.green`, `AppColors.orange`).

## 5. Pantallas de la app móvil (mockup ya validado — imágenes reales en `docs/mockups/app/`, índice en `docs/mockups/README.md`)

1. **Login** — `screens/login_screen.dart`
2. **Inicio / Dashboard** — peso actual/meta, % grasa, % agua, días
   para meta (ML), racha, macros del día, semáforo nutricional,
   calorías quemadas totales, rutina de hoy — `dashboard_screen.dart`
3. **Rutinas** (listado de 7 categorías) — `routines_screen.dart`
4. **Detalle de rutina** (lista de ejercicios en orden) —
   `routine_detail_screen.dart`
5. **Registrar rutina** (peso inicial/final + reps por ejercicio +
   tiempo total) — `log_routine_screen.dart`
6. **Nutrición** (macros + 5 tiempos de comida con sugerencias) —
   `nutrition_screen.dart`
7. **Perfil** (solo lectura de peso/medidas) — `profile_screen.dart`
8. **Editar Perfil** (nombre, edad, altura, meta, nivel de actividad —
   SIN peso/medidas) — `edit_profile_screen.dart`

## 6. Pantallas del panel admin (Django) — pendientes de construir

El scaffold actual solo trae el **Django admin genérico** registrado
(`apps/*/admin.py`) y el **API REST** completo. Falta construir la UI
web personalizada que replique el mockup — imágenes reales en
`docs/mockups/admin_panel/` (índice en `docs/mockups/README.md`), con
estas pantallas:

- **Dashboard**: miembros activos, pagos pendientes, % constancia
  nutricional, actividad reciente de miembros.
- **Miembros**: listado + "Agregar Miembro" (datos personales,
  correo, teléfono, datos físicos —peso, medidas, meta, fecha de
  inicio/próximo pago—, marcar pagado/desactivar usuario).
- **Rutinas**: listado de rutinas semanales + "Editar ejercicios" por
  rutina (selección desde catálogo predefinido).
- **Nutrición**: "Dietas por Revisar" / "Dietas Aprobadas y en
  Seguimiento" (aprobar/rechazar planes).
- **Datos del estudio**: exportador CSV con VD1 y VD2 por usuario y
  rango de fechas (ya implementado el endpoint:
  `GET /api/tracking/study-export/?start=...&end=...`, falta la UI).

Decisión pendiente: construir estas vistas con **templates Django +
HTMX/Alpine** (más simple, coherente con "sin costo, un solo
desarrollador") o un frontend separado (React/Vue). El anteproyecto
solo compromete "panel de administración online con Django", no
especifica el enfoque de frontend — priorizar la opción más rápida de
implementar dado el tiempo limitado (octubre 2026 como fecha límite
para tener el sistema estable).

## 7. Estructura del backend

```
backend/
  config/                  # settings, urls, wsgi
  apps/
    members/                # User (auth), Member (perfil completo)
    routines/                # RoutineCategory, Exercise, Routine, RoutineExercise
    nutrition/                # NutritionPlan, MealSuggestion (status: pendiente/aprobado/rechazado)
    tracking/                # WorkoutSessionLog, WorkoutExerciseEntry, DailyNutritionLog,
                              # BodyMeasurementLog, StudyExportView (CSV VD1/VD2)
    ml_predictions/           # MLPrediction, services.py (inferencia), trained_models/
```

Autenticación: JWT (`djangorestframework-simplejwt`), login con email
vía `/api/auth/login/`. Un solo modelo `User` (`members.User`):
`is_staff=True` = coach (panel admin), `is_staff=False` = miembro
(app), vinculado a su `Member` vía `Member.user`.

## 8. Próximos pasos sugeridos (orden recomendado)

1. `cd backend && pip install -r requirements.txt`, configurar
   `.env` (copiar de `.env.example`), levantar Postgres
   (`docker compose up db`), correr `python manage.py migrate` y
   `createsuperuser`.
2. Cargar el catálogo de ejercicios reales del gimnasio (nombres
   exactos de las máquinas, ver `docs/requerimientos_resumen.md`) —
   pendiente de que el coach entregue la lista completa con
   íconos/fotos.
3. Construir la UI del panel admin (ver punto 6).
4. Conectar Flutter (`cd mobile && flutter pub get`) contra el backend
   local (`ApiClient.baseUrl`, ajustar según emulador/dispositivo).
5. Definir con el asesor la fórmula exacta de "sesiones planificadas"
   para VD1 y actualizar `StudyExportView` y
   `MyProgressPredictionView`.
6. ~~Cuando arranque octubre 2026: usar `ml/training/` para entrenar el
   modelo real~~ — **Parcialmente resuelto**: el pipeline ya está
   conectado end-to-end con datos **sintéticos**
   (`ml/training/generate_synthetic_data.py` →
   `train_progress_model.py` →
   `backend/apps/ml_predictions/trained_models/random_forest_progress_v1.joblib`).
   `GET /api/ml/me/progress/` ya usa `model_type: "RANDOM_FOREST"` en
   vez de la heurística. **Sigue pendiente** reentrenar con datos
   reales exportados de `study-export/` una vez concluya oct-nov 2026
   (mismo comando, solo cambia el CSV de entrada).
7. ~~Revisar cálculo de % grasa / % agua corporal~~ — **Resuelto**: se
   implementó el U.S. Navy Method en
   `backend/apps/members/services.py::calculate_body_composition`,
   invocado automáticamente desde `Member.save()`. Requiere
   `Member.gender` y `Member.neck_cm` (campos nuevos, agregados para
   esto) además de `waist_cm`/`height_cm`/`hip_cm` ya existentes. El %
   de agua corporal es una estimación derivada del % de grasa (no hay
   fórmula Navy estándar para agua) — ver docstring del módulo para la
   fuente citada. **Implica que el coach debe medir el cuello del
   miembro desde ahora**, además de las medidas que ya tomaba.

## 9. Terminología obligatoria (documento académico, mantener consistencia también en código/UI)

Usar: **constancia** (no "adherencia"), **seguimiento** (no
"monitoreo"), **nutrición / plan nutricional** (no "alimentación"),
**usuarios** (no "clientes"). Ya aplicado en nombres de modelos,
variables y comentarios de este scaffold.

## 10. Bibliografía técnica relevante ya usada para justificar decisiones

- Anderson (2010) — Kanban como metodología de desarrollo.
- Suri et al. (2022) — Flutter (rendimiento cercano a nativo).
- Pedregosa et al. (2011) — scikit-learn (LinearRegression,
  RandomForestRegressor, validación cruzada, MAE, R²).
- Kanojia & Surywanshi (2024); Chen & Wang (2025) — apps de fitness
  integrales y ML para recomendaciones personalizadas.
- Schoeppe et al. (2016) — apps multicomponente mejoran constancia.

Ver `Anteproyecto.docx` (proyecto original) para el marco completo si
se necesita justificar una decisión de diseño en la documentación
académica (Capítulos 4-6).
