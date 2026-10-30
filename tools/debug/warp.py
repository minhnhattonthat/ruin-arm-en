"""warp.py: reach scenes from tools/debug/scenes.lua in the emulator from a cold boot (docs/re/debug.md).

    python -X utf8 tools/debug/warp.py menu_items [more scenes..] [--rom build/ruinarm_en.sfc] [--save]
    python -X utf8 tools/debug/warp.py --all [--jobs 4]   # every scene + the map tour; states -> work/states/
    python -X utf8 tools/debug/warp.py maps                # tour: one cold boot, a shot of every map
    python -X utf8 tools/debug/warp.py msgs_10             # tour: every message of script/msg10.json, a shot per page
    python -X utf8 tools/debug/warp.py --list

Each scene writes work/qa/warp/<scene>/scene.png (the tour: map_AARR.png each) and, with --save or --all,
work/states/<scene>.mss. Exit 1 if any scene did not report READY.
"""
import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SCRIPTS  # noqa: E402

DEBUG = ROOT / "tools" / "debug"
ROM = ROOT / "rom" / "Ruin Arm (Japan).sfc"


def scene_names():
    text = (DEBUG / "scenes.lua").read_text(encoding="utf-8")
    body = text[text.index("SCENES = {"):]
    return re.findall(r"^  ([a-z0-9_]+)\s*=\s*\{", body, re.M)


def run(scene, rom, out_root, save):
    out = out_root / scene
    tour = scene == "maps" or scene.startswith("msgs_")
    cmd = [sys.executable, "-X", "utf8", str(Path(SCRIPTS) / "emu.py"), str(rom), "--out", str(out),
           "--script", str(DEBUG / "scenes.lua")]
    if scene.startswith("msgs_"):
        strings = json.loads((ROOT / "script" / f"msg{scene[5:]}.json").read_text(encoding="utf-8"))
        ids = [int(s["id"], 16) for s in strings if re.fullmatch(r"[0-9A-F]{4}", s["id"])]  # orphans have no id
        out.mkdir(parents=True, exist_ok=True)
        (out / "msgs.lua").write_text("MSGS = {" + ",".join(f"0x{i:04X}" for i in ids) + "}\n", encoding="utf-8")
        cmd += ["--script", str(out / "msgs.lua")]
    cmd += ["--script", str(DEBUG / "warp.lua"), "--var", f"SCENE='{scene}'",
            "--frames", "300000" if tour else "20000", "--timeout", "3000" if tour else "300"]
    if save and not tour:
        cmd += ["--var", f"SAVE=[[{(ROOT / 'work' / 'states' / (scene + '.mss')).as_posix()}]]"]
    subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    ok = "READY" in log
    stuck = [l for l in log.splitlines() if l.startswith("STUCK")]
    if tour and ok:  # 16 full-size shots a sheet for the visual-QA gate; sheet.txt names each sheet's tiles
        res = subprocess.run([sys.executable, "-X", "utf8", str(Path(SCRIPTS) / "sheet.py"),
                              str(out / ("map_*.png" if scene == "maps" else "m_*.png")),
                              "--div", "1", "--cols", "4", "--max", "16", "--out", str(out / "sheet.png")],
                             capture_output=True, text=True, encoding="utf-8")
        (out / "sheet.txt").write_text(res.stdout, encoding="utf-8")
    print(f"{'ok  ' if ok else 'FAIL'} {scene:16} {out.relative_to(ROOT).as_posix()}" + (f"  {len(stuck)} stuck" if stuck else ""))
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenes", nargs="*")
    ap.add_argument("--rom", type=Path, default=ROM)
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "qa" / "warp")
    ap.add_argument("--all", action="store_true", help="every scene in scenes.lua plus the map tour, saving states")
    ap.add_argument("--save", action="store_true", help="save work/states/<scene>.mss at each scene")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    a.out = a.out.resolve()
    names = scene_names()
    if a.list:
        print("\n".join(names + ["maps", "map_AARR (any map id)", "exit_N (any exit index)"]))
        return 0
    scenes = names + ["maps"] if a.all else a.scenes
    if not scenes:
        ap.error("name a scene, or --all / --list")
    with ThreadPoolExecutor(a.jobs) as ex:
        oks = list(ex.map(lambda s: run(s, a.rom, a.out, a.save or a.all), scenes))
    if len(scenes) > 1:
        shots = [str(a.out / s / "scene.png") for s, ok in zip(scenes, oks) if ok and (a.out / s / "scene.png").exists()]
        if shots:
            subprocess.run([sys.executable, str(Path(SCRIPTS) / "sheet.py"), *shots, "--out", str(a.out / "scenes.png")])
    return 0 if all(oks) else 1


if __name__ == "__main__":
    sys.exit(main())
