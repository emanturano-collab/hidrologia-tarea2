"""Calcula el techo energetico anual y lo compara con ET=P-Q.

Lee exclusivamente productos existentes: la serie mensual de radiacion neta de
1.2.3 y la tabla de anos hidrologicos de 1.2.1. No descarga datos ni modifica
ninguna fuente. Los anos hidrologicos van de septiembre a agosto y se nombran
por el ano de agosto (por ejemplo, AH 2002 = 2001-09 a 2002-08).
"""

from __future__ import annotations

import calendar
import csv
import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
PRODUCT_DIR = ROOT / "productos" / "punto1"
RADIATION_MONTHLY = PRODUCT_DIR / "punto_1_2_3_radiacion_neta_real_era5land_mensual.csv"
BALANCE_HYDROLOGICAL = PRODUCT_DIR / "punto_1_2_anios_hidrologicos_sep_ago.csv"
LAMBDA_J_KG = 2.45e6


def read_csv(path: Path) -> list[dict[str, str]]:
    # ``utf-8-sig`` admite tanto UTF-8 normal como el BOM presente en la
    # tabla hidrologica original, sin modificar el archivo fuente.
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def hydrological_year(month: str) -> int:
    year, month_number = map(int, month.split("-"))
    return year + 1 if month_number >= 9 else year


