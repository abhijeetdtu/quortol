# Blog Article Workflow

End-to-end process for creating data-driven feature articles with primary-source research, custom charts, and prose polish.

## Stages

### 1. Research sweep

Use `websearch` to gather primary sources only — government datasets (BLS, Census, FRED, NPS), peer-reviewed academic papers, official institutional reports. No secondary or tertiary aggregation. Capture the URL, title, publisher, and key data points from each source.

**Track progress** with `todowrite` — one todo per research category. Mark each `completed` only after you have verifiable source URLs in hand.

### 2. Direction check

Present the research findings to the user with `question`. Offer options for article format (feature, brief, explainer, case study), visual treatment (charts only, photos only, mixed, none), and draft approach (outline first, full draft, short brief). Let the user decide before proceeding.

### 3. Full draft

Write the magazine-style article into a `.md` file under `backend/blogs/`. Use the structure:

- **Lede** — sensory, scene-based opening
- **Nut graf** — the economic/cultural heft in a single paragraph
- **Thematic sections** — each anchored to specific primary sources with inline citations as raw URLs
- **Closing** — a return to the human scale

Every factual claim must link directly to its primary source. No endnotes — inline Markdown links.

### 4. Custom charts (data_guy)

Use the `data_guy` subagent to create accompanying data visualizations. The prompt must include:

- Exact data series (year/value pairs) with source attribution
- Chart type (line, bar, horizontal bar)
- Styling requirements (1200×720 px, 150 DPI, colorblind-safe palette, no label overlap, source line)
- Output path: `backend/blogs/images/{slug}_{chart_name}.png`
- Script path: `backend/blogs/scripts/chart{N}_{slug}_{chart_name}.py`

### 5. Prose polish (oscar_wilde)

Use the `oscar_wilde` subagent to rewrite the article. The prompt must instruct:

- Preserve all facts, numbers, dates, names, URLs, citations exactly
- Preserve all section headings
- Preserve the `---` divider and source disclaimer
- Apply the Wildean voice: epigrammatic, paradoxical, elegant, amused
- Embed images at the correct relative path (see step 6)

### 6. Image paths

After chart generation and Wilde rewrite, verify image paths match the repo convention. Other blogs in this repo use:

```
](/api/blog/images/{filename}.png)
```

NOT `](images/...` or `](./images/...`. Run `grep` on a known-good blog to confirm the pattern before finalizing.

### 7. File locations

| Asset | Path |
|-------|------|
| Article | `backend/blogs/{slug}.md` |
| Chart PNGs | `backend/blogs/images/{slug}_{name}.png` |
| Chart scripts | `backend/blogs/scripts/chart{N}_{slug}_{name}.py` |

### Source integrity checklist

- [ ] Every number in the article maps to a primary source URL
- [ ] URLs are direct to the original dataset or paper (not a news write-up)
- [ ] Government data: BLS via FRED, Census Bureau, NPS, state tourism economics reports
- [ ] Academic: peer-reviewed journals (JCR, JORT, etc.) via DOI or institutional repository
- [ ] Institutional: Main Street America, Heartland Forward, university research (Iowa State, etc.)
- [ ] No tertiary aggregators, no blogspam, no Wikipedia
