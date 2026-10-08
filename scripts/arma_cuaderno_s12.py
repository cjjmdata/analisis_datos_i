"""Arma el cuaderno de Colab de las sesiones 12 y 13.

Mismo patrón que `arma_cuaderno_s11.py`: el cuaderno se genera desde aquí para
que se pueda rehacer y para que el texto pase por `lint_redaccion.py`.

Uso: python scripts/arma_cuaderno_s12.py
"""

import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent

URL_HOGARES = ('https://raw.githubusercontent.com/cjjmdata/analisis_datos_i/main/'
               'datos/enigh2024_hogares.csv.gz')
URL_PAISES = ('https://raw.githubusercontent.com/cjjmdata/analisis_datos_i/main/'
              'datos/banco_mundial.csv')
URL_ENCUESTA = ('https://docs.google.com/spreadsheets/d/e/2PACX-1vTTKC57eWZVIQ9lwhoR5nVqYM4'
                'kgi5zA9yifa-YStdfdJwNe7ATs0p-TUCUwvjfcWmHmvsZDEK8VX4I/pub?gid=1326008067'
                '&single=true&output=csv')

S12 = [
    ("md", """# Sesiones 12 y 13 · Centro: moda, mediana y media

**Antes de empezar:** Entorno de ejecución → Cambiar tipo de entorno de ejecución
→ **R**, y después Archivo → Guardar una copia en Drive."""),

    ("md", """## 1 · Los hogares de México

Encuesta Nacional de Ingresos y Gastos de los Hogares (ENIGH) 2024, del INEGI.
Cada renglón es un hogar, sin importar cuántas personas vivan en él. Las columnas
`ingreso` y `gasto` están **en pesos por trimestre**.

El archivo está comprimido y `read_csv()` lo abre igual."""),
    ("code", f'''library(tidyverse)

hogares <- read_csv("{URL_HOGARES}", show_col_types = FALSE)

glimpse(hogares)'''),
    ("md", """La columna `factor` dice a cuántos hogares del país representa cada hogar
visitado. Las cifras calculadas sin factor describen a los hogares visitados; las
que usan el factor describen a los hogares del país.

Antes de seguir, anota tu apuesta: un hogar típico en México, ¿cuánto recibe al
mes?"""),

    ("md", """## 2 · La moda

El valor más frecuente. Es la medida de centro que admite cualquier variable
categórica.

Antes de correr la celda: ¿cuál es la escolaridad más frecuente entre los jefes y
jefas de hogar?"""),
    ("code", """escolaridad <- count(hogares, educa_jefe, sort = TRUE)

escolaridad"""),
    ("code", """ggplot(escolaridad, aes(x = n, y = fct_reorder(educa_jefe, n))) +
  geom_col(fill = "#5A7B5A", alpha = 0.85) +
  geom_text(aes(label = n), hjust = -0.15) +
  scale_x_continuous(expand = expansion(mult = c(0, 0.18))) +
  labs(x = "Hogares visitados", y = NULL)"""),
    ("md", """Con pocos valores posibles, como el número de integrantes, la moda es un valor
exacto. ¿Cuántos integrantes tiene el hogar más frecuente?"""),
    ("code", """count(hogares, integrantes, sort = TRUE)"""),

    ("md", """### Con una variable continua

¿Cuántos hogares crees que coinciden en el mismo ingreso exacto?"""),
    ("code", """length(unique(hogares$ingreso))

sort(table(hogares$ingreso), decreasing = TRUE)[1:3]"""),
    ("md", """El valor exacto que más se repite señala una coincidencia. Para encontrar dónde se
concentran los datos, primero se agrupan en intervalos: el intervalo con más
observaciones es la **clase modal**, y su punto medio es la moda estimada."""),
    ("code", """cortes <- seq(0, 200000, by = 10000)
conteo <- table(cut(hogares$ingreso, breaks = cortes, right = FALSE, dig.lab = 10))

sort(conteo, decreasing = TRUE)[1:3]"""),
    ("code", """i <- which.max(conteo)

moda_clase <- (cortes[i] + cortes[i + 1]) / 2   # punto medio del intervalo
moda_clase"""),
    ("md", """### El ancho decide la moda

Cambia `ancho` a 5000 y después a 20000, y vuelve a correr la celda."""),
    ("code", """ancho <- 10000

cortes_prueba <- seq(0, 300000, by = ancho)
conteo_prueba <- table(cut(hogares$ingreso, breaks = cortes_prueba, right = FALSE, dig.lab = 10))
j <- which.max(conteo_prueba)

(cortes_prueba[j] + cortes_prueba[j + 1]) / 2"""),
    ("md", """Tres anchos, tres modas, y las tres bien calculadas. La moda de una variable
continua se **estima**, y el resultado depende del ancho del intervalo, igual que
la forma del histograma depende de su `binwidth`. Una moda estimada se reporta
junto con el ancho que la produjo.

### Un pico o varios

La estatura de la encuesta del grupo, por género."""),
    ("code", f'''url_grupo <- paste0("{URL_ENCUESTA[:70]}",
                    "{URL_ENCUESTA[70:]}")

estaturas <- read_csv(url_grupo, show_col_types = FALSE) |>
  select(genero = `Género`, estatura = `Estatura, en metros`) |>
  filter(!is.na(estatura))

ggplot(estaturas, aes(x = estatura, fill = genero)) +
  geom_histogram(binwidth = 0.02, boundary = 1.5, color = "white") +
  labs(x = "Estatura del grupo, en metros", y = "Estudiantes", fill = NULL)'''),
    ("md", """Una distribución con un solo pico es **unimodal**; con dos, **bimodal**; con más,
**multimodal**. Aquí cada grupo tiene su propio pico, y un solo número de centro
para todo el grupo cae entre los dos. Cuando una distribución tiene dos picos, la
primera hipótesis es que mezcla dos poblaciones."""),

    ("md", """## 3 · La mediana

Deja la mitad de los hogares debajo y la mitad arriba. Es el segundo cuartil, con
otro uso."""),
    ("code", """median(hogares$ingreso)

quantile(hogares$ingreso, 0.50)"""),
    ("md", """El hogar con mayor ingreso de la base recibe más de 17 millones de pesos en el
trimestre. Antes de correr las celdas: si sale de la base junto con el resto del
1% más alto, ¿cuánto cambia la mediana?"""),
    ("code", """quitados <- filter(hogares, ingreso <= quantile(ingreso, 0.99))

nrow(hogares) - nrow(quitados)     # hogares que salieron

max(hogares$ingreso)
max(quitados$ingreso)"""),
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
    ("md", """La mediana se calcula por posición, y la posición de en medio apenas se recorre.
El eje llega hasta 300,000: `coord_cartesian()` recorta la vista, no los datos."""),

    ("md", """## 4 · La media

Suma todos los valores y reparte el total entre el número de observaciones:

$$\\bar{x} = \\frac{\\sum x_i}{n}$$

Es la única de las tres medidas que usa todos los valores, así que cualquier
valor que entra o sale la mueve."""),
    ("code", """sum(hogares$ingreso) / length(hogares$ingreso)

mean(hogares$ingreso)"""),
    ("code", """mean(hogares$ingreso)
mean(quitados$ingreso)"""),
    ("md", """Las tres medidas sobre el mismo histograma. Verde la moda, azul la mediana, rojo
la media: los tres colores se usan igual en todo el curso."""),
    ("code", """ggplot(filter(hogares, ingreso <= 200000), aes(x = ingreso)) +
  geom_histogram(binwidth = 10000, fill = "#CCCCCC", color = "white", boundary = 0) +
  geom_vline(xintercept = moda_clase, color = "#5A7B5A", linewidth = 1.2) +
  geom_vline(xintercept = median(hogares$ingreso), color = "#3A6B6F", linewidth = 1.2) +
  geom_vline(xintercept = mean(hogares$ingreso), color = "#A4503C", linewidth = 1.2) +
  labs(x = "Ingreso trimestral del hogar, en pesos", y = "Hogares visitados")"""),
    ("md", """¿Por qué quedan en ese orden? Corre la celda: ¿qué porcentaje de los hogares
visitados recibe menos que la media?"""),
    ("code", """mean(hogares$ingreso < mean(hogares$ingreso)) * 100"""),
    ("md", """La media reparte el total entre todos los hogares, así que un ingreso muy alto
sube el promedio sin cambiar la situación de ningún otro hogar. Con una cola
larga a la derecha, la media describe el reparto del total y la mediana describe
al hogar de en medio."""),

    ("md", """## 5 · La media ponderada

Un curso con tres componentes que pesan distinto. La media simple trata igual a
los tres; la media ponderada multiplica cada calificación por su peso:

$$\\bar{x}_w = \\frac{\\sum w_i\\,x_i}{\\sum w_i}$$

**Cambia los pesos y las calificaciones por los de tu curso** y vuelve a correr
la celda. ¿Cuánto se separa tu media ponderada de la simple?"""),
    ("code", """curso <- tibble(
  componente   = c("Primer parcial", "Segundo parcial", "Portafolio"),
  calificacion = c(70, 80, 100),
  peso         = c(0.20, 0.30, 0.50)
)

mean(curso$calificacion)

sum(curso$peso * curso$calificacion) / sum(curso$peso)

weighted.mean(curso$calificacion, curso$peso)"""),

    ("md", """### De la muestra a la población

La **población** son los hogares que había en México en 2024. La **muestra** son
los que la encuesta visitó. Cada hogar visitado representa a un número distinto
de hogares del país, y ese número es su `factor`."""),
    ("code", """nrow(hogares)          # la muestra: hogares visitados

sum(hogares$factor)    # la población: hogares del país

range(hogares$factor)"""),
    ("md", """La muestra se eligió en dos etapas. Primero las zonas del país se agrupan en 1,175
estratos según entidad, tamaño de localidad y nivel socioeconómico; en cada
estrato se sortean conglomerados de 80 a 160 viviendas, y dentro de cada
conglomerado se sortean las viviendas que se visitan. Es una muestra
**probabilística**: cada vivienda tiene una probabilidad conocida de ser elegida.

El factor es el inverso de esa probabilidad. Si una vivienda tenía una
probabilidad de 1 en 400 de ser elegida, se cuenta por 400. Después se ajusta por
las viviendas que no respondieron y para que el total coincida con la estimación
de población del INEGI.

Fuente: INEGI (2025), *ENIGH 2024. Nueva serie. Diseño muestral*, pp. 1 a 8."""),
    ("code", """mean(hogares$ingreso)                           # los hogares visitados

weighted.mean(hogares$ingreso, hogares$factor)  # los hogares del país"""),
    ("md", """La cifra ponderada, 77,864 pesos trimestrales, es la que publica el INEGI.

Un **decil de ingreso** parte al país en diez grupos con el mismo número de
hogares: se ordenan por ingreso, se acumula a cuántos hogares representan, y se
corta cada vez que se junta otro 10%."""),
    ("code", """deciles <- hogares |>
  arrange(ingreso) |>
  mutate(decil = pmin(ceiling(cumsum(factor) / sum(factor) * 10), 10)) |>
  summarise(visitados = n(),
            representa = sum(factor),
            factor_promedio = round(mean(factor)), .by = decil)

deciles"""),
    ("code", """ggplot(deciles, aes(x = decil, y = visitados)) +
  geom_col(fill = "#CCCCCC", width = 0.75) +
  geom_text(aes(label = visitados), vjust = -0.5) +
  scale_x_continuous(breaks = 1:10) +
  labs(x = "Decil de ingreso, del más bajo al más alto", y = "Hogares visitados")"""),
    ("md", """Los diez deciles representan el mismo número de hogares del país, pero para
juntar el decil más bajo hizo falta visitar más hogares que para el más alto. La
muestra tiene proporcionalmente más hogares de ingreso bajo que el país, y el
factor les quita peso.

### La mediana del país

Usa el mismo corte que los deciles, al 50%."""),
    ("code", """mediana_pais <- hogares |>
  arrange(ingreso) |>
  mutate(acumulado = cumsum(factor) / sum(factor)) |>
  filter(acumulado >= 0.5) |>
  slice(1) |>
  pull(ingreso)

mediana_pais
median(hogares$ingreso)    # la de los hogares visitados"""),
    ("md", """Cualquier cifra que hable del país se calcula con el factor: la media, la
mediana, los porcentajes y los conteos.

### El mismo cálculo en otra base

El PIB per cápita promedio de quince países, ¿se calcula sumándolos y dividiendo
entre quince?"""),
    ("code", f'''paises <- read_csv("{URL_PAISES}", show_col_types = FALSE)

ultimo <- filter(paises, anio == max(anio), !is.na(pib_per_capita))

mean(ultimo$pib_per_capita)

weighted.mean(ultimo$pib_per_capita, ultimo$poblacion)'''),
    ("md", """En la ENIGH ponderar subía el promedio; aquí lo baja. El peso corrige hacia lo
que cada observación representa, en la dirección que toque."""),

    ("md", """## 6 · El perfil de Oaxaca

Antes de correr la celda: ordenadas las 32 entidades de menor a mayor ingreso
promedio por hogar, ¿en qué lugar queda Oaxaca?"""),
    ("code", """hogares |>
  summarise(ingreso = weighted.mean(ingreso, factor), .by = entidad) |>
  arrange(ingreso)"""),
    ("code", """oaxaca <- filter(hogares, entidad == "Oaxaca")

mediana_con_factor <- function(x, w) {
  o <- order(x)
  x[o][which(cumsum(w[o]) / sum(w) >= 0.5)[1]]
}

weighted.mean(oaxaca$ingreso, oaxaca$factor)
mediana_con_factor(oaxaca$ingreso, oaxaca$factor)

weighted.mean(hogares$ingreso, hogares$factor)
mediana_pais"""),
    ("md", """Compara las dos proporciones: el promedio de Oaxaca contra el nacional, y la
mediana de Oaxaca contra la nacional. Escribe en tu cuaderno qué dice que sean
parecidas.

Cambia `"Oaxaca"` por otra entidad y vuelve a correr las celdas."""),

    ("md", """## Tarea

Sobre **tu serie del portafolio**:

1. La media y la mediana de tu variable numérica, con sus unidades.
2. Cuál de las dos describe mejor tu serie, con una razón que salga de la forma
   de tu histograma.
3. El porcentaje de tus observaciones que queda debajo de la media.
4. Si tu base trae alguna columna que sirva de peso, la media ponderada y la
   diferencia contra la simple. Si no la trae, qué pesaría si la tuviera.
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
