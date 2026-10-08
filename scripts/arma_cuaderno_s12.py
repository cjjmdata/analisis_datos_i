"""Arma el cuaderno de Colab de las sesiones 12 y 13.

Mismo patrón que `arma_cuaderno_s11.py`.

Uso: python scripts/arma_cuaderno_s12.py
"""

import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent

URL_HOGARES = ('https://raw.githubusercontent.com/cjjmdata/analisis_datos_i/main/'
               'datos/enigh2024_hogares.csv.gz')
URL_PAISES = ('https://raw.githubusercontent.com/cjjmdata/analisis_datos_i/main/'
              'datos/banco_mundial.csv')

S12 = [
    ("md", """# Sesiones 12 y 13 · Centro: moda, mediana y media

**Antes de empezar:** Entorno de ejecución → Cambiar tipo de entorno de ejecución
→ **R**, y después Archivo → Guardar una copia en Drive."""),

    ("md", f"""## 1 · Una base nueva

La Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH) 2024, del
INEGI. Cada renglón es un hogar; el ingreso y el gasto son trimestrales, en
pesos.

El archivo está comprimido y `read_csv()` lo abre igual."""),
    ("code", f'''library(tidyverse)

hogares <- read_csv("{URL_HOGARES}", show_col_types = FALSE)

glimpse(hogares)'''),
    ("md", """Antes de calcular, las cuatro preguntas:

- **Unidad de observación:** el hogar, no la persona.
- **Variables:** ingreso y gasto en pesos, integrantes y perceptores en
  personas, el resto categóricas.
- **¿Hubo aleatorización?** Sí, es una muestra probabilística de hogares.
- **¿Observacional o experimento?** Observacional.

Antes de correr la celda siguiente, escribe tu apuesta: un hogar típico en
México, ¿cuánto recibe al mes?"""),

    ("md", """## 2 · La moda

El valor que más se repite. Es la única medida de centro que funciona con
variables categóricas."""),
    ("code", """count(hogares, educa_jefe, sort = TRUE)"""),
    ("code", """# ¿Y con una variable continua?
sort(table(hogares$ingreso), decreasing = TRUE)[1:3]

length(unique(hogares$ingreso))"""),
    ("md", """El ingreso toma decenas de miles de valores distintos y el más repetido lo
comparten unas cuantas decenas de hogares. Con variables continuas la moda
describe una coincidencia, no un centro."""),

    ("md", """## 3 · La mediana

Parte los datos ordenados en dos mitades. Es el segundo cuartil de la sesión
10, con otro nombre."""),
    ("code", """median(hogares$ingreso)

quantile(hogares$ingreso, 0.50)"""),
    ("md", """Antes de correr la celda: si el 1% de hogares con mayor ingreso saliera de la
base, ¿qué le pasaría a la mediana?"""),
    ("code", """quitados <- filter(hogares, ingreso <= quantile(ingreso, 0.99))

nrow(hogares) - nrow(quitados)     # hogares que salieron

median(hogares$ingreso)
median(quitados$ingreso)"""),

    ("md", """## 4 · La media

Suma todos los valores y reparte el total entre el número de observaciones:

$$\\bar{x} = \\frac{\\sum x_i}{n}$$

Es el único de los tres centros que usa todos los datos."""),
    ("code", """sum(hogares$ingreso) / length(hogares$ingreso)

mean(hogares$ingreso)"""),
    ("code", """# Los mismos hogares fuera, y ahora mira la media
mean(hogares$ingreso)
mean(quitados$ingreso)"""),
    ("md", """La mediana se calcula por posición y casi no se movió. La media reparte el
total, así que cada peso que sale la mueve.

Dibuja las dos sobre el histograma. La gráfica recorta el 5% de ingresos más
altos para que se vea la forma; los hogares recortados siguen en los
cálculos."""),
    ("code", """ggplot(filter(hogares, ingreso <= quantile(ingreso, 0.95)), aes(x = ingreso)) +
  geom_histogram(binwidth = 5000, fill = "#CCCCCC", color = "white", boundary = 0) +
  geom_vline(xintercept = median(hogares$ingreso), color = "#3A6B6F", linewidth = 1.2) +
  geom_vline(xintercept = mean(hogares$ingreso), color = "#A4503C", linewidth = 1.2) +
  labs(x = "Ingreso trimestral del hogar, en pesos", y = "Hogares")"""),
    ("code", """# ¿Qué porcentaje de hogares recibe menos que la media?
mean(hogares$ingreso < mean(hogares$ingreso)) * 100"""),
    ("md", """Dos de cada tres hogares quedan debajo del promedio. Cuando la distribución
tiene cola larga, la media deja de describir al hogar que está en medio."""),

    ("md", """## 5 · La media ponderada

La ENIGH visitó 91,414 hogares para describir a los casi 39 millones que hay en
México. Cada hogar visitado representa a muchos otros, y cuántos viene en la
columna `factor`."""),
    ("code", """range(hogares$factor)

sum(hogares$factor)"""),
    ("md", """La media ponderada multiplica cada valor por su peso, suma, y reparte entre la
suma de los pesos:

$$\\bar{x}_w = \\frac{\\sum w_i\\,x_i}{\\sum w_i}$$

Con todos los pesos iguales a 1, el denominador es $n$ y la fórmula vuelve a ser
la media de siempre."""),
    ("code", """sum(hogares$factor * hogares$ingreso) / sum(hogares$factor)

weighted.mean(hogares$ingreso, hogares$factor)"""),
    ("md", """Ese resultado, 77,864 pesos trimestrales, es la cifra que publica el INEGI. La
media simple describe a la muestra; la ponderada describe al país.

Corre la celda y mira cómo cambia el factor promedio según el ingreso."""),
    ("code", """hogares |>
  mutate(decil = ntile(ingreso, 10)) |>
  summarise(factor_promedio = round(mean(factor)), .by = decil) |>
  arrange(decil)"""),

    ("md", f"""### El mismo cálculo en otra base

El PIB per cápita promedio de quince países, ¿se calcula sumándolos y
dividiendo entre quince?"""),
    ("code", f'''paises <- read_csv("{URL_PAISES}", show_col_types = FALSE)

ultimo <- filter(paises, anio == max(anio), !is.na(pib_per_capita))

mean(ultimo$pib_per_capita)

weighted.mean(ultimo$pib_per_capita, ultimo$poblacion)'''),
    ("md", """En la ENIGH la media simple quedaba por debajo de la ponderada; aquí queda por
encima. El peso corrige hacia lo que cada observación representa, y eso puede ir
en cualquiera de las dos direcciones."""),

    ("md", """## 6 · El perfil de Oaxaca

Compara tu estado con el país."""),
    ("code", """oaxaca <- filter(hogares, entidad == "Oaxaca")

nrow(oaxaca)
sum(oaxaca$factor)

weighted.mean(oaxaca$ingreso, oaxaca$factor)
weighted.mean(hogares$ingreso, hogares$factor)"""),
    ("code", """median(oaxaca$ingreso)
median(hogares$ingreso)"""),
    ("md", """El promedio de Oaxaca es alrededor de dos tercios del nacional. Revisa si la
mediana guarda la misma proporción, y escribe en tu cuaderno qué significa que
no la guarde.

Cambia `"Oaxaca"` por otra entidad y vuelve a correr las celdas."""),
    ("code", """hogares |>
  summarise(ingreso = weighted.mean(ingreso, factor), .by = entidad) |>
  arrange(ingreso)"""),

    ("md", """## Tarea

Sobre **tu serie del portafolio**:

1. La media y la mediana de tu variable numérica, con sus unidades.
2. Cuál de las dos describe mejor tu serie, con una razón que salga de la forma
   de tu histograma.
3. El porcentaje de tus observaciones que queda debajo de la media.
4. Si tu base trae alguna columna que sirva de peso, la media ponderada y la
   diferencia contra la simple. Si no la trae, escribe qué pesaría si pudieras.
5. Una línea sobre lo que tu medida de centro no muestra.

**Guarda tu copia.**"""),
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


escribe("s12_centro.ipynb", S12)
