# Feasibility Study Workflow

End-to-end process for creating data-driven feasibility studies — from initial concept through market research, operational modeling, financial analysis, risk assessment, and polished prose. Produces rigorous, magazine-style evaluations of speculative or ambitious propositions, grounded in comparative market evidence and transparent about what remains unknown.

## Stages

### Stage 1: Concept Definition & Scope

Clarify the proposition before researching a single number.

- **The proposition**: What exactly is being evaluated? A new product category? A development concept? A business model in a new domain? Define it in one sentence.
- **The core question**: What is the single unanswered question the study exists to answer? ("Is there a market for X?", "Can X be built at Y price point?", "What would it take for X to work?")
- **Tier or gradient analysis**: Is the proposition one point on a spectrum of ambition? Define a gradient (typically 3–5 tiers) from the simplest existing model to the most ambitious hypothetical. Identify which tier the study is actually evaluating — and why that tier, not the others.
- **Domain and constraints**: What industry, geography, regulatory environment, and time horizon bounds the analysis?
- **Comparative precedents**: What existing models, analogues, or adjacent industries can serve as reference points?

**Track progress** with `todowrite` — one todo per stage. Mark each `completed` only after you have verifiable source URLs or concrete analytical output in hand.

**Example from the genre** (from *The Medieval Westworld*):

> The gradient ran from Tier 1 (daytime spectacle: Renaissance Faires) through Tier 2 (overnight immersive: human-staffed 48-hour experience) and Tier 3 (labor colony: medieval survival school) to Tier 4 (AI Westworld: science fiction). The study identified Tier 2 as the realistic frontier — the vacant niche between what exists and what is impossible.

---

### Stage 2: Market Research & Comparable Analysis

Gather the existing market data that establishes whether demand exists. The best argument for a new proposition is the demonstrated health of adjacent ones.

Use `websearch` for:

- **Existing comparable models**: Companies, venues, or experiences that serve a related demand. For each, capture: revenue, attendance, price points, growth trajectory, operational lifespan, ownership structure. Prefer official financial disclosures, court records, economic impact studies, or verified industry reporting.
- **Market sizing**: Total addressable market for the broader category (e.g., "experiential tourism," "live entertainment," "luxury hospitality"). Use government tourism data, industry reports (Statista, IBISWorld, Polaris), and peer-reviewed economic impact studies. Capture the source, methodology, and year — markets are not static.
- **Growth trajectory evidence**: Multi-year data series showing the category expanding. Year-over-year revenue growth, attendance growth, market entry by major players, investment inflows.
- **Grassroots confirmation**: Small-scale successes that demonstrate organic demand independent of marketing spend. Niche festivals, regional operators, crowdfunding campaigns, waitlist data.
- **The ceiling of comparables**: What existing models *cannot* do. Identify the structural limitation they all share — the gap the proposition aims to fill.

**Source types by priority**:

| Priority | Source type | Example |
|----------|-------------|---------|
| Primary | Court-ordered valuations, annual reports, government tourism data | Texas Renaissance Festival $60M sale valuation |
| Primary | Official institutional publications | Glastonbury Abbey visitor figures |
| Primary | Economic impact studies (university or government-commissioned) | Youghal Medieval Festival €863K spin-off |
| Secondary | Verified industry reporting with named sources | NPR, Verge, Quartz — with original documents cited |
| Tertiary | Market research aggregators | Statista, IBISWorld — use for broad sizing only |
| Do not use | Blogspam, Wikipedia-only claims, anonymous revenue estimates | — |

**Rule for comparable selection**: Choose comparables that share at least two of the three dimensions — *price point, duration of experience, or core activity*. Medieval Times (dinner show, $60, 2 hours) is a weaker comparable for an overnight $1,500/night experience than Guédelon (heritage tourism, €12/day, all-day visit). Use both, but be explicit about which dimensions align and which diverge.

---

### Stage 3: Operational Modeling

Model the supply side. This is where most feasibility studies fail — the market case is made, but the operational reality is not stress-tested.

**Construction and capital infrastructure**:
- How long would it *really* take to build? Use real-world precedent projects, not contractor estimates. If period-authentic construction is required, reference actual heritage projects (Guédelon: 27 years and counting; Campus Galli: projected 40 years).
- What is the realistic capital cost for a phased build? Anchor to comparable themed entertainment or hospitality developments, scaled by scope.
- What modern concessions to authenticity are operationally necessary and aesthetically tolerable? (Concealed plumbing, modern kitchens, emergency access roads.)

