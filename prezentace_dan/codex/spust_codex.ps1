# Codex jako kontrolor: prompt ze souboru, výstup do <Vystup>, sandbox read-only (fact-check) nebo workspace-write jen v <Dir>.
param(
  [string]$Prompt,
  [string]$Vystup,
  [string]$Dir = "C:\Users\danie\Documents\hackathon-2026-prezentace",
  [string]$Sandbox = "read-only",
  [int]$LimitMin = 30,
  [string]$Effort = "high"
)
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:PATH = "C:\Users\danie\.venvs\hackathon\Scripts;C:\Users\danie\.local\bin;C:\Users\danie\AppData\Roaming\npm;$env:PATH"
Set-Location $Dir
$log = "$Vystup.log"
$sw = [Diagnostics.Stopwatch]::StartNew()
$cmd = "type `"$Prompt`" | codex exec --skip-git-repo-check -C . -s $Sandbox -m gpt-6.1-sol -c model_reasoning_effort=$Effort -o `"$Vystup`" - > `"$log`" 2>&1"
$p = Start-Process cmd -ArgumentList "/c", $cmd -PassThru -WindowStyle Hidden
if (-not $p.WaitForExit($LimitMin * 60 * 1000)) {
  taskkill /PID $p.Id /T /F | Out-Null
  "TIMEOUT po $LimitMin min" | Add-Content $log
}
"EXIT $($p.ExitCode) za $([int]$sw.Elapsed.TotalSeconds) s" | Add-Content $log
