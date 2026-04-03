#!/usr/bin/env python3
"""
Scan text for tortured phrases and LLM vocabulary markers.

Usage:
    python scan_phrases.py <input_file>
    cat full_text.txt | python scan_phrases.py -

Output: JSON with categorized findings, counts, and weighted score.
"""

import json
import re
import sys
from collections import Counter

# === TORTURED PHRASES (paper mill indicators) ===
# Any single match = MAJOR flag
TORTURED_PHRASES = {
    "amino corrosive": "amino acid",
    "anaerobic devastation": "anaerobic digestion",
    "artificial intelligence network": "artificial neural network",
    "big number crunching": "big data analytics",
    "boiling acid": "hydrochloric acid",
    "brand name protein": "branded protein",
    "browning focus point": "Brownian focal point",
    "compound hydrogen": "hydrogen compound",
    "counterfeit neural systems": "artificial neural networks",
    "dim going": "dark matter",
    "enormous information": "big data",
    "false neural system": "artificial neural network",
    "fitness demonstrating": "genetic modeling",
    "glucose bigotry": "glucose intolerance",
    "glucose narrow-mindedness": "glucose intolerance",
    "grand neural system": "large neural network",
    "hard silver": "sterling silver",
    "harsh corrosive": "strong acid",
    "huge information preparing": "big data processing",
    "human experience disclosure": "human exposure assessment",
    "inherited recurrence": "genetic recurrence",
    "natural forces": "chemical reactions",
    "profound learning": "deep learning",
    "sham neural system": "artificial neural network",
    "shrewd gadgets": "smart devices",
    "brilliant gadgets": "smart devices",
    "sign of rapidity": "velocity vector",
    "warm water": "hot water (thermal)",
    "writing soft copy": "writing digitally",
    "convolutionary brain system": "convolutional neural network",
    "arbitrary woodland": "random forest",
    "bolster vector machine": "support vector machine",
    "apparatus learning": "machine learning",
    "gadget learning": "machine learning",
}

# === LLM VOCABULARY MARKERS ===
TIER1_PHRASES = [
    r"delves?\s+into",
    r"intricate\s+landscape",
    r"nuanced\s+landscape",
    r"a\s+testament\s+to",
    r"in\s+the\s+realm\s+of",
    r"a\s+myriad\s+of",
    r"rapidly\s+evolving",
    r"ever-evolving\s+landscape",
    r"tapestry\s+of",
    r"indelible\s+mark",
    r"\bnestled\b",
]

TIER2_PHRASES = [
    r"it\s+is\s+worth\s+noting\s+that",
    r"it\s+should\s+be\s+noted\s+that",
    r"comprehensive\s+overview",
    r"plays?\s+a\s+(?:crucial|pivotal)\s+role",
    r"offers?\s+valuable\s+insights?\s+into",
    r"sheds?\s+light\s+on",
    r"paves?\s+the\s+way\s+for",
    r"underscores?\s+the\s+importance\s+of",
    r"\bmeticulous\b",
    r"\bvibrant\b",
    r"\bgroundbreaking\b",
    r"\bprofound\b",
    r"\bshowcasing\b",
    r"\bexemplifies?\b",
    r"\bfostering\b",
    r"commitment\s+to\s+\w+",
    r"boasts?\s+a\b",
]

TIER3_PHRASES = [
    r"^Additionally\b",  # sentence opener
    r"\bFurthermore\b",
    r"\bMoreover\b",
    r"\balign\s+with\b",
    r"\bhighlighting\b",
    r"\bensuring\b",
]

# === CITATION ARTIFACTS (definitive AI markers) ===
CITATION_ARTIFACTS = [
    r"turn\d+search\d+",
    r"contentReference",
    r"oaicite",
    r"oai_citation",
    r"\+1\b",
    r"attached_file",
    r"grok_card",
    r"as\s+of\s+my\s+(?:last\s+)?training\s+data",
    r"my\s+training\s+(?:data|cutoff)",
    r"Let\s+me\s+explain",
]

# === COPULA AVOIDANCE PATTERNS ===
COPULA_AVOIDANCE = [
    r"\bserves?\s+as\b",
    r"\bstands?\s+as\b",
    r"\brepresents?\s+a\b",
    r"\bmarks?\s+a\s+(?:pivotal|significant|crucial)\b",
]

