# ---------------------------------------------------------------------------
# Profeco · Quién es Quién en los Precios
#
# La fuente publica un CSV por quincena de ~150 MB con todos los productos del
# país. Este script baja una quincena y recorta un subconjunto docente: los
# productos de la canasta básica que se usan en clase.
#
# El recorte se hace por bloques para no cargar 150 MB en memoria.
#
#   Rscript scripts/01_profeco.R
#
# Licencia de la fuente: CC-BY-4.0. Catálogo en datos.gob.mx.
# ---------------------------------------------------------------------------

library(readr)
library(dplyr)

dir.create("datos", showWarnings = FALSE)

BASE <- paste0("https://repodatos.atdt.gob.mx/api_update/profeco/",
               "programa_quien_es_quien_precios_2025/")
QUINCENAS <- c("11-2025_01.csv", "11-2025_02.csv")

# Productos de canasta básica. Se eligen porque todos los alumnos los conocen
# y porque son comparables entre tiendas: mismo producto, misma presentación.
PRODUCTOS <- c("Aceite", "Arroz", "Atún", "Azúcar", "Detergente para ropa",
               "Frijol", "Huevo", "Leche ultrapasteurizada", "Papel higiénico",
               "Pasta para sopa")

TIPOS <- cols(
  producto = col_character(), presentacion = col_character(),
  marca = col_character(), categoria = col_character(),
  catalogo = col_character(), precio = col_double(),
  fecha_registro = col_character(), cadena_comercial = col_character(),
  giro = col_character(), nombre_comercial = col_character(),
  direccion = col_character(), estado = col_character(),
  municipio = col_character(), latitud = col_double(), longitud = col_double()
)

filtrar <- function(bloque, pos) {
  bloque |>
    filter(producto %in% PRODUCTOS, !is.na(precio), precio > 0) |>
    select(producto, presentacion, marca, categoria, precio, fecha_registro,
           cadena_comercial, giro, estado, municipio)
}

partes <- list()

for (q in QUINCENAS) {
  url <- paste0(BASE, q)
  tmp <- tempfile(fileext = ".csv")
  message("Descargando ", q, " ...")

  ok <- try(download.file(url, tmp, quiet = TRUE, mode = "wb"), silent = TRUE)
  if (inherits(ok, "try-error")) {
    unlink(tmp)
    stop("No se pudo descargar ", q, ". Vuelve a intentarlo.")
  }

  message("  recortando por bloques ...")
  partes[[q]] <- read_csv_chunked(
    tmp, DataFrameCallback$new(filtrar),
    chunk_size = 200000, col_types = TIPOS, progress = FALSE
  )
  unlink(tmp)
  message("  ", nrow(partes[[q]]), " registros conservados")
}

precios <- bind_rows(partes) |>
  mutate(fecha_registro = as.Date(fecha_registro, format = "%Y/%m/%d")) |>
  arrange(producto, estado, cadena_comercial)

# Verificación de cobertura antes de escribir.
faltan <- setdiff(PRODUCTOS, unique(precios$producto))
if (length(faltan) > 0) {
  warning("Sin registros para: ", paste(faltan, collapse = ", "))
}
stopifnot(nrow(precios) > 0)

write_csv(precios, "datos/precios_profeco.csv")

message("\nListo: datos/precios_profeco.csv")
message("  ", nrow(precios), " registros | ",
        length(unique(precios$producto)), " productos | ",
        length(unique(precios$cadena_comercial)), " cadenas | ",
        length(unique(precios$estado)), " estados")
message("  periodo: ", min(precios$fecha_registro), " a ", max(precios$fecha_registro))
message("  tamaño: ", round(file.size("datos/precios_profeco.csv") / 1e6, 1), " MB")
