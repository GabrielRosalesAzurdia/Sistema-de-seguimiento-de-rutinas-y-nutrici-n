"""
Entrena y compara LinearRegression vs RandomForestRegressor para
predecir 'días para alcanzar la meta' (indicador del dashboard),
según lo descrito en el Marco Metodológico del anteproyecto.

Evaluación: MAE y R², con validación cruzada (KFold), tal como se
documenta en el capítulo de Herramientas de Desarrollo (Scikit-learn).

Uso:
    python train_progress_model.py \
        --input ../data/synthetic_training_data.csv \
        --output ../../backend/apps/ml_predictions/trained_models/random_forest_progress_v1.joblib
"""
import argparse
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_absolute_error, r2_score

ACTIVITY_MAP = {"SEDENTARIO": 0, "MODERADO": 1, "ACTIVO": 2, "MUY_ACTIVO": 3}
GOAL_MAP = {"GANAR_PESO": 0, "PERDER_PESO": 1, "MANTENER_PESO": 2, "TONIFICAR": 1}


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Debe mantenerse en sincronía con
    backend/apps/ml_predictions/services.py -> _vectorize()."""
    features = pd.DataFrame({
        "age": df["age"],
        "imc": df["imc"],
        "activity_level": df["activity_level"].map(ACTIVITY_MAP),
        "fitness_goal": df["fitness_goal"].map(GOAL_MAP),
        "weight_diff_kg": df["weight_diff_kg"],
        "training_adherence": df["training_adherence"],
        "nutrition_adherence": df["nutrition_adherence"],
    })
    return features


def evaluate(model, X, y, name: str):
    kfold = KFold(n_splits=5, shuffle=True, random_state=42)
    mae_scores = -cross_val_score(model, X, y, cv=kfold, scoring="neg_mean_absolute_error")
    r2_scores = cross_val_score(model, X, y, cv=kfold, scoring="r2")
    print(f"[{name}] MAE promedio (5-fold): {mae_scores.mean():.2f} (+/- {mae_scores.std():.2f})")
    print(f"[{name}] R^2 promedio (5-fold): {r2_scores.mean():.3f} (+/- {r2_scores.std():.3f})")
    return mae_scores.mean(), r2_scores.mean()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    X = build_features(df)
    y = df["days_to_goal"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    linear_model = LinearRegression()
    rf_model = RandomForestRegressor(n_estimators=200, random_state=42)

    print("=== Validación cruzada ===")
    evaluate(linear_model, X, y, "LinearRegression")
    evaluate(rf_model, X, y, "RandomForestRegressor")

    print("\n=== Evaluación en conjunto de prueba (hold-out 20%) ===")
    for name, model in [("LinearRegression", linear_model), ("RandomForestRegressor", rf_model)]:
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        print(f"[{name}] MAE={mae:.2f}  R^2={r2:.3f}")

    # Se guarda el Random Forest entrenado con TODOS los datos disponibles
    # (decisión de diseño: mejor generalización que la regresión lineal
    # simple para relaciones no lineales entre adherencia y progreso).
    rf_model.fit(X, y)
    joblib.dump(rf_model, args.output)
    print(f"\nModelo guardado en: {args.output}")


if __name__ == "__main__":
    main()
