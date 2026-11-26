#!/usr/bin/env python3
"""Banco de problemas de los exámenes del curso (formato xsim).

Cada examen es un archivo LaTeX con el bloque xsim estándar del curso
(assets/bloque-xsim.tex): cada problema es un entorno ``exercise`` con su
``solution`` justo debajo, y la línea ``\\xsimsetup{tags={...}}`` elige qué
problemas se imprimen. Los demás forman el banco.

Subcomandos:
  listar    [EXAMEN.tex ...]                    tabla de todos los problemas
  banco     [EXAMEN.tex ...] -o banco.tex       documento con todos los problemas
            [--sin-soluciones] [--tag T]        (y sus soluciones), compilado a PDF
  armar     --ids "a,b|c|d" -o nuevo.tex        examen nuevo con los problemas elegidos;
            [--soluciones] [--puntos a=20,...]  "|" separa páginas. Compila a PDF.
            [--etiqueta parcial-4] [--fuentes EXAMEN.tex ...]
  convertir VIEJO.tex NUEVO.tex --etiqueta T    pasa un examen con \\item\\label{item:...}
            [--puntos a=25,...]                 y comment/solution al formato xsim

Sin archivos, listar/banco/armar usan examenes/*/examen.tex del repositorio.
Un problema se nombra por su ID; si el ID se repite en dos exámenes, use
EXAMEN:ID (EXAMEN es el nombre de la carpeta, p. ej. parcial-2-2025-2:montana).
"""
import argparse, re, subprocess, sys, shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BLOQUE = (AQUI.parent / 'assets' / 'bloque-xsim.tex').read_text(encoding='utf-8')
MARCA_INI, MARCA_FIN = '% --- xsim: problemas', '% --- fin xsim ---'
SEL_INI, SEL_FIN = '% === Selección del examen', '% === fin selección ==='


def raiz_repo():
    p = Path.cwd().resolve()
    for q in [p, *p.parents]:
        if (q / 'examenes').is_dir():
            return q
    for q in AQUI.parents:
        if (q / 'examenes').is_dir():
            return q
    return None


def seleccion(etiqueta, soluciones=False):
    return f"""{SEL_INI} (cambie solo estas líneas) ===
\\xsimsetup{{tags={{{etiqueta}}}}}   % se imprimen solo los problemas con esta etiqueta
\\newif\\ifsoluciones
\\soluciones{'true' if soluciones else 'false'}   % \\solucionestrue: solucionario (también muestra lo que va en \\phantom)
\\ifsoluciones\\xsimsetup{{solution/print=true}}\\renewcommand{{\\phantom}}[1]{{#1}}\\fi
{SEL_FIN}
"""


# ---------------------------------------------------------------- lectura
OPC = re.compile(r'\\begin\{exercise\}(?:\[(.*?)\])?\s*\n', re.S)


def leer_opciones(s):
    """'ID=x, subtitle={a, b}, tags={p,q}' -> dict (respeta llaves)."""
    d, prof, k, buf = {}, 0, None, ''
    partes, cur = [], ''
    for ch in s:
        if ch == '{': prof += 1
        if ch == '}': prof -= 1
        if ch == ',' and prof == 0:
            partes.append(cur); cur = ''
        else:
            cur += ch
    partes.append(cur)
    for p in partes:
        if not p.strip():
            continue
        k, _, v = p.partition('=')
        v = v.strip()
        if v.startswith('{') and v.endswith('}'):
            v = v[1:-1]
        d[k.strip()] = v.strip()
    return d


def escribir_opciones(d):
    orden = ['ID', 'subtitle', 'tags', 'points', 'nuevapagina']
    ks = [k for k in orden if k in d] + [k for k in d if k not in orden]
    out = []
    for k in ks:
        v = d[k]
        out.append(f'{k}={{{v}}}' if k in ('subtitle', 'tags') or ',' in v or '=' in v else f'{k}={v}')
    return ', '.join(out)


