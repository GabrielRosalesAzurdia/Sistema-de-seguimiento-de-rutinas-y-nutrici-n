# Backend — Guía de arquitectura (Club Fitness App)

Documento de orientación para retomar el desarrollo del backend Django.
Explica **qué hay implementado, cómo está organizado y dónde encontrar
cada cosa**. Para las decisiones de negocio y contexto del proyecto de
graduación, ver `CLAUDE.md` en la raíz — este documento se enfoca solo
en el código.

Estado actual: **modelos, API REST y Django admin genérico completos.
Falta construir la UI personalizada del panel web** (ver sección 8).

---

## 1. Stack y arranque

- **Django 5.0** + **Django REST Framework 3.15**
- **PostgreSQL** (`psycopg2-binary`)
- **JWT** vía `djangorestframework-simplejwt`
- **scikit-learn / pandas / numpy / joblib** para inferencia ML
- **CORS** vía `django-cors-headers` (para consumo desde Flutter / futuro
  panel web)
- **WhiteNoise** para estáticos, **Gunicorn** como servidor WSGI en
  producción (Render, ver `Dockerfile`)

Comandos típicos (`backend/`):

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # completar SECRET_KEY, DB_*, etc.
docker compose up db          # Postgres local (ver docker-compose.yml en la raíz)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Panel Django admin genérico: `http://localhost:8000/admin/`
Login API (coach o miembro, por email): `POST /api/auth/login/`

---

## 2. Mapa de carpetas

```
backend/
  config/
    settings.py     # config Django/DRF/JWT/CORS, todo vía variables de entorno (.env)
    urls.py          # router raíz: /admin/, /api/auth/, /api/<app>/
    wsgi.py
  apps/
    members/          # Autenticación (User) + perfil del miembro (Member)
    routines/          # Catálogo de ejercicios, rutinas y su composición semanal
    nutrition/         # Planes nutricionales (macros) + flujo de aprobación del coach
    tracking/           # Registros de entrenamiento, semáforo nutricional, medidas, export CSV
    ml_predictions/      # Predicción "días para meta" (scikit-learn / heurística)
  manage.py
  requirements.txt
  Dockerfile
  .env.example
```

Cada app de `apps/` sigue el mismo patrón interno: `models.py` →
`serializers.py` → `views.py` → `urls.py` → `admin.py`.

---

## 3. Autenticación y permisos

Un único modelo de usuario (`apps.members.models.User`, extiende
`AbstractUser`), login por **email** (`USERNAME_FIELD = "email"`).

- `is_staff=True` → **coach/dueño**: acceso al Django admin y a los
  endpoints administrativos del API.
- `is_staff=False` → **miembro**: acceso solo a "sus" endpoints en la
  app móvil, vinculado vía `Member.user` (OneToOne).

Endpoints de auth (`config/urls.py`):
- `POST /api/auth/login/` — `EmailTokenObtainPairView`
  (`apps/members/views.py:20`), devuelve `access`/`refresh` JWT.
- `POST /api/auth/refresh/` — refresh estándar de simplejwt.

Configuración JWT (`config/settings.py:116`): access token 8h, refresh
14 días.

**Patrón de permisos repetido en cada app** (cada app define su propia
clase, no hay una compartida todavía):
- `IsCoach` — solo `request.user.is_staff` (usado para todo lo
  administrativo: altas de miembros, revisión de dietas, medidas
  corporales, export CSV).
- `IsCoachOrReadOnly` (en `routines`) — miembros autenticados leen,
  solo el coach escribe.
- `IsOwnerOrCoach` (en `tracking`) — cualquier autenticado entra a la
  vista, pero el `get_queryset()` filtra: el miembro solo ve sus
  propios registros (`member=user.member_profile`), el coach ve todo.

`REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"]` es `IsAuthenticated`
por defecto (`config/settings.py:109`), así que cualquier vista sin
`permission_classes` explícito ya exige login.

---

## 4. Apps del dominio

### 4.1 `apps/members` — usuarios y perfil

**Modelos** (`models.py`):
- `User(AbstractUser)` — email único como login.
- `Member` — perfil completo del miembro: datos personales (nombre,
  correo, teléfono — **solo panel admin**), datos físicos (peso,
  medidas, % grasa, % agua — **editables solo por el coach**), meta
  fitness (`FitnessGoal`), nivel de actividad (`ActivityLevel`),
  membresía/pagos (`is_paid`, `next_payment_date`), y flags del
  estudio (`informed_consent_signed`, `participates_in_study`).
  - Propiedades calculadas: `full_name`, `imc` (usado como insumo del
    modelo de ML).

**Endpoints** (`urls.py`, prefijo `/api/members/`):
| Método/ruta | Vista | Quién |
|---|---|---|
| CRUD `/api/members/` | `MemberAdminViewSet` | Coach (`IsCoach`) — pantalla "Miembros" del panel |
| GET/PUT/PATCH `/api/members/me/` | `MyProfileView` | Miembro autenticado — pantalla "Perfil" / "Editar Perfil" |

