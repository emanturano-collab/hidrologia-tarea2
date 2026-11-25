"""Construye los productos documentales complementarios del numeral 1.3.3.

No recalcula Budyko ni elasticidad.  Registra únicamente evidencia verificada
en fuentes que ya están dentro del proyecto y las limitaciones de inferencia.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = next(p for p in Path(__file__).resolve().parents if (p / "codigo").is_dir() and (p / "datos").is_dir())
ANEXOS = ROOT / "anexos" / "punto1" / "1_3_regimen_evaporativo"
TABLAS = ROOT / "productos" / "punto1" / "1_3_regimen_evaporativo" / "tablas"
METADATOS = ROOT / "datos" / "punto1" / "metadatos"
FUENTES = ANEXOS / "fuentes_documentales"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    bocatoma = FUENTES / "PEOT_Bocatoma_Racarumi.pdf"
    trasvases = FUENTES / "PEOT_Trasvases_Chotano_Conchano_2025.pdf"
    for source in (bocatoma, trasvases):
        if not source.is_file():
            raise FileNotFoundError(source)

    evidence = [
        {
            "id": "PEOT-BR-01",
            "tema": "Bocatoma Racarumi y Sistema Tinajones",
            "fuente_relativa": "tarea 02/anexos/punto1/1_3_regimen_evaporativo/fuentes_documentales/PEOT_Bocatoma_Racarumi.pdf",
            "institucion": "Proyecto Especial Olmos Tinajones (PEOT), Gobierno Regional Lambayeque",
            "fecha_documento": "julio de 2023",
            "pagina_pdf": "12",
            "pagina_impresa": "12 de 21",
            "evidencia_verificada": "Ubica la Bocatoma Racarumi en la cuenca del río Chancay, como parte de la Infraestructura Mayor de Riego del Sistema Hidráulico Mayor Tinajones, operado por PEOT.",
            "relevancia_budyko": "El caudal observado no debe suponerse automáticamente como salida natural no regulada; se requiere contrastar la estación con la operación del sistema.",
            "limite_de_inferencia": "No aporta serie de caudales, derivaciones, volúmenes ni establece el efecto en PE_200907.",
        },
        {
            "id": "PEOT-BR-02",
            "tema": "Regulación y derivación",
            "fuente_relativa": "tarea 02/anexos/punto1/1_3_regimen_evaporativo/fuentes_documentales/PEOT_Bocatoma_Racarumi.pdf",
            "institucion": "PEOT, Gerencia de Operación y Mantenimiento del Sistema Mayor Tinajones",
            "fecha_documento": "julio de 2023",
            "pagina_pdf": "3, 5, 12",
            "pagina_impresa": "3, 5 y 12 de 21",
            "evidencia_verificada": "Describe protección de barrajes, poza disipadora y canalización; además, condiciona la ejecución de obra al sistema de operación de la Bocatoma y a coordinación con Junta de Usuarios, ANA y OPEMA.",
            "relevancia_budyko": "Constituye evidencia de infraestructura y gestión hidráulica relevantes para interpretar P−Q y la desviación de la curva de Budyko.",
            "limite_de_inferencia": "No identifica el sentido, la magnitud ni el calendario de un posible efecto sobre la serie CAMELS-PE.",
        },
        {
            "id": "PEOT-TC-01",
            "tema": "Trasvase Chotano–Chancay-Lambayeque",
            "fuente_relativa": "tarea 02/anexos/punto1/1_3_regimen_evaporativo/fuentes_documentales/PEOT_Trasvases_Chotano_Conchano_2025.pdf",
            "institucion": "Proyecto Especial Olmos Tinajones (PEOT)",
            "fecha_documento": "19 de diciembre de 2025",
            "pagina_pdf": "1",
            "pagina_impresa": "1 de 2",
            "evidencia_verificada": "PEOT informa mantenimiento de los túneles Chotano y Conchano para asegurar la operatividad, seguridad y continuidad del trasvase del río Chotano hacia el valle Chancay-Lambayeque.",
            "relevancia_budyko": "Documenta una fuente externa potencial al sistema Chancay-Lambayeque; por tanto, P local y Q observado pueden no cerrar un balance estrictamente natural de cuenca.",
            "limite_de_inferencia": "No permite asignar aportes al punto de aforo Racarumi ni reconstruirlos retrospectivamente.",
        },
        {
            "id": "PEOT-TC-02",
            "tema": "Oferta hídrica y mantenimiento de trasvases",
            "fuente_relativa": "tarea 02/anexos/punto1/1_3_regimen_evaporativo/fuentes_documentales/PEOT_Trasvases_Chotano_Conchano_2025.pdf",
            "institucion": "Proyecto Especial Olmos Tinajones (PEOT)",
            "fecha_documento": "19 de diciembre de 2025",
            "pagina_pdf": "2",
            "pagina_impresa": "2 de 2",
            "evidencia_verificada": "Informa trabajos para mantener la infraestructura en condiciones para el trasvase de agua del río Chotano y fortalecer la oferta para uso poblacional, agrícola e industrial en Lambayeque.",
            "relevancia_budyko": "Refuerza que la interpretación de ET/P obtenida como P−Q debe permanecer exploratoria mientras falten balances de almacenamiento y operación.",
            "limite_de_inferencia": "La nota es de 2025; no documenta por sí sola la condición de cada año 1981–2023.",
        },
    ]
    write_csv(TABLAS / "1_3_3_evidencias_documentales_PEOT.csv", evidence)

    attributes = [
        {"atributo": "Identificador CAMELS-PE", "valor": "PE_200907", "unidad_o_categoria": "—", "fuente_local": "selection_summary.csv; station.csv", "estado": "verificado", "nota": "Estación Racarumi."},
        {"atributo": "Nombre oficial de cuenca", "valor": "Cuenca Chancay-Lambayeque", "unidad_o_categoria": "—", "fuente_local": "selection_summary.csv", "estado": "verificado", "nota": "Nombre contenido en la metadata seleccionada de CAMELS-PE."},
        {"atributo": "Área", "valor": "2363.302", "unidad_o_categoria": "km²", "fuente_local": "selection_summary.csv (topographic_attributes.csv)", "estado": "verificado", "nota": "Atributo topográfico preservado localmente."},
        {"atributo": "Cota de estación", "valor": "265", "unidad_o_categoria": "m s.n.m.", "fuente_local": "station.csv", "estado": "verificado", "nota": "No representa la elevación media de toda la cuenca."},
        {"atributo": "Elevación media ponderada de celdas SRTM", "valor": "2348.98", "unidad_o_categoria": "m", "fuente_local": "PE_200907_ERA5Land_cells_SRTM_elevation.csv", "estado": "verificado", "nota": "Media ponderada con los 33 pesos espaciales de Tarea 1."},
        {"atributo": "Rango altitudinal SRTM en celdas intersectadas", "valor": "264–4084", "unidad_o_categoria": "m", "fuente_local": "PE_200907_ERA5Land_cells_SRTM_elevation.csv", "estado": "verificado", "nota": "Extremos de las celdas; no se presenta como atributo estático CAMELS."},
        {"atributo": "Cobertura vegetal / uso del suelo", "valor": "No disponible", "unidad_o_categoria": "—", "fuente_local": "Paquete CAMELS-PE local preservado", "estado": "no verificado", "nota": "No se halló tabla local de atributos de cobertura/uso para PE_200907."},
        {"atributo": "Cobertura forestal", "valor": "No disponible", "unidad_o_categoria": "—", "fuente_local": "Paquete CAMELS-PE local preservado", "estado": "no verificado", "nota": "No inferir a partir de la altitud ni de los documentos PEOT."},
        {"atributo": "Nieve y glaciares", "valor": "No disponible", "unidad_o_categoria": "—", "fuente_local": "Paquete CAMELS-PE local preservado", "estado": "no verificado", "nota": "No se encontró atributo o inventario local que permita afirmarlo o descartarlo."},
        {"atributo": "Características del suelo", "valor": "No disponible", "unidad_o_categoria": "—", "fuente_local": "Paquete CAMELS-PE local preservado", "estado": "no verificado", "nota": "La humedad ERA5-Land no sustituye atributos edáficos observados."},
        {"atributo": "Tipo de caudal CAMELS-PE", "valor": "flow_obs: Observed streamflow", "unidad_o_categoria": "mm/día", "fuente_local": "data_dictionary.csv; daily_audit_summary.json", "estado": "verificado", "nota": "La metadata local no dice que esté naturalizado."},
        {"atributo": "Naturalización del caudal", "valor": "No documentada", "unidad_o_categoria": "—", "fuente_local": "Metadata CAMELS-PE local", "estado": "no verificado", "nota": "No es válido afirmar que Q sea naturalizado ni que incluya trasvases sin metadatos de estación/operación."},
        {"atributo": "Intervención hidráulica contextual", "valor": "Bocatoma Racarumi y Sistema Hidráulico Mayor Tinajones operado por PEOT; trasvase Chotano–Chancay-Lambayeque documentado", "unidad_o_categoria": "evidencia documental", "fuente_local": "Dos documentos PEOT incorporados", "estado": "verificado como contexto", "nota": "No cuantifica ni prueba el efecto en la serie de la estación."},
    ]
    write_csv(TABLAS / "1_3_3_atributos_fisicos_CAMELSPE_Racarumi.csv", attributes)

    interpretation = """# 1.3.3 Budyko — complemento documental y físico

