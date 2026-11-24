#!/usr/bin/env python3
"""Crea la carpeta de trabajo de un examen nuevo.

Uso:
    python3 scripts/nuevo_examen.py <examen> [--curso "..."] [--tema "..."] [--paginas N]

Ejemplo:
    python3 scripts/nuevo_examen.py parcial-3-2026-1 --tema electromagnetismo --paginas 4

Crea examenes/<examen>/ con:
  examen.tex   copia de plantilla/examen.tex (o déjalo y pon ahí el LaTeX real)
  examen.json  esqueleto del JSON del calificador (se completa a partir del examen)
  README.md    ficha del examen: fuente, estado y enlace del calificador publicado
No sobrescribe nada que ya exista.
"""
import argparse, json, shutil
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('examen', help='nombre corto, p. ej. parcial-3-2026-1')
    ap.add_argument('--curso', default='Fundamentación en Física')
    ap.add_argument('--codigo', default='302133')
    ap.add_argument('--institucion', default='Universidad de Antioquia')
    ap.add_argument('--tema', default='')
    ap.add_argument('--paginas', type=int, default=4)
    a = ap.parse_args()

    d = RAIZ / 'examenes' / a.examen
    d.mkdir(parents=True, exist_ok=True)
    creados = []
    tex = d / 'examen.tex'
    if not tex.exists():
        shutil.copy(RAIZ / 'plantilla' / 'examen.tex', tex); creados.append(tex)
    js = d / 'examen.json'
    if not js.exists():
        nombre = a.examen.split('-')
        titulo = ' '.join(nombre[:2]).capitalize() if len(nombre) >= 2 else a.examen
        esqueleto = {
            'curso': a.curso, 'codigo': a.codigo, 'institucion': a.institucion,
            'examen': titulo, 'tema': a.tema, 'paginas': a.paginas,
            'distribucion': [f'página {i + 1}: …' for i in range(a.paginas)],
            'escala_max': 5,
            'problemas': [{'n': 1, 'titulo': '…', 'enunciado': '…', 'solucion': '…',
                           'partes': [{'id': '1-a', 'txt': '…', 'max': 10}]}],
        }
        js.write_text(json.dumps(esqueleto, ensure_ascii=False, indent=2) + '\n'); creados.append(js)
    rd = d / 'README.md'
    if not rd.exists():
        rd.write_text(f'''# {a.examen}

- **Curso:** {a.curso} ({a.codigo}), {a.institucion}
- **Tema:** {a.tema or '…'}
- **Creado:** {date.today().isoformat()}
- **Fuente del examen:** `examen.tex` (o el repositorio de Overleaf: …)
- **Calificador publicado:** … (modo estudiante: el mismo enlace con `#estudiante`)

## Estado

- [ ] Examen con soluciones en `examen.tex`
- [ ] `examen.json` completo (problemas, partes y puntos)
- [ ] Calificador construido y verificado
- [ ] Calificador publicado y compartido
''')
        creados.append(rd)
    for c in creados:
        print('creado', c.relative_to(RAIZ))
    if not creados:
        print('nada que crear: la carpeta ya existe completa')


if __name__ == '__main__':
    main()
