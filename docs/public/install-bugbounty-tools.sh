#!/usr/bin/env bash
set -Eeuo pipefail

# SKILL-ISSUE - Installation conditionnelle des outils Bug Bounty
# Cible : Exegol et Kali Linux (APT).

ORIGINAL_PATH="$PATH"
export GOTOOLCHAIN=auto
info() { printf '[*] %s\n' "$*"; }
ok() { printf '[OK] %s\n' "$*"; }
warn() { printf '[!] %s\n' "$*"; }
error() { printf '[ERREUR] %s\n' "$*" >&2; }

if [[ "$(uname -s)" != Linux ]] || ! command -v apt-get >/dev/null 2>&1; then
  error 'Ce script est prévu pour Exegol ou Kali Linux avec APT.'
  exit 1
fi

# httpx doit être le binaire ProjectDiscovery, pas le client Python.
has() {
  local name="$1"
  command -v "$name" >/dev/null 2>&1 || return 1
  if [[ "$name" == httpx ]]; then
    local help
    help="$(httpx -h 2>&1 || true)"
    [[ "$help" == *'-sc'* && "$help" == *'-title'* ]]
    return
  fi
  return 0
}

# Ajouter uniquement les paquets nécessaires.
APT_PACKAGES=()
add_pkg() {
  local pkg="$1" item
  for item in "${APT_PACKAGES[@]:-}"; do [[ "$item" == "$pkg" ]] && return 0; done
  APT_PACKAGES+=("$pkg")
}

# Outils système utilisés par le parcours.
has nmap || add_pkg nmap
has amass || add_pkg amass
has curl || add_pkg curl
has jq || add_pkg jq
has grep || add_pkg grep
has sort || add_pkg coreutils
has mktemp || add_pkg coreutils
has cp || add_pkg coreutils
has sha256sum || add_pkg coreutils
has dig || add_pkg dnsutils

# Outils Go : installer Go uniquement si au moins un binaire manque.
GO_INSTALLS=(
  'subfinder github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest'
  'assetfinder github.com/tomnomnom/assetfinder@latest'
  'chaos github.com/projectdiscovery/chaos-client/cmd/chaos@latest'
  'dnsx github.com/projectdiscovery/dnsx/cmd/dnsx@latest'
  'httpx github.com/projectdiscovery/httpx/cmd/httpx@latest'
  'httprobe github.com/tomnomnom/httprobe@latest'
  'katana github.com/projectdiscovery/katana/cmd/katana@latest'
  'gau github.com/lc/gau/v2/cmd/gau@latest'
  'waybackurls github.com/tomnomnom/waybackurls@latest'
  'urlfinder github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest'
  'gospider github.com/jaeles-project/gospider@latest'
  'nuclei github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest'
  'ffuf github.com/ffuf/ffuf/v2@latest'
  'anew github.com/tomnomnom/anew@latest'
  'unfurl github.com/tomnomnom/unfurl@latest'
  'gf github.com/tomnomnom/gf@latest'
)
NEED_GO=0
for entry in "${GO_INSTALLS[@]}"; do
  name="${entry%% *}"
  if ! has "$name"; then NEED_GO=1; fi
done
if (( NEED_GO )) && ! command -v go >/dev/null 2>&1; then add_pkg golang-go; fi

# Dépendances des outils non-Go.
if ! has findomain; then
  has curl || add_pkg curl
  command -v unzip >/dev/null 2>&1 || add_pkg unzip
  command -v find >/dev/null 2>&1 || add_pkg findutils
fi
ARJUN_NEEDS_INSTALL=0
if ! has arjun; then
  ARJUN_NEEDS_INSTALL=1
  command -v python3 >/dev/null 2>&1 || add_pkg python3
  command -v pipx >/dev/null 2>&1 || add_pkg pipx
