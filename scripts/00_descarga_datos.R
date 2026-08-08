# ---------------------------------------------------------------------------
# Descarga y congela los datos compartidos del curso.
#
# Se ejecuta UNA VEZ por semestre. Las sesiones leen los archivos que este
# script deja en datos/; nunca descargan en vivo. Ver AGENTS.md, decisión 4.
#
#   Rscript scripts/00_descarga_datos.R
# ---------------------------------------------------------------------------

library(jsonlite)
library(dplyr)
library(tidyr)
library(readr)

dir.create("datos", showWarnings = FALSE)

# ---------------------------------------------------------------------------
# Banco Mundial · API de indicadores
#
# Es la única fuente del catálogo verificada de punta a punta sin token ni
# registro (ver datos/catalogo.qmd). Por eso sostiene la sesión 1: en el
# primer día nada puede fallar.
#
# Una petición por INDICADOR, con `country/all`, y el filtro por país se hace
# en local. La versión anterior pedía país × indicador —60 peticiones— y la
# API estrangulaba la ráfaga: se perdieron 4 países y el 64% de la serie de
# población, sin aviso. Así son 4 peticiones y ~4 segundos.
# ---------------------------------------------------------------------------

paises <- c(
  MEX = "México",        USA = "Estados Unidos", CAN = "Canadá",
  BRA = "Brasil",        ARG = "Argentina",      CHL = "Chile",
  COL = "Colombia",      PER = "Perú",           CRI = "Costa Rica",
  ESP = "España",        DEU = "Alemania",       JPN = "Japón",
  KOR = "Corea del Sur", CHN = "China",          IND = "India"
)

indicadores <- c(
  pib_per_capita   = "NY.GDP.PCAP.CD",  # US$ corrientes
  exportaciones_pc = "NE.EXP.GNFS.ZS",  # % del PIB
  poblacion        = "SP.POP.TOTL",
  inflacion        = "FP.CPI.TOTL.ZG"   # % anual
)

anio_min <- 1990
anio_max <- 2025

# Baja una serie (un país, un indicador).
#
# Notas de campo, por si esto vuelve a fallar:
#
#  - Una petición por país-indicador. Pedir `country/all` en una sola llamada
#    parecía más elegante, pero la API da timeout con respuestas grandes.
#  - Se usa `jsonlite::fromJSON(url)`, NO el paquete `curl`. En Windows con
#    Schannel, `curl_fetch_memory()` falló en las 60 series; `fromJSON` sobre
#    el URL responde en ~0.3 s.
#  - La pausa entre peticiones no es cortesía: sin ella la API estrangula la
#    ráfaga y devuelve series vacías. Sin reintentos se perdieron 4 países y
#    el 64% de una serie, y el archivo resultante parecía correcto.
bajar_serie <- function(iso, codigo, intentos = 3) {
  url <- sprintf(
    paste0("https://api.worldbank.org/v2/country/%s/indicator/%s",
           "?format=json&per_page=500&date=%d:%d"),
    iso, codigo, anio_min, anio_max
  )

  for (intento in seq_len(intentos)) {
    respuesta <- try(fromJSON(url, flatten = TRUE), silent = TRUE)

    # La API devuelve [metadatos, datos].
    if (!inherits(respuesta, "try-error") && length(respuesta) >= 2) {
      datos <- respuesta[[2]]
      if (is.data.frame(datos) && nrow(datos) > 0) {
        Sys.sleep(0.5)
        return(tibble(
          iso   = iso,
          anio  = as.integer(datos$date),
          valor = as.numeric(datos$value)
        ) |> filter(!is.na(valor)))
      }
    }
    Sys.sleep(intento)
  }

  NULL  # agotados los intentos; el llamador lo detecta
}

# Baja un indicador para los 15 países del curso.
bajar_indicador <- function(nombre, codigo) {
  partes <- lapply(names(paises), function(iso) bajar_serie(iso, codigo))
  faltan <- names(paises)[vapply(partes, is.null, logical(1))]

  if (length(faltan) > 0) {
    message(sprintf("  %-16s FALLA en: %s", nombre, paste(faltan, collapse = ", ")))
    return(NULL)
  }

  resultado <- bind_rows(partes)
  message(sprintf("  %-16s %d registros, %d países",
                  nombre, nrow(resultado), length(unique(resultado$iso))))
  rename(resultado, !!nombre := valor)
}

message("Descargando del Banco Mundial (",
        length(paises) * length(indicadores), " series)...")

series <- Map(bajar_indicador, names(indicadores), indicadores)

# Truncamiento silencioso = archivo que parece bueno y no lo es.
fallos <- names(series)[vapply(series, is.null, logical(1))]
if (length(fallos) > 0) {
  stop("No se pudieron descargar estos indicadores: ",
       paste(fallos, collapse = ", "),
       "\nVuelve a ejecutar el script.")
}

# Una fila por país-año, una columna por indicador: la forma que los alumnos
# van a manipular en clase.
banco_mundial <- Reduce(function(a, b) full_join(a, b, by = c("iso", "anio")),
                        series) |>
  mutate(pais = unname(paises[iso]), .after = iso) |>
  arrange(pais, anio)

# Verificación de cobertura antes de escribir. Mejor enterarse aquí que en clase.
faltantes <- setdiff(unname(paises), unique(banco_mundial$pais))
if (length(faltantes) > 0) {
  stop("Faltan países en el resultado final: ", paste(faltantes, collapse = ", "))
}

message("\nCobertura por indicador:")
for (v in names(indicadores)) {
  message(sprintf("  %-16s %.0f%%", v, 100 * mean(!is.na(banco_mundial[[v]]))))
}

write_csv(banco_mundial, "datos/banco_mundial.csv")

message("\nListo: datos/banco_mundial.csv (", nrow(banco_mundial), " filas, ",
        length(unique(banco_mundial$pais)), " países, ",
        min(banco_mundial$anio), "-", max(banco_mundial$anio), ")")

# ---------------------------------------------------------------------------
# Pendientes de agregar conforme avancen las unidades:
#
#   - Profeco "Quién es Quién en los Precios" (datos.gob.mx, CC-BY-4.0)
#     → unidad 3, dispersión de precios del mismo producto entre tiendas
#   - INEGI ENIGH, con factores de expansión
#     → unidad 3, media ponderada y deciles de ingreso
#   - Serie de precios accionarios
#     → unidad 3, media geométrica
#     OJO: Stooq bloquea descargas por script. Usar quantmod/Yahoo.
# ---------------------------------------------------------------------------
