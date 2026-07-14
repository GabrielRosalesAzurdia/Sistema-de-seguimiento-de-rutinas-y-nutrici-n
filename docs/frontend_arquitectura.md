# Frontend (app móvil) — Guía de arquitectura (Club Fitness App)

Documento de orientación para retomar el desarrollo de la app Flutter
(`mobile/`). Explica **qué hay implementado, cómo está organizado y
dónde encontrar cada cosa**. Para las decisiones de negocio y contexto
del proyecto de graduación, ver `CLAUDE.md` en la raíz — este
documento se enfoca solo en el código. Ver también
`docs/backend_arquitectura.md` para la contraparte del servidor.

Estado actual: **las 8 pantallas del mockup están implementadas y
conectadas al API REST real** (sin mocks). Panel admin web (Django)
todavía no existe — ver sección 8 de `CLAUDE.md`.

---

## 1. Stack y arranque

- **Flutter** (Dart SDK `>=3.3.0 <4.0.0`), Material Design, **solo
  Android** en v1.
- **`provider: ^6.1.2`** — declarado en `pubspec.yaml` pero **aún no
  se usa** en el código; el manejo de estado actual es 100%
  `StatefulWidget` + `setState` local por pantalla.
- **`dio: ^5.4.3`** — cliente HTTP hacia el backend Django REST
  Framework.
- **`flutter_secure_storage: ^9.0.0`** — guarda los tokens JWT
  (access/refresh) en almacenamiento cifrado del dispositivo.
- **`fl_chart: ^0.68.0`** — declarado para las gráficas de progreso
  del dashboard/perfil, pero **todavía no se usa** en ninguna pantalla
  (las métricas se muestran como tarjetas de texto, no como gráficas).
- **`intl: ^0.19.0`** — declarado, tampoco usado todavía (no hay
  formateo de fechas/números en el código actual).

Comandos típicos (`mobile/`):

```bash
flutter pub get
flutter run                 # requiere backend corriendo (ver docs/backend_arquitectura.md)
```

No hay archivo `.env` ni configuración por entorno: la URL del backend
está **hardcodeada** en `lib/core/api_client.dart:28`
(`http://10.0.2.2:8000/api`, la IP especial del emulador Android para
`localhost` de la máquina host). Para dispositivo físico o producción
hay que editar esa constante manualmente (ver comentario en el mismo
archivo).

---

## 2. Mapa de carpetas

```
mobile/
  lib/
    main.dart                    # entry point, tema, decide Login vs Home según sesión
    core/
      api_client.dart             # cliente Dio singleton + JWT interceptor + secure storage
      theme.dart                  # AppColors y AppTheme (paleta negro/amarillo/verde/naranja)
    models/
      member.dart                  # Member (perfil, sin correo/teléfono/peso editable)
      routine.dart                  # Exercise, RoutineExerciseItem, Routine
      nutrition_plan.dart            # MealSuggestion, NutritionPlan, NutritionCheckStatus (enum)
    services/                        # una clase por recurso del API, sin capa de repositorio extra
      auth_service.dart                # login / logout / isLoggedIn
      member_service.dart               # GET/PATCH /members/me/
      routine_service.dart               # GET /routines/, /routines/:id/
      nutrition_service.dart              # GET current-plan, POST nutrition-logs (semáforo)
      tracking_service.dart                # POST workout-logs, GET ml/me/progress/
    screens/                                # 1 archivo por pantalla del mockup
      login_screen.dart
      main_nav_screen.dart                    # bottom nav: Inicio → Rutinas → Nutrición → Perfil
      dashboard_screen.dart
      routines_screen.dart
      routine_detail_screen.dart
      log_routine_screen.dart
      nutrition_screen.dart
      profile_screen.dart
      edit_profile_screen.dart
    widgets/                                   # carpeta creada, vacía — sin widgets compartidos aún
  assets/icons/                                 # íconos de ejercicios (referenciados por Exercise.iconUrl)
  test/widget_test.dart                          # test por defecto del template de Flutter, sin actualizar
  android/ ios/ web/ linux/ macos/ windows/       # solo Android es el objetivo real (v1)
  pubspec.yaml
```

No existe una carpeta `providers/` ni `blocs/`: cada pantalla
`Stateful` instancia directamente su(s) `Service` en `initState()` y
guarda el resultado en variables de estado locales.

---

## 3. Arranque y autenticación

`lib/main.dart` decide qué mostrar al abrir la app:

1. `ClubFitnessApp` aplica `AppTheme.darkTheme` (tema único, oscuro) y
   monta `_RootDecider`.
2. `_RootDecider` llama a `AuthService().isLoggedIn()` (verifica si
   hay un `access_token` guardado en `flutter_secure_storage`) y
   muestra `LoginScreen` o `MainNavScreen` según el resultado.

**Login** (`screens/login_screen.dart`): formulario email/contraseña
→ `AuthService.login()` → `POST /auth/login/` → si es exitoso guarda
`access`/`refresh` con `ApiClient.saveTokens()` y navega a
`MainNavScreen` con `pushReplacement` (no se puede volver atrás al
login). El enlace "Olvidé mi contraseña" está sin implementar
(`TODO` en el código, línea 82).

