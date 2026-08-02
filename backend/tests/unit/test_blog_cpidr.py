from __future__ import annotations

from dataclasses import dataclass

import pytest

from backend.blog_cpidr import evaluate_text, markdown_to_prose


@dataclass(eq=False)
class Token:
    text: str
    tag_: str
    dep_: str = ""
    pos_: str = ""
    lemma_: str = ""
    is_punct: bool = False
    is_space: bool = False
    like_url: bool = False

    @property
    def lower_(self) -> str:
        return self.text.lower()

    def __post_init__(self) -> None:
        if not self.lemma_:
            self.lemma_ = self.lower_


class Pipeline:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    def __call__(self, text: str) -> list[Token]:
        return self.tokens


def evaluate(tokens: list[Token]):
    return evaluate_text("fixture text", nlp=Pipeline(tokens))


def test_markdown_cleanup_keeps_visible_prose_and_removes_non_prose():
    markdown = """---
title: Test
---
# Useful Heading

Read [the report](https://example.com/report) now. https://example.com/raw

![A chart](/api/blog/images/chart.png)

```python
secret_call()
```

| Name | Value |
| --- | --- |
| Alpha | 4 |
"""
    prose = markdown_to_prose(markdown)

    assert "Useful Heading" in prose
    assert "Read the report now." in prose
    assert "Name Value" in prose
    assert "Alpha 4" in prose
    assert "title: Test" not in prose
    assert "secret_call" not in prose
    assert "chart.png" not in prose
    assert "https://" not in prose
    assert "|" not in prose


def test_baseline_categories_and_articles():
    result = evaluate(
        [
            Token("The", "DT"),
            Token("quick", "JJ"),
            Token("fox", "NN"),
            Token("runs", "VBZ"),
            Token("swiftly", "RB"),
            Token("through", "IN"),
            Token("woods", "NNS"),
        ]
    )

    assert result.word_count == 7
    assert result.proposition_count == 4
    assert result.idea_density == pytest.approx(4 / 7)
    assert result.category_counts == {
        "adjectives": 1,
        "adverbs": 1,
        "prepositions": 1,
        "verbs": 1,
    }
    assert result.adjustment_counts["articles_excluded"] == 1


def test_auxiliary_chain_and_negative_modal_count_only_semantic_ideas():
    result = evaluate(
        [
            Token("may", "MD"),
            Token("not", "RB"),
            Token("have", "VB", dep_="aux", pos_="AUX"),
            Token("been", "VBN", dep_="aux", pos_="AUX", lemma_="be"),
            Token("singing", "VBG", dep_="ROOT", pos_="VERB", lemma_="sing"),
        ]
    )

    assert result.proposition_count == 2
    assert result.category_counts == {"adverbs": 1, "verbs": 1}
    assert result.adjustment_counts["auxiliary_verbs_combined"] == 2
    assert result.adjustment_counts["negative_modals_observed"] == 1


def test_infinitive_to_is_combined_with_verb():
    result = evaluate([Token("to", "TO"), Token("run", "VB", pos_="VERB")])

    assert result.proposition_count == 1
    assert result.adjustment_counts["infinitive_to_combined"] == 1


def test_adjectival_copula_is_combined_but_noun_predicate_is_not():
    adjective = evaluate(
        [Token("She", "PRP"), Token("is", "VBZ", lemma_="be"), Token("kind", "JJ")]
    )
    noun = evaluate(
        [
            Token("She", "PRP"),
            Token("is", "VBZ", lemma_="be"),
            Token("a", "DT"),
            Token("doctor", "NN"),
        ]
    )

    assert adjective.proposition_count == 1
    assert adjective.adjustment_counts["adjectival_copulas_combined"] == 1
    assert noun.proposition_count == 1


@pytest.mark.parametrize(
    "first,second", [("either", "or"), ("neither", "nor"), ("both", "and")]
)
def test_paired_conjunctions_count_as_one(first: str, second: str):
    result = evaluate(
        [
            Token(first, "RB"),
            Token("cats", "NNS"),
            Token(second, "CC"),
            Token("dogs", "NNS"),
        ]
    )

    assert result.proposition_count == 1
    assert result.adjustment_counts["paired_conjunctions_combined"] == 1


def test_empty_text_has_zero_density_without_calling_pipeline():
    class FailPipeline:
        def __call__(self, text: str):
            raise AssertionError("empty input should not be tagged")

    result = evaluate_text("", nlp=FailPipeline())

    assert result.word_count == 0
    assert result.proposition_count == 0
    assert result.idea_density == 0.0
