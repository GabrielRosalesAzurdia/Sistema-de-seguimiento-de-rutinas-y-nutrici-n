"""
Genera un dataset sintético plausible para poder desarrollar y probar
el pipeline de entrenamiento ANTES de contar con datos reales del
período de implementación (oct-nov 2026).

IMPORTANTE: esto es solo para desarrollo. El modelo final para el
trabajo de graduación debe entrenarse con datos reales exportados vía
GET /api/tracking/study-export/ una vez concluida la implementación.

Uso:
    python generate_synthetic_data.py --n 300 --output ../data/synthetic_training_data.csv
"""
import argparse
import numpy as np
import pandas as pd

ACTIVITY_LEVELS = ["SEDENTARIO", "MODERADO", "ACTIVO", "MUY_ACTIVO"]
FITNESS_GOALS = ["GANAR_PESO", "PERDER_PESO", "MANTENER_PESO"]


def generate(n: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    age = rng.integers(18, 55, size=n)
    imc = rng.normal(26, 4, size=n).clip(16, 40)
    activity_level = rng.choice(ACTIVITY_LEVELS, size=n)
    fitness_goal = rng.choice(FITNESS_GOALS, size=n)
    weight_diff_kg = rng.normal(8, 4, size=n).clip(0.5, 30)
    training_adherence = rng.beta(2, 1.5, size=n)  # sesgado hacia constancia media-alta
    nutrition_adherence = rng.beta(2, 1.5, size=n)

    activity_factor = pd.Series(activity_level).map(
        {"SEDENTARIO": 1.2, "MODERADO": 1.0, "ACTIVO": 0.85, "MUY_ACTIVO": 0.7}
    ).to_numpy()

    adherence_factor = (training_adherence + nutrition_adherence) / 2
    adherence_factor = np.clip(adherence_factor, 0.2, 1.0)

    base_days_per_kg = 14  # ~0.5kg/semana como referencia conservadora
    noise = rng.normal(0, 5, size=n)
    days_to_goal = (
        (weight_diff_kg * base_days_per_kg * activity_factor) / adherence_factor
    ) + noise
    days_to_goal = days_to_goal.clip(min=7)

    return pd.DataFrame({
        "age": age,
        "imc": imc,
        "activity_level": activity_level,
        "fitness_goal": fitness_goal,
        "weight_diff_kg": weight_diff_kg,
        "training_adherence": training_adherence,
        "nutrition_adherence": nutrition_adherence,
        "days_to_goal": days_to_goal.round().astype(int),
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=300)
    parser.add_argument("--output", type=str, default="../data/synthetic_training_data.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    df = generate(args.n, args.seed)
    df.to_csv(args.output, index=False)
    print(f"Dataset sintético generado: {args.output} ({len(df)} filas)")
