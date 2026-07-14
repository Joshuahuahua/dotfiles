# dotfiles

This repo uses a **shared base config + OS-specific entrypoint wrapper** layout.

## Layout

Shared/base config lives at the repo root:

- `.zshrc`
- `.tmux.conf`
- `alacritty/alacritty.toml`
- `nvim/`
- `lazygit.yml`

OS-specific entrypoints live in per-OS folders:

- `mint/`
- `windows/`

## Mint structure

Mint uses wrapper files in `mint/` that point back to the shared root config.

- `mint/.zshrc`
  - dynamically resolves its own path
  - sources the shared root `.zshrc`
- `mint/.tmux.conf`
  - resolves the real path of `~/.tmux.conf`
  - derives the repo root from that
  - sources the shared root `.tmux.conf`
- `mint/alacritty.toml`
  - imports `../alacritty/alacritty.toml`
  - adds Mint-specific shell settings

Neovim is currently shared directly via the root `nvim/` directory rather than using a Mint-specific wrapper.

## Why this layout?

This keeps:

- shared behavior in one place
- OS-specific differences small and isolated
- duplication low

For single-file configs, the OS-specific file acts as the entrypoint and loads the shared base config.

## Intended symlinks on Mint

The Mint setup is intended to symlink:

- `~/.zshrc` -> `mint/.zshrc`
- `~/.tmux.conf` -> `mint/.tmux.conf`
- `~/.config/alacritty/alacritty.toml` -> `mint/alacritty.toml`
- `~/.config/nvim` -> `nvim/`
- `~/.config/lazygit/config.yml` -> `lazygit.yml`

## Mint bootstrap

Use:

```bash
./mint/install.sh
```

The script is intended to:

- install base packages like `zsh`, `tmux`, `neovim`, `ripgrep`, `fd`, `fzf`, etc.
- install tools like `starship`, `zoxide`, `fnm`, Node LTS, `pnpm`, `lazygit`, and `eza`
- create the symlinks listed above
- install `paq-nvim`

## Windows

Windows setup lives in:

- `windows/install.ps1`
- `windows/Microsoft.PowerShell_profile.ps1`

That side of the repo uses the same general idea: shared config where possible, with platform-specific entrypoints where needed.
