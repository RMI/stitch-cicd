#! /usr/bin/env -S uv run --package stitch-api --exact

"""Check API_REFERENCE.md against the current OpenAPI schema for missing endpoints."""

import re
import sys
from pathlib import Path

from stitch.api.main import app


def get_doc_endpoints(doc_path: Path) -> set[str]:
    """Extract endpoint signatures from markdown headings."""
    text = doc_path.read_text()
    matches = re.findall(r"### `(\w+) (.+?)`", text)
    return {f"{method} {path}" for method, path in matches}


def get_openapi_endpoints() -> set[str]:
    """Extract endpoint signatures from the OpenAPI schema."""
    openapi = app.openapi()
    endpoints = set()
    for path, methods in openapi.get("paths", {}).items():
        for method in methods:
            if method in ("get", "post", "put", "patch", "delete"):
                endpoints.add(f"{method.upper()} {path}")
    return endpoints


def main():
    script_dir = Path(__file__).parent
    default_doc = script_dir.parent / "API_REFERENCE.md"
    doc_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_doc

    if not doc_path.exists():
        print(f"Error: {doc_path} not found")
        sys.exit(1)

    doc_endpoints = get_doc_endpoints(doc_path)
    api_endpoints = get_openapi_endpoints()

    missing = api_endpoints - doc_endpoints
    if missing:
        print("API_REFERENCE.md is out of date. Missing endpoints:")
        for endpoint in sorted(missing):
            print(f"  - {endpoint}")
        sys.exit(1)

    print("API_REFERENCE.md is up to date.")


if __name__ == "__main__":
    main()
