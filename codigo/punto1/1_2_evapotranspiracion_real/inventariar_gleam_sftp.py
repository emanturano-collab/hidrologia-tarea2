"""Inventaria metadatos GLEAM por SFTP sin descargar datos ni guardar secretos."""

from __future__ import annotations

import getpass
import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path

import paramiko


HOST = "aether.ugent.be"
PORT = 2225
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
OUTPUT = ROOT / "datos" / "punto1" / "gleam4_3a_sftp_inventory.json"
MAX_DEPTH = 4
MAX_ENTRIES = 5000


def attr_record(path: str, item: paramiko.SFTPAttributes) -> dict:
    return {
        "path": path,
        "type": "directory" if stat.S_ISDIR(item.st_mode) else "file",
        "size_bytes": item.st_size if not stat.S_ISDIR(item.st_mode) else None,
        "modified_utc": datetime.fromtimestamp(item.st_mtime, timezone.utc).isoformat(),
    }


def main() -> None:
    known_hosts = Path.home() / ".ssh" / "known_hosts"
    if not known_hosts.exists():
        raise FileNotFoundError(
            "No existe known_hosts. Ejecute primero registrar_host_gleam_sftp.ps1 y acepte la clave del host de forma interactiva."
        )

    username = input("Usuario SFTP de GLEAM: ").strip()
    if not username:
        raise ValueError("El usuario no puede estar vacio.")
    password = os.environ["GLEAM_SFTP_PASSWORD"]
    client = paramiko.SSHClient()
    client.load_host_keys(str(known_hosts))
    client.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        client.connect(HOST, port=PORT, username=username, password=password, look_for_keys=False, allow_agent=False)
        sftp = client.open_sftp()
        queue: list[tuple[str, int]] = [(".", 0)]
        inventory: list[dict] = []
        root_listing: list[dict] = []
        while queue and len(inventory) < MAX_ENTRIES:
            directory, depth = queue.pop(0)
            for item in sftp.listdir_attr(directory):
                path = f"{directory.rstrip('/')}/{item.filename}" if directory != "." else item.filename
                record = attr_record(path, item)
                inventory.append(record)
                if directory == ".":
                    root_listing.append(record)
                if record["type"] == "directory" and depth < MAX_DEPTH:
                    queue.append((path, depth + 1))
                if len(inventory) >= MAX_ENTRIES:
                    break

        terms = ("gleam", "4.3a", "readme", "monthly")
        relevant = [record for record in inventory if any(term in record["path"].lower() for term in terms)]
        result = {
            "server": {"protocol": "SFTP", "host": HOST, "port": PORT},
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "credentials_stored": False,
            "files_downloaded": False,
            "known_host_verified": True,
            "max_depth": MAX_DEPTH,
            "entries_scanned": len(inventory),
            "scan_truncated": len(inventory) >= MAX_ENTRIES,
            "root_listing": root_listing,
            "relevant_entries": relevant,
        }
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(f"Conexion e inventario completados. Metadatos guardados en: {OUTPUT}")
    finally:
        password = None
        client.close()


if __name__ == "__main__":
    main()
