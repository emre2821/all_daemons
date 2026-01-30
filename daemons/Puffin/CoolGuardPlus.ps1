# CoolGuardPlus.ps1 — Puffin+ thermal guardian for Windows
# Requires: LibreHardwareMonitor running with Remote Web Server enabled (http://localhost:8085/data.json)
# Optional: PowerShell module BurntToast for richer toasts (Install-Module BurntToast -Scope CurrentUser)

<#
  What’s new vs. your CoolGuard:
    - Hysteresis (avoids throttle flapping): separate COOL thresholds
    - Remembers & restores the original power plan after cooldown
    - Optional GPU temp watch (enable if you want)
    - AC/DC CPU caps (set both) + option to only throttle on AC
    - Robust JSON scrape across varied LHM sensor names
    - Logging to file + minimal backoff when endpoint is down
    - Configurable action on sustained “Hot”: Sleep (default), Hibernate, or ShutDown
    - Safer toast: uses BurntToast if present, falls back to NotifyIcon
#>

# ---------------- SETTINGS ----------------
$PollSeconds = 10 # how often to check
$CPUWarmC = 85 # start throttling at/above
$CPUHotC = 92 # consider “hot” at/above
$CPUCooleDownC = 78 # clear throttle when CPU below this
$SSDWarmC = 70
$SSDHotC = 80
$SSDCoolDownC = 60

$WatchGPU = $false # set $true to include GPU in warm/hot logic
$GPUWarmC = 82
$GPUHotC = 90
$GPUCoolDownC = 75

$HotSustainMinutes = 3 # must remain “hot” this long to trigger action
$ActionOnHot = "Sleep" # Sleep | Hibernate | ShutDown

$ThrottleOnACOnly = $true # if true, don’t cap CPU when on battery
$MaxCPUWhenWarmAC = 80 # cap CPU (AC) when warm
$MaxCPUWhenWarmDC = 60 # cap CPU (Battery) when warm (only used if $ThrottleOnACOnly -eq $false)

$PowerPlanCoolName = "Power saver" # switch to this when throttling
$LogPath = "$env:ProgramData\Puffin\CoolGuardPlus.log"
$ToastTitle = "Puffin CoolGuard+"
$Endpoint = "http://localhost:8085/data.json"
# ------------------------------------------

# Prep filesystem
$null = New-Item -ItemType Directory -Force -Path ([System.IO.Path]::GetDirectoryName($LogPath)) 2>$null
function Log([string]$msg) {
  $stamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
  "$stamp $msg" | Out-File -FilePath $LogPath -Append -Encoding utf8
}

# Toast: BurntToast if available, else NotifyIcon
$UseBurntToast = $false
try {
  if (Get-Module -ListAvailable -Name BurntToast) { $UseBurntToast = $true }
} catch {}
Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue | Out-Null
Add-Type -AssemblyName System.Drawing -ErrorAction SilentlyContinue | Out-Null
function Send-Toast([string]$msg, [string]$title = $ToastTitle) {
  try {
    if ($UseBurntToast) {
      New-BurntToastNotification -Text $title, $msg -ErrorAction SilentlyContinue | Out-Null
    } else {
      $balloon = New-Object System.Windows.Forms.NotifyIcon
      $balloon.Icon = [System.Drawing.SystemIcons]::Information
      $balloon.Visible = $true
      $balloon.BalloonTipTitle = $title
      $balloon.BalloonTipText = $msg
      $balloon.ShowBalloonTip(3000)
      Start-Sleep -Milliseconds 500
      $balloon.Dispose()
    }
  } catch { }
  Log "[TOAST] $msg"
}

