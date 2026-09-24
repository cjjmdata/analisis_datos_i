# Deciles de ingreso corriente por hogar, ENIGH 2024.
#
# Produce datos/enigh2024_deciles.csv, que usa la sesión 10.
#
# Método de INEGI: los hogares se ordenan por ingreso corriente trimestral, se
# expanden con el factor de la encuesta y se parten en diez grupos con el mismo
# número de hogares expandidos.
#
# El ingreso se publica trimestral. Aquí se agrega la columna mensual porque el
# alumno tiene presente el ingreso mensual de su hogar.
#
# Validado contra la presentación de resultados de INEGI (julio de 2025). El
# promedio nacional está en las pp. 7 y 9; los diez deciles, en la p. 12.
#   ingreso corriente trimestral promedio  77,864 pesos  (aquí: 77,864)
#   diez deciles                           diferencia máxima de 3 pesos, en el X
# La diferencia viene del reparto del hogar que cae justo en el corte entre
# deciles. Verificado el 23 de septiembre de 2026.
#
# Las columnas piso y tope son el menor y el mayor ingreso observado dentro de
# cada decil. INEGI publica los promedios; los límites se calculan aquí.
#
# Fuente: INEGI, Encuesta Nacional de Ingresos y Gastos de los Hogares 2024.
#   https://www.inegi.org.mx/programas/enigh/nc/2024/
#   https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024/doc/enigh2024_ns_presentacion_resultados.pdf
#   https://www.inegi.org.mx/contenidos/saladeprensa/boletines/2025/enigh/ENIGH2024.pdf
#
# Uso: Rscript scripts/02_enigh_deciles.R

library(tidyverse)

URL <- paste0("https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024/",
              "microdatos/enigh2024_ns_concentradohogar_csv.zip")

options(timeout = 600)
tmp <- tempfile(fileext = ".zip")
destino <- file.path(tempdir(), "enigh2024")

message("Descargando ENIGH 2024 ...")
download.file(URL, tmp, mode = "wb", quiet = TRUE)
archivos <- unzip(tmp, exdir = destino)
csv <- archivos[grepl("concentradohogar\\.csv$", archivos)][1]
if (is.na(csv)) stop("El zip no trae concentradohogar.csv")

hogares <- read_csv(csv, show_col_types = FALSE) |>
  select(folioviv, foliohog, ing_cor, factor)

if (nrow(hogares) == 0) stop("La tabla llegó vacía")

deciles <- hogares |>
  arrange(ing_cor) |>
  mutate(decil = pmin(ceiling(cumsum(factor) / sum(factor) * 10), 10)) |>
  group_by(decil) |>
  summarise(
    hogares    = sum(factor),
    trimestral = weighted.mean(ing_cor, factor),
    piso       = min(ing_cor),   # el hogar de menor ingreso dentro del decil
    tope       = max(ing_cor),
    .groups    = "drop"
  ) |>
  mutate(
    mensual      = trimestral / 3,
    piso_mensual = piso / 3,
    tope_mensual = tope / 3,
    porcentaje_del_ingreso = trimestral * hogares / sum(trimestral * hogares) * 100
  )

# Verificación ruidosa: si el promedio nacional se aleja de lo publicado, algo
# cambió en la fuente y la cifra de las láminas dejaría de ser la de INEGI.
promedio <- weighted.mean(hogares$ing_cor, hogares$factor)
message(sprintf("Ingreso trimestral promedio: %s pesos", format(round(promedio), big.mark = ",")))
if (abs(promedio - 77864) > 50) {
  stop("El promedio no coincide con el publicado por INEGI (77,864). Revisar la edición.")
}

write_csv(deciles, "datos/enigh2024_deciles.csv")
message("Escrito datos/enigh2024_deciles.csv")
print(deciles |> mutate(across(where(is.numeric), \(x) round(x, 1))))