**Staffing and labor**:
- What staff-to-guest ratio does the proposition require? Calculate at minimum viable, comfortable, and luxury service levels.
- What shift structure is needed for 24-hour or extended-hour operation? Include days off, turnover, and seasonal variation.
- What skill sets are required and how specialized are they? (Heritage craftspeople, character actors, animal handlers, safety personnel.)
- What is the realistic labor pool for the location? Can the local workforce support the required headcount, or must staff be imported?
- Benchmark wages against comparable roles in adjacent industries (theme parks, cruise lines, luxury resorts, theatrical productions).

**Seasonality and weather**:
- How many operational days per year does the climate permit? Reference weather data and comparable seasonal attractions in the target region.
- If indoor alternatives break the illusion, how does the model adapt to off-season?
- What is the revenue impact of a 40% seasonal swing on a fixed cost structure?

**Infrastructure and logistics**:
- Site size and land requirements: what acreage for the built environment, parking, buffer zones, service areas?
- Utilities: power, water, sewage, waste management, internet (if permitted). Cost and feasibility of concealed infrastructure.
- Access: road connectivity, airport proximity, public transit. Guest arrival and departure flows.
- Supply chain: how do food, materials, costumes, and replacement parts reach an operationally remote site?

---

### Stage 4: Financial Pro-Forma

Build a transparent financial model with ranges, not single-point estimates.

**Capital costs (CapEx)**:
- Construction: land acquisition, site preparation, buildings, infrastructure, themed elements
- Concealed modern amenities: HVAC, plumbing, electrical, fire suppression, emergency systems built into period structures
- Vehicles, animals, equipment: stables, livestock, tools, costumes, kitchen equipment
- Pre-opening: recruitment, training, soft-launch phase
- Contingency: 20–30% of hard costs is standard for themed construction
- Reference comparables: scale from known projects. (Pandora — Avatar: $500M. Harry Potter (first phase): $250M. Texas Renaissance Festival forced valuation: $60M.)

**Operating costs (OpEx)**:
- Largest line item first. For labor-intensive propositions, model payroll in detail — use a table:

| Role | Headcount | Annual rate | Total |
|------|-----------|-------------|-------|
| Character actors | 1,500 | $24,000 | $36M |
| Craftspeople | 50 | $45,000 | $2.25M |
| Maintenance | 30 | $40,000 | $1.2M |
| ... | ... | ... | ... |

- Food, beverage, and consumables
- Utilities, insurance, property tax, maintenance reserves
- Marketing and sales (typically 8–15% of projected revenue)
- Management and administrative overhead
- Reserve for narrative refresh (new scripts, costumes, set updates)

**Revenue projections**:
- Price point × capacity × occupancy × operating days = gross revenue
- Model at three occupancy scenarios: conservative (40%), realistic (65%), optimistic (85%)
- Ancillary revenue: food, beverage, merchandise, private events, add-on experiences
- Break-even calculation: how many guests per night at what average spend?
- Payback period: cumulative net cash flow against total CapEx

**Why ranges matter**: The Westworld fictional model priced at $40,000/night. A real medieval Tier 2 model at $2,500/night still pencils — but only at 150 guests, 85% occupancy, with a $36M annual actor payroll. Change any one assumption and the model collapses. Show the math. Let the reader see which assumptions are doing the work.

---

### Stage 5: Risk & Constraint Inventory

List every factor that could prevent the proposition from succeeding — categorized and stress-tested.

**Regulatory and legal**:
- Zoning: does the target jurisdiction have a land-use classification for the proposition? If not, what variance process is required and how long does it take?
- Liability: what activities create tort exposure? (Horses, fire, weapons, livestock, alcohol.) Can they be insured? At what premium? Reference analogous insurance costs from adjacent industries.
- Employment law: minimum wage, overtime, housing for seasonal workers, visa requirements for specialized talent.
- Content constraints: what experiences are legally permissible? (Simulated violence vs. actual harm; sexual content; alcohol service in character.)

**Technical and operational**:
- Is the core technology available today, or does the proposition depend on a not-yet-existing capability? Be ruthless here. (Example: Tier 4 AI Westworld requires human-passing androids at $1.5M/unit. Current state of the art: Boston Dynamics Atlas at $1M+ and 330 pounds. Not close.)
- What is the single point of operational failure? (Weather? A single specialized craftsman? A supply chain for a specific material?)