**Cliente HTTP** (`core/api_client.dart`): singleton `ApiClient` que
envuelve una instancia de `Dio`. Un `InterceptorsWrapper` inyecta
automáticamente `Authorization: Bearer <token>` en cada request leyendo
el token de `flutter_secure_storage` — los servicios nunca manejan el
token manualmente. **No hay lógica de refresh token**: si el access
token expira, las requests simplemente empiezan a fallar (no hay
interceptor de reintento con el refresh token todavía).

**Logout**: no hay botón de logout implementado en ninguna pantalla
actualmente (`AuthService.logout()` existe pero no se llama desde la
UI).

---

## 4. Navegación

`screens/main_nav_screen.dart` es el shell principal: un
`BottomNavigationBar` fijo de 4 tabs que intercambia el `body` entre
las 4 pantallas raíz (todas se instancian de una vez en una lista
`const`, así que mantienen su estado al cambiar de tab):

```
Inicio (DashboardScreen) → Rutinas (RoutinesScreen) → Nutrición (NutritionScreen) → Perfil (ProfileScreen)
```

Pantallas secundarias (fuera del bottom nav, con `Navigator.push` y
`AppBar` propio con back button):

- `RoutinesScreen` → tap en una tarjeta → `RoutineDetailScreen(routineId)`
- `RoutineDetailScreen` → botón "Iniciar / Registrar" → `LogRoutineScreen(routine)`
- `LogRoutineScreen` → al guardar, hace `popUntil((route) => route.isFirst)` (vuelve directo al dashboard, saltándose el detalle) y muestra un `SnackBar`.
- `ProfileScreen` → botón "Editar" → `EditProfileScreen(member)` → al volver, `ProfileScreen` recarga su `Future` para reflejar cambios.

---

## 5. Pantallas — detalle

| Pantalla | Archivo | Servicio(s) que consume | Notas |
|---|---|---|---|
| Login | `login_screen.dart` | `AuthService` | Sin recuperación de contraseña (TODO) |
| Inicio / Dashboard | `dashboard_screen.dart` | `MemberService`, `NutritionService`, `TrackingService` | Ver detalle abajo |
| Rutinas | `routines_screen.dart` | `RoutineService.getRoutines()` | Lista las 7 categorías vía `FutureBuilder` |
| Detalle de rutina | `routine_detail_screen.dart` | `RoutineService.getRoutineDetail(id)` | Solo muestra el **orden** de ejercicios, sin checkbox por ejercicio (decisión de negocio, comentada en el código) |
| Registrar rutina | `log_routine_screen.dart` | `TrackingService.logWorkoutSession()` | Un `TextField` de peso inicial/final/reps por ejercicio + tiempo total; arma `ExerciseLogEntry` por ejercicio |
| Nutrición | `nutrition_screen.dart` | `NutritionService.getMyCurrentPlan()` | Si no hay plan aprobado (`null`), muestra mensaje "pendiente de aprobación por el coach" en vez de error |
| Perfil | `profile_screen.dart` | `MemberService.getMyProfile()` | Solo lectura; incluye nota explícita de que peso/medidas los registra el coach |
| Editar Perfil | `edit_profile_screen.dart` | `MemberService.updateMyProfile()` | Solo permite editar edad, altura, meta fitness y nivel de actividad — **nunca** peso/medidas |

### Dashboard (`dashboard_screen.dart`) — la pantalla más compleja

Carga en paralelo con `Future.wait` (`_load()`, líneas 37–53):
`MemberService.getMyProfile()`, `NutritionService.getMyCurrentPlan()`
y `TrackingService.getDaysToGoal()`. Compuesta por widgets privados
internos al archivo (no extraídos a `widgets/`):

- `_MetricsGrid` / `_MetricCard`: grid 2x2 con peso actual/meta, %
  grasa corporal, % agua corporal y "días para meta" (predicción ML).
- `_NutritionMacros` / `_MacroPill`: proteína/carbos/grasas del plan
  aprobado del día.
- `_NutritionSemaphore`: los 3 botones del semáforo diario
  (HECHO/PARCIALMENTE/SE ME FUE) — al tocar uno, actualiza el estado
  local **optimista** y en paralelo llama a
  `NutritionService.registerDailyCheck()` (`POST
  /tracking/nutrition-logs/`). No hay manejo de error si el POST
  falla (el estado local ya cambió).
- `_TodayRoutineCard`: **hardcodeada** ("BRAZO Y ESPALDA", "Aprox 500
  calorías · 60 min") — hay un `TODO` explícito en el código (línea
  293) para reemplazarla por la rutina real del día según un
  calendario semanal, que todavía no existe en el backend.

Nota: "calorías quemadas totales" y "racha" del mockup original
(`CLAUDE.md`, sección 5) **no están implementadas** en esta pantalla
todavía — el dashboard actual solo cubre peso/meta, % grasa, % agua,
días para meta, macros, semáforo y rutina de hoy (placeholder).

---

