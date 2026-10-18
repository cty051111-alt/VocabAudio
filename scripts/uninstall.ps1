# VocabAudio safe removal: only app-owned named files / folders are deleted.
# User PDFs / Word files / MP3 exports are never in the deletion allow-list.
$ErrorActionPreference = 'Stop'
$Root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$DataRoot = Join-Path $env:LOCALAPPDATA 'VocabAudio'
$AllowedFiles = @('VocabAudio.exe','app.py','vocab_core.py','settings_store.py','START_APP.bat','INSTALL_DEPENDENCIES.bat','Uninstall_VocabAudio.bat','requirements.txt','requirements-dev.txt','README.md','README_EN.md','LICENSE','CHANGELOG.md','CONTRIBUTING.md','SECURITY.md','RELEASE_NOTES_v1.1.0.md','RELEASE_NOTES_v2.0.0-beta.md')
$AllowedFolders = @('scripts','tests','docs','.github','__pycache__')
Write-Host 'VocabAudio Safe Uninstall' -ForegroundColor Cyan
Write-Host "Program folder: $Root"
Write-Host "Settings/cache folder: $DataRoot"
Write-Host 'Only known VocabAudio files and its private cache will be deleted.' -ForegroundColor Yellow
Write-Host 'Personal PDF/DOCX/MP3 files, Python, and other unknown files remain untouched.'
$reply = Read-Host 'Type UNINSTALL to continue'
if ($reply -cne 'UNINSTALL') { Write-Host 'Cancelled'; exit 0 }
if (-not (Test-Path (Join-Path $Root 'Uninstall_VocabAudio.bat'))) {throw 'Uninstall marker is missing'}
# Delete the program files after the uninstaller has exited; avoid deleting its own script mid-run.
$escapeRoot = $Root.Replace("'", "''")
$escapeData = $DataRoot.Replace("'", "''")
$filesText = ($AllowedFiles | ForEach-Object {"'" + $_.Replace("'", "''") + "'"}) -join ','
$foldersText = ($AllowedFolders | ForEach-Object {"'" + $_.Replace("'", "''") + "'"}) -join ','
$script = @"
Start-Sleep -Seconds 3
`$r = '$escapeRoot'
`$d = '$escapeData'
foreach (`$name in @($filesText)) {
  `$p = Join-Path `$r `$name
  if (Test-Path -LiteralPath `$p -PathType Leaf) { Remove-Item -LiteralPath `$p -Force -ErrorAction SilentlyContinue }
}
foreach (`$name in @($foldersText)) {
  `$p = Join-Path `$r `$name
  if (Test-Path -LiteralPath `$p -PathType Container) { Remove-Item -LiteralPath `$p -Recurse -Force -ErrorAction SilentlyContinue }
}
if (Test-Path -LiteralPath `$d -PathType Container) { Remove-Item -LiteralPath `$d -Recurse -Force -ErrorAction SilentlyContinue }
"@
$encoded=[Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script))
Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile','-EncodedCommand',$encoded) -WindowStyle Hidden
Write-Host 'Cleanup scheduled. You can now close this window.'
