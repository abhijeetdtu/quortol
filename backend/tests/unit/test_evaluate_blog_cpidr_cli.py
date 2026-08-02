from __future__ import annotations

import io
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import evaluate_blog_cpidr as cli
from backend.blog_cpidr import IdeaDensityResult, NLPModelUnavailable


def result(path: Path, density: float) -> IdeaDensityResult:
    return IdeaDensityResult(
        path=str(path),
        word_count=10,
        proposition_count=round(density * 10),
        idea_density=density,
        category_counts={"verbs": 2},
        adjustment_counts={},
    )


def test_directory_json_output_is_sorted_and_aggregated(tmp_path, monkeypatch):
    (tmp_path / "z.md").write_text("# Z", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "a.txt").write_text("A", encoding="utf-8")
    (nested / "ignored.csv").write_text("Ignored", encoding="utf-8")
    monkeypatch.setattr(cli, "load_nlp", lambda: object())
    monkeypatch.setattr(
        cli,
        "evaluate_markdown",
        lambda path, nlp: result(path, 0.2 if path.name == "a.txt" else 0.6),
    )
    stdout = io.StringIO()

    exit_code = cli.run_cli(
        [str(tmp_path), "--format", "json"], stdout=stdout, stderr=io.StringIO()
    )
    report = json.loads(stdout.getvalue())

    assert exit_code == 0
    assert [Path(item["path"]).name for item in report["files"]] == ["a.txt", "z.md"]
    assert report["aggregate"] == {
        "file_count": 2,
        "error_count": 0,
        "mean_density": 0.4,
        "min_density": 0.2,
        "max_density": 0.6,
    }
    assert "pass" not in report["files"][0]


def test_mixed_batch_reports_error_and_returns_one(tmp_path, monkeypatch):
    good = tmp_path / "good.md"
    bad = tmp_path / "bad.md"
    good.write_text("Good", encoding="utf-8")
    bad.write_text("Bad", encoding="utf-8")
    monkeypatch.setattr(cli, "load_nlp", lambda: object())

    def fake_evaluate(path, nlp):
        if path.name == "bad.md":
            raise UnicodeError("invalid UTF-8")
        return result(path, 0.5)

    monkeypatch.setattr(cli, "evaluate_markdown", fake_evaluate)
    stdout = io.StringIO()

    exit_code = cli.run_cli([str(tmp_path)], stdout=stdout, stderr=io.StringIO())

    assert exit_code == 1
    assert "good.md: density=0.5000" in stdout.getvalue()
    assert "ERROR" in stdout.getvalue()


def test_invalid_target_and_missing_model_return_two(tmp_path, monkeypatch):
    stderr = io.StringIO()
    assert (
        cli.run_cli([str(tmp_path / "missing.md")], stdout=io.StringIO(), stderr=stderr)
        == 2
    )
    assert "does not exist" in stderr.getvalue()

    unsupported = tmp_path / "blog.pdf"
    unsupported.write_bytes(b"PDF")
    stderr = io.StringIO()
    assert cli.run_cli([str(unsupported)], stdout=io.StringIO(), stderr=stderr) == 2
    assert "must be .md or .txt" in stderr.getvalue()

    blog = tmp_path / "blog.md"
    blog.write_text("Blog", encoding="utf-8")
    monkeypatch.setattr(
        cli,
        "load_nlp",
        lambda: (_ for _ in ()).throw(NLPModelUnavailable("install model")),
    )
    stderr = io.StringIO()
    assert cli.run_cli([str(blog)], stdout=io.StringIO(), stderr=stderr) == 2
    assert "install model" in stderr.getvalue()


def test_output_file_receives_report(tmp_path, monkeypatch):
    blog = tmp_path / "blog.txt"
    output = tmp_path / "report.json"
    blog.write_text("Blog", encoding="utf-8")
    monkeypatch.setattr(cli, "load_nlp", lambda: object())
    monkeypatch.setattr(cli, "evaluate_markdown", lambda path, nlp: result(path, 0.4))

    exit_code = cli.run_cli(
        [str(blog), "--format", "json", "--output", str(output)],
        stdout=io.StringIO(),
        stderr=io.StringIO(),
    )

    assert exit_code == 0
    assert (
        json.loads(output.read_text(encoding="utf-8"))["files"][0]["idea_density"]
        == 0.4
    )
