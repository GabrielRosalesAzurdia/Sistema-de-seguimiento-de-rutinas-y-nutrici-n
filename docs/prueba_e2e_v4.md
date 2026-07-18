# Prueba E2E v4 — Verificación del feedback de la tercera ronda

Cuarta pasada de prueba E2E, enfocada en verificar los cambios hechos
a partir de `docs/prueba_e2e_v3 feedback.md` (hallazgos adicionales
encontrados durante la tercera ronda, además de los 19 puntos ya
verificados en `docs/prueba_e2e_v3.md`). Si no tocaste algo en esta
lista, sigue funcionando igual que en rondas anteriores — no hace
falta repetirlo, aunque puedes si quieres una pasada completa.

Misma convención: **Acción** → **Resultado esperado**. Si no coincide,
documenta el paso, lo que viste y cualquier traceback.

## 0. Preparación del entorno

```bash
cd backend
source venv/bin/activate
docker compose up -d db
python manage.py migrate   # trae la migración nueva 0004 (status SUPERSEDED)
python manage.py runserver
```

> **Nota:** para esta ronda es preferible usar la base que ya tengas
> (con Ana Martínez y los miembros que hayas creado en rondas
> anteriores), porque varios pasos dependen de historial ya existente
> — igual que en la ronda 3.

App móvil: `flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000/api`
(simulador iOS/macOS) o `flutter run` (emulador Android).

---

## 1. Panel — Un plan reemplazado ya no se acumula como "activo"

Reproduce el escenario exacto reportado en la ronda anterior: vencer
un plan aprobado, aprobar su sucesor, y confirmar que ya no quedan dos
planes "activos" para el mismo miembro.

1. **Acción:** aprueba un plan de nutrición cualquiera (si no tienes
   uno a la mano, entra a **Nutrición → Dietas por Revisar**, revisa
   uno pendiente y aprueba). Anota el miembro.
2. **Acción (backend):** en `/admin/nutrition/nutritionplan/`, edita
   ese plan aprobado y cambia `reviewed_at` a una fecha de hace más de
   30 días. Guarda.
3. **Acción:** ve a **Nutrición** en el panel (dispara el chequeo de
   vencimiento al cargar la pantalla).
   **Resultado esperado:** aparece un plan nuevo pendiente de revisión
   para ese mismo miembro en "Dietas por Revisar".
4. **Acción:** entra a revisar ese plan nuevo y haz clic en
   **"Aprobar"**.
   **Resultado esperado:** se aprueba sin error.
5. **Acción:** vuelve a **Nutrición → Dietas Aprobadas y en
   Seguimiento**.
   **Resultado esperado:** el miembro aparece **una sola vez** en la
   lista — antes de este fix aparecía dos veces (el plan viejo y el
   nuevo, ambos con status `APPROVED`).
6. **Acción:** entra al detalle del plan **viejo** (el que venció, no
   el que acabas de aprobar — puedes encontrarlo en
   `/admin/nutrition/nutritionplan/` filtrando por ese miembro).
   **Resultado esperado:** el estado dice **"Reemplazada"**, no
   "Aprobada y en seguimiento". No aparece ningún botón de
   Aprobar/Rechazar/Guardar — la pantalla es de solo lectura, con un
   aviso "Este plan fue reemplazado por uno más reciente" y un link
   directo al plan vigente.
7. **Acción:** intenta forzar un `POST` a ese plan viejo (por ejemplo,
   recargando una pestaña que hayas dejado abierta desde antes del fix
   y haciendo clic en un botón de Aprobar/Rechazar que ya no debería
   existir, o repitiendo la petición con curl/Postman si quieres
   verificarlo a bajo nivel).
   **Resultado esperado:** mensaje de error "Este plan ya no está
   activo y es de solo lectura" — no se genera ningún plan adicional.
8. **Acción (verificación final):** revisa
   `/admin/nutrition/nutritionplan/` filtrando por ese miembro.
   **Resultado esperado:** hay exactamente **un** plan con status
   "Aprobada y en seguimiento" (`is_current=True`), el resto con
   status "Reemplazada" o "Rechazada" según corresponda — nunca dos o
   más con status "Aprobada" al mismo tiempo.

---

## 2. Panel — Página 404 con la paleta del proyecto

1. **Acción (backend, opcional/avanzado):** con `DEBUG=False` en tu
   `.env` local temporalmente, visita una URL que no existe (por
   ejemplo `/panel/esto-no-existe/`).
   **Resultado esperado:** una pantalla simple con la paleta del
   proyecto ("Página no encontrada" + botón "Volver al panel"), no la
   página técnica de debug de Django.
   **Nota:** en desarrollo normal (`DEBUG=True`) seguirás viendo la
   página de debug de Django — es lo esperado, este punto solo aplica
   si quieres verificar el comportamiento de producción (mismo
   comportamiento ya validado para el error 500 en la ronda 3).

---

## 3. Panel — Botón "Generar nueva contraseña"

1. **Acción:** entra a **Editar Miembro** de cualquier miembro
   activo.
   **Resultado esperado:** ves un nuevo botón amarillo **"Generar
   nueva contraseña"**, junto a "Generar nueva dieta" y "Desactivar
   Usuario".
2. **Acción:** haz clic en "Generar nueva contraseña".
   **Resultado esperado:** aparece el mismo modal de contraseña
   temporal que se usa al crear un miembro (fondo oscuro, botón
   "Copiar", botón "Cerrar"), con una contraseña nueva.
3. **Acción:** copia la contraseña, cierra el modal.
   **Acción:** en la app móvil, intenta iniciar sesión con las
   credenciales viejas de ese miembro (la contraseña que tenía antes).
   **Resultado esperado:** el login **falla** — la contraseña anterior
   ya no es válida.
