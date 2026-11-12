# Instalación

OpenReplica tiene dos formas de instalarse: global, para todos tus proyectos, o
por proyecto, dentro de una sola app. Las dos usan los mismos archivos; cambia
solo el destino.

## Requisitos

- opencode instalado y funcionando.
- Python 3.8 o superior.
- Git, solo para clonar el repositorio.
- Opcional: Playwright y Chromium si quieres captura real en navegador.

El CLI no necesita `pip install`. Todo el núcleo usa la librería estándar.

## Instalación global

La instalación global deja el comando `replica` disponible en tu usuario y las
skills, comandos y agente en la configuración global de opencode.

```bash
git clone https://github.com/miguelabrador1414-commits/openreplica.git
cd openreplica
./scripts/install.sh --global
```

El script escribe en estas rutas:

| Qué | Dónde |
| --- | --- |
| CLI y datos | `~/.local/share/openreplica` |
| Lanzador `replica` | `~/.local/bin/replica` |
| Skills | `~/.config/opencode/skills` |
| Comandos | `~/.config/opencode/commands` |
| Agente | `~/.config/opencode/agents` |

Si `~/.local/bin` no está en tu `PATH`, el script te avisa. Añádelo a tu
`~/.bashrc` o `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Después comprueba:

```bash
replica doctor
```

`replica doctor` (revisa el entorno) dice si encuentra Python, git, node,
Playwright, el estado del proyecto y el propio comando en el `PATH`. Si algo
falla, muestra qué falta y no inventa un resultado.

Reinicia opencode después de instalar. opencode carga skills, comandos y
agentes al arrancar; si estaba abierto, no ve los archivos nuevos.

## Instalación por proyecto

La instalación por proyecto copia `.opencode` dentro de la app, incluido un CLI
local. No toca tu configuración global y sirve para probar una versión concreta
del pack sin depender de una instalación global.

```bash
cd /ruta/a/openreplica
./scripts/install.sh --project /ruta/a/tu-app
```

El resultado queda en:

```text
/ruta/a/tu-app/.opencode/
  opencode.json
  skills/
  commands/
  agents/
  tools/
  bin/replica
```

Si ya existía `.opencode/opencode.json`, el instalador no lo sobrescribe. En ese
caso añade a mano `"default_agent": "replica"` y el `"model"` que quieras usar.

El CLI local no se añade al `PATH`. Úsalo con su ruta:

```bash
cd /ruta/a/tu-app
.opencode/bin/replica doctor
.opencode/bin/replica init
```

Si prefieres escribir `replica` a secas, añade la carpeta del CLI local a tu
`PATH`:

```bash
export PATH="/ruta/a/tu-app/.opencode/bin:$PATH"
```

El agente resuelve el CLI solo: usa `replica` si está en el `PATH` y, si no,
`.opencode/bin/replica` desde la raíz del proyecto.

Si quieres las dos cosas a la vez:

```bash
./scripts/install.sh --both /ruta/a/tu-app
```

## Instalación manual

Si prefieres copiar archivos a mano:

```bash
git clone https://github.com/miguelabrador1414-commits/openreplica.git
cp -R openreplica/.opencode/skills/* ~/.config/opencode/skills/
cp -R openreplica/.opencode/commands/* ~/.config/opencode/commands/
cp -R openreplica/.opencode/agents/* ~/.config/opencode/agents/
ln -sf "$PWD/openreplica/bin/replica" ~/.local/bin/replica
```

El lanzador resuelve enlaces simbólicos, así que el `ln -sf` funciona aunque el
repositorio se mueva de sitio. Si prefieres no usar enlaces, copia `bin/` y
`tools/` juntos y ejecuta `python3 -m replkit` desde `tools/`.

## Comprobar la instalación

Dentro de un proyecto:

```bash
replica init
replica status
replica doctor
```

En opencode:

```text
/replica-recon
```

Si el comando aparece y el agente `replica` está disponible, la instalación
está completa. Si opencode no lo ve, revisa que los archivos estén en
`~/.config/opencode` o en `<proyecto>/.opencode` y reinicia.

## Desinstalar

Instalación global:

```bash
rm -f ~/.local/bin/replica
rm -rf ~/.local/share/openreplica
rm -rf ~/.config/opencode/skills/replica-*
rm -f ~/.config/opencode/commands/replica-*.md
rm -f ~/.config/opencode/agents/replica.md
```

Instalación por proyecto:

```bash
rm -rf /ruta/a/tu-app/.opencode/skills/replica-*
rm -f /ruta/a/tu-app/.opencode/commands/replica-*.md
rm -f /ruta/a/tu-app/.opencode/agents/replica.md
rm -rf /ruta/a/tu-app/.opencode/tools
rm -rf /ruta/a/tu-app/.opencode/bin
```

Los artefactos de tu app están en `replica/` dentro del proyecto. Bórralos solo
si quieres perder el estado y la evidencia de las fases.

## Problemas comunes

**`replica: command not found`.** `~/.local/bin` no está en el `PATH`. Añádelo
y abre una terminal nueva.

**opencode no muestra `/replica-*`.** El archivo no está en la ruta de opencode
o la sesión sigue abierta con la configuración anterior. Reinicia opencode.

**`replica doctor` no encuentra Playwright.** Es opcional. La captura por
defecto es offline con fixtures o manual. Si quieres captura real, instala
Playwright y Chromium por tu cuenta y usa `--allow-network`.

**El script falla con `No encuentro .opencode/skills`.** Estás ejecutándolo
desde un directorio que no es el checkout de OpenReplica. Usa la ruta completa
al script o entra al repositorio.
