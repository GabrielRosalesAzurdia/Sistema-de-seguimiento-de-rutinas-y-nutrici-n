# NOTAS RESULTADO:


- Gráfica de nutrición aún no implementada, esto fue porque al exportar el mockup de figma este chart no se incluyo por un error, en esta carpeta se encuentra la pantalla bajo el nombre de "nutricion chart mockup.png"
- Contraseña generada por el sistema si sale en el panel de miembros al crear un miembro pero hacerla mas visible, talvez un pop up o un alerta para llamar la atención del administrador del sistema.
- El botón desactivar usuario no debería pedir que se llenen los datos del formulario de actualizar ( saltó que debía llenar fecha de inicio cuando eso debe de estar ya lleno de igual manera ).
- Al desactivar el usuario su posición en la tabla debe colocarse de color “dim” o grisaseo para visualizar que este usuario fue desactivado, sumado a eso cuando un usuario este desactivado ya no muestra la opcion de datos fitness, en vez de eso muestra la opción de reactivar usuario.
- Al momento de ingresar a la pantalla de PERFIL en la app, entrar a Editar y regresar a PERFIL por medio de la flechita de la parte superior de la app surge este mensaje “http://127.0.0.1:50724/n6_NIHyjz_c=/devtools/?uri=ws://127.0.0.1:50724/n6_NIHyjz_c=/ws
- [ERROR:flutter/runtime/dart_vm_initializer.cc(40)] Unhandled Exception: setState() callback argument returned a Future.
- The setState() method on _ProfileScreenState#518c1 was called with a closure or method that returned a Future. Maybe it is marked as "async".
- Instead of performing asynchronous work inside a call to setState(), first execute the work (without updating the widget state), and then synchronously update the state inside a call to setState().
- #0      State.setState.<anonymous closure> (package:flutter/src/widgets/framework.dart:1202:9)
- #1      State.setState (package:flutter/src/widgets/framework.dart:1218:6)
- #2      _ProfileScreenState.build.<anonymous closure>.<anonymous closure> (package:club_fitness_app/screens/profile_screen.dart:65:29)
- <asynchronous suspension>” 
- La contraseña generada por el sistema funciona al iniciar sesión en la app, pero, esta contraseña es demasiado difícil de recordar, permitir al usuario cambiar su contraseña al usar la generada por el sistema, o mejor aún exigir al usuario crear una contraseña propia.
- Al intentar crear un usuario con el mismo correo muestra “IntegrityError at /panel/miembros/agregar/
* duplicate key value violates unique constraint "members_user_username_key"
* DETAIL:  Key (username)=(pgabriel@elpatojismo.edu.gt) already exists.
Request Method:    POST
Request URL:    http://127.0.0.1:8000/panel/miembros/agregar/
Django Version:    5.0.6
Exception Type:    IntegrityError
Exception Value:    duplicate key value violates unique constraint "members_user_username_key"
DETAIL:  Key (username)=(pgabriel@elpatojismo.edu.gt) already exists.
Exception Location:    /Users/gabrielrosales/Documents/mariano galvez/semestre X/club_fitness_app/backend/venv/lib/python3.12/site-packages/django/db/backends/utils.py, line 105, in _execute
Raised during:    apps.panel.views.MemberCreateView
Python Executable:    /Users/gabrielrosales/Documents/mariano galvez/semestre X/club_fitness_app/backend/venv/bin/python
Python Version:    3.12.13
Python Path:    ['/Users/gabrielrosales/Documents/mariano galvez/semestre '
 'X/club_fitness_app/backend',
 '/opt/homebrew/anaconda3/lib/python312.zip',
 '/opt/homebrew/anaconda3/lib/python3.12',
 '/opt/homebrew/anaconda3/lib/python3.12/lib-dynload',
 '/Users/gabrielrosales/Documents/mariano galvez/semestre '
 'X/club_fitness_app/backend/venv/lib/python3.12/site-packages']
Server time:    Thu, 16 Jul 2026 19:50:02 -0600
" que esta bien porque es un error pero no quiero esta pantalla de error gigante quiero una manera simple y bonita de mostrar el error.
- El sistema al precionar editar usuario sigue pidiendo llenar siempre la fecha de inicio. La fecha de inicio es la fecha en que el miembro se unió al gym, no debe de estarse cambiando cada vez que edito info del miembro, y para calcular la fecha del proximo pago tomar la última vez que se marcó como pagado y calcular un mes desde ese día. Es decir, cuando se crea el miembro calcular un mes desde fecha de inicio, para proximos meses calcularlo tomando la fecha de último pago. Si esto no se puede hacer con la data actual ampliar la ifnormación que se guarda. 
- Si el miembro solo se unió pero no ha pagado o no ha sido marcado como pagado mostrar PENDIENTE DE PAGO como proxima fecha. Esto es igual si llega una fecha de proximo pago para cualquier usuario sin importar su antiguedad.
-  Ingresé 2 actualizaciones de peso al usuario nuevo y la gráfica es mucho mas legible, es bueno, pero ambos cambios de peso sucedieron en julio 2026, pero la grafica lo toma de julio a julio, no esta considerando que hubo 2 pesajes el mismo mes y esto es un error, no debe hacer estos saltos de mes a mes si este caso llega a suceder, todo lo demás de la grafica esta genial como que cuando no hay actualización de datos aún peus no se muestra.
- Sobre nutrición, cuando el usuario es creado debería de al mismo tiempo con su data generarse una dieta sugerida por el ML, y una nueva dieta debe de surgir cuando el coach la solicite por medio de un botón por cada miembro o cuando se cumpla el plazo de una dieta ( este plazo nunca se establecio o no se ha contemplado por lo que no se si hacerlo semanal o mensual )
- Si el coach rechaza una dieta entonces se debe generar otra, si el coach actualiza la dieta con nuevos macros o su distribución esto es feedback para el ML al igual que si la dieta entera es rechazada. 
- El ML me da los macros y los macros separados por tiempos de comida, pero las sugerencias de comida las llena al 100%el coach esas no se generan por ML. 
- Cree una dieta en el ADMIN de django y me aparece en nutrición, todo bien, al momento de revisarla me aparecen todos los datos correctos pero al aprobarla me sale “     •    meal_time
    * Este campo es requerido.”, lleno una sugerencia en cada tiempo de comida y el mismo mensaje sale, lleno todas las sugerencias de tiempo de comida y el mismo mensaje sale, no me deja aprobar la dieta, voy a la dieta del fixture, la intento aprobar otra vez y me sale el mismo error. Que por cierto si una dieta ya esta aprobada no debe salir este botón de nuevo, pero si el de rechazarla por si se aprobo por error. 
- Al momento de crear un miembro los dias de dieta y de ejercicio se calculan de manera mensual segun entiendo, hacer esta aclaracion para que no piensen que se limita solo a la semana.
- Como puntos futuros hay que seguir haciendo pruebas de E2E para seguir encontrando detalles y luego trabajar en los modelos de ML para entrenarlos para PREDICCIÓN DE META y para GENERACIÓN DE DIETAS.


 Termine de hacer la prueba docs/prueba_e2e_v2.md y puse mis comentarios en docs/prueba_e2e_v2 feedback.md
  leelo y planifica una ruta de cambios, fixes, etc para cumplir con esta nueva lista de requerimientos.
  Hazme preguntas sobre cosas que no exprese bien o datos faltantes para poder hacer el mejor trabajo posible e implementar estos cambios tanto a backend como a frontend según sea necesario. También dejame saber comentarios y recomendaciones 
