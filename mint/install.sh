#!/usr/bin/env bash
set -Eeuo pipefail

REPO_URL="https://github.com/Joshuahuahua/dotfiles/"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

log() {
  printf '\n==> %s\n' "$*"
}

warn() {
  printf 'WARNING: %s\n' "$*" >&2
}

require_repo() {
  if ! git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf 'Error: %s is not inside a git repository.\n' "$REPO_ROOT" >&2
    exit 1
  fi

  local remote
  remote="$(git -C "$REPO_ROOT" config --get remote.origin.url || true)"
  if [[ -n "$remote" && "$remote" != "$REPO_URL" && "$remote" != "git@github.com:Joshuahuahua/dotfiles.git" ]]; then
    warn "Repository remote does not match expected dotfiles repo: $remote"
  fi
}

backup_path() {
  local dest="$1"
  if [[ -L "$dest" || -e "$dest" ]]; then
    local backup="${dest}.backup-${TIMESTAMP}"
    mv "$dest" "$backup"
    log "Backed up $dest -> $backup"
  fi
}

symlink_path() {
  local src="$1"
  local dest="$2"

  mkdir -p "$(dirname "$dest")"

  if [[ -L "$dest" ]] && [[ "$(readlink -f "$dest")" == "$(readlink -f "$src")" ]]; then
    log "Symlink already correct: $dest"
    return
  fi

  if [[ -L "$dest" || -e "$dest" ]]; then
    backup_path "$dest"
  fi

  ln -s "$src" "$dest"
  log "Linked $dest -> $src"
}

apt_install() {
  sudo apt install -y "$@"
}

