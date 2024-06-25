$ErrorActionPreference = "Stop"
$repoUrl = "https://github.com/Joshuahuahua/dotfiles/" 

# Install/Update Scoop
try
{
  scoop update
} catch
{
  Invoke-RestMethod -Uri get.scoop.sh | Invoke-Expression
  scoop update
}

# Install Dependencies
scoop bucket add extras
scoop install wezterm neovim gcc fnm fd ripgrep starship lazygit eza python zoxide

try {
  pip install isort black
} catch {
  Write-Warning Pip install failed
}

# Clone Repo
if ($PSScriptRoot -eq "")
{
  git clone "https://github.com/Joshuahuahua/dotfiles/" dotfiles
  Set-Location dotfiles
} else
{
  Set-Location $PSScriptRoot
  try
  {
    if ((Split-Path -Path (Get-Location) -Leaf) -ne "dotfiles")
    {
      Throw
    }
    git rev-parse --is-inside-work-tree
    if ((git config --get remote.origin.url) -ne $repoUrl)
    {
		    Throw
    }
  } catch
  {
    Write-Error "Script not being run from correct repository."
    Exit
  }
}

# Install Paq
if (-not (Test-Path -Path "$env:LOCALAPPDATA\nvim-data\site\pack\paqs\start\paq-nvim")) {
  git clone "https://github.com/savq/paq-nvim.git" "$($env:LOCALAPPDATA)\nvim-data\site\pack\paqs\start\paq-nvim"
}



# Symlink PowerShell Config
New-Item -Path $PROFILE -ItemType SymbolicLink -Value (Resolve-Path .\windows\Microsoft.PowerShell_profile.ps1) -Force

fnm install --lts

# RESTART SHELL INSTANCE
# . $profile

# Symlink Neovim Config
New-Item -Path $HOME\AppData\Local\nvim -ItemType SymbolicLink -Value (Resolve-Path .\nvim) -Force

# Symlink Wezterm Config
New-Item -Path $HOME\.wezterm.lua -ItemType SymbolicLink -Value (Resolve-Path .\.wezterm.lua) -Force

# Install nvim packages
nvim --headless +PaqSync +q
Write-Host # New Line

Write-Host "`n`n`nInstallation Complete." -Foreground Green
Read-Host "Press ENTER to exit..."
Exit
