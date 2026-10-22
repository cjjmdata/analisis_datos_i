# Rendimiento de los CETES, serie mensual.
#
# Produce datos/cetes_mensual.csv, para la sesión 14 (media geométrica): el
# rendimiento promedio de una inversión que se reinvierte año con año.
#
# Fuente: Fondo Monetario Internacional, International Financial Statistics,
# serie "Interest Rates, Government Securities, Treasury Bills" de México, en
# porcentaje anual y promedio mensual. Se descarga de FRED (St. Louis Fed), serie
# INTGSTMXM193N, que no pide clave. Los títulos de deuda de corto plazo del
# gobierno de México son los CETES; LA FUENTE NO INDICA EL PLAZO (28, 91, 182 o
# 364 días), así que en las láminas se rotula sin plazo. Si se consigue una clave
# del SIE de Banxico, la serie SF43936 (CETES a 28 días) sustituye a esta con
# plazo conocido.
#
# Falla si la descarga no trae el formato esperado o si faltan meses entre 2000
# y el último año completo: una serie con huecos daría un promedio de otros años.
#
# Uso: Rscript scripts/05_cetes.R

library(tidyverse)

URL   <- "https://fred.stlouisfed.org/graph/fredgraph.csv?id=INTGSTMXM193N"
DESDE <- as.Date("2000-01-01")

# A archivo temporal y con reintentos: la lectura directa de la URL falla a veces
# con un error de HTTP/2 que no se repite al segundo intento
tmp <- tempfile(fileext = ".csv")
for (intento in 1:3) {
  ok <- tryCatch(download.file(URL, tmp, mode = "wb", quiet = TRUE) == 0, error = \(e) FALSE)
  if (ok) break
  Sys.sleep(3)
}
if (!ok) stop("No se pudo descargar ", URL, " en tres intentos")
crudo <- read_csv(tmp, show_col_types = FALSE)
stopifnot(identical(names(crudo), c("observation_date", "INTGSTMXM193N")))

cetes <- crudo |>
  transmute(fecha = as.Date(observation_date),
            tasa_anual = as.numeric(INTGSTMXM193N)) |>
  filter(fecha >= DESDE, !is.na(tasa_anual))

# Cobertura: los doce meses de cada año completo
ultimo_completo <- max(year(cetes$fecha[month(cetes$fecha) == 12]))
esperados <- seq(DESDE, as.Date(sprintf("%d-12-01", ultimo_completo)), by = "month")
faltan <- esperados[!esperados %in% cetes$fecha]
if (length(faltan) > 0) {
  stop("Faltan ", length(faltan), " meses en la serie: ", paste(head(faltan, 10), collapse = ", "))
}
stopifnot(all(cetes$tasa_anual > 0), all(cetes$tasa_anual < 100))

write_csv(cetes, "datos/cetes_mensual.csv")
cat("datos/cetes_mensual.csv:", nrow(cetes), "meses,", format(min(cetes$fecha)), "a",
    format(max(cetes$fecha)), "· años completos hasta", ultimo_completo, "\n")
