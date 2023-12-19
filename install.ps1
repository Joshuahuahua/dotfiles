$ErrorActionPreference = "Stop"

# Install/Update Scoop
try
{
  scoop update
} catch
{
  Invoke-RestMethod -Uri get.scoop.sh | Invoke-Expression
  scoop update
}

# install dependencies
scoop bucket add extras
scoop install wezterm neovim gcc fnm fd ripgrep starship lazygit eza

# Clone repo
git clone "https://github.com/Joshuahuahua/dotfiles/" dotfiles
New-Item -Path $PROFILE -ItemType SymbolicLink -Value (Resolve-Path .\dotfiles\Microsoft.PowerShell_profile.ps1) -Force

fnm install --lts

. $profile
# RESTART SHELL INSTANCE

New-Item -Path $HOME\AppData\Local\nvim -ItemType SymbolicLink -Value (Resolve-Path .\dotfiles\nvim) -Force

Exit

# symlink .wezterm.lua ($HOME)
# symlink nvim (%userprofile%\AppData\Local\nvim)`



# run neovim once headless-ly to install deps
