// Simulador de la sesión 15: desviaciones al cuadrado, varianza y desviación estándar.
//
// Cinco valores sobre una recta. Cada desviación respecto de la media se dibuja
// como un cuadrado de lado |x − media|: la varianza es el área promedio de esos
// cuadrados (dividiendo entre n − 1) y la desviación estándar es el lado del
// cuadrado promedio, que aparece punteado.
//
// Pensado para no fallar frente al grupo:
//   - Sin librerías ni recursos externos: funciona sin internet.
//   - Sin números aleatorios: el mismo control da siempre el mismo resultado.
//   - Los valores iniciales, los límites y los casos llegan desde R
//     (PARAMS_DISPERSION), así que ninguna cifra de la lámina se teclea aquí.
//   - Si algo falla al dibujar, la lámina muestra un aviso y la siguiente trae
//     los mismos casos calculados en R.
//
// Prueba sin navegador: node valida `calcula` contra R (ver la sesión 15).
// Prueba en navegador: ?prueba-simulador recorre los casos y deja los resultados
// en el atributo data-prueba del contenedor.

(function (raiz) {
  "use strict";

  // Cálculo puro: también lo usa la prueba con node
  function calcula(valores) {
    const n = valores.length;
    const media = valores.reduce((a, b) => a + b, 0) / n;
    const desv = valores.map(v => v - media);
    const sumaDesv = desv.reduce((a, b) => a + b, 0);
    const sumaCuad = desv.reduce((a, d) => a + d * d, 0);
    const varianza = sumaCuad / (n - 1);
    return { n, media, desv, sumaDesv, sumaCuad, varianza, varianzaN: sumaCuad / n, de: Math.sqrt(varianza) };
  }

  if (typeof module !== "undefined" && module.exports) { module.exports = { calcula }; return; }

  const P = raiz.PARAMS_DISPERSION || { valores: [32, 48, 60, 43, 29], min: 15, max: 95, unidad: "años",
                                        etiqueta: "Edad del jefe del hogar", casos: [] };
  const NS = "http://www.w3.org/2000/svg";
  const COL = { punto: "#3A6B6F", media: "#A4503C", pos: "#5B888C", neg: "#B4704F", eje: "#9AA5A6", tinta: "#24494C" };
  const f1 = v => (Math.abs(v) < 0.05 ? 0 : v).toFixed(1).replace(/^-/, "−");
  const miles = v => Math.round(v).toLocaleString("en-US");

  function el(tag, attrs, padre) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (padre) padre.appendChild(e);
    return e;
  }

  function monta(cont) {
    const n = P.valores.length;
    cont.innerHTML = `
      <div class="sim-controles">
        ${P.valores.map((v, i) => `<label>Hogar ${i + 1}: <b class="sim-v-${i}"></b>
          <input class="sim-x-${i}" type="range" min="${P.min}" max="${P.max}" step="1"></label>`).join("")}
        <div class="sim-casos">Casos: ${P.casos.map((c, k) => `<button type="button" data-caso="${k}">${c.nombre}</button>`).join("")}</div>
      </div>
      <div class="sim-cuerpo">
        <svg class="sim-grafica" viewBox="0 0 560 330" preserveAspectRatio="xMidYMid meet"></svg>
        <table class="sim-tabla">
          <tr><td style="color:${COL.media}">Media</td><td class="sim-t-media"></td></tr>
          <tr><td>Suma de desviaciones</td><td class="sim-t-sdesv"></td></tr>
          <tr><td>Suma de cuadrados</td><td class="sim-t-scuad"></td></tr>
          <tr><td>Varianza (÷ n − 1)</td><td class="sim-t-var"></td></tr>
          <tr><td>Desviación estándar</td><td class="sim-t-de"></td></tr>
          <tr><td style="color:#6C7A7B">Varianza (÷ n)</td><td class="sim-t-varn" style="color:#6C7A7B"></td></tr>
        </table>
      </div>`;
    const q = s => cont.querySelector(s);
    const ctrl = P.valores.map((v, i) => q(`.sim-x-${i}`));
    ctrl.forEach((c, i) => { c.value = P.valores[i]; });

    function dibuja() {
      const x = ctrl.map(c => Math.min(Math.max(Number(c.value), P.min), P.max));
      const R = calcula(x);
      x.forEach((v, i) => { q(`.sim-v-${i}`).textContent = v + " " + P.unidad; });
      q(".sim-t-media").textContent = f1(R.media);
      q(".sim-t-sdesv").textContent = f1(R.sumaDesv);
      q(".sim-t-scuad").textContent = miles(R.sumaCuad);
      q(".sim-t-var").textContent = f1(R.varianza);
      q(".sim-t-de").textContent = f1(R.de) + " " + P.unidad;
      q(".sim-t-varn").textContent = f1(R.varianzaN);
      cont.dataset.resultado = [x.join(","), R.media.toFixed(4), R.sumaCuad.toFixed(4),
                                R.varianza.toFixed(4), R.de.toFixed(4)].join("|");

      // Escala fija: los cuadrados conservan su área real al mover los controles
      const svg = q(".sim-grafica");
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      const izq = 30, der = 540, eje = 300;
      const k = (der - izq) / (P.max - P.min);          // pixeles por unidad
      const X = v => izq + k * (v - P.min);

      // Cuadrados de las desviaciones, apoyados en el eje entre la media y cada valor
      x.forEach((v, i) => {
        const d = v - R.media, lado = Math.abs(d) * k;
        if (lado < 0.5) return;
        el("rect", { x: Math.min(X(v), X(R.media)), y: eje - lado, width: lado, height: lado,
                     fill: d > 0 ? COL.pos : COL.neg, "fill-opacity": 0.18,
                     stroke: d > 0 ? COL.pos : COL.neg, "stroke-width": 1.5 }, svg);
      });
      // El cuadrado promedio: área = varianza, lado = desviación estándar
      const ladoDE = R.de * k;
      if (ladoDE > 0.5) {
        el("rect", { x: X(R.media) - ladoDE / 2, y: eje - ladoDE, width: ladoDE, height: ladoDE, fill: "none",
                     stroke: COL.tinta, "stroke-width": 2, "stroke-dasharray": "6 4" }, svg);
      }
      // Eje con marcas
      el("line", { x1: izq, x2: der, y1: eje, y2: eje, stroke: COL.eje, "stroke-width": 1.5 }, svg);
      const paso = (P.max - P.min) > 50 ? 10 : 5;
      for (let t = Math.ceil(P.min / paso) * paso; t <= P.max; t += paso) {
        el("line", { x1: X(t), x2: X(t), y1: eje, y2: eje + 5, stroke: COL.eje }, svg);
        el("text", { x: X(t), y: eje + 20, "text-anchor": "middle", "font-size": 13, fill: COL.eje }, svg).textContent = t;
      }
      // Media
      el("line", { x1: X(R.media), x2: X(R.media), y1: 10, y2: eje, stroke: COL.media, "stroke-width": 2.5 }, svg);
      el("text", { x: X(R.media) + 5, y: 22, "font-size": 14, fill: COL.media }, svg).textContent = "media " + f1(R.media);
      // Valores
      x.forEach((v, i) => {
        el("circle", { cx: X(v), cy: eje, r: 7, fill: COL.punto, stroke: "#FFFFFF", "stroke-width": 1.5 }, svg);
        el("text", { x: X(v), y: eje - 11 - (i % 2) * 14, "text-anchor": "middle", "font-size": 12, fill: COL.tinta }, svg)
          .textContent = i + 1;
      });
    }

    ctrl.forEach(c => c.addEventListener("input", dibuja));
    cont.querySelectorAll(".sim-casos button").forEach(b => b.addEventListener("click", () => {
      P.casos[Number(b.dataset.caso)].valores.forEach((v, i) => { ctrl[i].value = v; });
      dibuja();
    }));
    // Que las flechas muevan el control y no cambien de lámina
    const TECLAS_CONTROL = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", "Home", "End"];
    cont.addEventListener("keydown", e => {
      if (e.target.tagName === "INPUT" && TECLAS_CONTROL.includes(e.key)) e.stopPropagation();
    });
    dibuja();

    // ?prueba-simulador: recorre los casos por el mismo camino que un control movido
    // por el usuario (evento input) y deja los resultados en el DOM
    if (raiz.location && /[?&]prueba-simulador/.test(raiz.location.search)) {
      const res = [];
      for (const caso of P.casos) {
        caso.valores.forEach((v, i) => { ctrl[i].value = v; });
        ctrl[0].dispatchEvent(new Event("input", { bubbles: true }));
        res.push(cont.dataset.resultado);
      }
      cont.dataset.prueba = res.join(";");
    }
  }

  function inicia() {
    document.querySelectorAll(".simulador-dispersion").forEach(cont => {
      try { monta(cont); }
      catch (err) {
        cont.innerHTML = '<p style="color:#A4503C">El simulador no pudo cargarse. La lámina siguiente trae los mismos casos.</p>';
      }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", inicia);
  else inicia();
})(typeof window !== "undefined" ? window : globalThis);
