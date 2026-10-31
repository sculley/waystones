"""Validate and package Waystones into dist/.

Usage:  python tools/build.py [version]

Produces dist/Waystones-<version>.mcaddon plus one .mcpack per pack.
If a version is given (e.g. "1.2.0" or "v1.2.0"), it is stamped into both
manifests in the packaged copy; the files in the repo are left untouched.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACKS = ["Waystones_BP", "Waystones_RP"]
DIST = os.path.join(ROOT, "dist")


def fail(msg):
    sys.exit(f"build failed: {msg}")


def validate():
    for pack in PACKS:
        for dirpath, _, files in os.walk(os.path.join(ROOT, pack)):
            for name in files:
                path = os.path.join(dirpath, name)
                if name.endswith(".json"):
                    try:
                        json.load(open(path, encoding="utf-8"))
                    except ValueError as e:
                        fail(f"{os.path.relpath(path, ROOT)}: {e}")
                elif name.endswith(".js") and shutil.which("node"):
                    with tempfile.TemporaryDirectory() as tmp:
                        copy = os.path.join(tmp, name[:-3] + ".mjs")
                        shutil.copy(path, copy)
                        result = subprocess.run(["node", "--check", copy], capture_output=True, text=True)
                        if result.returncode:
                            fail(f"{os.path.relpath(path, ROOT)}:\n{result.stderr}")
    print("validated JSON and scripts")


def manifest_version():
    m = json.load(open(os.path.join(ROOT, PACKS[0], "manifest.json")))
    return ".".join(map(str, m["header"]["version"]))


def stamp(folder, version, pack_uuids):
    triple = [int(x) for x in version.split(".")]
    path = os.path.join(folder, "manifest.json")
    m = json.load(open(path))
    m["header"]["version"] = triple
    for module in m["modules"]:
        module["version"] = triple
    for dep in m.get("dependencies", []):
        if dep.get("uuid") in pack_uuids:
            dep["version"] = triple
    json.dump(m, open(path, "w"), indent=2)


def zip_dir(src, dest, prefix=""):
    with zipfile.ZipFile(dest, "a" if os.path.exists(dest) else "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, files in os.walk(src):
            for name in sorted(files):
                full = os.path.join(dirpath, name)
                z.write(full, os.path.join(prefix, os.path.relpath(full, src)))


def main():
    version = (sys.argv[1] if len(sys.argv) > 1 else manifest_version()).lstrip("v")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(f"version must look like 1.2.3, got {version!r}")
    validate()

    shutil.rmtree(DIST, ignore_errors=True)
    os.makedirs(DIST)
    pack_uuids = {json.load(open(os.path.join(ROOT, p, "manifest.json")))["header"]["uuid"] for p in PACKS}
    addon = os.path.join(DIST, f"Waystones-{version}.mcaddon")
    with tempfile.TemporaryDirectory() as tmp:
        for pack in PACKS:
            staged = os.path.join(tmp, pack)
            shutil.copytree(os.path.join(ROOT, pack), staged)
            stamp(staged, version, pack_uuids)
            zip_dir(staged, os.path.join(DIST, f"{pack}-{version}.mcpack"))
            zip_dir(staged, addon, prefix=pack)
    for name in sorted(os.listdir(DIST)):
        print(f"built dist/{name}")


if __name__ == "__main__":
    main()