def leer_examen(ruta):
    """Devuelve (preambulo, encabezado, problemas, etiqueta_actual)."""
    t = Path(ruta).read_text(encoding='utf-8')
    pre, _, cuerpo = t.partition('\\begin{document}')
    cuerpo = cuerpo.rsplit('\\end{document}', 1)[0]
    m = re.search(r'\\xsimsetup\{tags=\{([^}]*)\}\}', pre)
    etiqueta = m.group(1) if m else ''
    problemas = []
    pos = 0
    primero = None
    nombre = Path(ruta).parent.name if Path(ruta).name == 'examen.tex' else Path(ruta).stem
    for m in OPC.finditer(cuerpo):
        if m.start() < pos:
            continue
        if primero is None:
            primero = m.start()
        fin = cuerpo.index('\\end{exercise}', m.end())
        enun = cuerpo[m.end():fin].strip('\n')
        pos = fin + len('\\end{exercise}')
        sol = ''
        ms = re.match(r'\s*\\begin\{solution\}\s*\n?', cuerpo[pos:])
        if ms:
            ini = pos + ms.end()
            fs = cuerpo.index('\\end{solution}', ini)
            sol = cuerpo[ini:fs].strip('\n')
            pos = fs + len('\\end{solution}')
        op = leer_opciones(m.group(1) or '')
        problemas.append({'examen': nombre, 'ruta': str(ruta), 'op': op, 'id': op.get('ID', f'p{len(problemas)+1}'),
                          'enunciado': enun, 'solucion': sol})
    encabezado = cuerpo[:primero].strip() if primero is not None else ''
    return pre, encabezado, problemas, etiqueta


def fuentes_por_defecto():
    r = raiz_repo()
    if not r:
        sys.exit('No encuentro la carpeta examenes/: pase los archivos .tex de los exámenes.')
    fs = sorted((r / 'examenes').glob('*/examen.tex'))
    return [f for f in fs if 'begin{exercise}' in f.read_text(encoding='utf-8')]


def cargar(fuentes):
    fuentes = fuentes or fuentes_por_defecto()
    pres, todos = [], []
    for f in fuentes:
        pre, enc, ps, et = leer_examen(f)
        pres.append(pre)
        for p in ps:
            p['impreso'] = bool(set(x.strip() for x in p['op'].get('tags', '').split(',')) & set(x.strip() for x in et.split(',')))
        todos += ps
    cuenta = {}
    for p in todos:
        cuenta[p['id']] = cuenta.get(p['id'], 0) + 1
    for p in todos:
        p['clave'] = p['id'] if cuenta[p['id']] == 1 else f"{p['examen']}:{p['id']}"
    return pres, todos


def preambulo_union(pres):
    """Une los preámbulos: paquetes y macros sin repetir; quita los bloques xsim y de selección."""
    lineas, vistos, libs = [], set(), []
    clase = None
    for pre in pres:
        pre = re.sub(re.escape(MARCA_INI) + r'.*?' + re.escape(MARCA_FIN) + r'\n?', '', pre, flags=re.S)
        pre = re.sub(re.escape(SEL_INI) + r'.*?' + re.escape(SEL_FIN) + r'\n?', '', pre, flags=re.S)
        for l in pre.splitlines():
            s = l.strip()
            if s.startswith('\\documentclass'):
                clase = clase or l
                continue
            m = re.match(r'\\usetikzlibrary\{([^}]*)\}', s)
            if m:
                for x in m.group(1).split(','):
                    if x.strip() and x.strip() not in libs:
                        libs.append(x.strip())
                continue
            if re.match(r'\\renewcommand\{\\phantom\}', s):
                continue
            if s and not s.startswith('%') and s in vistos:
                continue
            m = re.match(r'\\(?:re)?newcommand\{?(\\[A-Za-z]+)', s)
            if m and m.group(1) in vistos:
                continue
            if m:
                vistos.add(m.group(1))
            if s and not s.startswith('%'):
                vistos.add(s)
                lineas.append(l)
    out = [clase or '\\documentclass[12pt, a4paper]{article}'] + lineas
    if libs:
        i = max((k for k, l in enumerate(out) if '{tikz}' in l), default=len(out) - 1)
        out.insert(i + 1, '\\usetikzlibrary{' + ', '.join(libs) + '}')
    return '\n'.join(out) + '\n'


