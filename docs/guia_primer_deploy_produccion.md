# Guía paso a paso — Primer despliegue a producción (Render + Neon + APK)

Fecha de esta guía: 2026-07-22. Escrita para el lanzamiento piloto en
el gimnasio Fitness Club, después de varias rondas de pruebas E2E.
Contexto y decisiones ya tomadas: ver
`docs/decision_lanzamiento_y_ml.md` y el plan de lanzamiento (memoria
del proyecto). Resumen de esas decisiones:

- Base de datos: **Neon Postgres, tier Free** (100 CU-horas/mes, se
  suspende sola tras 5 min de inactividad y despierta automáticamente
  en la siguiente query — comportamiento aceptable, a diferencia de
  Supabase que requiere reactivación manual). **Decisión actualizada
  el 2026-07-22**, reemplaza lo que decía esta guía antes (Render
  Postgres Starter) — ver `docs/migracion_neon_render.md` para el plan
  de contingencia si el consumo de CU-horas se acerca al tope
  mensual.
- Web service del backend: tier **Starter** (siempre activo, sin cold
  starts) — también actualizado el 2026-07-22, antes era Free.
- Distribución de la app: **APK firmado, compartido directamente**
  (no Play Store).
- El asesor de tesis ya autorizó lanzar antes de octubre — la entrega
  final sigue siendo en noviembre 2026, pero mientras antes se lance,
  más datos reales se acumulan para VD1/VD2 y para reentrenar ML más
  adelante.

Los cambios de código que este despliegue necesita (Dockerfile,
`settings.py`, `.env.example`, soporte de `DB_SSLMODE`, el `.joblib`
del modelo ML ya commiteado) **ya están en `main`** del repo del
backend. Lo que falta es 100% manual, en los dashboards de Neon y
Render y en tu máquina para el APK. Esta guía cubre eso.

---

## Parte A — Backend en Render + base de datos en Neon

### A.1 Crear la cuenta y conectar GitHub

1. Entra a [render.com](https://render.com) y crea cuenta (lo más
   simple: "Sign up with GitHub", así ya queda autorizado el acceso a
   tus repos).
2. Si no te registraste con GitHub: ve a **Account Settings → GitHub**
   y conecta tu cuenta, dando acceso al repo
   `Sistema-de-seguimiento-de-rutinas-y-nutrici-n-backend`.

### A.2 Crear la base de datos PRIMERO (antes que el web service)

1. Entra a [neon.tech](https://neon.tech) y crea cuenta (puedes usar
   "Sign in with GitHub").
2. **New Project** → nombre, por ejemplo `club-fitness-db`.
3. **Postgres version**: `16` (para igualar tu `docker-compose.yml`
   local y lo que corre en Render por si algún día migras — ver
   `docs/migracion_neon_render.md`).
4. **Region**: elige la más cercana a donde vaya a estar el web
   service de Render (ej. si tu web service queda en Oregon, elige
   una región de Neon en EE.UU.). Al ser proveedores distintos no hay
   red "interna" compartida como en Render, así que esto solo importa
   para la latencia, no es bloqueante.
5. Crea el proyecto. Neon te da de inmediato una **connection
   string** completa (`postgres://usuario:password@host/db?sslmode=require`).
   Guárdala — la vas a partir en sus 5 componentes para el paso A.4:
   - `Hostname` (el host en la URL)
   - `Port` (`5432`)
   - `Database` (el nombre de la base, normalmente `neondb` o el que
     hayas puesto)
   - `Username`
   - `Password`
6. Anota también la connection string completa en un lugar seguro —
   la necesitas como `NEON_DATABASE_URL` si algún día corres
   `backup_neon.sh` (ver `docs/migracion_neon_render.md`).

### A.3 Crear el Web Service

1. Dashboard → **New +** → **Web Service**.
2. Conecta el repo
   `Sistema-de-seguimiento-de-rutinas-y-nutrici-n-backend`.
3. **Runtime**: Render debería detectar el `Dockerfile` y ofrecer
   runtime **Docker** automáticamente. Si no aparece solo,
   selecciónalo a mano.
4. **Region**: la que quieras (ya no depende de Neon — al ser
   proveedores distintos no hay red interna compartida).
5. **Branch**: `main`.
6. **Instance Type**: **Starter**.
7. Antes de darle "Create", baja a **Environment Variables** y
   agrega las del siguiente paso — Render te deja hacerlo en la misma
   pantalla de creación.

