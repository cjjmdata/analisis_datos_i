"""Arma el cuaderno resuelto de la parte 2 del segundo parcial (segunda vuelta) para Oaxaca.

Oaxaca no se asignó a ningún alumno en el examen: el cuaderno sirve de modelo de
respuesta. Mismo patrón que `arma_cuaderno_s12.py`. Las cifras de "lo que debes
obtener" se calculan aquí desde la ENIGH, no se teclean.

Uso: python scripts/arma_cuaderno_p02v2_oaxaca.py
"""

import json
import pathlib

import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parent.parent
ENTIDAD = "Oaxaca"
URL_HOGARES = ('https://raw.githubusercontent.com/cjjmdata/analisis_datos_i/main/'
               'datos/enigh2024_hogares.csv.gz')

gasto = pd.read_csv(RAIZ / "datos" / "enigh2024_hogares.csv.gz").query("entidad == @ENTIDAD")["gasto"].to_numpy(float)
n = len(gasto)
q1, mediana, q3 = np.quantile(gasto, [0.25, 0.50, 0.75])   # tipo 7, el de quantile() en R
ric = q3 - q1
cerca = q3 + 1.5 * ric
arriba = int((gasto > cerca).sum())
media = gasto.mean()
debajo = 100 * (gasto < media).mean()
assert n > 0 and debajo > 50


def pesos(x):
    return f"{x:,.2f}".replace(".00", "")


CELDAS = [
    ("md", f"""# Segundo parcial, segunda vuelta · Parte 2 resuelta para {ENTIDAD}

{ENTIDAD} no le tocó a nadie en el examen: aquí está la parte 2 completa para que
compares tu procedimiento con el de tu entidad. Cada cifra sale de una celda.

**Antes de empezar:** Entorno de ejecución → Cambiar tipo de entorno de ejecución
→ **R**, y después Archivo → Guardar una copia en Drive."""),

    ("md", """## Preparación

La misma celda del examen, con la entidad ya escrita. Si `nrow()` diera cero, el
nombre no está escrito igual que en la base: revisa acentos y mayúsculas."""),
    ("code", f'''library(tidyverse)
url_hogares <- paste0("https://raw.githubusercontent.com/",
                      "cjjmdata/analisis_datos_i/main/datos/enigh2024_hogares.csv.gz")
hogares <- read_csv(url_hogares, show_col_types = FALSE)
mi_entidad <- filter(hogares, entidad == "{ENTIDAD}")'''),

    ("md", """## C1 · ¿Cuántos hogares visitados tiene la entidad?

Cada renglón de `mi_entidad` es un hogar visitado, así que la respuesta es el
número de renglones."""),
    ("code", "nrow(mi_entidad)"),
    ("md", f"""**Lo que debes obtener:** {n:,} hogares."""),

    ("md", """## C2 · Cuartiles y rango intercuartil del gasto

`quantile()` da los tres cuartiles de una vez. El rango intercuartil es la
distancia entre el tercero y el primero: donde está la mitad central de los
hogares."""),
    ("code", """cuartiles <- quantile(mi_entidad$gasto, c(0.25, 0.50, 0.75))
cuartiles

ric <- cuartiles[3] - cuartiles[1]   # lo mismo que IQR(mi_entidad$gasto)
ric"""),
    ("md", f"""**Lo que debes obtener:** $Q_1$ = {pesos(q1)}, mediana = {pesos(mediana)},
$Q_3$ = {pesos(q3)} y rango intercuartil = {pesos(ric)} pesos al trimestre."""),

    ("md", """## C3 · Cerca superior y hogares arriba de ella

La cerca superior del diagrama de caja es $Q_3 + 1.5 \\times RIC$. Los hogares que la
pasan son los puntos sueltos a la derecha de la caja.

`mi_entidad$gasto > cerca` marca con `TRUE` a cada hogar arriba de la cerca, y
`sum()` cuenta los `TRUE`."""),
    ("code", """cerca <- cuartiles[3] + 1.5 * ric
cerca

sum(mi_entidad$gasto > cerca)"""),
    ("md", f"""**Lo que debes obtener:** cerca superior = {pesos(cerca)} pesos y {arriba}
hogares arriba de ella. Contar con `>=` en lugar de `>` daría el mismo número en
{ENTIDAD}: ningún hogar cae justo en la cerca."""
        if arriba == int((gasto >= cerca).sum()) else
        f"""**Lo que debes obtener:** cerca superior = {pesos(cerca)} pesos y {arriba}
hogares arriba de ella."""),

    ("md", """## C4 · La media y el porcentaje de hogares debajo de ella

`mean()` de una comparación da la proporción de `TRUE`: por 100, el porcentaje."""),
    ("code", """media <- mean(mi_entidad$gasto)
media

mean(mi_entidad$gasto < media) * 100"""),
    ("md", f"""**Lo que debes obtener:** media = {pesos(round(media, 2))} pesos y
{debajo:.1f}% de los hogares gasta menos que ella."""),

    ("md", f"""## C5 · ¿La media describe al hogar típico?

Un reporte afirma: *"El hogar típico de {ENTIDAD} gasta {pesos(round(media))} pesos al
trimestre"*.

**¿La media describe al hogar típico?** No.

**¿Por qué?** El {debajo:.1f}% de los hogares gasta menos que la media: bastante más
de la mitad. Unos cuantos hogares con gasto muy alto la jalan hacia arriba, y
queda por encima de lo que gasta la mayoría.

**Qué medida usarías y su valor:** la mediana, {pesos(mediana)} pesos. Deja la
mitad de los hogares de cada lado y no la mueven los gastos extremos.

**Algo que no se puede saber con la media ni con la mediana.** Cualquiera de estas
respuestas vale:

- Qué tan distintos son los gastos entre hogares: la dispersión. Dos entidades
  con la misma mediana pueden tener hogares muy parecidos o muy desiguales.
- En qué se va el gasto: comida, renta, transporte.
- Cuántas personas viven de ese gasto: no es lo mismo un hogar de una persona
  que uno de seis.
- Que describen a los hogares **visitados**, no a todos los hogares de {ENTIDAD}:
  para eso hace falta el factor de expansión."""),

    ("md", """## Para comparar con tu examen

1. Si una cifra tuya no coincide, revisa primero que hayas usado `gasto` y no
   `ingreso`, y que el filtro tenga tu entidad.
2. La cerca usa $Q_3$ y el rango intercuartil, no la mediana.
3. El porcentaje de C4 compara contra la **media**, no contra la mediana: contra
   la mediana siempre daría alrededor de 50%."""),
]


def celda(tipo, fuente):
    lineas = fuente.split("\n")
    fuente_ipynb = [l + "\n" for l in lineas[:-1]] + [lineas[-1]]
    if tipo == "md":
        return {"cell_type": "markdown", "metadata": {}, "source": fuente_ipynb}
    return {"cell_type": "code", "execution_count": None, "metadata": {},
            "outputs": [], "source": fuente_ipynb}


nb = {
    "cells": [celda(t, s) for t, s in CELDAS],
    "metadata": {
        "kernelspec": {"display_name": "R", "language": "R", "name": "ir"},
        "language_info": {"name": "R"},
        "colab": {"provenance": []},
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}
destino = RAIZ / "cuadernos" / "p02v2_parte2_oaxaca.ipynb"
destino.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{destino.name}: {len(CELDAS)} celdas · {n} hogares · media {media:.2f} · {debajo:.1f}% debajo")
