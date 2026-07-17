NOTAS ENCONTRADAS
- El logout no funciona en el panel de admin
- Hacer el formulario de inicio de seción de admin mas parecido al de la app, se mira mal
- A la gráfica de peso agregarle leyendas  en ejes X y Y. siendo el eje X pesos y el eje Y meses. Esto para que sea mas comprensible ya que puede ser complicarla leerla sin estas leyendas. Al leerla por primera vez me hizo pensar que era una diagonal y que un extremo era mi peso actual y el otro la meta.
- En el panel del coach al editar un miembro algunso nombres de partes del cuerpo están en inglés, esto debe de cambiarse a español.
- La casilla de siguiente pago automaticamente debe llenarse con un mes calculado desde la fecha de pago inicial con la que se creo el usuario.
- Cada vez que se quiere editar el usuario pide llenar nuevamente la fecha de inicio, este dato debe de estar ya lleno en el formulario de edición.
- El botón de “iniciar” en “routine_detail_screen” debe de ser estilo block no orillado a la izquierda y pequeño. Debe cubrir todo el espacio de manera horizontal pero sin tocar los bordes de la pantalla siempre con un margen para mantener la buena visual. Lo mismo con el botón de registrar rutina.
- Botón de “registrar” Rutina deja registrar la rutina aún cuando todos los campos fueron dejados vacíos, esto es un error, solo debe registrarla si todos los campos están llenos.
- Agregar botón de cancelar edición en editar información de miembro.
- Cuando se edita el peso del miembro no se crea una nueva entrada en “Registros de medidas corporales”.
- En el panel de administración en la pestaña de miembros he tomado una decisión y es agregar 2 tipos distintos de edición, edición de datos personales como nombre, apellido, etc… y otro tipo llamado actualización de datos fitness donde se registra un nuevo peso corpora, medidas corporales, etc… separando los datos del usuario de sus datos fisicos y esto ya crea un nuevo registro en los registros de medias corporales.
- Cuando agrego un nuevo miembro no me crea un nuevo usuario, esto creo que tiene problemas para la autenticación mas tarde, ya que el miembro no tiene un usuario asociado, creo que es porque intente hacer la prueba colocando el mismo correo que el usuario ya existente miembro.prueba@fitnessclub.test, no hice la prueba con el correo de ana.martinez@fitnessclub.test ya que se supone que un usuario/miembro solo tiene un correo asociado no veo porque el usuario y miembro son 2 correos distintos.  Que por cierto cuando se agrega un miembro no le pide contraseña y esto es un error también ya que entonces como puede el miembro ingresar a la app ?
- Los dias de nutricion muestran 1/0 cuando en el perfil de ana martinez precione “HECHO” por hoy, ese 0 no se donde se edita o donde le asigno cuantos dias debe de seguir la dieta. Si esto es a lo que se refiere con como se mide la variable esta dieta o dias planificados tanto para rutinas y dieta deberia ser un dato del usuarioq/miembro que el coach  ingresa cuando registra al miembro ya que le pregunta cuantos dias desea hacer dieta o cuantos dias desea hacer rutina y en en base a ese numero que calcula su constancia y sus proyecciónes. Si rebasa los dias que supuestamente esta activo mas que genial pero esa seria como la meta individual de cada usuario.
- Cuando revise el apartado de Planes Nutricionales de Ana Martinez en el atributo Ml prediction: surgen muchos RANDOMFOREST no se en que momento se genero esto y si esto es una fuga de memoria que se esta constantemente creando o que proboca que se cree una instancia de esto.
-  Registré una rutina, el día de racha si avanzó pero las calorías quemadas se quedaron en 0. el campo “Calories burned:” en el admin se quedo en blanco.
- El plan nutricional está acompañando de su seccionamiento por desayuno, almuerzo, cena y sugerencia de platos, el coach no tiene forma de ver esto en el panel ya que para aprobarlo solo le muestra los gramos totales, agregar esta información para que pueda aprobar el plan nutricional como es debido y no con información a medias.
- El reporte de datos de estudio esta genial.


PENDIENTES QUE SI SE HARÁN A MANO CON EL COACH
- catalogo rela de ejercicios
- Iconos y fotos de referencia a cada ejercicio
- Miembros reales del gimnasio
- Macros de 5 sugerencias de comida ( Las sugerencias de comida las debe de dar el coach, cuando aprueba la dieta, esto no lo hace el ML, el ML solamente da los macros nutricionales. y luego los divide en los tiempos de comida pero las sugerencias de platillos las debe de poder agregar el coach en el panel de administración )