### A.4 Variables de entorno

Agrega estas variables (nombre → valor):

| Variable | Valor |
|---|---|
| `SECRET_KEY` | Genera una nueva, nunca reutilices el default de desarrollo. Corre en tu terminal: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` y pega el resultado. |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | El dominio que Render te asigna: `<nombre-que-elegiste>.onrender.com` (tú eliges ese nombre al crear el servicio en A.3). |
| `CORS_ALLOWED_ORIGINS` | `https://<nombre-que-elegiste>.onrender.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://<nombre-que-elegiste>.onrender.com` |
| `SECURE_SSL_REDIRECT` | `True` |
| `SESSION_COOKIE_SECURE` | `True` |
| `CSRF_COOKIE_SECURE` | `True` |
| `DB_NAME` | el `Database` del paso A.2 (Neon) |
| `DB_USER` | el `Username` del paso A.2 (Neon) |
| `DB_PASSWORD` | el `Password` del paso A.2 (Neon) |
| `DB_HOST` | el `Hostname` del paso A.2 (Neon) |
| `DB_PORT` | `5432` |
| `DB_SSLMODE` | `require` — Neon exige SSL, esta variable ya existe en `settings.py`/`.env.example` para esto. |

No necesitas configurar `PORT` — Render la inyecta sola y el
`Dockerfile` ya la lee (`$PORT`).

Dale **Create Web Service**. Empieza el primer build/deploy — tarda
varios minutos (instala dependencias del `Dockerfile`, corre
migraciones, arranca gunicorn).

### A.5 Verificar el primer deploy

1. En la pestaña **Logs** del web service, espera a ver algo como
   `Applying ... migrations` sin errores, seguido de que gunicorn
   arranca (`Listening at: http://0.0.0.0:xxxx`).
2. Abre `https://<tu-dominio>.onrender.com/panel/login/` en el
   navegador. Debe cargar el formulario de login del panel — nunca
   un error 500 con traceback (si `DEBUG=False` está bien puesto, un
   error real se ve como una página genérica, no un traceback).
3. Si el login (POST) da un error 400 "Bad Request": revisa que
   `CSRF_TRUSTED_ORIGINS` y `ALLOWED_HOSTS` coincidan **exactamente**
   con el dominio real que Render te asignó (lo ves en la parte de
   arriba del dashboard del servicio, puede no ser idéntico al que
   escribiste si el nombre ya estaba tomado).

### A.6 Crear el superusuario real (el coach)

1. En el dashboard del web service, ve a la pestaña **Shell** (Render
   da una terminal contra el contenedor corriendo).
2. Corre:
   ```
   python manage.py createsuperuser
   ```
   Usa el correo real del coach (Alex Ovando) y una contraseña que él
   pueda usar para entrar a `/panel/`.
3. **No corras** `python manage.py loaddata fixtures/seed_data.json`
   en esta shell — ese fixture crea un miembro de prueba con
   contraseña conocida (`Prueba1234`), es solo para desarrollo local.
   Si termina en la base real sería un hueco de seguridad.
4. Entra a `/panel/login/` con ese superusuario y confirma que carga
   el Dashboard del panel.
5. **Antes de dar de alta miembros reales**, confirma que la conexión
   a Neon funciona sin errores intermitentes (revisa los logs del web
   service) — si ves errores de conexión, probablemente falta
   `DB_SSLMODE=require`.

---

## Parte B — App móvil (Android)

### B.1 Generar el keystore de release

Esto es **irreversible y no se puede regenerar**. Si lo pierdes, no
podrás publicar actualizaciones firmadas con la misma identidad —
tendrías que redistribuir la app como si fuera otra app a todos de
nuevo. Guárdalo en un lugar con backup (Drive personal, gestor de
contraseñas con adjuntos, etc.), **nunca solo en tu laptop sin copia**.

En tu terminal:

```bash
keytool -genkey -v -keystore club-fitness-release.keystore \
  -alias club_fitness -keyalg RSA -keysize 2048 -validity 10000
```

Te va a pedir:
- Una contraseña para el keystore (anótala en un lugar seguro).
- Una contraseña para la key (puede ser la misma que la anterior).
- Nombre, organización, ciudad, etc. — datos reales tuyos o del
  gimnasio, no es crítico para un APK de distribución directa.

