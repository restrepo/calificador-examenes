---
name: banco-examenes
description: Banco de problemas de los exámenes de Fundamentación en Física (formato xsim). Lista los problemas, arma el banco con soluciones en PDF y monta un examen, taller o quiz con problemas elegidos, con o sin soluciones.
---

# Banco de problemas de los exámenes (xsim)

Usa esta skill cuando el profesor quiera:

- ver todos los problemas de los exámenes, con o sin soluciones («modo banco de preguntas»);
- armar un examen, supletorio, taller o quiz con algunos problemas elegidos, con o sin soluciones;
- saber qué problemas hay de un tema, cuáles ya salieron en un examen o cuáles quedaron en el banco;
- pasar un examen viejo (`\item\label{item:…}` con `comment`/`solution`) al formato xsim.

Trabaja sobre el repositorio `restrepo/calificador-examenes`: cada examen vive en `examenes/<examen>/examen.tex`, que es una copia del `main.tex` del repositorio del examen (sincronizado con Overleaf):

| Examen | Repositorio del examen | Etiqueta |
|---|---|---|
| `parcial-2-2025-2` (dinámica newtoniana) | `restrepo/Fundamentacion_en_Fisica_Parcial_2_2025-2` | `parcial2` |
| `parcial-3-2025-2` (electromagnetismo) | `restrepo/FF_examen3` | `parcial3` |

Si no estás dentro de un clon de ese repositorio, clónalo primero (es público) y trabaja desde su raíz:

```bash
git clone --depth 1 https://github.com/restrepo/calificador-examenes /tmp/ce && cd /tmp/ce
```

Si el profesor cambió el examen en Overleaf, primero trae el `main.tex` actualizado de ese repositorio a `examenes/<examen>/examen.tex`.

## El formato xsim del curso

Cada problema es un entorno `exercise` con su `solution` justo debajo:

```latex
\begin{exercise}[ID=coulomb-nulo, subtitle={Punto de fuerza nula}, tags={parcial3}, points=25, nuevapagina=true]
  Enunciado...
\end{exercise}
\begin{solution}
  Solución...
\end{solution}
```

