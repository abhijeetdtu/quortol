# Blog Writing Best Practices

## Structure Guidelines

### 1. Executive Summary (Required)

**Purpose:** Give readers a quick overview of what they'll learn.

**Requirements:**
- 100-200 words maximum
- State the main argument clearly
- Mention key findings or conclusions
- No technical jargon (write for general audience)

**Example:**
> AI agents are on a revolutionary trajectory to dramatically reduce human workload on repetitive tasks, potentially freeing individuals from "grunt work" and enabling more fulfilling lives. Research indicates task completion capabilities are **doubling every 7 months**, with frontier AI systems reaching 110-minute autonomous task horizons by 2026.

---

### 2. Introduction (Required)

**Purpose:** Set context and hook readers.

**Techniques:**
- Start with a surprising statistic or fact
- Ask a compelling question
- Tell a brief story or anecdote
- Connect to current events

**Length:** 150-300 words

---

### 3. Body Sections (Recommended: 3-5 sections)

**Structure per section:**
```markdown
## Section Title

[2-3 paragraphs of analysis]

### Subsection (if needed)
[Supporting evidence or details]

#### Data Table/Chart
| Metric | Value | Change |
|--------|-------|--------|

> [Key quote or insight]
```

**Tips:**
- Each section should have a clear purpose
- Use evidence to support claims
- Include at least one data point per section
- Vary content types (text, tables, quotes, code)

---

### 4. Implications Section (Required)

**Purpose:** Explain what findings mean in practice.

**Include:**
- Who will be affected?
- What actions should readers take?
- Timeline for changes
- Potential risks or opportunities

---

### 5. Conclusion (Required)

**Requirements:**
- Summarize main points (3-5 bullet points)
- End with a strong closing statement
- No new information in conclusion

---

## Citation Standards

### Primary Sources (Required)

Every claim must trace to:
- Company reports (earnings calls, press releases)
- Academic papers (peer-reviewed studies)
- Government data (Bureau of Labor Statistics, etc.)
- Expert interviews (recorded conversations or quoted statements)

**Format:**
```markdown
- [Source Name], [Date]: [URL]
- Author, "Title," Publication, Year: DOI/URL
- Interview with [Name], [Role], [Date]
```

### Confidence Indicators (Optional but Recommended)

Rate source reliability:
```markdown
**High Confidence:** Peer-reviewed studies, company earnings reports  
**Medium Confidence:** Industry surveys, analyst estimates  
**Low Confidence:** Projections, speculative analysis
```

---

## Data Visualization

### Tables

**When to use:**
- Comparing multiple metrics
- Showing before/after changes
- Presenting structured data

**Requirements:**
- Maximum 5 columns (easy to scan)
- Clear headers with units
- Context in caption: "What this shows"

**Example:**
```markdown
| Metric | Before AI | After AI | Change |
|--------|-----------|----------|--------|
| Issues resolved/hour | 14 | 16 | +14% |
| Cost per resolution | $8-$15 | $0.50-$2 | -60% |
```

### Images/Charts

**When to reference:**
- Complex trends over time
- Comparisons too detailed for text
- Visual proof of argument

**Format:**
```markdown
![Chart description](/api/blog/images/chart_name.png)

*Figure 1: What this chart shows and key insight*
```

**Requirements:**
- Descriptive alt text (for accessibility)
- Informative caption with insight
- Source attribution in caption

---

## Writing Style

### Tone

**Do:**
- Professional but accessible
- Respectful of complexity
- Acknowledge uncertainty ("It is plausible that...")
- Present counterarguments fairly

**Don't:**
- Use overly academic language
- Make definitive claims without evidence
- Ignore limitations or risks
- Sound ideological or biased

### Sentence Structure

**Effective techniques:**
- Vary sentence length (5-30 words)
- Use parallel structure for emphasis
- Ask rhetorical questions (answer immediately)
- Use quotes from authoritative sources

**Example:**
> "Not at the scale that some alarmists predicted. Not at the speed that some optimists hoped. But at a rate that is visible in the data."

### Jargon Management

**First use of technical terms:**
```markdown
> *Mixture-of-experts (MoE): An architecture where different neural network "experts" handle different aspects of a task.*
```

**Keep definitions brief:**
- One sentence maximum
- Focus on what it means, not technical implementation
- Link to further reading if needed

---

## Common Mistakes to Avoid

### ❌ Too Many Statistics in One Paragraph

**Bad:**
> "By 2025, 57% of companies had deployed AI. GitHub reports 30% acceptance rate. Microsoft has 160k organizations. Goldman Sachs estimates $2.9T value."

**Good:**
Break into separate sections:
```markdown
### Current Adoption Rates

57% of companies have deployed AI agents in production (Gartner, 2025).

### Enterprise Scale

Microsoft's Copilot Studio counts 160,000 organizations using the platform.
```

### ❌ Future Projections as Facts

**Bad:**
> "By 2028, agents will handle full work weeks."

**Good:**
> "*Projection based on METR extrapolation: By 2028, agents could handle full work weeks autonomously.* Actual outcomes depend on regulatory decisions and technical breakthroughs."

### ❌ Missing Source Attribution

**Bad:**
> "AI is transforming customer support."

**Good:**
> "AI is transforming customer support—Klarna announced its AI assistant replaced the equivalent of 700 customer service agents (Klarna Q3 2025 earnings call)."

---

## Quality Checklist

Before publishing, verify:

- [ ] Executive summary (100-200 words)
- [ ] Clear introduction hooking readers
- [ ] 3-5 body sections with evidence
- [ ] At least one data table or chart reference
- [ ] Implications/future outlook section
- [ ] Conclusion summarizing main points
- [ ] All claims have citations
- [ ] Future projections marked as estimates
- [ ] No broken image references
- [ ] Read time under 30 minutes

---

*This guide is based on analysis of successful long-form essays and academic journalism standards.*
