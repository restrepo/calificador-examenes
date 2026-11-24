---
name: completar-documento-latex
description: >-
  Convierte un fragmento de código LaTeX (subido como archivo .tex, documento
  adjunto, o pegado directamente en el prompt) en un documento LaTeX completo
  y compilable, agregando \documentclass, un preámbulo con los paquetes
  necesarios (un preset base fijo más extras detectados automáticamente
  según los comandos usados en el fragmento), \begin{document}/\end{document},
  y compilándolo a PDF. Usa esta skill SIEMPRE que el usuario suba o pegue un
  fragmento .tex y pida "generar el documento completo", "compilar esto",
  "pasar a PDF", "agregarle el preámbulo", "hazlo un documento LaTeX
  completo", o cuando el fragmento contenga las marcas '% begin texto
  manuscrito' / '% end texto manuscrito' (producidas por la skill
  imagen-a-latex-manuscrito) y el usuario quiera el parcial/examen como
  documento final listo para revisar. No es necesario que el usuario diga
  explícitamente "paquetes" o "preámbulo".
---

# Completar documento LaTeX (fragmento → documento compilable)

Toma un fragmento de LaTeX (solo cuerpo, sin `\documentclass` ni preámbulo) y
lo convierte en un archivo `.tex` completo y compilable, además de generar el
PDF resultante.

## Cuándo se usa

- El usuario sube/pega un fragmento `.tex` que es solo el *cuerpo* del
  documento (preguntas, texto, fórmulas), típicamente la salida de la skill
  `imagen-a-latex-manuscrito` (que incluye marcas
  `% begin texto manuscrito` / `% end texto manuscrito`).
- Pide explícitamente el documento completo, compilarlo, o el PDF final.
- También aplica a cualquier fragmento LaTeX genérico (apuntes, ejercicios,
  etc.) que no tenga esas marcas — en ese caso simplemente no hay nada que
  resaltar en color.

## Qué NO hacer

- No reescribas ni "mejores" el contenido del fragmento (texto, fórmulas,
  estructura). Tu trabajo es envolverlo en un documento válido, no editar su
  contenido — salvo los ajustes mínimos de sintaxis que hagan falta para que
  compile (ver "Si no compila").
- No elimines ni modifiques las marcas `% begin/end texto manuscrito` sin
  procesarlas correctamente (ver más abajo): deben convertirse en resaltado
  visual, no perderse ni quedar como comentario suelto sin efecto.

## Preset base de paquetes (siempre se incluyen)

```latex
\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish]{babel}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage[margin=2.5cm]{geometry}
\usepackage{enumitem}
\usepackage{xcolor}
```

(Si el fragmento está en otro idioma, ajusta la opción de `babel` en
consecuencia; si no puedes determinarlo, deja `spanish` por defecto salvo que
el usuario indique lo contrario.)

## Detección automática de paquetes extra

Antes de armar el preámbulo, escanea el fragmento buscando comandos/entornos
que requieran paquetes fuera del preset base, y agrégalos solo si aparecen:

| Si el fragmento usa... | Agregar paquete |
|---|---|
| `\includegraphics` | `graphicx` |
| `tabularx`, `\newcolumntype` | `tabularx`, `array` |
| entorno `tikzpicture` | `tikz` |
| `\url`, `\href` | `hyperref` (cargar de último en el preámbulo) |
| entorno `multicols` | `multicol` |
| `\ce{...}` (fórmulas químicas) | `mhchem` |
| entorno `algorithm`/`algorithmic` | `algorithm`, `algorithmic` |
| `\SI{...}{...}`, unidades | `siunitx` |
| `\emoji`, símbolos raros no cubiertos por amssymb | revisa el símbolo puntual y añade el paquete correspondiente (p. ej. `stmaryrd`, `bbding`) |

No agregues paquetes "por si acaso": solo los que el contenido realmente usa.
Si tienes dudas sobre qué paquete provee un comando puntual, puedes buscarlo
antes de compilar.

## Manejo del texto manuscrito (resaltado en color)

Si el fragmento contiene bloques `% begin texto manuscrito` / `% end texto
manuscrito`, en el preámbulo define:

```latex
\newenvironment{manuscrito}{\color{blue}}{\color{black}}
```

y reemplaza cada par de marcas por el entorno correspondiente:

```latex
% begin texto manuscrito
$x = 12 - 5 = 7$
% end texto manuscrito
```

se convierte en:

```latex
\begin{manuscrito}
$x = 12 - 5 = 7$
\end{manuscrito}
```

Reglas:

- Un bloque manuscrito por cada par de marcas; no fusiones bloques separados
  ni dejes marcas sin convertir.
- El entorno funciona igual dentro de texto normal, listas y modo matemático
  (`\color` de `xcolor` afecta también fórmulas), así que no necesitas
  tratamiento especial para `$...$` dentro del bloque.
- Si el fragmento no trae estas marcas, omite el entorno `manuscrito` del
  preámbulo (no hace falta definirlo si no se usa).

## Proceso paso a paso

1. Lee el fragmento completo (con `view` si es un archivo).
2. Escanea qué comandos/entornos usa para decidir los paquetes extra
   (tabla anterior).
3. Arma el preámbulo: preset base + extras detectados + (si aplica) el
   entorno `manuscrito`.
4. Convierte cada par `% begin/end texto manuscrito` en
   `\begin{manuscrito}...\end{manuscrito}`.
5. Ensambla el documento completo:
   ```latex
   <preámbulo>
   \begin{document}
   <cuerpo procesado>
   \end{document}
   ```
6. Guarda el `.tex` en el directorio de trabajo y compílalo (ver siguiente
   sección).
7. Entrega `.tex` y `.pdf` al usuario con la herramienta de presentación de
   archivos.

## Compilación a PDF

Compila con `pdflatex` (ya disponible en el entorno) corriéndolo dos veces
para resolver referencias:

```bash
cd /directorio/de/trabajo
pdflatex -interaction=nonstopmode archivo.tex
pdflatex -interaction=nonstopmode archivo.tex
```

### Si no compila

- Lee el log (`archivo.log` o la salida de la terminal) para identificar el
  error.
- Si es un paquete faltante, instálalo con `tlmgr install <paquete>` (o
  `apt-get install -y texlive-lang-spanish` etc. si `tlmgr` no está
  configurado) y vuelve a compilar.
- Si es un error de sintaxis dentro del fragmento original (delimitador de
  fórmula sin cerrar, entorno mal balanceado), corrígelo con el cambio mínimo
  necesario para que compile, y menciona brevemente al usuario qué corregiste
  y por qué (recuerda: no se trata de "arreglar" el contenido matemático del
  estudiante si el fragmento viene de un examen — solo la sintaxis LaTeX).
- Si tras 2-3 intentos no logras compilar, entrega igualmente el `.tex` y
  muestra el error relevante del log para que el usuario decida cómo seguir.

## Formato de salida

Entrega siempre el archivo `.tex` completo. Si la compilación fue exitosa,
entrega también el `.pdf`. Usa la herramienta de presentación de archivos
para que el usuario pueda abrir/descargar ambos.
