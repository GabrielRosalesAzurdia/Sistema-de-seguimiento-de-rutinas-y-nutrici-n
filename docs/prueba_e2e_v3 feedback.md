
NOTAS:
- Actualizar requirements.txt
- Crear una página en diseño para un 404 not found, como una ruta inexistente. Una página simple como la del error 500 indicando que la pagina no existe. Y un botón para ir al panel.
- Agregar botón de generación de nueva contraseña en el panel del coach, en las opciones de edición del usuario, que genere una nueva contraseña por si el usuario olvida la suya, siguiendo el mismo patrón de contraseña temporal que luego el usuario tendrá que reemplazar.
- Cuando un usuario se queda con una seción abierta en la app y este usuario se desactiva la app pasa a un infinite loading y hace miles de peticiones al servidor “[17/Jul/2026 21:07:51] "GET /api/members/me/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- Unauthorized: /api/nutrition/me/current-plan/
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- Unauthorized: /api/tracking/me/summary/
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- Unauthorized: /api/ml/me/progress/
- [17/Jul/2026 21:07:51] "GET /api/tracking/me/summary/ HTTP/1.1" 401 61
- Unauthorized: /api/members/me/
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- Unauthorized: /api/tracking/me/summary/
- [17/Jul/2026 21:07:51] "GET /api/ml/me/progress/ HTTP/1.1" 401 61
- Unauthorized: /api/routines/me/today/
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "GET /api/tracking/me/weight-history/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "GET /api/routines/me/today/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "GET /api/routines/me/today/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "GET /api/routines/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "GET /api/ml/me/progress/ HTTP/1.1" 401 61
- Unauthorized: /api/members/me/
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "GET /api/tracking/me/summary/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "GET /api/ml/me/progress/ HTTP/1.1" 401 61
- Unauthorized: /api/nutrition/me/current-plan/
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- Unauthorized: /api/members/me/
- Unauthorized: /api/tracking/me/weight-history/
- [17/Jul/2026 21:07:51] "GET /api/nutrition/me/current-plan/ HTTP/1.1" 401 61
- Unauthorized: /api/tracking/me/weight-history/
- [17/Jul/2026 21:07:51] "GET /api/members/me/ HTTP/1.1" 401 61
- Unauthorized: /api/tracking/me/summary/
- [17/Jul/2026 21:07:51] "GET /api/tracking/me/summary/ HTTP/1.1" 401 61
- Unauthorized: /api/ml/me/progress/
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "GET /api/routines/me/today/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- Unauthorized: /api/routines/me/today/
- [17/Jul/2026 21:07:51] "GET /api/members/me/ HTTP/1.1" 401 61
- Unauthorized: /api/nutrition/me/current-plan/
- Unauthorized: /api/ml/me/progress/
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- Unauthorized: /api/routines/
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "GET /api/members/me/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "GET /api/nutrition/me/current-plan/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "GET /api/tracking/me/weight-history/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "GET /api/tracking/me/summary/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51] "GET /api/ml/me/progress/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "GET /api/tracking/me/weight-history/ HTTP/1.1" 401 61
- [17/Jul/2026 21:07:51] "POST /api/auth/refresh/ HTTP/1.1" 200 245
- [17/Jul/2026 21:07:51,897] - Broken pipe from ('127.0.0.1', 60555)
- [17/Jul/2026 21:07:51,889] - Broken pipe from ('127.0.0.1', 60556)
- [17/Jul/2026 21:07:51,890] - Broken pipe from ('127.0.0.1', 52066)
- [17/Jul/2026 21:07:51,892] - Broken pipe from ('127.0.0.1', 60557)
- [17/Jul/2026 21:07:51,894] - Broken pipe from ('127.0.0.1', 60559)
- [17/Jul/2026 21:07:51,894] - Broken pipe from ('127.0.0.1', 54817)
- [17/Jul/2026 21:07:51,894] - Broken pipe from ('127.0.0.1', 54450)
- [17/Jul/2026 21:07:51,897] - Broken pipe from ('127.0.0.1', 60552)
- [17/Jul/2026 21:07:51,880] - Broken pipe from ('127.0.0.1', 52067)
- [17/Jul/2026 21:07:51,898] - Broken pipe from ('127.0.0.1', 54726)
- [17/Jul/2026 21:07:51,898] - Broken pipe from ('127.0.0.1', 54721)
- Unauthorized: /api/routines/me/today/
- Unauthorized: /api/members/me/
- [17/Jul/2026 21:07:51,903] - Broken pipe from ('127.0.0.1', 52064)
- [17/Jul/2026 21:07:51,903] - Broken pipe from ('127.0.0.1', 54722)”
- Para los datos del estudio si el usuario esta desactivado dejar de contarlo para los porcentajes de VD1 y de VD2.
- Se ingresaron 3 pesos en un mes a un usuario y la gráfica se deformo de esta forma, “ ver docs/grafica.png” explicar por que sucede esto y si puede corregirse. Las leyendas de la grafica si estan bien tanto eje X y Y.
- Cuando modifique el review_at del plan nutricional activo que era 17/07/2026 al 16/06/2026 y guardé actualicé el panel de administración en la pestaña de nutrición y si sale la nueva dieta en la sección de por revisar, cuando apruebo esta dieta pasa algo malo y es que se acumulan ambas dietas, la actual y la recíen aceptada, entré al detalle de ambas dietas y ambas aparecen como activas y en seguimiento, probé precionar el botón de rechazar a la dieta vieja y lo que hizo fue inmediatamente generar una nueva sugerencai de dieta en la bandeja de dietas por revisar. Si esta nueva dieta la acepto otra vez tengo 2 dietas activas y en seguimiento de un mismo usuario.

Usuarios:
safi@fitnessclub.com
TeAmo1234

pgabriel@elpatojismo.edu.gt
Prueba12345
