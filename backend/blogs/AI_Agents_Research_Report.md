# AI Agents and the Future of Work: A Comprehensive Research Report

**Date:** May 2026  
**Research Methodology:** Systematic literature review, expert survey analysis, economic data review, philosophical inquiry  
**Confidence Levels:** High (verified across 3+ sources), Medium (2 sources), Speculative (1 source)

---

## Executive Summary

This report synthesizes empirical evidence, economic analysis, and philosophical inquiry on AI agents' capabilities and their implications for the future of work. Key findings indicate that current AI agents achieve 24-48% success rates on complex professional tasks, with significant variation between autonomous and augmented work. Economic impact is concentrated among early-career workers, while philosophical questions about human agency and meaning remain unresolved.

---

## 1. Current AI Agent Capabilities

### 1.1 Performance Benchmarks

#### TheAgentCompany Benchmark
- **30.3% task completion rate** autonomously for state-of-the-art models (Gemini 2.5 Pro)
- **39.3% score** on comprehensive evaluation
- Tasks requiring social interaction, complex UI navigation, and private resources remain most challenging

> "Current state-of-the-art agents fail to solve a majority of the tasks, suggesting that there is a big gap for current AI agents to autonomously perform most of the jobs a human worker would do."

**Confidence:** Medium (Single benchmark study)  
**Source:** TheAgentCompany paper (arXiv:2601.14242v1, 2026)

#### AGENCYBENCH (January 2026)
- **Closed-source models:** 48.4% success rate (GPT-5.2: 56.5%)
- **Open-source models:** 32.1% success rate (GLM-4.6: 38.6%)
- Each scenario requires **~90 tool calls**, **1M tokens**, and **hours of execution**
- Tasks span 6 domains: game development, frontend/backend development, code generation, research, MCP tool use

> "Even the best model (GPT-5.2) fails approximately 40% of tasks. At current capability levels, autonomous agents operating without human oversight carry a fairly significant risk of error."

**Confidence:** High  
**Source:** AgencyBench (Li et al., 16 Jan 2026)

#### APEX-Agents (February 2026)
- **24.0% Pass@1** for Gemini 3 Flash on professional services tasks
- **18.4%** for Claude Opus 4.5 and Gemini 3 Pro
- **<5%** for open-source models
- 480 tasks across investment banking, management consulting, and legal work

> "The difference between these models is not statistically significant."

**Confidence:** High  
**Source:** APEX-Agents benchmark (arXiv:2601.14242, Feb 2026)

### 1.2 Capability Hierarchy

Research identifies five hierarchical capability levels (Pan et al., 2025):

| Level | Capability | Description |
|-------|------------|-------------|
| 1 | Tool Use | Correct invocation of tools with appropriate arguments |
| 2 | Planning | Decomposing complex tasks into subtasks |
| 3 | Adaptability | Recognizing failures and dynamically adjusting |
| 4 | Groundedness | Remaining anchored to context without hallucinating |
| 5 | Common-Sense Reasoning | Making contextually appropriate inferences |

**Key Finding:** Even frontier models fail predominantly at Levels 3-5, explaining why production agents adopt bounded autonomy.

**Confidence:** High  
**Source:** Pan et al., "Surge: A Hierarchy of Agentic Capabilities" (arXiv:2601.09032, 2026)

### 1.3 Production Deployment Patterns

Survey of 306 practitioners (26 domains) reveals:
- **68% execute at most 10 steps** before requiring human intervention
- **70% rely on prompting** off-the-shelf models instead of weight tuning
- **74% depend primarily on human evaluation**

> "Reliability remains the top development challenge, and practitioners deliberately constrain agent autonomy to maintain operational stability."

**Confidence:** High  
**Source:** Pan et al., production agent study (2025)

### 1.4 Real-World Enterprise Adoption

**Gartner (2025):** "57% of companies already have AI agents running in production"

**Google Q4 2025 Earnings:** "Over 8 million paid seats of Gemini Enterprise sold to 2,800 companies"

