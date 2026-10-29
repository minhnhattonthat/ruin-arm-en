"""Phase 6: batch tool and the text lint (every English string in script/ passes the batch checks)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def test_batches_selftest():
    import batches
    batches.selftest()


def test_script_english_lint():
    import batches
    script, gl = batches.load_script(), batches.glossary()
    errs = [f"{e['id']}: {m}" for name, es in script.items() for e in es if e["en"]
            for m in batches.entry_errors(name, e, e["en"], gl)]
    assert not errs, "\n".join(errs[:40])
