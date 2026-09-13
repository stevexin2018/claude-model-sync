[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$Manifest,
  [Parameter(Mandatory=$false)][string]$Output,
  [switch]$Apply,
  [switch]$PiercingMSIX,
  [string]$PackageFamilyName = "Claude_pzs8sxrjxfjjc",
  [switch]$RestartApp
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $Manifest)) {
  throw "Manifest file not found: $Manifest"
}

if (-not $Output) {
  $Output = [System.IO.Path]::ChangeExtension($Manifest, ".reg")
}

$data = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
$aliases = @($data.models | Where-Object { $_.visible -eq $true } | ForEach-Object { $_.alias })
$json = $aliases | ConvertTo-Json -Compress
$escaped = $json.Replace('\', '\\').Replace('"', '\"')
$content = "Windows Registry Editor Version 5.00`r`n`r`n[HKEY_CURRENT_USER\Software\Policies\Claude]`r`n\"inferenceModels\"=\"$escaped\"`r`n"
Set-Content -LiteralPath $Output -Value $content -Encoding Unicode
Write-Output "Generated $Output with $($aliases.Count) visible aliases."

if ($Apply -or $PiercingMSIX) {
  # 1. Apply to host registry
  reg import "$Output"
  Write-Output "Imported to host registry HKCU\Software\Policies\Claude."

  # 2. Check for MSIX container
  $msixInstalled = Get-AppxPackage -Name "*Claude*" -ErrorAction SilentlyContinue |
    Where-Object { $_.PackageFamilyName -eq $PackageFamilyName -or $_.Name -like "*Claude*" } |
    Select-Object -First 1

  if ($msixInstalled -or $PiercingMSIX) {
    $family = if ($msixInstalled) { $msixInstalled.PackageFamilyName } else { $PackageFamilyName }
    $appId = "Claude"
    Write-Output "Detected MSIX package $family. Piercing container virtual registry..."

    $cmd = Get-Command Invoke-CommandInDesktopPackage -ErrorAction SilentlyContinue
    if ($cmd) {
      Invoke-CommandInDesktopPackage -PackageFamilyName $family -AppId $appId -Command "reg.exe" -Args "import `"$Output`""
      Write-Output "Successfully pierced MSIX container and imported policy into virtual registry."
    } else {
      Write-Warning "Invoke-CommandInDesktopPackage not available on this system. Unable to pierce MSIX container automatically."
    }
  }
}

if ($RestartApp) {
  Write-Output "Terminating existing Claude Desktop processes..."
  Get-Process -Name claude -ErrorAction SilentlyContinue | Stop-Process -Force
  Start-Sleep -Seconds 1
  Write-Output "Relaunching Claude Desktop..."
  Start-Process "shell:AppsFolder\$PackageFamilyName!Claude"
}