**Serializers** — tres variantes clave para respetar la regla de
negocio "el peso lo edita solo el coach":
- `MemberAdminSerializer` — todos los campos (panel admin).
- `MemberAppSerializer` — solo lectura, sin email/teléfono, incluye
  peso/medidas pero de solo lectura (pantalla Perfil de la app).
- `MemberAppEditableSerializer` — el subconjunto que el miembro sí
  puede editar (nombre, edad, altura, meta, nivel de actividad) — **no
  incluye peso ni medidas**.

### 4.2 `apps/routines` — catálogo y rutinas

**Modelos**:
- `RoutineCategory` (TextChoices) — las 7 categorías fijas.
- `Exercise` — catálogo predefinido, con `icon`/`reference_photo`
  (para no subir imágenes repetidas), `category`, `is_active`.
- `Routine` — una por categoría (`category` es `unique=True`), con
  duración/calorías estimadas.
- `RoutineExercise` — tabla intermedia `Routine`↔`Exercise` con
  `order` (la app solo muestra orden, no marca por ejercicio).

**Endpoints** (prefijo `/api/routines/`), todos `IsCoachOrReadOnly`:
- `/api/routines/exercises/` — CRUD catálogo de ejercicios.
- `/api/routines/routine-exercises/` — CRUD de la composición semanal
  de una rutina (pantalla admin "Editar ejercicios").
- `/api/routines/` — CRUD de rutinas, serializadas con sus ejercicios
  anidados en orden (`RoutineSerializer.exercises`).

### 4.3 `apps/nutrition` — planes nutricionales

**Modelos**:
- `NutritionPlan` — macros totales (`total_calories`, `protein_g`,
  `carbs_g`, `fats_g`) por miembro, `status`
  (`PENDING_REVIEW`/`APPROVED`/`REJECTED`), flag `generated_by_ml` +
  FK opcional a `MLPrediction`, `is_current` (un solo plan vigente por
  miembro), `reviewed_by`/`reviewed_at`.
- `MealSuggestion` — hasta 3 sugerencias por tiempo de comida
  (`MealTime`: 5 valores) dentro de un plan, con sus propios macros.

**Endpoints** (prefijo `/api/nutrition/`):
| Método/ruta | Vista | Quién |
|---|---|---|
| GET `/api/nutrition/me/current-plan/` | `MyCurrentPlanView` | Miembro — plan vigente y **aprobado** (pantalla "Nutrición") |
| CRUD `/api/nutrition/plans/` | `NutritionPlanAdminViewSet` | Coach — pantallas "Dietas por Revisar" / "Aprobadas" |
| PATCH `/api/nutrition/plans/<id>/review/` | `ReviewNutritionPlanView` | Coach — aprobar/rechazar (setea `reviewed_by`/`reviewed_at`) |

Regla de negocio clave ya implementada: `MyCurrentPlanView` solo
devuelve un plan si `status="APPROVED"` — un plan pendiente nunca
llega al usuario final.

### 4.4 `apps/tracking` — registros de actividad y export del estudio

**Modelos**:
- `WorkoutSessionLog` — sesión de rutina completada (`duration_minutes`,
  `calories_burned`), fuente principal de **VD1**.
- `WorkoutExerciseEntry` — detalle por ejercicio dentro de una sesión
  (peso inicial/final en lb, reps).
- `NutritionCheckStatus` / `DailyNutritionLog` — el **semáforo diario
  único** (`HECHO`/`PARCIALMENTE`/`SE_ME_FUE`), `unique_together =
  ["member", "date"]` → fuente de **VD2**.
- `BodyMeasurementLog` — historial mensual de peso/medidas, **solo el
  coach lo crea** (`recorded_by`), preserva histórico aunque
  `Member.current_weight_kg` se sobreescriba.

**Endpoints** (prefijo `/api/tracking/`):
| Método/ruta | Vista | Notas |
|---|---|---|
| CRUD `/api/tracking/workout-logs/` | `WorkoutSessionLogViewSet` | Crea sesión + entradas anidadas en un solo POST (`WorkoutSessionLogSerializer.create`) |
| CRUD `/api/tracking/nutrition-logs/` | `DailyNutritionLogViewSet` | `create()` hace `update_or_create` → un solo registro por día aunque el usuario reenvíe |
| CRUD `/api/tracking/measurement-logs/` | `BodyMeasurementLogViewSet` | Solo coach (`IsCoach`) |
| GET `/api/tracking/study-export/?start=&end=` | `StudyExportView` | Solo coach — CSV con VD1/VD2 por miembro |

**`StudyExportView` (`views.py:63`)**: recorre `Member.objects.filter(
participates_in_study=True)` y por cada uno calcula VD1 (%
sesiones completadas/planificadas) y VD2 (% días con registro
nutricional/días activos). **Pendiente confirmado en el propio código**
(`views.py:95-99`): "sesiones planificadas" hoy usa `planned =
completed` como placeholder (da VD1 = 100% siempre) — falta cerrar con
el asesor la definición operacional y reemplazarla. Ver también
`CLAUDE.md` sección 1 y 8.

