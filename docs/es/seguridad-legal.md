# Seguridad y legal

OpenReplica reconstruye funciones y flujos. No copia activos propietarios. Esa
distinción no es un detalle técnico: es la base para que el resultado pueda
publicarse sin arrastrar la propiedad intelectual de otra persona.

Esta página resume las reglas del pack. No es asesoría legal. Si hay dinero en
juego, consulta a un abogado antes de lanzar.

## Copia limpia

Qué significa en la práctica:

- Se estudian páginas públicas, capturas y el comportamiento visible.
- Se escriben de nuevo el código, los textos, los estilos y los componentes.
- No se copia el código fuente de la original, ni sus assets, ni su logo, ni
  sus fuentes, ni sus ilustraciones, ni sus textos.
- No se usan APIs privadas ni se extraen datos de una cuenta ajena.

Lo que se reconstruye es la función: reservar una cita, crear una lista,
compartir un enlace. Lo que no se reconstruye es el contenido que la app posee
o licencia.

## Fuentes permitidas

Permitido:

- Páginas públicas: help center, precios, blog, documentación, ficha de tienda.
- Tu propia cuenta, con tus credenciales y tu consentimiento.
- Reseñas públicas con enlace verificable.
- Capturas que tú mismo tomas de pantallas públicas.

No permitido:

- Entrar en la cuenta de otra persona.
- Saltar un muro de pago o un login.
- Hacer scraping contra los términos del sitio.
- Usar datos privados, filtraciones o bases de datos compradas.
- Automatizar acciones que el sitio prohíbe.

Si los términos de tu cuenta prohíben usarla para construir un competidor, la
fase de recon debe decirlo y limitarse a fuentes públicas. La comodidad no
justifica romper el contrato.

## Marcas y confusión

Antes de lanzar:

- Comprueba el nombre en el registro de marcas de tu jurisdicción.
- Comprueba el dominio y los perfiles sociales.
- No uses un nombre que suene igual o se escriba casi igual que el original.
- No uses su logo, sus colores característicos ni su eslogan.
- No afirmes ser la app original ni tener relación con ella.

La fase de marca entrega una lista de comprobaciones. Ejecutarla es tu
responsabilidad. El barrido de código detecta nombres y colores, pero no
sustituye una búsqueda de marcas.

## Derechos de autor y licencias

Reconstruir una función no te da derecho al contenido de la original. Un
catálogo de música, una base de datos de recetas, un directorio de profesionales
o un conjunto de imágenes tienen sus propias licencias.

Revisa también las licencias de todo lo que uses:

- fuentes,
- iconos,
- imágenes,
- librerías,
- plantillas,
- APIs de terceros.

La fase de diseño prefiere fuentes e iconos abiertos precisamente para evitar
este problema. Si eliges un recurso con licencia restrictiva, el coste legal es
tuyo.

## Reseñas y datos de usuarios

La fase Entrepreneur lee reseñas públicas. Sus reglas:

- Cada cita debe ser literal y tener un enlace.
- No se inventan reseñas, valoraciones, fechas ni fuentes.
- Se declara el tamaño de la muestra.
- Se descartan las filas sin enlace.
- No se publican datos personales de los autores más allá de lo que ya es
  público y necesario para citar.

Si recopilas reseñas a mano, guarda solo lo necesario. No subas exportaciones
con correos, teléfonos o identificadores privados al repositorio.

## Secretos y credenciales

- No escribas claves en `replica/`, en las skills ni en capturas.
- Usa `.env` para local y `.env.example` para documentar variables.
- No subas `.env` al repositorio.
- El agente pide confirmación antes de `git push`, `gh`, `curl` y `npm publish`.
- Revisa el diff antes de publicar.

Si una clave se filtra, revócala primero y limpia el historial después. Borrar
el archivo no basta si ya está en un commit.

## Capturas y datos de terceros

Las capturas de la app original pueden contener nombres, fotos o datos de
usuarios. Úsalas solo para análisis interno. No las publiques en la landing, en
la ficha de tienda ni en el repositorio público. La fase de marca debe
reemplazarlas por capturas de tu propio clon.

## Publicación

Antes de desplegar:

- Tests en verde.
- Paridad mínima de 80.
- Barrido de marca limpio.
- Ficha de tienda sin errores.
- Sin secretos en el repositorio.
- Términos y política de privacidad revisados.

La puerta de deploy comprueba lo técnico. Lo legal y lo comercial sigue siendo
tu decisión.

## Uso responsable

No uses OpenReplica para:

- suplantar una app existente,
- engañar a usuarios,
- copiar contenido protegido,
- extraer datos privados,
- atacar o sobrecargar un servicio.

La herramienta está pensada para reconstruir funciones y competir con un
producto propio, con marca propia y con evidencia verificable.

## Créditos y licencia

OpenReplica es un fork de The Replica skill de Jake Schincariol, publicado bajo
licencia MIT. El copyright original se conserva en `LICENSE` y la atribución en
`NOTICE`. Las modificaciones de este fork también se publican bajo MIT.
