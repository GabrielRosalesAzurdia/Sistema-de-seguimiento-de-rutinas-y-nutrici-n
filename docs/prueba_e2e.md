# Prueba E2E — App móvil + Panel admin (en conjunto)

Guía paso a paso para probar el sistema completo de punta a punta,
verificando que las acciones del **coach en el panel admin** se
reflejen correctamente en la **app móvil del miembro**, y viceversa.
Usa el miembro de prueba sembrado en `backend/fixtures/seed_data.json`
(Ana Martínez).

Convención de esta guía: cada paso indica **Acción** y **Resultado
esperado**. Si el resultado esperado no coincide, es un bug a reportar
(indica el paso, lo que viste vs. lo que se esperaba).

## 0. Preparación del entorno

### 0.1 Backend

```bash
cd backend
source venv/bin/activate          # o el entorno virtual que uses
docker compose up -d db           # PostgreSQL local (ver docker-compose.yml en la raíz)
python manage.py migrate
python manage.py loaddata fixtures/seed_data.json
python manage.py createsuperuser  # cuenta del coach para el panel — usa un email propio
python manage.py runserver
```

**Resultado esperado:** el servidor queda escuchando en
`http://127.0.0.1:8000/`. `loaddata` siembra 29 ejercicios, 7 rutinas,
el calendario semanal, 1 miembro de prueba (`miembro.prueba@fitnessclub.test`
/ `Prueba1234`) y su plan nutricional ya **aprobado**.

> Nota: si ya corriste `loaddata` antes y el panel modificó datos (p. ej.
> editaste ejercicios de una rutina), un segundo `loaddata` puede fallar
> por conflicto de claves — no es un bug, es esperado (ver
> `docs/seed_data_pendientes.md`). En ese caso continúa sin recargar.

El superusuario que crees con `createsuperuser` **es el coach**: al
tener `is_staff=True`, entra al panel en `/panel/` (además del Django
admin genérico en `/admin/`).

### 0.2 App móvil

Corre según tu plataforma de prueba (ver `mobile/README.md`):

```bash
cd mobile
flutter pub get

# Simulador iOS / macOS desktop:
flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000/api

# Emulador Android (no requiere flag, usa el default 10.0.2.2):
flutter run

# Dispositivo físico (celular real en la misma red que tu compu):
flutter run --dart-define=API_BASE_URL=http://<IP-de-tu-compu>:8000/api
```

**Resultado esperado:** la app muestra el splash amarillo con el logo
~1.2s y luego navega a **Login** (si es la primera vez, o si borraste
sesión) o directo al **Dashboard** (si ya había sesión activa válida).

---

## 1. Panel admin — primer acceso del coach

1. **Acción:** abre `http://127.0.0.1:8000/panel/login/` en el
   navegador, inicia sesión con el superusuario creado en el paso 0.1.
   **Resultado esperado:** redirige a `/panel/` (Dashboard), fondo
   negro con acentos amarillo/verde/naranja igual que el mockup
   (`docs/mockups/admin_panel/`).
2. **Acción:** revisa el Dashboard.
   **Resultado esperado:** muestra 1 miembro activo (Ana Martínez),
   indicador de pagos pendientes (0, porque `is_paid: true` en el
   seed), y algún resumen de actividad reciente.
3. **Acción:** intenta entrar a `/panel/` en una pestaña de incógnito
   sin loguearte.
   **Resultado esperado:** redirige a `/panel/login/` (protegido por
   `CoachRequiredMixin`).

---

## 2. App móvil — login del miembro

1. **Acción:** en la app, en la pantalla de Login, ingresa
   `miembro.prueba@fitnessclub.test` / `Prueba1234`.
   **Resultado esperado:** navega al Dashboard (Inicio) sin errores.
2. **Acción:** ingresa credenciales incorrectas.
   **Resultado esperado:** mensaje de error visible, permanece en
   Login (no crashea, no se queda cargando indefinidamente).
3. **Acción:** revisa el Dashboard recién logueado.
   **Resultado esperado (valores del seed):**
   - Peso actual / meta: 68.50 kg → 60.00 kg
   - % grasa corporal: 28.5%
   - % agua corporal: 52.0%
   - Días para meta: un número entero (predicción ML, `RANDOM_FOREST`)
   - Racha: `0 d` (no hay `WorkoutSessionLog` en el seed todavía)
   - Gráfica de peso: 3 puntos (2026-05-01: 71.00, 2026-06-01: 69.80,
     2026-07-01: 68.50 kg), tendencia descendente
   - Nutrición diaria: 135g proteína / 180g carbohidratos / 55g grasas
   - Semáforo nutricional: sin selección todavía
   - Calorías quemadas en total: `0 CAL`
   - Rutina de hoy: depende del día de la semana actual y el género de
     Ana (MUJER) — ver tabla en `apps/routines/migrations/0003_seed_weekly_schedule.py`.
     Si hoy es **sábado o domingo**, la card muestra *"Hoy no tienes
     una rutina asignada. Consulta con tu coach."* — esto es
     comportamiento esperado (día de descanso), no un bug.

---

## 3. Panel admin — Miembros

