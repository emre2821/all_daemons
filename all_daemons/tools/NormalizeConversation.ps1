param(
  [Parameter(Mandatory=$true)]
  [string]$InputPath,

  [Parameter(Mandatory=$false)]
  [string]$OutputPath,

  [switch]$OnlyWhenPrefixed,

  [switch]$StripPrefix
)

<#
.SYNOPSIS
  Normalize role names in a role+text JSON transcript by detecting speaker prefixes like "[Alfred]:" or "Alfred:" at the start of a line.

.DESCRIPTION
  - Reads an array of objects: [{ role: string, text: string }]
  - If a message text begins with a speaker prefix (e.g., "[Agent]:" or "Agent:"), assigns role to that speaker and (optionally) removes the prefix from text.
  - Works for any role (assistant, user, tool, system). If -OnlyWhenPrefixed is set, only reassigns roles when a prefix is detected.

.PARAMETER InputPath
  Path to the JSON file containing the array of { role, text } objects.

.PARAMETER OutputPath
  Optional output path. If omitted, overwrites the input file.

.PARAMETER OnlyWhenPrefixed
  If set, only changes roles when a prefix is detected. Otherwise, no-op for messages without prefix.

.PARAMETER StripPrefix
  If set, removes the detected prefix (e.g., "[Alfred]: ") from the text after assigning the role.

.EXAMPLE
  pwsh tools/NormalizeConversation.ps1 -InputPath path\to\conv.json -StripPrefix

.EXAMPLE
  pwsh tools/NormalizeConversation.ps1 -InputPath conv.json -OutputPath conv_norm.json -OnlyWhenPrefixed -StripPrefix
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Test-Path -LiteralPath $InputPath)) {
  throw "Input file not found: $InputPath"
}

$outPath = if ($OutputPath) { $OutputPath } else { $InputPath }

# Load JSON
$data = Get-Content -LiteralPath $InputPath -Raw | ConvertFrom-Json
if ($null -eq $data) { throw "Failed to parse JSON from: $InputPath" }

# Ensure array
if ($data -isnot [System.Collections.IEnumerable]) {
  $data = @($data)
}

# Regex patterns for prefixes at start of text:
#  - [Name]: ... or [Name] - ...
#  - Name: ...
$patterns = @(
  '^[\s]*\[(?<name>[^\]\r\n]{1,64})\][\s]*[:\-][\s]*',
  '^[\s]*(?<name>[A-Za-z0-9 _&\-]{1,64})[\s]*:[\s]+'
)

foreach ($item in $data) {
  $txt = [string]$item.text
  if ([string]::IsNullOrWhiteSpace($txt)) { continue }

  $matched = $false
  foreach ($pat in $patterns) {
    $m = [System.Text.RegularExpressions.Regex]::Match($txt, $pat)
    if ($m.Success) {
      $name = ($m.Groups['name'].Value).Trim()
      if (-not [string]::IsNullOrWhiteSpace($name)) {
        $item.role = $name
        if ($StripPrefix) {
          $item.text = [System.Text.RegularExpressions.Regex]::Replace($txt, $pat, '')
        }
        $matched = $true
        break
      }
    }
  }

  if ($OnlyWhenPrefixed -and -not $matched) {
    # No change when requested to act only on prefixed lines
    continue
  }
}

$data | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $outPath -Encoding UTF8
Write-Output "Normalized conversation written to: $outPath"

