# Datos semilla — pendientes de llenar / decidir manualmente

Este documento acompaña a `backend/fixtures/seed_data.json` (cargado con
`python manage.py loaddata fixtures/seed_data.json`). Ese fixture siembra
lo mínimo necesario para probar la app de punta a punta: catálogo de
ejercicios en las 7 categorías, las 7 rutinas con sus ejercicios en
orden, un miembro de prueba con su usuario de login, y un plan
nutricional ya aprobado con sus 5 tiempos de comida.

Lo que sigue es lo que el fixture **no puede** resolver por sí solo,
porque depende de datos reales del gimnasio o de decisiones de negocio
todavía abiertas.

## Lo que tienes que llenar / decidir manualmente

1. **Catálogo real de ejercicios.** Del mockup solo se confirmaron 2
   categorías: `Brazos y Espalda` (Polea abierta, Peso muerto,
   Predicador, Copa, Remo) y `Pierna-Cuádriceps` (Sentadilla Sumo,
   Extensiones, Prensa, Zancadas, Sentadilla Hack, Peso Muerto Rumano,
   Levantamiento de Caderas, Sentadilla Búlgara). Las otras 5
   categorías (Pecho, Cardio, ABS, Pierna-Glúteos, Hombro) se
   sembraron con nombres genéricos y **están marcados explícitamente
   con "(placeholder)" en el nombre** para que no se confundan con
   datos reales — reemplázalos cuando el coach entregue la lista
   completa con nombres exactos e íconos/fotos de referencia (ver
   `docs/requerimientos_resumen.md`).
2. **Íconos y fotos de referencia de cada ejercicio** (`icon`,
   `reference_photo` en `Exercise`). Son campos `ImageField`: no se
   pueden sembrar por JSON, quedaron vacíos. Se suben después desde el
   panel/admin, una sola vez por ejercicio (para no repetir subida
   semanal, según pidió el coach).
3. **Miembros reales del gimnasio** (~85-186 según el levantamiento).
   El fixture trae solo 1 miembro ficticio de prueba (Ana Martínez,
   `miembro.prueba@fitnessclub.test`). La carga de miembros reales
   queda pendiente — a mano desde el panel admin, o con un import
   masivo aparte si el coach entrega un Excel/CSV con los datos
   personales y físicos.
4. **Fechas y estado de pago reales** (`next_payment_date`, `is_paid`,
   `start_date` de cada miembro real). En el fixture están inventados
   solo para poder probar el flujo.
5. **Contraseña del usuario de prueba.** Es fija (`Prueba1234`,
   hasheada con `make_password` de Django). No reutilizar ese hash ni
   esa contraseña para cuentas reales en producción — generar una
   distinta y segura por cada miembro real.
6. **% grasa corporal y % agua corporal.** El fixture puso valores de
   ejemplo (28.5% y 52.0%) a mano. Sigue pendiente la fórmula real de
   cálculo a partir de las medidas (Navy Method u otra), ver
   `docs/backend_arquitectura.md` sección 6 y `CLAUDE.md` sección 8,
   punto 7 — hoy son campos que cualquiera llena manualmente sin
   cálculo automático.
7. **Macros de las 5 sugerencias de comida** (`MealSuggestion`) del
   plan de prueba son valores inventados para que sumen razonablemente
   cerca del total del plan (1800 kcal / 135g proteína / 180g carbos /
   55g grasa). No son una guía nutricional real — el coach/nutricionista
   debe definir las sugerencias y macros reales por plan.
8. **Sesiones planificadas (VD1)** y el resto de los TODOs de negocio
   ya documentados en `CLAUDE.md` (sección 1 y 8) y
   `docs/backend_arquitectura.md` (sección 6) no se tocan con este
   seed — son decisiones a cerrar con el asesor, no datos de prueba.

## Nota de diseño encontrada al armar el seed

`Exercise.name` es **único a nivel global** en el modelo actual
(`unique=True`), no único por categoría. En el mockup del gimnasio,
"Peso Muerto" aparece tanto en la rutina "Brazos y Espalda" como en
"Pierna-Cuádriceps" — con el esquema actual eso no se puede repetir
tal cual: en el seed hubo que renombrar la segunda aparición a "Peso
Muerto Rumano" para evitar el choque de unicidad.

Si en la operación real el mismo ejercicio se reutiliza en más de una
rutina/categoría, vale la pena decidir con el asesor si:

- (a) el modelo debería cambiar a `unique_together = ["name", "category"]`
  (o quitar la unicidad de `name` y usar solo `id` como identificador
  único), permitiendo que el mismo nombre exista en más de una
  categoría, o
- (b) se mantiene la regla de "un nombre, una categoría" y cada
  aparición del mismo ejercicio en otra rutina se registra con un
  nombre ligeramente distinto (como se hizo aquí de forma temporal).

Esto no bloquea las pruebas actuales, pero conviene resolverlo antes
de cargar el catálogo real completo, para no tener que renombrar
ejercicios reales más adelante.