## Alcance

Este complemento **no recalcula** el ajuste de Fu ni las elasticidades. Interpreta
los resultados exploratorios ya verificados para el periodo común 2002–2022:
índice de aridez `φ = 1.098`, índice evaporativo de diagnóstico `(P−Q)/P =
0.540`, `ω = 1.756`, distancia vertical a Budyko (1974) `−0.186` y elasticidad
teórica `1.555`; la elasticidad empírica previamente estimada es `1.488`.

## Evidencia incorporada

El documento técnico de PEOT de julio de 2023 ubica la Bocatoma Racarumi en la
cuenca del río Chancay, la integra al Sistema Hidráulico Mayor Tinajones y señala
que PEOT lo opera (p. 12 impresa). También muestra infraestructura de barrajes,
protección y coordinación de condiciones de operación (pp. 3, 5 y 12).

La nota institucional de PEOT del 19 de diciembre de 2025 informa mantenimiento
de los túneles Chotano y Conchano para el trasvase del río Chotano hacia el valle
Chancay-Lambayeque (pp. 1–2). Es evidencia de conexión hidráulica y de gestión,
no una serie de aportes históricos ni una cuantificación de transferencia.

## Lectura científica prudente

La distancia vertical negativa indica que el cociente diagnóstico `(P−Q)/P` está
por debajo de la curva de Budyko (1974) para el `φ` usado. Esta posición no debe
atribuirse a vegetación, nieve, suelo o regulación de forma aislada: el paquete
local conservado no aporta atributos estáticos verificables de cobertura vegetal,
bosque, nieve/glaciares ni suelo para PE_200907.

