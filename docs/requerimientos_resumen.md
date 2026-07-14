# Resumen de requerimientos — Club Fitness App

Extraído de: Acta 1 (27/mar/2026), Cuestionario de requerimientos
(27/mar/2026) y Cuestionario 2 — presentación de diseño (15/abr/2026).
Documentos completos en el proyecto de Claude (`Acta_1_transcrita.docx`,
`Cuestionario_requerimientos_trancrito.docx`,
`Cuestionario_Requerimientos_2_transcrito.docx`).

## Contexto del gimnasio

- ~85-186 usuarios activos (el número varía entre documentos según la
  fecha del levantamiento; usar el dato más reciente del panel admin
  una vez en producción).
- Rango de edad más común: 20-30 años.
- Objetivos: ganar, perder y mantener peso.
- **Sin wifi** en el gimnasio (relevante para UX: la app debe tolerar
  conexión intermitente / datos móviles del usuario).
- Mayoría de usuarios con **Android**.
- Báscula disponible en el gimnasio.
- Rutinas: fuerza, cardio, hipertrofia, funcional, abs — organizadas
  por objetivo, diseñadas por el dueño, actualizadas cada semana.

## Ejercicios de ejemplo (nomenclatura propia del gym)

Extraídos del mockup para la rutina "Brazo y Espalda":
- Polea abierta
- Peso muerto
- Predicador
- Copa
- Remo

Y para "Pierna - Cuádriceps":
- Sentadilla Sumo
- Extensiones
- Prensa
- Zancadas
- Sentadilla Hack
- Peso Muerto
- Levantamiento Caderas
- Sentadilla Búlgara

⚠️ Esta lista es parcial (tomada del mockup, no es el catálogo
completo). Falta que el coach entregue el listado completo de
ejercicios por rutina con nombres exactos y fotos/íconos de referencia
(pendiente mencionado en Cuestionario 2, E2).

## Colores de marca

- Fondo: negro
- Amarillo: `#FFD600`
- Verde y naranja "chintón" (vivo/saturado) — tono exacto no
  especificado en hex por el gimnasio, usar `AppColors.green` /
  `AppColors.orange` en `mobile/lib/core/theme.dart` como referencia
  y ajustar si el coach da una muestra de color específica.

## Datos de un miembro (panel admin)

Personales: primer/segundo nombre, primer/segundo apellido, correo,
teléfono, edad.

Físicos (solo coach, mensual): peso (kg), % grasa corporal (calculado
por el sistema), % agua corporal (calculado por el sistema), brazo
izq/der, pierna izq/der, pantorrilla izq/der, cadera, espalda, pecho,
cintura.

Membresía: meta fitness, fecha de inicio, siguiente pago, pagado
(sí/no), activo/desactivado.

## Fórmulas pendientes de definir

- **% grasa corporal** y **% agua corporal**: el gimnasio pidió que el
  sistema los calcule a partir de las medidas registradas por el
  coach, pero no se definió la fórmula exacta durante el levantamiento.
  Investigar métodos estándar (p. ej. U.S. Navy Method para % grasa
  usando cintura/cuello/altura, o fórmulas de bioimpedancia si el
  gimnasio tiene báscula compatible) y documentar la elección en el
  capítulo de Análisis y Diseño.
- **Sesiones planificadas** (denominador de VD1): debe definirse con
  el asesor. Opciones: (a) fijo por semana según categoría de rutina
  asignada, (b) configurable por el coach por usuario, (c) derivado
  del calendario de rutinas semanales. Placeholder actual en el código:
  usa el número de sesiones completadas como referencia (VD1 = 100%),
  lo cual NO es la implementación final.

## Fuera de alcance v1 (confirmado)

- Notificaciones push / recordatorios.
- Selección de plan de comida por el usuario (solo semáforo diario
  simplificado).
- Alimentos típicos guatemaltecos / recetas específicas (solo macros).
- Comparaciones entre usuarios o visibilidad de datos de otros
  miembros.
- Versión iOS (tentativa, sujeta a tiempo/recursos).
- Multi-idioma (solo español).