# === PARTICIPLE ATTACHMENT ===
PARTICIPLE_ATTACH = [
    r",\s*highlighting\s+(?:the\s+)?(?:importance|need|significance)",
    r",\s*underscoring\s+(?:the\s+)?(?:importance|need|significance)",
    r",\s*demonstrating\s+(?:its|the|their)",
    r",\s*emphasizing\s+(?:the\s+)?(?:importance|need|significance)",
    r",\s*showcasing\s+(?:the|its|their)",
]


def count_pattern_matches(text: str, patterns: list[str], flags=re.IGNORECASE | re.MULTILINE) -> list[dict]:
    """Find all matches for a list of regex patterns."""
    matches = []
    for pattern in patterns:
        for m in re.finditer(pattern, text, flags):
            # Get surrounding context (50 chars each side)
            start = max(0, m.start() - 50)
            end = min(len(text), m.end() + 50)
            context = text[start:end].replace("\n", " ").strip()
            matches.append({
                "phrase": m.group(),
                "pattern": pattern,
                "position": m.start(),
                "context": f"...{context}...",
            })
    return matches


def scan_tortured(text: str) -> list[dict]:
    """Scan for tortured phrases."""
    findings = []
    text_lower = text.lower()
    for tortured, intended in TORTURED_PHRASES.items():
        positions = [m.start() for m in re.finditer(re.escape(tortured), text_lower)]
        for pos in positions:
            start = max(0, pos - 50)
            end = min(len(text), pos + len(tortured) + 50)
            context = text[start:end].replace("\n", " ").strip()
            findings.append({
                "tortured_phrase": tortured,
                "intended_term": intended,
                "position": pos,
                "context": f"...{context}...",
            })
    return findings


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

    # Run all scans
    tortured = scan_tortured(text)
    tier1 = count_pattern_matches(text, TIER1_PHRASES)
    tier2 = count_pattern_matches(text, TIER2_PHRASES)
    tier3 = count_pattern_matches(text, TIER3_PHRASES)
    artifacts = count_pattern_matches(text, CITATION_ARTIFACTS)
    copula = count_pattern_matches(text, COPULA_AVOIDANCE)
    participle = count_pattern_matches(text, PARTICIPLE_ATTACH)

    # Calculate weighted vocabulary score
    vocab_score = len(tier1) * 2 + len(tier2) * 1 + len(tier3) * 0.5

    # Determine flags
    flags = []
    if tortured:
        flags.append({"type": "MAJOR", "category": "tortured_phrases",
                       "detail": f"{len(tortured)} tortured phrase(s) found — paper mill indicator"})
    if artifacts:
        flags.append({"type": "MAJOR", "category": "citation_artifacts",
                       "detail": f"{len(artifacts)} AI tool artifact(s) — definitive LLM marker"})
    if vocab_score >= 9:
        flags.append({"type": "MAJOR", "category": "llm_vocabulary",
                       "detail": f"Weighted vocabulary score {vocab_score} (threshold: 9)"})
    elif vocab_score >= 4:
        flags.append({"type": "MINOR", "category": "llm_vocabulary",
                       "detail": f"Weighted vocabulary score {vocab_score} (threshold: 4)"})
    if len(copula) >= 5:
        flags.append({"type": "MINOR", "category": "copula_avoidance",
                       "detail": f"{len(copula)} copula avoidance instances"})
    if len(participle) >= 4:
        flags.append({"type": "MINOR", "category": "participle_attachment",
                       "detail": f"{len(participle)} participle attachment patterns"})

    output = {
        "tortured_phrases": {"count": len(tortured), "findings": tortured},
        "llm_markers": {
            "tier1": {"count": len(tier1), "weight": 2, "findings": tier1},
            "tier2": {"count": len(tier2), "weight": 1, "findings": tier2},
            "tier3": {"count": len(tier3), "weight": 0.5, "findings": tier3},
            "weighted_score": vocab_score,
        },
        "citation_artifacts": {"count": len(artifacts), "findings": artifacts},
        "copula_avoidance": {"count": len(copula), "findings": copula},
        "participle_attachment": {"count": len(participle), "findings": participle},
        "flags": flags,
        "flag_summary": {
            "major": sum(1 for f in flags if f["type"] == "MAJOR"),
            "minor": sum(1 for f in flags if f["type"] == "MINOR"),
        },
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
