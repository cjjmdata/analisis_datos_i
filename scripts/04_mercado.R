# Serie diaria de mercado: TSLA y AAPL desde 2015.
#
# Produce datos/mercado_diario.csv, la serie de tiempo de las sesiones 15 a 17
# y 28: dispersión, forma de la distribución y la curva normal.
#
# Fuente: Yahoo Finance, a través de quantmod. No usa clave ni tiene cupo.
# Se evaluó Alpha Vantage y se descartó para el diario: con clave gratuita
# `outputsize=full` es función de paga y solo entrega los últimos 100 días.
# Stooq bloquea las descargas por script con un reto JavaScript.
#
# EL PRECIO AJUSTADO ES EL QUE SIRVE PARA RENDIMIENTOS. TSLA partió su acción
# en 2020 y en 2022; con el precio sin ajustar, esos días aparecen como caídas
# de 66% y 80% que nunca ocurrieron. Por eso se guardan las dos columnas y la
# validación de abajo rechaza el archivo si el ajuste falta.
#
# Uso: Rscript scripts/04_mercado.R

library(tidyverse)
library(quantmod)

EMISORAS <- c("TSLA", "AAPL")
DESDE    <- "2015-01-01"

baja <- function(simbolo) {
  serie <- getSymbols(simbolo, src = "yahoo", from = DESDE,
                      auto.assign = FALSE, warnings = FALSE)
  tibble(
    clave    = simbolo,
    fecha    = as.Date(index(serie)),
    apertura = as.numeric(Op(serie)),
    maximo   = as.numeric(Hi(serie)),
    minimo   = as.numeric(Lo(serie)),
    cierre   = as.numeric(Cl(serie)),
    ajustado = as.numeric(Ad(serie)),
    volumen  = as.numeric(Vo(serie))
  )
}

message("Descargando ", paste(EMISORAS, collapse = " y "), " desde ", DESDE, " ...")
mercado <- map(EMISORAS, baja) |> list_rbind() |> arrange(clave, fecha)

# Validación 1: cobertura. Doce años de historia no caben en menos de 2,000 días
por_emisora <- count(mercado, clave)
message("Días por emisora: ",
        paste(por_emisora$clave, por_emisora$n, sep = " = ", collapse = " · "))
if (any(por_emisora$n < 2000)) {
  stop("Alguna emisora trae menos de 2,000 días. La descarga quedó incompleta.")
}

# Validación 2: el ajuste por splits. Un rendimiento diario de más de 40% en el
# precio ajustado delata que el ajuste no se aplicó
saltos <- mercado |>
  mutate(rendimiento = ajustado / lag(ajustado) - 1, .by = clave) |>
  filter(abs(rendimiento) > 0.4)
if (nrow(saltos) > 0) {
  print(saltos |> select(clave, fecha, ajustado, rendimiento))
  stop("Hay saltos mayores a 40% en el precio ajustado: revisar el ajuste por splits.")
}

if (anyNA(mercado$ajustado)) stop("Hay precios ajustados faltantes.")

write_csv(mercado, "datos/mercado_diario.csv")
message("Escrito datos/mercado_diario.csv: ",
        format(nrow(mercado), big.mark = ","), " renglones, ",
        round(file.size("datos/mercado_diario.csv") / 1e6, 2), " MB, ",
        "de ", min(mercado$fecha), " a ", max(mercado$fecha))
