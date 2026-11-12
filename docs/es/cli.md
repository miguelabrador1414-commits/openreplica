# Referencia del CLI

El comando `replica` tiene dos capas: los comandos de proyecto (`init`,
`status`, `gate`, `mark`, `doctor`, `capture`, `extract`) y las herramientas
deterministas que se reenvían tal cual (`imgdiff`, `parity`, `sweep`,
`contrast`, `reviews`, `listing`).

```bash
replica --help
replica <comando> --help
```

Todos los comandos aceptan `--root` cuando trabajan sobre el estado de un
proyecto. Por defecto usan el directorio actual.

Si instalaste solo en un proyecto y `replica` no está en el `PATH`, usa
`.opencode/bin/replica` desde la raíz de ese proyecto:

```bash
.opencode/bin/replica status
```

## init

Crea `replica/state.json` y la carpeta de trabajo.

```bash
replica init
replica init /ruta/al/proyecto --name "Mi App"
replica init --force
```

| Opción | Efecto |
| --- | --- |
| `path` | Proyecto destino. Por defecto `.`. |
| `--name` | Nombre visible del proyecto. |
| `--force` | Reemplaza un estado existente. |

Sin `--force`, si ya existe un estado, falla para no borrar evidencia.

## status

Muestra la fase actual, el estado de las once fases y la siguiente.

```bash
replica status
replica status --json
replica status --root /ruta/al/proyecto
```

`--json` sirve para que otro programa lea el estado sin analizar texto.

## gate

Comprueba la evidencia de una fase.

```bash
replica gate recon
replica gate deploy --json
```

Sale con código 0 si pasa y 2 si está bloqueada. La salida lista los archivos o
valores que faltan. No modifica el estado.

## mark

Actualiza el estado de una fase.

```bash
replica mark recon in_progress
replica mark recon passed --notes "18 pantallas, 7 flujos"
replica mark build passed --artifact app/page.tsx --artifact app/book/page.tsx
replica mark build passed --model opencode/deepseek-v4.1-flash-free
```

| Opción | Efecto |
| --- | --- |
| `phase` | Una de las once fases. |
| `status` | `pending`, `in_progress`, `blocked` o `passed`. |
| `--notes` | Nota libre para la fase. |
| `--artifact` | Artefacto asociado. Se puede repetir. |
| `--model` | Modelo usado en esa fase. |

`mark` no ejecuta la puerta. Marcar `passed` sin pasar `gate` deja un estado
falso. El flujo correcto es `gate` primero y `mark` después.

## doctor

Revisa el entorno y la instalación.

```bash
replica doctor
replica doctor --json
```

Comprueba Python, git, node, Playwright, el estado del proyecto, el `PATH` y la
presencia de los archivos de opencode. Sale con 0 si todo lo importante está
bien y 1 si falta algo.

Playwright es opcional. Que no esté no invalida la instalación; solo desactiva
la captura real.

## capture

Captura una URL o un fixture local.

```bash
replica capture https://example.com
replica capture https://example.com --viewport desktop=1440x900 --viewport mobile=390x844
replica capture fixture --fixture tests/fixtures/site --backend stub
replica capture https://example.com --backend playwright --allow-network
replica capture https://example.com --backend manual
```

| Opción | Efecto |
| --- | --- |
| `url` | URL o nombre lógico de la captura. |
| `--out` | Carpeta de salida. Por defecto `replica/screens`. |
| `--backend` | `auto`, `stub`, `playwright` o `manual`. |
| `--fixture` | HTML o carpeta con `index.html`, `styles.json` y `screens/`. |
| `--allow-network` | Permiso explícito para usar la red. |
| `--viewport` | `nombre=ANCHOxALTO`, repetible. |

`auto` usa Playwright solo si está instalado y se pasó `--allow-network`. Si no,
usa el fixture o prepara una captura manual. Nunca descarga Chromium.

## extract

Lee un HTML y extrae rutas, controles, colores y fuentes.

```bash
replica extract pagina.html
replica extract pagina.html --json
```

Sirve para pasar de una captura estática a datos que la fase de diseño puede
usar. No ejecuta JavaScript ni abre un navegador.

## imgdiff

Compara dos capturas PNG.

```bash
replica imgdiff original.png clon.png
replica imgdiff original.png clon.png --mode pixel --out diff.png
replica imgdiff original.png clon.png --json --fail-under 80
```

