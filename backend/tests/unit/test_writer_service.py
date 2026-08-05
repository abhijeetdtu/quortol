import builtins

import pytest
import requests

from backend.features.writer.analysis import (
    ANALYSIS_TASKS,
    RECOMMENDATIONS_TASK,
    WriterAnalysisService,
    extract_model_text,
    sse_event,
)
from backend.features.writer.service import (
    CURSOR_MARKER,
    build_autocomplete_prompt,
    build_cursor_context,
    clean_recommendation,
    parse_initial_options,
    parse_recommendations,
    writer_backend_available,
)


WRITER_CONFIG = {
    'LLAMA_CPP_BASE_URL': 'http://llama.invalid/v1',
    'LLAMA_CPP_API_KEY': 'secret',
}


class ModelResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_writer_backend_available_accepts_openai_model_list(monkeypatch):
    monkeypatch.setattr(requests, 'get', lambda *args, **kwargs: ModelResponse({'data': []}))
    assert writer_backend_available(WRITER_CONFIG) is True


@pytest.mark.parametrize('failure', [
    requests.Timeout('timed out'),
    requests.ConnectionError('cannot connect'),
])
def test_writer_backend_available_handles_transport_failures(monkeypatch, failure):
    def fail(*args, **kwargs):
        raise failure
    monkeypatch.setattr(requests, 'get', fail)
    assert writer_backend_available(WRITER_CONFIG) is False


@pytest.mark.parametrize('payload', [None, {}, {'data': {}}, []])
def test_writer_backend_available_rejects_malformed_responses(monkeypatch, payload):
    monkeypatch.setattr(requests, 'get', lambda *args, **kwargs: ModelResponse(payload))
    assert writer_backend_available(WRITER_CONFIG) is False


def test_writer_backend_available_handles_missing_dependencies(monkeypatch):
    original_import = builtins.__import__

    def missing_langchain(name, *args, **kwargs):
        if name == 'langchain_openai':
            raise ImportError('missing')
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', missing_langchain)
    assert writer_backend_available(WRITER_CONFIG) is False


def test_clean_recommendation_removes_wrappers_and_repeated_prefix():
    assert clean_recommendation('```markdown\nHello world again\n```', 'Hello world') == 'again'


def test_parse_recommendations_reads_structured_response():
    assert parse_recommendations('["first", "second"]') == ['first', 'second']


@pytest.mark.parametrize('content', ['{}', '[1]', 'not json'])
def test_parse_recommendations_rejects_invalid_shapes(content):
    with pytest.raises((ValueError, TypeError)):
        parse_recommendations(content)


def test_parse_initial_options_separates_recommendations_and_angles():
    content = '[{"kind":"recommendation","text":"continue"},{"kind":"emotional_angle","text":"playful"}]'
    assert parse_initial_options(content) == (['continue'], ['playful'])


def test_cursor_context_marks_one_insertion_point():
    context = build_cursor_context('before', 'after')
    assert context['marked_document'].count(CURSOR_MARKER) == 1
    assert context['focused_left'] == 'before'


def test_autocomplete_prompt_keeps_cursor_instruction_last():
    prompt = build_autocomplete_prompt({'prefix': 'before', 'suffix': 'after', 'count': 2})
    assert prompt.endswith('Return only options that can be inserted at the marked cursor.')


@pytest.mark.parametrize('content,expected', [
    (' plain prose ', 'plain prose'),
    ([{'type': 'text', 'text': 'first'}, {'text': 'second'}], 'first\nsecond'),
    (['first', 'second'], 'first\nsecond'),
    ({'text': 'unsupported container'}, ''),
    (None, ''),
])
def test_extract_model_text_is_non_interpreting(content, expected):
    assert extract_model_text(content) == expected


def test_sse_event_serializes_unicode_as_one_frame():
    frame = sse_event({'type': 'block', 'block': {'content': 'café'}})
    assert frame.startswith('data: {')
    assert 'café' in frame
    assert frame.endswith('\n\n')


def test_analysis_stream_emits_ordered_blocks_and_recommendation_context(monkeypatch):
    service = WriterAnalysisService({})
    monkeypatch.setattr(service, '_llm', lambda: object())
    calls = []

    def run(llm, task, document, completed):
        calls.append((task.id, dict(completed)))
        return f'{task.id} prose'

    monkeypatch.setattr(service, '_run_task', run)
    events = list(service.stream('Title', 'Body'))
    blocks = [event['block'] for event in events if event['type'] == 'block']
    expected_ids = [task.id for task in ANALYSIS_TASKS] + [RECOMMENDATIONS_TASK.id]
    assert [block['id'] for block in blocks] == expected_ids
    assert set(calls[-1][1]) == set(expected_ids[:-1])
    assert events[-1] == {'type': 'complete', 'completed_ids': expected_ids, 'failed_ids': []}


def test_analysis_stream_continues_after_step_failure(monkeypatch):
    service = WriterAnalysisService({})
    monkeypatch.setattr(service, '_llm', lambda: object())

    def run(llm, task, document, completed):
        if task.id == 'imagery':
            raise TimeoutError('private upstream detail')
        return f'{task.id} prose'

    monkeypatch.setattr(service, '_run_task', run)
    events = list(service.stream('', 'Body'))
    error = next(event for event in events if event['type'] == 'step_error')
    assert error == {'type': 'step_error', 'id': 'imagery', 'message': 'Could not complete this section.'}
    assert events[-1]['failed_ids'] == ['imagery']
    assert events[-1]['completed_ids'][-1] == 'recommendations'
