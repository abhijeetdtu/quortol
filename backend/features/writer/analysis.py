"""Progressive, plain-text whole-draft analysis."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
import json
from typing import Any

from .service import WriterDependenciesUnavailable

SCHEMA_VERSION = '2.0'


@dataclass(frozen=True)
class AnalysisTask:
    id: str
    title: str
    instruction: str


ANALYSIS_TASKS = (
    AnalysisTask('logical_consistency', 'Logical consistency',
                 'Assess logical consistency, progression, contradictions, and unsupported claims.'),
    AnalysisTask('depth', 'Depth', 'Assess the literary depth and development of ideas.'),
    AnalysisTask('originality', 'Originality', 'Assess originality and distinctiveness without guessing influences.'),
    AnalysisTask('voice', 'Voice', 'Assess the consistency and effectiveness of the authorial voice.'),
    AnalysisTask('imagery', 'Imagery', 'Assess imagery, sensory specificity, and figurative language.'),
    AnalysisTask('emotional_resonance', 'Emotional resonance',
                 'Assess emotional resonance and whether the text earns its emotional effects.'),
)
RECOMMENDATIONS_TASK = AnalysisTask(
    'recommendations', 'Recommendations',
    'Give the most useful concrete revision recommendations while preserving the author\'s voice.',
)


def extract_model_text(content: Any) -> str:
    """Flatten supported LangChain message content without interpreting model prose."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get('text'), str):
                parts.append(block['text'])
        return '\n'.join(part.strip() for part in parts if part.strip()).strip()
    return ''


def sse_event(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


class WriterAnalysisService:
    def __init__(self, config: dict[str, Any]):
        self.config = config

    def check_dependencies(self) -> None:
        try:
            import langchain_core.messages  # noqa: F401
            import langchain_openai  # noqa: F401
        except ImportError as exc:
            raise WriterDependenciesUnavailable from exc

    def _llm(self):
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise WriterDependenciesUnavailable from exc
        return ChatOpenAI(
            base_url=self.config['LLAMA_CPP_BASE_URL'],
            api_key=self.config['LLAMA_CPP_API_KEY'],
            model=self.config['LLAMA_CPP_MODEL'],
            temperature=0.2,
            max_tokens=self.config['WRITER_ANALYSIS_MAX_OUTPUT_TOKENS'],
            timeout=self.config['WRITER_ANALYSIS_TIMEOUT_SECONDS'],
            n=1,
            extra_body={'chat_template_kwargs': {'enable_thinking': False}},
        )

    @staticmethod
    def _document(title: str, body: str) -> str:
        return f'<TITLE>\n{title}\n</TITLE>\n\n<DRAFT>\n{body}\n</DRAFT>'

    def _run_task(
        self,
        llm: Any,
        task: AnalysisTask,
        document: str,
        completed: dict[str, str],
    ) -> str:
        from langchain_core.messages import HumanMessage, SystemMessage

        context = ''
        if task.id == 'recommendations':
            context = (
                '\n\n<COMPLETED_ASSESSMENTS>\n'
                + '\n\n'.join(f'{key}:\n{value}' for key, value in completed.items())
                + '\n</COMPLETED_ASSESSMENTS>'
            )
        prompt = (
            f'{task.instruction} Respond with one concise plain-text editorial note. '
            'Use short exact excerpts when useful. Do not return JSON, headings, scores, or boilerplate. '
            'Discuss only the requested task.\n\n'
            f'{document}{context}'
        )
        result = llm.invoke([
            SystemMessage(content='You are a rigorous, constructive literary editor.'),
            HumanMessage(content=prompt),
        ])
        text = extract_model_text(result.content)
        if not text:
            raise ValueError('The model returned empty content.')
        return text

    def stream(self, title: str, body: str) -> Iterator[dict[str, Any]]:
        llm = self._llm()
        document = self._document(title, body)
        completed: dict[str, str] = {}
        failed: list[str] = []
        yield {'type': 'start', 'schema_version': SCHEMA_VERSION}
        for task in (*ANALYSIS_TASKS, RECOMMENDATIONS_TASK):
            try:
                content = self._run_task(llm, task, document, completed)
                completed[task.id] = content
                yield {
                    'type': 'block',
                    'block': {'id': task.id, 'title': task.title, 'content': content},
                }
            except GeneratorExit:
                raise
            except Exception:
                failed.append(task.id)
                yield {
                    'type': 'step_error', 'id': task.id,
                    'message': 'Could not complete this section.',
                }
        yield {
            'type': 'complete',
            'completed_ids': list(completed),
            'failed_ids': failed,
        }