def compilar(tex):
    tex = Path(tex).resolve()
    for _ in range(2):
        r = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', tex.name],
                           cwd=tex.parent, capture_output=True, text=True)
    pdf = tex.with_suffix('.pdf')
    log = tex.with_suffix('.log').read_text(errors='ignore')
    errores = [l for l in log.splitlines() if l.startswith('!')]
    if errores or not pdf.exists():
        print('ERRORES DE LATEX:', *errores[:10], sep='\n  ')
        return None
    pags = subprocess.run(['pdfinfo', str(pdf)], capture_output=True, text=True).stdout
    m = re.search(r'Pages:\s+(\d+)', pags)
    print(f'PDF: {pdf} ({m.group(1) if m else "?"} páginas)')
    return pdf


def bloque(p, op):
    s = f"\\begin{{exercise}}[{escribir_opciones(op)}]\n{p['enunciado']}\n\\end{{exercise}}\n"
    if p['solucion']:
        s += f"\\begin{{solution}}\n{p['solucion']}\n\\end{{solution}}\n"
    return s


# ---------------------------------------------------------------- listar
def cmd_listar(a):
    _, ps = cargar(a.fuentes)
    print(f"{'clave':34} {'examen':20} {'impreso':7} {'pts':>4}  {'etiquetas':22} título o inicio")
    for p in ps:
        t = p['op'].get('subtitle') or re.sub(r'\s+', ' ', re.sub(r'\\[a-zA-Z]+|[{}$]', '', p['enunciado']))[:50]
        print(f"{p['clave']:34} {p['examen']:20} {'sí' if p['impreso'] else '—':7} {p['op'].get('points', ''):>4}  "
              f"{p['op'].get('tags', ''):22} {t}{'' if p['solucion'] else '  [sin solución]'}")
    print(f"\n{len(ps)} problemas; {sum(p['impreso'] for p in ps)} están en los exámenes impresos.")


# ---------------------------------------------------------------- banco
def cmd_banco(a):
    pres, ps = cargar(a.fuentes)
    if a.tag:
        ps = [p for p in ps if a.tag in [x.strip() for x in p['op'].get('tags', '').split(',')]]
    pre = preambulo_union(pres)
    plantilla = r"""\DeclareExerciseProperty{origen}
\DeclareExerciseEnvironmentTemplate{banco}
  {\par\bigskip\noindent\rule{\linewidth}{0.4pt}\par\nopagebreak\noindent
   \hfill{\small\ttfamily\GetExerciseProperty{origen}}\par\nopagebreak
   \begin{enumerate}[start=\GetExerciseProperty{counter}]
   \item \IfExercisePropertySetT{subtitle}{\textbf{\GetExerciseProperty{subtitle}.} }\ignorespaces}
  {\end{enumerate}}
\xsimsetup{exercise/template=banco}
"""
    sol = '' if a.sin_soluciones else '\\xsimsetup{solution/print=true}\n\\renewcommand{\\phantom}[1]{#1}\n'
    cuerpo = []
    for p in ps:
        op = dict(p['op'])
        op['ID'] = p['clave'].replace(':', '/')
        op.pop('nuevapagina', None)
        info = f"{p['clave']} · {p['examen']}"
        if op.get('tags'):
            info += f" · {op['tags']}"
        if op.get('points'):
            info += f" · {op['points']} pts"
        op['origen'] = info.replace('_', r'\_').replace('#', r'\#')
        cuerpo.append(bloque(p, op))
    doc = (pre + BLOQUE + plantilla + sol + '\\begin{document}\n'
           f'\\begin{{center}}\\Large\\bfseries Banco de problemas{" con soluciones" if not a.sin_soluciones else ""}\\end{{center}}\n'
           f'\\noindent {len(ps)} problemas de: {", ".join(sorted(set(p["examen"] for p in ps)))}.\n\n'
           + '\n'.join(cuerpo) + '\\end{document}\n')
    Path(a.o).write_text(doc, encoding='utf-8')
    print(f'escrito {a.o} ({len(ps)} problemas)')
    if not a.no_compilar:
        compilar(a.o)


