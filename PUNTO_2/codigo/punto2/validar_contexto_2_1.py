"""Resume la evidencia OSM alrededor del outlet para cerrar 2.1."""
from pathlib import Path
import json, math

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datos" / "punto2" / "Abtsgmuend_Untergroeningen" / "control_2_1"
LAT, LON = 48.9181944444, 9.9123611111

def distance_m(element):
    c = element.get("center", {})
    return 111320 * math.hypot(c.get("lat", LAT) - LAT,
                               (c.get("lon", LON) - LON) * math.cos(math.radians(LAT)))

def main():
    data = json.loads((DATA / "osm_outlet_context.json").read_text(encoding="utf-8"))
    water = []
    roads = []
    for e in data.get("elements", []):
        tags = e.get("tags", {})
        if tags.get("waterway"):
            water.append({"distance_m": round(distance_m(e), 1), "name": tags.get("name", ""), "type": tags["waterway"]})
        if tags.get("highway"):
            roads.append({"distance_m": round(distance_m(e), 1), "name": tags.get("name", ""), "type": tags["highway"]})
    water.sort(key=lambda x: x["distance_m"]); roads.sort(key=lambda x: x["distance_m"])
    out = {"outlet_lat": LAT, "outlet_lon": LON, "osm_elements": len(data.get("elements", [])),
           "waterways_within_1200m": len(water), "roads_within_1200m": len(roads),
           "nearest_waterway": water[0] if water else None, "nearest_road": roads[0] if roads else None,
           "named_waterways": sorted({x["name"] for x in water if x["name"]}),
           "osm_query_radius_m": 1200}
    (DATA / "osm_outlet_summary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False))

if __name__ == "__main__":
    main()