## 6. Modelos (`lib/models/`)

Los 3 modelos son clases inmutables planas con `factory .fromJson()`,
sin `toJson()` general (cada `Service` arma el `Map` de la request a
mano cuando hace falta, ver `tracking_service.dart` y
`nutrition_service.dart`). No usan `json_serializable` ni generación
de código — todo el parseo es manual.

- **`Member`**: espejo de `MemberAppSerializer` del backend (ver
  comentario en el archivo) — expone medidas/porcentajes calculados
  por el coach pero **nunca** correo/teléfono, y no tiene setters
  editables para peso/medidas.
- **`Routine`** / `Exercise` / `RoutineExerciseItem`: una rutina trae
  su lista de ejercicios ya ordenada (`order` + objeto `exercise`
  anidado).
- **`NutritionPlan`** / `MealSuggestion` / `NutritionCheckStatus`: el
  plan trae sus 5 comidas anidadas; `NutritionCheckStatus` es un
  `enum` de Dart con extensión `apiValue`/`label` para mapear
  `HECHO` / `PARCIALMENTE` / `SE_ME_FUE` hacia y desde el API.

---

## 7. Servicios y endpoints consumidos

| Servicio | Método | Endpoint | Uso |
|---|---|---|---|
| `AuthService` | `login()` | `POST /auth/login/` | Login screen |
| `AuthService` | `logout()` | (solo borra tokens localmente) | No conectado a ninguna UI todavía |
| `MemberService` | `getMyProfile()` | `GET /members/me/` | Dashboard, Perfil |
| `MemberService` | `updateMyProfile()` | `PATCH /members/me/` | Editar Perfil |
| `RoutineService` | `getRoutines()` | `GET /routines/` | Rutinas |
| `RoutineService` | `getRoutineDetail()` | `GET /routines/:id/` | Detalle de rutina |
| `NutritionService` | `getMyCurrentPlan()` | `GET /nutrition/me/current-plan/` | Dashboard, Nutrición |
| `NutritionService` | `registerDailyCheck()` | `POST /tracking/nutrition-logs/` | Semáforo del dashboard |
| `TrackingService` | `logWorkoutSession()` | `POST /tracking/workout-logs/` | Registrar rutina |
| `TrackingService` | `getDaysToGoal()` | `GET /ml/me/progress/` | Dashboard (predicción ML) |

Todos los servicios son clases simples (sin interfaz/abstracción)
que instancian `ApiClient.instance` directamente — no hay inyección de
dependencias ni mocks para tests.

---

## 8. Tema visual (`core/theme.dart`)

`AppColors` centraliza la paleta aprobada por el coach (ver
`CLAUDE.md`, sección 4): fondo `#121212`, superficie `#1E1E1E`,
amarillo `#FFD600`, verde `#00E676`, naranja `#FF6D00`, texto
secundario gris y rojo de peligro `#FF5252`. `AppTheme.darkTheme`
aplica esta paleta a `ThemeData` (cards redondeadas, botones amarillos
con texto negro, bottom nav con selección amarilla). Es el **único**
tema — no hay modo claro ni theming dinámico.

---

## 9. Huecos conocidos / deuda técnica

- **`android/app/src/main/AndroidManifest.xml` no declara
  `<uses-permission android:name="android.permission.INTERNET"/>`** —
  solo está en `android/app/src/debug/AndroidManifest.xml` (que
  Flutter agrega automáticamente en debug). En un **build de
  release**, todas las llamadas de `dio` fallarán silenciosamente por
  falta de permiso de red si no se agrega el permiso al manifest
  principal.
- `ApiClient.baseUrl` está hardcodeado a la IP del emulador Android;
  falta una estrategia de configuración por entorno (dart-define,
  flavors, o archivo `.env`) antes de probar en dispositivo físico o
  desplegar a producción (Render).
- No hay manejo de expiración de JWT (sin refresh automático) ni
  pantalla de logout — al expirar el token, el usuario queda con
  pantallas en estado de carga infinita o errores no manejados.
- `provider`, `fl_chart` e `intl` están declarados en `pubspec.yaml`
  pero no se usan en ningún archivo actual — quedaron reservados para
  cuando se implementen gráficas de progreso y manejo de estado
  compartido (ver mockup: gráficas del dashboard/perfil).
- `_TodayRoutineCard` en el dashboard es texto fijo, pendiente de
  conectarse a un endpoint real de "rutina del día" (no existe aún en
  el backend).
- "Racha" y "calorías quemadas totales" del mockup (sección 5 de
  `CLAUDE.md`) no están implementadas en el dashboard.
- `test/widget_test.dart` es el test placeholder que genera `flutter
  create` por defecto — no hay tests reales del proyecto todavía.
- Carpeta `lib/widgets/` existe pero está vacía; todos los widgets
  reutilizables (`_MetricCard`, `_MacroPill`, etc.) están definidos
  como clases privadas dentro del archivo de cada pantalla, sin
  compartirse entre pantallas (p. ej. `_MacroPill` del dashboard y
  `_MacroChip` de nutrición son casi idénticos pero están duplicados).
