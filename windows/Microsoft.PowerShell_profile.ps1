# Check once a day if a new powershell update exists
function GetPowerShellUpdate {
  $cacheFile = "~/.pwshCache"
  $currDate = Get-Date

  try {
    if (Test-Path $cacheFile) {
      $lastChecked = Get-Content $cacheFile -ErrorAction Stop
      $lastCheckedDate = [datetime]::ParseExact($lastChecked, "MM-dd-yyyy", $null)

      if ($currDate -gt $lastCheckedDate.AddMonths(1)) {
        winget upgrade --id Microsoft.Powershell # Update powershell (if required)
        $currDate.ToString("MM-dd-yyyy") | Set-Content $cacheFile
      }
    } else {
      winget upgrade --id Microsoft.Powershell # Update powershell (if required)
      $currDate.ToString("MM-dd-yyyy") | Set-Content $cacheFile
    }
  } catch {
      Write-Error "An error occurred while checking for updates."
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


# Update Powershell
GetPowerShellUpdate
Clear-Host

# Aliases/Variables
Set-Alias -Name ... GoToGitRoot
Set-Alias -Name lg lazygit
Set-Alias -Name ls runEza

$user = Join-Path -Path $PSScriptRoot -ChildPath "user.ps1"

# User Settings
if (Test-Path $user -PathType Leaf) {
    try { . $user } 
    catch { Write-Error "Failed to execute script 'user.ps1'. $_" }
} 


# Run Starship
Invoke-Expression (&starship init powershell)
Invoke-Expression (& { (zoxide init powershell | Out-String) })
