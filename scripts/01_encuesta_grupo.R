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

# La marca de tiempo se conserva: no hay identificador con el que cruzarla, y
# sirve para ver el orden de llegada. Solo se normaliza el nombre de la columna.
marca <- names(crudos)[1]
if (grepl("marca|timestamp|hora", marca, ignore.case = TRUE)) {
  names(crudos)[1] <- "momento"
  message("Marca de tiempo conservada, renombrada a 'momento'.")
}

# Los nombres largos del formulario no sirven para teclear en clase.
# Se seleccionan por nombre y no por posición: la hoja de respuestas de Google
# es acumulativa, así que al editar el formulario las columnas quedan en un orden
# que ya no es el del cuestionario.
grupo <- crudos |>
  select(
    momento,
    genero   = starts_with("Género"),
    carrera  = starts_with("Carrera"),
    edad     = starts_with("Edad"),
    estatura = starts_with("Estatura"),
    traslado = starts_with("Tiempo de traslado"),
    calzado  = starts_with("Número de calzado")
  ) |>
  mutate(
    across(c(edad, estatura, traslado, calzado), as.numeric),
    carrera = factor(carrera),
    genero  = factor(genero)
  )

# Toda operación que descarta observaciones reporta cuántas descartó.
completos <- grupo |> filter(!is.na(edad), !is.na(estatura), !is.na(traslado))
descartados <- nrow(grupo) - nrow(completos)
if (descartados > 0) {
  message("Renglones con algún dato faltante: ", descartados, " de ", nrow(grupo))
  message("Se conservan de todas formas: los faltantes son tema de la sesión 7.")
}

# Se ordena por momento de respuesta, que es el orden natural del registro.
grupo <- arrange(grupo, momento)

stopifnot(nrow(grupo) == n_crudos)

dir.create("datos", showWarnings = FALSE)
write_csv(grupo, "datos/encuesta_grupo.csv")

message("\nListo: datos/encuesta_grupo.csv (", nrow(grupo), " respuestas)")
message("Carreras: ", paste(levels(grupo$carrera), collapse = " · "))
