/**
 * Crea el formulario de la encuesta del grupo (sesión 2).
 *
 * Cómo se usa, una vez por grupo y por semestre:
 *   1. script.google.com → Nuevo proyecto
 *   2. Pegar este archivo completo
 *   3. Ejecutar crearEncuestaDelGrupo()
 *   4. Autorizar cuando lo pida (es tu propia cuenta creando tu propio form)
 *   5. Copiar las dos ligas que imprime el registro de ejecución
 *
 * Por qué un script y no armarlo a mano: el instrumento queda versionado. Si el
 * semestre que entra hay que cambiar una pregunta, se ve en el diff qué cambió,
 * que es lo mismo que el curso le exige al alumno sobre sus datos.
 *
 * ANONIMATO. El formulario no pide nombre ni correo y no exige iniciar sesión.
 * Un dato personal recogido de forma identificable no se puede desidentificar
 * después; la única protección efectiva es no recogerlo.
 *
 * La marca de tiempo NO se puede desactivar: Google la escribe siempre en la
 * columna A de la hoja de respuestas. Se descarta al publicar, con el paso 3 de
 * la guía, y también en scripts/01_encuesta_grupo.R.
 */

var CARRERAS = [
  'Mercadotecnia Estratégica',
  'Administración y Dirección de Empresas',
  'Finanzas y Contaduría Pública',
  'Negocios Internacionales'
];

function crearEncuestaDelGrupo() {
  var form = FormApp.create('Encuesta del grupo · Análisis de Datos I')
    .setDescription(
      'Cinco datos del grupo, para trabajarlos en clase durante las tres ' +
      'primeras unidades.\n\n' +
      'Es anónima: no se pide nombre ni correo, y no hace falta iniciar sesión. ' +
      'Contesta con el dato que tengas; si alguno no lo sabes con exactitud, ' +
      'aproxima y lo discutimos en clase, porque esa imprecisión es parte del tema.'
    )
    .setCollectEmail(false)
    .setProgressBar(false)
    .setAllowResponseEdits(false)
    .setLimitOneResponsePerUser(false)
    .setConfirmationMessage('Listo. Tus datos ya están en el conjunto del grupo.');

  // En cuentas de Workspace este método existe; en cuentas personales el
  // formulario ya es público y la llamada truena. Se protege para que el
  // script corra igual en las dos.
  try {
    form.setRequireLogin(false);
  } catch (e) {
    Logger.log('setRequireLogin no aplica en esta cuenta: ' + e.message);
  }

  // --- Carrera -------------------------------------------------------------
  // Lista cerrada: con texto libre, count(grupo, carrera) devuelve una fila por
  // cada forma de escribir lo mismo.
  form.addMultipleChoiceItem()
    .setTitle('Carrera')
    .setChoiceValues(CARRERAS)
    .showOtherOption(true)
    .setRequired(true);

  // --- Edad ----------------------------------------------------------------
  form.addTextItem()
    .setTitle('Edad, en años cumplidos')
    .setHelpText('Solo el número. Ejemplo: 20')
    .setValidation(
      FormApp.createTextValidation()
        .setHelpText('Escribe un número entero entre 15 y 80.')
        .requireNumberBetween(15, 80)
        .build()
    )
    .setRequired(true);

  // --- Estatura ------------------------------------------------------------
  // En metros con punto decimal. El redondeo que haga cada quien es el material
  // de la discusión de la sesión 4.
  form.addTextItem()
    .setTitle('Estatura, en metros')
    .setHelpText('Con punto decimal. Ejemplo: 1.72')
    .setValidation(
      FormApp.createTextValidation()
        .setHelpText('Escribe un número entre 1.20 y 2.20, con punto. Ejemplo: 1.72')
        .requireNumberBetween(1.20, 2.20)
        .build()
    )
    .setRequired(true);

  // --- Traslado ------------------------------------------------------------
  form.addTextItem()
    .setTitle('Tiempo de traslado a la universidad, en minutos')
    .setHelpText('De puerta a puerta, en un día normal de clases. Solo el número.')
    .setValidation(
      FormApp.createTextValidation()
        .setHelpText('Escribe un número entre 0 y 300.')
        .requireNumberBetween(0, 300)
        .build()
    )
    .setRequired(true);

  // --- Calzado -------------------------------------------------------------
  // Dos preguntas y no una: en México conviven la numeración mexicana y la
  // europea, y un solo campo numérico mezcla dos escalas distintas en la misma
  // columna. Preguntar cuál se usó permite separarlas, y de paso es el ejemplo
  // de la sesión 4 sobre definir la variable antes de medirla.
  form.addTextItem()
    .setTitle('Número de calzado')
    .setHelpText('El número que usas normalmente. Solo la cifra.')
    .setValidation(
      FormApp.createTextValidation()
        .setHelpText('Escribe un número entre 15 y 50.')
        .requireNumberBetween(15, 50)
        .build()
    )
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('¿En qué numeración es ese número?')
    .setChoiceValues(['Mexicana', 'Europea', 'No sé'])
    .setRequired(true);

  // --- Hoja de respuestas --------------------------------------------------
  var hoja = SpreadsheetApp.create('Encuesta del grupo · respuestas');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, hoja.getId());

  Logger.log('=========================================================');
  Logger.log('Liga para contestar:  ' + form.getPublishedUrl());
  Logger.log('Liga para editar:     ' + form.getEditUrl());
  Logger.log('Hoja de respuestas:   ' + hoja.getUrl());
  Logger.log('=========================================================');
  Logger.log('Falta el paso 3 de la guía: crear la hoja "publica" y');
  Logger.log('publicarla como CSV. La hoja de respuestas trae la marca de');
  Logger.log('tiempo en la columna A y esa columna no se publica.');
}