def expected_months(year: int) -> list[str]:
    return [f"{year - 1}-{month:02d}" for month in range(9, 13)] + [f"{year}-{month:02d}" for month in range(1, 9)]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if not RADIATION_MONTHLY.exists() or not BALANCE_HYDROLOGICAL.exists():
        raise FileNotFoundError("Falta la serie mensual de radiacion o la tabla hidrologica original de 1.2.1.")

    radiation_rows = read_csv(RADIATION_MONTHLY)
    if len(radiation_rows) != 276:
        raise ValueError(f"Se esperaban 276 meses de radiacion; se obtuvieron {len(radiation_rows)}.")
    by_year: dict[int, list[dict[str, str]]] = defaultdict(list)
    seen_months: set[str] = set()
    for row in radiation_rows:
        month = row["month"]
        if month in seen_months:
            raise ValueError(f"Mes duplicado en la radiacion: {month}.")
        seen_months.add(month)
        if row["complete"] != "True" or row["valid_grid_cells"] != "33" or float(row["spatial_weight_covered_pct"]) != 100.0:
            raise ValueError(f"Cobertura espacial incompleta en {month}.")
        if row["ssr_source_units"] != "J m**-2" or row["str_source_units"] != "J m**-2":
            raise ValueError(f"Unidades no esperadas en {month}.")
        rn_month = float(row["rn_monthly_energy_j_m2"])
        water_month = float(row["energy_equivalent_mm_month"])
        if not math.isclose(rn_month / LAMBDA_J_KG, water_month, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(f"Conversion J/m2 a mm inconsistente en {month}.")
        by_year[hydrological_year(month)].append(row)

    energy_annual: list[dict] = []
    for year in sorted(by_year):
        rows = sorted(by_year[year], key=lambda row: row["month"])
        months = [row["month"] for row in rows]
        if months != expected_months(year):
            continue
        rn_j_m2_year = sum(float(row["rn_monthly_energy_j_m2"]) for row in rows)
        rn_mm_year = sum(float(row["energy_equivalent_mm_month"]) for row in rows)
        if not math.isclose(rn_j_m2_year / LAMBDA_J_KG, rn_mm_year, rel_tol=0.0, abs_tol=1e-10):
            raise ValueError(f"Conversion anual J/m2 a mm inconsistente en AH {year}.")
        energy_annual.append({
            "hydrological_year": f"AH {year}",
            "period": f"{year - 1}-09 a {year}-08",
            "months_available": len(rows),
            "rn_annual_energy_j_m2": rn_j_m2_year,
            "rn_lambda_mm_year": rn_mm_year,
        })

    if len(energy_annual) != 23:
        raise ValueError(f"Se esperaban 23 anos hidrologicos completos de energia; se obtuvieron {len(energy_annual)}.")

    balance_rows = read_csv(BALANCE_HYDROLOGICAL)
    balance_complete: dict[str, dict[str, str]] = {}
    for row in balance_rows:
        if row["status"] == "Completo":
            if any(row[field] == "" for field in ("pl_mm_year", "pi_mm_year", "q_mm_year", "et_l_mm_year", "et_i_mm_year")):
                raise ValueError(f"Balance completo con valores vacios: {row['hydrological_year']}.")
            balance_complete[row["hydrological_year"]] = row
    if len(balance_complete) != 21:
        raise ValueError(f"Se esperaban 21 anos completos en el balance original; se obtuvieron {len(balance_complete)}.")

    comparison: list[dict] = []
    for energy in energy_annual:
        year_label = energy["hydrological_year"]
        if year_label not in balance_complete:
            continue
        balance = balance_complete[year_label]
        et_l = float(balance["et_l_mm_year"])
        et_i = float(balance["et_i_mm_year"])
        ceiling = energy["rn_lambda_mm_year"]
        exceeds_l = et_l > ceiling
        exceeds_i = et_i > ceiling
        comparison.append({
            "hydrological_year": year_label,
            "period": energy["period"],
            "rn_lambda_mm_year": ceiling,
            "et_l_mm_year": et_l,
            "et_i_mm_year": et_i,
            "rn_lambda_minus_et_l_mm_year": ceiling - et_l,
            "rn_lambda_minus_et_i_mm_year": ceiling - et_i,
            "et_l_exceeds_energy_ceiling": exceeds_l,
            "et_i_exceeds_energy_ceiling": exceeds_i,
            "any_et_exceeds_energy_ceiling": exceeds_l or exceeds_i,
        })

    if len(comparison) != 21:
        raise ValueError(f"El cruce energia-balance debe tener 21 anos comunes; se obtuvieron {len(comparison)}.")

    def mean(field: str) -> float:
        return sum(float(row[field]) for row in comparison) / len(comparison)

    summary = [{
        "common_complete_hydrological_years": ";".join(row["hydrological_year"] for row in comparison),
        "number_of_years": len(comparison),
        "period": "AH 2002; AH 2004-AH 2023",
        "mean_rn_lambda_mm_year": mean("rn_lambda_mm_year"),
        "mean_et_l_mm_year": mean("et_l_mm_year"),
        "mean_et_i_mm_year": mean("et_i_mm_year"),
        "mean_rn_lambda_minus_et_l_mm_year": mean("rn_lambda_minus_et_l_mm_year"),
        "mean_rn_lambda_minus_et_i_mm_year": mean("rn_lambda_minus_et_i_mm_year"),
        "years_et_l_exceeds_energy_ceiling": ";".join(row["hydrological_year"] for row in comparison if row["et_l_exceeds_energy_ceiling"]),
        "years_et_i_exceeds_energy_ceiling": ";".join(row["hydrological_year"] for row in comparison if row["et_i_exceeds_energy_ceiling"]),
    }]

    PRODUCT_DIR.mkdir(parents=True, exist_ok=True)
    energy_output = PRODUCT_DIR / "punto_1_2_3_techo_energetico_anual.csv"
    comparison_output = PRODUCT_DIR / "punto_1_2_3_techo_energetico_vs_balance_anual.csv"
    summary_output = PRODUCT_DIR / "punto_1_2_3_techo_energetico_vs_balance_resumen.csv"
    verification_output = PRODUCT_DIR / "punto_1_2_3_techo_energetico_verificacion.json"
    write_csv(energy_output, energy_annual, list(energy_annual[0]))
    write_csv(comparison_output, comparison, list(comparison[0]))
    write_csv(summary_output, summary, list(summary[0]))
    verification_output.write_text(json.dumps({
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "radiation_source": str(RADIATION_MONTHLY.relative_to(ROOT)),
        "balance_hydrological_source": str(BALANCE_HYDROLOGICAL.relative_to(ROOT)),
        "monthly_radiation_months": len(radiation_rows),
        "monthly_radiation_period": [min(seen_months), max(seen_months)],
        "complete_energy_hydrological_years": len(energy_annual),
        "complete_balance_hydrological_years": len(balance_complete),
        "common_hydrological_years": [row["hydrological_year"] for row in comparison],
        "excluded_balance_years": [row["hydrological_year"] for row in balance_rows if row["status"] != "Completo"],
        "units": {"rn_annual_energy": "J m-2 year-1", "rn_lambda_et_differences": "mm year-1"},
        "conversion": "rn_lambda_mm_year = rn_annual_energy_j_m2 / 2450000",
        "checks": {"all_months_complete_with_33_weights": True, "annual_conversion_identity_checked": True},
    }, indent=2), encoding="utf-8")
    print(json.dumps({
        "energy_annual": str(energy_output),
        "comparison": str(comparison_output),
        "summary": str(summary_output),
        "verification": str(verification_output),
        "common_years": len(comparison),
    }, indent=2))


if __name__ == "__main__":
    main()
