$repo_url = ""

# install scoop
irm get.scoop.sh | iex

# install dependencies
scoop bucket add extras
scoop install wezterm neovim gcc fnm fd ripgrep starship lazygit

# Clone repo
git clone $repo_url ./dotfiles
New-Item -Path $PROFILE -ItemType SymbolicLink -Value (Resolve-Path .\dotfiles\Microsoft.PowerShell_profile.ps1) -Force

fnm install --lts

. $profile
# RESTART SHELL INSTANCE

New-Item -Path $HOME\AppData\Local\nvim -ItemType SymbolicLink -Value (Resolve-Path .\dotfiles\nvim) -Force

# symlink .wezterm.lua ($HOME)
# symlink nvim (%userprofile%\AppData\Local\nvim)`



# run neovim once headless-ly to install deps
