"""Arma el cuaderno de Colab de la sesión 17: forma, Chebyshev y regla empírica.

Mismo patrón que `arma_cuaderno_s15.py`: el cuaderno se genera desde aquí para
que se pueda rehacer y para que el texto pase por `lint_redaccion.py`. Sigue el
orden de `slides/u3/s17_forma.qmd`; las preguntas van antes de cada celda para
que el alumno anote su respuesta antes de correrla.

Uso: python scripts/arma_cuaderno_s17.py
"""

import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent

BASE = 'https://raw.githubusercontent.com/cjjmdata/analisis_datos_i/main/'
URL_HOGARES = BASE + 'datos/enigh2024_hogares.csv.gz'
URL_MERCADO = BASE + 'datos/mercado_diario.csv'
URL_ECONOMIAS = BASE + 'datos/banco_mundial_economias.csv'
URL_COLORES = BASE + 'R/colores.R'

S17 = [
    ("md", """# Sesión 17 · Forma: sesgo, curtosis, Chebyshev y regla empírica

**Antes de empezar:** Entorno de ejecución → Cambiar tipo de entorno de ejecución
→ **R**, y después Archivo → Guardar una copia en Drive."""),

    ("md", """## 1 · Los datos

Tres bases: los hogares de la ENIGH 2024, los precios diarios de Apple (AAPL) y
Tesla (TSLA), y una nueva, `economias`: la esperanza de vida y el acceso a
electricidad de todas las economías del mundo, según el Banco Mundial. Cada
renglón de `economias` es un país o territorio."""),
    ("code", f'''library(tidyverse)
source("{URL_COLORES}")   # colores del curso

hogares   <- read_csv("{URL_HOGARES}", show_col_types = FALSE)
mercado   <- read_csv("{URL_MERCADO}", show_col_types = FALSE)
economias <- read_csv("{URL_ECONOMIAS}", show_col_types = FALSE)

glimpse(economias)'''),

    ("md", """## 2 · Tres formas

El porcentaje del gasto que cada hogar dedica a alimentos, el gasto del hogar y
la esperanza de vida de cada economía. Antes de correr la celda: ¿cuál crees que
tiene una cola larga, y hacia qué lado?"""),
    ("code", """con_gasto <- filter(hogares, gasto > 0)          # sin gasto no hay porcentaje
nrow(hogares) - nrow(con_gasto)                     # hogares que se descartan

alimentos <- 100 * con_gasto$alimentos / con_gasto$gasto

ggplot(tibble(x = alimentos), aes(x)) +
  geom_histogram(binwidth = 2.5, fill = TEAL_500, color = "white") +
  geom_vline(xintercept = mean(alimentos), color = col_media, linewidth = 1.2) +
  geom_vline(xintercept = median(alimentos), color = col_mediana, linewidth = 1.2, linetype = "dashed") +
  labs(x = "% del gasto en alimentos", y = "Frecuencia")"""),
    ("code", """ggplot(hogares, aes(x = gasto)) +
  geom_histogram(binwidth = 5000, fill = TEAL_500, color = "white") +
  geom_vline(xintercept = mean(hogares$gasto), color = col_media, linewidth = 1.2) +
  geom_vline(xintercept = median(hogares$gasto), color = col_mediana, linewidth = 1.2, linetype = "dashed") +
  coord_cartesian(xlim = c(0, 200000)) +
  labs(x = "Gasto trimestral del hogar, pesos", y = "Frecuencia")"""),
    ("code", """ggplot(economias, aes(x = esperanza_vida)) +
  geom_histogram(binwidth = 2, fill = TEAL_500, color = "white") +
  geom_vline(xintercept = mean(economias$esperanza_vida), color = col_media, linewidth = 1.2) +
  geom_vline(xintercept = median(economias$esperanza_vida), color = col_mediana, linewidth = 1.2, linetype = "dashed") +
  labs(x = "Esperanza de vida al nacer, años", y = "Frecuencia")"""),
    ("md", """La línea continua es la media y la discontinua la mediana. ¿Hacia qué lado se
mueve la media en cada caso?

### La media que no representa a nadie

La media mundial del acceso a electricidad, ¿a cuántas economías describe? Dos
economías no tienen dato y se quitan antes de calcular."""),
    ("code", """luz <- economias$acceso_electricidad[!is.na(economias$acceso_electricidad)]
sum(is.na(economias$acceso_electricidad))           # economías sin dato

mean(luz)
median(luz)

sum(abs(luz - mean(luz)) <= 5)                      # a menos de 5 puntos de la media
sum(luz == 100)                                     # con acceso total"""),

    ("md", """## 3 · Coeficiente de asimetría

Los integrantes de los cinco primeros hogares. Con tu calculadora: la media, las
desviaciones, sus cuadrados y sus cubos.

$$g_1 = \\frac{\\frac{1}{n}\\sum (x_i - \\bar{x})^3}{\\left(\\frac{1}{n}\\sum (x_i - \\bar{x})^2\\right)^{3/2}}$$"""),
    ("code", """cinco <- hogares$integrantes[1:5]
cinco

d <- cinco - mean(cinco)
d
d^2
d^3

mean(d^3) / mean(d^2)^(3/2)     # la fórmula, traducida literalmente"""),
    ("md", """### Una función propia

R no trae una función para la asimetría. La escribes una vez y la usas como
`mean()` o `sd()`."""),
    ("code", """asimetria <- function(x) {
  d <- x - mean(x)                  # las desviaciones
  mean(d^3) / mean(d^2)^(3/2)       # la última línea es el resultado
}

asimetria(cinco)"""),
    ("md", """¿Coinciden los signos con lo que viste en los histogramas? ¿Qué pasa si le
pasas una columna con valores faltantes?"""),
    ("code", """asimetria(alimentos)
asimetria(hogares$gasto)
asimetria(economias$esperanza_vida)

asimetria(economias$acceso_electricidad)
asimetria(luz)"""),

    ("md", """### Cinco hogares contra todos

Los integrantes de todos los hogares están sesgados a la derecha. ¿Qué parte de
las muestras de cinco hogares crees que da un sesgo negativo o cero?
`replicate()` repite una instrucción las veces que le pidas."""),
    ("code", """asimetria(hogares$integrantes)

muestras <- replicate(5000, asimetria(sample(hogares$integrantes, 5)))

sum(is.nan(muestras))                               # cinco hogares iguales: 0 entre 0
mean(muestras[!is.nan(muestras)] <= 0)"""),
    ("md", """Cambia el 5 por 30 y por 300 en `sample()`. ¿Qué pasa con la proporción?

### Un hogar mueve el coeficiente"""),
    ("code", """sin_mayor <- hogares$ingreso[hogares$ingreso < max(hogares$ingreso)]

asimetria(hogares$ingreso)
asimetria(sin_mayor)"""),

    ("md", """## 4 · Curtosis

Los rendimientos diarios de AAPL, en porcentaje, contra una curva normal con la
misma media y la misma desviación estándar. ¿En qué zonas hay más días de los que
predice la curva?"""),
    ("code", """rendimientos <- mercado |>
  arrange(clave, fecha) |>
  group_by(clave) |>
  mutate(rend = (ajustado / lag(ajustado) - 1) * 100) |>
  ungroup() |>
  filter(!is.na(rend))                              # el primer día no tiene rendimiento

aapl <- rendimientos$rend[rendimientos$clave == "AAPL"]

ggplot(tibble(x = aapl), aes(x)) +
  geom_histogram(aes(y = after_stat(density)), binwidth = 0.25, fill = TEAL_500, color = "white") +
  stat_function(fun = dnorm, args = list(mean = mean(aapl), sd = sd(aapl)),
                color = col_destaca, linewidth = 1.2) +
  coord_cartesian(xlim = c(-8, 8)) +
  labs(x = "Rendimiento diario de AAPL, %", y = "Densidad")"""),
    ("md", """### Primero a mano

$$g_2 = \\frac{\\frac{1}{n}\\sum (x_i - \\bar{x})^4}{\\left(\\frac{1}{n}\\sum (x_i - \\bar{x})^2\\right)^{2}} - 3$$

Se resta 3 porque una normal da 3: el resultado es el **exceso de curtosis**."""),
    ("code", """mean(d^4) / mean(d^2)^2 - 3     # los cinco hogares, a mano

curtosis <- function(x) {
  d <- x - mean(x)
  mean(d^4) / mean(d^2)^2 - 3       # 0 para una normal
}

curtosis(cinco)
curtosis(aapl)"""),
    ("md", """¿Qué parte de la curtosis de AAPL viene de los días a más de 3 desviaciones
estándar de la media?"""),
    ("code", """z <- (aapl - mean(aapl)) / sd(aapl)

sum(abs(z) > 3)                                     # días a más de 3 desviaciones
mean(abs(z) > 3)                                    # como proporción de los días

sum(z[abs(z) > 3]^4) / sum(z^4)                     # su parte de la suma de cuartas potencias"""),

    ("md", """## 5 · Chebyshev y la regla empírica

Para cualquier conjunto de datos, al menos $1 - 1/k^2$ de los datos está a menos
de $k$ desviaciones estándar de la media."""),
    ("code", """k <- c(1.5, 2, 3)
1 - 1 / k^2"""),
    ("md", """El gasto de los hogares: ¿cuál es el intervalo $\\bar{x} \\pm 2s$, y qué
porcentaje de los hogares cae ahí?"""),
    ("code", """mean(hogares$gasto) - 2 * sd(hogares$gasto)
mean(hogares$gasto) + 2 * sd(hogares$gasto)

mean(abs(hogares$gasto - mean(hogares$gasto)) <= 2 * sd(hogares$gasto))"""),
    ("md", """La regla empírica dice 68%, 95% y 99.7% para datos de forma normal. Compárala
con lo que observas en cada variable."""),
    ("code", """# Proporción de datos a menos de 1, 2 y 3 desviaciones estándar de la media
dentro <- function(x) {
  c(k1 = mean(abs(x - mean(x)) <= 1 * sd(x)),
    k2 = mean(abs(x - mean(x)) <= 2 * sd(x)),
    k3 = mean(abs(x - mean(x)) <= 3 * sd(x)))
}

dentro(alimentos)
dentro(hogares$gasto)
dentro(aapl)
dentro(economias$esperanza_vida)
dentro(luz)"""),
    ("md", """¿En cuál de las cinco acierta la regla empírica? ¿Se cumple Chebyshev en todas?

## 6 · Tu serie

Sobre la variable numérica de tu serie del portafolio: su histograma con media y
mediana, `asimetria()`, `curtosis()` y la proporción de datos a menos de 1, 2 y 3
desviaciones estándar. ¿Cuál regla la describe mejor?"""),
    ("code", """# Lectura de tu serie
"""),
]


def celda(tipo, fuente):
    lineas = fuente.split("\n")
    fuente_ipynb = [l + "\n" for l in lineas[:-1]] + [lineas[-1]]
    if tipo == "md":
        return {"cell_type": "markdown", "metadata": {}, "source": fuente_ipynb}
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": fuente_ipynb}


def escribe(nombre, celdas):
    nb = {
        "cells": [celda(t, s) for t, s in celdas],
        "metadata": {
            "kernelspec": {"display_name": "R", "language": "R", "name": "ir"},
            "language_info": {"name": "R"},
            "colab": {"provenance": []},
        },
        "nbformat": 4,
        "nbformat_minor": 0,
    }
    destino = RAIZ / "cuadernos" / nombre
    destino.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{nombre}: {len(celdas)} celdas "
          f"({sum(1 for t, _ in celdas if t == 'code')} de código)")


escribe("s17_forma.ipynb", S17)