**Market**:
- Is demand permanent or faddish? Reference the lifespan of comparable propositions. (Medieval Times: 40 years. Renaissance Faires: 50+ years. That is structural durability.)
- What would a recession do to a luxury-priced proposition? Stress-test the occupancy model at 30% of baseline.
- Is the proposition dependent on an IP license or unique talent that could be withdrawn?

**Execution**:
- Has anyone attempted this before? If so, what happened? If not, why?
- What is the hardest single thing about building this proposition, and does the team have experience doing it?

**The constraint table** — organize risks into a structured format for the draft:

| Category | Risk | Likelihood | Impact | Mitigation |
|----------|------|------------|--------|------------|
| Regulatory | No zoning classification exists | High | High | Early PUD variance, target permissive counties |
| Technical | Period construction takes decades | Certain | High | Use modern methods with period finishes |
| Market | Luxury demand is recession-sensitive | Medium | High | Diversified price tiers, local day-trip revenue |
| Operational | Weather limits season | High | Medium | Southern location, covered spaces |

---

### Stage 6: Phased Roadmap

Translate the analysis into a staged implementation plan. Each phase should be designed so that failure in one phase does not cascade into the next.

**Phase structure**:
- **Phase 0 — Due diligence**: Site selection, entitlement, environmental studies, feasibility confirmation. Cost and duration. Exit option: if Phase 0 findings are negative, the project stops here with minimal sunk cost.
- **Phase 1 — Minimum viable proposition**: What is the smallest version of this that proves demand? Open the daytime component before the overnight component. Validate traffic before adding rooms. Capital cost, revenue projection, headcount. Kill criterion: what attendance or revenue trigger justifies proceeding to Phase 2?
- **Phase 2 — Core proposition**: Add the overnight or immersive component that defines the concept. New capital, expanded staffing, revised pricing. Validate at low capacity before scaling.
- **Phase 3 — Full vision**: Expand to full thematic ambition. Live within the operating cash flow generated by Phases 1 and 2. No new external capital required — or if required, justified by demonstrated unit economics.

**For each phase**, specify:
- Duration
- Capital cost (with range)
- Operational headcount
- Revenue projection
- Critical dependency (what must be true for this phase to work)
- Kill criterion (the metric that determines whether to proceed or abandon)

**Anchor to a real-world valuation** when one exists: "The Texas Renaissance Festival, a seasonal Tier 1 attraction with permanent structures and 500,000+ annual visitors, was valued at $60 million in a 2024 forced sale. That is the best available proxy for what a mid-scale attraction is actually worth."

---

### Stage 7: Open Questions & Honest Verdict

The most important section. A feasibility study that ends with certainty is not credible. End with what the analysis cannot settle.

**What is knowable**:
- The market exists (supported by comparables and trend data)
- The operational model pencils (at specific assumptions made explicit)
- The capital requirement is in a defined range
- The risks are identifiable and categorizable

**What remains unknown**:
- The critical unknown that determines success or failure. (For the medieval Westworld: whether a permanent experience can sustain year-round quality at luxury price points. The SXSW activation worked because it was three days. A permanent park has no closing night.)
- Assumptions that, if wrong, change the conclusion entirely. (Occupancy rate. Labor availability. Insurance market evolution.)
- Questions that cannot be answered without building Phase 1. (Will guests really surrender their phones? Will the weather cooperate? Will the local community support or oppose?)

**The verdict framework**:
- Is the proposition *feasible*? (Can it be built and operated with current technology and known costs?)
- Is it *viable*? (Can it generate a return on capital comparable to alternative investments in the same risk class?)
- Is it *desirable*? (Will enough people pay enough money at the required price point?)
- The verdict does not need to be uniform across all three. A thing can be feasible and viable but not desirable. Or desirable and viable but not feasible.

**Formatting for the draft**: Close with a single, contained section that acknowledges the limits of the analysis. A strong ending does not resolve the tension — it names it. (From the exemplar: *"The village could be built. The harder question is whether it can be kept alive."*)

---

### Stage 8: Drafting & Production

Write the feasibility study as a magazine-style feature under `backend/blogs/`.

**Structure**:
- **Lede** — A vivid, scene-based opening that dramatizes the question. Show the closest existing version of the proposition. Start with a real event, a real place, a real moment of built wonder. (From the exemplar: the SXSW Sweetwater activation — a 3-day Westworld that existed and then vanished.)
- **Nut graf** — The core question and the market heft in one paragraph. This is where the market sizing lands. Use the biggest number first.
- **Thematic sections** — Each anchored to specific primary sources with inline citations as raw URLs.
  - The market that already exists (comparables)
  - The gradient (tiers of ambition)
  - The construction problem (operational reality)
  - The operating model (financial modeling)
  - The hardest limits (risks and constraints)
  - The phased roadmap
  - The open question
