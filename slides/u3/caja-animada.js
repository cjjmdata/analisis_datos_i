// Construcción paso a paso del diagrama de caja para la sesión 11.
//
// Recibe los datos desde R (variable DATOS_CAJA, ya ordenada) para que ningún
// número de la lámina se escriba a mano. Arriba, cada respuesta como un punto;
// abajo, la caja que se va armando. Los dos paneles comparten el eje horizontal.
//
// Los cuartiles se calculan con la misma regla que quantile() de R por omisión
// (tipo 7): posición 1 + (n - 1) p, con interpolación lineal. Así la caja del
// applet y la que dibuja geom_boxplot() coinciden.
//
// El deslizador cambia el factor que multiplica al rango intercuartil. Se mueve
// para que el grupo vea que 1.5 es una convención, no un resultado.

(function () {
  const AZUL = "#3A6B6F", GRIS = "#C9CFCF", ROJO = "#A4503C", TINTA = "#24494C";
  const NS = "http://www.w3.org/2000/svg";

  const PASOS = [
    "1 · Las respuestas, una por punto",
    "2 · La caja: del primer al tercer cuartil",
    "3 · La mediana parte la caja",
    "4 · Las cercas: Q1 − k·RIC y Q3 + k·RIC",
    "5 · Los bigotes llegan al dato más lejano que queda dentro",
  ];

  function cuantil(x, p) {
    const h = (x.length - 1) * p, i = Math.floor(h);
    return i + 1 < x.length ? x[i] + (h - i) * (x[i + 1] - x[i]) : x[i];
  }
  const fmt = v => (Math.round(v * 100) / 100).toString();

  function el(tag, attrs, padre) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (padre) padre.appendChild(e);
    return e;
  }

  function montar(caja, datosOriginales) {
    const W = 1000, H = 340, M = { izq: 45, der: 45 };
    const puntosY = 160;                       // línea base de los puntos
    const cajaY = 215, cajaAlto = 54;          // franja de la caja
    const ejeY = 292;
    let datos = datosOriginales.slice();
    let paso = 1;
    let k = 1.5;
    let estirado = false;
    let xmax = Math.max(...datos) * 1.06;

    const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, width: "100%", role: "img",
      "aria-label": "Construcción del diagrama de caja de los tiempos de traslado" }, caja);
    svg.style.fontFamily = "inherit";

    const escX = v => M.izq + (v / xmax) * (W - M.izq - M.der);

    const eje = el("g", {}, svg);
    const capaCaja = el("g", {}, svg);
    const capaPuntos = el("g", {}, svg);
    const rotulo = el("text", { x: M.izq, y: 26, "font-size": 19, "font-weight": 700, fill: TINTA }, svg);

    // Un círculo por respuesta; se apilan cuando el valor se repite
    const puntos = datos.map(() => {
      const c = el("circle", { r: 4.5, fill: GRIS, stroke: "white", "stroke-width": 1 }, capaPuntos);
      c.style.transition = "cx 0.6s ease, cy 0.6s ease, fill 0.3s";
      return c;
    });

    function dibujarEjes() {
      eje.innerHTML = "";
      el("line", { x1: M.izq, x2: W - M.der, y1: ejeY, y2: ejeY, stroke: "#888" }, eje);
      const paso_eje = xmax > 300 ? 100 : xmax > 150 ? 25 : 10;
      for (let v = 0; v <= xmax; v += paso_eje) {
        el("line", { x1: escX(v), x2: escX(v), y1: ejeY, y2: ejeY + 6, stroke: "#888" }, eje);
        el("text", { x: escX(v), y: ejeY + 24, "text-anchor": "middle", "font-size": 17, fill: "#555" }, eje)
          .textContent = v;
      }
      el("text", { x: W / 2, y: H - 4, "text-anchor": "middle", "font-size": 17, fill: "#555" }, eje)
        .textContent = "Minutos de traslado";
    }

    function colocarPuntos() {
      const pila = {};
      datos.forEach((v, i) => {
        pila[v] = (pila[v] || 0) + 1;
        puntos[i].setAttribute("cx", escX(v));
        puntos[i].setAttribute("cy", puntosY - (pila[v] - 1) * 10);
      });
    }

    function texto(x, y, contenido, color, ancla) {
      const t = el("text", { x: x, y: y, "text-anchor": ancla || "middle",
        "font-size": 16, fill: color || TINTA }, capaCaja);
      t.textContent = contenido;
      return t;
    }

    function dibujarCaja(q1, med, q3, cercaInf, cercaSup, bigoteInf, bigoteSup) {
      capaCaja.innerHTML = "";
      const y0 = cajaY - cajaAlto / 2, y1 = cajaY + cajaAlto / 2;

      if (paso >= 2) {
        el("rect", { x: escX(q1), y: y0, width: escX(q3) - escX(q1), height: cajaAlto,
          fill: AZUL, "fill-opacity": 0.3, stroke: AZUL, "stroke-width": 2 }, capaCaja);
        texto(escX(q1), y0 - 8, "Q1 = " + fmt(q1), AZUL);
        texto(escX(q3), y0 - 8, "Q3 = " + fmt(q3), AZUL);
      }
      if (paso >= 3) {
        el("line", { x1: escX(med), x2: escX(med), y1: y0, y2: y1, stroke: AZUL, "stroke-width": 4 }, capaCaja);
        texto(escX(med), y1 + 20, "mediana = " + fmt(med), AZUL);
      }
      if (paso >= 4) {
        for (const c of [cercaInf, cercaSup]) {
          if (c < 0 || c > xmax) continue;
          el("line", { x1: escX(c), x2: escX(c), y1: 40, y2: y1 + 6, stroke: ROJO,
            "stroke-width": 2, "stroke-dasharray": "7 5" }, capaCaja);
          texto(escX(c), 56, "cerca " + fmt(c), ROJO);
        }
      }
      if (paso >= 5) {
        el("line", { x1: escX(bigoteInf), x2: escX(q1), y1: cajaY, y2: cajaY, stroke: AZUL, "stroke-width": 2 }, capaCaja);
        el("line", { x1: escX(q3), x2: escX(bigoteSup), y1: cajaY, y2: cajaY, stroke: AZUL, "stroke-width": 2 }, capaCaja);
        for (const b of [bigoteInf, bigoteSup]) {
          el("line", { x1: escX(b), x2: escX(b), y1: y0 + 12, y2: y1 - 12, stroke: AZUL, "stroke-width": 2 }, capaCaja);
        }
        texto(escX(bigoteSup), y1 + 20, "bigote = " + fmt(bigoteSup), AZUL);
      }
    }

    // Controles
    const panel = document.createElement("div");
    panel.style.cssText = "display:flex;align-items:center;gap:0.7em;flex-wrap:wrap;font-size:0.5em;margin-top:0.1em;";
    panel.innerHTML = `
      <button data-accion="anterior">◀ Paso</button>
      <button data-accion="siguiente">Paso ▶</button>
      <label style="display:flex;align-items:center;gap:0.4em;">Factor k
        <input type="range" min="0" max="3" step="0.1" value="1.5" style="width:12em;"></label>
      <button data-accion="uno-cinco">Regresar a 1.5</button>
      <button data-accion="estirar">Alargar el máximo</button>`;
    caja.appendChild(panel);
    const lectura = document.createElement("div");
    lectura.style.cssText = "font-size:0.46em;color:" + TINTA + ";margin-top:0.25em;line-height:1.5;";
    caja.appendChild(lectura);
    panel.querySelectorAll("button").forEach(b => {
      b.style.cssText = "font:inherit;padding:0.15em 0.7em;border:1px solid " + AZUL +
        ";background:white;color:" + AZUL + ";border-radius:4px;cursor:pointer;";
    });
    const deslizador = panel.querySelector("input");

    function actualizar() {
      const q1 = cuantil(datos, 0.25), med = cuantil(datos, 0.5), q3 = cuantil(datos, 0.75);
      const ric = q3 - q1;
      const cercaInf = q1 - k * ric, cercaSup = q3 + k * ric;
      const dentro = datos.filter(v => v >= cercaInf && v <= cercaSup);
      const bigoteInf = dentro.length ? Math.min(...dentro) : q1;
      const bigoteSup = dentro.length ? Math.max(...dentro) : q3;
      const marcados = datos.filter(v => v < cercaInf || v > cercaSup);

      rotulo.textContent = PASOS[paso - 1];
      puntos.forEach((c, i) => {
        const fuera = paso >= 5 && (datos[i] < cercaInf || datos[i] > cercaSup);
        c.setAttribute("fill", fuera ? ROJO : GRIS);
        c.setAttribute("r", fuera ? 6 : 4.5);
      });
      dibujarCaja(q1, med, q3, cercaInf, cercaSup, bigoteInf, bigoteSup);

      // La lectura crece con los pasos: cada número aparece cuando se dibuja
      const lineas = [`n = <b>${datos.length}</b> respuestas, ordenadas de menor a mayor`];
      if (paso >= 2) lineas.push(`Q1 = <b>${fmt(q1)}</b> · Q3 = <b>${fmt(q3)}</b> · RIC = Q3 − Q1 = <b>${fmt(ric)}</b>`);
      if (paso >= 3) lineas.push(`mediana = <b>${fmt(med)}</b>`);
      if (paso >= 4) lineas.push(`cercas = ${fmt(q1)} − ${fmt(k)} × ${fmt(ric)} y ${fmt(q3)} + ${fmt(k)} × ${fmt(ric)} ` +
        `→ de <b>${fmt(cercaInf)}</b> a <b>${fmt(cercaSup)}</b>`);
      if (paso >= 5) lineas.push(`bigotes en <b>${fmt(bigoteInf)}</b> y <b>${fmt(bigoteSup)}</b> · ` +
        `marcados: <b>${marcados.length}</b>${marcados.length ? " (" + marcados.map(fmt).join(", ") + ")" : ""}`);
      lectura.innerHTML = lineas.join("<br>");
    }

    function redibujar() { dibujarEjes(); colocarPuntos(); actualizar(); }

    deslizador.addEventListener("input", () => { k = Number(deslizador.value); if (paso < 4) paso = 4; actualizar(); });
    panel.querySelector('[data-accion="siguiente"]').addEventListener("click", () => {
      paso = Math.min(PASOS.length, paso + 1); actualizar();
    });
    panel.querySelector('[data-accion="anterior"]').addEventListener("click", () => {
      paso = Math.max(1, paso - 1); actualizar();
    });
    panel.querySelector('[data-accion="uno-cinco"]').addEventListener("click", () => {
      k = 1.5; deslizador.value = 1.5; actualizar();
    });
    panel.querySelector('[data-accion="estirar"]').addEventListener("click", ev => {
      estirado = !estirado;
      datos = datosOriginales.slice();
      if (estirado) datos[datos.length - 1] = datos[datos.length - 1] * 3;
      xmax = Math.max(...datos) * 1.06;
      ev.target.textContent = estirado ? "Regresar el máximo" : "Alargar el máximo";
      redibujar();
    });

    redibujar();
    return redibujar;
  }

  function iniciar() {
    const caja = document.getElementById("caja-animada");
    if (!caja || typeof DATOS_CAJA === "undefined") return;
    const redibujar = montar(caja, DATOS_CAJA);
    const visible = () => {
      const s = window.Reveal && Reveal.getCurrentSlide && Reveal.getCurrentSlide();
      if (!s || s.contains(caja)) redibujar();
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
