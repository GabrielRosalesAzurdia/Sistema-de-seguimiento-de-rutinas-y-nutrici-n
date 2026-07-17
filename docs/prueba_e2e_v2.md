# Prueba E2E v2 — Verificación del feedback de la primera ronda

Segunda pasada de prueba E2E, enfocada en verificar los cambios hechos
a partir de `docs/prueba_e2e_feedback.md` (la primera ronda). Si no
tocaste algo en esta lista, sigue funcionando igual que en
`docs/prueba_e2e.md` (guía original) — no hace falta repetir esos
pasos, aunque puedes si quieres una pasada completa.

Misma convención: **Acción** → **Resultado esperado**. Si no coincide,
documenta el paso, lo que viste y cualquier traceback.

## 0. Preparación del entorno

```bash
cd backend
source venv/bin/activate
docker compose up -d db
python manage.py migrate
python manage.py loaddata fixtures/seed_data.json   # ver nota abajo
python manage.py runserver
```

> **Nota:** si tu base de datos local ya tiene datos de pruebas
> anteriores (rutinas editadas, miembros creados a mano, etc.),
> `loaddata` puede fallar por conflicto de claves — es lo esperado,
> documentado en `docs/seed_data_pendientes.md`. No bloquea la prueba.

Si ya tienes un superusuario de una sesión anterior, no hace falta
crear otro — solo asegúrate de que tenga `is_staff=True` (se creó así
por default con `createsuperuser`).

App móvil: igual que antes, `flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000/api`
(simulador iOS/macOS) o `flutter run` (emulador Android).

---

## 1. Panel — Login y Logout (bug corregido)

1. **Acción:** entra a `/panel/login/` con tu cuenta de coach.
   **Resultado esperado:** la tarjeta de login ahora se ve como la app
   (logo del gimnasio arriba, "Bienvenido", inputs con fondo oscuro y
   foco amarillo) — ya no se ve con inputs blancos default del
   navegador chocando con el tema oscuro.
2. **Acción:** ya logueado, haz clic en **"Salir"** (arriba a la
   derecha).
   **Resultado esperado:** te desloguea y redirige a
   `/panel/login/` — antes esto daba un error 405 (Django 5 requiere
   POST para logout y el link mandaba un GET).

---

## 2. Panel — Alta de un miembro nuevo (crea su acceso a la app)

1. **Acción:** ve a **Miembros → Agregar Miembro**, llena los datos
   personales (nombre, correo nuevo p. ej. `prueba.nueva@test.com`,
   teléfono, edad, género, altura, meta, nivel de actividad, **días
   planificados de rutina** y **días planificados de dieta** —
   nuevos campos), guarda.
   **Resultado esperado:** mensaje de éxito que incluye una
   **contraseña temporal generada**, algo como "... Contraseña
   temporal: `Xy7kP2mNqR3s` — cópiala y compártela con el miembro, no
   se volverá a mostrar." Anótala para el siguiente paso.
2. **Acción (verificación):** en el listado de Miembros, confirma que
   el nuevo miembro aparece.
   **Resultado esperado:** aparece con sus datos; si buscas por su
   correo en el buscador de la lista, lo encuentra (antes de este
   fix, el buscador rompía si el correo no vivía en `Member.email`).
3. **Acción:** en la app móvil (otra sesión o tras cerrar sesión),
   inicia sesión con el correo del nuevo miembro y la contraseña
   temporal del paso 1.
   **Resultado esperado:** login exitoso, entra al Dashboard — antes
   de este fix, un miembro recién creado **no tenía ningún usuario de
   login** y no podía entrar de ninguna forma.
4. **Acción:** intenta crear otro miembro repitiendo el mismo correo.
   **Resultado esperado:** error de validación de formulario (correo
   duplicado), no crea un miembro roto sin usuario.

---

## 3. Panel — Editar datos personales (próximo pago, cancelar)

1. **Acción:** entra a **Editar Miembro** de un miembro que **no**
   tenga `next_payment_date` definido, o bórralo y guarda.
   **Resultado esperado:** al guardar sin poner fecha de próximo pago,
   se autocompleta como *fecha de inicio + 1 mes*.
2. **Acción:** con el miembro ya guardado, entra otra vez a Editar.
   **Resultado esperado:** la **fecha de inicio** aparece ya llena con
   el valor guardado (antes pedía llenarla de nuevo cada vez).