### 4.5 `apps/ml_predictions` — predicción de progreso

**Modelo**: `MLPrediction` — guarda cada inferencia: `model_type`
(`LINEAR_REGRESSION`/`RANDOM_FOREST`), `input_features` (JSON snapshot:
edad, IMC, nivel actividad, meta, adherencias, etc.),
`predicted_days_to_goal`, métricas `mae`/`r2_score` si están
disponibles.

**`services.py`** — capa de inferencia, desacoplada de las vistas:
- `_load_model()` intenta cargar
  `trained_models/random_forest_progress_v1.joblib` (aún no existe en
  el repo — se entrenará con datos reales oct-nov 2026, ver
  `ml/training/`).
- `predict_days_to_goal(member, training_adherence, nutrition_adherence)`
  — si no hay modelo entrenado, usa una **heurística placeholder**
  (días ≈ `peso_diff_kg * 14 / adherence_factor`) documentada con TODO
  explícito para reemplazarla.
- `_vectorize()` — mapea features categóricas a números; debe
  mantenerse sincronizado con el preprocesamiento del script de
  entrenamiento cuando exista.

**Endpoints** (prefijo `/api/ml/`):
| Método/ruta | Vista | Notas |
|---|---|---|
| GET `/api/ml/me/progress/` | `MyProgressPredictionView` | Miembro — calcula adherencia de los últimos 30 días desde `WorkoutSessionLog`/`DailyNutritionLog`, llama al servicio, **persiste** un `MLPrediction` y lo devuelve. Alimenta "DÍAS PARA META" del dashboard. |
| GET `/api/ml/predictions/` | `MLPredictionAdminViewSet` (read-only) | Solo admin — histórico |

Nota: `training_adherence` asume ~12 sesiones planificadas en 30 días
(placeholder, mismo TODO que en `StudyExportView`).

---

## 5. Cómo encajan las pantallas de la app / panel con el API

| Pantalla | Endpoint(s) principales |
|---|---|
| Login | `POST /api/auth/login/` |
| Dashboard (app) | `GET /api/members/me/`, `GET /api/ml/me/progress/`, `GET /api/nutrition/me/current-plan/`, `GET/POST /api/tracking/nutrition-logs/` |
| Rutinas / Detalle | `GET /api/routines/` |
| Registrar rutina | `POST /api/tracking/workout-logs/` |
| Nutrición (app) | `GET /api/nutrition/me/current-plan/` |
| Perfil / Editar perfil | `GET/PUT /api/members/me/` |
| Panel — Miembros | `/api/members/` (`MemberAdminViewSet`) |
| Panel — Rutinas / Editar ejercicios | `/api/routines/routine-exercises/`, `/api/routines/exercises/` |
| Panel — Nutrición (revisar/aprobar) | `/api/nutrition/plans/`, `/api/nutrition/plans/<id>/review/` |
| Panel — Datos del estudio | `GET /api/tracking/study-export/` (CSV) |

---

## 6. Lo que NO existe todavía en el backend

- **UI del panel web** (templates/HTMX o frontend separado) — hoy solo
  hay Django admin genérico + API. Ver `CLAUDE.md` sección 6 para el
  detalle de pantallas pendientes.
- **Modelo de ML entrenado real** — `services.py` corre en modo
  heurístico hasta que se entrene con datos de oct-nov 2026 y se
  coloque el `.joblib` en `apps/ml_predictions/trained_models/`.
- **Fórmula de % grasa / % agua corporal** — hoy son campos que el
  coach puede llenar manualmente (`BodyMeasurementLog`,
  `Member.body_fat_percentage`/`body_water_percentage`); no hay
  cálculo automático a partir de las medidas (p. ej. Navy Method).
- **Definición operacional de "sesiones planificadas"** para VD1 —
  placeholder en `StudyExportView` y en `MyProgressPredictionView`.
- **Tests automatizados** — no se encontró carpeta `tests/` ni archivos
  `test_*.py` en ninguna app.
- **Notificaciones push** — fuera de alcance v1 (confirmado, no es un
  pendiente técnico).

---

## 7. Puntos de extensión frecuentes

- **Agregar un campo a `Member`**: recordar actualizar los 3
  serializers (`MemberAdminSerializer`, `MemberAppSerializer`,
  `MemberAppEditableSerializer`) según a quién debe ser visible/editable.
- **Nuevo endpoint que distingue coach vs miembro**: seguir el patrón
  `IsCoach` / `IsOwnerOrCoach` con `get_queryset()` filtrando por
  `request.user.member_profile` — no hay una permission class
  compartida entre apps, así que si se crea una debe ir en un módulo
  común (no existe todavía, hoy está duplicada en cada `views.py`).
- **Reemplazar el modelo de ML**: solo tocar
  `apps/ml_predictions/services.py::predict_days_to_goal` — las vistas
  y serializers no cambian.
- **Cerrar la definición de VD1**: los dos lugares a tocar son
  `apps/tracking/views.py::StudyExportView` (línea ~99) y
  `apps/ml_predictions/views.py::MyProgressPredictionView` (línea ~28).
