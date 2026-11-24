#!/usr/bin/env python3
"""Empaqueta las skills de .claude/skills/ como archivos .skill en dist/.

Determinista (fecha fija y orden alfabético): si una skill no cambió, su
.skill tampoco. Además arma dist/skills-calificador-examenes.zip con todas.

Uso, desde la raíz del repositorio:
    python3 -B scripts/empaquetar_skills.py
"""
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FECHA = (2020, 1, 1, 0, 0, 0)


def agrega(z, nombre, datos):
    info = zipfile.ZipInfo(nombre, FECHA)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    z.writestr(info, datos)


def archivos(carpeta):
    return sorted(p for p in carpeta.rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.pyc'))


def main():
    dist = RAIZ / 'dist'
    dist.mkdir(exist_ok=True)
    skills = sorted(p for p in (RAIZ / '.claude' / 'skills').iterdir() if (p / 'SKILL.md').exists())
    for s in skills:
        destino = dist / f'{s.name}.skill'
        with zipfile.ZipFile(destino, 'w') as z:
            for p in archivos(s):
                agrega(z, f'{s.name}/{p.relative_to(s).as_posix()}', p.read_bytes())
        print(f'{destino.relative_to(RAIZ)}  {destino.stat().st_size / 1024:,.0f} KB')
    todo = dist / 'skills-calificador-examenes.zip'
    with zipfile.ZipFile(todo, 'w') as z:
        for s in skills:
            agrega(z, f'skills-calificador-examenes/{s.name}.skill', (dist / f'{s.name}.skill').read_bytes())
    print(f'{todo.relative_to(RAIZ)}  {todo.stat().st_size / 1024:,.0f} KB')


if __name__ == '__main__':
    main()