3. **Acción:** haz clic en **"Pagado"**.
   **Resultado esperado:** `next_payment_date` avanza a *hoy + 1 mes*
   automáticamente (no hace falta escribirla a mano).
4. **Acción:** entra a Editar Miembro y haz clic en **"Cancelar"**
   sin guardar.
   **Resultado esperado:** regresa al listado de Miembros sin guardar
   cambios (botón nuevo, antes no existía).
5. **Acción:** revisa las etiquetas de los campos de medidas en
   cualquier formulario de miembro.
   **Resultado esperado:** todas en español ("Brazo izquierdo (cm)",
   "Cadera (cm)", "Cintura (cm)", etc.) — antes varias aparecían en
   inglés-ish generado por Django ("Left arm cm", "Hip cm", etc.).

---

## 4. Panel — Actualizar datos fitness (separado de datos personales)

1. **Acción:** desde el listado de Miembros, haz clic en
   **"Datos fitness"** junto a un miembro (link nuevo, separado de
   "Editar").
   **Resultado esperado:** pantalla dedicada solo a peso + medidas
   corporales + cuello (sin los campos personales mezclados).
2. **Acción:** ingresa un peso nuevo y guarda.
   **Resultado esperado:** mensaje de éxito; % grasa/agua corporal se
   recalculan automáticamente (Navy Method).
3. **Acción (verificación en backend):** revisa
   `/admin/tracking/bodymeasurementlog/` (Django admin genérico) para
   ese miembro.
   **Resultado esperado:** aparece un **registro nuevo** con la fecha
   de hoy — antes, editar el peso desde el panel **no** creaba ningún
   registro en "Registros de medidas corporales".
4. **Acción:** en la app (pull-to-refresh en el Dashboard del
   miembro), revisa la gráfica de peso.
   **Resultado esperado:** tiene un punto nuevo con el peso recién
   registrado.

---

## 5. App móvil — Gráfica de peso con ejes

1. **Acción:** en el Dashboard, revisa la card "PESO ACTUAL/META" con
   la gráfica de línea (necesitas al menos 2 registros de peso — usa
   el miembro de prueba Ana Martínez, que ya trae 3 en el seed, o el
   miembro del paso 4).
   **Resultado esperado:** el eje Y muestra el peso en kg (ej. "68
   kg", "70 kg") y el eje X muestra el mes de cada registro (ej. "May",
   "Jun", "Jul") — antes la gráfica no tenía ninguna leyenda y podía
   confundirse con una simple diagonal entre dos puntos.

---

## 6. App móvil — Botones de ancho completo + validación al registrar

1. **Acción:** entra a **Rutinas → (cualquier categoría) → detalle**.
   **Resultado esperado:** el botón **"Iniciar"** ocupa todo el ancho
   de la pantalla (con margen a los lados, sin tocar los bordes) — ya
   no se ve pequeño y pegado a la izquierda.
2. **Acción:** dentro de "Registrar rutina", revisa el botón
   **"Registrar"**.
   **Resultado esperado:** también de ancho completo, mismo estilo.
