"""Arma el cuaderno de Colab de la sesión 11.

Mismo patrón que `arma_cuadernos_s08_s10.py`: el cuaderno se genera desde aquí
para que se pueda rehacer y para que el texto pase por `lint_redaccion.py` como
cualquier otro material.

Uso: python scripts/arma_cuaderno_s11.py
"""

import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent

URL_ENCUESTA = ('https://docs.google.com/spreadsheets/d/e/2PACX-1vTTKC57eWZVIQ9lwhoR5nVqYM4'
                'kgi5zA9yifa-YStdfdJwNe7ATs0p-TUCUwvjfcWmHmvsZDEK8VX4I/pub?gid=1326008067'
                '&single=true&output=csv')
URL_PAISES = ('https://raw.githubusercontent.com/cjjmdata/analisis_datos_i/main/'
              'datos/banco_mundial.csv')

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

S11 = [
    ("md", """# Sesión 11 · Diagrama de caja

**Antes de empezar:** Entorno de ejecución → Cambiar tipo de entorno de ejecución
→ **R**, y después Archivo → Guardar una copia en Drive."""),

    ("md", "## 1 · Los datos"),
    ("code", PREPARACION),

    ("md", """## 2 · Los cinco números, dibujados

La sesión pasada terminó con estos cinco valores."""),
    ("code", """quantile(grupos$traslado, probs = seq(0, 1, by = 0.25))"""),
    ("code", """ggplot(grupos, aes(x = traslado)) +
  geom_boxplot(fill = "#3A6B6F", alpha = 0.35, width = 0.5) +
  scale_y_continuous(NULL, breaks = NULL) +
  labs(x = "Minutos de traslado")"""),
    ("md", """Compara el extremo derecho del bigote con el máximo de la lista de arriba. No
son el mismo número.

El bigote no llega al máximo porque la caja aplica una regla antes de dibujarlo."""),

    ("md", """## 3 · Primero a mano

Los once tiempos de la sesión pasada, más el compañero que más tarda."""),
    ("code", """doce <- sort(c(head(grupos$traslado, 11), max(grupos$traslado)))
doce"""),
    ("md", """La regla mide la distancia en **rangos intercuartiles**, contados desde los
bordes de la caja:

$$RIC = Q_3 - Q_1$$

$$\\text{cerca inferior} = Q_1 - 1.5\\,RIC \\qquad
\\text{cerca superior} = Q_3 + 1.5\\,RIC$$

Lo que cae fuera de las cercas se marca."""),
    ("code", """q <- quantile(doce, probs = c(0.25, 0.75))
ric <- q[2] - q[1]
ric"""),
    ("code", """q[2] + 1.5 * ric      # cerca superior
q[1] - 1.5 * ric      # cerca inferior"""),
    ("code", """doce[doce > q[2] + 1.5 * ric]     # los que pasan la cerca"""),
    ("md", """El bigote no llega hasta la cerca: llega hasta el último dato que todavía cae
dentro."""),
    ("code", """max(doce[doce <= q[2] + 1.5 * ric])"""),
    ("code", """# La caja que dibuja R con esos mismos doce datos
ggplot(tibble(minutos = doce), aes(x = minutos)) +
  geom_boxplot(fill = "#3A6B6F", alpha = 0.35, width = 0.5) +
  scale_y_continuous(NULL, breaks = NULL) +
  labs(x = "Minutos de traslado")"""),

    ("md", """## 4 · El factor 1.5 es una convención

Cambia el valor de `k` y corre la celda otra vez. Con `k = 0` queda marcada media
base; con `k = 3` casi nunca se marca nada.

El 1.5 lo propuso John Tukey en 1977 y está calibrado para que, cuando no pasa
nada raro, casi nada quede fuera. No es una prueba estadística."""),
    ("code", """k <- 1.5

cerca_sup <- quantile(grupos$traslado, 0.75) + k * IQR(grupos$traslado)
cerca_inf <- quantile(grupos$traslado, 0.25) - k * IQR(grupos$traslado)

sum(grupos$traslado > cerca_sup | grupos$traslado < cerca_inf)"""),
    ("md", """Una regla que midiera la distancia al centro en desviaciones estándar tendría un
problema: el dato extremo infla la desviación estándar y termina escondiéndose a
sí mismo. El rango intercuartil se calcula por posición y no se deja arrastrar.

Corre la celda: el máximo se multiplica por cinco y solo una de las dos medidas
se mueve."""),
    ("code", """extremo <- grupos$traslado
extremo[which.max(extremo)] <- max(extremo) * 5

IQR(grupos$traslado)
IQR(extremo)

sd(grupos$traslado)
sd(extremo)"""),

    ("md", """## 5 · Comparar grupos

Una caja por carrera. La variable categórica va en el eje vertical."""),
    ("code", """ggplot(grupos, aes(x = traslado, y = carrera)) +
  geom_boxplot(fill = "#3A6B6F", alpha = 0.35) +
  labs(x = "Minutos de traslado", y = NULL)"""),
    ("code", """ggplot(grupos, aes(x = traslado, y = genero)) +
  geom_boxplot(fill = "#3A6B6F", alpha = 0.35) +
  labs(x = "Minutos de traslado", y = NULL)"""),
    ("md", """Compara los puntos sueltos de las tres gráficas: la del grupo completo, la de
carreras y la de géneros. Son los mismos datos y no queda marcada la misma gente.

Ser atípico no es una propiedad del dato. Es una propiedad de la comparación: una
observación es atípica **respecto de un grupo**, y ese grupo se nombra."""),

    ("md", """## 6 · Decidir qué hacer

Ante un punto marcado, cuatro preguntas:

1. ¿Es un error de captura? Se corrige y se documenta.
2. ¿Está en otra unidad, horas contra minutos? Se convierte.
3. ¿Pertenece a otra población? Se separa, y se dice que se separó.
4. ¿Es el fenómeno real? Se queda, y muchas veces es el hallazgo.

Ninguna de las cuatro respuestas es borrar el dato en silencio. Si decides sacar
observaciones, la cuenta de cuántas sacaste va en el cuaderno."""),
    ("code", """cerca <- quantile(grupos$traslado, 0.75) + 1.5 * IQR(grupos$traslado)

sin_marcados <- filter(grupos, traslado <= cerca)

nrow(grupos) - nrow(sin_marcados)     # cuántas se quedaron fuera"""),
    ("code", """median(grupos$traslado)
median(sin_marcados$traslado)

max(grupos$traslado)
max(sin_marcados$traslado)"""),
    ("md", """Quitar las marcadas no arregla los datos: cambia la pregunta que estás
contestando. Con todas describes a quienes contestaron; sin ellas describes a
quienes tardan menos que la cerca. Las dos respuestas sirven; lo que no sirve es
entregar la segunda diciendo que describe a todo el grupo."""),

    ("md", f"""## 7 · La misma técnica en otra base

Inflación anual de quince países, del snapshot del Banco Mundial que ya usaron en
la sesión 1."""),
    ("code", f'''paises <- read_csv("{URL_PAISES}", show_col_types = FALSE)

paises_con_inflacion <- filter(paises, !is.na(inflacion))

nrow(paises) - nrow(paises_con_inflacion)   # años sin dato'''),
    ("code", """ggplot(paises_con_inflacion, aes(x = inflacion, y = pais)) +
  geom_boxplot(fill = "#3A6B6F", alpha = 0.35) +
  labs(x = "Inflación anual, en porcentaje", y = NULL)"""),
    ("md", """No se ve nada: un solo año manda sobre todo el eje. Para poder ver el resto se
saca ese tramo de **la gráfica**, no de la base, y se reporta cuántos años se
sacaron."""),
    ("code", """moderada <- filter(paises_con_inflacion, inflacion < 40)

nrow(paises_con_inflacion) - nrow(moderada)"""),
    ("code", """ggplot(moderada, aes(x = inflacion, y = fct_reorder(pais, inflacion, median))) +
  geom_boxplot(fill = "#3A6B6F", alpha = 0.35) +
  labs(x = "Inflación anual, en porcentaje", y = NULL)"""),
    ("md", """Las cajas van ordenadas por mediana. Con el orden alfabético la gráfica se lee
peor y no dice nada.

Ahora los años que la regla marca en México."""),
    ("code", """mexico <- filter(paises_con_inflacion, pais == "México")

cerca_mexico <- quantile(mexico$inflacion, 0.75) + 1.5 * IQR(mexico$inflacion)

filter(mexico, inflacion > cerca_mexico)"""),
    ("md", """Esos años no se corrigen ni se quitan: son la crisis de 1994 y lo que vino
después. En una serie de negocio, el punto marcado suele ser justo el que pide
explicación."""),

    ("md", """## Tarea

Sobre **tu serie del portafolio**:

1. El diagrama de caja de tu variable numérica, con los cinco números al lado.
2. La cerca superior e inferior calculadas, y cuántas observaciones quedan fuera.
3. Para cada observación marcada, la decisión con las cuatro preguntas: qué es y
   qué hiciste. Si no puedes averiguarlo, escribe que no pudiste.
4. Una caja segmentada por alguna variable categórica de tu base, y una línea
   sobre si la segmentación cambió quién queda marcado.
5. Una línea sobre lo que tu caja no muestra.

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


escribe("s11_diagrama-caja.ipynb", S11)
