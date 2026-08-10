# AGENTS.md

Contexto de diseño del proyecto para cualquier asistente de IA (Claude, Codex)
que trabaje en este repositorio. Léelo completo antes de producir material.

## Qué es este proyecto

Sitio público del curso **Análisis de Datos I (MAT1409)**, impartido por Javier
(CJJM) en la Universidad Anáhuac. Es la **primera** materia cuantitativa de la
secuencia; su continuación es *Análisis de Datos II (MAT2409)*, cuyo repositorio
vive en `../analisis_de_datos/analisis_datos_ii` y es el referente de estructura.

- 16 semanas · 6 créditos · 48 h con académico + 48 h independientes
- Seriación: requiere MAT1405
- Cobertura: estadística descriptiva y probabilidad (la inferencia es AD-II)

### Perfil de los alumnos — las restricciones de diseño

1. **Sin experiencia previa de programación.** Ninguna. Para muchos, este curso es
   su primer contacto con una línea de código.
2. **Grupos mixtos entre carreras**, no separados por perfil: Mercadotecnia
   Estratégica · Administración y Dirección de Empresas · Finanzas y Contaduría
   Pública · Negocios Internacionales.
3. Son alumnos de negocios, no de matemáticas. Pero **este curso sí lleva teoría,
   fórmulas y demostración ligera** — no es un taller de herramientas.

### La restricción operativa: enseñar R sin perder el temario

Es el problema central de cada semestre. La solución adoptada:

::: **R nunca tiene sesión propia.** :::

Cada herramienta de R entra en la sesión donde hace falta para responder una
pregunta estadística. La columna "Herramienta de R" del calendario en `index.qmd`
es el contrato: si una herramienta no aparece ahí, no se enseña.

El antecedente que lo motiva: el curso *Análisis de Datos con Excel y R* dedicaba
un tema completo (`T03_R_Basico`) a historia de R, ventajas de R y configuración
de Colab. Ese tiempo sale del temario y no enseña estadística.

## Principio rector

> **La fórmula explica qué se calcula. El código lo ejecuta. La interpretación y
> sus límites son intransferibles — y son la parte que la IA no hace por ti.**

## Marcos pedagógicos

Documentados para los alumnos en `curso/enfoque.qmd`. Resumen para producción:

1. **Diseño inverso** (Wiggins y McTighe): el portafolio es el resultado deseado;
   el temario es la lista de bloques necesarios para construirlo.
2. **GAISE** (ASA, 2016): pensamiento estadístico · entendimiento conceptual ·
   datos reales con contexto y propósito · aprendizaje activo · tecnología para
   explorar conceptos · evaluación que mejora el aprendizaje. Más los dos énfasis
   de la revisión 2016: proceso investigativo y pensamiento multivariado.
3. **Cinco principios de diseño** (Çetinkaya-Rundel, 2023):
   🍒 cuidar el primer día · 🍰 empezar por el pastel · 🍼 saltarse los pasos de
   bebé · 🥦 esconder las verduras · 🌲 aprovechar el ecosistema.

## Arquitectura pedagógica

### El arco: pregunta → ver → resumir y comparar → anticipar → modelar

El temario oficial es **matriz de cobertura, no guion**. El orden de enseñanza
responde al arco de un análisis real. La matriz punto por punto está en
`curso/programa.qmd` y hay que mantenerla actualizada: es la defensa institucional
del curso.

| Unidad | Sesiones | Temario que cubre |
|---|:--:|---|
| 1 · La pregunta y los datos | 1–3 | 1.1–1.3 |
| 2 · Ver los datos | 4–8 | 3.1, 3.2.1, 3.2.2 |
| 3 · Resumir y comparar | 9–20 | 2.1–2.6, 3.2.3, 3.3 |
| 4 · Anticipar | 21–25 | 4.1–4.4 |
| 5 · Modelar | 26–31 | 5.1–5.4 |

**Las gráficas van antes que los estadísticos.** Es la inversión más importante
respecto del documento oficial: enseñar la media antes del histograma es enseñar
el resumen de una forma que el alumno nunca ha visto. Coincide con R4DS, que abre
con visualización.

### Columna vertebral común + lente de carrera

Los grupos son mixtos, así que **no se producen cuatro cursos paralelos**.

