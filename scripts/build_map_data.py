# -*- coding: utf-8 -*-
"""data/map-facilities.json を AREA ページ（map/index.html）へ反映し、基本整合性を検査する。"""

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "map-facilities.json"
MAP_PATH = ROOT / "map" / "index.html"
PATTERN = re.compile(r"ALL=uniqueFacilities\((\[.*?\])\);", re.S)


def valid_position(item):
    lat, lng = item.get("lat"), item.get("lng")
    return (
        isinstance(lat, (int, float))
        and isinstance(lng, (int, float))
        and lat not in (None, 0)
        and lng not in (None, 0)
    )


def validate(rows):
    errors = []
    source_rows = [item.get("sourceRow") for item in rows]
    if len(source_rows) != len(set(source_rows)):
        errors.append("sourceRow が重複しています")
    for item in rows:
        for key in ("name", "pref", "sourceRow", "lat", "lng"):
            if key not in item:
                errors.append(f"必須項目がありません: {item.get('name', '?')} / {key}")
        has_lat = item.get("lat") not in (None, 0)
        has_lng = item.get("lng") not in (None, 0)
        if has_lat != has_lng:
            errors.append(f"緯度・経度の片方だけがあります: {item.get('name')}")
    if errors:
        raise RuntimeError("\n".join(errors))


def render(source, rows):
    compact = json.dumps(rows, ensure_ascii=False, separators=(",", ":"))
    replacement = f"ALL=uniqueFacilities({compact});"
    result, count = PATTERN.subn(lambda _match: replacement, source, count=1)
    if count != 1:
        raise RuntimeError("map/index.html の施設データを検出できません")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="HTMLが正本と同期しているかだけ確認")
    args = parser.parse_args()

    old = MAP_PATH.read_text(encoding="utf-8")
    rows = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    validate(rows)
    new = render(old, rows)
    coordinates = sum(valid_position(item) for item in rows)

    if args.check:
        if new != old:
            raise SystemExit("NG: map/index.html が data/map-facilities.json と同期していません")
        print(f"OK: facilities={len(rows)}, coordinates={coordinates}, missing={len(rows)-coordinates}")
        return

    MAP_PATH.write_text(new, encoding="utf-8")
    print(f"UPDATED: facilities={len(rows)}, coordinates={coordinates}, missing={len(rows)-coordinates}")


if __name__ == "__main__":
    main()
