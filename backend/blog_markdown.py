from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re


BLOGS_DIR = Path(__file__).resolve().parent / "blogs"
SERIES_DIR = BLOGS_DIR / "series"


@dataclass(frozen=True)
class BlogMarkdownDocument:
    path: Path
    title: str
    slug: str
    excerpt: str
    content: str
    tags: list[str]
    published_at: datetime
    updated_at: datetime
    has_explicit_published_at: bool
    has_explicit_updated_at: bool


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return slug.strip("-")


def iter_blog_markdown_files(blogs_dir: Path = BLOGS_DIR) -> list[Path]:
    series_dir = blogs_dir / "series"
    top_level = blogs_dir.glob("*.md")
    series_posts = series_dir.rglob("*.md") if series_dir.exists() else []
    return sorted([*top_level, *series_posts])


def default_slug_for_path(path: Path, blogs_dir: Path = BLOGS_DIR) -> str:
    relative = path.relative_to(blogs_dir)
    if relative.parent == Path("."):
        return slugify(path.stem)
    without_suffix = relative.with_suffix("")
    return slugify(str(without_suffix).replace("\\", "/"))


def derive_excerpt(content: str, max_len: int = 220) -> str:
    for paragraph in content.split("\n\n"):
        cleaned = paragraph.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        single_line = " ".join(cleaned.split())
        if len(single_line) <= max_len:
            return single_line
        return single_line[: max_len - 3].rstrip() + "..."
    return ""


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    raw = value.strip().strip('"').strip("'")
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError:
        pass

    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%B %Y", "%b %Y"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue

    return None


def extract_date_from_body(body: str) -> datetime | None:
    body_head = "\n".join(body.splitlines()[:40])
    candidates = [
        r"\*\*Date:\*\*\s*([A-Za-z]+\s+\d{1,2},\s+\d{4}|[A-Za-z]+\s+\d{4})",
        r"\*Published:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})\*",
        r"\*\s*By[^\n|]*\|\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})\*",
    ]
    for pattern in candidates:
        match = re.search(pattern, body_head, flags=re.IGNORECASE)
        if not match:
            continue
        parsed = parse_datetime(match.group(1))
        if parsed:
            return parsed

    return None


def parse_file_mtime(path: Path) -> datetime | None:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(
            tzinfo=None
        )
    except OSError:
        return None


def parse_tags(raw_tags: str | None) -> list[str]:
    if not raw_tags:
        return []
    if "\n" in raw_tags:
        return [
            line.strip().lstrip("-").strip().strip('"').strip("'")
            for line in raw_tags.splitlines()
            if line.strip().startswith("-")
        ]
    if raw_tags.startswith("[") and raw_tags.endswith("]"):
        raw_tags = raw_tags[1:-1]
    return [tag.strip().strip('"').strip("'") for tag in raw_tags.split(",") if tag.strip()]


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    metadata: dict[str, str] = {}
    body = text

    frontmatter_match = re.match(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?", text, flags=re.DOTALL)
    if not frontmatter_match:
        return metadata, body

    frontmatter = frontmatter_match.group(1)
    body = text[frontmatter_match.end() :]
    lines = frontmatter.splitlines()
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        if ":" not in line:
            idx += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key == "tags" and value == "":
            list_lines = []
            idx += 1
            while idx < len(lines) and lines[idx].strip().startswith("-"):
                list_lines.append(lines[idx].strip())
                idx += 1
            metadata[key] = "\n".join(list_lines)
            continue
        metadata[key] = value
        idx += 1

    return metadata, body


def parse_markdown_file(path: Path, blogs_dir: Path = BLOGS_DIR) -> BlogMarkdownDocument:
    text = path.read_text(encoding="utf-8")
    metadata, body = split_frontmatter(text)

    title = metadata.get("title")
    if not title:
        for line in body.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
    if not title:
        title = path.stem.replace("-", " ").replace("_", " ").title()

    slug = metadata.get("slug") or default_slug_for_path(path, blogs_dir=blogs_dir)
    excerpt = metadata.get("excerpt") or derive_excerpt(body)
    tags = parse_tags(metadata.get("tags", ""))
    explicit_published_at = (
        parse_datetime(metadata.get("published_at"))
        or parse_datetime(metadata.get("date"))
        or extract_date_from_body(body)
    )
    file_mtime = parse_file_mtime(path)
    published_at = explicit_published_at or file_mtime or datetime.utcnow()
    explicit_updated_at = parse_datetime(metadata.get("updated_at"))
    updated_at = explicit_updated_at or published_at

    return BlogMarkdownDocument(
        path=path,
        title=title,
        slug=slug,
        excerpt=excerpt,
        content=body.strip(),
        tags=tags,
        published_at=published_at,
        updated_at=updated_at,
        has_explicit_published_at=explicit_published_at is not None,
        has_explicit_updated_at=explicit_updated_at is not None,
    )


def markdown_to_spoken_text(markdown: str) -> str:
    text = markdown.replace("\r\n", "\n")
    text = re.sub(r"```[\s\S]*?```", "\nCode example omitted.\n", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<img[^>]*alt=[\"']([^\"']*)[\"'][^>]*>", r"\1", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    text = re.sub(r"^\s{0,3}[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}(#{1,6})\s+(.*)$", lambda match: f"\nSection: {match.group(2).strip()}\n", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "• ", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "• ", text, flags=re.MULTILINE)

    lines: list[str] = []
    table_buffer: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if table_buffer:
                lines.append(_flatten_table_rows(table_buffer))
                table_buffer = []
            lines.append("")
            continue
        if "|" in line and line.count("|") >= 2:
            if re.fullmatch(r"[\|\-\:\s]+", line):
                continue
            table_buffer.append(line)
            continue
        if table_buffer:
            lines.append(_flatten_table_rows(table_buffer))
            table_buffer = []
        lines.append(line)

    if table_buffer:
        lines.append(_flatten_table_rows(table_buffer))

    normalized = "\n".join(lines)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    normalized = re.sub(r"(?m)^\s*•\s*", "- ", normalized)
    return normalized.strip()


def _flatten_table_rows(rows: list[str]) -> str:
    flattened: list[str] = []
    for row in rows:
        cells = [cell.strip() for cell in row.strip("|").split("|") if cell.strip()]
        if cells:
            flattened.append(", ".join(cells))
    if not flattened:
        return ""
    return "Table: " + " ; ".join(flattened)
