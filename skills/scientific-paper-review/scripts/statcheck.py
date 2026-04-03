#!/usr/bin/env python3
"""
Statcheck: Recalculate p-values from reported test statistics.

Usage:
    python statcheck.py <input_file>
    echo "t(34) = 2.10, p = .02" | python statcheck.py -

Input: Text file or stdin containing statistical results.
       Extracts APA-formatted statistics automatically.

Output: JSON array of results with PASS/FLAG/FAIL per statistic.
"""

import json
import os
import re
import sys
from math import sqrt

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    from scipy import stats as sp_stats
except ImportError:
    print(json.dumps({"error": "scipy not installed. Run: pip install scipy"}))
    sys.exit(1)


# Regex patterns for APA-formatted statistics
PATTERNS = {
    "t": re.compile(
        r"t\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*(-?\d+(?:\.\d+)?)\s*,\s*p\s*([<>=≤≥])\s*\.?(\d+(?:\.\d+)?)",
        re.IGNORECASE,
    ),
    "F": re.compile(
        r"F\s*\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*(-?\d+(?:\.\d+)?)\s*,\s*p\s*([<>=≤≥])\s*\.?(\d+(?:\.\d+)?)",
        re.IGNORECASE,
    ),
    "chi2": re.compile(
        r"[χΧχ²X]\s*[²2]?\s*\(\s*(\d+(?:\.\d+)?)\s*(?:,\s*[Nn]\s*=\s*\d+)?\s*\)\s*=\s*(-?\d+(?:\.\d+)?)\s*,\s*p\s*([<>=≤≥])\s*\.?(\d+(?:\.\d+)?)",
        re.IGNORECASE,
    ),
    "r": re.compile(
        r"r\s*\(\s*(\d+(?:\.\d+)?)\s*\)\s*=\s*(-?\d+(?:\.\d+)?)\s*,\s*p\s*([<>=≤≥])\s*\.?(\d+(?:\.\d+)?)",
        re.IGNORECASE,
    ),
    "Z": re.compile(
        r"[Zz]\s*=\s*(-?\d+(?:\.\d+)?)\s*,\s*p\s*([<>=≤≥])\s*\.?(\d+(?:\.\d+)?)",
        re.IGNORECASE,
    ),
}


def parse_p_value(comparator: str, p_str: str) -> tuple[float, bool]:
    """Parse reported p-value. Returns (value, is_exact).

    Handles the common APA convention where p-values omit the leading zero:
    "p = .02" is captured as p_str="02" (the regex's optional \\. eats the dot),
    so we need to reconstruct 0.02 from the raw "02".
    But "p = 1.0" should stay as 1.0 — a legitimate (if rare) p-value.
    """
    p = float(p_str)
    # Only apply the leading-zero correction when the raw string has no dot,
    # meaning the regex consumed a standalone ".02" as "02".  A real "1.0"
    # keeps its dot and won't enter this branch.
    if p >= 1 and "." not in p_str:
        p = p / (10 ** len(p_str))
    is_exact = comparator in ("=", )
    return p, is_exact


