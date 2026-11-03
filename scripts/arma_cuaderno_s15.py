"""Arma el cuaderno de Colab de las sesiones 15 y 16: dispersión.

Mismo patrón que `arma_cuaderno_s12.py`: el cuaderno se genera desde aquí para
que se pueda rehacer y para que el texto pase por `lint_redaccion.py`. Sigue el
orden de `slides/u3/s15_dispersion.qmd`; las preguntas van antes de cada celda
para que el alumno anote su respuesta antes de correrla.

Uso: python scripts/arma_cuaderno_s15.py
"""

import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent

URL_HOGARES = ('https://raw.githubusercontent.com/cjjmdata/analisis_datos_i/main/'
               'datos/enigh2024_hogares.csv.gz')
URL_MERCADO = ('https://raw.githubusercontent.com/cjjmdata/analisis_datos_i/main/'
               'datos/mercado_diario.csv')
URL_COLORES = ('https://raw.githubusercontent.com/cjjmdata/analisis_datos_i/main/'
               'R/colores.R')

S15 = [
    ("md", """# Sesiones 15 y 16 · Dispersión

**Antes de empezar:** Entorno de ejecución → Cambiar tipo de entorno de ejecución
→ **R**, y después Archivo → Guardar una copia en Drive."""),

    ("md", """## 1 · Los datos

Los hogares de la ENIGH 2024, que ya conoces: cada renglón es un hogar, y
`ingreso` y `gasto` están en pesos por trimestre. También las acciones de Apple
(AAPL) y Tesla (TSLA), con su precio diario en dólares."""),
    ("code", f'''library(tidyverse)
source("{URL_COLORES}")   # colores del curso

hogares <- read_csv("{URL_HOGARES}", show_col_types = FALSE)
mercado <- read_csv("{URL_MERCADO}", show_col_types = FALSE)'''),

    ("md", """## 2 · El mismo centro, otra dispersión

Durango y Michoacán tienen casi el mismo ingreso medio. Antes de correr la
siguiente celda: ¿en cuál de los dos estados crees que los ingresos están más
separados entre sí?"""),
    ("code", """dos <- filter(hogares, entidad %in% c("Durango", "Michoacán"))

dos |>
  group_by(entidad) |>
  summarize(hogares = n(), media = mean(ingreso), mediana = median(ingreso))"""),
    ("code", """ggplot(dos, aes(x = ingreso, y = entidad)) +
  geom_boxplot(fill = TEAL_100, color = TEAL_700, outlier.color = col_destaca, outlier.alpha = 0.5) +
  coord_cartesian(xlim = c(0, 300000)) +
  scale_x_continuous(labels = scales::comma) +
  labs(x = "Ingreso trimestral del hogar, en pesos", y = NULL)"""),

    ("md", """## 3 · Rango y rango intercuartil

Las dos medidas se calculan por posición: el rango con el mínimo y el máximo, el
rango intercuartil con los cuartiles 1 y 3."""),
    ("code", """diff(range(hogares$ingreso))     # máximo menos mínimo

IQR(hogares$ingreso)             # tercer cuartil menos primer cuartil"""),
    ("md", """Si quitas el hogar de mayor ingreso, ¿cuál de las dos cambia más? Anota tu
respuesta y corre la celda."""),
    ("code", """sin_mayor <- filter(hogares, ingreso < max(ingreso))

diff(range(sin_mayor$ingreso))
IQR(sin_mayor$ingreso)"""),

    ("md", """## 4 · Varianza y desviación estándar

Las edades del jefe del hogar en los cinco primeros hogares de la base. Con tu
calculadora: la media, la distancia de cada edad a la media y la suma de esas
distancias."""),
    ("code", """edades <- hogares$edad_jefe[1:5]
edades

desv <- edades - mean(edades)
desv
sum(desv)"""),
    ("md", """### Primero a mano

La varianza eleva cada desviación al cuadrado y divide la suma entre $n - 1$:

$$s^2 = \\frac{\\sum (x_i - \\bar{x})^2}{n - 1}$$

¿Coinciden las tres cifras de la celda siguiente?"""),
    ("code", """sum(desv^2) / (length(edades) - 1)    # la fórmula, traducida literalmente

var(edades)                           # la función de R

sum(desv^2) / length(edades)          # dividiendo entre n"""),
    ("md", """La desviación estándar es la raíz de la varianza y regresa a la unidad original:
de años al cuadrado, a años."""),
    ("code", """sqrt(var(edades))
sd(edades)"""),
    ("md", """Cambia una de las edades por 90 y vuelve a calcular. ¿Cuánto cambia la
desviación estándar?"""),
    ("code", """otras <- edades
otras[3] <- 90

sd(edades)
sd(otras)"""),

    ("md", """### La edad de todos los jefes de hogar

Las líneas punteadas van a una desviación estándar de la media, una abajo y otra
arriba. Antes de correr la segunda celda: ¿qué parte de los hogares crees que
queda entre ellas?"""),
    ("code", """media_edad <- mean(hogares$edad_jefe)
de_edad    <- sd(hogares$edad_jefe)
limites    <- media_edad + c(-1, 1) * de_edad     # media − s y media + s
limites

ggplot(hogares, aes(x = edad_jefe)) +
  geom_histogram(binwidth = 2, boundary = 0, fill = TEAL_500, color = "white") +
  geom_vline(xintercept = media_edad, color = col_media, linewidth = 1.2) +
  geom_vline(xintercept = limites, color = col_media, linetype = "dashed") +
  labs(x = "Edad del jefe del hogar, años", y = "Hogares")"""),
    ("code", """# Proporción de hogares a menos de una desviación estándar de la media
mean(abs(hogares$edad_jefe - media_edad) <= de_edad)

# La distancia promedio a la media, sin signo, no es la desviación estándar
mean(abs(hogares$edad_jefe - media_edad))
de_edad"""),
    ("md", """¿Por qué la desviación estándar queda por encima de la distancia promedio?
Piensa en qué hace el cuadrado con las distancias grandes."""),

    ("md", """### La desviación estándar del ingreso

¿Cuánto crees que cambia la desviación estándar de los hogares del país si quitas
el hogar de mayor ingreso?"""),
    ("code", """sd(hogares$ingreso)
sd(sin_mayor$ingreso)

IQR(hogares$ingreso)
IQR(sin_mayor$ingreso)"""),
    ("md", """Durango y Michoacán con las dos medidas. ¿Cuál es más disperso con cada una?"""),
    ("code", """dos |>
  group_by(entidad) |>
  summarize(media = mean(ingreso), de = sd(ingreso), ric = IQR(ingreso), maximo = max(ingreso))"""),

    ("md", """## 5 · Coeficiente de variación

La desviación estándar como porcentaje de la media:

$$CV = \\frac{s}{\\bar{x}} \\times 100$$

¿Qué varía más entre los hogares, el ingreso o el número de integrantes?"""),
    ("code", """sd(hogares$ingreso) / mean(hogares$ingreso) * 100

sd(hogares$integrantes) / mean(hogares$integrantes) * 100"""),

    ("md", """### Precios de dos acciones en 2025

La desviación estándar del precio de TSLA es mayor que la de AAPL. ¿Su precio fue
más disperso también en relación con su precio medio?"""),
    ("code", """mercado |>
  filter(year(fecha) == 2025) |>
  group_by(clave) |>
  summarize(media = mean(cierre), de = sd(cierre), cv = de / media * 100)"""),
    ("md", """Ahora con los rendimientos diarios, en porcentaje. Según el coeficiente de
variación, ¿cuál acción fue más arriesgada? ¿Coincide con la desviación
estándar?"""),
    ("code", """mercado |>
  arrange(clave, fecha) |>
  group_by(clave) |>
  mutate(rend = (ajustado / lag(ajustado) - 1) * 100) |>
  filter(year(fecha) == 2025) |>
  summarize(media = mean(rend), de = sd(rend), cv = de / media * 100)"""),
    ("md", """La media de un rendimiento diario está cerca de cero, y dividir entre un número
cercano a cero produce cocientes enormes. El coeficiente de variación solo tiene
sentido con variables positivas cuyo cero significa ausencia."""),

    ("md", """## 6 · Dispersión por grupos

`group_by()` separa la base en grupos y `summarize()` calcula un renglón por
grupo."""),
    ("code", """hogares |>
  group_by(tam_loc) |>
  summarize(
    hogares = n(),
    media   = mean(ingreso),
    de      = sd(ingreso),
    cv      = de / media * 100,
    ric     = IQR(ingreso)
  )"""),
    ("md", """Los ingresos de los hogares de Oaxaca, ¿están más o menos dispersos que los del
resto del país?"""),
    ("code", """hogares |>
  mutate(region = if_else(entidad == "Oaxaca", "Oaxaca", "Resto del país")) |>
  group_by(region) |>
  summarize(media = mean(ingreso), de = sd(ingreso),
            cv = de / media * 100, ric = IQR(ingreso))"""),
    ("code", """cv_entidad <- hogares |>
  group_by(entidad) |>
  summarize(cv = sd(ingreso) / mean(ingreso) * 100) |>
  arrange(desc(cv))

cv_entidad"""),

    ("md", """## 7 · Tu serie

Sobre la variable numérica de tu serie del portafolio: el rango, el rango
intercuartil, la desviación estándar y el coeficiente de variación, con sus
unidades. Si tu serie es un índice o un precio que sigue una tendencia, calcula
la dispersión de sus variaciones de un periodo al siguiente."""),
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


escribe("s15_dispersion.ipynb", S15)
