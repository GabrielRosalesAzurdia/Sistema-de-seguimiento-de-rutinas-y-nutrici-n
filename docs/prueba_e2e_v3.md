# Prueba E2E v3 — Verificación del feedback de la segunda ronda

Tercera pasada de prueba E2E, enfocada en verificar los cambios hechos
a partir de `docs/prueba_e2e_v2 feedback.md` (la segunda ronda). Si no
tocaste algo en esta lista, sigue funcionando igual que en
`docs/prueba_e2e.md`/`docs/prueba_e2e_v2.md` — no hace falta repetir
esos pasos, aunque puedes si quieres una pasada completa.

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
> anteriores, `loaddata` puede fallar por conflicto de claves — es lo
> esperado, documentado en `docs/seed_data_pendientes.md`. No bloquea
> la prueba. De hecho, para esta ronda es preferible usar la base que
> ya tengas (con Ana Martínez y cualquier miembro que hayas creado en
> rondas anteriores), porque varios pasos dependen de historial ya
> existente.

App móvil: `flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000/api`
(simulador iOS/macOS) o `flutter run` (emulador Android).

---

## 1. Panel — Alta de miembro: email duplicado ya no revienta

1. **Acción:** ve a **Miembros → Agregar Miembro**, usa el correo de
   un miembro que ya exista (por ejemplo, repite el correo de Ana
   Martínez o de cualquier miembro que ya hayas creado), llena el
   resto del formulario y guarda.
   **Resultado esperado:** el formulario muestra un error legible
   junto al campo "Correo" (algo como "Ya existe un usuario
   registrado con este correo") — **no** aparece la pantalla técnica
   de error de Django (antes esto tiraba un `IntegrityError` crudo).
2. **Acción:** corrige el correo por uno nuevo y guarda.
   **Resultado esperado:** se crea el miembro normalmente y aparece
   el modal de contraseña temporal (ver punto 2).

---

## 2. Panel — Contraseña temporal en modal

1. **Acción:** crea un miembro nuevo (correo distinto a cualquier
   existente).
   **Resultado esperado:** al guardar aparece un **modal** (no un
   simple mensaje de banner) con la contraseña temporal generada,
   fondo oscuro sobre el resto de la pantalla, con botón **"Copiar"**
   y botón **"Cerrar"**.
2. **Acción:** haz clic en "Copiar" y pega en cualquier campo de
   texto (o en el buscador de miembros).
   **Resultado esperado:** pega exactamente la contraseña mostrada en
   el modal.
3. **Acción:** cierra el modal y recarga la página (F5).
   **Resultado esperado:** el modal no vuelve a aparecer (era un
   mensaje de una sola vez).

---

## 3. Panel — Desactivar / Reactivar miembro (ya no pide llenar el formulario)

1. **Acción:** desde el listado de **Miembros**, haz clic en
   **"Desactivar"** en la fila de cualquier miembro activo (link
   directo en la lista, no hace falta entrar a Editar).
   **Resultado esperado:** el miembro se desactiva de inmediato, sin
   pedir llenar ningún campo (fecha de inicio, edad, etc.) — antes
   esto reutilizaba el formulario completo de "Editar Miembro" y
   fallaba si algún campo no estaba lleno.
2. **Acción (verificación visual):** revisa la fila de ese miembro en
   el listado.
   **Resultado esperado:** la fila se ve atenuada/"apagada" (opacidad
   reducida), con la etiqueta "(inactivo)" junto al nombre, y el link
   "Datos fitness" fue reemplazado por **"Reactivar"**.
3. **Acción (verificación de bloqueo real):** en la app móvil, intenta
   iniciar sesión con las credenciales de ese miembro desactivado.
   **Resultado esperado:** el login **falla** — antes de este fix, un
   miembro "desactivado" en el panel seguía pudiendo loguearse en la
   app porque solo se tocaba `Member.is_active`, nunca `User.is_active`.
4. **Acción:** desde la fila del miembro inactivo, haz clic en
   **"Reactivar"**.
   **Resultado esperado:** el miembro vuelve a verse normal en la
   lista (sin atenuar), y el login en la app vuelve a funcionar.
5. **Acción (mismo fix, desde la pantalla de edición):** entra a
   **Editar Miembro** de un miembro activo, sin cambiar nada, haz clic
   en **"Desactivar Usuario"** (ahora es un botón/form independiente
   del formulario principal).
   **Resultado esperado:** se desactiva sin pedir llenar el formulario
   completo, igual que en el punto 1.

---

## 4. Panel — Fecha de inicio fija y próximo pago desde el último pago

1. **Acción:** entra a **Editar Miembro** de cualquier miembro ya
   existente.
   **Resultado esperado:** el campo **"Fecha de inicio"** aparece
   lleno con el valor original, pero **deshabilitado** (no se puede
   editar) — ya no se puede cambiar después de creado el miembro.
2. **Acción:** en un miembro que **nunca** hayas marcado como
   "Pagado", revisa la columna "Siguiente Pago" en el listado de
   Miembros.
   **Resultado esperado:** dice **"PENDIENTE DE PAGO"**, no una fecha
   — antes mostraba una fecha autocalculada aunque el miembro nunca
   hubiera pagado.
3. **Acción:** en Editar Miembro de ese mismo miembro, haz clic en
   **"Pagado"**.
   **Resultado esperado:** ahora la columna "Siguiente Pago" muestra
   una fecha real (hoy + 1 mes).
4. **Acción (verificación en backend):** revisa
   `/admin/members/member/` para ese miembro, campo
   `last_payment_date`.
   **Resultado esperado:** tiene la fecha de hoy — nuevo campo que no
   existía antes de esta ronda.
5. **Acción:** simula que la fecha de pago ya venció — desde
   `/admin/members/member/`, edita manualmente `next_payment_date` a
   una fecha pasada (por ejemplo, ayer) y guarda.
   **Resultado esperado:** al volver al listado de Miembros, esa fila
   vuelve a mostrar **"PENDIENTE DE PAGO"** en vez de la fecha vencida
   — aplica sin importar la antigüedad del miembro.

---

## 5. Panel — Nutrición: aprobar/rechazar ya no falla (bug crítico corregido)

1. **Acción:** ve a **Nutrición**, entra a **"Revisar"** en cualquier
   plan pendiente (usa uno del fixture o uno generado automáticamente,
   ver sección 6).
   **Resultado esperado:** ves las 5 comidas **en orden de consumo**
   (Desayuno, Refacción I, Almuerzo, Refacción II, Cena) — antes
   podían aparecer en orden alfabético (Almuerzo, Cena, Desayuno...).
2. **Acción:** sin cambiar nada, haz clic en **"Aprobar"**.
   **Resultado esperado:** el plan se aprueba sin ningún error — antes
   esto **siempre** fallaba con "meal_time - Este campo es requerido",
   sin importar los datos ya guardados (bug bloqueante de la ronda
   anterior).
3. **Acción:** vuelve a entrar al detalle del plan que acabas de
   aprobar.
   **Resultado esperado:** ya **no** aparece el botón "Aprobar" (solo
   "Rechazar" y "Guardar") — un plan aprobado no debe poder
   re-aprobarse.
4. **Acción (verificación en la app):** en la app móvil del miembro
   dueño de ese plan, revisa la pantalla **Nutrición**.
   **Resultado esperado:** el plan aprobado aparece ahí.
5. **Acción:** crea otro plan pendiente (sección 6 o vía
   `/admin/nutrition/nutritionplan/`), entra a revisarlo, y haz clic
   en **"Rechazar"**.
   **Resultado esperado:** el plan pasa a "Rechazada"; ver sección 8
   para confirmar la regeneración automática.

---

## 6. Panel/App — Dieta automática al primer peso registrado

1. **Acción:** crea un miembro nuevo (o usa uno sin ningún plan de
   nutrición todavía) y ve a **"Actualizar datos fitness"**, llena
   peso, medidas, y guarda por primera vez para ese miembro.
   **Resultado esperado:** mensaje de éxito adicional: "Se generó una
   dieta sugerida para [nombre], pendiente de tu revisión en
   Nutrición."
2. **Acción:** ve a **Nutrición → Dietas por Revisar**.
   **Resultado esperado:** aparece un plan nuevo para ese miembro,
   marcado como generado (revisa `/admin/nutrition/nutritionplan/`,
   columna `generated_by_ml` en `True`), con macros ya calculados y
   las 5 comidas con macros llenos pero **sin** sugerencias de
   platillo (esas las llenas tú al revisar).
3. **Acción:** vuelve a guardar "Actualizar datos fitness" para ese
   mismo miembro una segunda vez (otro peso).
   **Resultado esperado:** **no** se genera un segundo plan pendiente
   duplicado — el trigger solo aplica en el primer registro de peso.

---

## 7. Panel — Botón manual "Generar nueva dieta"

1. **Acción:** entra a **Editar Miembro** de un miembro que ya tenga
   un plan aprobado y ningún plan pendiente, haz clic en **"Generar
   nueva dieta"**.
   **Resultado esperado:** te lleva directo al detalle de un plan
   nuevo, pendiente de revisión, con macros calculados.
2. **Acción:** sin aprobar ni rechazar ese plan, vuelve a Editar
   Miembro del mismo miembro y haz clic en **"Generar nueva dieta"**
   otra vez.
   **Resultado esperado:** mensaje indicando que ya existe un plan
   pendiente de revisión (no crea un segundo plan duplicado).
3. **Acción:** intenta "Generar nueva dieta" para un miembro que
   **no** tenga peso registrado todavía (recién creado, sin pasar por
   "Actualizar datos fitness").
   **Resultado esperado:** mensaje de error indicando que faltan
   datos (peso/altura/edad/género) antes de poder generar la dieta —
   no debe romper con un error 500.

---

## 8. Panel — Regeneración automática al rechazar

1. **Acción:** retomando el plan que rechazaste en el punto 5.5,
   revisa **Nutrición → Dietas por Revisar**.
   **Resultado esperado:** aparece un plan nuevo pendiente para ese
   mismo miembro, generado automáticamente tras el rechazo (mensaje
   de éxito adicional al rechazar: "Se generó una nueva dieta sugerida
   para [nombre]").
2. **Acción:** entra al detalle del plan **rechazado** (no el nuevo).
   **Resultado esperado:** ya no muestra botones de Aprobar/Rechazar
   (solo lectura), y aparece un aviso "Ya se generó un plan sucesor
   pendiente de revisión" con link directo al plan nuevo.

---

## 9. Panel — Vencimiento mensual de dietas (simulado)

Como no hay forma de esperar 30 días reales, se simula adelantando la
fecha de revisión desde el admin genérico.

1. **Acción:** aprueba un plan de nutrición cualquiera (si no tienes
   uno a la mano, repite el punto 5). Anota el miembro.
2. **Acción (backend):** en `/admin/nutrition/nutritionplan/`, edita
   ese plan aprobado y cambia `reviewed_at` a una fecha de hace más de
   30 días. Guarda.
3. **Acción:** ve a **Nutrición** en el panel (esto dispara el
   chequeo de vencimiento al cargar la pantalla).
   **Resultado esperado:** aparece un plan nuevo pendiente de revisión
   para ese miembro en "Dietas por Revisar" — el plan aprobado sigue
   activo (el miembro sigue viendo el plan viejo en la app) hasta que
   apruebes el nuevo.
4. **Acción:** recarga la pantalla de Nutrición varias veces seguidas.
   **Resultado esperado:** no se generan planes pendientes adicionales
   para ese miembro (ya tiene uno esperando revisión).

---

## 10. Panel — Error 500 amigable

1. **Acción (backend, opcional/avanzado):** si tienes forma de forzar
   `DEBUG=False` en tu `.env` local temporalmente y provocar un error
   no controlado (por ejemplo, deteniendo la base de datos y haciendo
   una petición), revisa la pantalla de error.
   **Resultado esperado:** una pantalla simple con la paleta del
   proyecto ("Algo salió mal" + botón para volver al panel), no la
   página técnica de debug de Django con el traceback completo.
   **Nota:** en desarrollo normal (`DEBUG=True`) seguirás viendo la
   página de debug de Django — es lo esperado, este punto solo aplica
   si quieres verificar el comportamiento de producción.

---

## 11. App móvil — Contraseña temporal obligatoria

1. **Acción:** crea un miembro nuevo desde el panel (o usa uno que
   nunca haya iniciado sesión), copia su contraseña temporal del
   modal.
2. **Acción:** en la app móvil, inicia sesión con el correo del
   miembro y esa contraseña temporal.
   **Resultado esperado:** **no** entra directo al Dashboard — te
   lleva a una pantalla **"Crea tu contraseña"** obligatoria, sin
   flecha de back.
3. **Acción:** intenta salir de esa pantalla con el botón de back del
   sistema/gesto.
   **Resultado esperado:** no te deja salir (la pantalla bloquea la
   navegación hacia atrás mientras sea obligatoria).
4. **Acción:** llena "Contraseña temporal" (la misma que usaste para
   entrar), una nueva contraseña, y su confirmación — usa una que no
   coincida con la confirmación primero.
   **Resultado esperado:** mensaje de error "Las contraseñas nuevas no
   coinciden", no te deja continuar.
5. **Acción:** corrige la confirmación para que coincida y envía.
   **Resultado esperado:** entra al Dashboard normalmente.
6. **Acción:** cierra sesión y vuelve a iniciar sesión con el correo
   del miembro y la **contraseña nueva** que acabas de crear.
   **Resultado esperado:** login exitoso, entra directo al Dashboard
   **sin** pasar por la pantalla de "Crea tu contraseña" (ya no está
   pendiente).
7. **Acción (salida de emergencia):** repite el login con una
   contraseña temporal de otro miembro nuevo, y en la pantalla
   obligatoria de cambio de contraseña, toca **"Cerrar sesión"**.
   **Resultado esperado:** te regresa a la pantalla de Login sin
   crashear.

---

## 12. App móvil — Cambiar contraseña desde Perfil (opcional)

1. **Acción:** con un usuario que ya inició sesión normalmente (sin
   contraseña temporal pendiente), ve a **Perfil** y toca
   **"Contraseña"**.
   **Resultado esperado:** abre la misma pantalla de cambio de
   contraseña, pero esta vez **con** flecha de back y sin bloqueo de
   navegación.
2. **Acción:** ingresa una contraseña actual incorrecta a propósito.
   **Resultado esperado:** mensaje de error indicando que la
   contraseña actual no es correcta (viene del backend).
3. **Acción:** corrige con la contraseña actual real, una nueva
   válida, y confirma.
   **Resultado esperado:** SnackBar "Contraseña actualizada.", vuelve
   a Perfil.

---

## 13. App móvil — Perfil ya no crashea al volver de Editar

1. **Acción:** entra a **Perfil**, toca **"Editar"**, y luego regresa
   con la flecha de la parte superior de la app (sin guardar cambios
   o guardando, cualquiera de los dos casos).
   **Resultado esperado:** vuelve a Perfil normalmente, sin ningún
   error en consola — antes esto producía
   `Unhandled Exception: setState() callback argument returned a Future`.

---

## 14. App móvil — Gráfica de peso: mismo mes, sin saltos

1. **Acción:** desde el panel, registra **2 pesos distintos** para un
   mismo miembro **en el mismo mes calendario** (por ejemplo, dos
   veces en el mes actual, en días distintos) vía "Actualizar datos
   fitness".
2. **Acción:** en el Dashboard de la app de ese miembro, revisa la
   card "PESO ACTUAL/META".
   **Resultado esperado:** los dos puntos se ven **cercanos entre sí**
   en el eje X (ambos dentro del mismo mes), no equiespaciados como si
   fueran meses distintos — antes esto podía verse como un salto de
   "Jul" a "Jul" ocupando todo el ancho de la gráfica.
3. **Acción:** si el miembro tiene registros en meses distintos
   también (ej. Ana Martínez, que trae historial del fixture), revisa
   que esos puntos sí se vean espaciados proporcionalmente según la
   distancia real en días entre fechas.
   **Resultado esperado:** la separación entre puntos refleja el
   tiempo real transcurrido, no un índice fijo.

---

## 15. App móvil — Dona de nutrición

1. **Acción:** en la app de un miembro con un plan de nutrición
   aprobado, entra a la pantalla **Nutrición**.
   **Resultado esperado:** en vez de las 3 píldoras de macros sueltas,
   ahora hay una **gráfica de dona** con las calorías totales al
   centro (ej. "2200 CAL") y una leyenda a la derecha con
   Carbohidratos / Proteínas / Grasas y sus gramos — coincide con
   `docs/nutricion chart mockup.png`.
2. **Acción:** revisa los colores de la dona y la leyenda.
   **Resultado esperado:** Carbohidratos = amarillo, Proteínas =
   naranja, Grasas = verde.
3. **Acción:** compara esos mismos colores con la card "NUTRICIÓN
   DIARIA" del Dashboard (macros del día).
   **Resultado esperado:** los mismos 3 colores en el mismo orden —
   antes el Dashboard tenía proteína en verde y grasas en naranja
   (invertido respecto al mockup de la dona).
4. **Acción:** debajo de la dona, revisa el orden de las 5 tarjetas de
   comida.
   **Resultado esperado:** Desayuno, Refacción I, Almuerzo, Refacción
   II, Cena — en ese orden (mismo fix de orden cronológico que en el
   panel, punto 5.1).

---

## Checklist rápido de cierre

| # | Escenario | Esperado | OK? |
|---|-----------|----------|-----|
| 1 | Alta con correo duplicado | Error de formulario legible, no crash | |
| 2 | Contraseña temporal al crear miembro | Modal con botón Copiar | |
| 3 | Desactivar miembro desde la lista | No pide llenar el formulario | |
| 4 | Fila de miembro inactivo | Se ve atenuada, con "Reactivar" | |
| 5 | Login de miembro desactivado | Falla (bloqueado también en `User`) | |
| 6 | Miembro sin pagos | "PENDIENTE DE PAGO" en vez de fecha | |
| 7 | Editar Miembro | Fecha de inicio deshabilitada, no editable | |
| 8 | Aprobar plan nutricional | Ya no falla con "meal_time requerido" | |
| 9 | Plan ya aprobado | Ya no muestra botón "Aprobar" de nuevo | |
| 10 | Primer peso registrado de un miembro | Genera dieta pendiente automática | |
| 11 | Botón "Generar nueva dieta" | Funciona, no duplica si ya hay pendiente | |
| 12 | Rechazar plan aprobado | Genera reemplazo pendiente automático | |
| 13 | Plan aprobado con `reviewed_at` viejo | Genera reemplazo al abrir Nutrición | |
| 14 | Login con contraseña temporal | Fuerza pantalla "Crea tu contraseña" | |
| 15 | Cambiar contraseña desde Perfil | Funciona, opcional | |
| 16 | Perfil → Editar → volver | Ya no crashea | |
| 17 | Gráfica de peso, 2 pesajes mismo mes | Puntos cercanos, sin salto de mes | |
| 18 | Pantalla Nutrición | Dona con colores C=amarillo/P=naranja/G=verde | |
| 19 | Orden de comidas (panel y app) | Desayuno→Refacción I→Almuerzo→Refacción II→Cena | |

Si algún punto falla, documenta: paso exacto, comportamiento
observado, y cualquier traceback/log (backend: consola de
`runserver`; app: consola de `flutter run`).