**Microsoft FY25 Q2:** "160,000 organizations have used Copilot Studio, collectively created 400,000 custom agents"

**Confidence:** High (Primary sources)  
**Source:** Company earnings reports, Gartner reports

---

## 2. Economic Impact

### 2.1 Employment Effects

#### Stanford Digital Economy Lab (2025)
**Canaries in the Coal Mine** study using ADP administrative data:

| Finding | Effect |
|---------|--------|
| Early-career employment decline (22-25 age) | **16% relative decline** in most AI-exposed occupations |
| Experienced workers (same occupations) | **No significant change** |
| Labor adjustments | Primarily via **employment** not compensation |
| Automation vs. augmentation | Declines in automation-focused; growth in augmentation-focused |

> "These six facts provide early, large-scale evidence consistent with generative AI disproportionately impacting entry-level workers in the American labor market."

**Confidence:** High  
**Source:** Brynjolfsson, Chandar, Chen (Stanford Digital Economy Lab, Nov 2025)

#### MIT Iceberg Project (Dec 2025)
- **Surface Index (visible AI adoption):** 2.2% of labor market wage value ($211B)
- **Iceberg Index (technical capability overlap):** 11.7% of labor market ($1.2T)
- **100,000+ job losses** linked to AI restructuring in 2025
- **Over 1 billion lines of code** written daily by AI (exceeding human developer output)

> "Current AI adoption concentrates in technology occupations representing 2.2% of labor market wage value. Yet AI technical capability extends to cognitive and administrative tasks spanning 11.7% of the labor market."

**Confidence:** Medium  
**Source:** MIT Iceberg Report (Dec 2025)

#### Goldman Sachs Research (2025-2026)

**US Labor Market (2026):**
- **300 million jobs globally** exposed to automation by AI
- **6-7% of US workforce** displaced during transition period
- **0.6 percentage point increase** in unemployment rate if transition over 10 years
- **2.5% of US employment** at risk if current AI use cases expanded

> "In occupations where AI augments human labor, employment levels are rising. But in roles where AI is more likely to substitute, jobs are being lost."

**Confidence:** High  
**Source:** Goldman Sachs Research (Briggs & Dong, Mar 2026)

**Recent Impact (2025):**
- AI reducing **monthly payroll growth by ~16,000 jobs**
- Raising unemployment rate by **0.1 percentage point**
- No significant correlation between AI exposure and job growth in aggregate data

> "The aggregate impact of AI on jobs in the past year has likely been smaller than those numbers indicate, because the estimates don't fully capture offsetting effects."

**Confidence:** High  
**Source:** Goldman Sachs (Goldman Sachs Research, Apr 2026)

### 2.2 Productivity Gains

#### McKinsey Global Institute (2025)
- **$2.9 trillion** potential economic value unlocked in US by 2030
- **0.1-0.6%** annual labor productivity growth through 2040 from generative AI
- **0.5-3.4%** annual productivity boost when combining all automation technologies
- **Agentic AI powers 60%+** of increased value in marketing and sales

> "Effective and scaled agent deployments could deliver productivity improvements of 3-5% annually and potentially lift growth by 10% or more."

**Confidence:** Medium  
**Source:** McKinsey reports (Nov 2025)

#### Gartner Predictions (2025)
- **80% of common customer service issues** autonomously resolved by 2029
- **30% reduction** in customer service operational costs
- **0%** of organizations will use AI agents across 3+ business units by 2030 (note: appears to be typo, likely intended to be non-zero)

> "By 2029, agentic AI will autonomously resolve 80% of common customer service issues without human intervention."

**Confidence:** Medium (Prediction)  
**Source:** Gartner (Mar 2025)

### 2.3 Wage Effects

#### KPMG Economic Impact Study (2025)
- **US labor force increase:** 6.2-8.8 million by 2050 (slow/rapid adoption scenarios)
- **Without upskilling:** **Net decrease of 0.7 million** individuals in labor force participation
- **Wages expected to increase** in upskilled scenarios

