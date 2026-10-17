"""Create a ZIP and verify its complete payload using SHA-256."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", "__pycache__", "reports", "releases", "work", "local", "local-backups"}

def payload_files():
    return sorted(
        p for p in ROOT.rglob("*")
        if p.is_file() and not p.is_symlink()
        and not EXCLUDED.intersection(p.relative_to(ROOT).parts)
        and p.name not in {"MANIFEST.json", "local-install-report.json", "zz_haipam_local_rules.txt", "weapon_components.csv"}
        and p.suffix not in {".pyc", ".log", ".key", ".pem", ".pfx", ".tmp"}
        and not p.name.startswith('zz_haipam_dual_')
        and not p.name.startswith('.env')
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT.parent / "haipam-stellaris-prototype-v0.5.1-20261017.zip"))
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("ZIP must be outside the source directory")
    if output.suffix.lower() != ".zip":
        raise ValueError("Output must have .zip suffix")
    output.parent.mkdir(parents=True, exist_ok=True)
    files = payload_files()
    manifest = {
        "package_version": re.search(r'version="([^"]+)"', (ROOT/"mod/haipam/descriptor.mod").read_text(encoding="utf-8"))[1],
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "kind": "mod_source_prototype_and_design",
        "gameplay_verified": False,
        "files": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
    }
    manifest_path = ROOT / "MANIFEST.json"
    manifest_temp=manifest_path.with_suffix('.json.tmp')
    manifest_temp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest_temp.replace(manifest_path)
    subprocess.run([sys.executable, str(ROOT / "scripts/validate_handoff.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/validate_mod.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/validate_content.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/validate_frontier.py")], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts/dual_ascension_adapter.py")], check=True)
    files.append(manifest_path)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for p in files:
            archive.write(p, ROOT.name + "/" + p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(output) as archive:
        corrupt = archive.testzip()
        if corrupt is not None:
            raise ValueError("ZIP CRC failure")
        if len(archive.namelist()) != len(files) or len(set(archive.namelist())) != len(files):
            raise ValueError("ZIP entry count mismatch")
        for p in files:
            name = ROOT.name + "/" + p.relative_to(ROOT).as_posix()
            if hashlib.sha256(archive.read(name)).digest() != hashlib.sha256(p.read_bytes()).digest():
                raise ValueError("ZIP payload mismatch: " + name)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    checksum = Path(str(output) + ".sha256")
    checksum.write_text(digest + "  " + output.name + "\n", encoding="utf-8")
    report = {"ok": True, "archive": output.name, "bytes": output.stat().st_size, "sha256": digest, "zip_entries": len(files), "all_payload_hashes_match": True, "requirements": 32, "scope": "mod_source_prototype_and_design", "gameplay_verified": False, "github_upload_verified": False, "codex_cloud_published": False}
    Path(str(output) + ".verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))

if __name__ == "__main__":
    main()

