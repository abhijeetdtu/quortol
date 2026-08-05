"""LangGraph workflow for llama.cpp-backed writing completions."""

from __future__ import annotations

import json
import re
from typing import Any, TypedDict

import requests

CURSOR_MARKER = '<CURSOR_INSERTION_POINT>'
FOCUSED_LEFT_CONTEXT_CHARS = 1200


class CursorContext(TypedDict):
    marked_document: str
    focused_left: str


class WriterState(TypedDict, total=False):
    prefix: str
    suffix: str
    count: int
    prompt: str
    raw_recommendations: list[str]
    recommendations: list[str]
    emotional_angles: list[str]
    conditioning: str
    base_recommendations: list[str]


class WriterDependenciesUnavailable(RuntimeError):
    """Raised when the optional autocomplete runtime is not installed."""


def writer_backend_available(config: dict[str, Any]) -> bool:
    """Return whether the optional writer runtime and llama.cpp are ready."""
    try:
        import langchain_core.messages  # noqa: F401
        import langchain_openai  # noqa: F401
        import langgraph.graph  # noqa: F401
    except ImportError:
        return False

    base_url = str(config['LLAMA_CPP_BASE_URL']).rstrip('/')
    headers = {'Authorization': f"Bearer {config['LLAMA_CPP_API_KEY']}"}
    try:
        response = requests.get(f'{base_url}/models', headers=headers, timeout=3.0)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError, TypeError):
        return False
    return isinstance(payload, dict) and isinstance(payload.get('data'), list)


def build_cursor_context(
    prefix: str,
    suffix: str,
    focused_chars: int = FOCUSED_LEFT_CONTEXT_CHARS,
) -> CursorContext:
    """Represent the full document while making the actual insertion edge salient."""
    return {
        'marked_document': (
            f'<DOCUMENT>\n{prefix}\n{CURSOR_MARKER}\n{suffix}\n</DOCUMENT>'
        ),
        'focused_left': prefix[-focused_chars:],
    }


def cursor_instruction(context: CursorContext) -> str:
    """Place cursor-local context last to counter recency bias from a long suffix."""
    return (
        '<FOCUSED_LEFT_EDGE>\n'
        f"{context['focused_left']}\n"
        '</FOCUSED_LEFT_EDGE>\n\n'
        'Generate text only for <CURSOR_INSERTION_POINT>. Continue directly from the final '
        'words in <FOCUSED_LEFT_EDGE>. Everything after the cursor marker is already-written '
        'reference material: do not continue from, answer, summarize, or rewrite the document '
        'ending. Return only options that can be inserted at the marked cursor.'
    )


def build_autocomplete_prompt(state: WriterState) -> str:
    """Build either workflow prompt with identical cursor semantics and ordering."""
    context = build_cursor_context(state['prefix'], state['suffix'])
    focused_task = cursor_instruction(context)
    if state.get('conditioning'):
        originals = '\n'.join(f'- {value}' for value in state['base_recommendations'])
        return (
            f"{context['marked_document']}\n\n"
            f"ORIGINAL CANDIDATES AT THE MARKED CURSOR:\n{originals}\n\n"
            f"Rewrite the candidate continuations through this emotional or stylistic angle: "
            f"{state['conditioning']}. Produce exactly {state['count']} distinct short "
            f"insertions and exactly {state['count']} fresh emotional or stylistic angles "
            'that could transform the rewritten options again. Angle text must be a concise '
            '2-5 word label. Return one JSON array of objects; each object must contain kind '
            '(recommendation or emotional_angle) and text. Preserve the surrounding prose '
            'and return no explanation.\n\n'
            f"{focused_task}"
        )
    return (
        f"{context['marked_document']}\n\n"
        "Preserve the author's tone, delivery, style, and structure. "
        "Do not suggest language the author would not plausibly write. "
        f"Produce exactly {state['count']} distinct short insertions and exactly "
        f"{state['count']} useful emotional or stylistic angles (for example: funnier, "
        'more serious, more technical). Angle text must be a concise 2-5 word label. '
        'Return one JSON array of objects. Each object must contain kind '
        '(recommendation or emotional_angle) and text. Return no explanation.\n\n'
        f"{focused_task}"
    )


def clean_recommendation(value: str, prefix: str) -> str:
    text = value.strip()
    text = re.sub(r"^```(?:markdown|text)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^(?:assistant|continuation|suggestion)\s*:\s*", "", text, flags=re.IGNORECASE)
    if prefix and text.startswith(prefix):
        text = text[len(prefix):].lstrip()
    return text.strip()


