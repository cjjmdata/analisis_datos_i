# Esperanza de vida y acceso a electricidad en todas las economías del mundo.
#
# Produce datos/banco_mundial_economias.csv, para la sesión 17 (forma): las dos
# variables reales del curso con sesgo a la izquierda. Ninguna variable de
# hogares, mercado ni de los 15 países de banco_mundial.csv lo tiene.
#
# Va en un script propio y no en 00_descarga_datos.R: volver a correr ese script
# re-descarga banco_mundial.csv, y el Banco Mundial revisa cifras hacia atrás.
# Cambiarían los números de las sesiones ya publicadas y de los exámenes
# generados con ese archivo.
#
# Fuente: API de indicadores del Banco Mundial, sin token ni registro.
#   SP.DYN.LE00.IN  Esperanza de vida al nacer, total (años)
#   EG.ELC.ACCS.ZS  Acceso a la electricidad (% de la población)
# Un corte transversal: un renglón por economía, un solo año.
#
# Las respuestas de `country/all` traen también agregados (regiones, grupos de
# ingreso, "Mundo"). Se quitan con el catálogo de países: un agregado tiene
# región "NA". Sin ese filtro, "Mundo" y "América Latina" entran como si fueran
# países y cambian la forma de la distribución.
#
# Falla si alguna descarga no responde o si la cobertura baja del mínimo: una
# distribución a la que le faltan los países más pobres tiene otra forma.
#
# Uso: Rscript scripts/06_banco-mundial_economias.R

library(jsonlite)
library(dplyr)
library(readr)

options(timeout = 20)

ANIO <- 2024                 # último año con cobertura completa al congelar
MIN_ECONOMIAS <- 210         # de 217; por debajo, el script se detiene

indicadores <- c(
  esperanza_vida      = "SP.DYN.LE00.IN",
  acceso_electricidad = "EG.ELC.ACCS.ZS"
)

# Una petición con reintentos y espera creciente (ver notas de campo en
# 00_descarga_datos.R: la API estrangula ráfagas y devuelve respuestas vacías)
pedir <- function(url, intentos = 4) {
  for (intento in seq_len(intentos)) {
    r <- try(fromJSON(url, flatten = TRUE), silent = TRUE)
    if (!inherits(r, "try-error") && length(r) >= 2 &&
        is.data.frame(r[[2]]) && nrow(r[[2]]) > 0) {
      Sys.sleep(0.5)
      return(r[[2]])
    }
    Sys.sleep(5 * intento)
  }
  stop("Sin respuesta después de ", intentos, " intentos: ", url)
}

# Catálogo de economías, con nombre, región y grupo de ingreso en español
catalogo <- pedir("https://api.worldbank.org/v2/es/country?format=json&per_page=400") |>
  filter(region.id != "NA") |>
  transmute(iso = id, pais = name,
            region = trimws(region.value), grupo_ingreso = trimws(incomeLevel.value))
message("Economías en el catálogo: ", nrow(catalogo))

bajar <- function(nombre, codigo) {
  url <- sprintf(paste0("https://api.worldbank.org/v2/es/country/all/indicator/%s",
                        "?format=json&per_page=400&date=%d"), codigo, ANIO)
  pedir(url) |>
    transmute(iso = countryiso3code, !!nombre := as.numeric(value)) |>
    filter(iso %in% catalogo$iso)
}

series <- Map(bajar, names(indicadores), indicadores)

economias <- Reduce(function(a, b) left_join(a, b, by = "iso"), series, catalogo) |>
  mutate(anio = ANIO, .after = grupo_ingreso) |>
  arrange(pais)

# Cobertura antes de escribir
message("\nCobertura en ", ANIO, ":")
for (v in names(indicadores)) {
  con_dato <- sum(!is.na(economias[[v]]))
  sin_dato <- economias$pais[is.na(economias[[v]])]
  message(sprintf("  %-20s %d de %d economías%s", v, con_dato, nrow(economias),
                  if (length(sin_dato) > 0) paste0("  (sin dato: ", paste(sin_dato, collapse = ", "), ")") else ""))
  if (con_dato < MIN_ECONOMIAS) {
    stop(v, ": solo ", con_dato, " economías con dato en ", ANIO, "; mínimo ", MIN_ECONOMIAS)
  }
}

# Rangos posibles: años de vida y porcentaje
stopifnot(all(between(economias$esperanza_vida, 30, 95), na.rm = TRUE),
          all(between(economias$acceso_electricidad, 0, 100), na.rm = TRUE))

write_csv(economias, "datos/banco_mundial_economias.csv")
message("\nListo: datos/banco_mundial_economias.csv (", nrow(economias), " economías, año ", ANIO, ")")