- **Closing** — A return to human scale. A single image, a single unresolved tension. No false resolution.

**Every factual claim** must link directly to its primary source. No endnotes — inline Markdown links.

**Visuals and photographs**:
- Use `websearch` to find relevant photographs of comparable sites, spaces, and people.
- Fetch each image source page — not just the image URL. Record photographer, date, location, license/usage terms.
- Prefer images from institutional sources, wire services (NPR, Getty, Reuters), Wikimedia Commons (with verified CC licensing), or licensed news media.
- Place images after the paragraph that introduces their subject. Use inline captions with credit.
- Path convention: `](/api/blog/images/{slug}_{descriptor}.jpg)`

**Image sourcing checklist per image**:
- [ ] Source page fetched and read
- [ ] Photographer or institution identified
- [ ] Date and location captured
- [ ] License or usage terms verified
- [ ] Caption written: what the image shows, where, when, and by whom
- [ ] Why this image matters to the story

**Custom charts (data_guy)**:
Use the `data_guy` subagent to create accompanying data visualizations. The prompt must include:

- Exact data series (year/value pairs) with source attribution
- Chart type (line, bar, horizontal bar)
- Styling requirements (1200×720 px, 150 DPI, colorblind-safe palette, no label overlap, source line)
- Output path: `backend/blogs/images/{slug}_{chart_name}.png`
- Script path: `backend/blogs/scripts/chart{N}_{slug}_{chart_name}.py`

**Prose polish (oscar_wilde)**:
Use the `oscar_wilde` subagent to rewrite the article. The prompt must instruct:

- Preserve all facts, numbers, dates, names, URLs, citations exactly
- Preserve all section headings
- Preserve the `---` divider and source disclaimer
- Apply the Wildean voice: epigrammatic, paradoxical, elegant, amused
- Embed images at the correct relative path

**Image path verification**:
After chart generation and Wilde rewrite, verify image paths match the repo convention:

```
](/api/blog/images/{filename}.png)
```

NOT `](images/...` or `](./images/...`. Run `grep` on a known-good blog to confirm the pattern before finalizing.

---

### File Locations

| Asset | Path |
|-------|------|
| Feasibility study | `backend/blogs/{slug}.md` |
| Chart PNGs | `backend/blogs/images/{slug}_{name}.png` |
| Chart scripts | `backend/blogs/scripts/chart{N}_{slug}_{name}.py` |
| Photographs | `backend/blogs/images/{slug}_{descriptor}.{jpg,png}` |

---

### Source Integrity Checklist

- [ ] Every number in the article maps to a primary or verified secondary source URL
- [ ] Market sizing numbers include the source's methodology and year
- [ ] Comparable models cite verifiable revenue, attendance, or valuation data — not anonymous estimates
- [ ] URLs are direct to the original dataset, report, or article (not a news write-up of a write-up)
- [ ] Government data: BLS via FRED, Census Bureau, NPS, state tourism economics reports, EDA
- [ ] Academic: peer-reviewed journals via DOI or institutional repository
- [ ] Institutional: Main Street America, Heartland Forward, university economic impact studies
- [ ] No tertiary aggregators, no blogspam, no Wikipedia as a primary source
- [ ] Financial projections state their assumptions explicitly and include ranges
- [ ] Risk assessments are categorized and sourced (insurance costs, legal precedents, weather data)
- [ ] Phased roadmap includes kill criteria for each phase

---

### Quality Gates (checklist)

- [ ] Proposition is defined: one sentence, one core question, one tier
- [ ] Market case is built from at least 3 independent comparables with verified data
- [ ] Operational model includes construction timeline, staffing plan, and seasonal analysis
- [ ] Financial pro-forma has CapEx, OpEx, revenue at 3 occupancy scenarios, and break-even
- [ ] Risk inventory has at least 5 entries with likelihood, impact, and mitigation
- [ ] Phased roadmap has 3–4 phases with kill criteria
- [ ] Open questions section names at least one assumption that, if wrong, changes the conclusion
- [ ] Every factual claim has an inline URL to a primary or verified secondary source
- [ ] Images sourced: captions, credits, dates, license terms all recorded
- [ ] Charts generated (if applicable): data_guy prompt specifies exact series and source attribution
- [ ] Prose polished: oscar_wilde applied with preservation verification
- [ ] Image path convention verified with grep against a known-good blog
- [ ] File locations match the repo convention
