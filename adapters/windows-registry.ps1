param(
  [Parameter(Mandatory=$true)][string]$Manifest,
  [Parameter(Mandatory=$true)][string]$Output
)
$ErrorActionPreference = "Stop"
$data = Get-Content -LiteralPath $Manifest -Raw | ConvertFrom-Json
$aliases = @($data.models | Where-Object { $_.visible -eq $true } | ForEach-Object { $_.alias })
$json = $aliases | ConvertTo-Json -Compress
$escaped = $json.Replace('\', '\\').Replace('"', '\"')
$content = "Windows Registry Editor Version 5.00`r`n`r`n[HKEY_CURRENT_USER\Software\Policies\Claude]`r`n\"inferenceModels\"=\"$escaped\"`r`n"
Set-Content -LiteralPath $Output -Value $content -Encoding Unicode
Write-Output "Generated $Output with $($aliases.Count) visible aliases. Review before importing."
