// Visualización interactiva de cuantiles para la sesión 10.
//
// Recibe los datos desde R (variable DATOS_CUANTIL, ya ordenada) para que ningún
// número de la lámina se escriba a mano. Dos paneles comparten el eje horizontal:
// arriba, cada respuesta como un punto; abajo, la curva acumulada. Un control
// deslizante mueve la proporción y marca el mismo corte en los dos paneles.
//
// El cuantil se calcula con la misma regla que quantile() de R por omisión
// (tipo 7): posición 1 + (n - 1) p, con interpolación lineal.

(function () {
  const AZUL = "#3A6B6F", GRIS = "#C9CFCF", ROJO = "#A4503C", TINTA = "#24494C";
  const NS = "http://www.w3.org/2000/svg";

  function cuantil(x, p) {
    const h = (x.length - 1) * p, i = Math.floor(h);
    return i + 1 < x.length ? x[i] + (h - i) * (x[i + 1] - x[i]) : x[i];
  }
  const fmt = v => (Math.round(v * 10) / 10).toString();

  function el(tag, attrs, padre) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (padre) padre.appendChild(e);
    return e;
  }

  function montar(caja, datosOriginales) {
    const W = 1000, H = 390, M = { izq: 60, der: 30 };
    const puntosY0 = 25, puntosY1 = 160;          // franja de los puntos
    const curvaY0 = 180, curvaY1 = 335;           // franja de la curva
    let datos = datosOriginales.slice();
    let estirado = false;
    let xmax = Math.max(...datos) * 1.05;

    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", role: "img",
      "aria-label": "Cuantiles de los tiempos de traslado del grupo" }, caja);
    svg.style.fontFamily = "inherit";

    const escX = v => M.izq + (v / xmax) * (W - M.izq - M.der);
    const escCurva = p => curvaY1 - p * (curvaY1 - curvaY0);

    // Ejes
    const eje = el("g", {}, svg);
    const curva = el("path", { fill: "none", stroke: AZUL, "stroke-width": 3 }, svg);
    const hLinea = el("line", { stroke: ROJO, "stroke-width": 2, "stroke-dasharray": "6 5" }, svg);
    const vLinea = el("line", { stroke: ROJO, "stroke-width": 2, "stroke-dasharray": "6 5" }, svg);
    const capaPuntos = el("g", {}, svg);
    const etiquetaP = el("text", { fill: ROJO, "font-size": 20, "font-weight": 700, "text-anchor": "end" }, svg);

    function dibujarEjes() {
      eje.innerHTML = "";
      el("line", { x1: M.izq, x2: W - M.der, y1: curvaY1, y2: curvaY1, stroke: "#888" }, eje);
      el("line", { x1: M.izq, x2: M.izq, y1: curvaY0, y2: curvaY1, stroke: "#888" }, eje);
      const paso = xmax > 300 ? 100 : xmax > 150 ? 50 : 25;
      for (let v = 0; v <= xmax; v += paso) {
        el("text", { x: escX(v), y: curvaY1 + 22, "text-anchor": "middle", "font-size": 18, fill: "#555" }, eje).textContent = v;
      }
      el("text", { x: W / 2, y: H - 2, "text-anchor": "middle", "font-size": 18, fill: "#555" }, eje).textContent = "Minutos de traslado";
      for (const p of [0, 0.5, 1]) {
        el("text", { x: M.izq - 10, y: escCurva(p) + 6, "text-anchor": "end", "font-size": 16, fill: "#555" }, eje).textContent = (p * 100) + "%";
      }
    }

    // Puntos: uno por respuesta, apilados cuando el valor se repite
    const puntos = datos.map(() => {
      const c = el("circle", { r: 4.5, fill: GRIS, stroke: "white", "stroke-width": 1 }, capaPuntos);
      c.style.transition = "cx 1.2s ease, cy 1.2s ease, fill 0.25s";
      return c;
    });

    function posicionesOrdenadas() {
      const pila = {};
      return datos.map(v => {
        pila[v] = (pila[v] || 0) + 1;
        return { cx: escX(v), cy: puntosY1 - (pila[v] - 1) * 9.5 };
      });
    }
    function colocar(pos) { puntos.forEach((c, i) => { c.setAttribute("cx", pos[i].cx); c.setAttribute("cy", pos[i].cy); }); }
    function desordenar() {
      colocar(datos.map(() => ({ cx: M.izq + Math.random() * (W - M.izq - M.der), cy: puntosY0 + Math.random() * (puntosY1 - puntosY0) })));
    }

    function dibujarCurva() {
      const n = datos.length;
      let d = `M ${escX(0)} ${escCurva(0)}`;
      datos.forEach((v, i) => {
        d += ` L ${escX(v)} ${escCurva(i / n)} L ${escX(v)} ${escCurva((i + 1) / n)}`;
      });
      d += ` L ${escX(xmax)} ${escCurva(1)}`;
      curva.setAttribute("d", d);
    }

    // Controles
    const panel = document.createElement("div");
    panel.style.cssText = "display:flex;align-items:center;gap:0.8em;flex-wrap:wrap;font-size:0.55em;margin-top:0.2em;";
    panel.innerHTML = `
      <label style="display:flex;align-items:center;gap:0.5em;">Proporción
        <input type="range" min="1" max="99" value="25" style="width:18em;"></label>
      <button data-p="25">Q1</button><button data-p="50">Mediana</button><button data-p="75">Q3</button>
      <button data-accion="ordenar">Ordenar de nuevo</button>
      <button data-accion="estirar">Alargar el máximo</button>`;
    caja.appendChild(panel);
    const lectura = document.createElement("div");
    lectura.style.cssText = "font-size:0.5em;color:" + TINTA + ";margin-top:0.3em;";
    caja.appendChild(lectura);
    panel.querySelectorAll("button").forEach(b => {
      b.style.cssText = "font:inherit;padding:0.15em 0.7em;border:1px solid " + AZUL + ";background:white;color:" + AZUL + ";border-radius:4px;cursor:pointer;";
    });
    const deslizador = panel.querySelector("input");

    function actualizar() {
      const p = deslizador.value / 100;
      const q = cuantil(datos, p);
      const debajo = datos.filter(v => v <= q).length;
      puntos.forEach((c, i) => c.setAttribute("fill", datos[i] <= q ? AZUL : GRIS));
      hLinea.setAttribute("x1", M.izq); hLinea.setAttribute("x2", escX(q));
      hLinea.setAttribute("y1", escCurva(p)); hLinea.setAttribute("y2", escCurva(p));
      vLinea.setAttribute("x1", escX(q)); vLinea.setAttribute("x2", escX(q));
      vLinea.setAttribute("y1", puntosY0 - 10); vLinea.setAttribute("y2", curvaY1);
      etiquetaP.setAttribute("x", escX(q) - 8); etiquetaP.setAttribute("y", puntosY0 + 4);
      etiquetaP.textContent = fmt(q) + " min";
      const cuart = [0.25, 0.5, 0.75].map(pp => fmt(cuantil(datos, pp)));
      lectura.innerHTML =
        `El <b>${deslizador.value}%</b> queda debajo de <b>${fmt(q)} minutos</b> ` +
        `(${debajo} de ${datos.length} respuestas). ` +
        `Q1 = ${cuart[0]} · mediana = ${cuart[1]} · Q3 = ${cuart[2]} · RIC = ${fmt(cuantil(datos, 0.75) - cuantil(datos, 0.25))} · máximo = ${fmt(datos[datos.length - 1])}`;
    }

    function redibujar() { dibujarEjes(); colocar(posicionesOrdenadas()); dibujarCurva(); actualizar(); }

    deslizador.addEventListener("input", actualizar);
    panel.querySelectorAll("button[data-p]").forEach(b =>
      b.addEventListener("click", () => { deslizador.value = b.dataset.p; actualizar(); }));
    panel.querySelector('[data-accion="ordenar"]').addEventListener("click", () => {
      desordenar(); setTimeout(() => colocar(posicionesOrdenadas()), 60);
    });
    panel.querySelector('[data-accion="estirar"]').addEventListener("click", ev => {
      estirado = !estirado;
      datos = datosOriginales.slice();
      if (estirado) datos[datos.length - 1] = datos[datos.length - 1] * 5;
      xmax = Math.max(...datos) * 1.05;
      ev.target.textContent = estirado ? "Regresar el máximo" : "Alargar el máximo";
      redibujar();
    });

    // Arranca desordenado; se ordena cuando la lámina aparece en pantalla
    dibujarEjes(); dibujarCurva(); desordenar(); actualizar();
    let yaOrdenado = false;
    function alMostrar() {
      if (yaOrdenado) return;
      yaOrdenado = true;
      setTimeout(() => { colocar(posicionesOrdenadas()); actualizar(); }, 300);
    }
    return alMostrar;
  }

  function iniciar() {
    const caja = document.getElementById("cuantil-animado");
    if (!caja || typeof DATOS_CUANTIL === "undefined") return;
    const alMostrar = montar(caja, DATOS_CUANTIL);
    const visible = () => {
      const s = window.Reveal && Reveal.getCurrentSlide && Reveal.getCurrentSlide();
      if (!s || s.contains(caja)) alMostrar();
    };
    if (window.Reveal && Reveal.on) {
      Reveal.on("ready", visible);
      Reveal.on("slidechanged", visible);
    }
    visible();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", iniciar);
  else iniciar();
})();
