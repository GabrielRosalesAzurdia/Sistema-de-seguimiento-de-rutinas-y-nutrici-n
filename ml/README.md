# Módulo de Inteligencia Artificial — Club Fitness App

Scripts de entrenamiento y experimentación para los modelos de
predicción de progreso descritos en el Marco Metodológico del
anteproyecto (LinearRegression y RandomForestRegressor de
scikit-learn, biblioteca Pedregosa et al., 2011).

Este módulo vive **fuera** del backend Django a propósito: el
entrenamiento es un proceso offline/experimental (notebooks, prueba
de hiperparámetros, validación cruzada) que no debe acoplarse al
ciclo de despliegue del servidor. El artefacto final entrenado
(`.joblib`) se copia a
`backend/apps/ml_predictions/trained_models/` para que el backend lo
cargue en inferencia (ver `apps/ml_predictions/services.py`).

## Qué predice el modelo

Input (features por usuario, ver `services._vectorize`):
- Edad
- IMC (peso actual / altura²)
- Nivel de actividad (codificado)
- Meta fitness (codificada; "Tonificar" se trata como "Perder peso")
- Diferencia entre peso actual y peso meta (kg)
- % de constancia reciente al entrenamiento (VD1, ventana de 30 días)
- % de constancia reciente al plan nutricional (VD2, ventana de 30 días)

Output: días estimados para alcanzar la meta de peso.

## Evaluación

Según el anteproyecto, las métricas de evaluación son:
- **MAE** (Error Absoluto Medio)
- **R²** (Coeficiente de determinación)

usando validación cruzada de scikit-learn (`cross_val_score` /
`KFold`) para obtener una estimación más realista del desempeño.

## Estado actual

⚠️ **No hay datos históricos todavía.** El período de implementación
es octubre-noviembre 2026; hasta entonces no existen registros reales
de `WorkoutSessionLog` / `DailyNutritionLog` / `BodyMeasurementLog`
suficientes para entrenar un modelo con datos propios del gimnasio.

Dos caminos posibles, a decidir con el asesor:

1. **Dataset sintético inicial** (`training/generate_synthetic_data.py`):
   genera datos plausibles para poder programar y probar el pipeline
   completo end-to-end antes de tener datos reales.
2. **Reentrenamiento con datos reales** una vez arranque la
   implementación: exportar desde
   `GET /api/tracking/study-export/` y usarlo como dataset de
   entrenamiento real.

Mientras tanto, `backend/apps/ml_predictions/services.py` usa una
heurística determinística como placeholder para no bloquear el resto
del desarrollo (dashboard, endpoints, app), y cae automáticamente al
modelo real en cuanto exista un `.joblib` en `trained_models/`.

## Cómo entrenar (una vez haya datos)

```bash
cd ml
pip install -r requirements.txt
python training/train_progress_model.py --input data/study_export.csv --output ../backend/apps/ml_predictions/trained_models/random_forest_progress_v1.joblib
```