apt_install_if_available() {
  local available=()
  local pkg
  for pkg in "$@"; do
    if apt-cache show "$pkg" >/dev/null 2>&1; then
      available+=("$pkg")
    else
      warn "APT package not available: $pkg"
    fi
  done

  if ((${#available[@]})); then
    sudo apt install -y "${available[@]}"
  fi
}

install_oh_my_zsh() {
  if [[ -d "$HOME/.oh-my-zsh" ]]; then
    log "oh-my-zsh already installed"
    return
  fi

  log "Installing oh-my-zsh"
  RUNZSH=no CHSH=no KEEP_ZSHRC=yes sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
}

install_starship() {
  if command -v starship >/dev/null 2>&1; then
    log "starship already installed"
    return
  fi

  log "Installing starship"
  curl -fsSL https://starship.rs/install.sh | sh -s -- -y
}

install_zoxide() {
  if command -v zoxide >/dev/null 2>&1; then
    log "zoxide already installed"
    return
  fi

  log "Installing zoxide"
  curl -fsSL https://raw.githubusercontent.com/ajeetdsouza/zoxide/main/install.sh | bash
}

install_fnm_and_node() {
  if ! command -v fnm >/dev/null 2>&1; then
    log "Installing fnm"
    curl -fsSL https://fnm.vercel.app/install | bash -s -- --install-dir "$HOME/.local/share/fnm" --skip-shell
  else
    log "fnm already installed"
  fi

  export PATH="$HOME/.local/share/fnm:$PATH"
  eval "$(fnm env --shell bash)"

  log "Installing latest LTS Node.js via fnm"
  fnm install --lts
  fnm use lts-latest
  fnm default lts-latest

  log "Enabling Corepack and activating pnpm"
  corepack enable
  corepack prepare pnpm@latest --activate
}

install_lazygit() {
  if command -v lazygit >/dev/null 2>&1; then
    log "lazygit already installed"
    return
  fi

  log "Installing lazygit"
  local arch version tmpdir asset
  case "$(uname -m)" in
    x86_64) arch="x86_64" ;;
    aarch64|arm64) arch="arm64" ;;
    *)
      warn "Unsupported architecture for lazygit auto-install: $(uname -m)"
      return
      ;;
  esac

  version="$(curl -fsSL https://api.github.com/repos/jesseduffield/lazygit/releases/latest | grep -Po '"tag_name": "v\K[^"]+')"
  tmpdir="$(mktemp -d)"
  asset="lazygit_${version}_Linux_${arch}.tar.gz"

  curl -fsSL "https://github.com/jesseduffield/lazygit/releases/latest/download/${asset}" -o "$tmpdir/lazygit.tar.gz"
  tar -xzf "$tmpdir/lazygit.tar.gz" -C "$tmpdir" lazygit
  sudo install "$tmpdir/lazygit" /usr/local/bin/lazygit
  rm -rf "$tmpdir"
}

install_eza() {
  if command -v eza >/dev/null 2>&1; then
    log "eza already installed"
    return
  fi

  if apt-cache show eza >/dev/null 2>&1; then
    log "Installing eza from apt"
    sudo apt install -y eza
    return
  fi

  log "Installing eza apt repo"
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://raw.githubusercontent.com/eza-community/eza/main/deb.asc \
    | sudo gpg --dearmor -o /etc/apt/keyrings/gierens.gpg
  echo "deb [signed-by=/etc/apt/keyrings/gierens.gpg] http://deb.gierens.de stable main" \
    | sudo tee /etc/apt/sources.list.d/gierens.list >/dev/null
  sudo chmod 644 /etc/apt/keyrings/gierens.gpg /etc/apt/sources.list.d/gierens.list
  sudo apt update
  sudo apt install -y eza
}

ensure_fd_alias() {
  mkdir -p "$HOME/.local/bin"
  if command -v fd >/dev/null 2>&1; then
    return
  fi
  if command -v fdfind >/dev/null 2>&1; then
    ln -sfn "$(command -v fdfind)" "$HOME/.local/bin/fd"
    log "Linked fd -> fdfind in ~/.local/bin"
  fi
}

install_paq() {
  local paq_dir="${XDG_DATA_HOME:-$HOME/.local/share}/nvim/site/pack/paqs/start/paq-nvim"
  if [[ -d "$paq_dir" ]]; then
    log "paq-nvim already installed"
    return
  fi

  log "Installing paq-nvim"
  git clone https://github.com/savq/paq-nvim.git "$paq_dir"
}

main() {
  require_repo

  log "Updating apt package lists"
  sudo apt update

  log "Installing base packages"
  apt_install \
    curl \
    git \
    zsh \
    tmux \
    neovim \
    ripgrep \
    fd-find \
    fzf \
    chafa \
    unzip \
    tar \
    build-essential \
    ca-certificates \
    gpg \
    pipx \
    python3-pip \
    python3-venv

  log "Installing optional apt packages when available"
  apt_install_if_available alacritty zoxide

  install_oh_my_zsh
  install_starship
  install_zoxide
  install_fnm_and_node
  install_lazygit
  install_eza
  ensure_fd_alias

  log "Installing Python CLI helpers"
  pipx install black || true
  pipx install isort || true

  log "Symlinking dotfiles"
  symlink_path "$REPO_ROOT/.zshrc" "$HOME/.zshrc"
  symlink_path "$REPO_ROOT/.tmux.conf" "$HOME/.tmux.conf"
  symlink_path "$REPO_ROOT/nvim" "$HOME/.config/nvim"
  symlink_path "$REPO_ROOT/alacritty" "$HOME/.config/alacritty"
  symlink_path "$REPO_ROOT/lazygit.yml" "$HOME/.config/lazygit/config.yml"

  install_paq

  log "Setup complete"
  printf '\nNotes:\n'
  printf '  - Your Alacritty config is symlinked from the repo, but it currently contains a Windows/WSL shell setting.\n'
  printf '  - If you want zsh as your default shell, run: chsh -s "$(command -v zsh)"\n'
  printf '  - You may want to open Neovim and run :PaqInstall or :PaqSync after first bootstrapping.\n'
}

main "$@"