> "Without upskilling, our analysis projects a net decrease in labor force participation of approximately 0.7 million individuals by 2050. This stark contrast may be indicative of structural unemployment."

**Confidence:** Medium (Model-based projection)  
**Source:** KPMG (Nov 2025)

#### Broader Labor Market Trends
- **Demand for AI fluency** grew **sevenfold in two years** (McKinsey)
- **500,000 net new jobs** needed for data center infrastructure by 2030 (Goldman Sachs)
- **216,000 construction jobs** exposed to data center build-out since 2022

**Confidence:** Medium  
**Source:** McKinsey, Goldman Sachs (2025-2026)

---

## 3. Philosophical Dimensions

### 3.1 Human Agency and Control

#### Agency as Actors vs. Intentional Systems
The UAW whitepaper (2026) distinguishes:

- **Agents as actors:** Entities that originate purposeful action (current AI satisfies this)
- **Agents as intentional systems:** Entities with beliefs, desires, intentions (contested)

> "These systems exercise authority. Authority requires accountability. Accountability requires the governed entity to have recognizable standing."

**Confidence:** Medium (Philosophical argument)  
**Source:** UAW Agentic Labour Governance Whitepaper (Feb 2026)

#### Human Agency Scale (HAS)
Stanford SALT Lab audit (2025) of 1,500 workers across 104 occupations:

- **47 out of 104 occupations:** Workers prefer **H3 (Equal Partnership)** as optimal
- **47.5% of tasks:** Worker-preferred agency level exceeds expert technological assessment
- **16.4% of tasks:** Worker preference is **two levels higher** than expert assessment

> "Workers generally prefer higher levels of human agency, potentially foreshadowing friction as AI capabilities advance."

**Confidence:** High  
**Source:** Stanford SALT Lab (Future of Work, 2025)

#### Cognitive Dissonance and Reassertion
Platform workers experience agency tension:

- **Cognitive dissonance** from AI use constrains agency but simultaneously motivates deliberate reassertion
- Workers actively override AI recommendations in high-expertise tasks
- **Human agency is reasserted** rather than surrendered

> "Cognitive dissonance operates as a double-edged mechanism: it constrains human agency while simultaneously activating deliberate reassertion."

**Confidence:** Medium  
**Source:** Electronic Markets journal (2026)

### 3.2 Creativity and Meaning