**Columna vertebral (todos, en clase).** Dos fuentes: la **encuesta del grupo**
(sesión 1; los alumnos son la población; sostiene las unidades 1–3) y el **caso de
negocio** de una empresa mexicana exportadora (desde la unidad 2; toca las cuatro
carreras a la vez).

**Lente de carrera (portafolio).** Cada alumno adopta una serie del catálogo
(`datos/catalogo.qmd`) según su carrera y le aplica cada técnica del curso. La
producción se hace una vez; la transferencia ocurre N veces. La mezcla de carreras
deja de ser problema y se vuelve material de discusión.

### Los cuatro dispositivos didácticos

Clases de CSS en `estilo-sitio.scss` y `estilo-slides.scss`. Sintaxis de div de
Quarto: `::: {.a-mano} ... :::`

| Clase | Rótulo | Cuándo |
|---|---|---|
| `.a-mano` | PRIMERO A MANO | **Solo** el cálculo traducido de la fórmula, antes de la función enlatada |
| `.nota` | *(sin rótulo)* | Todo lo demás que se destaque: idea rectora, regla, advertencia técnica |
| `.friccion` | *(sin rótulo)* | Pregunta que se contesta antes de ver el resultado |
| `.no-dice` | LO QUE ESTE NÚMERO NO DICE | Límites de lo que se acaba de calcular |
| `.ia-nota` | IA EN ESTE TEMA | Uso e implicaciones de la IA, anclado al tema exacto |

**Si un rótulo se imprime solo, tiene que ser cierto en todos los usos.**
`.a-mano` llegó a tener 19 apariciones sin un cálculo manual dentro, porque se
usó como recuadro genérico. Queda reservado para las sesiones de la 10 en
adelante, que son las que tienen ese ejercicio. Para destacar cualquier otra
cosa, `.nota`.

**`.a-mano` es obligatorio** la primera vez que aparece cualquier estadístico. No
es una invención: **es el patrón que Javier ya usaba** en sus cuadernos de 2025
(rango a mano → `min`/`max` → `range`+`diff`; suma/n → `mean`; ponderada paso a
paso → `weighted.mean`). Aquí solo se sistematiza y se le da nombre.

```r
# 1. La fórmula, traducida literalmente
sum(x) / length(x)
# 2. La función que hace lo mismo
mean(x)
# 3. ¿Coinciden siempre? (con quantile() la respuesta es NO)
```

**`.ia-nota` no se acumula en una sesión final.** Se distribuye donde la
implicación es concreta: media geométrica (S14), cuantiles y el `type` que el
software elige (S9), curtosis mal definida como "picudez" (S17), probabilidad
condicional (S25).

### La rutina de las cuatro preguntas

Adaptada de GAISE. Se aplica a todo conjunto de datos antes de calcular:
unidades de observación · variables y su tipo · ¿hubo aleatorización? ·
¿observacional o experimento? Es la primera sección del portafolio y aparece en
exámenes.

### Cómo se construye el código de una sesión

Partir todo bloque en tres: **Preparación** (necesaria pero lejos del objetivo de
hoy; se da hecha y con nombre) · **Guardado** (ni necesaria ni relacionada; se
elimina) · **Protagonista** (el corazón; se construye línea por línea con
`code-line-numbers` y `output-location: column`).

## Decisiones tomadas (no reabrir sin razón fuerte)

1. **El curso es en R.** `tidyverse` para manipular y graficar, **base R para los
   estadísticos** (`mean`, `quantile`, `var`, `sd`). Se evaluó migrar a Python y se
   descartó: AD-II ya existe en R y los mismos alumnos la cursan después. Si algún
   día se migra, se migran ambas.

2. **El entorno es Google Colab con kernel de R.** Nada que instalar el primer
   día. Es el principio 🍒 y es lo que Javier ya usa. La instalación local se
   documenta como opcional en `curso/computo.qmd`.

