"""Arma los cuadernos de Colab de las sesiones 8 y 10.

Los cuadernos se generan desde aquí para que se puedan rehacer y para que el
texto pase por `scripts/lint_redaccion.py` como cualquier otro material.

Uso: python scripts/arma_cuadernos_s08_s10.py
"""

import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent

URL_ENCUESTA = ('https://docs.google.com/spreadsheets/d/e/2PACX-1vTTKC57eWZVIQ9lwhoR5nVqYM4'
                'kgi5zA9yifa-YStdfdJwNe7ATs0p-TUCUwvjfcWmHmvsZDEK8VX4I/pub?gid=1326008067'
                '&single=true&output=csv')
URL_DECILES = ('https://raw.githubusercontent.com/cjjmdata/analisis_datos_i/main/'
               'datos/enigh2024_deciles.csv')

PREPARACION = f'''library(tidyverse)

url <- paste0("{URL_ENCUESTA[:70]}",
              "{URL_ENCUESTA[70:]}")

grupos <- read_csv(url, show_col_types = FALSE) |>
  select(
    carrera  = Carrera,
    genero   = `Género`,
    estatura = `Estatura, en metros`,
    traslado = `Tiempo de traslado a la universidad, en minutos`
  ) |>
  filter(!is.na(traslado), !is.na(estatura))

glimpse(grupos)'''

S08 = [
    ("md", """# Sesión 8 · Histograma y frecuencia acumulada

**Antes de empezar:** Entorno de ejecución → Cambiar tipo de entorno de ejecución
→ **R**, y después Archivo → Guardar una copia en Drive.

Los datos son los de la encuesta que contestaron en la sesión 2."""),

    ("md", "## 1 · Los datos"),
    ("code", PREPARACION),

    ("md", """## 2 · El recorrido

El **rango** es la distancia entre el valor mayor y el menor:

$$R = x_{max} - x_{min}$$

Antes de correr la celda, escribe tu apuesta: ¿cuántos minutos tarda quien más
tarda?"""),
    ("code", """min(grupos$traslado)
max(grupos$traslado)

max(grupos$traslado) - min(grupos$traslado)"""),
    ("code", """# Las dos funciones que hacen lo mismo en una línea
range(grupos$traslado)
diff(range(grupos$traslado))"""),

    ("md", """El rango se calcula con dos datos de todos los que hay. Una sola persona con un
traslado muy largo lo cambia por completo, y el resto del grupo sigue igual.

Para ver dónde está la mayoría, el recorrido se parte por dentro."""),

    ("md", """## 3 · El histograma

Con una variable categórica las categorías vienen dadas. Con una numérica se
fabrican: el recorrido se parte en intervalos del mismo ancho y se cuenta cuántas
observaciones caen en cada uno.

Las barras se tocan porque el eje es continuo: cada barra cubre un tramo."""),
    ("code", """ggplot(grupos, aes(x = traslado)) +
  geom_histogram(binwidth = 10, fill = "#3A6B6F", color = "white", boundary = 0) +
  labs(x = "Minutos de traslado", y = "Estudiantes")"""),

    ("md", """### El ancho es una decisión

Corre las dos celdas siguientes y compara. Son los mismos datos."""),
    ("code", """ggplot(grupos, aes(x = traslado)) +
  geom_histogram(binwidth = 5, fill = "#3A6B6F", color = "white", boundary = 0) +
  labs(title = "binwidth = 5", x = "Minutos de traslado", y = NULL)"""),
    ("code", """ggplot(grupos, aes(x = traslado)) +
  geom_histogram(binwidth = 20, fill = "#3A6B6F", color = "white", boundary = 0) +
  labs(title = "binwidth = 20", x = "Minutos de traslado", y = NULL)"""),
    ("md", """Las dos son correctas. Con intervalos angostos se ve el detalle y también el
ruido; con intervalos anchos se ve la forma general y se pierden los huecos.
Quien elige el ancho elige la historia, así que el ancho se declara junto a la
gráfica."""),

    ("md", """## 4 · Comparar dos grupos

Dos histogramas encimados se tapan. El polígono de frecuencias une los puntos
medios y deja leer los dos a la vez."""),
    ("code", """ggplot(grupos, aes(x = traslado, color = genero)) +
  geom_freqpoly(binwidth = 10, linewidth = 1) +
  labs(x = "Minutos de traslado", y = "Estudiantes", color = NULL)"""),

    ("md", """## 5 · La frecuencia acumulada

El histograma contesta cuántos hay en cada tramo. Esta pregunta es otra:
**¿cuántos llegan en 30 minutos o menos?**

`cumsum()` va sumando lo acumulado hasta cada renglón."""),
    ("code", """grupos |>
  count(traslado) |>
  mutate(
    acumulada  = cumsum(n),
    porcentaje = acumulada / sum(n) * 100
  ) |>
  head(10)"""),
    ("code", """ggplot(grupos, aes(x = traslado)) +
  stat_ecdf(color = "#3A6B6F", linewidth = 1) +
  scale_y_continuous(labels = scales::percent) +
  labs(x = "Minutos de traslado", y = "Porcentaje acumulado")"""),
    ("md", """Para cada valor del eje horizontal, la curva dice qué porcentaje del grupo queda
en ese valor o por debajo. Es la **ojiva** de los libros de texto.

Cambia el umbral y contesta la pregunta con un número:"""),
    ("code", """umbral <- 30

mean(grupos$traslado <= umbral) * 100"""),

    ("md", """## Tarea

Sobre **tu serie del portafolio**:

1. El mínimo, el máximo y el rango de tu variable numérica, con sus unidades.
2. Un histograma con dos anchos distintos, y una línea que diga cuál elegiste y
   por qué.
3. La curva de frecuencia acumulada, y una pregunta de umbral contestada con
   ella: *"el ___% de mis observaciones está en ___ o menos"*.

Si tu variable numérica tiene pocos valores distintos, el histograma va a salir
pobre. Escríbelo en tu cuaderno: es un hallazgo sobre tu fuente.

**Guarda tu copia.**"""),
]

