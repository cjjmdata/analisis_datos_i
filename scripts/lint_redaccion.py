"""Revisa la prosa del curso contra los criterios de redaccion.

Une dos fuentes:

1. `prompts/decisiones.md`, las reglas propias del curso.
2. `../../Trabajo/Propuestas/references/redaccion.md`, el registro de redaccion
   del despacho. De ahi se toma lo que aplica a material docente: marcadores de
   LLM, lexico de consultoria anglosajona, muletillas que sustituyen al verbo,
   nominalizacion y titulos nominales. NO se toma la voz impersonal: el material
   del curso le habla al alumno.

Uso:
    python scripts/lint_redaccion.py                # todo el material publicable
    python scripts/lint_redaccion.py ruta [ruta...] # archivos concretos

Salida: una linea por hallazgo, `archivo:linea: [categoria] fragmento`.
El codigo de salida es 1 si hay hallazgos de gravedad `error`.
"""

import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent

# Carpetas que se revisan cuando no se pasan rutas. `prompts/` y `examen/` no
# entran: son notas internas, no material del alumno.
CARPETAS = ["curso", "unidades", "slides", "datos", "portafolio", "recursos", "cuadernos"]
SUELTOS = ["index.qmd", "README.md", "AGENTS.md"]

# (categoria, gravedad, patron, sugerencia)
REGLAS = [
    # --- Marcadores de LLM (references/redaccion.md) ------------------------
    ("marcador-llm", "error", r"\bcabe (destacar|señalar|mencionar|notar)\b", "afirmación directa"),
    ("marcador-llm", "error", r"\bes importante (señalar|destacar|mencionar|notar)\b", "afirmación directa"),
    ("marcador-llm", "error", r"\ben este sentido\b", "quitar"),
    ("marcador-llm", "error", r"\bvale la pena\b", "quitar o decir por qué"),
    ("marcador-llm", "error", r"\bdicho de otro modo\b", "decirlo una sola vez"),
    ("marcador-llm", "error", r"\b(obsérvese|nótese|véase que)\b", "afirmación directa"),
    ("marcador-llm", "error", r"\bno es menor\b", "decir la magnitud"),
    ("marcador-llm", "error", r"\bel corazón de\b", "nombrar la parte"),
    ("marcador-llm", "error", r"\b(claramente|notablemente|indudablemente|sin duda)\b", "adverbio sin función"),
    ("marcador-llm", "aviso", r"\bpor su parte\b|\basimismo\b|\bpor otro lado\b", "conector de relleno"),

    # --- Nominalizacion -----------------------------------------------------
    ("nominalizacion", "error", r"\bmediante la (aplicación|utilización|realización|implementación) de\b", "recuperar el verbo"),
    ("nominalizacion", "error", r"\b(se procede a|proceder a) la\b", "recuperar el verbo"),
    ("nominalizacion", "error", r"\bhacer uso de\b", "usar"),
    ("nominalizacion", "error", r"\bllevar a cabo\b", "el verbo propio"),
    ("nominalizacion", "error", r"\bdar cumplimiento a\b", "cumplir"),
    ("nominalizacion", "aviso", r"\bla (obtención|generación|elaboración|realización) de\b", "recuperar el verbo"),

    # --- Muletillas que sustituyen al verbo ---------------------------------
    ("muletilla", "error", r"\b(la tabla|la gráfica|la figura|el cuadro|el histograma) muestra\b", "registra, concentra, sitúa"),
    ("muletilla", "error", r"\b(los datos|los resultados) (presentan|muestran)\b", "registran, concentran"),
    ("muletilla", "error", r"\bse (realizó|realiza|realizaron) (el|la|un|una)\b", "el verbo propio del procedimiento"),
    ("muletilla", "error", r"\b(sostiene|sustenta|sostienen|sustentan) que\b", "establece, permite afirmar"),
    ("muletilla", "aviso", r"\bse aplic(ó|a|aron) (el|la)\b", "el verbo propio"),

    # --- Lexico de consultoria anglosajona ----------------------------------
    ("lexico-importado", "error", r"\bhito(s)?\b", "punto de entrega, fecha de corte"),
    ("lexico-importado", "error", r"\bgranularidad\b", "nivel de desagregación"),
    ("lexico-importado", "error", r"\baccionable(s)?\b", "que permite decidir"),
    ("lexico-importado", "error", r"\baterriza(r|ndo)\b", "concretar, aplicar"),
    ("lexico-importado", "error", r"\bescalable\b|\biterativo\b", "decir qué hace"),
    ("lexico-importado", "error", r"\babordaje\b", "tratamiento, enfoque"),
    ("lexico-importado", "error", r"\bde cara a\b|\bponer en valor\b", "para, ante"),
    ("lexico-importado", "error", r"\brobustecer\b|\bcapitalizar\b", "reforzar"),
    ("lexico-importado", "aviso", r"\bmape(o|ar)\b", "solo si hay cartografía"),

    # --- Reglas propias del curso (prompts/decisiones.md) -------------------
    # El guion entre cifras es un rango tipografico correcto (1-3, 2020-2024)
    # y no el marcador que se persigue.
    ("guion-largo", "error", r"(?<!\d)[—–](?!\d)", "coma, dos puntos o paréntesis"),
    ("instruir", "aviso", r"\b(hay que|tienes que|vas a tener que|debes de)\b", "enunciar la disciplina"),
    ("sobreventa", "error", r"\b(obliga a|garantiza|revoluciona|poderoso|esencial|crucial|robusto)\b", "mostrar por qué importa"),
    ("sobreventa", "aviso", r"\b(clave|fundamental)\b", "casi siempre sobra"),
    ("remate", "error", r"(Eso es todo\.|Y ya\.|Es así de simple\.)", "quitar"),
    ("antitesis", "aviso", r"\bNo es .{3,40}: es\b", "la afirmación directa"),
    ("coloquial", "aviso", r"\b(entre manos|de golpe|a ojo|de corrido|se cae|te va a llenar de)\b", "registro adulto"),
    ("termino-propio", "error", r"\bfricción cognitiva\b", "Bjork, Kapur, Sweller, ICAP"),
]

