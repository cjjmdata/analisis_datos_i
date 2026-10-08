# Colores del curso, para que una medida se vea igual en todas las sesiones.
#
# Las tres medidas de centro tienen color propio y no se intercambian: el alumno
# aprende a leer la línea por su color antes que por su etiqueta.
#
# Uso desde una presentación: source("../../R/colores.R")

# Paleta del sitio, derivada de STA 210
TEAL_900 <- "#24494C"
TEAL_700 <- "#3A6B6F"
TEAL_500 <- "#5B888C"
TEAL_100 <- "#D9E3E4"
SALMON   <- "#B4704F"
BRICK    <- "#A4503C"
SAGE     <- "#5A7B5A"
GRIS     <- "#CCCCCC"
TINTA    <- "#34425A"

# Las tres medidas de centro
col_media   <- BRICK     # ladrillo
col_mediana <- TEAL_700  # verde azulado
col_moda    <- SAGE      # verde

# Usos generales dentro de las gráficas
col_datos    <- GRIS     # las observaciones, cuando no son el protagonista
col_destaca  <- BRICK    # el caso que la lámina señala
col_apoyo    <- TEAL_700 # curvas y trazos del análisis

# Para comparar dos grupos. Deliberadamente distintos de los tres de arriba:
# un color de medida nunca debe aparecer nombrando una categoría.
col_grupos <- c("#5B888C", "#E0A890")