1. **Acción:** ve a **Miembros**, revisa el listado.
   **Resultado esperado:** aparece Ana Martínez con sus datos, botón
   para editar.
2. **Acción:** entra a "Editar" el perfil de Ana, cambia el peso
   actual (ej. de 68.50 a 67.00 kg) y guarda.
   **Resultado esperado:** guarda sin error; al recalcularse
   `Member.save()`, `body_fat_percentage` / `body_water_percentage`
   se recalculan automáticamente vía Navy Method (los valores del
   listado cambian, ya no son los `28.5`/`52.0` fijos del seed).
3. **Acción:** en la app (pull-to-refresh en el Dashboard, o
   relogueando), revisa los valores de peso y % grasa/agua.
   **Resultado esperado:** reflejan los nuevos valores editados desde
   el panel — confirma que el peso/medidas **solo** los edita el coach
   y la app los muestra de solo lectura (no hay campo editable de peso
   en `profile_screen.dart` / `edit_profile_screen.dart`).
4. **Acción:** intenta "Agregar Miembro" con un email ya existente
   (`ana.martinez@fitnessclub.test`).
   **Resultado esperado:** error de validación de formulario, no crash
   ni error 500.
5. **Acción:** marca a Ana como "pagado" o cambia `next_payment_date`.
   **Resultado esperado:** el Dashboard del panel refleja el cambio en
   el conteo de pagos pendientes.

---

## 4. Panel admin — Rutinas y calendario

1. **Acción:** ve a **Rutinas**, abre "Editar ejercicios" de la
   categoría `PECHO`.
   **Resultado esperado:** lista los 4 ejercicios placeholder
   sembrados (Press de banca, Press inclinado, etc.), permite
   agregar/quitar/reordenar desde el catálogo.
2. **Acción:** agrega un ejercicio nuevo a la rutina de `PECHO` (o
   reordénalos) y guarda.
   **Resultado esperado:** guarda sin error; el orden se refleja igual
   en `RoutineExercise.order`.
3. **Acción:** en la app, ve a **Rutinas → Pecho** (o si hoy toca Pecho
   en el calendario, revisa la card "Rutina de hoy" en el Dashboard).
   **Resultado esperado:** el detalle de la rutina muestra los
   ejercicios en el nuevo orden/lista editada desde el panel — sin
   necesidad de reinstalar la app ni tocar el backend.
4. **Acción:** ve a **Rutinas → Calendario** en el panel, cambia qué
   categoría corresponde hoy para el género MUJER (por ejemplo, si hoy
   es descanso, asígnale una categoría).
   **Resultado esperado:** al refrescar el Dashboard en la app
   (miembro MUJER), la card "Rutina de hoy" cambia acorde.

---

## 5. App móvil — Registrar una rutina completa

1. **Acción:** en la app, entra a **Rutinas**, selecciona cualquier
   categoría (ej. Pierna-Cuádriceps), abre el detalle.
   **Resultado esperado:** lista de 8 ejercicios en orden (Sentadilla
   Sumo → ... → Sentadilla Búlgara), sin marcado individual por
   ejercicio (solo el botón para registrar la rutina completa).
2. **Acción:** toca "Registrar rutina", llena peso inicial/final (lb)
   y repeticiones para cada ejercicio, más el tiempo total, y confirma.
   **Resultado esperado:** SnackBar "¡Rutina registrada!", regresa al
   Dashboard.
3. **Acción:** revisa el Dashboard tras registrar.
   **Resultado esperado:**
   - **Racha** pasa de `0 d` a `1 d` (hay un `WorkoutSessionLog` con
     `completed_at` de hoy).
   - **Calorías quemadas en total** aumenta en el valor de
     `estimated_calories` de esa rutina (450 para
     Pierna-Cuádriceps, según el seed).
4. **Acción (opcional, racha de varios días):** repite el registro en
   días consecutivos (o ajusta `completed_at` vía Django shell/admin
   para simular días pasados) y confirma que la racha suma
   correctamente, y que se rompe (vuelve a 0 o al conteo desde el día
   más reciente) si se salta un día.

---

## 6. App móvil + Panel — Semáforo nutricional diario

1. **Acción:** en el Dashboard de la app, toca una de las 3 opciones
   del semáforo (HECHO / PARCIALMENTE / SE ME FUE).
   **Resultado esperado:** la opción tocada queda resaltada con su
   color (verde/amarillo/rojo), las otras dos quedan atenuadas.
2. **Acción:** toca otra opción del semáforo el mismo día.
   **Resultado esperado:** reemplaza la selección anterior (un solo
   registro por día, no uno por comida — confirmar que no hay
   marcado independiente por Desayuno/Almuerzo/etc.).
3. **Acción (verificación en backend):** revisa
   `DailyNutritionLog` para el miembro vía `/admin/` (Django admin
   genérico) o `manage.py shell`.
   **Resultado esperado:** un solo registro para la fecha de hoy con
   el último estado seleccionado (no 2 registros duplicados).

---

## 7. Panel admin — Revisión de planes nutricionales