- `ID` es único dentro del examen. `subtitle`, `points` y `nuevapagina=true` (empieza en página nueva) son opcionales.
- El bloque «Selección del examen» del preámbulo decide qué se imprime: `\xsimsetup{tags={parcial3}}` imprime solo los problemas con esa etiqueta. Los demás (`tags={banco}`) quedan guardados en el banco. Para mover un problema entre el examen y el banco se cambia solo su etiqueta.
- `\solucionestrue` imprime el solucionario (y lo que va dentro de `\phantom`). `\mostrarpuntosfalse` oculta «(25 puntos)».
- Las partes de un problema que no se preguntan van en `\begin{comment}…\end{comment}` dentro del problema.
- El bloque estándar está en `assets/bloque-xsim.tex`. La plantilla de examen nuevo es `plantilla/examen.tex`, la misma del proyecto de Overleaf «Plantilla de examen (xsim)» (https://www.overleaf.com/project/6b0862db0a86c5748e890b7f/share#9b7bf43e27cdfb83fce83ef8612a49fe7169d6c17608c4f7), sincronizado con `restrepo/exam_template`. Para un examen nuevo en Overleaf, sugiere copiar ese proyecto y pegar ahí lo que produzca `armar`.

## El script

`scripts/banco.py`, desde la raíz del repositorio (`B=.claude/skills/banco-examenes/scripts/banco.py`). Sin archivos, usa todos los `examenes/*/examen.tex` en formato xsim. Compila con `pdflatex` (TeX Live con `texlive-lang-spanish`, `xsim` y `environ`). Escribe los `.tex` y PDF en una carpeta de trabajo fuera del repositorio.

| Tarea | Comando |
|---|---|
| Tabla de problemas: clave, examen, si se imprime, puntos, etiquetas y título | `python3 -B $B listar` |
| Banco completo con soluciones (PDF) | `python3 -B $B banco -o /tmp/banco/banco.tex` |
| Solo enunciados | `... banco --sin-soluciones -o …` |
| Solo una etiqueta (p. ej. lo que quedó en el banco) | `... banco --tag banco -o …` |
| Examen nuevo con problemas elegidos | `python3 -B $B armar --ids "caida,impulso\|coulomb-nulo\|balmer" --etiqueta repaso --titulo "Taller de repaso" -o /tmp/banco/repaso.tex` |
| El mismo, con soluciones | añadir `--soluciones` |
| Cambiar puntos | `--puntos caida=20,impulso=20,coulomb-nulo=30,balmer=30` |
| Pasar un examen viejo a xsim | `python3 -B $B convertir viejo.tex nuevo.tex --etiqueta parcial4 --puntos a=25,b=25` |

En `--ids`, la coma separa problemas de la misma página y `|` empieza una página nueva. Si un ID se repite en dos exámenes, se escribe `EXAMEN:ID` (por ejemplo `parcial-2-2025-2:montana`); `listar` muestra la clave que hay que usar.

`armar` deja un examen completo en el mismo formato xsim. Ese archivo puede ser el `examen.tex` de un examen nuevo, o pegarse en Overleaf.

## Flujo

1. **Ver qué hay.** Ejecuta `listar` y muestra al profesor la tabla, agrupada por examen o por tema si ayuda. Si pidió «el banco» o «todos los problemas», genera `banco` con soluciones y envíale el PDF con `SendUserFile`.
2. **Elegir.** Si el profesor describe lo que quiere («un quiz de energía con dos problemas»), propone problemas concretos de la tabla, con su clave y puntos, y confírmalos antes de armar, salvo que ya los haya nombrado.
3. **Armar.** Ejecuta `armar` con los IDs en el orden y la paginación pedidos. Genera la versión sin soluciones y, si la pidió, la versión con soluciones. El script avisa si hay errores de LaTeX y cuenta las páginas.
4. **Revisar.** Rasteriza las páginas (`pdftoppm -r 50`) y míralas: que ninguna figura se salga de la página, que la numeración y los literales a), b) estén bien y que los puntos sumen lo que espera el profesor.
5. **Entregar.** Envía el PDF (y el `.tex` si lo va a editar en Overleaf) con `SendUserFile`. Dile cuántos problemas tiene, de qué exámenes salieron y el total de puntos.
6. **Si es un examen nuevo del curso.** Crea su carpeta con `python3 -B scripts/nuevo_examen.py <examen> --tema "…" --paginas N`, guarda el resultado de `armar` como `examenes/<examen>/examen.tex`, y sigue con la skill `calificador-parcial` para el calificador. Haz commit y push solo de `examen.tex`, `examen.json` y `README.md`.

## Notas

- **Problema nuevo para el banco.** Agrégalo al `examen.tex` del examen al que pertenece con `tags={banco}` y su solución, y también al `main.tex` de su repositorio de Overleaf, para que las dos copias no se separen.
- **Si un `examen.tex` no está en xsim,** `listar` no lo ve. Conviértelo con `convertir`, compílalo y compáralo con el PDF original (mismo número de páginas y mismo texto con `pdftotext`) antes de reemplazarlo.
- **Problemas técnicos de xsim que el bloque estándar ya resuelve:**
  - En español, babel activa `<` y `>`, y eso rompía opciones de TikZ como `>=stealth`; el bloque desactiva esos atajos.
  - El paquete `comment` no funciona dentro de un `exercise`, así que el bloque define `comment` con `environ`.
  - No quites esas líneas.
- **Notas de clase.** Con el tiempo, todos los problemas y soluciones del banco se sincronizarán con las notas de clase (`restrepo/Derivaci-n-de-las-transformaciones-de-Lorentz`): cuando agregues o cambies un problema, ofrece llevarlo también al capítulo correspondiente y su solución al apéndice.
- **Privacidad.** Los problemas y soluciones son públicos; los datos de los estudiantes nunca se suben.
