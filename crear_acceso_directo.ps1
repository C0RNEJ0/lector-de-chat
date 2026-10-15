$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktop = [Environment]::GetFolderPath('Desktop')
$ws = New-Object -ComObject WScript.Shell
$lnk = $ws.CreateShortcut((Join-Path $desktop 'Starvios Bot OBS.lnk'))
$lnk.TargetPath = Join-Path $dir 'Iniciar_Bot_Starvios.bat'
$lnk.WorkingDirectory = $dir
$lnk.Description = 'Starvios Voice Assistant — Creado por CORNEJOXx'
$lnk.IconLocation = 'shell32.dll,168'
$lnk.Save()
Write-Output ("Creado en: " + $desktop)
