# MathJax 2.7.9, copia local

Copia del paquete oficial `mathjax@2.7.9` (npm), licencia Apache 2.0 (`LICENSE`).
Es la versión que Quarto usa por omisión en las presentaciones. Se guarda aquí
para que las fórmulas se vean aunque el salón no tenga internet.

Solo se conservan los archivos que usa la configuración `TeX-AMS_HTML-full`:
núcleo, configuración, entrada TeX, salida HTML-CSS con la fuente TeX (woff y
otf), extensiones y traducción al español.

Uso en una presentación, dentro de `format: revealjs:`

    html-math-method:
      method: mathjax
      url: "../../libs/mathjax-2.7.9/MathJax.js"

## Salida SVG (desde 2026-11-19)

Las presentaciones dibujan las fórmulas en SVG, no en HTML-CSS. Con HTML-CSS,
MathJax usa fuentes: si el navegador no carga sus fuentes web, o encuentra las
fuentes STIX del sistema (pasó en macOS con Firefox), dibuja con otra fuente y la
barra de la media queda despegada de la x. En SVG cada símbolo es un trazo y se ve
igual en cualquier navegador.

- Se agregaron `jax/output/SVG` (solo la fuente TeX) y
  `config/TeX-AMS_SVG-full.js`, del mismo paquete `mathjax@2.7.9`.
- Quarto fija `config: 'TeX-AMS_HTML-full'` en su plantilla de revealjs, así que
  el cambio de salida lo hace `salida-svg.html`, que cada presentación incluye:

      include-in-header: ../../libs/mathjax-2.7.9/salida-svg.html
