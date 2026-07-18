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
- **VD2**: Constancia al plan nutricional = % días con registro / días planificados de dieta.

**Resuelto**: "sesiones planificadas" (VD1) y "días planificados"
(VD2) son la meta individual que el coach define por miembro al
registrarlo (`Member.planned_training_days` /
`Member.planned_nutrition_days`, panel admin, pantalla Miembros), no
un valor derivado del calendario semanal. Si el miembro completa más
de lo planificado, el % puede superar 100% (se considera meta
superada). Implementado en
`backend/apps/tracking/services.py::compute_study_metrics`, que
además **excluye por completo a los miembros desactivados**
(`Member.is_active=False`) del cálculo — no hay campo de fecha de
baja, así que se excluyen del todo en vez de recortar solo el período
en que estuvieron activos (feedback de la prueba E2E v3).

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
  visibles en la app.** El correo vive únicamente en `User.email`
  (login) — `Member` ya no tiene un campo `email` propio que pudiera
  divergir del de login; expone `Member.email` como property de solo
  lectura que delega a `user.email`.
- **Todo miembro tiene cuenta de acceso a la app desde que se crea.**
  El panel genera la contraseña automáticamente al dar de alta al
  miembro y la muestra en un modal (no un simple banner) al guardar
  (el coach la copia y se la comparte por su medio habitual) — antes
  el alta no creaba ningún `User`, así que un miembro nuevo no podía
  loguearse. Como esa contraseña generada es difícil de recordar, el
  primer login del miembro con ella fuerza obligatoriamente la
  pantalla "Crear tu contraseña" antes de llegar al Dashboard
  (`User.must_change_password`, ver `ChangePasswordScreen` en
  `mobile/` y `ChangePasswordView` en `apps/members/`); después de
  cambiarla también queda disponible como opción normal en Perfil.
  Si el miembro la olvida, el coach puede generar una nueva
  contraseña temporal en cualquier momento desde **Editar Miembro**
  (botón "Generar nueva contraseña", `MemberResetPasswordView`) —
  mismo patrón: modal de una sola vez + `must_change_password=True`
  de nuevo.
- **Próximo pago se calcula desde el último pago registrado, no desde
  la fecha de inicio.** `Member.start_date` (fecha en que el miembro
  se unió al gym) es fija desde la creación y ya no se puede reeditar
  después. Al crear, `next_payment_date = start_date + 1 mes`; cada
  vez que se marca "Pagado" se guarda `last_payment_date = hoy` y
  `next_payment_date = last_payment_date + 1 mes`. Si el miembro nunca
  ha sido marcado como pagado, o si `next_payment_date` ya llegó o
  pasó, el panel muestra "PENDIENTE DE PAGO" en vez de una fecha
  (`Member.payment_status_display`).
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
- **Dieta sugerida automática ("por ML"), aunque hoy es una heurística
  determinística.** El modelo real de ML para dietas no existe todavía
  (no hay datos reales del estudio para entrenarlo, igual que pasa con
  el modelo de "días para meta"); mientras tanto
  `apps/nutrition/services.py::generate_plan_for_member` calcula
  macros con Mifflin-St Jeor + multiplicador de actividad + reparto
  por objetivo, y crea el plan con `generated_by_ml=True` como
  placeholder — mismo patrón que el modelo de días-a-meta con datos
  sintéticos. Se dispara automáticamente en el primer peso registrado
  del miembro (no al crear el miembro: el peso no existe todavía en
  ese punto), se regenera automáticamente si el coach rechaza un plan,
  vence y se regenera solo cada 30 días desde su aprobación (chequeo
  lazy al abrir la pantalla Nutrición del panel, no hay cron), y el
  coach puede forzar una regeneración manual con el botón "Generar
  nueva dieta" en Editar Miembro. **Solo un plan por miembro puede
  estar `APPROVED`/vigente a la vez**: al aprobar un plan nuevo, el
  plan `APPROVED` anterior del mismo miembro pasa a status
  `SUPERSEDED` (no se queda `APPROVED` para siempre) y su detalle
  pasa a ser de solo lectura, sin botones de acción — antes este bug
  permitía que un plan reemplazado siguiera apareciendo como
  "aprobado" en el panel, y que "Rechazarlo" disparara otra
  generación automática, acumulando varios planes "activos" para el
  mismo miembro (feedback de la prueba E2E v3). La heurística
  **nunca** llena las
  sugerencias de platillo (`suggestion_1/2/3`) — esas siempre las
  escribe el coach al 100%. Se guarda un snapshot de lo sugerido
  originalmente (`NutritionPlan.ml_suggested_*`) para comparar contra
  lo que el coach termina aprobando, como insumo de un reentrenamiento
  futuro con datos reales — no hay reentrenamiento en vivo.
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
   - Tras un login con contraseña temporal (`must_change_password`),
     redirige obligatoriamente a **"Crear tu contraseña"**
     (`screens/change_password_screen.dart`, `isMandatory: true`) en
     vez del Dashboard; sin flecha de back, con salida de emergencia
     "Cerrar sesión". La misma pantalla se reusa, no obligatoria,
     desde Perfil.
   - Si el backend responde 401 de forma persistente incluso después
     de refrescar el token (ej. el coach desactiva al miembro con la
     sesión abierta en el celular), `ApiClient`
     (`core/api_client.dart`) fuerza un logout local y navega de
     vuelta a Login vía un `navigatorKey` global
     (`core/navigation.dart`) — antes esto entraba en un loop
     infinito de reintentos (refresh 200 + reintento 401 sin límite,
     feedback de la prueba E2E v3).