| Opción | Efecto |
| --- | --- |
| `--mode layout` | Compara estructura, ignora color. Es el modo por defecto. |
| `--mode pixel` | Compara píxeles con tolerancia. |
| `--width` | Ancho de comparación. Por defecto 480. |
| `--cols` | Columnas de la rejilla. Por defecto 12. |
| `--tolerance` | Diferencia por canal ignorada en modo pixel. Por defecto 24. |
| `--out` | Escribe una imagen de diferencias. |
| `--json` | Salida JSON para parity. |
| `--fail-under` | Sale con 1 si la nota queda por debajo. |

El modo `layout` convierte las imágenes en mapas de bordes: así un color nuevo
no penaliza si la estructura coincide.

## parity

Puntúa la matriz de funciones.

```bash
replica parity replica/features.csv
replica parity replica/features.csv --visual replica/diffs/*.json --markdown
replica parity replica/features.csv --fail-under 80
```

| Opción | Efecto |
| --- | --- |
| `--visual` | Lee salidas JSON de `imgdiff` y las incorpora. |
| `--markdown` | Imprime un informe en Markdown. |
| `--json` | Salida JSON. |
| `--fail-under` | Sale con 1 si la nota queda por debajo. |

Los must pesan más que los should, y los should más que los could. Una función
parcial cuenta la mitad. Lo que dejaste fuera a propósito no resta.

## contrast

Comprueba contraste WCAG.

```bash
replica contrast replica/design/tokens.json
replica contrast "#ffffff" "#111111"
replica contrast "#ffffff" "#111111" --json
```

Acepta un archivo de tokens o dos colores hexadecimales. En tokens revisa las
parejas definidas. Marca AA y AAA según corresponda.

## sweep

Busca el nombre, dominio o colores de la original en el código.

```bash
replica sweep .
replica sweep . --avoid "Original App" --domains original.com
replica sweep . --config replica/brand.json
replica sweep . --include-replica --json
```

| Opción | Efecto |
| --- | --- |
| `--avoid` | Nombres separados por coma. |
| `--domains` | Dominios separados por coma. |
| `--colors` | Colores hexadecimales separados por coma. |
| `--config` | JSON con listas `avoid`, `domains` y `colors`. |
| `--include-replica` | Incluye la carpeta `replica/` en el barrido. |
| `--json` | Salida JSON. |

Por defecto ignora dependencias, binarios, locks y carpetas de planificación.

## reviews

Ordena reseñas reales en quejas y peticiones.

```bash
replica reviews replica/reviews.csv
replica reviews replica/reviews.csv --out replica/feedback.md
replica reviews replica/reviews.csv --months 12 --today 2026-11-12
```

| Opción | Efecto |
| --- | --- |
| `--themes` | JSON de temas. Por defecto el del pack. |
| `--months` | Reseñas más viejas cuentan la mitad. Por defecto 18. |
| `--today` | Fecha para resultados reproducibles. |
| `--out` | Escribe el informe Markdown. |
| `--json` | Salida JSON. |

El CSV necesita `source,url,date,rating,text`. Las filas sin enlace se
descartan. Cada cita sale literal y con su URL.

## listing

Revisa una ficha de tienda.

```bash
replica listing replica/listing.json
replica listing replica/listing.json --avoid "Original App"
replica listing replica/listing.json --json
```

Comprueba límites de App Store y Google Play, afirmaciones en el título,
caracteres de palabras clave desperdiciados y nombres prohibidos.

## Códigos de salida

| Código | Significado |
| --- | --- |
| 0 | Todo bien o puerta pasada. |
| 1 | `doctor` encontró un problema o una herramienta no alcanzó `--fail-under`. |
| 2 | Error de uso, estado ausente o puerta bloqueada. |
| 130 | Cancelado con Ctrl+C. |

## Variables de entorno

| Variable | Uso |
| --- | --- |
| `XDG_DATA_HOME` | Cambia `~/.local/share` en la instalación global. |
| `XDG_CONFIG_HOME` | Cambia `~/.config` en la instalación global. |
| `XDG_BIN_HOME` | Cambia `~/.local/bin` en la instalación global. |

El CLI no lee claves de API. Las integraciones que las necesiten las toman del
entorno del proyecto, nunca de este repositorio.
