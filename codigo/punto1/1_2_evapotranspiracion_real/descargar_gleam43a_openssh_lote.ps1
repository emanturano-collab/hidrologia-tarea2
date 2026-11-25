# Descarga segura del lote 2002--2023 con una sesion OpenSSH.
# La contrasena solo la solicita OpenSSH y no se escribe en este script.
param(
    [Parameter(Mandatory=$true)][string]$Usuario,
    [switch]$SoloProbarAutenticacion
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$python = Join-Path $root '.venv\Scripts\python.exe'
$planner = Join-Path $PSScriptRoot 'gleam43a_lote_openssh.py'
$raw = Join-Path $root 'datos\punto1\gleam4_3a_raw'
$testPlan = Join-Path $PSScriptRoot 'gleam_openssh_prueba.sftp'

function Invoke-GleamSftp([string]$ArchivoComandos) {
    & sftp `
        -b $ArchivoComandos `
        -o BatchMode=no `
        -o PubkeyAuthentication=no `
        -o PasswordAuthentication=yes `
        -o PreferredAuthentications=password `
        -o StrictHostKeyChecking=yes `
        -o UserKnownHostsFile="$env:USERPROFILE\.ssh\known_hosts" `
        -P 2225 `
        "$Usuario@aether.ugent.be" | Out-Host
    $exitCode = $LASTEXITCODE
    return $exitCode
}

if ($SoloProbarAutenticacion) {
    Write-Host 'Prueba SFTP sin descarga: se ejecutara unicamente pwd.'
    Write-Host 'OpenSSH solicitara la contrasena de forma oculta.'
    $code = Invoke-GleamSftp $testPlan
    if ($code -ne 0) { throw 'Fallo la autenticacion SFTP por lotes; no se descargo ningun archivo.' }
    Write-Host 'AUTENTICACION_SFTP_OK: prueba completada sin descarga.'
    exit 0
}

& $python $planner plan
if ($LASTEXITCODE -ne 0) { throw 'La planificacion detecto un archivo local inconsistente.' }
$plan = Join-Path $raw 'openssh_reget_2002_2023.sftp'
if ((Get-Item -LiteralPath $plan).Length -gt 0) {
    Write-Host 'OpenSSH solicitara la contrasena de forma oculta una sola vez.'
    Push-Location $raw
    try {
        $code = Invoke-GleamSftp $plan
        if ($code -ne 0) {
            throw 'OpenSSH no completo el lote. Los .part se conservan para reanudar con el mismo comando.'
        }
    } finally {
        Pop-Location
    }
} else { Write-Host 'No hay archivos pendientes de descarga.' }
& $python $planner validate
if ($LASTEXITCODE -ne 0) { throw 'La validacion fallo. Los .part no validados se conservaron; revise el error.' }