# Power plan helpers
function Get-ActivePlanGuid() {
  $out = powercfg /getactivescheme | Out-String
  if ($out -match "([A-F0-9-]{36})") { return $matches[1] }
  return $null
}
function Get-PlanGuidByName($name){
  $out = powercfg /list | Out-String
  if ($out -match "([A-F0-9-]{36})\s+\($([regex]::Escape($name))\)") { return $matches[1] }
  return $null
}
function Set-MaxCPU-ACDC($guid, [int]$pctAC, [int]$pctDC) {
  if (-not $guid) { return }
  $SUB_PROCESSOR = "54533251-82be-4824-96c1-47b60b740d00"
  $PROCTHROTTLEMAX = "bc5038f7-23e0-4960-96da-33abaf5935ec"
  if ($pctAC -gt 0) { powercfg /setacvalueindex $guid $SUB_PROCESSOR $PROCTHROTTLEMAX $pctAC | Out-Null }
  if ($pctDC -gt 0) { powercfg /setdcvalueindex $guid $SUB_PROCESSOR $PROCTHROTTLEMAX $pctDC | Out-Null }
}
function Activate-Plan($guid) {
  if ($guid) { powercfg /setactive $guid | Out-Null }
}

# Poll LHM data with lightweight backoff
$Backoff = 0
function Get-LHMData() {
  try {
    $data = Invoke-RestMethod -Uri $Endpoint -TimeoutSec 2
    $Global:Backoff = 0
    return $data
  } catch {
    $Global:Backoff = [Math]::Min(60, [int]($Global:Backoff + 5))
    Log "WARN: LHM endpoint unavailable ($Endpoint). Backing off ${Global:Backoff}s."
    Start-Sleep -Seconds $Global:Backoff
    return $null
  }
}

# Sensor scraping
function Max-TempFrom($root, [string[]]$hwMatch, [string[]]$nameRegex) {
  $max = $null
  foreach ($hw in $root.Children) {
    if ($hwMatch | Where-Object { $hw.Text -match $_ }) {
      foreach ($branch in $hw.Children) {
        foreach ($s in $branch.Sensors) {
          if ($s.SensorType -eq "Temperature") {
            if ($nameRegex | Where-Object { $s.Name -match $_ }) {
              $v = [double]$s.Value
              if (-not $max -or $v -gt $max) { $max = $v }
            }
          }
        }
      }
    }
  }
  return $max
}

function Read-Temps($data) {
  $cpu = Max-TempFrom $data @("CPU","Ryzen","Core") @("Package|Tctl|Tdie|CPU")
  $ssd = Max-TempFrom $data @("Storage|NVMe|SSD") @("Temperature|Composite")
  $gpu = $null
  if ($WatchGPU) { $gpu = Max-TempFrom $data @("GPU|Graphics") @("Hot Spot|GPU|Core") }
  [pscustomobject]@{ CPU=$cpu; SSD=$ssd; GPU=$gpu }
}

# Decide state
function Eval-State($t) {
  $isWarm = $false; $isHot = $false; $cooled = $false
  if ($t.CPU -and $t.CPU -ge $CPUWarmC) { $isWarm = $true }
  if ($t.SSD -and $t.SSD -ge $SSDWarmC) { $isWarm = $true }
  if ($WatchGPU -and $t.GPU -ge $GPUWarmC) { $isWarm = $true }
  if ($t.CPU -and $t.CPU -ge $CPUHotC) { $isHot = $true }
  if ($t.SSD -and $t.SSD -ge $SSDHotC) { $isHot = $true }
  if ($WatchGPU -and $t.GPU -ge $GPUHotC) { $isHot = $true }
  # hysteresis: “cooled” when all temps under cooldown thresholds
  $coolCPU = (-not $t.CPU) -or ($t.CPU -le $CPUCooleDownC)
  $coolSSD = (-not $t.SSD) -or ($t.SSD -le $SSDCoolDownC)
  $coolGPU = (-not $WatchGPU) -or (-not $t.GPU) -or ($t.GPU -le $GPUCoolDownC)
  if ($coolCPU -and $coolSSD -and $coolGPU) { $cooled = $true }
  return [pscustomobject]@{ Warm=$isWarm; Hot=$isHot; Cooled=$cooled }
}