1. **Acción:** desde `manage.py shell` o el admin genérico, crea un
   segundo `NutritionPlan` para Ana con `status="PENDING"` (simula que
   el sistema/ML generó una propuesta nueva).
   **Resultado esperado:** aparece en el panel bajo **Nutrición →
   Dietas por Revisar**.
2. **Acción:** en la app, ve a **Nutrición** mientras el plan sigue
   pendiente (antes de aprobarlo).
   **Resultado esperado:** la app sigue mostrando el plan **actual
   aprobado** (`is_current=True`, `status="APPROVED"`) — el plan
   pendiente no debe ser visible ni afectar la vista del miembro hasta
   que el coach lo apruebe.
3. **Acción:** en el panel, aprueba el nuevo plan pendiente.
   **Resultado esperado:** pasa a la lista "Dietas Aprobadas y en
   Seguimiento"; se convierte en el plan `is_current` del miembro.
4. **Acción:** en la app, haz pull-to-refresh en Nutrición/Dashboard.
   **Resultado esperado:** ahora muestra los macros y comidas del plan
   recién aprobado (reemplazando al anterior).
5. **Acción (caso sin plan):** usando un miembro sin ningún plan
   aprobado (crea uno nuevo desde el panel sin asignarle plan), inicia
   sesión en la app con ese usuario y ve a Nutrición.
   **Resultado esperado:** mensaje "Tu plan nutricional está pendiente
   de aprobación por el coach. Vuelve pronto." — sin error 500 (bug ya
   corregido en `MyCurrentPlanView`, ver `apps/nutrition/tests.py`).

---

## 8. App móvil — Perfil (solo lectura) y logout

1. **Acción:** ve a **Perfil**.
   **Resultado esperado:** muestra peso/medidas/% grasa/% agua como
   **solo lectura** — ningún campo editable de peso o medidas.
2. **Acción:** ve a **Editar Perfil**.
   **Resultado esperado:** permite editar nombre, edad, altura, meta,
   nivel de actividad — **NO** peso ni medidas corporales.
3. **Acción:** toca el botón de logout (ícono en Perfil).
   **Resultado esperado:** vuelve a Login; si intentas navegar hacia
   atrás, no regresa al Dashboard (se limpió el stack de navegación).
4. **Acción:** cierra la app completamente y vuelve a abrirla sin
   loguearte de nuevo.
   **Resultado esperado:** muestra Login (no Dashboard) — el logout
   limpió los tokens correctamente.
5. **Acción:** en Login, toca "Olvidé mi contraseña".
   **Resultado esperado:** muestra un SnackBar informativo (funcionalidad
   real de recuperación está fuera de alcance v1).

---

## 9. Panel admin — Datos del estudio (export CSV)

1. **Acción:** ve a **Datos del estudio**, define un rango de fechas
   que cubra los registros creados en los pasos anteriores (ej. todo
   julio 2026), exporta.
   **Resultado esperado:** descarga un CSV con VD1 (% sesiones
   completadas / planificadas) y VD2 (% días con registro nutricional
   / días activos) por usuario. Ana debe aparecer con datos > 0% si
   completaste los pasos 5 y 6.

---

## 10. Regresión — bug de "carga infinita" ya corregido

Ver contexto completo en el historial de commits del repo `mobile`
(`Corregir carga infinita + login saltado`).

1. **Acción:** con el backend **apagado**, abre la app.
   **Resultado esperado:** tras ~10s (timeout de Dio), el Dashboard
   dejar de mostrar el spinner infinito y cae al estado vacío (`-` en
   las cards), no se queda cargando para siempre.
2. **Acción:** desinstala la app del simulador/dispositivo, reinstala,
   ábrela sin loguearte antes.
   **Resultado esperado:** muestra **Login**, nunca entra directo al
   Dashboard (verifica que no sobrevivió ningún token de una sesión
   anterior vía Keychain/almacenamiento del sistema).

---

## Checklist rápido de cierre

| # | Escenario | Esperado | OK? |
|---|-----------|----------|-----|
| 1 | Login coach en panel | Dashboard con 1 miembro activo | |
| 2 | Login miembro en app | Dashboard con datos del seed | |
| 3 | Coach edita peso de Ana | % grasa/agua se recalculan solos | |
| 4 | Coach edita ejercicios de una rutina | Cambio visible en la app sin redeploy | |
| 5 | Miembro registra una rutina | Racha +1, calorías totales suman | |
| 6 | Miembro marca semáforo nutricional | 1 solo registro por día | |
| 7 | Coach aprueba un plan nuevo | App muestra el plan recién aprobado | |
| 8 | Miembro sin plan aprobado | Mensaje de "pendiente", sin error 500 | |
| 9 | Logout + reapertura de app | Vuelve a Login, no a Dashboard | |
| 10 | Backend apagado | Spinner cede tras ~10s, no cuelga infinito | |
| 11 | Desinstalar/reinstalar app | Siempre muestra Login primero | |
| 12 | Export CSV datos del estudio | Descarga con VD1/VD2 por usuario | |

Si algún punto falla, documenta: paso exacto, comportamiento
observado, y si hay traceback/log de error (backend: consola de
`runserver`; app: consola de `flutter run`).