3. **Acción:** sin llenar ningún campo (pesos, repeticiones, tiempo),
   toca **"Registrar"**.
   **Resultado esperado:** aparece un mensaje ("Completa todos los
   campos antes de registrar la rutina.") y **no** se guarda nada —
   antes esto se guardaba silenciosamente con ceros en los campos
   vacíos.
4. **Acción:** llena todos los campos correctamente y registra.
   **Resultado esperado:** SnackBar "¡Rutina registrada!", vuelve al
   Dashboard.

---

## 7. Backend — Calorías quemadas ya no quedan en 0

1. **Acción (verificación en backend):** tras registrar una rutina
   (paso 6.4), revisa `/admin/tracking/workoutsessionlog/` para ese
   registro.
   **Resultado esperado:** el campo **"Calories burned"** tiene un
   valor (las calorías estimadas de esa rutina, ej. 450 para
   Pierna-Cuádriceps) — antes quedaba vacío/`NULL`.
2. **Acción:** revisa la card "CALORÍAS QUEMADAS EN TOTAL" del
   Dashboard en la app.
   **Resultado esperado:** ahora sí suma (ya no se queda en `0 CAL`
   después de registrar rutinas).

---

## 8. Panel — Revisión de nutrición con detalle editable

1. **Acción:** ve a **Nutrición**, en la tabla de pendientes haz clic
   en **"Revisar"** junto a un plan (antes había botones ✓/✕ directos
   en la lista; ahora abre una pantalla de detalle).
   **Resultado esperado:** ves las **5 comidas** (Desayuno, Refacción
   I, Almuerzo, Refacción II, Cena) con sus macros y hasta 3 campos de
   sugerencia de platillo cada una, editables — antes la revisión solo
   mostraba los totales del plan (grasas/carbos/proteína), sin ver ni
   poder tocar las sugerencias por comida.
2. **Acción:** edita/completa alguna sugerencia de platillo y haz clic
   en **"Guardar sin aprobar"**.
   **Resultado esperado:** guarda los cambios sin cambiar el estado
   del plan (sigue pendiente).
3. **Acción:** vuelve a entrar al detalle y haz clic en **"Aprobar"**.
   **Resultado esperado:** el plan pasa a "Dietas Aprobadas y en
   Seguimiento"; en la app, el miembro ve las sugerencias que
   editaste en el paso 2.

---

## 9. Backend — VD1/VD2 con "días planificados" (cierra el TODO de tesis)

1. **Acción:** ve a **Datos del estudio**, revisa la tabla VD1.
   **Resultado esperado:** la columna "Planeadas" ahora muestra el
   valor real de `planned_training_days` del miembro (el que
   definiste al crearlo/editarlo), no un placeholder igual a las
   completadas.
2. **Acción:** revisa la tabla VD2.
   **Resultado esperado:** la columna ahora dice "Días planificados"
   (antes "Días Activos", que confundía — era el mismo bug del
   "1/0" que viste en el Dashboard del panel).
3. **Acción:** en el Dashboard del panel, revisa "Actividad Reciente
   de Miembros".
   **Resultado esperado:** la columna "Días de Nutrición" ahora
   muestra `registrados/planificados` (ej. `1/30`) en vez de
   `1/0` — el "0" confuso que reportaste ya no aparece.
4. **Acción:** haz que un miembro complete más sesiones de las que
   tiene planificadas (o ajusta `planned_training_days` a un número
   bajo, ej. 2, y registra 3 rutinas).
   **Resultado esperado:** el % de VD1 puede superar 100% sin error
   (decisión de negocio confirmada: se considera meta superada).

---

## 10. Backend — Predicción de ML ya no se duplica

1. **Acción (verificación en backend):** revisa
   `/admin/ml_predictions/mlprediction/` para un miembro, cuenta
   cuántas filas tiene con la fecha de **hoy**.
   **Resultado esperado:** como máximo **una** fila por miembro por
   día, sin importar cuántas veces hayas recargado el Dashboard en la
   app hoy — antes cada carga del Dashboard creaba una fila
   `RANDOM_FOREST` nueva.
2. **Acción:** recarga el Dashboard de la app varias veces seguidas
   (pull-to-refresh).
   **Resultado esperado:** "Días para meta" sigue mostrando un valor
   coherente, y el conteo de filas en el paso anterior no crece.

---

## Checklist rápido de cierre

| # | Escenario | Esperado | OK? |
|---|-----------|----------|-----|
| 1 | Logout del panel | Redirige a login, sin error 405 | |
| 2 | Crear miembro nuevo | Contraseña temporal mostrada, login funciona en la app | |
| 3 | Editar sin poner próximo pago | Se autocompleta (+1 mes) | |
| 4 | Reabrir Editar Miembro | Fecha de inicio ya viene llena | |
| 5 | Marcar Pagado | Próximo pago avanza +1 mes desde hoy | |
| 6 | Botón Cancelar en Editar Miembro | Vuelve al listado sin guardar | |
| 7 | Etiquetas de medidas corporales | Todas en español | |
| 8 | Actualizar datos fitness | Crea registro nuevo en medidas corporales | |
| 9 | Gráfica de peso en la app | Ejes X (mes) / Y (kg) visibles | |
| 10 | Botones Iniciar/Registrar | Ancho completo, con margen | |
| 11 | Registrar rutina con campos vacíos | Bloqueado con mensaje de error | |
| 12 | Calorías quemadas tras registrar rutina | Ya no se queda en 0 | |
| 13 | Revisar plan nutricional pendiente | Muestra y permite editar las 5 comidas | |
| 14 | VD1/VD2 en Datos del estudio | Usa días planificados reales, no placeholder | |
| 15 | Predicciones ML repetidas en un día | Máximo 1 fila por miembro por día | |

Si algún punto falla, documenta: paso exacto, comportamiento
observado, y cualquier traceback/log (backend: consola de
`runserver`; app: consola de `flutter run`).
