# Alternativa manual OpenSSH: conserva host-key checking y contrasena oculta.
# Se abre una sola sesion SFTP; no pega ni guarda secretos.
param(
    [Parameter(Mandatory=$true)][string]$Usuario,
    [int]$Anio = 2001
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$destino = Join-Path $root 'datos\punto1\gleam4_3a_raw'
New-Item -ItemType Directory -Force -Path $destino | Out-Null
$nombre = "E_${Anio}_GLEAM_v4.3a_MO.nc"
$remoto = "/data/v4.3a/monthly/E/$nombre"
$parcial = Join-Path $destino "$nombre.part"
Write-Host 'OpenSSH pedira la contrasena de forma oculta.'
Write-Host 'La clave del servidor debe estar ya verificada en known_hosts.'
Write-Host "En sftp>, ejecute exactamente: reget $remoto $parcial"
Write-Host 'Al terminar, escriba: exit'
& sftp -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$env:USERPROFILE\.ssh\known_hosts" -P 2225 "$Usuario@aether.ugent.be"
Write-Host "Archivo parcial esperado: $parcial"
Write-Host 'Luego ejecute el descargador Python: validara, renombrara y calculara SHA-256.'