def parse_recommendations(content: Any) -> list[str]:
    """Extract the recommendations array from one structured model response."""
    if isinstance(content, list):
        content = ''.join(
            block.get('text', '') if isinstance(block, dict) else str(block)
            for block in content
        )
    if not isinstance(content, str):
        raise ValueError('Autocomplete model returned non-text content.')
    text = content.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    payload = json.loads(text)
    values = payload
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ValueError('Autocomplete model returned invalid recommendations.')
    return values


def parse_initial_options(content: Any) -> tuple[list[str], list[str]]:
    """Parse one array containing recommendation and emotional-angle objects."""
    if isinstance(content, list):
        content = ''.join(
            block.get('text', '') if isinstance(block, dict) else str(block)
            for block in content
        )
    if not isinstance(content, str):
        raise ValueError('Autocomplete model returned non-text content.')
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)
    payload = json.loads(text)
    if not isinstance(payload, list):
        raise ValueError('Autocomplete model returned invalid options.')
    recommendations: list[str] = []
    angles: list[str] = []
    for item in payload:
        if not isinstance(item, dict) or not isinstance(item.get('text'), str):
            raise ValueError('Autocomplete model returned invalid options.')
        if item.get('kind') == 'recommendation':
            recommendations.append(item['text'])
        elif item.get('kind') == 'emotional_angle':
            angles.append(item['text'])
    return recommendations, angles


class WriterAutocompleteService:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self._graph = None

    def _build_graph(self):
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain_openai import ChatOpenAI
            from langgraph.graph import END, START, StateGraph
        except ImportError as exc:
            raise WriterDependenciesUnavailable from exc

        def build_prompt(state: WriterState) -> WriterState:
            return {'prompt': build_autocomplete_prompt(state)}

        def generate(state: WriterState) -> WriterState:
            llm = ChatOpenAI(
                base_url=self.config['LLAMA_CPP_BASE_URL'],
                api_key=self.config['LLAMA_CPP_API_KEY'],
                model=self.config['LLAMA_CPP_MODEL'],
                temperature=0.55,
                max_tokens=max(self.config['WRITER_MAX_OUTPUT_TOKENS'], state['count'] * 128),
                timeout=self.config['WRITER_TIMEOUT_SECONDS'],
                n=1,
                extra_body={'chat_template_kwargs': {'enable_thinking': False}},
            )
            messages = [
                SystemMessage(content=(
                    'You are a precise cursor-insertion engine. The cursor marker—not the end of '
                    'the supplied document—is always the sole generation point.'
                )),
                HumanMessage(content=state['prompt']),
            ]
            output_schema = {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'kind': {'type': 'string', 'enum': ['recommendation', 'emotional_angle']},
                        'text': {'type': 'string'},
                    },
                    'required': ['kind', 'text'],
                    'additionalProperties': False,
                },
                'minItems': state['count'] * 2,
                'maxItems': state['count'] * 2,
            }
            schema = {'type': 'json_schema', 'schema': output_schema}
            result = llm.invoke(messages, response_format=schema)
            values, angles = parse_initial_options(result.content)
            return {'raw_recommendations': values, 'emotional_angles': angles}

        def normalize(state: WriterState) -> WriterState:
            unique: list[str] = []
            seen: set[str] = set()
            for raw in state.get('raw_recommendations', []):
                candidate = clean_recommendation(raw, state['prefix'])
                key = candidate.casefold()
                if candidate and key not in seen:
                    seen.add(key)
                    unique.append(candidate)
            angles: list[str] = []
            seen_angles: set[str] = set()
            for raw in state.get('emotional_angles', []):
                angle = raw.strip().rstrip('?').strip()
                key = angle.casefold()
                if angle and key not in seen_angles:
                    seen_angles.add(key)
                    angles.append(angle)
            return {
                'recommendations': unique[:state['count']],
                'emotional_angles': angles[:state['count']],
            }

        graph = StateGraph(WriterState)
        graph.add_node('build_prompt', build_prompt)
        graph.add_node('generate', generate)
        graph.add_node('normalize', normalize)
        graph.add_edge(START, 'build_prompt')
        graph.add_edge('build_prompt', 'generate')
        graph.add_edge('generate', 'normalize')
        graph.add_edge('normalize', END)
        return graph.compile()

    def autocomplete(
        self,
        prefix: str,
        suffix: str,
        count: int,
        conditioning: str = '',
        base_recommendations: list[str] | None = None,
    ) -> dict[str, list[str]]:
        if self._graph is None:
            self._graph = self._build_graph()
        result = self._graph.invoke({
            'prefix': prefix,
            'suffix': suffix,
            'count': count,
            'conditioning': conditioning,
            'base_recommendations': base_recommendations or [],
        })
        return {
            'recommendations': result.get('recommendations', []),
            'emotional_angles': result.get('emotional_angles', []),
        }
