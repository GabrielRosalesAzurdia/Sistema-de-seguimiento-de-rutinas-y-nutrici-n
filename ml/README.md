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

✅ **Pipeline conectado end-to-end con datos sintéticos** (placeholder,
no el modelo final de la tesis). Se generó `data/synthetic_training_data.csv`
con `generate_synthetic_data.py` y se entrenó
`backend/apps/ml_predictions/trained_models/random_forest_progress_v1.joblib`
con `train_progress_model.py` — `services.py` ya lo carga y
`GET /api/ml/me/progress/` devuelve `model_type: "RANDOM_FOREST"` en
vez de `"HEURISTIC_PLACEHOLDER"`.

⚠️ **Sigue sin haber datos históricos reales.** El período de
implementación es octubre-noviembre 2026; hasta entonces este modelo
entrenado con datos sintéticos es solo una prueba de que el pipeline
funciona, no una predicción confiable para producción.

**Reentrenamiento con datos reales** una vez arranque la
implementación: exportar desde `GET /api/tracking/study-export/`,
correr `train_progress_model.py` sobre ese CSV real, y reemplazar el
`.joblib` en `trained_models/` (mismo nombre de archivo, el backend no
requiere cambios de código).

## Cómo entrenar (una vez haya datos)

```bash
cd ml
pip install -r requirements.txt
python training/train_progress_model.py --input data/study_export.csv --output ../backend/apps/ml_predictions/trained_models/random_forest_progress_v1.joblib
```
