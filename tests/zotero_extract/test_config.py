import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from scripts.zotero_extract.config import CODETAG_TO_SECTION, FALLBACK_SECTION


def test_all_fish_sections_reachable():
    sections = set(CODETAG_TO_SECTION.values())
    expected = {
        "** Background and motivation",
        "** Supporting Ideas and hypothesis",
        "** Purpose, Relevance, and Contribution",
        "** Methodology",
        "** Results",
        "** Interesting findings and not categorized stuff",
        "** Critics",
    }
    assert expected.issubset(sections)


def test_codetags_are_lowercase():
    for key in CODETAG_TO_SECTION:
        assert key == key.lower(), f"Key '{key}' must be lowercase"


def test_fallback_is_findings():
    assert FALLBACK_SECTION == "** Interesting findings and not categorized stuff"