fi
if ! has urldedupe; then
  command -v find >/dev/null 2>&1 || add_pkg findutils
  command -v git >/dev/null 2>&1 || add_pkg git
  command -v cmake >/dev/null 2>&1 || add_pkg cmake
  command -v make >/dev/null 2>&1 || add_pkg build-essential
  command -v c++ >/dev/null 2>&1 || add_pkg build-essential
fi

if ((${#APT_PACKAGES[@]})); then
  if [[ "$EUID" -eq 0 ]]; then
    APT=(apt-get)
  elif command -v sudo >/dev/null 2>&1; then
    APT=(sudo apt-get)
  else
    error 'Des paquets système manquent : relancer en root ou installer sudo.'
    exit 1
  fi
  info "Dépendances système manquantes : ${APT_PACKAGES[*]}"
  "${APT[@]}" update
  "${APT[@]}" install -y --no-install-recommends "${APT_PACKAGES[@]}"
else
  ok 'Aucune dépendance APT supplémentaire.'
fi

if (( NEED_GO )) && ! command -v go >/dev/null 2>&1; then
  error 'Go reste introuvable après son installation.'
  exit 1
fi

# Répertoire des binaires. En root, /usr/local/bin est déjà dans le PATH standard.
if command -v go >/dev/null 2>&1; then
  GOBIN_CURRENT="$(go env GOBIN 2>/dev/null || true)"
  if [[ -n "$GOBIN_CURRENT" ]]; then
    BIN_DIR="$GOBIN_CURRENT"
  elif [[ "$EUID" -eq 0 ]]; then
    BIN_DIR='/usr/local/bin'
  else
    GOPATH_CURRENT="$(go env GOPATH)"
    BIN_DIR="${GOPATH_CURRENT%%:*}/bin"
  fi
elif [[ "$EUID" -eq 0 ]]; then
  BIN_DIR='/usr/local/bin'
else
  BIN_DIR="$HOME/.local/bin"
fi
mkdir -p "$BIN_DIR"
export GOBIN="$BIN_DIR"
export PATH="$BIN_DIR:$HOME/.local/bin:$PATH"

# Installer seulement les outils Go absents.
for entry in "${GO_INSTALLS[@]}"; do
  name="${entry%% *}"
  module="${entry#* }"
  if has "$name"; then
    ok "$name : déjà présent, conservé."
  else
    info "Installation de $name..."
    go install -v "$module"
    hash -r
    has "$name" || { error "$name reste introuvable après installation."; exit 1; }
    ok "$name : installé et vérifié."
  fi
done

# Findomain : binaire officiel précompilé, selon l'architecture.
if has findomain; then
  ok 'findomain : déjà présent, conservé.'
else
  case "$(uname -m)" in
    x86_64|amd64) ASSET='findomain-linux.zip' ;;
    aarch64|arm64) ASSET='findomain-aarch64.zip' ;;
    *) error 'Architecture non prise en charge automatiquement pour Findomain.'; exit 1 ;;
  esac
  TMP_FINDOMAIN="$(mktemp -d)"
  curl -fsSL "https://github.com/Findomain/Findomain/releases/latest/download/$ASSET" -o "$TMP_FINDOMAIN/findomain.zip"
  unzip -q "$TMP_FINDOMAIN/findomain.zip" -d "$TMP_FINDOMAIN"
  BIN_FINDOMAIN="$(find "$TMP_FINDOMAIN" -type f -name findomain -print -quit)"
  [[ -n "$BIN_FINDOMAIN" ]] || { error 'Binaire Findomain absent de l’archive.'; exit 1; }
  cp "$BIN_FINDOMAIN" "$BIN_DIR/findomain"
  chmod 0755 "$BIN_DIR/findomain"
  rm -rf "$TMP_FINDOMAIN"
  hash -r
  has findomain || { error 'Findomain installé mais introuvable.'; exit 1; }
  ok 'findomain : installé et vérifié.'
fi

