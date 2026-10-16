"""Create a ZIP and verify its complete payload using SHA-256."""
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", "__pycache__", "reports", "releases", "work", "local"}

def payload_files():
    return sorted(
        p for p in ROOT.rglob("*")
        if p.is_file() and not p.is_symlink()
        and not EXCLUDED.intersection(p.relative_to(ROOT).parts)
        and p.name != "MANIFEST.json" and p.suffix != ".pyc"
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(ROOT.parent / "haipam-stellaris-handoff-v0.1.0-20261016.zip"))
    args = parser.parse_args()
    output = Path(args.output).resolve()
    if output.is_relative_to(ROOT):
        raise ValueError("ZIP must be outside the source directory")
    if output.suffix.lower() != ".zip":
        raise ValueError("Output must have .zip suffix")
    output.parent.mkdir(parents=True, exist_ok=True)
    files = payload_files()
    manifest = {
        "package_version": "0.1.0-design-handoff",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "kind": "design_and_development_handoff",
        "gameplay_verified": False,
        "files": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],
    }
    manifest_path = ROOT / "MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts/validate_handoff.py")], check=True)
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
    report = {"ok": True, "archive": output.name, "bytes": output.stat().st_size, "sha256": digest, "zip_entries": len(files), "all_payload_hashes_match": True, "requirements": 32, "scope": "design_handoff_only", "gameplay_verified": False, "github_upload_verified": False, "codex_cloud_published": False}
    Path(str(output) + ".verification.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))

if __name__ == "__main__":
    main()

