# OpenReplica

[![tests](https://github.com/miguelabrador1414-commits/openreplica/actions/workflows/tests.yml/badge.svg)](https://github.com/miguelabrador1414-commits/openreplica/actions/workflows/tests.yml)

Once skills nativas de opencode que reconstruyen la funcionalidad de una app
con copia limpia, y después le dan nombre, marca y lanzamiento propios. Gratis,
MIT, sin registro y sin claves de API para el pack.

[Read in English](README.md)

OpenReplica es un fork de [The Replica skill](https://github.com/Jakeschincariol/replica-skill)
de Jake Schincariol, reorganizado alrededor de un CLI único (`replica`), un
estado de proyecto explícito y puertas de calidad deterministas.

## Qué hace

Una skill reconstruye la app que quieres clonar. Otra la construye. Otra la
prueba y busca bugs. Otra lee lo que odian los usuarios de la original y lo
convierte en un plan de mejoras. En medio, el pack planifica el stack,
reconstruye el sistema de diseño, conecta auth y pagos, mide la paridad, pone
nombre y marca, escribe el lanzamiento y lo publica.

El flujo es:

```text
recon -> architect -> design -> build -> backend -> test -> diff
      -> entrepreneur -> brand -> launch -> deploy
```

Cada fase deja evidencia en `replica/`, dentro de tu proyecto. Cada fase tiene
una puerta. No se pasa a la siguiente hasta que la puerta pasa.

**Reconstruye lo que una app hace, nunca lo que posee.** Funciones y flujos con
copia limpia. No su código fuente, logo, textos, fuentes, contenido ni APIs
privadas.

## Requisitos

- [opencode](https://opencode.ai) con un modelo que sepa usar herramientas.
- Python 3.8 o superior para el CLI.
- Opcional: Playwright y Chromium para captura real en navegador. La captura
  por defecto es offline y no descarga nada.

El núcleo del CLI no tiene dependencias fuera de la librería estándar de Python.

## Instalación

### Global

```bash
git clone https://github.com/miguelabrador1414-commits/openreplica.git
cd openreplica
./scripts/install.sh --global
export PATH="$HOME/.local/bin:$PATH"
replica doctor
```

Esto instala:

- el CLI en `~/.local/share/openreplica`,
- el lanzador en `~/.local/bin/replica`,
- las skills en `~/.config/opencode/skills`,
- los comandos en `~/.config/opencode/commands`,
- el agente en `~/.config/opencode/agents`.

Reinicia opencode después de instalar para que cargue los archivos nuevos.

### Por proyecto

```bash
./scripts/install.sh --project /ruta/a/tu-app
```

Esto copia las skills, los comandos, el agente, la configuración de proyecto y
un CLI local al proyecto destino. No toca tu configuración global. Si el
proyecto ya tiene `.opencode/opencode.json`, el instalador no lo sobrescribe y
te pide que añadas los dos ajustes a mano. Usa el CLI local cuando `replica` no
esté en tu `PATH`:

```bash
/ruta/a/tu-app/.opencode/bin/replica doctor
```

### Manual

```bash
git clone https://github.com/miguelabrador1414-commits/openreplica.git
cp -R openreplica/.opencode/skills/* ~/.config/opencode/skills/
cp -R openreplica/.opencode/commands/* ~/.config/opencode/commands/
cp -R openreplica/.opencode/agents/* ~/.config/opencode/agents/
ln -sf "$PWD/openreplica/bin/replica" ~/.local/bin/replica
```

### Compatibilidad con Claude Code

El manifiesto `.claude-plugin` del upstream se conserva y apunta a
`.opencode/skills`. El objetivo probado es opencode; el soporte de Claude Code
es de mejor esfuerzo y no forma parte de la matriz de tests.

## Inicio rápido

```bash
cd mi-app
replica init
opencode
```

Después ejecuta las fases en orden:

```text
/replica-recon https://example.com
/replica-architect
/replica-design
/replica-build
/replica-backend
/replica-test
/replica-diff
/replica-entrepreneur
/replica-brand
/replica-launch
/replica-deploy
```

Puedes ejecutar una fase suelta. `/replica-entrepreneur` sobre una app que solo
estás considerando clonar es una buena forma de decidir si vale la pena.

## Las once fases

| # | Comando | Qué produce | Qué comprueba la puerta |
| --- | --- | --- | --- |
| 1 | `/replica-recon` | `replica/recon.md`, `replica/features.csv`, capturas | Mapa, matriz, prioridades, must-haves |
| 2 | `/replica-architect` | `replica/architecture.md` | Stack, esquema, rutas, orden de construcción |
| 3 | `/replica-design` | `replica/design/tokens.json`, especificación de componentes | Tokens y contraste WCAG AA |
| 4 | `/replica-build` | Pantallas, `replica/build-log.md`, matriz actualizada | Funciones implementadas y capturas del clon |
| 5 | `/replica-backend` | Migraciones, servidor, `replica/backend.md` | Notas, `.env.example`, sin secretos |
| 6 | `/replica-test` | `replica/test-plan.md`, `replica/bugs.md`, tests e2e | Plan presente, sin S1 ni S2 abiertos |
| 7 | `/replica-diff` | `replica/parity.json`, imágenes de diferencias | Paridad mínima de 70 |
| 8 | `/replica-entrepreneur` | `replica/reviews.csv`, `replica/feedback.md`, `replica/fixes.md` | Reseñas enlazadas y plan de mejoras |
| 9 | `/replica-brand` | `replica/brand.md`, `replica/brand.json` | Barrido de marca limpio |
| 10 | `/replica-launch` | `replica/launch/`, `replica/listing.json` | Lint de ficha sin errores |
| 11 | `/replica-deploy` | `replica/preflight.md`, puesta en producción | Preflight completo, paridad mínima 80, barrido limpio |

Las skills contienen el método detallado. Las puertas son el contrato.

## Estado y puertas

```bash
replica init                 # crea replica/state.json
replica status               # fase actual y siguiente paso
replica mark recon in_progress
# haz el trabajo
replica gate recon           # sale 0 si pasa, 2 si está bloqueado
replica mark recon passed    # solo después de que la puerta pase
```

`replica gate` comprueba los artefactos, no tu confianza. Si falla, lista el
archivo o el valor exacto que hay que corregir.

## El CLI

| Comando | Para qué |
| --- | --- |
| `replica init` | Crea `replica/` y el archivo de estado. |
| `replica status` | Muestra el estado de las fases y la siguiente. |
| `replica mark` | Actualiza estado, nota o artefactos de una fase. |
| `replica gate` | Comprueba una fase contra sus reglas de evidencia. |
| `replica doctor` | Revisa Python, git, node, Playwright, estado y PATH. |
| `replica capture` | Captura una URL o un fixture local. Offline por defecto. |
| `replica extract` | Lee rutas, controles, colores y fuentes de HTML. |
| `replica imgdiff` | Compara dos capturas por estructura o por píxeles. |
| `replica parity` | Puntúa la matriz de funciones y lista lo que falta. |
| `replica contrast` | Comprueba el contraste WCAG de los tokens. |
| `replica sweep` | Busca el nombre, dominio o colores de la original. |
| `replica reviews` | Ordena reseñas reales en quejas y peticiones. |
| `replica listing` | Revisa una ficha de App Store o Google Play. |

Ejemplos:

```bash
replica parity replica/features.csv --visual replica/diffs/*.json --markdown
replica imgdiff replica/screens/S07.png replica/clone-screens/S07.png --out diff-S07.png
replica contrast replica/design/tokens.json
replica sweep . --config replica/brand.json
replica listing replica/launch/listing.json
```

## Captura offline y captura real

`replica capture` usa por defecto un camino determinista:

- `--backend stub` con `--fixture` lee un HTML o una carpeta local. Sin red y
  sin descargas.
- `--backend manual` escribe una lista con los tamaños de pantalla exactos.
- `--backend playwright --allow-network` usa un navegador real. Solo funciona
  si tú instalaste Playwright y Chromium.

El pack nunca descarga Chromium por su cuenta.

## Modelos

El modelo por defecto del proyecto es `opencode/deepseek-v4.1-flash-free`.
Está en:

- `.opencode/opencode.json` como modelo del proyecto y agente por defecto,
- `.opencode/agents/replica.md` como modelo del agente.

Para usar otro modelo, cambia los dos archivos. Los identificadores siempre
llevan el proveedor delante. El CLI determinista y las puertas reducen la
dependencia del modelo, pero usa uno que sepa llamar herramientas con fiabilidad.

## Estructura del repositorio

```text
.opencode/
  skills/replica-*/SKILL.md    las 11 skills y sus referencias
  commands/replica-*.md        un comando de opencode por fase
  agents/replica.md            agente orquestador
  opencode.json                agente y modelo por defecto del proyecto
tools/replkit/                 CLI en Python sin dependencias
bin/replica                    lanzador para un checkout
tests/                         tests unitarios, fixtures y contrato del repo
docs/es/                       guías en español
scripts/install.sh             instalación global o por proyecto
```

Los artefactos de tu proyecto viven en `replica/`, dentro de tu app, no en este
repositorio.

## Desarrollo

```bash
make check     # compila, ejecuta 102 tests y lint si ruff está instalado
make test      # solo tests unitarios
./bin/replica --help
```

Reglas para contribuir:

- El Python del núcleo usa solo la librería estándar.
- La lógica determinista va en `tools/replkit/`, no en el texto de las skills.
- Cada comando del CLI necesita un test.
- El inglés es el idioma principal. Mantén `README.es.md` y `docs/es/` al día.
- Sin guiones largos (em dash) en el texto del repositorio. Los tests lo
  comprueban.
- No subas secretos, capturas privadas ni exportaciones personales de reseñas.

## Documentación

- [Instalación](docs/es/instalacion.md)
- [Flujo de trabajo](docs/es/flujo.md)
- [Referencia del CLI](docs/es/cli.md)
- [Modelos y agente](docs/es/modelos.md)
- [Seguridad y legal](docs/es/seguridad-legal.md)

## Seguridad y legal

**Copia limpia.** OpenReplica estudia qué hace una app y cómo se mueve el
usuario, y después escribe todo desde cero. Nunca copia el código fuente, los
assets propietarios, los logos, las marcas, los textos ni las APIs privadas del
objetivo.

**Solo fuentes permitidas.** Páginas públicas y tu propia cuenta. Nunca entra
en la cuenta de otra persona, salta un muro de pago ni hace scraping detrás de
un login. Si los términos de tu cuenta prohíben usarla para construir un
competidor, las skills lo dicen y se quedan en fuentes públicas.

**Marca nueva antes de lanzar.** Nombre, paleta, logo y textos nuevos. La
puerta de deploy bloquea hasta que el barrido esté limpio.

**"Clonar cualquier app" significa función y flujo.** No el contenido, la red
ni las licencias que posee una app. Puedes reconstruir el reproductor, las
listas y el compartir de una app de música. No puedes clonar su catálogo.

**No hay clon perfecto garantizado.** El resultado depende de la app. Una
herramienta de reservas son semanas. Un motor de hojas de cálculo no. Recon lo
dimensiona con honestidad y parity te da un número, no una sensación.

**Nada de evidencia inventada.** La fase Entrepreneur nunca fabrica reseñas,
citas, valoraciones ni fuentes. Cada cita es literal y enlazada, y el tamaño de
la muestra se declara.

**Comprueba antes de vender.** Ejecuta las comprobaciones de marca y dominio
que lista la fase de marca, lee los términos de todo lo que uses y habla con un
abogado antes de lanzar si hay dinero en juego. Esto no es asesoría legal.

## Créditos

Proyecto original: [The Replica skill](https://github.com/Jakeschincariol/replica-skill)
de Jake Schincariol, [opusjake.ai](https://opusjake.ai). El copyright original
y los términos MIT se conservan en `LICENSE` y `NOTICE`.

Las modificaciones de OpenReplica y la integración con opencode están
mantenidas por Miguel.

## Licencia

MIT. Tómala, cámbiala y publícala. Ver [LICENSE](LICENSE).
