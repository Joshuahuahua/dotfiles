# Check once a day if a new powershell update exists
function GetPowerShellUpdate
{
  $currDate = Get-Date -Format "MM-dd-yyyy"
  try
  { 
    $lastChecked = Get-Content "~/.pwshCache" -ErrorAction Stop
    if ($lastChecked -and [datetime]$currDate -gt [datetime]$lastChecked)
    {
      winget upgrade --id Microsoft.Powershell # Update powershell (if required)
    }
  } finally
  { 
    $currDate > "~/.pwshCache"
  }
}

# '...' cd's to either a repo root, or ~
function GoToGitRoot
{
  Set-Location (git rev-parse --show-toplevel 2>$null) || "~"
}

function runEza([string]$path = ".")
{
  eza $path --icons=always -a --group-directories-first 
}

#############################################################

# Set Node Version
fnm env --use-on-cd | Out-String | Invoke-Expression 

# Aliases
Set-Alias -Name ... GoToGitRoot
Set-Alias -Name lg lazygit
Set-Alias -Name ls runEza

# Run Starship
GetPowerShellUpdate
Clear-Host
Invoke-Expression (&starship init powershell)
