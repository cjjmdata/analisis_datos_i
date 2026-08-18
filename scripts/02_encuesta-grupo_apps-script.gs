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
 * La marca de tiempo se conserva. Google la escribe siempre en la columna A y no
 * se puede desactivar; se deja porque sin identificador con el que cruzarla no
 * señala a nadie, y porque sirve para ver el orden de llegada.
 *
 * SI EDITAS EL FORMULARIO A MANO DESPUÉS DE CREARLO, la hoja de respuestas no
 * se reacomoda: conserva los encabezados viejos, deja la columna de una
 * pregunta borrada y manda las nuevas al final, sin importar su posición en el
 * formulario. La hoja es un registro acumulativo, no un espejo. Por eso este
 * script es la definición del instrumento: se edita aquí y se vuelve a crear el
 * formulario, o se acepta que la hoja y el formulario dejen de coincidir.
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

  // --- Género --------------------------------------------------------------
  // Va primero porque es la más rápida de contestar y arranca el flujo. Se
  // levanta para comparar estatura y calzado entre grupos en la unidad 3.
  //
  // OJO con el anonimato: en un salón de treinta, género más carrera más
  // estatura más edad puede describir a una sola persona. El renglón deja de
  // ser anónimo aunque no traiga nombre. Conviene decirlo al levantarla.
  form.addMultipleChoiceItem()
    .setTitle('Género')
    .setChoiceValues(['Femenino', 'Masculino'])
    .showOtherOption(true)
    .setRequired(true);

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
  // La numeración se fija en el enunciado en vez de preguntarse aparte. En
  // México conviven la mexicana y la europea, y sin fijarla un 5 y un 38 pueden
  // ser el mismo pie. Que la escala se declare al definir la variable, y no se
  // rescate después, es el ejemplo de la sesión 4.
  form.addTextItem()
    .setTitle('Número de calzado (numeración mexicana)')
    .setHelpText('Solo la cifra. Si usas numeración europea, conviértela o pregúntame.')
    .setValidation(
      FormApp.createTextValidation()
        .setHelpText('Escribe un número entre 15 y 35.')
        .requireNumberBetween(15, 35)
        .build()
    )
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