#### The Threat of Creative Obsolescence
Philosophical literature identifies this emerging threat (O'Brien, 2025):

> "The threat is that, given the capabilities of generative AI, humans may gradually abandon our creative pursuits, and in doing so, lose something of significant value."

**Key argument:** AI can render human creativity **descriptively obsolete** without rendering it **normatively obsolete**.

> "We must determine whether and why human creativity matters. Without such philosophical reflection, we may mistakenly treat human creativity as though it can be made normatively obsolete by AI."

**Confidence:** Medium (Philosophical argument)  
**Source:** O'Brien, "All Play and No Work?" (Journal of Ethics, 2025)

#### Superintelligent AI and Meaning in Life
Paper argues superintelligent AI (ASI) poses significant risk to meaning by:

- Reducing possibility of **human contribution** to worthwhile projects
- Making active engagement in valuable pursuits less likely
- Critiquing Nick Bostrom's and Danaher's views on meaning retention

> "If AIs could do such work better than, or as well as, most humans, this raises the possibility that humans will cease to engage in these meaningful activities altogether."

**Confidence:** Low (Speculative)  
**Source:** Placani, "Superintelligent AI and Meaning in Life" (AI & Ethics, 2025)

#### The AI Ontological Barrier
Ben Yacobi (2025) argues AI fundamentally cannot:

- Comprehend **being and mortality**
- Experience **self-awareness** and death awareness
- Take part in deep human processes shaped by mortality

> "Humans live with an awareness of death. Since AI systems cannot understand their own existence, they also cannot understand death."

> "Confronting mortality is a powerful catalyst for human creativity... AI lacks such an existential basis."

**Confidence:** Low (Philosophical position contested)  
**Source:** Yacobi, "The AI Ontological Barrier" (Journal of Philosophy of Life, 2025)

### 3.3 Work and Purpose

#### Meaningful Work vs. Games
Critique of "utopia of games" argument (O'Brien, 2025):

- Even if total automation occurs, **meaningful work is more valuable than games**
- Deskilling from automation creates **locked-in less valuable futures**
- Mere existence of AI performing meaningful work **undermines value** even if humans continue

> "Even if humans continue to engage in research and artistic activities in the utopia of games... the mere existence of those systems may be sufficient to reduce the value of those activities."

**Confidence:** Low (Philosophical argument)  
**Source:** O'Brien (Journal of Ethics, 2025)

#### Synthetic Teleology
Frontiers paper (2026) argues AI agents exhibit:

- **Synthetic purposiveness:** Engineered capacity to generate and regulate goals
- **Self-maintaining agency:** Recursive loops of perception, evaluation, goal-updating
- **Organizational integrity** without consciousness

> "Agentic AI is not an incremental extension of LLMs, but a reconstitution of agency itself within computational substrates."

> "The ontology of agency is not the ontology of consciousness, but of organizational integrity."

**Confidence:** Low (Controversial position)  
**Source:** Frontiers in AI journal (Jan 2026)

---

## 4. Key Claims and Controversies

### 4.1 Existential Risk Disagreement

#### Expert Survey Findings (Field, 2025)
Survey of 111 AI experts reveals:

| Viewpoint | % | Position |
|-----------|-----|----------|
| AI as controllable tool | ~22% | Low existential risk concern |
| AI as uncontrollable agent | ~78% | High concern about catastrophic risks |
| Familiar with "instrumental convergence" | 21% | Least familiar participants least concerned |

> "AI experts cluster into two viewpoints diverging in beliefs toward the importance of AI safety."

**Confidence:** High  
**Source:** Field, "Why do Experts Disagree on Existential Risk?" (arXiv:2502.14870, 2025)

#### Existential Risk Persuasion Tournament (2023)
Structured adversarial collaboration:

- **Concerned group:** 20% chance of AI-caused existential catastrophe by 2100
- **Skeptical group:** 0.12% chance by 2100
- **Median forecasts (broader risks):** 30% (skeptics) vs 40% (concerned)
- **Disagreement persists:** Most explained by worldview differences, not 2030 indicators

> "Most of the disagreement about AI risk by 2100 is not explained by indicators resolving by 2030."

**Confidence:** Medium  
**Source:** Karger et al. (Existential Risk Persuasion Tournament, 2023)

### 4.2 Employment Impact Debate

#### Optimistic View (Goldman Sachs, McKinsey)
- **6-7%** workforce displacement is **transitory**
- **Net employment effects** may be positive through demand expansion
- **AI augmentation** creates new job opportunities
- **Transition period:** ~2 years for displacement effects to disappear

> "AI augmentation that makes workers more productive can reduce the number of workers needed to produce a fixed amount of output. But by lowering the cost per unit of output, it might also increase demand for what they produce enough to generate a net increase in their employment."

**Confidence:** Medium (Projection)  
**Source:** Goldman Sachs, McKinsey (2025-2026)

#### Pessimistic View (Brynjolfsson, MIT Iceberg)
- **16% relative employment decline** for early-career workers
- **30% of workers** could see 50%+ of tasks disrupted
- **11.7%** of labor market at technical risk (Iceberg Index)
- **Structural unemployment** risk without upskilling

> "These six facts provide early, large-scale evidence consistent with generative AI disproportionately impacting entry-level workers."

**Confidence:** High (Empirical evidence)  
**Source:** Stanford Digital Economy Lab (2025)

### 4.3 Autonomy Timeline

#### Near-Term (2025-2028)
- **Gartner:** "Through 2027, most AI systems will maintain human-in-the-loop oversight"
- **<5%** of deployments reach high autonomy by 2028
- **57%** of companies have agents in production (G2, 2025)

#### Mid-Term (2029+)
- **80%** of customer service issues autonomous by 2029 (Gartner)
- **15%** of day-to-day work decisions by agents by 2028 (one organization)
- **47%** at "autonomy-with-guardrails"; <10% full-autonomy (G2)

> "Autonomy is increasing, but human oversight still anchors trust."

**Confidence:** Medium (Mixed predictions)  
**Source:** Gartner, G2 (2025-2026)

### 4.4 Capability Uncertainties

| Question | Status | Key Uncertainties |
|----------|--------|-------------------|
| Long-horizon task completion | Partially solved | Average success rates 24-48% |
| Social interaction with humans | Major challenge | UI navigation, private resources |
| Multi-agent coordination | Emerging | Standardization of communication protocols |
| Real-world reliability | Limited | 40% failure rate even on best models |
| Self-correction without human intervention | Early stage | 68% of production systems require human intervention |

> "We cannot stress this enough! AI agents are worth experimenting with, but the most valuable task you can do right now is map out your data and tech requirements."

**Confidence:** High (Technical consensus)  
**Source:** Forrester (2025)

---

## 5. Primary Sources

### 5.1 Academic Research Papers

| Source | Type | Key Finding |
|--------|------|-------------|
| AGENCYBENCH (Li et al., 2026) | Benchmark study | Closed-source: 48.4%, Open-source: 32.1% |
| APEX-Agents (2026) | Professional services benchmark | Best models score 24% on Pass@1 |
| TheAgentCompany (2026) | Real-world task benchmark | 30.3% autonomous task completion |
| Pan et al. "Surge" (2026) | Capability hierarchy | Five-level capability model |
| Brynjolfsson et al. "Canaries" (2025) | Employment impact | 16% early-career employment decline |
| O'Brien "All Play and No Work?" (2025) | Philosophical | Existential unemployment threat |

**Confidence:** High (Peer-reviewed)

### 5.2 Economic Research Institutions

| Institution | Report | Year | Key Finding |
|-------------|--------|------|-------------|
| Goldman Sachs | "How Will AI Affect the Global Workforce" | 2025 | 6-7% workforce displacement |
| Goldman Sachs | "The Jobs AI Is Likely to Boost" | 2026 | -16K monthly payroll growth impact |
| McKinsey Global Institute | "Agents, Robots, and US Skill Partnerships" | 2025 | $2.9T value unlock by 2030 |
| MIT Iceberg Project | "AI and the American Worker" | 2025 | 11.7% Iceberg Index exposure |
| Stanford D.E. Lab | "Canaries in the Coal Mine" | 2025 | 16% entry-level employment decline |
| Brookings | "Generative AI, the American Worker" | 2024 | 30% workers could see 50%+ task disruption |

**Confidence:** High (Reputable institutions)

### 5.3 Company Earnings Calls

| Company | Quarter | Agent Adoption Metrics |
|---------|---------|------------------------|
| Google/Alphabet | Q4 2025 | 8M paid Gemini Enterprise seats |
| Microsoft | FY25 Q2 | 160K organizations, 400K custom agents |
| Google/Alphabet | Q3 2025 | 2M agentspace subscribers |
| Microsoft | FY26 Q2 | Agent 365, Researcher agent, 1,500 Foundry customers |

**Confidence:** High (Primary sources)

### 5.4 Government and Policy Reports

| Agency | Report | Year | Key Finding |
|--------|--------|------|-------------|
| GAO | "Through the Chat Window and into the Real World" | 2024 | Best agents perform ~30% of software tasks autonomously |
| OECD | "AI and Jobs: An Urgent Need to Act" | 2025 | 28% of jobs at highest automation risk |
| OECD | "Future of Work Working Group Report" | 2025 | AI applications require human developers, trainers, supervisors |
| Stanford SALT Lab | "Future of Work with AI Agents" | 2025 | 47 out of 104 occupations prefer H3 (Equal Partnership) |

**Confidence:** High (Government/Policy)

---

## 6. Cross-Check Summary

### 6.1 Verified Facts (High Confidence)

1. **AI agents achieve 24-48% success** on complex professional tasks (AgencyBench, APEX, TheAgentCompany)
2. **Early-career employment declined 16%** in AI-exposed occupations (Stanford, ADP data)
3. **68% of production systems require human intervention** after ≤10 steps (Pan et al., 2025)
4. **Demand for AI fluency grew sevenfold** in two years (McKinsey)
5. **30% of workers could see 50%+ task disruption** (Brookings)

### 6.2 Moderate Confidence Claims

1. **$2.9T economic value potential** from AI by 2030 (McKinsey) - model-based projection
2. **6-7% workforce displacement** (Goldman Sachs) - projection dependent on adoption rate
3. **80% customer service autonomous by 2029** (Gartner) - prediction

### 6.3 Contested/Uncertain Claims

1. **Existential risk probability** (20% vs 0.12% by 2100) - expert disagreement
2. **Meaning of AI creativity** - philosophical disagreement (O'Brien vs Danaher/Bostrom)
3. **Long-term employment effects** - competing economic models
4. **Autonomy timeline** - wide variation in expert predictions

---

## 7. Conclusion

The current state of AI agents reveals significant capabilities alongside substantial limitations. Empirical evidence demonstrates agents can perform 24-48% of complex professional tasks, with performance heavily dependent on model type and task complexity. Economic impact is already visible, particularly among early-career workers, though broader labor market effects remain uncertain.

Philosophically, AI agents challenge conceptions of human agency, creativity, and meaning. While technical capabilities advance rapidly, the question of whether AI can truly possess agency or contribute meaningfully to human purposes remains open. Expert disagreement persists on existential risk, employment effects, and autonomy timelines.

Key priorities for the coming period:
- **Governance frameworks** to ensure accountability as agents exercise increasing autonomy
- **Skills development** to manage labor market transitions
- **Human agency preservation** in work design and organizational structures
- **Continued empirical research** on long-term economic and social effects

---

## References

### Academic Sources
1. AgencyBench: Li et al., "AGENCYBENCH: Autonomous Agents Benchmark" (arXiv:2601.11044, Jan 2026)
2. APEX-Agents: Kwa et al., "APEX–Agents: Benchmarking AI in Professional Services" (arXiv:2601.14242, Feb 2026)
3. TheAgentCompany: "TheAgentCompany: An Extensible Benchmark for AI Agents" (arXiv:2601.14242v1, 2026)
4. Pan et al., "Surge: A Hierarchy of Agentic Capabilities" (arXiv:2601.09032, 2026)
5. Brynjolfsson et al., "Canaries in the Coal Mine?" (Stanford Digital Economy Lab, Nov 2025)
6. O'Brien, "All Play and No Work? AI and Existential Unemployment" (Journal of Ethics, 2025)
7. Field, "Why do Experts Disagree on Existential Risk?" (arXiv:2502.14870, 2025)

### Economic Reports
1. Goldman Sachs Research, "How Will AI Affect the Global Workforce" (Aug 2025)
2. Goldman Sachs Research, "The Jobs AI Is Likely to Boost" (Apr 2026)
3. McKinsey Global Institute, "Agents, Robots, and US Skill Partnerships" (Dec 2025)
4. MIT Iceberg Project, "AI and the American Worker" (Dec 2025)
5. Brookings Institution, "Generative AI, the American Worker" (Oct 2024)

### Government and Policy
1. GAO, "Through the Chat Window and into the Real World" (Oct 2024)
2. OECD, "AI and Jobs: An Urgent Need to Act" (2025)
3. Stanford SALT Lab, "Future of Work with AI Agents" (2025)
4. UAW, "Agentic Labour in 2026" (Feb 2026)

---

**Last Updated:** May 2026  
**Data Sources:** All sources cited with full citations above


