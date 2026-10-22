// Simulador de la sesión 14: variación de las tasas y las dos medias.
//
// Diez años de una inversión de 10,000 pesos cuyas tasas alternan entre
// media + variación y media - variación. Con un número par de años la media
// aritmética de las tasas es exactamente la media elegida; la media geométrica
// baja conforme crece la variación, y es la única que reproduce el monto final.
//
// Pensado para no fallar frente al grupo:
//   - Sin librerías ni recursos externos: funciona sin internet.
//   - Sin números aleatorios: el mismo control da siempre el mismo resultado.
//   - Los parámetros por omisión y los casos llegan desde R (PARAMS_SIMULADOR),
//     así que ninguna cifra de la lámina se teclea aquí.
//   - Si algo falla al dibujar, la lámina muestra un aviso y la siguiente trae
//     los mismos casos calculados en R.
//
// Prueba sin navegador: node valida `calcula` contra R (ver la sesión 14).
// Prueba en navegador: ?simulador=media,variacion fija los controles al cargar.

(function (raiz) {
  "use strict";

  // Cálculo puro: también lo usa la prueba con node
  function calcula(media, variacion, anios, inicial) {
    const tasas = [];
    for (let i = 0; i < anios; i++) tasas.push((i % 2 === 0 ? media + variacion : media - variacion) / 100);
    const real = [inicial];
    for (const r of tasas) real.push(real[real.length - 1] * (1 + r));
    const aritmetica = tasas.reduce((a, b) => a + b, 0) / anios;
    const sumaLog = tasas.reduce((a, r) => a + Math.log(1 + r), 0);
    const geometrica = Math.exp(sumaLog / anios) - 1;
    const conAritmetica = real.map((_, t) => inicial * Math.pow(1 + aritmetica, t));
    const conGeometrica = real.map((_, t) => inicial * Math.pow(1 + geometrica, t));
    return { tasas, real, aritmetica, geometrica, conAritmetica, conGeometrica,
             finalReal: real[anios], finalAritmetica: conAritmetica[anios], finalGeometrica: conGeometrica[anios] };
  }

  if (typeof module !== "undefined" && module.exports) { module.exports = { calcula }; return; }

  const P = raiz.PARAMS_SIMULADOR || { media: 7, variacion: 0, anios: 10, inicial: 10000,
                                       maxMedia: 15, maxVariacion: 40, casos: [0, 10, 23, 40] };
  const NS = "http://www.w3.org/2000/svg";
  const COL = { real: "#A4503C", arit: "#3A6B6F", geo: "#5A7B5A", eje: "#9AA5A6", tinta: "#24494C" };
  const pesos = v => Math.round(v).toLocaleString("en-US");
  const menos = s => s.replace(/^-/, "−");   // signo menos tipográfico
  const pct = (v, d) => menos((v * 100).toFixed(d)) + "%";

  function el(tag, attrs, padre) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (padre) padre.appendChild(e);
    return e;
  }

  function monta(cont) {
    cont.innerHTML = `
      <div class="sim-controles">
        <label>Tasa promedio (media simple): <b class="sim-v-media"></b>
          <input class="sim-media" type="range" min="0" max="${P.maxMedia}" step="0.5"></label>
        <label>Variación de un año a otro: <b class="sim-v-var"></b>
          <input class="sim-var" type="range" min="0" max="${P.maxVariacion}" step="1"></label>
        <div class="sim-casos">Casos: ${P.casos.map(c => `<button type="button" data-var="${c}">±${c}</button>`).join("")}</div>
      </div>
      <div class="sim-cuerpo">
        <svg class="sim-grafica" viewBox="0 0 560 300" preserveAspectRatio="xMidYMid meet"></svg>
        <table class="sim-tabla">
          <tr><td>Tasas de cada año</td><td class="sim-t-tasas"></td></tr>
          <tr><td style="color:${COL.arit}">Media aritmética</td><td class="sim-t-arit"></td></tr>
          <tr><td style="color:${COL.geo}">Media geométrica</td><td class="sim-t-geo"></td></tr>
          <tr><td style="color:${COL.real}">Monto real a ${P.anios} años</td><td class="sim-t-real"></td></tr>
          <tr><td style="color:${COL.arit}">Con la media aritmética</td><td class="sim-t-farit"></td></tr>
          <tr><td style="color:${COL.geo}">Con la media geométrica</td><td class="sim-t-fgeo"></td></tr>
        </table>
      </div>`;
    const q = s => cont.querySelector(s);
    const media = q(".sim-media"), vari = q(".sim-var");

    // ?simulador=media,variacion fija los valores al cargar (para probar y para clase)
    const m = /[?&]simulador=([\d.]+),([\d.]+)/.exec(raiz.location ? raiz.location.search : "");
    media.value = m ? m[1] : P.media;
    vari.value = m ? m[2] : P.variacion;

    function dibuja() {
      const mv = Math.min(Number(media.value), P.maxMedia);
      const vv = Math.min(Number(vari.value), P.maxVariacion);
      const R = calcula(mv, vv, P.anios, P.inicial);
      q(".sim-v-media").textContent = mv.toFixed(1) + "%";
      q(".sim-v-var").textContent = "±" + vv + " puntos";
      q(".sim-t-tasas").textContent = `${menos((mv + vv).toFixed(1))}% y ${menos((mv - vv).toFixed(1))}%, alternadas`;
      q(".sim-t-arit").textContent = pct(R.aritmetica, 2);
      q(".sim-t-geo").textContent = pct(R.geometrica, 2);
      q(".sim-t-real").textContent = pesos(R.finalReal);
      q(".sim-t-farit").textContent = pesos(R.finalAritmetica);
      q(".sim-t-fgeo").textContent = pesos(R.finalGeometrica);
      cont.dataset.resultado = [mv, vv, R.aritmetica.toFixed(6), R.geometrica.toFixed(6),
                                R.finalReal.toFixed(2), R.finalAritmetica.toFixed(2)].join("|");

      // Gráfica: eje y fijo entre el peor y el mejor caso posible, para que la
      // escala no salte al mover los controles
      const svg = q(".sim-grafica");
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      const izq = 62, der = 545, arr = 15, aba = 265;
      const peor = calcula(0, P.maxVariacion, P.anios, P.inicial), mejor = calcula(P.maxMedia, 0, P.anios, P.inicial);
      // Límites redondeados a miles, con marcas en múltiplos redondos
      const paso = 5000;
      const ymin = Math.floor(Math.min(...peor.real, ...peor.conGeometrica) / paso) * paso;
      const ymax = Math.ceil(Math.max(...mejor.real) / paso) * paso;
      const X = t => izq + (der - izq) * t / P.anios;
      const Y = v => aba - (aba - arr) * (v - ymin) / (ymax - ymin);
      for (let v = ymin; v <= ymax; v += paso * 2) {
        el("line", { x1: izq, x2: der, y1: Y(v), y2: Y(v), stroke: "#E3E8E8" }, svg);
        el("text", { x: izq - 6, y: Y(v) + 4, "text-anchor": "end", "font-size": 13, fill: COL.eje }, svg).textContent = pesos(v);
      }
      for (let t = 0; t <= P.anios; t++) {
        el("text", { x: X(t), y: aba + 16, "text-anchor": "middle", "font-size": 13, fill: COL.eje }, svg).textContent = t;
      }
      el("text", { x: (izq + der) / 2, y: aba + 32, "text-anchor": "middle", "font-size": 13, fill: COL.tinta }, svg).textContent = "Año";
      const linea = (vals, color, guion, ancho) => el("polyline", {
        points: vals.map((v, t) => `${X(t)},${Y(v)}`).join(" "), fill: "none", stroke: color,
        "stroke-width": ancho, "stroke-dasharray": guion || "none" }, svg);
      linea(R.conAritmetica, COL.arit, "7 5", 2.5);
      linea(R.conGeometrica, COL.geo, "2 4", 2.5);
      linea(R.real, COL.real, null, 3);
      R.real.forEach((v, t) => el("circle", { cx: X(t), cy: Y(v), r: 3.2, fill: COL.real }, svg));
    }

    for (const ctrl of [media, vari]) ctrl.addEventListener("input", dibuja);
    cont.querySelectorAll(".sim-casos button").forEach(b => b.addEventListener("click", () => {
      vari.value = b.dataset.var; dibuja();
    }));
    // Que las flechas muevan el control y no cambien de lámina; la barra
    // espaciadora y las demás teclas siguen avanzando la presentación
    const TECLAS_CONTROL = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End"];
    cont.addEventListener("keydown", e => {
      if (e.target.tagName === "INPUT" && TECLAS_CONTROL.includes(e.key)) e.stopPropagation();
    });
    dibuja();

    // ?prueba-simulador: recorre los casos por el mismo camino que un clic del
    // usuario (evento input del control) y deja los resultados en el DOM
    if (raiz.location && /[?&]prueba-simulador/.test(raiz.location.search)) {
      const res = [];
      for (const c of P.casos) {
        vari.value = c;
        vari.dispatchEvent(new Event("input", { bubbles: true }));
        res.push(cont.dataset.resultado);
      }
      cont.dataset.prueba = res.join(";");
    }
  }

  function inicia() {
    document.querySelectorAll(".simulador-geometrica").forEach(cont => {
      try { monta(cont); }
      catch (err) {
        cont.innerHTML = '<p style="color:#A4503C">El simulador no pudo cargarse. La lámina siguiente trae los mismos casos.</p>';
      }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", inicia);
  else inicia();
})(typeof window !== "undefined" ? window : globalThis);
