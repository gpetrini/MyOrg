import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from unittest.mock import patch, Mock
from scripts.zotero_extract.zotero_client import get_item_key, get_pdf_key, get_annotations

MOCK_ITEMS = [
    {"key": "ABCD1234", "data": {"key": "ABCD1234", "extra": "Citation Key: minsky_1977_Financial\nDOI: 10.1/x", "itemType": "journalArticle"}},
    {"key": "ZZZZ9999", "data": {"key": "ZZZZ9999", "extra": "Citation Key: other_2020", "itemType": "journalArticle"}},
]

MOCK_CHILDREN_PARENT = [
    {"key": "PDF00001", "data": {"key": "PDF00001", "contentType": "application/pdf", "itemType": "attachment"}},
    {"key": "NOTE0001", "data": {"key": "NOTE0001", "contentType": "", "itemType": "note"}},
]

MOCK_CHILDREN_PDF = [
    {"key": "ANN00001", "data": {"key": "ANN00001", "itemType": "annotation", "annotationType": "highlight",
                                  "annotationText": "some text", "annotationComment": "{BACKGROUND}",
                                  "annotationPageLabel": "3", "annotationColor": "#ffd400"}},
    {"key": "NOTE0002", "data": {"key": "NOTE0002", "itemType": "note"}},
]


def make_mock_get(url, params=None, headers=None):
    r = Mock()
    r.raise_for_status = Mock()
    if "PDF00001/children" in url:
        r.json.return_value = MOCK_CHILDREN_PDF
    elif "/children" in url:
        r.json.return_value = MOCK_CHILDREN_PARENT
    else:
        r.json.return_value = MOCK_ITEMS
    return r


@patch("scripts.zotero_extract.zotero_client.requests.get", side_effect=make_mock_get)
def test_get_item_key_finds_by_citekey(_):
    assert get_item_key("minsky_1977_Financial") == "ABCD1234"


@patch("scripts.zotero_extract.zotero_client.requests.get", side_effect=make_mock_get)
def test_get_item_key_raises_when_not_found(_):
    with pytest.raises(ValueError, match="No Zotero item"):
        get_item_key("missing_2099")


@patch("scripts.zotero_extract.zotero_client.requests.get", side_effect=make_mock_get)
def test_get_pdf_key_returns_pdf_attachment(_):
    assert get_pdf_key("ABCD1234") == "PDF00001"


@patch("scripts.zotero_extract.zotero_client.requests.get", side_effect=make_mock_get)
def test_get_annotations_returns_only_annotation_items(_):
    anns = get_annotations("PDF00001")
    assert len(anns) == 1
    assert anns[0]["annotationType"] == "highlight"
    assert anns[0]["key"] == "ANN00001"
