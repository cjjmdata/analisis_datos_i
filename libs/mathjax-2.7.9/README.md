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