3. **El libro del curso es R for Data Science 2e** (<https://r4ds.hadley.nz/>).
   La estrategia de Wickham —visualización primero, plomería del lenguaje
   después— es la que ordena el arco del curso. El mapeo capítulo↔unidad está en
   `recursos/index.qmd`.

4. **Los datos se sirven desde un snapshot versionado, no desde una API en
   vivo.** Descargar en clase falla. Verificado en agosto de 2026: **Stooq bloquea
   las descargas por script** con un reto JavaScript, así que
   `read_csv("https://stooq.com/...")` **no funciona**. Patrón:
   `scripts/00_descarga_datos.R` congela; las sesiones leen el archivo local.

5. **PISA queda fuera.** Fue el dataset de los cursos anteriores. Dos razones:
   mide competencias de jóvenes de 15 años, remoto para alumnos de negocios; y el
   CSV que se usaba (`pisa_18_mx_variables_curso.csv`) **no trae la columna de
   ponderadores**, así que `mean(pisa_18$PVMATH)` no es el promedio nacional de
   México sino la media no ponderada de la muestra. Se sustituye por **ENIGH**,
   que conserva la propiedad pedagógica (factores de expansión reales para enseñar
   media ponderada) y agrega relevancia para las cuatro carreras.

6. **Sin datos personales de alumnos en el repositorio.** La encuesta del grupo se
   anonimiza en el momento de la captura. Antecedente: el repo del curso 2021
   (`cjjmdata/curso_analisis_de_datos_I`) sigue público con nombres de pila, edad
   y estatura de 27 alumnos reales.

## Ajustes de cátedra al temario

Documentados para los alumnos en `curso/programa.qmd`. Hay libertad para ajustar
hasta ~40% de los temas.

| | Tema | Decisión |
|---|---|---|
| ⛔ | Media armónica (2.2.1) | **Eliminada.** Su dominio real no aparece en negocios; el tiempo va a la geométrica |
| ⚠️ | Gráfica de pastel (3.2.1) | **Se critica, no se produce.** Evidencia: Cleveland y McGill (1984), *JASA* 79(387), 531–554 |
| 🔁 | Ojiva (3.2.2) | **Se moderniza** como frecuencia acumulada / función de distribución empírica. Se menciona el nombre clásico |
| 🔁 | Conteo (4.2) | **Se comprime** a una sesión, enfocada en el supuesto de equiprobabilidad. La sesión liberada va a Bayes |
| ➕ | Datos faltantes (S6) | **Se agrega.** No está en el temario y es el problema más común de datos reales |
| ➕ | Paradoja de Simpson (S20) | **Se agrega.** Pensamiento multivariado de GAISE 2016; se enseña solo con porcentajes |

## Convenciones de código

- Comentarios en **español**, claros y profesionales.
- Pipe nativo `|>`, no `%>%`.
- UTF-8. Al leer CSV, `readr::read_csv()`, no `read.csv()`: el curso 2021 arrastró
  `GÃ.nero` por leer UTF-8 como Latin-1.
- Nombres de objetos y variables en **español**.
- Nunca `setwd()` ni rutas absolutas. Nunca `install.packages()` dentro de un
  `.qmd` ni de un script de sesión.
- Factores con niveles explícitos.
- Para leer de la web, `raw.githubusercontent.com`, jamás la vista `blob` de
  GitHub — devuelve HTML, no datos. Error real del material de 2021.
- **Ningún número tecleado a mano.** Si una slide muestra una cifra, sale del
  cómputo. Errores reales del material previo: `print("Hay 548.25 puntos de
  diferencia...")` y `binwidth = 9.73` cuando la línea anterior calculaba `h`.
- **Nunca `$` con nombre parcial.** `pisa$PVM` funciona por coincidencia parcial y
  se rompe en silencio el día que exista otra columna con ese prefijo. Aparece en
  los cuadernos de 2025.
- **Nada de truncamiento silencioso.** Si un script no puede traer todo lo que
  prometió, tiene que fallar ruidosamente. `scripts/00_descarga_datos.R` perdió 4
  países y el 64% de una serie en su primera versión sin avisar; ahora reintenta y
  verifica cobertura antes de escribir.

### Nombres estables entre sesiones

Los alumnos construyen un cuaderno propio que crece durante el semestre. Cambiar
el nombre de un objeto canónico rompe su trabajo.

| Nombre | Significado | Estable en |
|---|---|---|
| `grupo` | Encuesta anonimizada del grupo | Unidades 1–3 |
| `caso` | Datos del caso de negocio | Unidades 2–5 |
| `serie` | La serie que el alumno eligió para su portafolio | Todo el curso |
| `paises` | Snapshot del Banco Mundial | Todo el curso |

Auxiliares con sufijo inequívoco: `grupo_aux`, `caso_orig`. Nunca `grupo_full`,
`caso_final`, `serie_v2` — suenan a canónicos y confunden.

## Frontera público/privado

El repositorio es público. **NUNCA** agregar: reactivos de examen o claves ·
datos, listas, calificaciones o asistencia de alumnos · respuestas crudas de la
encuesta · rúbricas con ponderaciones institucionales · fechas del semestre en
curso · contenido administrativo. Todo eso vive en Brightspace.

`referencias/` está en `.gitignore`: contiene material fuente de semestres previos
y documentos institucionales.

## Estructura

```
.
├── AGENTS.md                    ← este archivo
├── _quarto.yml                  ← sidebar por unidades del arco
├── estilo-sitio.scss            ← tema claro   (Atkinson Hyperlegible)
├── estilo-oscuro.scss           ← tema oscuro  (solo colores)
├── estilo-slides.scss           ← tema revealjs
├── index.qmd                    ← portada + calendario de 31 sesiones
├── curso/                       ← programa, enfoque, evaluación, cómputo, IA
├── unidades/                    ← panorama de cada unidad (u1–u5)
├── slides/u1..u5/               ← presentaciones
├── datos/catalogo.qmd           ← fuentes por carrera, con estado verificado
├── portafolio/index.qmd         ← mecánica del portafolio
├── recursos/index.qmd           ← R4DS y bibliografía
├── scripts/                     ← NO SE PUBLICA
├── analisis/                    ← NO SE PUBLICA (notebooks de validación)
├── prompts/                     ← NO SE PUBLICA
├── examen/                      ← NO SE PUBLICA
└── referencias/                 ← NO SE VERSIONA (material fuente)
```

## Paleta

Derivada de STA 210 (Çetinkaya-Rundel), que es la referencia visual elegida.

```
teal-900   #24494C   encabezados y texto de énfasis
teal-700   #3A6B6F   enlaces y bordes
teal-500   #5B888C   acento principal (UI, no texto: 3.7:1)
teal-100   #D9E3E4   fondo de sidebar y footer
salmon-700 #B4704F   acento secundario en texto
salmon-500 #E0A890   acento secundario en UI
brick-700  #A4503C   advertencias fuertes
sage-700   #5A7B5A   confirmaciones
```

Tipografía **Atkinson Hyperlegible** (Google Fonts), diseñada para legibilidad.
Monoespaciada: JetBrains Mono / Fira Code / Consolas.

### Ligaduras tipográficas: desactivadas, no negociable

JetBrains Mono y Fira Code convierten `<-` en una flecha y `|>` en un triángulo.
El código copiado sale correcto, pero el alumno **ve un glifo que no está en su
teclado**. Con alumnos que nunca han programado eso es una barrera real.

Ambos SCSS apagan `liga`, `clig` y **`calt`** — esta última es la que implementa
las ligaduras en estas fuentes; sin ella no basta con `font-variant-ligatures`.

Si se cambia la fuente monoespaciada, verificar que la regla siga aplicando.

## Patrón de producción de una sesión

Dos archivos paralelos: `slides/uN/sXX_tema.qmd` (público) y
`analisis/sXX_tema.qmd` (notebook interno que ejecuta el análisis completo y
produce los números reales).

**Regla de oro**: si una slide muestra un número, ese número sale del cómputo. Se
actualiza solo cuando cambian los datos. Nunca marcadores de posición.

## Deploy

- URL: https://cjjmdata.github.io/analisis_datos_i/
- Push a `main` dispara `.github/workflows/publish.yml`.
- El CI **no instala R**: publica desde `_freeze/`, que se versiona.
- El workflow verifica primero que todo `.qmd` con chunks de R tenga su `_freeze/`
  y falla con mensaje claro si falta. Sin esa verificación el error aparece tarde
  y es críptico (AD-II tiene ese problema).

Flujo: `quarto render` en local → commit incluyendo `_freeze/` → push.

## Comandos

```bash
quarto preview                       # desarrollo
quarto render                        # producción; actualiza _freeze/
Rscript scripts/00_descarga_datos.R  # snapshot de datos (una vez por semestre)
```

## Trato con el usuario

Javier trabaja en Positron, escribe en español y prefiere **pushback sustantivo**:
si algo tiene un problema metodológico, pedagógico o técnico, hay que decirlo con
argumento, no validarlo por complacencia. Comentarios concisos. Nunca inventar
datos, cifras, referencias ni capacidades de una fuente: si no se verificó, se
declara como no verificado.
