# ---------------------------------------------------------------------------
# Valor al pasar el cursor sobre los puntos de una gráfica de ggplot.
#
# Dibuja la gráfica en PNG, calcula con grid dónde quedó cada punto dentro de
# la imagen y pone encima zonas transparentes con el texto en data-valor. El
# texto aparece solo con CSS (.puntos-info en estilo-slides.scss): no hace falta
# ningún paquete interactivo, funciona sin internet y las posiciones van en
# porcentajes, así que resisten el escalado de revealjs.
#
# Uso en una lámina, en un chunk con echo: false y output: asis:
#   source("../../R/puntos-info.R")
#   puntos_info(p, capa = 2, textos = ..., clave_x = ..., ancho = 5.2, alto = 5.1)
# ---------------------------------------------------------------------------

#' @param p        la gráfica de ggplot, tal como se ve en la lámina
#' @param capa     número de la capa de geom_point() dentro de p
#' @param textos   lo que aparece al pasar el cursor, uno por punto
#' @param clave_x  valores de x en el mismo orden que `textos`; sirven para
#'                 emparejar cada texto con su punto
#' @param ancho, alto  medidas de la figura en pulgadas (fig-width, fig-height)
#' @param lineas_x, textos_lineas  líneas verticales con su propio texto
#' @param alt      texto alternativo de la imagen
#' @param dpi      192 es lo que usa Quarto para estas láminas (pantalla retina)
puntos_info <- function(p, capa, textos, clave_x, ancho, alto,
                        lineas_x = NULL, textos_lineas = NULL,
                        alt = "", dpi = 192) {
  archivo <- tempfile(fileext = ".png")
  png(archivo, width = ancho, height = alto, units = "in", res = dpi)
  print(p)

  # Rangos del panel: convierten un valor de los datos a su lugar en el panel
  rangos <- ggplot2::ggplot_build(p)$layout$panel_params[[1]]
  a_npc <- \(v, r) (v - r[1]) / diff(r)

  # Del panel a la imagen completa, en pulgadas desde la esquina inferior izquierda
  grid::grid.force()
  vps <- grid::grid.ls(viewports = TRUE, grobs = FALSE, print = FALSE)$name
  grid::seekViewport(grep("^panel", vps, value = TRUE)[1])
  en_imagen <- function(x_npc, y_npc) {
    loc <- grid::deviceLoc(grid::unit(x_npc, "npc"), grid::unit(y_npc, "npc"),
                           valueOnly = TRUE)
    list(izq = loc$x / ancho * 100, arriba = (1 - loc$y / alto) * 100)
  }

  d <- ggplot2::layer_data(p, capa)
  pos <- en_imagen(a_npc(d$x, rangos$x.range), a_npc(d$y, rangos$y.range))
  texto_punto <- textos[match(d$x, clave_x)]
  stopifnot(!anyNA(texto_punto))

  borde <- en_imagen(c(0, 0), c(1, 0))      # arriba y abajo del panel
  lin <- if (length(lineas_x)) en_imagen(a_npc(lineas_x, rangos$x.range), rep(1, length(lineas_x)))
  dev.off()

  # Los puntos de la mitad derecha muestran el texto a su izquierda
  span <- \(clase, izq, estilo, texto)
    sprintf('<span class="%s%s" style="left:%.2f%%;%s" data-valor="%s"></span>',
            clase, ifelse(izq > 60, " izq", ""), izq, estilo,
            htmltools::htmlEscape(texto, attribute = TRUE))
  puntos <- span("punto", pos$izq, sprintf("top:%.2f%%", pos$arriba), texto_punto)
  lineas <- if (length(lineas_x))
    span("linea", lin$izq,
         sprintf("top:%.2f%%;height:%.2f%%", borde$arriba[1], borde$arriba[2] - borde$arriba[1]),
         textos_lineas)

  ancho_px <- round(ancho * 96)
  html <- c("```{=html}",
            sprintf('<div class="puntos-info" style="width:%dpx">', ancho_px),
            sprintf('<img src="%s" width="%d" alt="%s">', knitr::image_uri(archivo), ancho_px,
                    htmltools::htmlEscape(alt, attribute = TRUE)),
            lineas, puntos, "</div>", "```")
  knitr::asis_output(paste(html, collapse = "\n"))
}