Sí hay heterogeneidad altitudinal verificada en las celdas SRTM de Tarea 1
(264–4084 m; media ponderada 2348.98 m), además de estacionalidad y humedad
radicular ya analizadas. Esos factores son hipótesis físicamente plausibles para
explorar cuando existan datos consistentes, pero no explicaciones cuantificadas
de la desviación.

La metadata local de CAMELS-PE clasifica `flow_obs` como **caudal observado** y
no documenta naturalización. Junto con la evidencia de infraestructura/trasvase,
esto obliga a mantener `(P−Q)/P` como diagnóstico exploratorio y no como ET real:
faltan `ΔS` anual, ubicación hidráulica exacta del aforo frente a las obras,
series históricas de trasvases/derivaciones, operación de Tinajones y metodología
de naturalización si existiera.

## Datos requeridos para cerrar la interpretación

1. Ficha CAMELS-PE/SENAMHI de la estación: ubicación, datum, área efectiva y si
   el caudal fue naturalizado, regulado o corregido.
2. Series mensuales/anuales 1981–2023 de trasvases Chotano y Conchano, derivaciones
   de Bocatoma Racarumi, reglas de operación, niveles/volúmenes de almacenamiento.
3. Balance consolidado del numeral 1.2 con ET real y evaluación de `ΔS` anual.
4. Atributos espaciales trazables de uso/cobertura, bosque, suelo, nieve/glaciares
   y, si procede, evolución temporal de cobertura.

## Referencias

- Proyecto Especial Olmos Tinajones (PEOT), Gobierno Regional Lambayeque (2023).
  *Términos de Referencia: Supervisión de la obra Rehabilitación de la Bocatoma
  Racarumi del Sistema Hidráulico Mayor Tinajones*. Chiclayo, julio de 2023.
- Proyecto Especial Olmos Tinajones (PEOT) (2025). *PEOT concluye mantenimiento
  en túneles Chotano y Conchano para asegurar el trasvase de aguas hacia
  Lambayeque*. Nota institucional, 19 de diciembre de 2025.
- Fu, B. P. (1981). On the calculation of the evaporation from land surface.
  *Scientia Atmospherica Sinica*, 5, 23–31.
- Budyko, M. I. (1974). *Climate and Life*. Academic Press.
"""
    report = ANEXOS / "1_3_3_interpretacion_documental_Budyko.md"
    report.write_text(interpretation, encoding="utf-8")
    trace = {
        "scope": "Evidencia documental complementaria para 1.3.3; sin recálculo de Budyko ni elasticidad.",
        "pdfs": [
            {"path_relative": str(bocatoma.relative_to(ROOT)).replace("\\\\", "/"), "sha256": sha256(bocatoma), "bytes": bocatoma.stat().st_size, "physical_pdf_pages": 23, "key_pages": [3, 5, 12]},
            {"path_relative": str(trasvases.relative_to(ROOT)).replace("\\\\", "/"), "sha256": sha256(trasvases), "bytes": trasvases.stat().st_size, "physical_pdf_pages": 2, "key_pages": [1, 2]},
        ],
        "camels_local_sources": [
            "datos/punto1/originales/tarea1_minimos/selection_summary.csv",
            "datos/punto1/originales/tarea1_minimos/station.csv",
            "datos/punto1/originales/tarea1_minimos/data_dictionary.csv",
            "datos/punto1/originales/tarea1_minimos/PE_200907_ERA5Land_cells_SRTM_elevation.csv",
        ],
        "limitations": [
            "La evidencia PEOT prueba infraestructura/operación contextual, no el efecto cuantitativo en la estación.",
            "La metadata CAMELS-PE local no documenta naturalización de flow_obs.",
            "Los atributos estáticos de vegetación, suelo, bosque, nieve y glaciares no están conservados en el paquete local inspeccionado.",
        ],
    }
    METADATOS.mkdir(parents=True, exist_ok=True)
    (METADATOS / "1_3_3_trazabilidad_fuentes_documentales.json").write_text(json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
