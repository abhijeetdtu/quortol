"""CPIDR-inspired propositional idea-density evaluation for English prose.

This is a modern approximation of Brown et al. (2008), not an implementation
of, or drop-in replacement for, the original CPIDR software.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Any

METHOD_VERSION = "cpidr-inspired-spacy-v1"
DEFAULT_SPACY_MODEL = "en_core_web_sm"


class NLPModelUnavailable(RuntimeError):
    """Raised when the configured spaCy English pipeline cannot be loaded."""


@dataclass(frozen=True)
class IdeaDensityResult:
    path: str | None
    word_count: int
    proposition_count: int
    idea_density: float
    category_counts: dict[str, int]
    adjustment_counts: dict[str, int]
    method_version: str = METHOD_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_nlp: Any | None = None


def load_nlp(model_name: str = DEFAULT_SPACY_MODEL) -> Any:
    """Load and cache the configured spaCy pipeline."""
    global _nlp
    if _nlp is not None:
        return _nlp
    try:
        import spacy
    except ImportError as exc:
        raise NLPModelUnavailable(
            "spaCy is not installed. Run: pip install -r backend/requirements.txt"
        ) from exc
    try:
        _nlp = spacy.load(model_name)
    except OSError as exc:
        raise NLPModelUnavailable(
            f"spaCy model '{model_name}' is unavailable. Run: "
            f"python -m spacy download {model_name}"
        ) from exc
    return _nlp


def markdown_to_prose(markdown: str) -> str:
    """Remove Markdown metadata and non-prose syntax while retaining visible text."""
    text = markdown.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\A\ufeff?---\s*\n.*?\n---\s*(?:\n|\Z)", "", text, flags=re.DOTALL)
    text = re.sub(r"```[^\n]*\n[\s\S]*?```", " ", text)
    text = re.sub(r"~~~[^\n]*\n[\s\S]*?~~~", " ", text)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<https?://[^>]+>", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)

    prose_lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if re.fullmatch(r"\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*", line):
            continue
        line = re.sub(r"^#{1,6}\s+", "", line)
        line = re.sub(r"^>\s?", "", line)
        line = re.sub(r"^(?:[-+*]|\d+[.)])\s+", "", line)
        if "|" in line:
            line = " ".join(
                cell.strip() for cell in line.strip("|").split("|") if cell.strip()
            )
        line = re.sub(r"[*_~]+", "", line)
        prose_lines.append(line)
    return re.sub(r"\s+", " ", "\n".join(prose_lines)).strip()


def _category(tag: str) -> str | None:
    if tag == "CC":
        return "conjunctions"
    if tag == "CD":
        return "numerals"
    if tag in {"DT", "PDT"}:
        return "determiners"
    if tag == "IN":
        return "prepositions"
    if tag.startswith("JJ"):
        return "adjectives"
    if tag in {"POS", "PP$", "PRP$"}:
        return "possessives"
    if tag.startswith("RB"):
        return "adverbs"
    if tag == "TO":
        return "infinitives_or_to"
    if tag.startswith("VB"):
        return "verbs"
    if tag in {"WDT", "WP", "WP$", "WPS", "WRB"}:
        return "relatives_or_interrogatives"
    return None


def _next_word(tokens: list[Any], index: int) -> Any | None:
    for token in tokens[index + 1 :]:
        if not getattr(token, "is_punct", False) and not getattr(
            token, "is_space", False
        ):
            return token
    return None


def _next_content_word(tokens: list[Any], index: int) -> Any | None:
    for token in tokens[index + 1 :]:
        if getattr(token, "is_punct", False) or getattr(token, "is_space", False):
            continue
        if getattr(token, "lower_", token.text.lower()) in {"a", "an", "the"}:
            continue
        return token
    return None


def evaluate_text(
    text: str, *, nlp: Any | None = None, path: str | None = None
) -> IdeaDensityResult:
    """Evaluate plain English text using CPIDR-inspired POS rules."""
    pipeline = nlp or load_nlp()
    tokens = list(pipeline(text)) if text.strip() else []
    words = [
        token
        for token in tokens
        if not getattr(token, "is_punct", False)
        and not getattr(token, "is_space", False)
        and not getattr(token, "like_url", False)
    ]
    candidates: dict[int, str] = {}
    categories: Counter[str] = Counter()
    adjustments: Counter[str] = Counter()

    for index, token in enumerate(tokens):
        if token not in words:
            continue
        tag = getattr(token, "tag_", "")
        category = _category(tag)
        if category is None:
            continue
        lower = getattr(token, "lower_", token.text.lower())
        if tag == "DT" and lower in {"a", "an", "the"}:
            adjustments["articles_excluded"] += 1
            continue
        candidates[index] = category

    removed: set[int] = set()

    def remove(index: int, reason: str) -> None:
        if index in candidates and index not in removed:
            removed.add(index)
            adjustments[reason] += 1

    for index, token in enumerate(tokens):
        lower = getattr(token, "lower_", token.text.lower())
        tag = getattr(token, "tag_", "")
        dep = getattr(token, "dep_", "")
        following = _next_word(tokens, index)

        if (
            tag == "TO"
            and following is not None
            and getattr(following, "tag_", "").startswith("VB")
        ):
            remove(index, "infinitive_to_combined")

        if dep in {"aux", "auxpass"} and tag.startswith("VB"):
            remove(index, "auxiliary_verbs_combined")

        lemma = getattr(token, "lemma_", lower).lower()
        if lemma == "be" and tag.startswith("VB") and dep not in {"aux", "auxpass"}:
            complement = _next_content_word(tokens, index)
            if complement is not None and getattr(complement, "tag_", "").startswith(
                "JJ"
            ):
                remove(index, "adjectival_copulas_combined")

        if tag == "MD" and following is not None:
            next_lower = getattr(following, "lower_", following.text.lower())
            if next_lower in {"not", "n't", "n’t"}:
                adjustments["negative_modals_observed"] += 1

    pairs = {"either": "or", "neither": "nor", "both": "and"}
    for index, token in enumerate(tokens):
        lower = getattr(token, "lower_", token.text.lower())
        expected = pairs.get(lower)
        if expected and any(
            getattr(later, "lower_", later.text.lower()) == expected
            for later in tokens[index + 1 :]
        ):
            remove(index, "paired_conjunctions_combined")

    for index, category in candidates.items():
        if index not in removed:
            categories[category] += 1

    proposition_count = sum(categories.values())
    word_count = len(words)
    return IdeaDensityResult(
        path=path,
        word_count=word_count,
        proposition_count=proposition_count,
        idea_density=proposition_count / word_count if word_count else 0.0,
        category_counts=dict(sorted(categories.items())),
        adjustment_counts=dict(sorted(adjustments.items())),
    )


def evaluate_markdown(path: str | Path, *, nlp: Any | None = None) -> IdeaDensityResult:
    """Read and evaluate a UTF-8 Markdown blog."""
    markdown_path = Path(path)
    prose = markdown_to_prose(markdown_path.read_text(encoding="utf-8"))
    return evaluate_text(prose, nlp=nlp, path=str(markdown_path))
