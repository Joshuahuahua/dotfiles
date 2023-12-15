# Set Node Version
fnm env --use-on-cd | Out-String | Invoke-Expression 

# '...' cd's to either a repo root, or ~
function GoToGitRoot
{
  cd (git rev-parse --show-toplevel 2>$null) || "~"
}

function runEza
{
  eza --icons=always -a --group-directories-first 
}


# Aliases
Set-Alias -Name ... GoToGitRoot
Set-Alias -Name lg lazygit
Set-Alias -Name ls runEza

# Run Starship
Clear-Host
Invoke-Expression (&starship init powershell)
