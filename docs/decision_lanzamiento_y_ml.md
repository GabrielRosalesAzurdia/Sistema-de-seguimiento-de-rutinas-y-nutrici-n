# Lanzamiento anticipado y proceso de ML — notas de decisión

**Proyecto:** Club Fitness App — Gabriel Alejandro Rosales Azurdia,
Ingeniería en Sistemas de Información, UMG.

Respuestas a preguntas planteadas fuera del flujo de implementación
sobre la posibilidad de lanzar el sistema antes de octubre 2026 y cómo
debería manejarse el entrenamiento de los modelos de ML, dado que el
backend se despliega en Render.com como web service.

**Contenido:**
1. ¿Se puede lanzar antes de octubre sin afectar el diseño de tesis?
2. Entrenamiento de modelos con el backend en Render
3. Proceso de recolección de datos y entrenamiento, paso a paso

---

## 1. ¿Se puede lanzar antes de octubre sin afectar el diseño de tesis?

Esto es más una decisión académica que técnica. El anteproyecto
defiende un **diseño cuantitativo pre-experimental antes/después** con
ventana de estudio **oct-nov 2026**. Si el sistema empieza a usarse de
forma real antes de esa fecha, hay dos caminos:

- **(a)** Mover formalmente la ventana de estudio más temprano — está
  bien, siempre que quede documentado y sea consistente con lo que se
  defendió.
- **(b)** Hacer un "lanzamiento suave" cuyo uso no cuente para la
  medición oficial, para no contaminar la línea base "antes".

Esta decisión toca directamente la validez del diseño ya defendido, así
que **debe consultarse con el asesor de tesis**, no decidirse
unilateralmente desde el desarrollo.

---

## 2. Entrenamiento de modelos con el backend en Render

*Pregunta original: ¿cómo debería manejarse el entrenamiento de
modelos considerando que el backend corre en Render como web
service?*

El entrenamiento debe seguir siendo **100% offline/local, nunca dentro
del web service de Render**:

- Los planes de Render (sobre todo free/starter) tienen filesystem
  efímero y el servicio se duerme si está inactivo — cualquier modelo
  entrenado ahí se perdería en el siguiente deploy.
- El patrón ya implementado en el proyecto es el correcto y no debe
  cambiarse: se entrena local con `ml/training/train_progress_model.py`,
  se genera el `.joblib`, se commitea dentro de
  `backend/apps/ml_predictions/trained_models/`, y Render simplemente
  lo carga para hacer inferencia — **nunca entrena**.
- Tradeoff: cada reentrenamiento es un paso manual (correr el script,
  commitear, hacer push) en vez de un pipeline automático. Para el
  alcance de esta tesis eso es razonable — no hace falta infraestructura
  de MLOps.

**Matiz importante:** el modelo de nutrición **no es un modelo
entrenado todavía** — es la heurística determinística (Mifflin-St
Jeor) usada como placeholder mientras no existan datos reales de
dietas aprobadas/rechazadas. No hay "reentrenar" ahí por ahora; si
algún día se justifica un modelo real dependerá de cuántos datos reales
se reúnan (con ~85-186 usuarios en un par de meses podría no ser
suficiente para un modelo serio, y seguir con la heurística
indefinidamente es una opción defendible).

---

## 3. Proceso de recolección de datos y entrenamiento (para quien no lo ha hecho antes)

Explicación del flujo completo, revisada contra el código real del
proyecto (`ml/training/*.py`, `apps/tracking/views.py::StudyExportView`,
`apps/ml_predictions/`), para poder lanzar el backend ya completo y
reentrenar con datos reales más adelante.

### Los dos ingredientes de un modelo entrenado

Para entrenar un modelo supervisado (el `RandomForestRegressor` que ya
usa el proyecto) hace falta, por cada fila de datos:

