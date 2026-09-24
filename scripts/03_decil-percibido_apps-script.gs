/**
 * Crea el formulario de una sola pregunta para la sesión 10: en qué decil de
 * ingreso cree cada quien que cae su hogar.
 *
 * Cómo se usa, una vez por semestre (el mismo formulario sirve a los cuatro grupos):
 *   1. script.google.com → Nuevo proyecto
 *   2. Pegar este archivo completo
 *   3. Ejecutar crearFormularioDecil()
 *   4. Autorizar cuando lo pida
 *   5. Copiar las ligas que imprime el registro de ejecución
 *   6. Publicar la hoja de respuestas como CSV (pasos 3 y 4 de prompts/s02_encuesta-operacion.md)
 *
 * ANONIMATO. No pide nombre ni correo y no exige iniciar sesión. Importa más
 * aquí que en la encuesta del grupo: se está preguntando por el ingreso del
 * hogar, y la lámina promete que nadie lo dice en voz alta. El conteo se
 * proyecta agregado; ninguna respuesta individual se muestra.
 *
 * La marca de tiempo la escribe Google y no se puede desactivar. Para esta
 * pregunta no se usa.
 *
 * Los deciles van en números romanos porque es la convención del INEGI en la
 * ENIGH, que es la fuente de la tabla contra la que se compara.
 */

var DECILES = [
  'I · el de menor ingreso',
  'II',
  'III',
  'IV',
  'V',
  'VI',
  'VII',
  'VIII',
  'IX',
  'X · el de mayor ingreso'
];

function crearFormularioDecil() {
  var form = FormApp.create('¿En qué decil de ingreso cae tu hogar? · Análisis de Datos I')
    .setDescription(
      'Piensa en el ingreso mensual de tu hogar, sumando lo que entra de todas ' +
      'las personas que viven ahí.\n\n' +
      'Es una estimación, no un dato exacto: contesta con lo que creas.\n\n' +
      'Es anónima. No se pide nombre ni correo, y en clase solo se proyecta el ' +
      'conteo del grupo, nunca una respuesta individual.'
    )
    .setCollectEmail(false)
    .setProgressBar(false)
    .setAllowResponseEdits(false)
    .setLimitOneResponsePerUser(false)
    .setConfirmationMessage('Listo. Tu respuesta ya está en el conteo del grupo.');

  try {
    form.setRequireLogin(false);
  } catch (e) {
    Logger.log('setRequireLogin no aplica en esta cuenta: ' + e.message);
  }

  // El mismo formulario sirve a los cuatro grupos, así que la hoja acumula a
  // todos. Esta pregunta es la que permite filtrar y que cada clase vea solo
  // sus respuestas. Los grupos van por carrera.
  form.addMultipleChoiceItem()
    .setTitle('Grupo')
    .setChoiceValues([
      'Mercadotecnia Estratégica',
      'Administración y Dirección de Empresas',
      'Finanzas y Contaduría Pública',
      'Negocios Internacionales'
    ])
    .setRequired(true);

  // Lista cerrada y en orden: con texto libre no hay forma de contar por decil.
  form.addMultipleChoiceItem()
    .setTitle('¿En cuál de los diez deciles crees que cae tu hogar?')
    .setHelpText('El decil I agrupa a los hogares de menor ingreso del país; el X, a los de mayor.')
    .setChoiceValues(DECILES)
    .setRequired(true);

  var hoja = SpreadsheetApp.create('Decil percibido · respuestas');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, hoja.getId());

  Logger.log('=========================================================');
  // getShortUrl() ya no existe en FormApp; la liga completa funciona igual
  Logger.log('Liga para contestar:  ' + form.getPublishedUrl());
  Logger.log('Liga para editar:     ' + form.getEditUrl());
  Logger.log('Hoja de respuestas:   ' + hoja.getUrl());
  Logger.log('=========================================================');
  Logger.log('Falta publicar la hoja como CSV y pegar esa URL en el cuaderno');
  Logger.log('de la sesión 10, en la celda del conteo por decil.');
}
