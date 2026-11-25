"""Arma el ZIP de entrega con el nombre y la estructura que exige el enunciado.

Uso (desde la raiz del repositorio):
    python codigo/crear_zip_entrega.py --grupo 07 --apellidos Idrobo Irpanoca Manturano

Requiere haber compilado antes el informe y la presentacion
(anexos/informe_fuente/informe.pdf y presentacion.pdf). Valida el nombre con la
expresion regular del enunciado, revisa nombres ASCII, rutas absolutas y
credenciales, y descomprime el resultado en una carpeta temporal para
comprobar la estructura.
"""
from pathlib import Path
import argparse
import re
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REGEX = re.compile(r"^T2_202602_G[0-9]{2}(_[A-Z][A-Za-z]+){3}\.zip$")
EXCLUIR_DIR = {"__pycache__", ".git", ".ipynb_checkpoints"}
EXCLUIR_EXT = {".aux", ".log", ".out", ".toc", ".synctex.gz", ".pyc"}
PROHIBIDOS = {".cdsapirc", ".netrc", ".env"}

ap = argparse.ArgumentParser()
ap.add_argument("--grupo", required=True, help="numero de grupo con dos digitos, p. ej. 07")
ap.add_argument("--apellidos", nargs=3, required=True, help="primer apellido de cada integrante")
ap.add_argument("--salida", default=str(ROOT.parent), help="carpeta donde se escribe el ZIP")
a = ap.parse_args()

apellidos = sorted(a.apellidos)
nombre = f"T2_202602_G{int(a.grupo):02d}_" + "_".join(apellidos)
zip_name = nombre + ".zip"
if not REGEX.match(zip_name):
    raise SystemExit(f"El nombre {zip_name} no cumple la expresion regular del enunciado.")
gnn = f"G{int(a.grupo):02d}"

informe = ROOT / "anexos" / "informe_fuente" / "informe.pdf"
presentacion = ROOT / "anexos" / "informe_fuente" / "presentacion.pdf"
for f in (informe, presentacion):
    if not f.exists():
        raise SystemExit(f"Falta {f.relative_to(ROOT)}: compile primero el LaTeX.")

problemas = []
archivos = []
for carpeta in ("codigo", "datos", "productos", "anexos"):
    for p in (ROOT / carpeta).rglob("*"):
        if p.is_dir() or any(part in EXCLUIR_DIR for part in p.parts):
            continue
        if any(p.name.endswith(e) for e in EXCLUIR_EXT) or p.name in PROHIBIDOS:
            if p.name in PROHIBIDOS:
                problemas.append(f"credencial excluida: {p.relative_to(ROOT)}")
            continue
        rel = p.relative_to(ROOT).as_posix()
        if not re.fullmatch(r"[A-Za-z0-9_./\-]+", rel):
            problemas.append(f"nombre no ASCII o con espacios: {rel}")
        if p.suffix in {".py", ".ps1", ".tex"}:
            txt = p.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"[A-Za-z]:[\\/](Users|Documents)|/home/\w+", txt):
                problemas.append(f"ruta absoluta en {rel}")
        archivos.append(p)

salida = Path(a.salida)
zip_path = salida / zip_name
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(ROOT / "README.md", f"{nombre}/README.md")
    z.write(informe, f"{nombre}/T2_202602_{gnn}_informe.pdf")
    z.write(presentacion, f"{nombre}/T2_202602_{gnn}_presentacion.pdf")
    for p in archivos:
        z.write(p, f"{nombre}/{p.relative_to(ROOT).as_posix()}")

# Comprobacion: descomprimir y revisar la estructura
with tempfile.TemporaryDirectory() as tmp:
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(tmp)
    raiz = list(Path(tmp).iterdir())
    assert len(raiz) == 1 and raiz[0].name == nombre, "debe haber una sola carpeta con el nombre del ZIP"
    esperado = {"README.md", f"T2_202602_{gnn}_informe.pdf", f"T2_202602_{gnn}_presentacion.pdf",
                "codigo", "datos", "productos", "anexos"}
    presente = {p.name for p in raiz[0].iterdir()}
    assert presente == esperado, f"estructura distinta: {sorted(presente ^ esperado)}"
    for sub in ("codigo", "datos", "productos"):
        for pn in ("punto1", "punto2"):
            assert (raiz[0] / sub / pn).is_dir(), f"falta {sub}/{pn}"

print(f"ZIP: {zip_path} ({zip_path.stat().st_size / 1e6:.1f} MB, {len(archivos) + 3} archivos)")
print("Problemas:" if problemas else "Sin problemas de nombres, rutas ni credenciales.")
for x in problemas:
    print("  -", x)
