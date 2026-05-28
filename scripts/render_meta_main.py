#!/usr/bin/env python3
"""
Render meta/main.yml from templates/meta_main.yml.j2 using molecule/shared/vars.yml.

Supported input schema:
platform_matrix:
  ubuntu: ["26.04", "24.04"]
  debian: ["13", "12"]
  fedora: ["44", "43"]

Behavior:
- Ubuntu numeric releases are converted to codenames for Galaxy metadata.
- Debian numeric releases are converted to codenames for Galaxy metadata.
- Fedora is rendered as "all" in metadata to remain compatible with
  ansible-lint's current meta schema when newer Fedora releases are not yet listed.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

UBUNTU_CODENAME_MAP = {
    "20.04": "focal",
    "22.04": "jammy",
    "24.04": "noble",
    "26.04": "resolute",
}

DEBIAN_CODENAME_MAP = {
    "11": "bullseye",
    "12": "bookworm",
    "13": "trixie",
    "14": "forky",
}

PLATFORM_NAME_MAP = {
    "fedora": "Fedora",
    "ubuntu": "Ubuntu",
    "debian": "Debian",
}

PLATFORM_ORDER = ("fedora", "ubuntu", "debian")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a mapping in {path}")
    return data


def extract_matrix(data: dict[str, Any]) -> dict[str, list[Any]]:
    matrix = data.get("platform_matrix", data)
    if not isinstance(matrix, dict):
        raise ValueError("Expected 'platform_matrix' to be a mapping")
    return matrix


def normalize_versions(platform_key: str, versions: list[Any]) -> list[str]:
    normalized: list[str] = []

    if platform_key == "fedora":
        # ansible-lint's meta schema can lag Fedora releases.
        # Preserve the test matrix elsewhere, but render Galaxy metadata as "all".
        return ["all"]

    for raw in versions:
        value = str(raw).strip().strip('"').strip("'")
        if not value:
            continue

        if platform_key == "ubuntu":
            if value in UBUNTU_CODENAME_MAP:
                normalized.append(UBUNTU_CODENAME_MAP[value])
            elif value.replace(".", "").isdigit():
                raise ValueError(
                    f"Unsupported Ubuntu release in metadata renderer: {value}"
                )
            else:
                normalized.append(value.lower())

        elif platform_key == "debian":
            if value in DEBIAN_CODENAME_MAP:
                normalized.append(DEBIAN_CODENAME_MAP[value])
            elif value.isdigit():
                raise ValueError(
                    f"Unsupported Debian release in metadata renderer: {value}"
                )
            else:
                normalized.append(value.lower())

        else:
            normalized.append(value)

    return normalized


def matrix_to_platforms(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    platforms: list[dict[str, Any]] = []

    for key in PLATFORM_ORDER:
        versions = matrix.get(key)
        if versions is None:
            continue

        if not isinstance(versions, list):
            raise ValueError(
                f"Expected list of versions for '{key}', got {type(versions).__name__}"
            )

        items = normalize_versions(key, versions)
        if not items:
            continue

        platforms.append(
            {
                "name": PLATFORM_NAME_MAP[key],
                "versions": items,
            }
        )

    if not platforms:
        raise ValueError("No supported platforms found in matrix input")

    return platforms


def render(template_path: Path, output_path: Path, vars_path: Path) -> None:
    raw = load_yaml(vars_path)
    matrix = extract_matrix(raw)
    platforms = matrix_to_platforms(matrix)

    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.get_template(template_path.name)
    rendered = template.render(
        template_name=str(template_path),
        generated_on=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        platforms=platforms,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered.rstrip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render meta/main.yml from molecule/shared/vars.yml"
    )
    parser.add_argument(
        "--vars-file",
        default="molecule/shared/vars.yml",
        help="Path to shared vars file (default: molecule/shared/vars.yml)",
    )
    parser.add_argument(
        "--template",
        default="templates/meta_main.yml.j2",
        help="Path to metadata template (default: templates/meta_main.yml.j2)",
    )
    parser.add_argument(
        "--output",
        default="meta/main.yml",
        help="Output path (default: meta/main.yml)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    render(Path(args.template), Path(args.output), Path(args.vars_file))
