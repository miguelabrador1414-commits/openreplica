#!/usr/bin/env sh
set -eu

say() {
  printf '%s\n' "$*"
}

usage() {
  cat <<'EOF'
Uso:
  scripts/install.sh --global
  scripts/install.sh --project [DIR]
  scripts/install.sh --both [DIR]

--global  instala el CLI en ~/.local/share/openreplica, el wrapper en
          ~/.local/bin/replica y las skills, comandos y agente en
          ~/.config/opencode.
--project instala skills, comandos, agente y un CLI local en DIR/.opencode.
--both    hace las dos cosas.

El CLI global es el recomendado. La instalacion por proyecto evita depender
de la configuracion global de opencode.
EOF
}

MODE=""
PROJECT="."

while [ $# -gt 0 ]; do
  case "$1" in
    --global) MODE="global"; shift ;;
    --project) MODE="project"; shift ;;
    --both) MODE="both"; shift ;;
    -h|--help) usage; exit 0 ;;
    *)
      if [ -z "$MODE" ]; then
        say "Opcion desconocida: $1" >&2
        usage >&2
        exit 2
      fi
      PROJECT=$1
      shift
      ;;
  esac
done

if [ -z "$MODE" ]; then
  usage >&2
  exit 2
fi

SOURCE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if [ ! -d "$SOURCE/.opencode/skills" ]; then
  say "No encuentro .opencode/skills en $SOURCE" >&2
  exit 1
fi

install_skills() {
  dest=$1
  mkdir -p "$dest/skills" "$dest/commands" "$dest/agents"
  cp -R "$SOURCE/.opencode/skills/." "$dest/skills/"
  cp -R "$SOURCE/.opencode/commands/." "$dest/commands/"
  cp -R "$SOURCE/.opencode/agents/." "$dest/agents/"
  say "Skills, comandos y agente instalados en $dest"
}

install_global() {
  DATA_HOME=${XDG_DATA_HOME:-"$HOME/.local/share"}
  CONFIG_HOME=${XDG_CONFIG_HOME:-"$HOME/.config"}
  BIN_HOME=${XDG_BIN_HOME:-"$HOME/.local/bin"}
  SHARE="$DATA_HOME/openreplica"

  mkdir -p "$SHARE/tools" "$SHARE/bin" "$BIN_HOME" "$CONFIG_HOME/opencode"
  cp -R "$SOURCE/tools/." "$SHARE/tools/"
  cp -R "$SOURCE/bin/." "$SHARE/bin/"
  cp "$SOURCE/LICENSE" "$SOURCE/NOTICE" "$SHARE/"
  chmod +x "$SHARE/bin/replica"

  ln -sf "$SHARE/bin/replica" "$BIN_HOME/replica"
  install_skills "$CONFIG_HOME/opencode"

  say "CLI instalado en $SHARE"
  say "Wrapper: $BIN_HOME/replica"
  case ":$PATH:" in
    *":$BIN_HOME:"*) ;;
    *) say "Aviso: $BIN_HOME no esta en PATH. Anade: export PATH=\"$BIN_HOME:\$PATH\"" ;;
  esac
  say "Comprueba con: replica doctor"
}

install_project() {
  target=$(CDPATH= cd -- "$PROJECT" 2>/dev/null && pwd || true)
  if [ -z "$target" ]; then
    say "No existe el directorio del proyecto: $PROJECT" >&2
    exit 1
  fi
  install_skills "$target/.opencode"
  mkdir -p "$target/.opencode/tools" "$target/.opencode/bin"
  cp -R "$SOURCE/tools/." "$target/.opencode/tools/"
  cp -R "$SOURCE/bin/." "$target/.opencode/bin/"
  chmod +x "$target/.opencode/bin/replica"
  if [ ! -f "$target/.opencode/opencode.json" ]; then
    cp "$SOURCE/.opencode/opencode.json" "$target/.opencode/opencode.json"
    say "Config de proyecto instalada: $target/.opencode/opencode.json"
  else
    say "Aviso: ya existe .opencode/opencode.json; no lo sobrescribo."
    say "Anade default_agent=replica y el modelo si quieres usarlo por defecto."
  fi
  say "CLI local instalado en $target/.opencode/bin/replica"
  say "Si 'replica' no esta en PATH, usa: $target/.opencode/bin/replica"
}

case "$MODE" in
  global) install_global ;;
  project) install_project ;;
  both) install_global; install_project ;;
esac