# Arjun : environnement Python isolé avec pipx.
if has arjun; then
  ok 'arjun : déjà présent, conservé.'
else
  export PATH="$HOME/.local/bin:$PATH"
  pipx install --force arjun
  hash -r
  has arjun || { error 'Arjun installé par pipx mais absent du PATH.'; exit 1; }
  ok 'arjun : installé et vérifié.'
fi

# urldedupe : compilation depuis les sources officielles (CMake, C++17).
if has urldedupe; then
  ok 'urldedupe : déjà présent, conservé.'
else
  TMP_URLDEDUPE="$(mktemp -d)"
  git clone --depth 1 https://github.com/ameenmaali/urldedupe.git "$TMP_URLDEDUPE/source"
  cmake -S "$TMP_URLDEDUPE/source" -B "$TMP_URLDEDUPE/source/build"
  cmake --build "$TMP_URLDEDUPE/source/build" --parallel
  BIN_URLDEDUPE="$(find "$TMP_URLDEDUPE/source" -type f -name urldedupe -perm -u+x -print -quit)"
  [[ -n "$BIN_URLDEDUPE" ]] || { error 'Binaire urldedupe absent après compilation.'; exit 1; }
  cp "$BIN_URLDEDUPE" "$BIN_DIR/urldedupe"
  chmod 0755 "$BIN_DIR/urldedupe"
  rm -rf "$TMP_URLDEDUPE"
  hash -r
  has urldedupe || { error 'urldedupe compilé mais introuvable.'; exit 1; }
  ok 'urldedupe : compilé, installé et vérifié.'
fi

# Ajouter les chemins utilisateur au fichier de configuration du shell si nécessaire.
PATH_CONFIG_NEEDED=0
case ":$ORIGINAL_PATH:" in *":$BIN_DIR:"*) ;; *) PATH_CONFIG_NEEDED=1 ;; esac
if (( ARJUN_NEEDS_INSTALL )); then
  case ":$ORIGINAL_PATH:" in *":$HOME/.local/bin:"*) ;; *) PATH_CONFIG_NEEDED=1 ;; esac
fi
if (( PATH_CONFIG_NEEDED )); then
  case "${SHELL:-}" in
    */zsh) RC_FILE="$HOME/.zshrc" ;;
    */bash) RC_FILE="$HOME/.bashrc" ;;
    *) RC_FILE="$HOME/.profile" ;;
  esac
  printf -v PATH_LINE 'export PATH="%s:%s:$PATH"' "$BIN_DIR" "$HOME/.local/bin"
  grep -Fqx -- "$PATH_LINE" "$RC_FILE" 2>/dev/null || {
    printf '\n# SKILL-ISSUE - outils Bug Bounty\n%s\n' "$PATH_LINE" >> "$RC_FILE"
  }
  info "PATH enregistré dans $RC_FILE pour les prochaines sessions."
fi

# Contrôle final identique à la liste de préparation du parcours.
TOOLS=(subfinder amass assetfinder findomain chaos dnsx httpx httprobe katana gau waybackurls urlfinder gospider arjun nmap nuclei ffuf curl jq sort grep anew unfurl urldedupe gf dig mktemp cp sha256sum)
MISSING=()
printf '\nBilan final\n'
for tool in "${TOOLS[@]}"; do
  if has "$tool"; then printf '[OK] %s\n' "$tool"; else printf '[MANQUANT] %s\n' "$tool"; MISSING+=("$tool"); fi
done

if ((${#MISSING[@]})); then
  error "Installation incomplète. Outils manquants : ${MISSING[*]}"
  exit 1
fi
ok 'Tous les outils de la liste sont disponibles.'
warn 'Les clés API restent à configurer séparément pour chaos et certaines sources de subfinder.'
if (( PATH_CONFIG_NEEDED )); then
  warn "Ouvrir un nouveau shell ou recharger la configuration : source $RC_FILE."
fi
