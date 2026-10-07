# Perfil de los hogares, ENIGH 2024, concentrado por hogar.
#
# Produce datos/enigh2024_hogares.csv, la base transversal de las sesiones 12 a
# 18: centro, dispersión, forma y comparación de grupos.
#
# Del archivo original se conservan 16 de las 126 columnas. Las categóricas
# vienen etiquetadas en el .sav y se convierten a factor con sus niveles, como
# pide la convención del proyecto. La ubicación se recorta a entidad: el curso
# compara Oaxaca contra el país y no necesita municipio.
#
# Prueba de aceptación: el ingreso corriente trimestral promedio ponderado por
# el factor de expansión tiene que dar 77,864 pesos, que es la cifra publicada
# por INEGI. Si no coincide, el script falla y no escribe nada.
#   https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024/doc/enigh2024_ns_presentacion_resultados.pdf
#
# Fuente: INEGI, Encuesta Nacional de Ingresos y Gastos de los Hogares 2024.
#   https://www.inegi.org.mx/programas/enigh/nc/2024/
#
# Uso: Rscript scripts/03_enigh_hogares.R

library(tidyverse)
library(haven)

URL <- paste0("https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024/",
              "microdatos/enigh2024_ns_concentradohogar_sav.zip")

# Nombres de las 32 entidades, en el orden de su clave oficial. Catálogo de
# INEGI; no es un resultado del análisis.
ENTIDADES <- c(
  "Aguascalientes", "Baja California", "Baja California Sur", "Campeche",
  "Coahuila", "Colima", "Chiapas", "Chihuahua", "Ciudad de México", "Durango",
  "Guanajuato", "Guerrero", "Hidalgo", "Jalisco", "México", "Michoacán",
  "Morelos", "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro",
  "Quintana Roo", "San Luis Potosí", "Sinaloa", "Sonora", "Tabasco",
  "Tamaulipas", "Tlaxcala", "Veracruz", "Yucatán", "Zacatecas")

stopifnot(length(ENTIDADES) == 32, ENTIDADES[20] == "Oaxaca")

options(timeout = 900)
tmp <- tempfile(fileext = ".zip")
destino <- file.path(tempdir(), "enigh2024_sav")

message("Descargando ENIGH 2024, concentrado por hogar ...")
download.file(URL, tmp, mode = "wb", quiet = TRUE)
archivos <- unzip(tmp, exdir = destino)
sav <- archivos[grepl("\\.sav$", archivos, ignore.case = TRUE)][1]
if (is.na(sav)) stop("El zip no trae ningún .sav: ", paste(basename(archivos), collapse = ", "))

crudos <- read_sav(sav)
message("Leídas ", format(nrow(crudos), big.mark = ","), " filas y ", ncol(crudos), " columnas")

faltantes <- setdiff(
  c("ubica_geo", "tam_loc", "est_socio", "clase_hog", "sexo_jefe", "edad_jefe",
    "educa_jefe", "tot_integ", "perc_ocupa", "ing_cor", "gasto_mon", "alimentos",
    "transporte", "remesas", "factor"),
  names(crudos))
if (length(faltantes) > 0) stop("Faltan columnas en el origen: ", paste(faltantes, collapse = ", "))

hogares <- crudos |>
  mutate(
    clave_entidad = substr(as.character(ubica_geo), 1, 2),
    entidad       = factor(ENTIDADES[as.integer(clave_entidad)], levels = ENTIDADES),
    tam_loc       = as_factor(tam_loc),
    est_socio     = as_factor(est_socio),
    clase_hog     = as_factor(clase_hog),
    sexo_jefe     = as_factor(sexo_jefe),
    educa_jefe    = as_factor(educa_jefe),
    across(c(edad_jefe, tot_integ, perc_ocupa, factor), as.numeric),
    # Los importes vienen con centavos, que son precisión que la encuesta no
    # tiene. Redondear a pesos también quita 1.4 MB al archivo.
    across(c(ing_cor, gasto_mon, alimentos, transporte, remesas),
           \(x) round(as.numeric(x))),
    # El rótulo original de tam_loc ocupa 40 caracteres en cada uno de los
    # 91,414 renglones. Se acorta conservando los cortes de INEGI.
    tam_loc = fct_recode(
      tam_loc,
      "100 mil y más"   = "Localidades con 100 000 y más habitantes",
      "15 mil a 99 999" = "Localidades con 15 000 a 99 999 habitantes",
      "2 500 a 14 999"  = "Localidades con 2 500 a 14 999 habitantes",
      "menos de 2 500"  = "Localidades con menos de 2 500 habitantes")
  ) |>
  select(entidad, tam_loc, est_socio, clase_hog, sexo_jefe, edad_jefe, educa_jefe,
         integrantes = tot_integ, perceptores = perc_ocupa,
         ingreso = ing_cor, gasto = gasto_mon, alimentos, transporte, remesas,
         factor)

# Prueba de aceptación contra la cifra publicada
promedio <- weighted.mean(hogares$ingreso, hogares$factor)
message("Ingreso corriente trimestral promedio: ", format(round(promedio), big.mark = ","))
if (abs(promedio - 77864) > 50) {
  stop("El promedio ponderado da ", round(promedio),
       " y la cifra publicada por INEGI es 77,864. El archivo de origen cambió.")
}
if (anyNA(hogares$entidad)) stop("Hay hogares sin entidad: revisar ubica_geo")

# Se escribe comprimido: en texto plano son 9.7 MB que el repositorio cargaría
# para siempre. read_csv() lo abre igual, también desde una URL, y leer un .gz
# ya es contenido de curso/referencia-r.qmd.
write_csv(hogares, "datos/enigh2024_hogares.csv.gz")
message("Escrito datos/enigh2024_hogares.csv.gz: ",
        format(nrow(hogares), big.mark = ","), " hogares, ",
        ncol(hogares), " columnas, ",
        round(file.size("datos/enigh2024_hogares.csv.gz") / 1e6, 1), " MB")