def recalculate_p(test_type: str, groups: tuple) -> dict:
    """Recalculate p-value and compare with reported."""
    result = {"test_type": test_type, "raw_match": "".join(str(g) for g in groups)}

    try:
        if test_type == "t":
            df = float(groups[0])
            t_val = abs(float(groups[1]))
            p_reported, is_exact = parse_p_value(groups[2], groups[3])
            p_calc = sp_stats.t.sf(t_val, df) * 2  # two-tailed
            result.update({"df": df, "statistic": t_val, "p_reported": p_reported,
                           "p_calculated": round(p_calc, 6)})

        elif test_type == "F":
            df1, df2 = float(groups[0]), float(groups[1])
            f_val = float(groups[2])
            p_reported, is_exact = parse_p_value(groups[3], groups[4])
            if f_val < 0:
                result.update({"status": "FAIL", "reason": "F-statistic cannot be negative",
                               "p_reported": p_reported, "statistic": f_val})
                return result
            p_calc = sp_stats.f.sf(f_val, df1, df2)
            result.update({"df1": df1, "df2": df2, "statistic": f_val,
                           "p_reported": p_reported, "p_calculated": round(p_calc, 6)})

        elif test_type == "chi2":
            df = float(groups[0])
            chi2_val = float(groups[1])
            p_reported, is_exact = parse_p_value(groups[2], groups[3])
            if chi2_val < 0:
                result.update({"status": "FAIL", "reason": "Chi-square cannot be negative",
                               "p_reported": p_reported, "statistic": chi2_val})
                return result
            p_calc = sp_stats.chi2.sf(chi2_val, df)
            result.update({"df": df, "statistic": chi2_val, "p_reported": p_reported,
                           "p_calculated": round(p_calc, 6)})

        elif test_type == "r":
            df = float(groups[0])
            r_val = float(groups[1])
            p_reported, is_exact = parse_p_value(groups[2], groups[3])
            if abs(r_val) > 1:
                result.update({"status": "FAIL", "reason": "Correlation outside [-1, 1]",
                               "p_reported": p_reported, "statistic": r_val})
                return result
            # Convert r to t
            t_val = abs(r_val) * sqrt(df / (1 - r_val ** 2)) if abs(r_val) < 1 else float("inf")
            p_calc = sp_stats.t.sf(t_val, df) * 2  # two-tailed
            result.update({"df": df, "statistic": r_val, "p_reported": p_reported,
                           "p_calculated": round(p_calc, 6)})

        elif test_type == "Z":
            z_val = abs(float(groups[0]))
            p_reported, is_exact = parse_p_value(groups[1], groups[2])
            p_calc = sp_stats.norm.sf(z_val) * 2  # two-tailed
            result.update({"statistic": z_val, "p_reported": p_reported,
                           "p_calculated": round(p_calc, 6)})

        # Determine status
        p_reported = result["p_reported"]
        p_calc = result["p_calculated"]

        # Account for rounding: check if rounding the test statistic could explain the difference
        diff = abs(p_reported - p_calc)
        crosses_05 = (p_reported < 0.05) != (p_calc < 0.05)

        if diff < 0.005:
            result["status"] = "PASS"
            result["reason"] = "P-values match within rounding tolerance"
        elif crosses_05:
            result["status"] = "FAIL"
            result["reason"] = f"GROSS INCONSISTENCY: reported p={'<' if p_reported < 0.05 else '>'}.05 but calculated p={'<' if p_calc < 0.05 else '>'}.05"
        else:
            result["status"] = "FLAG"
            result["reason"] = f"P-values differ (Δ={diff:.4f}) but both on same side of .05"

    except (ValueError, ZeroDivisionError, OverflowError) as e:
        result["status"] = "ERROR"
        result["reason"] = str(e)

    return result


def extract_and_check(text: str) -> dict:
    """Extract all statistics from text and check each one."""
    results = []
    p_values = []

    for test_type, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            check = recalculate_p(test_type, match.groups())
            check["location"] = f"char {match.start()}-{match.end()}"
            check["original_text"] = match.group()
            results.append(check)
            if "p_reported" in check:
                p_values.append(check["p_reported"])

    # P-value clustering analysis
    bins = {
        ".001-.01": 0, ".01-.03": 0, ".03-.04": 0,
        ".04-.049": 0, ".05-.10": 0, ">.10": 0
    }
    for p in p_values:
        if p <= 0.01:
            bins[".001-.01"] += 1
        elif p <= 0.03:
            bins[".01-.03"] += 1
        elif p <= 0.04:
            bins[".03-.04"] += 1
        elif p < 0.05:
            bins[".04-.049"] += 1
        elif p <= 0.10:
            bins[".05-.10"] += 1
        else:
            bins[">.10"] += 1

    significant = sum(v for k, v in bins.items() if k in [".001-.01", ".01-.03", ".03-.04", ".04-.049"])
    p_hack_flag = False
    if significant > 0 and bins[".04-.049"] / significant > 0.3:
        p_hack_flag = True

    summary = {
        "statistics_found": len(results),
        "pass": sum(1 for r in results if r.get("status") == "PASS"),
        "flag": sum(1 for r in results if r.get("status") == "FLAG"),
        "fail": sum(1 for r in results if r.get("status") == "FAIL"),
        "error": sum(1 for r in results if r.get("status") == "ERROR"),
        "p_value_distribution": bins,
        "p_hacking_suspicion": p_hack_flag,
        "results": results,
    }

    return summary


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input_file>  (use - for stdin)")
        sys.exit(1)

    source = sys.argv[1]
    if source == "-":
        text = sys.stdin.read()
    else:
        with open(source, encoding="utf-8") as f:
            text = f.read()

    output = extract_and_check(text)
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
