# ---------------------------------------------------------------------------
# Lectura de datos con fuente en vivo y respaldo local.
#
# El curso lee de la fuente original cada vez que se abre un material. Si la
# fuente no responde, usa el respaldo congelado que vive en datos/.
#
# En los dos casos informa cuál se usó: la procedencia del dato es parte del
# resultado, no un detalle de implementación.
#
#   source("R/datos.R")
# ---------------------------------------------------------------------------

#' Intenta una fuente en vivo y cae al respaldo si falla.
#'
#' @param en_vivo   función sin argumentos que devuelve un data frame
#' @param respaldo  ruta al CSV congelado en el repositorio
#' @param espera    segundos antes de rendirse con la fuente en vivo
#'
#' @return data frame con el atributo `origen`, que dice de dónde salió
con_respaldo <- function(en_vivo, respaldo, espera = 20) {
  anterior <- options(timeout = espera)
  on.exit(options(anterior), add = TRUE)

  intento <- try(suppressWarnings(en_vivo()), silent = TRUE)

  sirve <- !inherits(intento, "try-error") &&
    is.data.frame(intento) && nrow(intento) > 0

  if (sirve) {
    attr(intento, "origen") <- "fuente en vivo"
    return(intento)
  }

  if (!file.exists(respaldo)) {
    stop("La fuente en vivo falló y no hay respaldo en ", respaldo)
  }

  datos <- readr::read_csv(respaldo, show_col_types = FALSE)
  fecha <- format(file.mtime(respaldo), "%d/%m/%Y")
  attr(datos, "origen") <- paste("respaldo del", fecha)
  datos
}

#' Frase corta que dice de dónde vinieron los datos.
#'
#' Se imprime en las presentaciones para que la procedencia quede a la vista.
origen <- function(datos) {
  o <- attr(datos, "origen")
  if (is.null(o)) "origen no declarado" else o
}

# ---------------------------------------------------------------------------
# Fuentes del curso
# ---------------------------------------------------------------------------

#' Indicadores del Banco Mundial para los 15 países del curso.
leer_paises <- function(respaldo = "datos/banco_mundial.csv") {
  con_respaldo(
    en_vivo = function() {
      paises <- c("MEX", "USA", "CAN", "BRA", "ARG", "CHL", "COL", "PER",
                  "CRI", "ESP", "DEU", "JPN", "KOR", "CHN", "IND")
      indicadores <- c(pib_per_capita   = "NY.GDP.PCAP.CD",
                       exportaciones_pc = "NE.EXP.GNFS.ZS",
                       poblacion        = "SP.POP.TOTL",
                       inflacion        = "FP.CPI.TOTL.ZG")

      una <- function(iso, codigo) {
        url <- sprintf(paste0("https://api.worldbank.org/v2/country/%s/",
                              "indicator/%s?format=json&per_page=500&date=1990:2025"),
                       iso, codigo)
        r <- jsonlite::fromJSON(url, flatten = TRUE)
        if (length(r) < 2 || !is.data.frame(r[[2]])) return(NULL)
        d <- r[[2]]
        data.frame(iso = iso, anio = as.integer(d$date),
                   valor = as.numeric(d$value))
      }

      series <- lapply(names(indicadores), function(nombre) {
        partes <- lapply(paises, function(iso) una(iso, indicadores[[nombre]]))
        if (any(vapply(partes, is.null, logical(1)))) return(NULL)
        out <- do.call(rbind, partes)
        out <- out[!is.na(out$valor), ]
        names(out)[names(out) == "valor"] <- nombre
        out
      })

      if (any(vapply(series, is.null, logical(1)))) return(NULL)
      Reduce(function(a, b) merge(a, b, by = c("iso", "anio"), all = TRUE), series)
    },
    respaldo = respaldo
  )
}

#' Precios diarios de una emisora de la Bolsa Mexicana de Valores.
#'
#' Claves de ejemplo: "BIMBOA.MX", "WALMEX.MX", "FEMSAUBD.MX", "CEMEXCPO.MX".
leer_emisora <- function(clave, respaldo = NULL, rango = "5y") {
  if (is.null(respaldo)) {
    respaldo <- file.path("datos", paste0("emisora_", tolower(sub("\\..*", "", clave)), ".csv"))
  }

  con_respaldo(
    en_vivo = function() {
      url <- sprintf("https://query1.finance.yahoo.com/v8/finance/chart/%s?range=%s&interval=1d",
                     clave, rango)
      r <- jsonlite::fromJSON(url, flatten = TRUE)
      res <- r$chart$result
      if (is.null(res) || nrow(res) == 0) return(NULL)

      # Con flatten = TRUE los campos anidados quedan con nombre punteado:
      # `indicators.quote`, no `indicators$quote`. Es el error clásico al
      # parsear esta API desde R.
      cotizacion <- res$indicators.quote[[1]]

      data.frame(
        clave  = clave,
        fecha  = as.Date(as.POSIXct(res$timestamp[[1]], origin = "1970-01-01", tz = "UTC")),
        cierre = as.numeric(cotizacion$close[[1]])
      ) |> subset(!is.na(cierre))
    },
    respaldo = respaldo
  )
}
