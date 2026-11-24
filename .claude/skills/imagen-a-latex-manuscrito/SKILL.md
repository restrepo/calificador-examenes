---
name: imagen-a-latex-manuscrito
description: Convierte una o varias imágenes de un examen/parcial (enunciado impreso con el desarrollo del estudiante escrito a mano encima) en un fragmento de código LaTeX, marcando con comentarios el texto manuscrito para diferenciarlo del texto impreso. Usa esta skill SIEMPRE que el usuario suba una foto o imagen de un examen, parcial, taller o formulario con partes impresas y partes manuscritas y pida "convertir a LaTeX", "pasar a LaTeX", "transcribir", "digitalizar" el documento, o mencione distinguir/marcar el texto manuscrito del impreso. También aplica si solo pide "transcribe este parcial" o "pasa esto a texto" cuando la imagen adjunta muestra un examen con desarrollo escrito a mano. No es necesario que el usuario diga la palabra "LaTeX" explícitamente si el contexto es claramente digitalizar un examen corregido o resuelto a mano.
---

# Imagen de examen a LaTeX (impreso vs. manuscrito)

Transcribe el contenido de una o varias imágenes de un examen/parcial a un
fragmento de LaTeX, preservando toda la estructura (enunciados, preguntas,
numeración, fórmulas) y marcando explícitamente qué partes fueron escritas a
mano por el estudiante.

## Cuándo se usa

- El usuario sube imagen(es) de un parcial/examen impreso que un estudiante
  resolvió a mano encima del enunciado.
- Pide transcribir, digitalizar o pasar a LaTeX ese contenido.
- Puede haber varias imágenes correspondientes a distintas páginas de un mismo
  examen — en ese caso se procesan en el orden en que se suben (o el orden
  que indique el usuario) y se concatenan en un solo fragmento.

## Qué NO hacer

- No generar un documento LaTeX completo (`\documentclass`, `\begin{document}`,
  etc.). La salida es solo el fragmento/cuerpo del contenido, listo para
  pegar dentro de un documento existente.
- No "corregir" ni completar lo que el estudiante escribió. Si una fórmula
  está mal planteada o el resultado es incorrecto, transcríbela tal cual
  aparece — el objetivo es preservar el desarrollo real del estudiante para
  que después se pueda corregir o calificar, no arreglarlo.
- No omitir el nombre, identificación u otros datos manuscritos que aparezcan
  al inicio del examen — deben transcribirse igual que el resto del
  desarrollo manuscrito.

## Cómo marcar el texto manuscrito

Cada bloque de texto manuscrito (contiguo) se envuelve así:

```latex
% begin texto manuscrito
... contenido transcrito ...
% end texto manuscrito
```

Reglas:

- El texto **impreso** (enunciados originales del examen) se transcribe
  como LaTeX normal, **sin** ningún comentario alrededor.
- El texto **manuscrito** (todo lo que el estudiante escribió a mano: nombre,
  identificación, desarrollo, respuestas, anotaciones al margen) va envuelto
  entre `% begin texto manuscrito` y `% end texto manuscrito`.
- Si dentro de una misma pregunta se alterna impreso y manuscrito varias
  veces (p. ej. el enunciado impreso de la parte b) después de la respuesta
  manuscrita de la parte a)), abre y cierra el par de comentarios cada vez
  que cambie el tipo de texto. No dejes un bloque manuscrito "abierto" que
  en realidad contenga texto impreso en medio.
- No anides pares de comentarios. Cada bloque manuscrito tiene un único
  `begin` y un único `end`.

## Si el usuario aporta el LaTeX del documento impreso

Si en la conversación el usuario ya compartió (o comparte en cualquier
momento) el código LaTeX original del examen/formulario impreso —por ejemplo
porque él mismo lo diseñó—, **úsalo como base** en lugar de reconstruir el
texto impreso desde cero a partir de la imagen:

- Toma ese código como la fuente de verdad para todo el texto impreso
  (enunciados, tabla, justificaciones, etiquetas como "Nombre:", etc.).
- Rellena únicamente las partes que en ese código aparecen en blanco o como
  marcador de espacio (p. ej. `\phantom{...}`, `\underline{\hspace{...}}`,
  `\hrulefill`, celdas vacías) con el contenido manuscrito correspondiente,
  envuelto en `% begin texto manuscrito` / `% end texto manuscrito`, siguiendo
  las reglas de la sección anterior sobre no compartir línea con contenido
  impreso.
