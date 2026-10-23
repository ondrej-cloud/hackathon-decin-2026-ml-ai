# Codex jako experimentátor: zápis jen do pracovní složky (-s workspace-write, -C <Dir>), bez internetu.
param(
  [string]$Prompt,
  [string]$Vystup,
  [string]$Dir,
  [int]$LimitMin = 40,
  [string]$Effort = "high"
)
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:OPENBLAS_NUM_THREADS = "4"
$env:PATH = "C:\Users\danie\.venvs\hackathon\Scripts;C:\Users\danie\.local\bin;$env:PATH"
Set-Location $Dir
$log = "$Vystup.log"
$sw = [Diagnostics.Stopwatch]::StartNew()
$cmd = "type `"$Prompt`" | codex exec --skip-git-repo-check -C . -s workspace-write -m gpt-6.1-sol -c model_reasoning_effort=$Effort -o `"$Vystup`" - > `"$log`" 2>&1"
$p = Start-Process cmd -ArgumentList "/c", $cmd -PassThru -WindowStyle Hidden
if (-not $p.WaitForExit($LimitMin * 60 * 1000)) {
  taskkill /PID $p.Id /T /F | Out-Null
  "TIMEOUT po $LimitMin min" | Add-Content $log
}
"EXIT $($p.ExitCode) za $([int]$sw.Elapsed.TotalSeconds) s" | Add-Content $log