- **Features** (lo que ya se sabe de un miembro en un momento dado):
  edad, IMC, nivel de actividad, meta, cuánto le falta bajar/subir, y
  qué tan constante ha sido con rutina/nutrición.
- **Label** (lo que se quiere predecir, ya observado en el pasado):
  cuántos días le tomó **realmente** llegar a su meta.

Hoy el pipeline (`ml/training/generate_synthetic_data.py` →
`train_progress_model.py`) usa datos **inventados matemáticamente** con
una fórmula plausible, porque todavía no existe ninguna fila real con
esas dos cosas — es un placeholder intencional y honesto, documentado
como tal.

### El problema real: el label tarda en existir, no importa cuándo se lance

"Días para meta" solo se puede medir de verdad cuando alguien ya llegó
(o casi llegó) a su meta. El endpoint que ya existe
(`GET /api/tracking/study-export/`) hoy exporta datos de VD1/VD2
(sesiones planificadas vs. completadas, días de dieta) — **no** exporta
el formato que necesita el entrenamiento (edad/IMC/actividad/meta/
adherencia/días-a-meta). Ese "conector" para armar el CSV de
entrenamiento real **todavía no existe**, habría que construirlo cuando
llegue el momento.

Y aunque se construyera hoy mismo, no se podría entrenar con datos
reales hasta que haya miembros que **de verdad** hayan alcanzado su
meta — eso toma semanas o meses de uso real, sin importar si el modelo
o el backend están listos antes. Por eso lanzar antes de octubre no es
solo "por las dudas": es la única forma de que ese reloj empiece a
correr antes. Cuanto antes se lance, más tiempo real de adherencia y
progreso habrá acumulado a la hora de escribir resultados.

### El proceso completo, de punta a punta

1. **Lanzar con el modelo sintético** (ya está así). No hace falta
   esperar a tener datos reales para lanzar — el backend en Render ya
   sirve el `.joblib` entrenado con datos sintéticos; es exactamente
   para eso que existe ese placeholder.
2. **Dejar que se acumule uso real.** Cada vez que el coach registra
   peso (`BodyMeasurementLog`) y los miembros registran rutinas/
   nutrición, ya se guarda la materia prima — no hace falta nada
   especial ahora, solo dejar que la app se use.
3. **Cuando llegue el momento de reentrenar** (después del período de
   estudio, o antes si se quiere una vista previa): construir un script
   que arme el CSV real, uniendo:
   - `Member` (edad, IMC vía la property `imc`, nivel de actividad, meta)
   - Historial de `BodyMeasurementLog` (para calcular cuánto le
     faltaba y, para los que sí llegaron, cuántos días les tomó)
   - Adherencia reciente de `WorkoutSessionLog`/`DailyNutritionLog`
     (misma lógica que ya usa `MyProgressPredictionView` al predecir)

   Esto probablemente signifique **filtrar solo a los miembros que
   efectivamente alcanzaron su meta** (o se acercaron mucho) — con
   ~85-186 usuarios en 2 meses, es realista terminar con un dataset
   chico (puede que unas decenas de filas, no cientos). Eso es normal y
   está bien para el alcance de una tesis; solo hay que ser honesto en
   el capítulo de resultados sobre el tamaño de muestra y su efecto en
   MAE/R².
4. **Correr `train_progress_model.py` local** con ese CSV real en vez
   del sintético (mismo comando, solo cambia `--input`).
5. **Commitear el nuevo `.joblib`** en
   `backend/apps/ml_predictions/trained_models/` y hacer push.
6. **Render redeploya solo** (deploy basado en git push) — el modelo
   nuevo entra en producción sin que el servicio haya tenido que
   entrenar nada.

### Sobre nutrición

No hay "entrenar" que hacer ahí todavía porque no hay un target claro
que observar desde el uso de la app (a diferencia de "días a meta", no
existe un "macro correcto" objetivamente medible solo con datos de
uso) — seguirá siendo la heurística, y eso también es una decisión
perfectamente defendible para esta tesis.
