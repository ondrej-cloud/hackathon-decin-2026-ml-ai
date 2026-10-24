# Codex jako kontrolor: jen čtení (-s read-only), prompt ze souboru, výstup do <Vystup>, časový limit.
param(
  [string]$Prompt,
  [string]$Vystup,
  [string]$Dir = "C:\Users\danie\Documents\hackathon-2026-nejistota",
  [int]$LimitMin = 25,
  [string]$Effort = "high"
)
$env:PYTHONIOENCODING = "utf-8"
$env:PATH = "C:\Users\danie\.venvs\hackathon\Scripts;C:\Users\danie\.local\bin;$env:PATH"
Set-Location $Dir
$log = "$Vystup.log"
$sw = [Diagnostics.Stopwatch]::StartNew()
$cmd = "type `"$Prompt`" | codex exec --skip-git-repo-check -C . -s read-only -m gpt-6.1-sol -c model_reasoning_effort=$Effort -o `"$Vystup`" - > `"$log`" 2>&1"
$p = Start-Process cmd -ArgumentList "/c", $cmd -PassThru -WindowStyle Hidden
if (-not $p.WaitForExit($LimitMin * 60 * 1000)) {
  taskkill /PID $p.Id /T /F | Out-Null
  "TIMEOUT po $LimitMin min" | Add-Content $log
}
"EXIT $($p.ExitCode) za $([int]$sw.Elapsed.TotalSeconds) s" | Add-Content $log
