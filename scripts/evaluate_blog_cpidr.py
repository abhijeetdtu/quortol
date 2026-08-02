#!/usr/bin/env python3
"""Evaluate Markdown or plain-text documents with a CPIDR-inspired metric."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parent.parent
SUPPORTED_SUFFIXES = {".md", ".txt"}
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.blog_cpidr import (
    METHOD_VERSION,
    NLPModelUnavailable,
    evaluate_markdown,
    load_nlp,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Measure CPIDR-inspired idea density in Markdown or text documents."
    )
    parser.add_argument(
        "target", help="A .md/.txt file or directory to scan recursively"
    )
    parser.add_argument(
        "--format", choices=("text", "json"), default="text", dest="output_format"
    )
    parser.add_argument(
        "--output", type=Path, help="Write the report to this path instead of stdout"
    )
    return parser


def resolve_files(target: Path) -> list[Path]:
    if target.is_file():
        if target.suffix.lower() not in SUPPORTED_SUFFIXES:
            raise ValueError(f"Target file must be .md or .txt: {target}")
        return [target]
    if target.is_dir():
        files = sorted(
            (
                path
                for path in target.rglob("*")
                if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
            ),
            key=lambda p: str(p).lower(),
        )
        if not files:
            raise ValueError(f"No .md or .txt files found under: {target}")
        return files
    raise ValueError(f"Target does not exist: {target}")


def build_report(files: list[Path], nlp: Any) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for path in files:
        try:
            results.append(evaluate_markdown(path, nlp=nlp).to_dict())
        except (OSError, UnicodeError) as exc:
            errors.append({"path": str(path), "error": str(exc)})

    densities = [item["idea_density"] for item in results]
    aggregate = {
        "file_count": len(results),
        "error_count": len(errors),
        "mean_density": sum(densities) / len(densities) if densities else 0.0,
        "min_density": min(densities) if densities else 0.0,
        "max_density": max(densities) if densities else 0.0,
    }
    return {
        "method": {
            "name": "CPIDR-inspired propositional idea density",
            "version": METHOD_VERSION,
            "diagnostic_only": True,
        },
        "files": results,
        "aggregate": aggregate,
        "errors": errors,
    }


def format_text(report: dict[str, Any]) -> str:
    lines = [f"{report['method']['name']} ({report['method']['version']})", ""]
    for item in report["files"]:
        lines.append(
            f"{item['path']}: density={item['idea_density']:.4f} "
            f"propositions={item['proposition_count']} words={item['word_count']}"
        )
    for error in report["errors"]:
        lines.append(f"ERROR {error['path']}: {error['error']}")
    aggregate = report["aggregate"]
    lines.extend(
        [
            "",
            f"Files: {aggregate['file_count']} evaluated, {aggregate['error_count']} errors",
            "Density: "
            f"mean={aggregate['mean_density']:.4f} min={aggregate['min_density']:.4f} "
            f"max={aggregate['max_density']:.4f}",
            "Diagnostic only; this score is not a publishing pass/fail decision.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_cli(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO = sys.stdout,
    stderr: TextIO = sys.stderr,
) -> int:
    args = build_parser().parse_args(argv)
    try:
        files = resolve_files(Path(args.target))
        nlp = load_nlp()
    except (ValueError, NLPModelUnavailable) as exc:
        print(f"Error: {exc}", file=stderr)
        return 2

    report = build_report(files, nlp)
    rendered = (
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output_format == "json"
        else format_text(report)
    )
    try:
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        else:
            stdout.write(rendered)
    except OSError as exc:
        print(f"Error writing report: {exc}", file=stderr)
        return 2
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(run_cli())