# Titulos que anuncian la posicion del lector en vez de nombrar el contenido.
TITULOS_POSICION = re.compile(
    r"^\s*#{1,6}\s+(el punto de partida|lo que sigue|hacia dónde|para empezar|"
    r"antes de continuar|en resumen|recapitulando)\b", re.I)

COMPILADAS = [(c, g, re.compile(p, re.I), s) for c, g, p, s in REGLAS]


def lineas_de(ruta):
    """Devuelve (numero, texto) de la prosa del archivo.

    En los cuadernos solo se revisa el texto, no el codigo ni las salidas.
    """
    if ruta.suffix == ".ipynb":
        nb = json.loads(ruta.read_text(encoding="utf-8"))
        n = 0
        for celda in nb.get("cells", []):
            if celda.get("cell_type") != "markdown":
                continue
            for l in "".join(celda["source"]).split("\n"):
                n += 1
                yield n, l
        return
    dentro_de_codigo = False
    for n, l in enumerate(ruta.read_text(encoding="utf-8").split("\n"), 1):
        if l.lstrip().startswith("```"):
            dentro_de_codigo = not dentro_de_codigo
            continue
        if not dentro_de_codigo:
            yield n, l


def revisa(ruta):
    hallazgos = []
    for n, linea in lineas_de(ruta):
        if not linea.strip():
            continue
        for categoria, gravedad, patron, sugerencia in COMPILADAS:
            for m in patron.finditer(linea):
                hallazgos.append((n, categoria, gravedad, m.group(0).strip(), sugerencia))
        if TITULOS_POSICION.match(linea):
            hallazgos.append((n, "titulo-posicion", "aviso", linea.strip(), "título nominal"))
    return hallazgos


def archivos(rutas):
    if rutas:
        return [pathlib.Path(r) for r in rutas]
    fuera = []
    for c in CARPETAS:
        for patron in ("**/*.qmd", "**/*.ipynb", "**/*.md"):
            fuera += sorted((RAIZ / c).glob(patron))
    fuera += [RAIZ / s for s in SUELTOS]
    return [f for f in fuera if f.exists()]


def main():
    total = {"error": 0, "aviso": 0}
    por_categoria = {}
    for ruta in archivos(sys.argv[1:]):
        for n, categoria, gravedad, fragmento, sugerencia in revisa(ruta):
            total[gravedad] += 1
            por_categoria[categoria] = por_categoria.get(categoria, 0) + 1
            rel = ruta.relative_to(RAIZ) if RAIZ in ruta.parents else ruta
            marca = "ERROR" if gravedad == "error" else "aviso"
            print(f"{rel}:{n}: [{marca} · {categoria}] «{fragmento}» -> {sugerencia}")

    print(f"\n{total['error']} errores · {total['aviso']} avisos")
    for c, n in sorted(por_categoria.items(), key=lambda t: -t[1]):
        print(f"  {n:4d}  {c}")
    return 1 if total["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
