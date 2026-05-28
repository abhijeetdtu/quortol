# Scaling the Harness: The Quiet Paradigm Shift in AI Agent Engineering

**May 27, 2026**

In the third week of May 2026, Shangding Gu, a researcher at UC Berkeley, posted a paper to arXiv that most AI engineers, in their haste to admire the next model, found time to overlook. [From Model Scaling to System Scaling: Scaling the Harness in Agentic AI](https://arxiv.org/abs/2605.26112) made a claim that felt, at first, like academic boundary-drawing: the kind of disciplinary gesture that fields make when they sense they are about to matter. Future progress in agentic AI, Gu argued, would depend as much on system design as on stronger foundation models. The paper proposed a formal framework of six interacting components — reasoning, memory, context construction, skill routing, orchestration, governance — and named their combination an *agent harness*.

It appeared on a Monday. By Wednesday, a separate team at the University of Hong Kong and Beijing Normal University had posted [AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents](https://arxiv.org/abs/2605.13357), defining an H0–H3 harness ladder that lets researchers ablate runtime support the way biologists ablate genes. A survey from multiple Chinese institutions, [Agent Harness for Large Language Model Agents: A Survey](https://www.preprints.org/manuscript/202604.0428), had already formalized the harness as a six-component tuple (E, T, C, S, L, V) and mapped 110+ systems against it. A fifth paper, [Code as Agent Harness](https://arxiv.org/abs/2605.18747), arrived three days later, as though to remove any doubt that something was in the air.

This was not coordination. It was convergence. After three years of building AI agents that mostly failed in production, the engineering community had independently arrived at the same question: what is the system around the model, and why has it suddenly become the binding constraint on performance?

---

## The Problem That Wasn't the Model

The standard story of AI agent development in 2024 and 2025 ran as follows: agents failed because the models were not good enough. Swap in a smarter model — GPT-5, Claude Opus 4, Gemini 3.0 — and the agent would stop getting confused, stop losing context, stop making on the tenth step the same error it had corrected on the third.

That story has begun to look rather unreliable against the data.

By early 2026, according to [KXN Technologies' survey](https://kxntech.com/global/en/research/state-of-agentic-ai-2026/) of 312 enterprise AI decision-makers, 67% of organizations had moved beyond agent pilots into production — up from 31% in 2024. Those that reached production reported serious returns: a median first-year net saving of $2.4 million, rising to $4 million for organizations running three or more concurrent agent workflows. The [Datadog 2026 State of AI Engineering report](https://newclawtimes.com/articles/datadog-2026-state-ai-engineering-agent-framework-adoption-doubles/) found agent framework adoption had nearly doubled year-over-year, from 9% of organizations in early 2025 to 18% by early 2026.

But the failure rate accompanying this growth was brutal. [AgentScout's analysis](https://agentscout.live/tech/ai-agents/insight/multi-agent-orchestration-22-percent-threshold/) of enterprise data from Digital Applied, Gartner, and McKinsey found that 88% of AI agent pilots never reach production — double the failure rate of traditional IT projects. Among the 78% of enterprises running agent pilots, only 14–15% achieve production scale. The [Databricks 2026 State of AI Agents report](https://learnagentic.substack.com/p/327-growth-in-multi-agent-workflows), drawing on anonymized data from over 20,000 organizations including 60% of the Fortune 500, found that multi-agent workflow usage had grown 327% between June and October 2025 alone, yet most of those deployments sat in the uncomfortable zone between "interesting experiment" and "reliable system."

The pattern across every data source was the same. Organizations that deployed better models did not necessarily deploy better agents. Organizations that deployed better infrastructure — observability, governance, evaluation tooling — did. Databricks found that companies using AI governance systems deployed 12 times more AI projects to production. Companies using evaluation tools deployed nearly 6 times more.

This is the empirical basis for what the academic papers formalized in May 2026: the model is not the bottleneck. The harness is.

---

## What Exactly Is a Harness?

The term "agent harness" emerged independently across at least five research groups in the first half of 2026, each converging on the same essential insight. An agent is not a model plus a prompt. An agent is a *system* — and the part of that system that is not the model is the harness.

The most comprehensive formalization comes from the survey [Agent Harness for Large Language Model Agents](https://www.preprints.org/manuscript/202604.0428), which defines an agent execution harness as a six-component tuple:

- **Execution Loop (E):** The observe-think-act cycle, termination conditions, error recovery
- **Tool Registry (T):** Typed tool catalog, routing, monitoring, schema validation
- **Context Manager (C):** What enters the context window, compaction, retrieval
- **State Store (S):** Persistence across turns and sessions, crash recovery
- **Lifecycle Hooks (L):** Authorization, logging, policy enforcement, instrumentation
- **Evaluation Interface (V):** Action trajectories, intermediate states, success signals

Zhong and Zhu, in [AI Harness Engineering](https://arxiv.org/abs/2605.13357), extend this to eleven component responsibilities: task specification, context selection, tool access, project memory, task state, observability, failure attribution, verification, permissions, entropy auditing, and intervention recording. Their central contribution is the H0–H3 harness ladder, a controlled-ablation framework that lets researchers expose progressively more runtime support to an agent while holding the model fixed. At H0, the agent receives only a task description and repository files — the baseline that most benchmarks still use. At H3, the agent has access to deterministic behavioral check registries, bug-reproduction protocols, failure-attribution frameworks, and structured verification report templates. The authors show that the same model, placed on different rungs of this ladder, produces qualitatively different evidence packages — and that H3-level support converts a working patch into a verifiable, attributable, maintainable change.

Gu's [Scaling the Harness](https://arxiv.org/abs/2605.26112) reframes the problem at the highest level of abstraction: agent performance over a horizon H is a function of reasoning quality, memory quality, context-construction quality, skill-selection quality, orchestration quality, and governance quality. Model scaling primarily improves reasoning; system scaling improves everything else. The paper identifies three bottlenecks — context governance, trustworthy memory, dynamic skill routing — and argues that each is now more limiting than model capability for long-horizon agents.

[Agentic Harness Engineering](https://arxiv.org/html/2604.25850v2) demonstrates the principle empirically: ten iterations of an observability-driven evolution loop lifted pass@1 on Terminal-Bench 2 from 69.7% to 77.0%, surpassing the human-designed Codex-CLI baseline at 71.9%. The evolved harness transferred without re-evolution to SWE-bench-verified, producing gains at 12% fewer tokens than the seed harness.

These are not theoretical papers in the usual sense. They are engineering frameworks that give a name to a layer of the stack that practitioners have been building by instinct for two years.

---

## The Framework Landscape, By the Numbers

While academics formalized the harness as an object of study, the engineering community had already been building production harnesses under the name of "agent frameworks." Three dominate the landscape in 2026, and their benchmark data tells a pointed story about where the field is heading.

**LangGraph** (LangChain's graph-based state machine) leads on raw performance and production readiness. PyPI data shows it averaging over 51 million monthly downloads as of May 2026 — roughly 1.3 million per day — across versions 1.1.0 through 1.2.0. The [PyPI page](https://pypi.org/project/langgraph/) confirms 51,040,708 downloads in the last month at time of measurement. It has been deployed at BlackRock, JPMorgan, LinkedIn, Uber, Replit, and Elastic. Independent benchmarks from [AI Agent Engineering](https://ai-agent-engineering.org/news/ai-agent-frameworks-benchmarked-langchain-vs-crewai-vs-autogen-in-2026-the-numbers-that-actually-matter) report its typical latency at 200–500ms per query, with 12,400 tokens consumed per query and a cost of $0.18 per query at GPT-4o pricing. Its production uptime benchmarks at 94%.

**CrewAI** (role-based crews) leads on developer velocity. GitHub data shows 51,380 stars as of May 2026, with 7,103 forks. The [Presenc AI GitHub rankings](https://presenc.ai/research/ai-agent-framework-github-rankings-2026) place it at #8 among all agent frameworks by stars. CrewAI's time-to-working-system is the best of any serious framework: teams report shipping a working pilot in 2–3 weeks on average, according to [Bananalabs' analysis](https://bananalabs.io/blog/langchain-vs-crewai-vs-autogen). The same benchmarks show CrewAI at roughly $0.12 per query and 14,000 tokens per query — the cheapest option by raw cost — but with a lower production success rate of 89%.

**AutoGen** (Microsoft's conversational framework) leads on multi-agent collaboration for complex reasoning tasks. It holds 58,025 GitHub stars, though its last stable release was September 2025 — six months of silence from a Microsoft-backed project, as [agntdev](https://agntdev.com/langchain-vs-crewai-vs-autogen-2026-honest-comparison/) notes. AutoGen's token consumption is the highest of the three at 24,200 tokens per query, and its latency runs 2–5 seconds. Cost per query hits $0.35.

![AI agent framework benchmarks across four key metrics — LangGraph leads on latency and success rate, CrewAI is the cheapest per query, AutoGen consumes the most tokens and has the highest latency. Source: AI Agent Engineering (March 2026).](/api/blog/images/scaling-the-harness_benchmark_comparison.png)

But Microsoft's internal benchmarks show 25% productivity gains from AutoGen-powered workflows, because the iterative multi-turn conversation catches errors that single-pass systems miss.

The aggregated [Presenc AI ranking](https://presenc.ai/research/ai-agent-framework-github-rankings-2026) of the 25 highest-starred agent frameworks tells a broader story about where attention is flowing. n8n (a no-code workflow tool predating the LLM era) leads with 187,791 stars, suggesting that many "agent" workloads are, in truth, workflow automation with LLM nodes attached. AutoGPT sits at 184,295 stars — mostly historical, accumulated in its first six months. LangChain at 136,707 stars is the largest pure-agent repository, though the organization's LangGraph repo has grown to 32,027 stars. The fastest riser is browser-use at 93,857 stars in roughly 18 months — a browser-automation framework that has outpaced every 2023 launch except LangChain itself.

![Top AI agent frameworks by GitHub stars as of May 2026 — n8n leads at 187K stars, with LangChain the largest pure-agent framework at 136K. Source: Presenc AI, GitHub public API, May 2026.](/api/blog/images/scaling-the-harness_github_stars.png)

[Rize's adoption-trend analysis](https://rize.io/blog/ai-adoption-trends-2024-2026) converts these star counts into velocity: AI coding tools add 3,100 stars per week across eight major projects, agent frameworks add 1,700 per week, and observability tools add 650 per week — the fastest-growing category by percentage. The shift from agent-building (slowing) to agent-monitoring (accelerating) signals that the field is moving from experimentation into infrastructure management.

---

## The Three Bottlenecks

If the academic and engineering communities agree on one thing, it is that the hard problems of agent reliability are now systems problems, not model problems. Gu's paper names three:

**Context governance.** The problem is not context window size. It is relevance, compactness, traceability, and freshness. A model with a 200K-token context window does not automatically attend to the right 2,000 tokens. [Research on context dilution](https://arxiv.org/abs/2605.26112) shows that token salience is driven by position, not content — models prefer evidence at the start or end of their context window and neglect the middle. The system move, Gu argues, is to treat each turn's context as the output of a selection policy: weight semantic relevance, penalize verbosity against a token budget, prefer recently validated content, record provenance.

**Trustworthy memory.** Memory in agent systems has a characteristic failure mode the paper calls *stale-but-confident*. A note written to memory ("the data loader is defined in utils/loader.py") can be correct at write time and flatly wrong after a refactor, yet semantic search still ranks it highly. The system move is to make trust a runtime decision, not a stored property: weight a staleness penalty alongside any relevance score, treat retrieved content as a hypothesis until re-checked against the live environment. Claude Code's CLAUDE.md hybrid — persistent project context combined with just-in-time glob and grep primitives — illustrates the pattern: durable memory without periodic verification accumulates undetected drift; environment-only search without distilled priors discards every prior verification.

**Dynamic skill routing.** As agents accumulate more specialized skills and subagents, the bottleneck shifts from having capabilities to dispatching them correctly. The failure mode is *confident-but-unchecked*: a specialized subagent returns plausible output that no downstream layer validates. The open research direction, Gu argues, is to treat routing as a learned policy with verification at every step — the analogue of scheduling in operating systems, where raw capacity exists but useful work depends on allocating it to the right pathway at the right time.

The same three bottlenecks surface in the [HarnessAudit framework](https://arxiv.org/abs/2605.14271), which evaluates ten harness configurations across frontier models and three multi-agent frameworks. The authors find that task completion is misaligned with safe execution, violations accumulate with trajectory length, and most violations concentrate in resource access and inter-agent information transfer. Multi-agent collaboration expands the safety risk surface; harness design sets the upper bound of safe deployment.

---

## The Pilot-to-Production Chasm

The most striking single number in the enterprise data is the 88% pilot-to-production failure rate. To understand why agents fail at production scale, one must examine what the successful 12% do differently.

The [Databricks report](https://learnagentic.substack.com/p/327-growth-in-multi-agent-workflows) found that technology companies are building 4 times more multi-agent systems than any other industry. The [KXN survey](https://kxntech.com/global/en/research/state-of-agentic-ai-2026/) found that 78% of enterprises now require human-in-the-loop validation for Tier 2 and above decisions, and ISO 42001 adoption — the international standard for AI Management Systems — has accelerated sharply, with 31% of respondents holding certification and 47% pursuing it.

The [Belitsoft/Gartner forecast](https://www.financialcontent.com/article/abnewswire-2026-4-8-belitsoft-releases-ai-agent-development-forecast-2026-40-of-enterprise-applications-to-include-task-specific-agents-by-year-end) predicts that 40% of enterprise applications will embed task-specific AI agents by the end of 2026, up from less than 5% in 2025. The [CallSphere analysis](https://callsphere.ai/blog/enterprise-ai-agents-production-72-percent-global-2000-beyond-pilots-2026.md) reports that 72% of Global 2000 companies have moved at least one agent system from pilot to full production, with a median timeline of 4–6 months from pilot approval to deployment.

The critical path, every report agrees, is not the AI development. It is the surrounding infrastructure: observability, security review, compliance approval, and integration with existing systems. The teams that begin with observability and security in the pilot phase cut the timeline roughly in half.

This is the practical meaning of harness engineering. It is the work of building the layer that turns a model's latent capability into a governed, auditable, verifiable production system. The 88% failure rate is not a model failure rate. It is a harness failure rate.

---

## The Emerging Science of Harness Engineering

The convergence of the May 2026 papers suggests that agent harness engineering is becoming a distinct technical discipline with its own vocabulary, its own evaluation methods, and its own research agenda.

The survey paper proposes a [Harness Completeness Matrix](https://www.preprints.org/manuscript/202604.0428) that maps which of the six harness components each system implements, enabling direct comparison across heterogeneous agent systems. It identifies nine open technical challenges where current research provides partial solutions but no production-grade infrastructure: formal security models, cross-harness portability, protocol interoperability (MCP/A2A), context economics at 1M+ tokens per task, Byzantine fault tolerance in multi-agent systems, and compositional verification.

[NLAH — Natural-Language Agent Harnesses](https://arxiv.org/abs/2603.25723) proposes that harness policy itself can be externalized as executable natural-language documents: editable text files that describe run-level harness policy, interpreted by a shared runtime. Across coding, terminal-use, and computer-use benchmarks, NLAH-executed harnesses achieve comparable task outcomes to code-based realizations while exposing much shorter static policies.

The [AHE framework](https://arxiv.org/html/2604.25850v2) introduces observability-driven evolution: a three-agent architecture where an Evolve Agent modifies harness components, an Agent Debugger produces layered evidence from trajectory logs, and a change manifest pairs every edit with a self-declared prediction verified against the next round's outcomes. The results — 77.0% pass@1 on Terminal-Bench 2, surpassing human-designed baselines — suggest that harness evolution via structured feedback can outpace manual harness design.

What these approaches share is a commitment to making the harness a *reportable scientific object*. The [HARNESSCARD proposal](https://www.preprints.org/frontend/manuscript/969cc3d9a5271168ae0d40072f261f0c/download_pub) — a lightweight reporting artifact that discloses the base model, control artifacts, runtime policy, action substrate, feedback stack, governance layer, and evaluation protocol — captures the ambition. The bar for "we built an agent" is shifting. It is no longer enough to name the model. The harness must be named too.

---

## The Last Bottleneck

What does this mean for someone building an agent system in mid-2026? The practical recommendations are surprisingly consistent across the benchmark comparisons and enterprise surveys.

[Bananalabs](https://bananalabs.io/blog/langchain-vs-crewai-vs-autogen) recommends LangGraph for production, CrewAI for speed, AutoGen for research — but notes that a single recommendation is almost always wrong. [AI Agent Engineering](https://ai-agent-engineering.org/news/ai-agent-frameworks-benchmarked-langchain-vs-crewai-vs-autogen-in-2026-the-numbers-that-actually-matter) offers a decision framework: choose LangGraph if your primary constraint is latency or integration breadth; choose CrewAI if your primary constraint is time-to-production or cost; choose AutoGen if your primary constraint is output quality in complex reasoning tasks where the cost of a wrong answer exceeds the cost of a slower one.

[Agntdev](https://agntdev.com/langchain-vs-crewai-vs-autogen-2026-honest-comparison/) offers the most pragmatic advice: build v1 with raw SDK calls, no abstractions. Get it working. Watch it fail. Understand why it fails. If one agent genuinely cannot handle the task, prototype the multi-agent version in CrewAI — it will take an afternoon. If the prototype works but you need tighter control for production, rewrite the critical paths in LangGraph. Keep CrewAI for the parts where "good enough" is good enough.

The deeper point, however, is not about which framework to choose. It is about what frameworks even are. The term "agent framework" implied that the framework was the agent — that LangGraph or CrewAI or AutoGen was what did the work. The harness perspective inverts this. The framework is infrastructure. The agent is the model plus the system around it. And the system around it is now the primary object of engineering attention.

In the third week of May 2026, five research groups independently published papers arguing that the next bottleneck in AI agent performance is not the model. It is the layer that every practitioner has been building by hand — context management, tool routing, memory hygiene, verification, governance, failure recovery. That layer now has a name, a formal vocabulary, and a research agenda.

What it does not yet have is a mature engineering discipline. That is what the next two years will build. Or, as the wise may suspect, what the next two years will discover they have been building all along.

---

*This article was researched and written in May 2026. All data points link directly to their primary sources. Enterprise adoption figures should be treated as estimates based on survey data and platform telemetry, not precise measurements.*

### Sources

- [Shangding Gu, "From Model Scaling to System Scaling: Scaling the Harness in Agentic AI" (arXiv, May 2026)](https://arxiv.org/abs/2605.26112)
- [Zhong & Zhu, "AI Harness Engineering: A Runtime Substrate for Foundation-Model Software Agents" (arXiv, May 2026)](https://arxiv.org/abs/2605.13357)
- [Meng, Wang & Chen, "Agent Harness for Large Language Model Agents: A Survey" (Preprints, Apr 2026)](https://www.preprints.org/manuscript/202604.0428)
- [Ning et al., "Code as Agent Harness" (arXiv, May 2026)](https://arxiv.org/abs/2605.18747)
- [AHE: "Agentic Harness Engineering" (arXiv, Apr 2026)](https://arxiv.org/html/2604.25850v2)
- [NLAH: "Natural-Language Agent Harnesses" (arXiv, Mar 2026)](https://arxiv.org/abs/2603.25723)
- [HarnessAudit: "Auditing Agent Harness Safety" (arXiv, May 2026)](https://arxiv.org/abs/2605.14271)
- [AgentScout: "Multi-Agent Orchestration at 22% Production" (May 2026)](https://agentscout.live/tech/ai-agents/insight/multi-agent-orchestration-22-percent-threshold/)
- [Datadog 2026 State of AI Engineering Report (Apr 2026)](https://newclawtimes.com/articles/datadog-2026-state-ai-engineering-agent-framework-adoption-doubles/)
- [KXN Technologies: "State of Agentic AI in the Enterprise 2026" (Mar 2026)](https://kxntech.com/global/en/research/state-of-agentic-ai-2026/)
- [CallSphere: "72% of Global 2000 Move Beyond Pilots" (2026)](https://callsphere.ai/blog/enterprise-ai-agents-production-72-percent-global-2000-beyond-pilots-2026.md)
- [Belitsoft/Gartner: "40% of Enterprise Apps to Include Agents by End of 2026" (Apr 2026)](https://www.financialcontent.com/article/abnewswire-2026-4-8-belitsoft-releases-ai-agent-development-forecast-2026-40-of-enterprise-applications-to-include-task-specific-agents-by-year-end)
- [Databricks (via Kanishk Patel): "327% Growth in Multi-Agent Workflows" (Apr 2026)](https://learnagentic.substack.com/p/327-growth-in-multi-agent-workflows)
- [Presenc AI: "AI Agent Framework GitHub Rankings May 2026"](https://presenc.ai/research/ai-agent-framework-github-rankings-2026)
- [AI Agent Engineering: "Framework Benchmarks 2026" (Mar 2026)](https://ai-agent-engineering.org/news/ai-agent-frameworks-benchmarked-langchain-vs-crewai-vs-autogen-in-2026-the-numbers-that-actually-matter)
- [Agntdev: "LangChain vs CrewAI vs AutoGen 2026" (Mar 2026)](https://agntdev.com/langchain-vs-crewai-vs-autogen-2026-honest-comparison/)
- [Bananalabs: "The Definitive AI Agent Framework Comparison" (Apr 2026)](https://bananalabs.io/blog/langchain-vs-crewai-vs-autogen)
- [Rize: "AI Adoption Trends 2024–2026" (May 2026)](https://rize.io/blog/ai-adoption-trends-2024-2026)
- [PyPI: langgraph download stats (May 2026)](https://pypi.org/project/langgraph/)
- [HARNESSCARD: "Natural-Language Agent Harnesses" preprint (2026)](https://www.preprints.org/frontend/manuscript/969cc3d9a5271168ae0d40072f261f0c/download_pub)
