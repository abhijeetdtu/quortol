from __future__ import annotations

import io
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_blog_podcasts as pipeline
from backend.blog_markdown import BlogMarkdownDocument


def _doc(path: Path, slug: str, title: str) -> BlogMarkdownDocument:
    return BlogMarkdownDocument(
        path=path,
        title=title,
        slug=slug,
        excerpt=f"{title} excerpt",
        content=f"# {title}\n\nSome content for {title}.",
        tags=["tag"],
        published_at=pipeline.datetime(2026, 1, 1),
        updated_at=pipeline.datetime(2026, 1, 1),
        has_explicit_published_at=True,
        has_explicit_updated_at=True,
    )


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_run_cli_generates_one_bundle_and_continues_after_failure(tmp_path, monkeypatch):
    path_a = tmp_path / "alpha.md"
    path_b = tmp_path / "beta.md"
    path_a.write_text("# Alpha", encoding="utf-8")
    path_b.write_text("# Beta", encoding="utf-8")
    documents = {
        path_a: _doc(path_a, "alpha", "Alpha"),
        path_b: _doc(path_b, "beta", "Beta"),
    }

    success_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "episode_title": "Alpha Episode",
                            "episode_summary": "Summary",
                            "segments": [
                                {"speaker": "host_a", "section": "intro", "text": "Intro."},
                                {"speaker": "host_b", "section": "discussion", "text": "Response."},
                            ],
                        }
                    )
                }
            }
        ]
    }

    def fake_requester(endpoint, json, timeout):
        prompt = json["messages"][1]["content"]
        if "title: Alpha" in prompt:
            return FakeResponse(success_payload)
        raise RuntimeError("llm offline")

    def fake_synthesizer(text: str, voice: str, speed: float, lang: str):
        return 24_000, [0.0, 0.1, -0.1]

    monkeypatch.setattr(pipeline, "resolve_target_files", lambda args: [path_a, path_b])
    monkeypatch.setattr(pipeline, "parse_markdown_file", lambda current_path: documents[current_path])
    monkeypatch.setattr(
        pipeline,
        "load_prompt_template",
        lambda current_path: (
            "SOURCE MATERIAL:\n{{SOURCE_MATERIAL}}\n\n"
            "PODCAST TITLE:\n{{PODCAST_TITLE}}\n\n"
            "TARGET LENGTH:\n{{WORD_COUNT}} words\n"
        ),
    )

    stdout = io.StringIO()
    stderr = io.StringIO()
    output_dir = tmp_path / "out"
    exit_code = pipeline.run_cli(
        ["--all", "--output-dir", str(output_dir)],
        stdout=stdout,
        stderr=stderr,
        requester=fake_requester,
        synthesizer=fake_synthesizer,
    )

    assert exit_code == 1
    assert (output_dir / "alpha" / "episode.wav").exists()
    assert (output_dir / "alpha" / "script.md").exists()
    assert (output_dir / "beta" / "manifest.json").exists()
    failed_manifest = json.loads((output_dir / "beta" / "manifest.json").read_text(encoding="utf-8"))
    assert failed_manifest["status"] == "failed"
    assert "[generated] alpha" in stdout.getvalue()
    assert "[failed] beta" in stdout.getvalue()
