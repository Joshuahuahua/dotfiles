fnm env --use-on-cd | Out-String | Invoke-Expression

$scripts = "S:\Users\Josh\Documents\Scripts"

function GoToGitRoot
{
  cd (git rev-parse --show-toplevel 2>$null) || "~"
}

Set-Alias -Name ... GoToGitRoot

Clear-Host

Invoke-Expression (&starship init powershell)