S10 = [
    ("md", """# Sesión 10 · Cuantiles

**Antes de empezar:** Entorno de ejecución → Cambiar tipo de entorno de ejecución
→ **R**, y después Archivo → Guardar una copia en Drive."""),

    ("md", "## 1 · Los datos"),
    ("code", PREPARACION),

    ("md", """## 2 · Primero a mano

Estos son los tiempos de once compañeros, ordenados de menor a mayor.

Antes de calcular: ¿qué valor parte esta lista en dos mitades?"""),
    ("code", """once <- sort(head(grupos$traslado, 11))
once"""),
    ("md", """Un cuartil se localiza primero por su **posición** en la lista ordenada:

$$Q_k = \\frac{k\\,(n+1)}{4}$$

Con 11 datos, el primer cuartil está en la posición $\\frac{1 \\times 12}{4} = 3$,
o sea el tercer dato."""),
    ("code", """n <- length(once)

(n + 1) * 0.25      # la posición
once[3]             # el dato que está en esa posición"""),
    ("code", """# Los tres cortes de una vez
posiciones <- (n + 1) * c(0.25, 0.50, 0.75)
posiciones

once[posiciones]"""),
    ("code", """# Y la función que hace lo mismo
quantile(once, probs = c(0.25, 0.50, 0.75))"""),

    ("md", """### ¿Coinciden siempre?

Con once datos las posiciones cayeron en un dato exacto. Con el grupo completo la
posición cae entre dos datos y el cuantil se interpola."""),
    ("code", """estatura <- sort(grupos$estatura)
m <- length(estatura)

(m + 1) * 0.75      # ya no es un entero"""),
    ("code", """# A mano, interpolando entre los dos datos vecinos
pos <- (m + 1) * 0.75
bajo <- floor(pos)

estatura[bajo] + (pos - bajo) * (estatura[bajo + 1] - estatura[bajo])"""),
    ("code", """# Y lo que devuelve R
quantile(grupos$estatura, 0.75)"""),
    ("md", """**No coinciden.** R tiene nueve definiciones de cuantil. La fórmula $(n+1)p$ que
usamos a mano es el tipo 6; la que R usa por omisión es el tipo 7."""),
    ("code", """x <- c(12, 14, 15, 18, 19, 22, 25, 28, 31, 40)

sapply(1:9, function(t) quantile(x, 0.25, type = t))"""),
    ("md", """En Excel pasa lo mismo: `PERCENTIL.INC` es el tipo 7 y `PERCENTIL.EXC` es el
tipo 6.

Si le preguntas a un modelo de lenguaje cuál es el primer cuartil, vas a recibir
un número sin saber con qué convención se calculó. La pregunta útil es cuál de
las nueve definiciones usó, y si es la misma que usa el resto de tu trabajo."""),

    ("md", """## 3 · Cuartiles, mediana y rango intercuartil"""),
    ("code", """quantile(grupos$traslado, probs = c(0.25, 0.50, 0.75))"""),
    ("md", """El segundo cuartil es la **mediana**: parte al grupo en dos mitades del mismo
tamaño.

$$Q_2 = D_5 = P_{50}$$

El **rango intercuartil** es la distancia entre el primer y el tercer cuartil, o
sea el tramo donde vive la mitad central:

$$RIC = Q_3 - Q_1$$"""),
    ("code", """q <- quantile(grupos$traslado, c(0.25, 0.75))
q[2] - q[1]

IQR(grupos$traslado)"""),

    ("md", """## 4 · Deciles

Nueve cortes. `seq()` los genera sin escribirlos uno por uno."""),
    ("code", """seq(0.1, 0.9, by = 0.1)"""),
    ("code", """quantile(grupos$traslado, probs = seq(0.1, 0.9, by = 0.1))"""),

    ("md", f"""### Los deciles de ingreso de México

Antes de correr la celda: pensando en el ingreso mensual de tu hogar, ¿en cuál de
los diez deciles crees que cae?

La tabla viene de la Encuesta Nacional de Ingresos y Gastos de los Hogares
(ENIGH) 2024 del INEGI. El ingreso se publica trimestral; aquí está dividido
entre tres."""),
    ("code", f'''deciles <- read_csv("{URL_DECILES}", show_col_types = FALSE)

deciles |>
  transmute(
    decil,
    ingreso_mensual = round(mensual),
    hasta           = round(tope_mensual),
    porcentaje_del_ingreso = round(porcentaje_del_ingreso, 1)
  )'''),
    ("md", """El decil dice en qué lugar del reparto cae un hogar. No dice si ese ingreso
alcanza: eso depende de cuántas personas viven de él, de dónde viven y de qué
cuestan ahí las cosas.

El decil X incluye tanto al hogar que recibe 50 mil pesos al mes como al que
recibe millones. Un corte por posición no describe lo que pasa dentro del último
tramo."""),

    ("md", """## 5 · Percentiles

Cien partes, para cuando las diez de los deciles resultan gruesas."""),
    ("code", """quantile(grupos$traslado, probs = c(0.05, 0.90, 0.95, 0.99))"""),
    ("md", """Con este número de respuestas, el percentil 37 y el 38 casi siempre caen entre
los dos mismos datos. El resultado sale con decimales y eso no significa que esté
medido con esa precisión."""),

    ("md", """## 6 · El resumen de cinco números"""),
    ("code", """quantile(grupos$traslado, probs = seq(0, 1, by = 0.25))"""),
    ("md", """Mínimo, $Q_1$, mediana, $Q_3$ y máximo describen la distribución completa con
cinco valores. Son los que dibuja el diagrama de caja de la próxima sesión."""),

    ("md", """## 7 · Tu percentil

Cambia el número por tu propio tiempo de traslado."""),
    ("code", """mi_traslado <- 30

mean(grupos$traslado <= mi_traslado) * 100"""),

    ("md", """## Tarea

Sobre **tu serie del portafolio**:

1. Los cuartiles de tu variable numérica, y una oración que interprete $Q_1$ y
   $Q_3$ con las unidades de tu serie.
2. El rango intercuartil, y qué tramo de tus datos describe.
3. Un percentil que sirva para decidir algo en tu dominio, elegido por ti, con la
   razón de por qué ese y no otro.
4. Una línea sobre qué no dice ese percentil.

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


escribe("s08_histograma-acumulada.ipynb", S08)
escribe("s10_cuantiles.ipynb", S10)
