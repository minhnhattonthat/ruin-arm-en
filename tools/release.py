"""release.py: build, gate and package the English patch. Stops at the first failure:
polish list ticked -> build -> check (tests + lint) -> smoke -> JP left (jp_reach.py) -> visual-QA gate -> debug tool off -> BPS patch
(re-applied to a clean original and compared) -> release/<version>/ zip of patch + README.txt.

    python -X utf8 tools/release.py --version 1.0 [--force]

The QA tour is not re-run here (`tools/debug/warp.py`, docs/status.md); callers must capture changed scenes on
the current build. The gate rejects sheets changed since their verdict. Never publishes.
"""
import argparse
import hashlib
import shutil
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build import OUT as BUILT, ROM  # noqa: E402
from skill import SCRIPTS  # noqa: E402

PY = [sys.executable, "-X", "utf8"]
NAME = "Ruin_Arm_EN"


def step(title, cmd):
    print(f"== {title}", flush=True)
    if subprocess.run(PY + [str(c) for c in cmd], cwd=ROOT).returncode:
        sys.exit(f"release stopped: {title} failed")


def hashes(b):
    return {"crc": f"{zlib.crc32(b):08X}", "md5": hashlib.md5(b).hexdigest(), "sha1": hashlib.sha1(b).hexdigest(),
            "size": f"{len(b):,}"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--version", required=True)
    ap.add_argument("--force", action="store_true", help="overwrite this version's files")
    a = ap.parse_args()
    out = ROOT / "release" / a.version
    if out.exists() and not a.force:
        sys.exit(f"{out} exists (--force to overwrite)")
    scripts = Path(SCRIPTS)
    open_items = [line for line in (ROOT / "docs" / "polish.md").read_text(encoding="utf-8").splitlines()
                  if line.startswith("- [ ]")]
    if open_items:
        sys.exit("release stopped: docs/polish.md has unticked items:\n" + "\n".join(open_items))
    step("build", [ROOT / "tools" / "build.py"])
    step("check", [ROOT / "tools" / "check.py"])
    step("smoke", [scripts / "emu.py", BUILT, "--out", ROOT / "work" / "qa" / "smoke", "--route",
                   ROOT / "tools" / "routes" / "boot.txt", "--smoke"])
    step("JP left", [ROOT / "tools" / "jp_reach.py", BUILT, "--known", ROOT / "script" / "keep_jp.txt"])
    qa = ROOT / "work" / "qa"
    for label, manifest, verdicts in (
        ("gameplay", "manifest.tsv", "verdicts"),
        ("ending", "ending-manifest.tsv", "ending-verdicts"),
        ("static graphics", "graphics-manifest.tsv", "graphics-verdicts"),
        ("map graphics", "graphics-maps-manifest.tsv", "graphics-maps-verdicts"),
        ("graphics fixes", "graphics-fixes-manifest.tsv", "graphics-fixes-verdicts"),
        ("story", "story/manifest.tsv", "story/verdicts"),
    ):
        step(f"{label} QA gate", [scripts / "qa_gate.py", "check", qa / manifest, qa / verdicts])
    # debug tool off: it is Lua run by the emulator (tools/debug/), so the ROM carries none of it; the build's own
    # writes are checked against the allowed ranges by tests/ (romdiff), which `check` just ran
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    patch = out / f"{NAME}_v{a.version}.bps"
    step("patch", [ROOT / "tools" / "bps.py", "make", ROM, BUILT, patch])
    orig, built = ROM.read_bytes(), BUILT.read_bytes()
    applied = out / "applied.sfc"
    step("re-apply", [ROOT / "tools" / "bps.py", "apply", ROM, patch, applied])
    if applied.read_bytes() != built:
        sys.exit("release stopped: the patch applied to a clean original differs from the build")
    applied.unlink()
    o, p = hashes(orig), hashes(built)
    readme = (ROOT / "docs" / "release-readme.txt").read_text(encoding="utf-8").format(
        version=a.version, patch=patch.name, o=o, p=p)
    (out / "README.txt").write_text(readme, encoding="utf-8", newline="\r\n")
    zp = out / f"{NAME}_v{a.version}.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(patch, patch.name)
        z.write(out / "README.txt", "README.txt")
    print(f"release ok: {zp} (patched SHA-1 {p['sha1']}, patch SHA-1 "
          f"{hashlib.sha1(patch.read_bytes()).hexdigest()}); not published")


if __name__ == "__main__":
    main()
