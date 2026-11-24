# Calificador de exámenes · Fundamentación en Física

Sistema para preparar, calificar y retroalimentar los exámenes del curso
**Fundamentación en Física** (302133, Universidad de Antioquia) con Claude.

Para cada examen se construye una página **«Calificador»**, publicada como
artefacto de claude.ai, con dos modos:

- **Profesor:** se suben las fotos del examen resuelto; Claude lee las
  respuestas y propone los puntos de cada apartado según la rúbrica, con una
  justificación. El profesor corrige y la nota se recalcula. Las notas se
  copian como tabla para la hoja de notas.
- **Estudiante** (el mismo enlace con `#estudiante`): una guía para pedir
  retroalimentación a Claude, ChatGPT o Gemini con los enunciados, las
  soluciones, la rúbrica y las convenciones de LaTeX del curso. Funciona con
  cuentas gratuitas.

## Empezar desde un chat nuevo de Claude

Ver [`COMENZAR.md`](COMENZAR.md): instrucciones para Claude Code (en la web,
el escritorio o la terminal) y para un chat de claude.ai sin acceso al
repositorio.

La versión corta, en una sesión de Claude Code con este repositorio:

> Vamos a trabajar en el examen `parcial-3-2026-1` de electromagnetismo. Te
> paso el LaTeX con las soluciones. Prepara el calificador.

## Contenido

```
CLAUDE.md                         instrucciones que Claude lee al abrir el repositorio
COMENZAR.md                       cómo arrancar desde un chat nuevo
.claude/skills/
  calificador-parcial/            plantilla del calificador, scripts y ejemplo
  imagen-a-latex-manuscrito/      foto de examen resuelto → LaTeX (manuscrito marcado)
  completar-documento-latex/      fragmento LaTeX → documento y PDF
  correo-estudiantes-curso/       correo a los estudiantes en CCO
plantilla/examen.tex              plantilla de examen: banco de problemas y soluciones conmutables
examenes/<examen>/                un examen: examen.tex, examen.json y su ficha README.md
  parcial-2-2025-2/               ejemplo: Parcial 2, dinámica newtoniana
scripts/nuevo_examen.py           crea la carpeta de un examen nuevo
scripts/empaquetar_skills.py      empaqueta las skills en dist/
dist/                             skills empaquetadas (.skill) para subir a claude.ai
```

## Flujo de un examen

1. `python3 -B scripts/nuevo_examen.py parcial-3-2026-1 --tema electromagnetismo --paginas 4`
2. Poner el LaTeX del examen con soluciones en `examenes/parcial-3-2026-1/examen.tex`.
3. Claude escribe `examen.json` (problemas, apartados y puntos) y construye el
   calificador:
   ```bash
   KIT=.claude/skills/calificador-parcial
   python3 -B $KIT/scripts/construir.py examenes/parcial-3-2026-1/examen.json /tmp/calificador.html
   python3 -B $KIT/scripts/verificar.py /tmp/calificador.html /tmp/caps
   ```
4. Claude lo publica como artefacto y anota el enlace en la ficha del examen.

Requisitos para construir y verificar: Python 3, `npm` (descarga KaTeX
0.16.9) y `playwright` con Chromium. Para compilar los exámenes: TeX Live con
`texlive-lang-spanish`.

## Privacidad

Aquí no se suben fotos de exámenes resueltos, notas, nombres, correos ni
números de identificación de estudiantes. Como el repositorio guarda las
soluciones de los exámenes, debe ser **privado**.

## Relacionado

- Lecciones interactivas del curso: <https://restrepo.github.io/fundamentacion_en_fisica/>
- Notas del curso (LaTeX): `restrepo/Derivaci-n-de-las-transformaciones-de-Lorentz`
- Ejemplos reales del modo estudiante: sección 6 de
  `.claude/skills/calificador-parcial/SKILL.md`.
