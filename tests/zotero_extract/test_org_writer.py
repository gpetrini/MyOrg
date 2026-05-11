import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from scripts.zotero_extract.org_writer import (
    parse_codetag, route_comment,
    find_org_file, already_inserted,
    insert_annotations,
)
from scripts.zotero_extract.config import FALLBACK_SECTION


# --- codetag parsing ---

def test_parse_codetag_curly_braces():
    assert parse_codetag("{BACKGROUND} some text") == "background"


def test_parse_codetag_square_brackets():
    assert parse_codetag("[RESULTS]") == "results"


def test_parse_codetag_title_case():
    assert parse_codetag("{Method}") == "method"


def test_parse_codetag_multi_word():
    assert parse_codetag("[Supporting Ideas] text") == "supporting ideas"


def test_parse_codetag_returns_none_when_absent():
    assert parse_codetag("plain text no tag") is None


def test_route_comment_known_tag():
    assert route_comment("{METHOD} details") == "** Methodology"


def test_route_comment_unknown_tag_falls_back():
    assert route_comment("{UNKNOWN_TAG}") == FALLBACK_SECTION


def test_route_comment_no_tag_falls_back():
    assert route_comment("no tag here") == FALLBACK_SECTION


# --- file search and idempotency ---

def test_find_org_file_by_reference(tmp_path):
    org = tmp_path / "paper.org"
    org.write_text("#+title: Test\n#+reference: minsky_1977\n\nContent\n")
    assert find_org_file("minsky_1977", tmp_path) == org


def test_find_org_file_raises_when_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        find_org_file("nonexistent_key", tmp_path)


def test_already_inserted_true():
    assert already_inserted("Some text [zotero:K3XP9D]\nMore", "K3XP9D") is True


def test_already_inserted_false():
    assert already_inserted("Some text\nMore", "K3XP9D") is False


# --- section insertion ---

ORG_CONTENT = """\
* FISH-5SS

** Background and motivation

** Methodology

** Results

** Interesting findings and not categorized stuff

** Critics

* Annotations (zotero)

* Additional Backlinks
"""


def test_insert_comment_into_correct_section(tmp_path):
    f = tmp_path / "paper.org"
    f.write_text(ORG_CONTENT)
    annotations = [
        {"key": "AA1", "annotationComment": "{BACKGROUND} Keynes context",
         "annotationText": "", "annotationPageLabel": "1"}
    ]
    insert_annotations(f, annotations)
    content = f.read_text()
    assert "- Keynes context [zotero:AA1]" in content
    assert content.index("** Background and motivation") < content.index("- Keynes context [zotero:AA1]")


def test_insert_highlight_into_annotations_section(tmp_path):
    f = tmp_path / "paper.org"
    f.write_text(ORG_CONTENT)
    annotations = [
        {"key": "BB2", "annotationComment": "",
         "annotationText": "Financial instability is endogenous.", "annotationPageLabel": "5"}
    ]
    insert_annotations(f, annotations)
    content = f.read_text()
    assert "- [p. 5] Financial instability is endogenous. [zotero:BB2]" in content
    assert content.index("* Annotations (zotero)") < content.index("- [p. 5]")


def test_annotation_with_both_comment_and_text(tmp_path):
    f = tmp_path / "paper.org"
    f.write_text(ORG_CONTENT)
    annotations = [
        {"key": "CC3", "annotationComment": "{RESULTS} Key finding",
         "annotationText": "Stability is cyclical.", "annotationPageLabel": "8"}
    ]
    insert_annotations(f, annotations)
    content = f.read_text()
    assert "- Key finding [zotero:CC3]" in content
    assert "- [p. 8] Stability is cyclical. [zotero:CC3]" in content


def test_idempotency(tmp_path):
    f = tmp_path / "paper.org"
    f.write_text(ORG_CONTENT)
    annotations = [
        {"key": "DD4", "annotationComment": "{RESULTS} Key result",
         "annotationText": "", "annotationPageLabel": "7"}
    ]
    insert_annotations(f, annotations)
    insert_annotations(f, annotations)
    assert f.read_text().count("[zotero:DD4]") == 1


def test_missing_section_goes_to_uncategorized(tmp_path):
    f = tmp_path / "paper.org"
    f.write_text("* FISH-5SS\n\n* Annotations (zotero)\n")
    annotations = [
        {"key": "EE5", "annotationComment": "{CRITICS} A critique",
         "annotationText": "", "annotationPageLabel": "2"}
    ]
    insert_annotations(f, annotations)
    content = f.read_text()
    assert "* Uncategorized annotations" in content
    assert "[zotero:EE5]" in content
