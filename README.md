# Análisis de Datos I — sitio del curso

Sitio público de consulta para **Análisis de Datos I (MAT1409)**, Universidad
Anáhuac. Contiene presentaciones, catálogo de fuentes de datos y recursos. Lo
administrativo se maneja por Brightspace.

🔗 <https://cjjmdata.github.io/analisis_datos_i/>

## Qué es este curso

Estadística descriptiva y probabilidad para estudiantes de negocios sin
experiencia previa de programación. El curso se imparte en **R**, y R se enseña
sobre la marcha: no hay sesiones de "introducción a R", cada herramienta entra en
la sesión donde hace falta para responder una pregunta estadística.

El temario oficial se cubre completo, pero se recorre en el orden en que ocurre un
análisis real: **pregunta → ver → resumir y comparar → anticipar → modelar**. La
matriz de cobertura punto por punto está en `curso/programa.qmd`.

Los alumnos trabajan en **Google Colab** con kernel de R. No se instala nada.

## Setup para desarrollo

### 1. Requisitos

- R 4.3+ con `tidyverse`, `jsonlite`, `knitr`
- [Quarto CLI](https://quarto.org/docs/get-started/) 1.4+
- Editor: Positron, RStudio o VS Code con la extensión de Quarto

### 2. Congelar los datos compartidos

Una vez por semestre:

```bash
Rscript scripts/00_descarga_datos.R
```

Descarga el snapshot del Banco Mundial a `datos/`. El script reintenta ante
fallos de la API y **falla ruidosamente** si no logra cobertura completa: un
archivo incompleto que parece correcto es peor que un error.

### 3. Renderizar

```bash
quarto preview     # desarrollo
quarto render      # producción; actualiza _freeze/
```

## Publicación

GitHub Pages, con estrategia de **freeze local**: el CI no ejecuta R, publica a
partir de los resultados precomputados en `_freeze/`, que se versionan.

1. Renderizar en local (`quarto render`)
2. Commit incluyendo `_freeze/`
3. Push a `main` → GitHub Actions publica

El workflow verifica antes de renderizar que todo `.qmd` con chunks de R tenga su
`_freeze/` correspondiente, y falla con un mensaje claro si falta.

## Estructura

```
.
├── AGENTS.md              ← contrato de diseño; léelo antes de producir material
├── _quarto.yml            ← configuración del sitio
├── index.qmd              ← portada y calendario de 31 sesiones
├── curso/                 ← programa, enfoque, evaluación, cómputo, postura IA
├── unidades/              ← panorama de cada unidad del arco
├── slides/                ← presentaciones por unidad
├── datos/catalogo.qmd     ← fuentes por carrera, con estado de verificación
├── portafolio/            ← mecánica del portafolio por carrera
├── recursos/              ← R4DS y bibliografía
└── scripts/               ← preparación de datos (no se publica)
```

## Licencia y privacidad

- Datos del Banco Mundial: CC-BY-4.0
- Materiales del curso: por definir

Este repositorio **nunca** contiene información administrativa ni datos
identificables de estudiantes. La encuesta del grupo se levanta anónima desde la
captura.
