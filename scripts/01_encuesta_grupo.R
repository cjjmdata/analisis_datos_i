# ---------------------------------------------------------------------------
# Deriva el conjunto anonimizado de la encuesta del grupo.
#
# Entrada:  la hoja de respuestas del formulario (ver
#           scripts/02_encuesta-grupo_apps-script.gs)
# Salida:   datos/encuesta_grupo.csv, que SÍ se versiona
#
# Las respuestas crudas NUNCA entran al repositorio: .gitignore bloquea
# datos/encuesta_cruda* por eso mismo.
#
#   Rscript scripts/01_encuesta_grupo.R
# ---------------------------------------------------------------------------

library(readr)
library(dplyr)

# URL del CSV publicado, o ruta local del archivo descargado.
ORIGEN <- Sys.getenv("ENCUESTA_URL", unset = "datos/encuesta_cruda.csv")

crudos <- read_csv(ORIGEN, show_col_types = FALSE)
n_crudos <- nrow(crudos)

# Google escribe la marca de tiempo en la primera columna y no se puede
# desactivar en el formulario. Se descarta aquí: con el orden de llegada y quién
# estaba en el salón, una marca de tiempo individual vuelve identificable un
# renglón que por lo demás no lo es.
marca <- names(crudos)[1]
if (grepl("marca|timestamp|hora", marca, ignore.case = TRUE)) {
  crudos <- select(crudos, -1)
  message("Descartada la columna de marca de tiempo: ", marca)
}

# Los nombres largos del formulario no sirven para teclear en clase.
grupo <- crudos |>
  rename_with(~ c("carrera", "edad", "estatura", "traslado",
                  "calzado", "numeracion")[seq_along(.x)]) |>
  mutate(
    across(c(edad, estatura, traslado, calzado), as.numeric),
    carrera    = factor(carrera),
    numeracion = factor(numeracion)
  )

# Toda operación que descarta observaciones reporta cuántas descartó.
completos <- grupo |> filter(!is.na(edad), !is.na(estatura), !is.na(traslado))
descartados <- nrow(grupo) - nrow(completos)
if (descartados > 0) {
  message("Renglones con algún dato faltante: ", descartados, " de ", nrow(grupo))
  message("Se conservan de todas formas: los faltantes son tema de la sesión 7.")
}

# El orden de llegada también informa quién contestó primero. Se rompe.
set.seed(1409)
grupo <- grupo[sample(nrow(grupo)), ]

stopifnot(nrow(grupo) == n_crudos)

dir.create("datos", showWarnings = FALSE)
write_csv(grupo, "datos/encuesta_grupo.csv")

message("\nListo: datos/encuesta_grupo.csv (", nrow(grupo), " respuestas)")
message("Carreras: ", paste(levels(grupo$carrera), collapse = " · "))
