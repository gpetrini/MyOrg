import argparse
import sys
from pathlib import Path
import requests

sys.path.insert(0, str(Path(__file__).parent))
from config import ORG_SEARCH_DIR
from zotero_client import get_item_key, get_pdf_key, get_annotations
from org_writer import find_org_file, insert_annotations


def main():
    parser = argparse.ArgumentParser(
        description="Extract Zotero annotations into Org bib file"
    )
    parser.add_argument("citekey", help="Better BibTeX citation key (used for Zotero lookup)")
    parser.add_argument("--file", type=Path, help="Path to .org file (skips automatic search)")
    args = parser.parse_args()

    try:
        item_key = get_item_key(args.citekey)
        pdf_key = get_pdf_key(item_key)
        annotations = get_annotations(pdf_key)
    except requests.ConnectionError:
        print("Error: Cannot connect to Zotero. Make sure Zotero is open.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        org_file = args.file if args.file else find_org_file(
            args.citekey, Path(ORG_SEARCH_DIR).expanduser()
        )
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    insert_annotations(org_file, annotations)
    print(f"Done: {len(annotations)} annotation(s) processed → {org_file}")


if __name__ == "__main__":
    main()
