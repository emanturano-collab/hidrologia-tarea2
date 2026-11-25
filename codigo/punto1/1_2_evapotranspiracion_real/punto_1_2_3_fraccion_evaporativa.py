"""Calcula fracciones evaporativas anuales para el numeral 1.2.3.

Usa exclusivamente la comparacion anual ya validada entre el techo energetico
R_n/lambda y ET=P-Q. No descarga datos ni modifica los productos fuente.
"""

from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
PRODUCT_DIR = ROOT / "productos" / "punto1"
SOURCE = PRODUCT_DIR / "punto_1_2_3_techo_energetico_vs_balance_anual.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError("Falta la comparacion anual de techo energetico y balance.")
    source_rows = read_csv(SOURCE)
    if len(source_rows) != 21:
        raise ValueError(f"Se esperaban 21 anos hidrologicos comunes; se obtuvieron {len(source_rows)}.")

    annual: list[dict] = []
    for row in source_rows:
        ceiling = float(row["rn_lambda_mm_year"])
        et_l = float(row["et_l_mm_year"])
        et_i = float(row["et_i_mm_year"])
        if not math.isfinite(ceiling) or ceiling <= 0:
            raise ValueError(f"Techo energetico no positivo o no finito en {row['hydrological_year']}.")
        if not math.isfinite(et_l) or not math.isfinite(et_i):
            raise ValueError(f"ET no finita en {row['hydrological_year']}.")
        f_l = et_l / ceiling
        f_i = et_i / ceiling
        annual.append({
            "hydrological_year": row["hydrological_year"],
            "period": row["period"],
            "rn_lambda_mm_year": ceiling,
            "et_l_mm_year": et_l,
            "et_i_mm_year": et_i,
            "f_et_l_dimensionless": f_l,
            "f_et_l_percent": 100.0 * f_l,
            "f_et_i_dimensionless": f_i,
            "f_et_i_percent": 100.0 * f_i,
            "f_et_l_negative": f_l < 0.0,
            "f_et_l_greater_than_1": f_l > 1.0,
            "f_et_i_negative": f_i < 0.0,
            "f_et_i_greater_than_1": f_i > 1.0,
        })

    def mean(field: str) -> float:
        return sum(float(row[field]) for row in annual) / len(annual)

    # Fraccion multianual: cociente de promedios, no promedio de fracciones.
    mean_ceiling = mean("rn_lambda_mm_year")
    mean_et_l = mean("et_l_mm_year")
    mean_et_i = mean("et_i_mm_year")
    f_l_multiyear = mean_et_l / mean_ceiling
    f_i_multiyear = mean_et_i / mean_ceiling
    summary = [{
        "common_complete_hydrological_years": ";".join(row["hydrological_year"] for row in annual),
        "number_of_years": len(annual),
        "period": "AH 2002; AH 2004-AH 2023",
        "mean_rn_lambda_mm_year": mean_ceiling,
        "mean_et_l_mm_year": mean_et_l,
        "mean_et_i_mm_year": mean_et_i,
        "f_et_l_multiyear_dimensionless": f_l_multiyear,
        "f_et_l_multiyear_percent": 100.0 * f_l_multiyear,
        "f_et_i_multiyear_dimensionless": f_i_multiyear,
        "f_et_i_multiyear_percent": 100.0 * f_i_multiyear,
        "method": "f_ET_multiyear = mean(ET) / mean(Rn/lambda); not mean(annual f_ET)",
        "years_f_et_l_negative": ";".join(row["hydrological_year"] for row in annual if row["f_et_l_negative"]),
        "years_f_et_l_greater_than_1": ";".join(row["hydrological_year"] for row in annual if row["f_et_l_greater_than_1"]),
        "years_f_et_i_negative": ";".join(row["hydrological_year"] for row in annual if row["f_et_i_negative"]),
        "years_f_et_i_greater_than_1": ";".join(row["hydrological_year"] for row in annual if row["f_et_i_greater_than_1"]),
    }]

    annual_output = PRODUCT_DIR / "punto_1_2_3_fraccion_evaporativa_anual.csv"
    summary_output = PRODUCT_DIR / "punto_1_2_3_fraccion_evaporativa_resumen.csv"
    verification_output = PRODUCT_DIR / "punto_1_2_3_fraccion_evaporativa_verificacion.json"
    write_csv(annual_output, annual, list(annual[0]))
    write_csv(summary_output, summary, list(summary[0]))
    verification_output.write_text(json.dumps({
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(SOURCE.relative_to(ROOT)),
        "formula": "f_ET = ET / (Rn/lambda) = lambda*ET/Rn",
        "number_of_common_hydrological_years": len(annual),
        "multiyear_method": "ratio of the matching 21-year means",
        "checks": {
            "all_energy_ceilings_positive": True,
            "negative_f_et_l": [row["hydrological_year"] for row in annual if row["f_et_l_negative"]],
            "f_et_l_greater_than_1": [row["hydrological_year"] for row in annual if row["f_et_l_greater_than_1"]],
            "negative_f_et_i": [row["hydrological_year"] for row in annual if row["f_et_i_negative"]],
            "f_et_i_greater_than_1": [row["hydrological_year"] for row in annual if row["f_et_i_greater_than_1"]],
        },
    }, indent=2), encoding="utf-8")
    print(json.dumps({
        "annual": str(annual_output),
        "summary": str(summary_output),
        "verification": str(verification_output),
        "f_et_l_multiyear_percent": 100.0 * f_l_multiyear,
        "f_et_i_multiyear_percent": 100.0 * f_i_multiyear,
    }, indent=2))


if __name__ == "__main__":
    main()
