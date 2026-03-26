#! /usr/bin/env -S uv run --package stitch-api --exact

"""CLI for generating and validating the Stitch API reference."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import click

from stitch.api.main import app

SCRIPT_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Generation helpers (from gen_api_doc.py)
# ---------------------------------------------------------------------------


def resolve_ref(schema: dict, openapi: dict) -> tuple[str | None, dict]:
    """Resolve a $ref pointer. Returns (schema_name, schema_dict)."""
    if "$ref" in schema:
        ref_path = schema["$ref"]  # e.g. "#/components/schemas/Foo"
        name = ref_path.rsplit("/", 1)[-1]
        parts = ref_path.lstrip("#/").split("/")
        node = openapi
        for part in parts:
            node = node[part]
        return name, node
    return None, schema


def format_type(prop: dict, openapi: dict) -> str:
    """Format a property's type as a readable string."""
    if "$ref" in prop:
        name, _ = resolve_ref(prop, openapi)
        return name or "object"

    if "anyOf" in prop:
        parts = []
        for variant in prop["anyOf"]:
            parts.append(format_type(variant, openapi))
        return " | ".join(parts)

    if "oneOf" in prop:
        parts = []
        for variant in prop["oneOf"]:
            parts.append(format_type(variant, openapi))
        return " | ".join(parts)

    typ = prop.get("type", "object")

    if typ == "null":
        return "null"

    if typ == "array":
        items = prop.get("items", {})
        item_type = format_type(items, openapi)
        return f"array[{item_type}]"

    if typ == "object":
        # Check for additionalProperties (dict-like)
        if "additionalProperties" in prop:
            val_type = format_type(prop["additionalProperties"], openapi)
            return f"object[string, {val_type}]"
        return "object"

    return typ


def render_properties(schema: dict, openapi: dict) -> list[str]:
    """Render a schema's properties as bulleted lines."""
    _, resolved = resolve_ref(schema, openapi)
    props = resolved.get("properties", {})
    lines = []
    for name, prop in props.items():
        type_str = format_type(prop, openapi)
        lines.append(f"- `{name}`: {type_str}")
    return lines


def get_request_body_schema(operation: dict) -> dict | None:
    """Extract the schema from a request body, if present."""
    body = operation.get("requestBody")
    if not body:
        return None
    content = body.get("content", {})
    json_content = content.get("application/json", {})
    return json_content.get("schema")


def get_response_schema(operation: dict) -> tuple[str, dict | None]:
    """Extract the success response status and schema."""
    responses = operation.get("responses", {})
    for status in ("200", "201", "204"):
        if status in responses:
            resp = responses[status]
            content = resp.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema")
            return status, schema
    # Fall back to first response
    if responses:
        status = next(iter(responses))
        resp = responses[status]
        content = resp.get("content", {})
        json_content = content.get("application/json", {})
        return status, json_content.get("schema")
    return "200", None


def generate_markdown(openapi: dict) -> str:
    """Generate the full Markdown document."""
    lines = ["# Stitch API Reference", ""]

    # Group paths by tag
    grouped: dict[str, list[tuple[str, str, dict]]] = {}
    for path, methods in openapi.get("paths", {}).items():
        for method, operation in methods.items():
            if method in ("get", "post", "put", "patch", "delete"):
                tags = operation.get("tags", ["Other"])
                tag = tags[0] if tags else "Other"
                grouped.setdefault(tag, []).append((method.upper(), path, operation))

    for tag, endpoints in grouped.items():
        # Section heading
        heading = tag.replace("-", " ").replace("_", " ").title()
        lines.append(f"## {heading}")
        lines.append("")

        for method, path, operation in endpoints:
            lines.append(f"### `{method} {path}`")
            lines.append("")
            lines.append("<!-- description -->")
            lines.append("")

            # Request body
            req_schema = get_request_body_schema(operation)
            if req_schema:
                name, _ = resolve_ref(req_schema, openapi)
                label = f"`{name}`" if name else "Body"
                lines.append(f"**Request Body:** {label}")
                lines.append("")
                prop_lines = render_properties(req_schema, openapi)
                lines.extend(prop_lines)
                lines.append("")

            # Response
            status, resp_schema = get_response_schema(operation)
            lines.append(f"**Response:** `{status}`")
            lines.append("")
            if resp_schema:
                prop_lines = render_properties(resp_schema, openapi)
                if prop_lines:
                    lines.extend(prop_lines)
                else:
                    # Array or primitive response
                    type_str = format_type(resp_schema, openapi)
                    lines.append(f"- {type_str}")
                lines.append("")

            lines.append("---")
            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.group()
def cli():
    """Stitch API documentation tools."""


@cli.command()
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default=None,
    help="Write output to PATH.",
)
@click.option(
    "--new",
    is_flag=True,
    default=False,
    help="Write to a timestamped file next to the script.",
)
def gen(output: str | None, new: bool):
    """Generate a Markdown API reference from the OpenAPI schema."""
    if output and new:
        raise click.UsageError("--output and --new are mutually exclusive.")

    openapi = app.openapi()
    md = generate_markdown(openapi)

    if new:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = SCRIPT_DIR / ".." / f"API_REFERENCE_{stamp}.md"
        dest = dest.resolve()
        dest.write_text(md)
        click.echo(f"Written to {dest}")
    elif output:
        Path(output).write_text(md)
        click.echo(f"Written to {output}")
    else:
        sys.stdout.write(md)


if __name__ == "__main__":
    cli()
