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
INEGI. Cada renglón es un hogar.

**El ingreso y el gasto son trimestrales**, en pesos: lo que entró al hogar en
tres meses. Para pensarlos al mes, se dividen entre tres.

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
    ("code", """escolaridad <- count(hogares, educa_jefe, sort = TRUE)

escolaridad"""),
    ("code", """ggplot(escolaridad, aes(x = n, y = fct_reorder(educa_jefe, n))) +
  geom_col(fill = "#5A7B5A", alpha = 0.85) +
  geom_text(aes(label = n), hjust = -0.15) +
  scale_x_continuous(expand = expansion(mult = c(0, 0.18))) +
  labs(x = "Hogares", y = NULL)"""),
    ("md", """Con el número de integrantes pasa lo mismo: son pocos valores y se repiten."""),
    ("code", """count(hogares, integrantes, sort = TRUE)"""),

    ("md", """### Con una variable continua

Antes de correr la celda: de 91,414 hogares, ¿cuántos crees que coinciden en el
mismo ingreso exacto?"""),
    ("code", """length(unique(hogares$ingreso))

sort(table(hogares$ingreso), decreasing = TRUE)[1:3]"""),
    ("md", """Casi ningún hogar coincide con otro. Para una variable continua, la moda se
busca agrupando: el intervalo con más observaciones es la **clase modal**."""),
    ("code", """cortes <- seq(0, 200000, by = 10000)
conteo <- table(cut(hogares$ingreso, breaks = cortes, right = FALSE, dig.lab = 10))

sort(conteo, decreasing = TRUE)[1:3]"""),
    ("code", """i <- which.max(conteo)

moda_clase <- (cortes[i] + cortes[i + 1]) / 2   # punto medio del intervalo
moda_clase"""),
    ("md", """La otra forma es suavizar el histograma. `density()` reparte cada observación en
una campanita pequeña y las suma: donde se amontonan más hogares, la curva sube.
La moda estimada es el punto más alto de esa curva."""),
    ("code", """curva <- density(hogares$ingreso)

moda_ingreso <- curva$x[which.max(curva$y)]
moda_ingreso"""),
    ("code", """ggplot(filter(hogares, ingreso <= 200000), aes(x = ingreso)) +
  geom_density(color = "#3A6B6F", fill = "#3A6B6F", alpha = 0.15, linewidth = 1) +
  geom_vline(xintercept = moda_ingreso, color = "#5A7B5A", linewidth = 1.2) +
  labs(x = "Ingreso trimestral del hogar, en pesos", y = NULL)"""),
    ("md", """### De qué depende el resultado

Cambia el valor de `adjust` y corre la celda otra vez. Con 0.5 la curva sigue
cada bulto; con 2 la aplana."""),
    ("code", """adjust <- 1

d <- density(hogares$ingreso, adjust = adjust)
d$x[which.max(d$y)]"""),
    ("md", """La clase modal y el pico de la curva dan números distintos, y ninguno está mal
calculado. La moda de una variable continua se **estima**, y el resultado depende
del ancho del intervalo o del suavizado, igual que el histograma depende de su
`binwidth`. Por eso se reporta junto con el método que la produjo.

### Una joroba, o varias

Una distribución es **unimodal** con una joroba, **bimodal** con dos y
**multimodal** con más. Dos jorobas casi siempre señalan dos poblaciones
mezcladas."""),

    ("md", """## 3 · La mediana

Parte los datos ordenados en dos mitades. Es el segundo cuartil de la sesión
10, con otro nombre."""),
    ("code", """median(hogares$ingreso)

quantile(hogares$ingreso, 0.50)"""),
    ("md", """Antes de correr la celda: si el 1% de hogares con mayor ingreso saliera de la
base, ¿qué le pasaría a la mediana?"""),
    ("code", """quitados <- filter(hogares, ingreso <= quantile(ingreso, 0.99))

nrow(hogares) - nrow(quitados)     # hogares que salieron

max(hogares$ingreso)
max(quitados$ingreso)"""),
    ("md", """El hogar más alto de la base recibe más de 17 millones de pesos al trimestre, y
sale junto con otros 914. Mira qué le pasa a la mediana."""),
    ("code", """median(hogares$ingreso)
median(quitados$ingreso)"""),
    ("code", """comparacion <- bind_rows(
  mutate(hogares,  base = "Todos los hogares"),
  mutate(quitados, base = "Sin el 1% más alto")
)

ggplot(comparacion, aes(x = ingreso, y = base)) +
  geom_boxplot(fill = "#CCCCCC", alpha = 0.5, outlier.alpha = 0.12) +
  geom_vline(xintercept = median(hogares$ingreso), color = "#3A6B6F", linewidth = 1) +
  coord_cartesian(xlim = c(0, 300000)) +
  labs(x = "Ingreso trimestral del hogar, en pesos", y = NULL)"""),
    ("md", """El eje llega hasta 300,000 para que se vean las cajas. Los hogares de ingreso
mayor siguen en los datos: `coord_cartesian()` recorta la vista, no la base."""),

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
    ("code", """ggplot(filter(hogares, ingreso <= 200000), aes(x = ingreso)) +
  geom_histogram(binwidth = 10000, fill = "#CCCCCC", color = "white", boundary = 0) +
  geom_vline(xintercept = moda_clase, color = "#5A7B5A", linewidth = 1.2) +
  geom_vline(xintercept = median(hogares$ingreso), color = "#3A6B6F", linewidth = 1.2) +
  geom_vline(xintercept = mean(hogares$ingreso), color = "#A4503C", linewidth = 1.2) +
  labs(x = "Ingreso trimestral del hogar, en pesos", y = "Hogares")"""),
    ("md", """Verde la moda, azul la mediana, rojo la media. Los tres colores se usan igual en
todo el curso."""),
    ("code", """# ¿Qué porcentaje de hogares recibe menos que la media?
mean(hogares$ingreso < mean(hogares$ingreso)) * 100"""),
    ("md", """Dos de cada tres hogares quedan debajo del promedio. Cuando la distribución
tiene cola larga, la media deja de describir al hogar que está en medio."""),

    ("md", """## 5 · La media ponderada

Empieza por algo conocido: un curso con tres componentes que pesan distinto. El
promedio simple trata igual a los tres; la media ponderada respeta el peso de
cada uno."""),
    ("code", """curso <- tibble(
  componente   = c("Primer parcial", "Segundo parcial", "Portafolio"),
  calificacion = c(70, 80, 100),
  peso         = c(0.20, 0.30, 0.50)
)

mean(curso$calificacion)

sum(curso$peso * curso$calificacion) / sum(curso$peso)

weighted.mean(curso$calificacion, curso$peso)"""),
    ("md", """Son pesos de ejemplo, para ver la mecánica.

### De la muestra a la población

La ENIGH visitó 91,414 hogares, que son la **muestra**. Con ellos describe a los
hogares que había en México en 2024, que son la **población**. La columna
`factor` dice a cuántos hogares representa cada uno de los visitados."""),
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
    ("code", """deciles <- hogares |>
  arrange(ingreso) |>
  mutate(decil = pmin(ceiling(cumsum(factor) / sum(factor) * 10), 10)) |>
  summarise(visitados = n(),
            representa = sum(factor),
            factor_promedio = round(mean(factor)), .by = decil)

deciles"""),
    ("md", """Un **decil de ingreso** parte al país en diez grupos con el mismo número de
hogares: se ordenan por ingreso, se va acumulando a cuántos hogares representan,
y se corta cada vez que se junta otro 10%.

Los diez representan 3.88 millones de hogares cada uno, por definición. Lo que
cambia es cuántos hogares hizo falta visitar para juntarlos, y cuánto representa
cada uno de ellos."""),
    ("code", """ggplot(deciles, aes(x = decil, y = visitados)) +
  geom_col(fill = "#CCCCCC", width = 0.75) +
  geom_text(aes(label = visitados), vjust = -0.5) +
  scale_x_continuous(breaks = 1:10) +
  labs(x = "Decil de ingreso, del más bajo al más alto", y = "Hogares visitados")"""),

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
