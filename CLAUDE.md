# Instrucciones para Claude — Calificador de exámenes

Este repositorio (`restrepo/calificador-examenes`) reúne el sistema para preparar,
calificar y dar retroalimentación de los exámenes del curso **Fundamentación en
Física** (302133, Universidad de Antioquia). Conversa con el profesor en
**español de Colombia**.

Las skills están en `.claude/skills/` y Claude Code las carga solas al abrir el
repositorio:

| Skill | Para qué |
|---|---|
| `calificador-parcial` | Del LaTeX o PDF del examen con soluciones a la página «Calificador», publicada como artefacto: modo profesor (califica fotos con la rúbrica) y modo estudiante (`#estudiante`, guía para pedir retroalimentación a Claude, ChatGPT o Gemini). |
| `imagen-a-latex-manuscrito` | Foto de un examen resuelto → LaTeX, con el texto manuscrito marcado. |
| `completar-documento-latex` | Fragmento LaTeX → documento compilable y PDF, con lo manuscrito en azul. |
| `correo-estudiantes-curso` | Correo a los estudiantes en CCO (fecha de examen, notas, supletorios). |

## Al empezar una sesión

1. `git pull`.
2. Pregunta con qué examen se va a trabajar si el profesor no lo dijo, y mira
   `examenes/` para ver si ya existe su carpeta (cada una tiene un `README.md`
   con su estado y el enlace del calificador publicado).

## Trabajar en un examen

1. **Carpeta del examen.** Si es nuevo:
   ```bash
   python3 -B scripts/nuevo_examen.py <examen> --tema "<tema>" --paginas <N>
   ```
   `<examen>` con la forma `parcial-3-2026-1`. Crea `examenes/<examen>/` con
   `examen.tex` (la plantilla), un esqueleto de `examen.json` y la ficha `README.md`.
2. **El examen.** Pon en `examen.tex` el LaTeX real del examen (pegado, adjunto,
   de Overleaf o de otro repositorio). Si se escribe desde cero, usa la
   plantilla: cada problema es un `\item\label{item:…}` con su `solution`
   debajo, y el banco de problemas va en `\begin{comment}`. Para imprimir, las
   soluciones quedan excluidas (`\excludecomment{solution}`).
3. **El JSON y el calificador.** Sigue la skill `calificador-parcial`
   (secciones 1 a 4) con `KIT=.claude/skills/calificador-parcial`:
   ```bash
   python3 -B $KIT/scripts/construir.py examenes/<examen>/examen.json /tmp/calificador-<examen>.html
   python3 -B $KIT/scripts/verificar.py /tmp/calificador-<examen>.html /tmp/caps-calificador
   ```
   El HTML construido **no** se guarda en el repositorio: se publica como
   artefacto y se anota su enlace en `examenes/<examen>/README.md`. Si el
   calificador ya existe, se republica en la misma URL.
4. **Commit y push** de `examen.tex`, `examen.json` y `README.md`.

## Calificar y retroalimentar

- **Modo profesor:** el profesor sube las fotos en el calificador publicado; la
  nota de Claude es una propuesta que él revisa. El listado de notas vive solo
  en su navegador.
- **Transcribir un examen resuelto:** `imagen-a-latex-manuscrito`, y para el PDF
  `completar-documento-latex`. Si `examen.tex` existe, úsalo como base del
  texto impreso.
- **Avisos al curso:** `correo-estudiantes-curso`.

## Privacidad

- **Nunca** se suben al repositorio fotos de exámenes resueltos, transcripciones
  de estudiantes, notas, listas de nombres, correos ni números de
  identificación. `.gitignore` bloquea los formatos habituales; si algo así
  aparece en `git status`, no lo agregues.
- El repositorio guarda exámenes con soluciones: mantenlo **privado**. Los
  estudiantes no lo necesitan; usan el enlace `#estudiante` del artefacto.

## Convenciones del curso

- Español de Colombia: computador, celular, carro.
- Leyes de Newton: «**ley de la fuerza**» ($F = \Delta p/\Delta t$) y
  «**acción y reacción**», nunca «segunda» o «tercera ley».
- Energía potencial: $U$.
- En el JSON del calificador, texto plano con Unicode y coma decimal (`9,8`).
- En el LaTeX de los exámenes, `siunitx` (`\qty`, `\num`) con **punto**
  decimal (`es-nodecimaldot`), vectores con `\boldsymbol`, y `\,` antes de la
  puntuación final de las ecuaciones centradas.

## Mantener el kit

- Si cambia el comportamiento del calificador, edita
  `.claude/skills/calificador-parcial/assets/plantilla.html`, reconstruye el
  ejemplo (`examenes/parcial-2-2025-2/examen.json`) y verifícalo.
- Después de cambiar cualquier skill, reempaqueta para claude.ai:
  ```bash
  python3 -B scripts/empaquetar_skills.py
  ```
  Deja los `.skill` y `dist/skills-calificador-examenes.zip` en `dist/`.
- Nada de `__pycache__` en el repositorio (usa `python3 -B`).