Guarda el archivo `club-fitness-release.keystore` **fuera** de la
carpeta del proyecto, para evitar subirlo por error a algún repo.

### B.2 Crear `key.properties`

Crea el archivo `mobile/android/key.properties` (este sí puede vivir
dentro del repo — ya está listado en `.gitignore`, así que nunca se
sube a git) con este contenido, usando las contraseñas de arriba y la
ruta real donde guardaste el `.keystore`:

```properties
storePassword=<la contraseña del keystore>
keyPassword=<la contraseña de la key>
keyAlias=club_fitness
storeFile=/ruta/absoluta/a/club-fitness-release.keystore
```

El `build.gradle.kts` del proyecto ya está preparado para leer este
archivo automáticamente si existe (si no existe, el build cae a firma
debug — por eso los builds de desarrollo funcionan sin este archivo).

### B.3 Compilar el APK de release

Una vez el backend ya esté desplegado y tengas su URL real de Render:

```bash
cd mobile
flutter build apk --release --dart-define=API_BASE_URL=https://<tu-dominio>.onrender.com/api
```

El resultado queda en
`mobile/build/app/outputs/flutter-apk/app-release.apk`.

### B.4 Probar antes de distribuir

1. Copia el `.apk` a un Android real (o usa
   `flutter install --release` con el dispositivo conectado por USB y
   depuración USB activada).
2. Android va a bloquear la instalación la primera vez — hay que
   habilitar "Instalar apps de origen desconocido" para la fuente que
   uses (navegador, gestor de archivos, WhatsApp, etc.). Es esperado,
   no viene de Play Store — avisa esto a los miembros cuando
   distribuyas.
3. Da de alta un miembro de prueba desde el `/panel/` real, prueba el
   login con la contraseña temporal que muestra el modal, confirma
   que fuerza la pantalla "Crear tu contraseña", y que después el
   Dashboard carga datos reales (no `10.0.2.2`, que era la IP del
   emulador local).
4. Registra una rutina y marca el semáforo nutricional del día, luego
   confirma en el panel que esos registros aparecen reflejados.

### B.5 Distribuir

Comparte el `.apk` por el medio que ya uses (WhatsApp, Drive, link
directo) con los miembros reales del gimnasio.

---

## Checklist final de verificación

- [ ] Deploy de Render responde en `/panel/login/` con `DEBUG=False`
      (un error real no expone traceback).
- [ ] Login del coach en el panel funciona; formularios POST (crear
      miembro, aprobar dieta) no fallan por CSRF.
- [ ] Alta de un miembro de prueba real genera su `User` + contraseña
      mostrada en el modal, igual que en local.
- [ ] APK release firmado instala en un dispositivo Android real,
      login con ese miembro de prueba funciona contra la URL de
      Render (no `10.0.2.2`).
- [ ] Primer login fuerza "Crear tu contraseña"
      (`must_change_password`) como se espera.
- [ ] Registrar una rutina y un semáforo nutricional desde la app
      aparece reflejado en el panel.
- [ ] Confirmado que la conexión a Neon funciona sin errores SSL
      intermitentes antes de dar de alta miembros reales.
- [ ] Anotado en el calendario el chequeo semanal de CU-horas de Neon
      durante oct-nov 2026 (ver `docs/migracion_neon_render.md`).

---

## Qué sigue después del lanzamiento (no bloquea nada de lo anterior)

Ver `docs/decision_lanzamiento_y_ml.md` para el detalle completo, pero
en resumen:

- El backend ya sirve el modelo Random Forest entrenado con datos
  sintéticos — es un placeholder intencional, no bloquea el
  lanzamiento.
- El uso real ya alimenta las tablas necesarias sin acción adicional
  (`BodyMeasurementLog`, `WorkoutSessionLog`, `DailyNutritionLog`).
- Cuando haya miembros que ya alcanzaron su meta de peso (semanas o
  meses de uso real), construir el script conector que arme el CSV de
  entrenamiento real y reentrenar
  `ml/training/train_progress_model.py` localmente. Nunca entrenar
  dentro de Render — solo commitear el `.joblib` nuevo y hacer push;
  Render redeploya solo y sirve el modelo actualizado.
- Nutrición sigue sin modelo entrenable (no hay un "macro correcto"
  objetivamente observable) — la heurística Mifflin-St Jeor se queda
  indefinidamente, ya es una decisión defendida.