# ---------------------------------------------------------------- armar
def cmd_armar(a):
    pres, ps = cargar(a.fuentes)
    por_clave = {p['clave']: p for p in ps}
    por_id = {}
    for p in ps:
        por_id.setdefault(p['id'], []).append(p)
    puntos = dict(x.split('=') for x in a.puntos.split(',')) if a.puntos else {}
    elegidos = []
    for k, pagina in enumerate(a.ids.split('|')):
        for j, nombre in enumerate(x.strip() for x in pagina.split(',') if x.strip()):
            if nombre in por_clave:
                p = por_clave[nombre]
            elif nombre in por_id and len(por_id[nombre]) == 1:
                p = por_id[nombre][0]
            elif nombre in por_id:
                sys.exit(f'El ID «{nombre}» está en varios exámenes; use una de: ' + ', '.join(q['clave'] for q in por_id[nombre]))
            else:
                sys.exit(f'No existe el problema «{nombre}». Vea la lista con: banco.py listar')
            op = {kk: v for kk, v in p['op'].items() if kk != 'nuevapagina'}
            op['ID'] = p['id'] if p['clave'] == p['id'] else p['clave'].replace(':', '-')
            op['tags'] = a.etiqueta
            if nombre in puntos or p['id'] in puntos:
                op['points'] = puntos.get(nombre, puntos.get(p['id']))
            if k > 0 and j == 0:
                op['nuevapagina'] = 'true'
            elegidos.append((p, op))
    pre = preambulo_union(pres)
    enc = '\\vspace*{-2cm}\nNombre:$\\underline{\\hspace{8.5cm}}$ Identificación: \\hrulefill\n\n\\quad\n'
    if a.titulo:
        enc = f'\\begin{{center}}\\large\\bfseries {a.titulo}\\end{{center}}\n' + enc.replace('\\vspace*{-2cm}\n', '')
    total = sum(float(op['points']) for _, op in elegidos if op.get('points'))
    doc = (pre + BLOQUE + seleccion(a.etiqueta, a.soluciones) + '\\begin{document}\n\n' + enc + '\n'
           + '\n'.join(bloque(p, op) for p, op in elegidos) + '\n\\end{document}\n')
    Path(a.o).write_text(doc, encoding='utf-8')
    print(f'escrito {a.o}: {len(elegidos)} problemas'
          + (f', {total:g} puntos' if total else '') + (', con soluciones' if a.soluciones else ''))
    for p, op in elegidos:
        print(f"  {op['ID']:28} de {p['examen']:20} {op.get('points', '—'):>4} pts{'  (página nueva)' if op.get('nuevapagina') else ''}")
    if not a.no_compilar:
        compilar(a.o)


