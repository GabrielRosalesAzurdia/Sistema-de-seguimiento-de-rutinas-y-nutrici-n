# Mockups — Club Fitness App

Capturas reales del diseño validado con el gimnasio (reunión 2,
15/abr/2026: "Todo está bien" sobre estilo visual y flujo de
navegación). Úsalas como referencia visual exacta para implementar o
ajustar las pantallas — colores, jerarquía, textos y disposición ya
están aprobados, no son solo bocetos.

## `app/` — App móvil (Flutter)

| Archivo | Pantalla | Implementada en |
|---|---|---|
| `01_splash.jpeg` | Splash/logo inicial | — (falta implementar) |
| `02_login.jpeg` | Login | `mobile/lib/screens/login_screen.dart` |
| `03_dashboard.jpeg` | Inicio / Dashboard | `mobile/lib/screens/dashboard_screen.dart` |
| `04_rutinas_listado.jpeg` | Rutinas (listado) | `mobile/lib/screens/routines_screen.dart` |
| `05_rutina_detalle.jpeg` | Detalle de rutina | `mobile/lib/screens/routine_detail_screen.dart` |
| `06_registrar_rutina.jpeg` | Registrar rutina completada | `mobile/lib/screens/log_routine_screen.dart` |
| `07_nutricion.jpeg` | Nutrición (plan diario) | `mobile/lib/screens/nutrition_screen.dart` |
| `08_perfil.jpeg` | Perfil | `mobile/lib/screens/profile_screen.dart` |
| `09_editar_perfil.jpeg` | Editar perfil | `mobile/lib/screens/edit_profile_screen.dart` |

## `admin_panel/` — Panel web (Django)

Ninguna de estas pantallas está implementada todavía en el scaffold
(solo existe el Django admin genérico + el API REST). Son la
referencia visual pendiente de construir:

| Archivo | Pantalla |
|---|---|
| `01_dashboard.jpeg` | Dashboard (miembros activos, pagos pendientes, % constancia nutricional, actividad reciente) |
| `02_miembros_listado.jpeg` | Miembros (listado + búsqueda) |
| `03_miembro_editar.jpeg` | Editar miembro (datos personales + físicos) |
| `04_miembro_agregar.jpeg` | Agregar miembro |
| `05_rutinas_listado.jpeg` | Rutinas semanales (7 categorías) |
| `06_rutinas_editar_ejercicios.jpeg` | Editar ejercicios de una rutina (selección desde catálogo) |
| `07_nutricion_revision.jpeg` | Dietas por revisar / aprobadas y en seguimiento |
| `08_datos_estudio_export.jpeg` | Exportador de datos del estudio (VD1/VD2, CSV) |

Nota: en `07_nutricion_revision.jpeg` y `08_datos_estudio_export.jpeg`
el texto de la barra superior no lista "Rutinas" por recorte de la
captura — la navegación completa es: **Dashboard · Miembros · Rutinas
· Nutrición · Datos del estudio**.
