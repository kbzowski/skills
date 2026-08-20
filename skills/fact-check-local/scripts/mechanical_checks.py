r"""Mechanical verification tests for a document vs its claim registry.

Usage: python mechanical_checks.py [checks_config.json]
Copy this script + a project-specific checks_config.json into the project.
Run after EVERY edit of the document. Exit code 1 on any FAIL.

Config keys (all optional except "report"):
{
  "report": "RAPORT.md",
  "arithmetic": [{"desc": "3 x 280 = 840", "check": "3*280 == 840"}],
  "crossref": {"100 kHz (force fs)": {"pattern": "100\\s?kHz", "min_count": 3}},
  "bibliography": [{"desc": "49 numbered entries", "pattern": "^\\d+\\.\\s+\\*\\*",
                    "section_after": "## 8. ", "expected_count": 49}],
  "negative_grep": [{"desc": "industrial protocols only in Kollment",
                     "terms": ["IO-Link", "EtherCAT", "Modbus"],
                     "corpus_globs": ["literature_md/**/*.md", "books/*.txt"],
                     "allowed_files": ["Kollment_2018.md"]}],
  "completeness": {"registry": "REJESTR_TWIERDZEN.md",
                   "unit_regex": "(?:kHz|MHz|Hz|µs|nm|MPa|°C|kN|%)",
                   "citation_regex": "[A-Z][a-ząćęłńóśźż]+ \\(?(?:19|20)\\d{2}"}
}
"""
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(".")
_cfg = Path(sys.argv[1] if len(sys.argv) > 1 else "checks_config.json")
if not _cfg.exists():
    sys.exit(f"config not found: {_cfg} — see the module docstring for its shape")
CONFIG = json.loads(_cfg.read_text(encoding="utf-8"))
_report = ROOT / CONFIG["report"]
if not _report.exists():
    sys.exit(f"report not found: {_report} (config key \"report\")")
REPORT = _report.read_text(encoding="utf-8")
FAILURES = []


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def approx(a, b, tol=0.01):
    return abs(a - b) <= tol * max(abs(a), abs(b))


def test_arithmetic():
    print("\n== T2: arithmetic recomputation ==")
    env = {"approx": approx, "abs": abs, "round": round, "math": math}
    for item in CONFIG.get("arithmetic", []):
        try:
            ok = bool(eval(item["check"], {"__builtins__": {}}, env))
        except Exception as e:
            ok = False
            item = {**item, "desc": item["desc"] + f" (eval error: {e})"}
        check(item["desc"], ok)


def test_crossref():
    print("\n== T3: cross-references of key values ==")
    for name, spec in CONFIG.get("crossref", {}).items():
        n = len(re.findall(spec["pattern"], REPORT))
        check(f"{name}: {n} occurrences (expected >= {spec['min_count']})", n >= spec["min_count"])


def test_bibliography():
    print("\n== T5: bibliography counts ==")
    for item in CONFIG.get("bibliography", []):
        text = REPORT.split(item["section_after"], 1)[1] if item.get("section_after") and item["section_after"] in REPORT else REPORT
        n = len(re.findall(item["pattern"], text, re.M))
        check(item["desc"], n == item["expected_count"], f"found {n}")


def test_negative_grep():
    print("\n== T4: corpus grep for negative claims ==")
    for item in CONFIG.get("negative_grep", []):
        hits = {}
        for g in item["corpus_globs"]:
            for f in ROOT.glob(g):
                text = f.read_text(encoding="utf-8", errors="ignore")
                for w in item["terms"]:
                    if re.search(re.escape(w), text, re.I):
                        hits.setdefault(f.name, set()).add(w)
        allowed = set(item.get("allowed_files", []))
        unexpected = {f: sorted(ws) for f, ws in hits.items() if f not in allowed}
        check(item["desc"], not unexpected, f"unexpected hits: {unexpected}" if unexpected else f"hits: { {f: sorted(w) for f, w in hits.items()} }")


def test_completeness():
    print("\n== extraction completeness (report tokens vs registry) ==")
    spec = CONFIG.get("completeness")
    if not spec:
        return
    rej_path = ROOT / spec["registry"]
    if not rej_path.exists():
        print(f"[SKIP] {spec['registry']} not found")
        return
    rej = re.sub(r"\s+", " ", rej_path.read_text(encoding="utf-8"))

    def sweep(label, pattern):
        tokens = {t.strip() for t in re.findall(pattern, REPORT) if len(t.strip()) > 2}
        missing = sorted(t for t in tokens if re.sub(r"\s+", " ", t) not in rej)
        check(f"{label} coverage: {len(tokens) - len(missing)}/{len(tokens)}",
              not missing, f"missing from registry: {missing[:20]}" if missing else "")

    sweep("numeric token", r"\d[\d\s,.–-]*\s?" + spec["unit_regex"])
    if spec.get("citation_regex"):
        sweep("citation", spec["citation_regex"])


if __name__ == "__main__":
    print(f"Report: {CONFIG['report']}")
    test_arithmetic()
    test_crossref()
    test_bibliography()
    test_negative_grep()
    test_completeness()
    print(f"\n{'=' * 40}\nRESULT: {'OK' if not FAILURES else f'{len(FAILURES)} FAIL'}")
    for f in FAILURES:
        print(f"  FAIL: {f}")
    sys.exit(1 if FAILURES else 0)