# ---------------------------------------------------------------- convertir
def cmd_convertir(a):
    t = Path(a.viejo).read_text(encoding='utf-8')
    pre, _, cuerpo = t.partition('\\begin{document}')
    cuerpo = cuerpo.rsplit('\\end{document}', 1)[0]
    enc, _, lista = cuerpo.partition('\\begin{enumerate}')
    lista, _, cola = lista.rpartition('\\end{enumerate}')
    # regiones del banco: \begin{comment}...\end{comment} que contienen problemas
    segs, pos = [], 0
    for m in re.finditer(r'\\begin\{comment\}', lista):
        if m.start() < pos:
            continue
        f = lista.index('\\end{comment}', m.end())
        dentro = lista[m.end():f]
        if '\\item\\label{item:' in dentro:
            segs.append((lista[pos:m.start()], False))
            segs.append((dentro.split('\n', 1)[1] if '\n' in dentro else dentro, True))
            pos = f + len('\\end{comment}')
    segs.append((lista[pos:], False))
    puntos = dict(x.split('=') for x in a.puntos.split(',')) if a.puntos else {}
    problemas, salto_pendiente, hubo_impreso = [], False, False
    for txt, banco in segs:
        partes = re.split(r'\\item\\label\{item:([^}]+)\}', txt)
        if not banco and '\\newpage' in partes[0] and hubo_impreso:
            salto_pendiente = True
        for k in range(1, len(partes), 2):
            ident, resto = partes[k], partes[k + 1]
            if '\\begin{solution}' in resto:
                enun, _, r2 = resto.partition('\\begin{solution}')
                sol, _, despues = r2.partition('\\end{solution}')
            else:
                enun, sol, despues = resto, '', ''
            # lo que viene después de la solución (o del enunciado sin solución)
            nueva = '\\newpage' in despues or '\\clearpage' in despues or (not sol and re.search(r'\\newpage\s*$', enun.strip()))
            enun = re.sub(r'\s*\\newpage\s*$', '', enun.rstrip())
            enun = re.sub(r'\n\s*%\s*=+[^\n]*', '', enun).strip('\n').rstrip()
            enun = enun.lstrip(' ')
            op = {'ID': ident}
            mt = re.match(r'\\textbf\{([^{}]+?)[.:]?\}[ \t]*', enun)
            if mt:
                op['subtitle'] = mt.group(1).strip()
                enun = enun[mt.end():]
            op['tags'] = 'banco' if banco else a.etiqueta
            if ident in puntos:
                op['points'] = puntos[ident]
            if not banco:
                if salto_pendiente:
                    op['nuevapagina'] = 'true'
                salto_pendiente = bool(nueva)
                hubo_impreso = True
            problemas.append(bloque({'enunciado': enun.strip('\n'), 'solucion': sol.strip('\n')}, op))
    # preámbulo: quita comment/solution/phantom y añade el bloque xsim y la selección
    pre = re.sub(r'\\usepackage\{comment\}\n', '', pre)
    pre = re.sub(r'\\(?:include|exclude|special)comment\{(?:solution|comment)\}(?:\n?\s*\{[^\n]*\}\{[^\n]*\})?[^\n]*\n', '', pre)
    pre = re.sub(r'%?\s*\\renewcommand\{\\phantom\}\[1\]\{#1\}[^\n]*\n', '', pre)
    pre = re.sub(r'% Para obtener solución[^\n]*\n', '', pre)
    pre = pre.rstrip() + '\n\n' + BLOQUE + seleccion(a.etiqueta) + '\n'
    enc = re.sub(r'\n\s*%\s*(---|===)[^\n]*', '', enc).rstrip()
    doc = pre + '\\begin{document}' + enc + '\n\n' + '\n'.join(problemas) + cola.strip() + '\n\\end{document}\n'
    Path(a.nuevo).write_text(doc, encoding='utf-8')
    n = sum(1 for p in problemas if f'tags={{{a.etiqueta}}}' in p)
    print(f'escrito {a.nuevo}: {len(problemas)} problemas ({n} en el examen, {len(problemas) - n} en el banco)')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('listar'); s.add_argument('fuentes', nargs='*'); s.set_defaults(f=cmd_listar)
    s = sub.add_parser('banco'); s.add_argument('fuentes', nargs='*'); s.add_argument('-o', default='banco.tex')
    s.add_argument('--sin-soluciones', action='store_true'); s.add_argument('--tag')
    s.add_argument('--no-compilar', action='store_true'); s.set_defaults(f=cmd_banco)
    s = sub.add_parser('armar'); s.add_argument('--ids', required=True); s.add_argument('-o', default='examen-nuevo.tex')
    s.add_argument('--fuentes', nargs='*', default=[]); s.add_argument('--soluciones', action='store_true')
    s.add_argument('--puntos'); s.add_argument('--etiqueta', default='examen'); s.add_argument('--titulo')
    s.add_argument('--no-compilar', action='store_true'); s.set_defaults(f=cmd_armar)
    s = sub.add_parser('convertir'); s.add_argument('viejo'); s.add_argument('nuevo')
    s.add_argument('--etiqueta', required=True); s.add_argument('--puntos'); s.set_defaults(f=cmd_convertir)
    a = ap.parse_args()
    a.f(a)


if __name__ == '__main__':
    main()
