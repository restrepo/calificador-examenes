# Cómo empezar a trabajar en un examen desde un chat nuevo

Hay dos formas, según dónde abras el chat.

## A. Claude Code (claude.ai/code, la app de escritorio o la terminal)

Es la forma recomendada: Claude trabaja dentro del repositorio, carga solo
las skills de `.claude/skills/` y las instrucciones de `CLAUDE.md`, y puede
hacer commit de cada examen.

1. Abre una sesión nueva y elige el repositorio `restrepo/calificador-examenes`.
   En la terminal: `git clone https://github.com/restrepo/calificador-examenes && cd calificador-examenes && claude`.
2. Pega uno de estos mensajes, cambiando lo que está entre ángulos:

   **Examen nuevo**
   > Vamos a trabajar en el examen `<parcial-3-2026-1>` sobre `<electromagnetismo>`.
   > Te adjunto el LaTeX con las soluciones (o: está en el repositorio `<usuario/repo>`).
   > Crea su carpeta, escribe el JSON y publica el calificador.

   **Examen que ya existe**
   > Sigamos con el examen `<parcial-2-2025-2>`. `<Lo que quieras hacer: cambiar la rúbrica, republicar el calificador, transcribir fotos de un estudiante…>`

   **Transcribir un examen resuelto**
   > Transcribe a LaTeX estas fotos del examen `<parcial-2-2025-2>`, usando su `examen.tex` como base, y genera el PDF.

Si la sesión es en la nube, conviene un entorno con TeX Live en español. En el
*setup script* del entorno:

```bash
#!/bin/bash
apt-get update -q && apt-get install -y -q texlive-lang-spanish texlive-xetex latexmk cm-super || true
python3 -m pip install --break-system-packages -q pillow || true
```

## B. Chat de claude.ai sin acceso al repositorio

1. Descarga las skills de [`dist/`](dist/) (o todas juntas en
   `dist/skills-calificador-examenes.zip`) y súbelas una vez en
   *Configuración → Capacidades → Skills*.
2. En un chat nuevo, adjunta el examen (`.tex`, `.zip` de Overleaf o `.pdf`)
   y escribe:
   > Prepara el calificador de este examen con la skill calificador-parcial.

La skill clona sola el kit de este repositorio si el chat tiene acceso a
GitHub; si no, usa el calificador de referencia ya publicado como base.

## Qué esperar al final

- El enlace del calificador (modo profesor) y el mismo enlace con
  `#estudiante` para los estudiantes. Compártelo desde el menú **Compartir**
  del artefacto.
- El reparto de puntos usado, las soluciones que Claude haya completado y los
  datos que haya supuesto (páginas, distribución), para que los revises.