- **Recuerda ese LaTeX impreso durante el resto de la conversación.** Si el
  usuario sube imágenes adicionales de otros estudiantes que corresponden al
  mismo examen/formulario (mismo enunciado impreso), reutiliza el mismo
  código base sin necesidad de que lo vuelva a pegar — solo cambia el
  contenido manuscrito según lo que muestre cada nueva imagen. Si una imagen
  nueva no calza con la fuente ya conocida (parece ser un examen distinto),
  pregunta o vuelve al modo de transcripción desde cero.
- Si el usuario **no** aporta el LaTeX impreso, transcribe el texto impreso
  directamente desde la imagen como se describe abajo. Al final de esa
  primera transcripción, puedes mencionar (brevemente, sin insistir) que si
  tiene el código LaTeX original del documento, compartirlo mejora la
  fidelidad del resultado y evita tener que reconstruir el texto impreso a
  ojo.

## Proceso

1. **Ver cada imagen** con la herramienta `view` (o el visor de imágenes
   disponible) antes de transcribir. Si hay varias páginas, revísalas todas
   antes de empezar a escribir el LaTeX, para entender la estructura completa
   del examen (numeración de preguntas, si continúan de una página a otra,
   etc.).

2. **Transcribir en orden**, preservando la estructura del documento:
   - Usa `\section*{}`, `\subsection*{}` o simplemente texto según el nivel
     jerárquico que tenga el examen (título, nombre de la materia, número de
     pregunta, sub-incisos).
   - Usa `\begin{enumerate}` / `\begin{itemize}` para preguntas numeradas o
     listas, tanto si son parte del enunciado impreso como si el estudiante
     numeró su propio desarrollo.
   - Cada bloque de texto (impreso o manuscrito) mantiene su propio formato
     natural; no fusiones dos preguntas en un solo bloque de comentario.

3. **Matemáticas manuscritas → LaTeX matemático real.** Si el estudiante
   escribió una fórmula, exponente, fracción, integral, etc., transcríbela
   usando sintaxis matemática de LaTeX correcta (`$x^2+1$`, `\frac{a}{b}`,
   `\int_0^1 f(x)\,dx`, etc.) — **aunque el contenido matemático en sí sea
   incorrecto**. Lo que se corrige es solo la sintaxis LaTeX para que
   compile; el error matemático del estudiante se preserva tal cual.

4. **Nombre e identificación del estudiante:** si aparecen manuscritos al
   inicio del examen (típicamente donde el formulario lo solicita), inclúyelos
   como texto normal dentro de su propio bloque `% begin texto manuscrito` /
   `% end texto manuscrito`, en el mismo lugar donde aparecen en la imagen.

5. **Varias imágenes/páginas:** procesa cada imagen y concatena el resultado
   en un único fragmento, en el orden correspondiente. Si es útil para la
   legibilidad, puedes separar páginas con un comentario simple como
   `% --- página 2 ---` (esto es solo una ayuda de navegación, no reemplaza
   las marcas de manuscrito/impreso).

6. **Revisa antes de entregar:** verifica que cada `% begin texto manuscrito`
   tenga su `% end texto manuscrito` correspondiente, que no haya bloques
   anidados, y que el LaTeX matemático usado sea sintácticamente válido
   (delimitadores de fórmula balanceados, comandos bien escritos).

## Formato de salida

Entrega el resultado como un archivo `.tex` (fragmento, no documento
completo) usando las herramientas de creación de archivos, y preséntaselo al
usuario. Si el examen es corto y el usuario solo quiere ver el resultado
rápido en el chat, también puedes mostrar el fragmento directamente en la
respuesta — pero si el usuario pide guardarlo, descargarlo o son varias
páginas, genera el archivo.

## Ejemplo breve

Imagina una imagen donde el enunciado impreso dice "1. Resuelva: x + 5 = 12"
y debajo, a mano, el estudiante escribió "Juan Pérez, CC 123456" arriba, y
luego "x = 12 - 5 = 7":

```latex
% begin texto manuscrito
Juan Pérez, CC 123456
% end texto manuscrito

\begin{enumerate}
  \item Resuelva: $x + 5 = 12$
\end{enumerate}

% begin texto manuscrito
$x = 12 - 5 = 7$
% end texto manuscrito
```
