from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "zip"
NAME = "T2_202602_G00_Idrobo_Irpanoca_Manturano"
STAGE = OUT / NAME

def copy_tree(src: Path, dst: Path, exclude_names=()):
    if not src.exists():
        return
    for p in src.rglob("*"):
        if p.is_dir() or any(part in exclude_names for part in p.parts):
            continue
        rel = p.relative_to(src)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)

if STAGE.exists():
    shutil.rmtree(STAGE)
STAGE.mkdir(parents=True)
OUT.mkdir(parents=True, exist_ok=True)

(STAGE / "README.md").write_text(
    "# Entrega Tarea 2 de Hidrología\n\n"
    "Paquete provisional reproducible del punto 2. El identificador `G00` es un "
    "marcador: reemplazarlo por el número oficial del grupo antes de entregar. "
    "El punto 1 queda reservado para integrar los archivos del grupo.\n\n"
    "## Contenido\n- `T2_202602_G00_informe.pdf`: informe del punto 2.\n"
    "- `T2_202602_G00_presentacion.pdf`: borrador de presentación oral.\n"
    "- `codigo/`, `datos/`, `productos/` y `anexos/`: fuentes y evidencias.\n",
    encoding="utf-8",
)
(STAGE / "punto1" / "README.md").parent.mkdir(parents=True, exist_ok=True)
(STAGE / "punto1" / "README.md").write_text(
    "# Punto 1\nReservado para integrar la solución final del punto 1.\n",
    encoding="utf-8",
)
(STAGE / "punto2" / "README.md").parent.mkdir(parents=True, exist_ok=True)
(STAGE / "punto2" / "README.md").write_text(
    "# Punto 2\nAnálisis de extremos, IDF, anomalías y diseño hidrológico.\n",
    encoding="utf-8",
)

pdf_src = ROOT / "output" / "pdf"
shutil.copy2(pdf_src / "informe_tarea2_humano.pdf", STAGE / "T2_202602_G00_informe.pdf")
shutil.copy2(pdf_src / "T2_202602_G00_presentacion.pdf", STAGE / "T2_202602_G00_presentacion.pdf")

# The clean package keeps raw source files out of the archive; processed and
# documented data remain available for reproducibility and reasonable size.
copy_tree(ROOT / "codigo", STAGE / "codigo", exclude_names=("__pycache__", "tmp"))
copy_tree(ROOT / "datos", STAGE / "datos", exclude_names=("raw",))
copy_tree(ROOT / "productos", STAGE / "productos", exclude_names=("__pycache__",))
copy_tree(ROOT / "anexos", STAGE / "anexos")

zip_path = OUT / f"{NAME}.zip"
if zip_path.exists():
    zip_path.unlink()
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for p in STAGE.rglob("*"):
        if p.is_file():
            zf.write(p, Path(NAME) / p.relative_to(STAGE))

required = {
    f"{NAME}/README.md",
    f"{NAME}/T2_202602_G00_informe.pdf",
    f"{NAME}/T2_202602_G00_presentacion.pdf",
    f"{NAME}/codigo/punto2/auditar_pre_informe.py",
    f"{NAME}/datos/punto2/Abtsgmuend_Untergroeningen/abtsgmuend_precipitation_10min.csv",
    f"{NAME}/productos/punto2/referencias_apa7.md",
    f"{NAME}/productos/punto2/declaracion_uso_ia.md",
    f"{NAME}/anexos/tarea2_enunciado.pdf",
}
with zipfile.ZipFile(zip_path) as zf:
    names = set(zf.namelist())
missing = sorted(required - names)
validation = OUT / "validacion_zip.md"
validation.write_text(
    f"# Validación del ZIP\n\n- Archivo: `{zip_path.name}`\n"
    f"- Tamaño: {zip_path.stat().st_size} bytes\n"
    f"- Entradas: {len(names)}\n- Raíz interna: `{NAME}/`\n"
    f"- Elementos requeridos faltantes: {', '.join(missing) if missing else 'ninguno'}\n"
    "- Estado: **válido como paquete provisional**; sustituir `G00` y añadir el punto 1 antes de entregar.\n",
    encoding="utf-8",
)
print(zip_path)
print(validation)
print("missing=", missing)