2. **Inicio / Dashboard** — peso actual/meta, % grasa, % agua, días
   para meta (ML), racha, macros del día, semáforo nutricional,
   calorías quemadas totales, rutina de hoy — `dashboard_screen.dart`
3. **Rutinas** (listado de 7 categorías) — `routines_screen.dart`
4. **Detalle de rutina** (lista de ejercicios en orden) —
   `routine_detail_screen.dart`
5. **Registrar rutina** (peso inicial/final + reps por ejercicio +
   tiempo total) — `log_routine_screen.dart`
6. **Nutrición** (dona de macros con calorías totales al centro +
   5 tiempos de comida con sugerencias, en orden de consumo:
   Desayuno, Refacción I, Almuerzo, Refacción II, Cena) —
   `nutrition_screen.dart`, dona en `widgets/nutrition_chart.dart`
7. **Perfil** (solo lectura de peso/medidas) — `profile_screen.dart`
8. **Editar Perfil** (nombre, edad, altura, meta, nivel de actividad —
   SIN peso/medidas) — `edit_profile_screen.dart`

## 6. Pantallas del panel admin (Django) — ya construidas

Panel propio en `backend/apps/panel/` (templates Django server-side,
sin HTMX/Alpine ni frontend separado — se priorizó la opción más
rápida de implementar dado el tiempo limitado, coherente con "sin
costo, un solo desarrollador"). Replica el mockup — imágenes reales en
`docs/mockups/admin_panel/` (índice en `docs/mockups/README.md`). El
**Django admin genérico** (`apps/*/admin.py`) se mantiene aparte,
disponible en `/admin/` para tareas de soporte (crear datos de prueba,
depurar), pero el coach usa `/panel/`.

Pantallas:

- **Login/Logout** (`/panel/login/`, `/panel/logout/`) — logout es
  POST-only (Django 5), el link del nav manda un form, no un `<a>`.
- **Dashboard** (`/panel/`): miembros activos, pagos pendientes, %
  constancia nutricional, actividad reciente (días con registro
  nutricional / planificados por miembro).
- **Miembros** (`/panel/miembros/`): listado + búsqueda. Miembros
  desactivados se ven atenuados ("dim") en la fila, con "Reactivar" en
  vez de "Datos fitness". Edición separada en dos flujos:
  - **"Editar Miembro"** (`/panel/miembros/<pk>/editar/`, también
    "Agregar Miembro"): datos personales, correo (crea/actualiza el
    `User` de login, valida unicidad en el form — ya no revienta con
    `IntegrityError`), teléfono, edad, género, altura, meta/objetivo,
    **días planificados de rutina/dieta (mensuales)**, fecha de inicio
    (fija desde la creación, no reeditable), próximo pago, botones
    Cancelar / Pagado / Generar nueva dieta / Generar nueva
    contraseña / Desactivar Usuario (Reactivar Usuario si ya está
    inactivo) — Desactivar/Reactivar son ahora una vista independiente
    (`MemberToggleActiveView`) que NO depende de validar el
    formulario completo, y desactiva tanto al `Member` como al `User`
    (bloquea también el login en la app). Al crear, genera una
    contraseña aleatoria mostrada en un modal (el coach se la
    comparte al miembro por su medio habitual); "Generar nueva
    contraseña" (`MemberResetPasswordView`) reusa el mismo modal para
    resetear la de un miembro que la olvidó, sin pasar por el
    formulario completo tampoco.
  - **"Actualizar datos fitness"** (`/panel/miembros/<pk>/fitness/`):
    peso + todas las medidas corporales + cuello. Cada guardado crea
    un `tracking.BodyMeasurementLog` nuevo (alimenta la gráfica de
    peso de la app) y recalcula % grasa/agua vía `Member.save()`.
- **Rutinas** (`/panel/rutinas/`): listado de las 7 categorías +
  "Editar ejercicios" por rutina (selección desde catálogo
  predefinido) + grilla del calendario semanal por género
  (`/panel/rutinas/calendario/`).
- **Nutrición** (`/panel/nutricion/`): "Dietas por Revisar" / "Dietas
  Aprobadas y en Seguimiento" — cada fila enlaza a un detalle
  (`/panel/nutricion/<pk>/revisar/`) que muestra y permite **editar
  las 5 comidas** (macros + hasta 3 sugerencias de texto por tiempo de
  comida) antes de Aprobar/Rechazar/Guardar sin aprobar (botones
  condicionados por estado: un plan ya aprobado no vuelve a mostrar
  "Aprobar"). Rechazar un plan dispara automáticamente la generación
  de un reemplazo pendiente (ver decisión de negocio en sección 3).
  Al abrir esta pantalla también corre el chequeo de vencimiento
  mensual de dietas aprobadas.
- **Datos del estudio** (`/panel/estudio/`): rango de fechas, VD1/VD2
  promedio y por miembro, botón "Exportar a CSV" (enlaza al endpoint
  `GET /api/tracking/study-export/?start=...&end=...`).

## 7. Estructura del backend

```
backend/
  config/                  # settings, urls, wsgi
  common/                  # permissions.py: IsCoach, IsCoachOrReadOnly, IsOwnerOrCoach (compartidos)
  apps/
    members/                # User (auth), Member (perfil completo, sin email propio: usa user.email)
    routines/                # RoutineCategory, Exercise, Routine, RoutineExercise, ScheduledRoutineDay
    nutrition/                # NutritionPlan, MealSuggestion (status: pendiente/aprobado/rechazado),
                              # services.py (generate_plan_for_member: heurística "por ML")
    tracking/                # WorkoutSessionLog, WorkoutExerciseEntry, DailyNutritionLog,
                              # BodyMeasurementLog, services.py (VD1/VD2, racha, calorías), StudyExportView
    ml_predictions/           # MLPrediction, services.py (inferencia), trained_models/
    panel/                   # Panel admin server-rendered (ver sección 6): views.py, forms.py,
                              # utils.py (add_one_month), templates/panel/*.html
```

Autenticación: JWT (`djangorestframework-simplejwt`), login con email
vía `/api/auth/login/`. Un solo modelo `User` (`members.User`):
`is_staff=True` = coach (panel admin), `is_staff=False` = miembro
(app), vinculado a su `Member` vía `Member.user`.

## 8. Próximos pasos sugeridos (orden recomendado)

1. `cd backend && pip install -r requirements.txt`, configurar
   `.env` (copiar de `.env.example`), levantar Postgres
   (`docker compose up db`), correr `python manage.py migrate` y
   `createsuperuser` (ese superusuario es el coach: entra a `/panel/`).
2. Conectar Flutter (`cd mobile && flutter pub get`) contra el backend
   local (`ApiClient.baseUrl` / `--dart-define=API_BASE_URL=...`,
   ajustar según emulador/dispositivo — ver `mobile/README.md`).
3. **Pendiente real, bloqueado en el coach** (no en diseño/código):
   cargar el catálogo de ejercicios reales del gimnasio (nombres
   exactos de las máquinas + íconos/fotos, ver
   `docs/requerimientos_resumen.md` y
   `docs/seed_data_pendientes.md`) y los miembros reales (~85-186).
   Hoy el seed trae ejercicios "(placeholder)" en 5 de las 7
   categorías y un único miembro de prueba (Ana Martínez). El coach
   entregará esto "otro día" — mientras tanto, seguir usando el
   fixture de prueba para desarrollo.
4. Reentrenar el modelo de ML con datos reales una vez concluya el
   período de estudio (oct-nov 2026): exportar
   `GET /api/tracking/study-export/` y volver a correr
   `ml/training/train_progress_model.py` con ese CSV en vez del
   sintético (mismo comando, solo cambia el archivo de entrada).

Historial de decisiones ya resueltas en sesiones anteriores (fórmula
Navy Method de % grasa/agua, calendario semanal de rutinas, conexión
del pipeline de ML con datos sintéticos, definición operacional de
VD1/VD2, panel admin completo, feedback de la primera prueba E2E): ver
`git log` de cada repo — este documento ya no repite el detalle de
cada una para no quedar desactualizado.

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