# AC or DC?
function On-AC() {
  try {
    $s = (Get-WmiObject -Class Win32_Battery -ErrorAction SilentlyContinue)
    if ($s) {
      # Battery present: test PowerStatus via .NET
      Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue | Out-Null
      return [System.Windows.Forms.SystemInformation]::PowerStatus.PowerLineStatus -eq 'Online'
    }
  } catch {}
  # Desktop with no battery => assume AC
  return $true
}

# Initial discovery
$OriginalPlan = Get-ActivePlanGuid
$CoolPlan = Get-PlanGuidByName $PowerPlanCoolName
Log "CoolGuard+ started. Original plan: $OriginalPlan | Cool plan: $CoolPlan | Endpoint: $Endpoint"
Send-Toast "CoolGuard+ active. Watching CPU/SSD$(if($WatchGPU){'/GPU'}) temps."

$HotSince   = $null
$Throttled  = $false
$LastState  = "Normal"

while ($true) {
  $data = Get-LHMData
  if (-not $data) { continue }

  $t = Read-Temps $data
  $state = Eval-State $t
  $onAC = On-AC

  # throttle on warm
  if ($state.Warm -and -not $Throttled) {
    if ($CoolPlan) {
      Activate-Plan $CoolPlan
      if ($ThrottleOnACOnly -and -not $onAC) {
        Log "Warm but on battery; not capping CPU (ThrottleOnACOnly=True)."
      } else {
        $capAC = $MaxCPUWhenWarmAC
        $capDC = ($ThrottleOnACOnly ? 0 : $MaxCPUWhenWarmDC)
        Set-MaxCPU-ACDC $CoolPlan $capAC $capDC
      }
      $Throttled = $true
      $LastState = "Warm"
      Send-Toast ("Temps high (CPU {0}°C, SSD {1}°C{2}). Capping CPU and switching plan." -f $t.CPU,$t.SSD, ($(if($WatchGPU){" , GPU $($t.GPU)°C"} else {""})))
      Log ("WARM: CPU={0}C SSD={1}C{2} | Throttled" -f $t.CPU,$t.SSD, ($(if($WatchGPU){" GPU="+$t.GPU+"C"} else {""})))
    } else {
      Log "No cool plan found; warm but cannot switch plan."
    }
  }

  # hot sustain logic
  if ($state.Hot) {
    if (-not $HotSince) { $HotSince = Get-Date }
    $hotFor = (Get-Date) - $HotSince
    if ($hotFor.TotalMinutes -ge $HotSustainMinutes) {
      $msg = ("Too hot for {0:N1} min (CPU {1}°C, SSD {2}°C{3}). Taking action: {4}" -f $hotFor.TotalMinutes,$t.CPU,$t.SSD, ($(if($WatchGPU){" , GPU "+$t.GPU+"°C"} else {""})), $ActionOnHot)
      Send-Toast $msg
      Log "ACTION: $msg"
      switch ($ActionOnHot) {
        "Hibernate" { shutdown.exe /h }
        "ShutDown"  { shutdown.exe /s /t 0 }
        default     { rundll32.exe powrprof.dll,SetSuspendState 0,1,0 }
      }
      # on resume: reset flags but keep original plan intact
      $HotSince  = $null
      $Throttled = $false
      Start-Sleep -Seconds $PollSeconds
      continue
    }
  } else {
    $HotSince = $null
  }

  # cool-down restore
  if ($Throttled -and $state.Cooled) {
    if ($OriginalPlan) { Activate-Plan $OriginalPlan }
    $Throttled = $false
    $LastState = "Normal"
    Send-Toast ("Temps normalized (CPU {0}°C, SSD {1}°C{2}). Restored your original plan." -f $t.CPU,$t.SSD, ($(if($WatchGPU){" , GPU "+$t.GPU+"°C"} else {""})))
    Log ("COOLED: CPU={0}C SSD={1}C{2} | Restored original plan" -f $t.CPU,$t.SSD, ($(if($WatchGPU){" GPU="+$t.GPU+"C"} else {""})))
  }

  Start-Sleep -Seconds $PollSeconds
}
