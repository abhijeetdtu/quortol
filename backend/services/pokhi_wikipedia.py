from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import datetime, timezone
import re
import time

import requests

try:
    import wikipedia
    from wikipedia import exceptions as wikipedia_exceptions
except ImportError:  # pragma: no cover - handled at runtime by service checks
    wikipedia = None
    wikipedia_exceptions = None

class _NeverRaisedWikipediaError(Exception):
    """Fallback exception class used when wikipedia dependency is missing."""

if wikipedia_exceptions is not None:
    DISAMBIGUATION_ERROR = wikipedia_exceptions.DisambiguationError
    PAGE_ERROR = wikipedia_exceptions.PageError
    WIKIPEDIA_BASE_ERROR = wikipedia_exceptions.WikipediaException
else:  # pragma: no cover - evaluated only when dependency is missing
    DISAMBIGUATION_ERROR = _NeverRaisedWikipediaError
    PAGE_ERROR = _NeverRaisedWikipediaError
    WIKIPEDIA_BASE_ERROR = _NeverRaisedWikipediaError


class WikipediaUnavailableError(RuntimeError):
    pass


class WikipediaServiceError(RuntimeError):
    pass


class WikipediaService:
    def __init__(
        self,
        *,
        lang: str = "en",
        timeout: int = 8,
        retries: int = 2,
        retry_delay: float = 0.25,
        max_images: int = 8,
        max_content_chars: int = 8000,
    ) -> None:
        self.lang = lang
        self.api_url = f"https://{self.lang}.wikipedia.org/w/api.php"
        self.timeout = max(1, int(timeout))
        self.retries = max(1, int(retries))
        self.retry_delay = max(0.0, float(retry_delay))
        self.max_images = max(1, int(max_images))
        self.max_content_chars = max(500, int(max_content_chars))
        self._image_noise_regex = re.compile(
            r"logo|edit\-clear|icon|padlock\-silver|blue_pencil|ambox_important|portal\-puzzle|symbol|lock\-green|p_vip",
            re.IGNORECASE,
        )

        if wikipedia is not None:
            wikipedia.set_lang(self.lang)
            wikipedia.set_rate_limiting(True)

    def _require_client(self) -> None:
        if wikipedia is None:
            raise WikipediaUnavailableError(
                "Wikipedia dependency is not installed. Install `wikipedia` to enable this feature."
            )

    def _call_with_retry(self, func, *args, **kwargs):
        self._require_client()

        last_error = None
        for attempt in range(self.retries):
            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(func, *args, **kwargs)
                    return future.result(timeout=self.timeout)
            except FutureTimeoutError as exc:
                last_error = exc
            except (DISAMBIGUATION_ERROR, PAGE_ERROR) as exc:
                raise exc
            except Exception as exc:  # pragma: no cover - branch depends on upstream behavior
                last_error = exc

            if attempt < self.retries - 1:
                time.sleep(self.retry_delay)

        raise WikipediaServiceError(f"Wikipedia request failed after retries: {last_error}")

    def _http_api_request(self, params: dict) -> dict:
        last_error = None

        for attempt in range(self.retries):
            try:
                response = requests.get(
                    self.api_url,
                    params={"format": "json", **params},
                    timeout=self.timeout,
                    headers={"User-Agent": "quortol-pokhi/1.0 (wiki integration)"},
                )
                response.raise_for_status()
                payload = response.json()
                if not isinstance(payload, dict):
                    raise WikipediaServiceError("Unexpected non-JSON response from Wikipedia API")
                return payload
            except Exception as exc:  # pragma: no cover - depends on upstream behavior
                last_error = exc
                if attempt < self.retries - 1:
                    time.sleep(self.retry_delay)

        raise WikipediaServiceError(f"Wikipedia API request failed after retries: {last_error}")

    def _normalize_images(self, images):
        if not images:
            return []
        filtered = [url for url in images if url and not self._image_noise_regex.search(url)]
        return filtered[: self.max_images]

    def _safe_page_field(self, page, field: str, default=None):
        if isinstance(page, dict):
            return page.get(field, default)

        try:
            return getattr(page, field)
        except (AttributeError, KeyError):
            return default

    def _normalize_item(self, topic: str, page) -> dict:
        title = self._safe_page_field(page, "title", "")
        if not title:
            raise WikipediaServiceError("Wikipedia response missing required field: title")

        summary = (self._safe_page_field(page, "summary", "") or "").strip()
        content = (self._safe_page_field(page, "content", "") or "").strip()
        images = self._safe_page_field(page, "images", []) or []
        source_url = self._safe_page_field(page, "url", "") or ""

        if len(content) > self.max_content_chars:
            content = content[: self.max_content_chars].rstrip() + "..."

        return {
            "topic": topic,
            "title": title,
            "summary": summary,
            "content": content,
            "images": self._normalize_images(images),
            "source_url": source_url,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    def _first_paragraph(self, text: str) -> str:
        for paragraph in (text or "").split("\n\n"):
            cleaned = paragraph.strip()
            if cleaned:
                return cleaned
        return ""

    def _fetch_page_via_api(self, topic: str) -> dict:
        payload = self._http_api_request(
            {
                "action": "query",
                "redirects": 1,
                "prop": "extracts|info|pageimages",
                "inprop": "url",
                "piprop": "original",
                "explaintext": 1,
                "titles": topic,
            }
        )

        pages = (payload.get("query") or {}).get("pages") or {}
        if not pages:
            raise WikipediaServiceError(f"Topic '{topic}' not found")

        page = next(iter(pages.values()))
        if page.get("missing") is not None:
            raise WikipediaServiceError(f"Topic '{topic}' not found")

        content = (page.get("extract") or "").strip()
        summary = self._first_paragraph(content)
        image_source = ((page.get("original") or {}).get("source") or "").strip()

        normalized_page = {
            "title": page.get("title") or topic,
            "summary": summary,
            "content": content,
            "images": [image_source] if image_source else [],
            "url": (page.get("fullurl") or "").strip(),
        }
        return self._normalize_item(topic, normalized_page)

    def _search_topics_via_api(self, topic: str, limit: int) -> list[str]:
        payload = self._http_api_request(
            {
                "action": "query",
                "list": "search",
                "srsearch": topic,
                "srlimit": min(max(limit, 1), 30),
            }
        )
        search_results = (payload.get("query") or {}).get("search") or []
        return [item.get("title", "").strip() for item in search_results if item.get("title")]

    def _random_topics_via_api(self, limit: int) -> list[str]:
        payload = self._http_api_request(
            {
                "action": "query",
                "list": "random",
                "rnnamespace": 0,
                "rnlimit": min(max(limit, 1), 30),
            }
        )
        random_results = (payload.get("query") or {}).get("random") or []
        return [item.get("title", "").strip() for item in random_results if item.get("title")]

    def fetch_page(self, topic: str) -> dict:
        if not topic or not topic.strip():
            raise WikipediaServiceError("Topic is required")
        topic = topic.strip()
        page = None
        last_error = None

        if wikipedia is not None:
            client = wikipedia
            try:
                page = self._call_with_retry(client.page, title=topic, auto_suggest=True, redirect=True)
            except DISAMBIGUATION_ERROR as exc:
                if exc.options:
                    page = self._call_with_retry(
                        client.page, title=exc.options[0], auto_suggest=False, redirect=True
                    )
                else:
                    last_error = WikipediaServiceError(f"Topic '{topic}' is ambiguous")
            except (WikipediaServiceError, PAGE_ERROR, WIKIPEDIA_BASE_ERROR) as exc:
                last_error = WikipediaServiceError(str(exc))
            except Exception as exc:  # pragma: no cover - defensive
                last_error = WikipediaServiceError(str(exc))

        if page is not None:
            try:
                return self._normalize_item(topic, page)
            except WikipediaServiceError:
                raise
            except Exception as exc:  # pragma: no cover - defensive
                last_error = WikipediaServiceError(f"Wikipedia response parsing failed: {exc}")

        try:
            return self._fetch_page_via_api(topic)
        except WikipediaServiceError as fallback_exc:
            if last_error is not None:
                raise WikipediaServiceError(f"{last_error}; fallback failed: {fallback_exc}")
            raise

    def _get_candidates(self, count: int, seed_topic: str | None) -> list[str]:
        candidate_count = min(max(count * 3, 10), 30)
        candidates = []
        primary_error = None

        if wikipedia is not None:
            client = wikipedia
            try:
                if seed_topic:
                    candidates = self._call_with_retry(client.search, seed_topic, results=candidate_count) or []
                else:
                    while len(candidates) < candidate_count:
                        take = min(10, candidate_count - len(candidates))
                        random_titles = self._call_with_retry(client.random, pages=take)
                        if isinstance(random_titles, str):
                            random_titles = [random_titles]
                        candidates.extend(random_titles)
            except WikipediaServiceError as exc:
                primary_error = exc

        if candidates:
            return [title for title in candidates if title]

        try:
            if seed_topic:
                return self._search_topics_via_api(seed_topic, candidate_count)
            return self._random_topics_via_api(candidate_count)
        except WikipediaServiceError as fallback_exc:
            if primary_error is not None:
                raise WikipediaServiceError(f"{primary_error}; fallback failed: {fallback_exc}")
            raise

    def generate_feed(self, count: int = 10, seed_topic: str | None = None) -> dict:
        requested_count = max(1, int(count))
        normalized_seed = seed_topic.strip() if seed_topic else None

        candidates = self._get_candidates(requested_count, normalized_seed)
        items = []
        seen_titles = set()
        failures = 0

        for candidate in candidates:
            if len(items) >= requested_count:
                break

            try:
                item = self.fetch_page(candidate)
            except WikipediaServiceError:
                failures += 1
                continue

            dedupe_key = str(item.get("title", "")).strip().lower()
            if not dedupe_key:
                failures += 1
                continue
            if dedupe_key in seen_titles:
                continue
            seen_titles.add(dedupe_key)
            items.append(item)

        if not items and failures > 0:
            return {
                "items": [],
                "count": 0,
                "requested_count": requested_count,
                "seed_topic": normalized_seed,
            }

        return {
            "items": items,
            "count": len(items),
            "requested_count": requested_count,
            "seed_topic": normalized_seed,
        }
