"""Validate this design handoff; this does not validate Stellaris gameplay."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def validate():
    data = json.loads((ROOT / "design/requirements.json").read_text(encoding="utf-8"))
    status = json.loads((ROOT / "design/project-status.json").read_text(encoding="utf-8"))
    reqs = data["requirements"]
    ids = [item["id"] for item in reqs]
    require(len(ids) == len(set(ids)), "Duplicate requirement IDs")
    require(len(reqs) == 32, "Expected all 32 handoff requirements")
    require(all(item["status"] == "confirmed_direction_not_implemented" for item in reqs), "Unexpected implemented requirement claim")
    gray = data["population"]["gray_population"]
    require(gray["fill_delay_months"] == {"min": 3, "max": 6}, "Population fill delay changed")
    require(gray["job_scope"] == "enabled_non_elite_jobs", "Non-elite employment scope changed")
    require(gray["surplus_policy"] == "remove_surplus_gray_population", "Surplus removal rule lost")
    require(not gray["resettlement_as_surplus_policy"], "Superseded resettlement policy restored")
    require(not gray["reserve_jobs_as_surplus_policy"], "Superseded reserve jobs restored")
    require(data["population"]["leader_species"] == "白蚊人", "White-only leader rule lost")
    require(data["ascension"]["haipam"]["combined"], "Combined ascension requirement lost")
    require(set(data["ascension"]["haipam"]["paths"]) == {"genetic", "psionic"}, "Haipam ascension routes changed")
    steel = data["ascension"]["steel_mosquito"]
    require(steel["initial_species"] == ["白蚊人", "机器人"], "Steel civilization composition changed")
    require(steel["path"] == "synthetic", "Steel ascension route changed")
    require(not steel["gray_species_conversion_is_origin_story"], "Superseded gray-to-steel origin restored")
    require(data["events"]["midgame"]["after_refusal_dialogue"] == "饿殍遍地", "Hunger dialogue missing")
    require(status["implemented_game_features"] == 0 and status["custom_models"] == 0, "Design handoff misrepresented as implemented")
    require(not status["in_game_tests_passed"], "Unperformed game testing claimed")
    manifest = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))
    paths = set()
    for entry in manifest["files"]:
        rel = entry["path"]
        require(rel not in paths, "Duplicate manifest path")
        paths.add(rel)
        file = (ROOT / rel).resolve()
        require(file.is_relative_to(ROOT) and not (ROOT / rel).is_symlink(), "Unsafe manifest path")
        raw = file.read_bytes()
        require(len(raw) == entry["bytes"], "Size mismatch: " + rel)
        require(hashlib.sha256(raw).hexdigest() == entry["sha256"], "Hash mismatch: " + rel)
        raw.decode("utf-8")
    print(json.dumps({"ok": True, "requirements": len(reqs), "verified_files": len(paths), "scope": "design_integrity_only", "gameplay_verified": False}, ensure_ascii=False))
    return True

if __name__ == "__main__":
    try:
        validate()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        sys.exit(1)