4. **Acción:** inicia sesión con la nueva contraseña generada.
   **Resultado esperado:** entra, pero la app fuerza la pantalla
   **"Crea tu contraseña"** (igual que con cualquier contraseña
   temporal) antes de llegar al Dashboard.

---

## 4. Panel — Datos del estudio: miembro desactivado excluido de VD1/VD2

1. **Acción:** elige un miembro con `participates_in_study=True` y
   con algo de historial (rutinas/nutrición registrada). Anota su
   VD1/VD2 actual en **Datos del estudio** (`/panel/estudio/`).
2. **Acción:** desde el listado de Miembros, desactívalo.
3. **Acción:** vuelve a **Datos del estudio**.
   **Resultado esperado:** ese miembro **ya no aparece** en la lista
   ni se cuenta en el promedio general de VD1/VD2 — antes seguía
   apareciendo con sus datos aunque estuviera desactivado.
4. **Acción:** haz clic en "Exportar a CSV" (con un rango de fechas
   que incluya el historial de ese miembro).
   **Resultado esperado:** el CSV **no** incluye ninguna fila para ese
   miembro.
5. **Acción:** reactiva al miembro y repite el paso 3.
   **Resultado esperado:** vuelve a aparecer con sus datos normales.

---

## 5. App móvil — Sesión: desactivar un usuario con sesión abierta ya no genera loop infinito

Este es el punto más importante de verificar con la consola de
`runserver` a la vista, porque el bug original se manifestaba ahí
(ráfaga de cientos de peticiones 401/refresh por segundo).

1. **Acción:** inicia sesión en la app móvil con un miembro de
   prueba y navega hasta el Dashboard (déjalo cargado).
2. **Acción:** desde el panel (en otra pestaña/dispositivo), **sin
   cerrar la app**, desactiva a ese mismo miembro.
3. **Acción:** en la app, haz pull-to-refresh en el Dashboard, o
   navega a otra pestaña (Rutinas, Nutrición) y vuelve.
   **Resultado esperado:** la app muestra un estado de carga que
   **sí termina** (no se queda girando indefinidamente), y luego te
   regresa automáticamente a la pantalla de **Login** — antes esto
   entraba en un loop infinito de "loading" sin fin.
4. **Acción:** revisa la consola de `runserver` durante el paso 3.
   **Resultado esperado:** ves un puñado de peticiones 401 y como
   mucho un par de `POST /api/auth/refresh/`, no una ráfaga continua
   de cientos de peticiones por segundo ni mensajes de "Broken pipe".
5. **Acción:** intenta iniciar sesión de nuevo con las credenciales de
   ese miembro (todavía desactivado).
   **Resultado esperado:** el login falla (comportamiento ya validado
   en la ronda 3, sigue vigente).
6. **Acción:** reactiva al miembro desde el panel y vuelve a iniciar
   sesión en la app.
   **Resultado esperado:** login exitoso, Dashboard carga con
   normalidad, sin ningún rastro del loop.

---

## 6. App móvil — Gráfica de peso: sin deformación con varios pesajes en el mismo mes

1. **Acción:** desde el panel, registra **3 pesos distintos** para un
   mismo miembro **en el mismo mes calendario**, con valores que no
   sean monótonos (por ejemplo: 71 kg, luego 70 kg, luego 71.5 kg —
   que suba y baje, no solo que suba o baje siempre) vía "Actualizar
   datos fitness".
2. **Acción:** en el Dashboard de la app de ese miembro, revisa la
   card "PESO ACTUAL/META".
   **Resultado esperado:** la curva pasa por los 3 puntos reales sin
   dibujar un "dip" en forma de U por debajo del peso mínimo real —
   antes la curva podía sobrepasar visualmente el rango real de los
   datos (ver `docs/grafica.png` de la ronda anterior).
3. **Acción:** compara contra el punto 14 de `docs/prueba_e2e_v3.md`
   (los puntos del mismo mes deben verse cercanos entre sí en el eje
   X).
   **Resultado esperado:** sigue cumpliéndose — este fix solo tocó la
   forma de la curva (suavizado), no el cálculo de posiciones en el
   eje X, que ya estaba correcto.

---

## Checklist rápido de cierre

| # | Escenario | Esperado | OK? |
|---|-----------|----------|-----|
| 1 | Vencer plan aprobado → aprobar sucesor | Solo un plan queda "Aprobada y en seguimiento" por miembro | |
| 2 | Detalle del plan viejo reemplazado | Estado "Reemplazada", solo lectura, sin botones | |
| 3 | Intentar Rechazar un plan ya reemplazado | Bloqueado, no genera un plan adicional | |
| 4 | URL inexistente con `DEBUG=False` | Página 404 con la paleta del proyecto | |
| 5 | Botón "Generar nueva contraseña" | Modal con nueva contraseña, la vieja deja de funcionar | |
| 6 | Login con contraseña reseteada | Fuerza "Crea tu contraseña" | |
| 7 | Miembro desactivado en Datos del estudio | Ya no cuenta en VD1/VD2 ni aparece en el CSV | |
| 8 | Reactivar miembro | Vuelve a contar en VD1/VD2 | |
| 9 | Desactivar miembro con sesión abierta en la app | Loading termina, regresa a Login, sin ráfaga de peticiones | |
| 10 | Consola de `runserver` durante el punto 9 | Sin loop de 401/refresh ni "Broken pipe" | |
| 11 | 3 pesajes no monótonos en el mismo mes | Curva sin "dip" en forma de U | |

Si algún punto falla, documenta: paso exacto, comportamiento
observado, y cualquier traceback/log (backend: consola de
`runserver`; app: consola de `flutter run`).
