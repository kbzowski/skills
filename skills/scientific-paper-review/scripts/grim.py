#!/usr/bin/env python3
"""
GRIM & GRIMMER tests: Check if reported means and SDs are mathematically
possible given sample size and integer-valued data.

Usage:
    python grim.py <input_json>
    echo '[{"mean": 3.47, "n": 10, "decimals": 2}]' | python grim.py -

Input: JSON array of objects with fields:
    - mean (float): reported mean
    - n (int): sample size
    - decimals (int): number of decimal places reported
    - sd (float, optional): reported standard deviation (for GRIMMER)
    - scale_min (int, optional): minimum scale value (default 1)
    - scale_max (int, optional): maximum scale value (default: no upper bound check)
    - label (str, optional): identifier for this statistic

Output: JSON array of results with CONSISTENT/INCONSISTENT per item.
"""

import json
import sys
from math import floor, ceil, isclose

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def grim_test(mean: float, n: int, decimals: int,
              scale_min: int = None, scale_max: int = None) -> dict:
    """
    GRIM test: multiply mean by n. For integer data, the result must be
    an integer within rounding tolerance.
    """
    result = {"test": "GRIM", "mean": mean, "n": n, "decimals": decimals}

    # Range check
    if scale_min is not None and mean < scale_min:
        result["status"] = "FAIL"
        result["reason"] = f"Mean {mean} below scale minimum {scale_min}"
        return result
    if scale_max is not None and mean > scale_max:
        result["status"] = "FAIL"
        result["reason"] = f"Mean {mean} above scale maximum {scale_max}"
        return result

    # GRIM granularity check
    product = mean * n
    tolerance = 0.5 * (10 ** (-decimals)) * n

    # Check if product is close to an integer
    nearest_int = round(product)
    deviation = abs(product - nearest_int)

    if deviation <= tolerance + 1e-10:
        result["status"] = "PASS"
        result["reason"] = f"Mean × N = {product:.4f}, nearest integer = {nearest_int}, within tolerance {tolerance:.4f}"
    else:
        result["status"] = "FAIL"
        result["reason"] = f"Mean × N = {product:.4f}, nearest integer = {nearest_int}, deviation {deviation:.4f} exceeds tolerance {tolerance:.4f}"

        # Find nearest possible means
        lower = floor(product) / n
        upper = ceil(product) / n
        result["nearest_possible_means"] = [round(lower, decimals), round(upper, decimals)]

    # Check GRIM applicability
    max_n = 10 ** decimals
    if n > max_n:
        result["warning"] = f"N={n} exceeds GRIM sensitivity for {decimals} decimal places (max useful N={max_n})"

    return result


def grimmer_test(mean: float, sd: float, n: int, decimals: int) -> dict:
    """
    GRIMMER test: check if reported SD is consistent with reported mean and N
    for integer data. Variance × (N-1) must be an integer.
    """
    result = {"test": "GRIMMER", "mean": mean, "sd": sd, "n": n, "decimals": decimals}

    if n <= 1:
        result["status"] = "SKIP"
        result["reason"] = "N <= 1, cannot compute variance"
        return result

    variance = sd ** 2
    # For integer data: sum of squared deviations must be an integer
    # variance * (n-1) = sum of (xi - mean)^2 ... but we need sum of xi^2 - n*mean^2
    # Actually: variance * (n-1) should be achievable given integer constraints

    sum_sq_dev = variance * (n - 1)
    tolerance = 0.5 * (10 ** (-decimals * 2)) * (n - 1) * 2  # wider tolerance for squared terms

    nearest_int = round(sum_sq_dev)
    deviation = abs(sum_sq_dev - nearest_int)

    if deviation <= tolerance + 1e-8:
        result["status"] = "PASS"
        result["reason"] = f"Var × (N-1) = {sum_sq_dev:.4f}, consistent with integer data"
    else:
        result["status"] = "FLAG"
        result["reason"] = f"Var × (N-1) = {sum_sq_dev:.4f}, deviation {deviation:.4f} from nearest integer {nearest_int}"

    return result


def process_items(items: list) -> dict:
    """Process a list of statistics to check."""
    results = []

    for item in items:
        mean = item.get("mean")
        n = item.get("n")
        decimals = item.get("decimals", 2)
        sd = item.get("sd")
        label = item.get("label", f"mean={mean}, n={n}")
        scale_min = item.get("scale_min")
        scale_max = item.get("scale_max")

        if mean is None or n is None:
            results.append({"label": label, "status": "ERROR", "reason": "Missing mean or n"})
            continue

        # GRIM test
        grim_result = grim_test(mean, n, decimals, scale_min, scale_max)
        grim_result["label"] = label
        results.append(grim_result)

        # GRIMMER test (if SD provided)
        if sd is not None:
            grimmer_result = grimmer_test(mean, sd, n, decimals)
            grimmer_result["label"] = label
            results.append(grimmer_result)

    summary = {
        "items_checked": len(items),
        "grim_pass": sum(1 for r in results if r.get("test") == "GRIM" and r.get("status") == "PASS"),
        "grim_fail": sum(1 for r in results if r.get("test") == "GRIM" and r.get("status") == "FAIL"),
        "grimmer_pass": sum(1 for r in results if r.get("test") == "GRIMMER" and r.get("status") == "PASS"),
        "grimmer_flag": sum(1 for r in results if r.get("test") == "GRIMMER" and r.get("status") == "FLAG"),
        "results": results,
    }

    return summary


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input_json>  (use - for stdin)")
        sys.exit(1)

    source = sys.argv[1]
    if source == "-":
        data = json.loads(sys.stdin.read())
    else:
        with open(source, encoding="utf-8") as f:
            data = json.load(f)

    if not isinstance(data, list):
        data = [data]

    output = process_items(data)
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
