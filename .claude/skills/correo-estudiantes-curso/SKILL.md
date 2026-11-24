---
name: "correo-estudiantes-curso"
description: "Envía un correo a los estudiantes del curso Fundamentación en Física en CCO, con cada destinatario como NOMBRE COMPLETO y su correo institucional entre ángulos, tomando la lista del último correo enviado al curso."
---

# Correo a los estudiantes del curso (CCO)

Úsala cuando el profesor pida avisar algo a los estudiantes del curso Fundamentación en Física: fecha de un examen, notas, cambios de clase, supletorios, etc.

## 1. Obtener la lista vigente de estudiantes

La lista no se guarda en ningún archivo ni repositorio: se toma del último correo que el profesor envió al curso en CCO, porque ahí ya están quitados los estudiantes que cancelaron.

1. Busca en Gmail (`search_threads`, vista `THREAD_VIEW_METADATA_ONLY`):
   `in:sent ("Fundamentación en Física" OR fundamentación) newer_than:120d`
2. Entre los mensajes enviados por el profesor, elige el **más reciente que tenga destinatarios en CCO** (`bccRecipients` no vacío). Si dos correos recientes tienen listas distintas, usa la del más reciente y menciónalo en la respuesta (quién entró o salió).
3. Con `get_message` de ese mensaje, arma cada destinatario con `addressDisplayNames`:
   `NOMBRE COMPLETO <correo@udea.edu.co>`
   - El nombre va tal cual aparece (en mayúsculas sostenidas, como en la lista de la universidad).
   - El correo se copia **carácter por carácter** desde `bccRecipients`: sin quitar puntos, guiones ni números (`yezikax.acosta@udea.edu.co`, `j.barrientos1@udea.edu.co`). Nunca se reescribe a mano.
   - Si a un correo le falta el nombre, usa solo `<correo>` y avísalo.
4. Excluye al propio profesor de la lista de CCO.
5. Si el profesor da una lista nueva (pegada o adjunta), úsala en lugar de la del correo, con el mismo formato.

## 2. Verificar la lista antes de enviar

- Cada entrada debe cumplir `^[^<>]+ <[a-z0-9._%+-]+@udea\.edu\.co>$` (o `<…>` solo).
- Compara los correos con los de `bccRecipients`: deben coincidir exactamente (mismo número, mismos puntos).
- No debe haber duplicados.

## 3. Redactar el correo

Estilo del profesor: corto, en español de Colombia, sin adornos.

```
Asunto: <Tema> - Fundamentación en Física

Hola a todos
<Aviso en una o dos frases, con día de la semana y fecha.>

Saludos
Diego
```

- Revisa que el día de la semana corresponda a la fecha (usa la herramienta de fecha actual).
- No inventes hora, lugar ni temas que el profesor no haya dado.
- Ejemplo de asunto: «Parcial capítulo 4 - Fundamentación en Física».

## 4. Enviar

Con `send_message` de Gmail:
- `to`: el correo del propio profesor (así nadie ve los demás correos).
- `bcc`: la lista en formato `NOMBRE COMPLETO <correo>` (Gmail acepta ese formato y conserva el nombre).
- `subject` y `body` en texto plano.

Si el profesor pidió revisar antes, crea un borrador (`create_draft`) en lugar de enviar.

## 5. Comprobar y reportar

- Lee el mensaje enviado con `get_message` (`METADATA_ONLY`) y confirma que `bccRecipients` tiene el mismo número de correos que la lista y que los correos coinciden.
- Responde en una o dos frases: asunto, número de estudiantes en CCO y de qué correo salió la lista. No pegues la lista de correos en la respuesta salvo que la pidan.

## Privacidad

Los nombres y correos de los estudiantes no se suben a repositorios, proyectos ni memoria.