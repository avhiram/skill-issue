#!/usr/bin/env bash
# Installe uniquement les outils manquants parmi ceux identifies dans le controle Bug Bounty.
set -uo pipefail

TOOLS=(urlfinder gospider unfurl urldedupe)
FAILED=()
INSTALLED=()
SKIPPED=()
BIN_DIR=""

log() { printf '\n[%s] %s\n' "$1" "$2"; }

if ! command -v go >/dev/null 2>&1; then
  printf 'Erreur : Go est requis pour installer urlfinder, gospider et unfurl.\n' >&2
  printf 'Installe Go depuis https://go.dev/dl/ puis relance ce script.\n' >&2
  exit 1
fi

BIN_DIR="$(go env GOBIN 2>/dev/null || true)"
if [[ -z "$BIN_DIR" ]]; then
  BIN_DIR="$(go env GOPATH)/bin"
fi
mkdir -p "$BIN_DIR"

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) export PATH="$BIN_DIR:$PATH"
     printf 'Note : %s a ete ajoute au PATH de cette execution.\n' "$BIN_DIR"
     printf 'Pour le conserver dans les prochains terminaux, ajoute cette ligne a ton profil shell :\n'
     printf 'export PATH="%s:$PATH"\n' "$BIN_DIR"
     ;;
esac

install_go_tool() {
  local name="$1"
  local module="$2"

  if command -v "$name" >/dev/null 2>&1; then
    log "DEJA PRESENT" "$name"
    SKIPPED+=("$name")
    return 0
  fi

  log "INSTALLATION" "$name"
  if ! GOBIN="$BIN_DIR" GOTOOLCHAIN=auto go install "$module"; then
    log "ECHEC" "$name"
    FAILED+=("$name")
    return 1
  fi

  if [[ -x "$BIN_DIR/$name" ]] || command -v "$name" >/dev/null 2>&1; then
    log "INSTALLE" "$name"
    INSTALLED+=("$name")
    return 0
  fi

  log "NON DETECTE APRES INSTALLATION" "$name"
  FAILED+=("$name")
  return 1
}

install_urldedupe() {
  local dep
  local missing=()
  local tmp

  if command -v urldedupe >/dev/null 2>&1; then
    log "DEJA PRESENT" "urldedupe"
    SKIPPED+=("urldedupe")
    return 0
  fi

  for dep in git cmake g++; do
    command -v "$dep" >/dev/null 2>&1 || missing+=("$dep")
  done

  if (("${#missing[@]}" > 0)); then
    if ! command -v apt-get >/dev/null 2>&1; then
      log "ECHEC" "urldedupe : dependances manquantes (${missing[*]}). Installer git, cmake et g++ avec le gestionnaire de paquets de la distribution."
      FAILED+=("urldedupe")
      return 1
    fi

    log "DEPENDANCES" "${missing[*]}"
    if [[ "$EUID" -eq 0 ]]; then
      apt-get update && apt-get install -y --no-install-recommends "${missing[@]}" || {
        FAILED+=("urldedupe")
        return 1
      }
    elif command -v sudo >/dev/null 2>&1; then
      sudo apt-get update && sudo apt-get install -y --no-install-recommends "${missing[@]}" || {
        FAILED+=("urldedupe")
        return 1
      }
    else
      log "ECHEC" "urldedupe : droits administrateur requis pour installer ${missing[*]}"
      FAILED+=("urldedupe")
      return 1
    fi
  fi

  tmp="$(mktemp -d)"
  log "COMPILATION" "urldedupe depuis les sources officielles"
  if ! git clone --depth 1 https://github.com/ameenmaali/urldedupe.git "$tmp/urldedupe" ||
     ! cmake -S "$tmp/urldedupe" -B "$tmp/urldedupe/build" -DCMAKE_BUILD_TYPE=Release ||
     ! cmake --build "$tmp/urldedupe/build" --parallel ||
     [[ ! -x "$tmp/urldedupe/build/urldedupe" ]]; then
    rm -rf "$tmp"
    log "ECHEC" "urldedupe"
    FAILED+=("urldedupe")
    return 1
  fi

  if ! install -m 0755 "$tmp/urldedupe/build/urldedupe" "$BIN_DIR/urldedupe"; then
    rm -rf "$tmp"
    log "ECHEC" "installation de urldedupe dans $BIN_DIR"
    FAILED+=("urldedupe")
    return 1
  fi
  rm -rf "$tmp"

  if [[ -x "$BIN_DIR/urldedupe" ]]; then
    log "INSTALLE" "urldedupe"
    INSTALLED+=("urldedupe")
    return 0
  fi

  log "ECHEC" "urldedupe non detecte apres compilation"
  FAILED+=("urldedupe")
  return 1
}

install_go_tool urlfinder github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest || true
install_go_tool gospider github.com/jaeles-project/gospider@latest || true
install_go_tool unfurl github.com/tomnomnom/unfurl@latest || true
install_urldedupe || true

printf '\n===== BILAN =====\n'
printf 'Deja presents : %s\n' "${#SKIPPED[@]}"
printf 'Installes      : %s\n' "${#INSTALLED[@]}"
printf 'Echecs         : %s\n' "${#FAILED[@]}"

if (("${#FAILED[@]}" > 0)); then
  printf 'A verifier : %s\n' "${FAILED[*]}"
  exit 1
fi

printf 'Tous les outils cibles sont disponibles.\n'
printf 'Relance ensuite le controle de disponibilite dans la cheatsheet.\n'
