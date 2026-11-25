# Registra interactivamente la clave publica del servidor GLEAM en known_hosts.
# No guarda ni imprime usuario o contrasena. El usuario escribe la contrasena en
# el cliente OpenSSH, donde no se muestra en pantalla.
$ErrorActionPreference = 'Stop'
$gleamUser = Read-Host 'Usuario SFTP de GLEAM'
if ([string]::IsNullOrWhiteSpace($gleamUser)) {
    throw 'El usuario no puede estar vacio.'
}

Write-Host 'Verifique que el host mostrado sea aether.ugent.be y acepte su clave solo si confia en la fuente oficial de GLEAM.'
Write-Host 'En el indicador sftp>, escriba exit despues de confirmar la conexion.'
& sftp -o StrictHostKeyChecking=ask -o UserKnownHostsFile="$env:USERPROFILE\.ssh\known_hosts" -P 2225 "$gleamUser@aether.ugent.be"
