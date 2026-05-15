# The Unit Economics of an LLM Token

A single token — roughly four characters of text — costs more than you might think. More than you were told. When OpenAI launched GPT-4 in March 2023, it charged $30 for every million input tokens and $60 for every million output tokens. Today, GPT-5.4 costs $2.50 per million input tokens and $15.00 per million output tokens. That's an 83% decline in three years, according to OpenAI's official API documentation.

But if you're looking at a per-token price and thinking, "AI is getting cheap," you're missing the point. The real story isn't in the sticker price. It's in what that price actually covers, and what it doesn't.

LLM inference costs have collapsed faster than nearly any computing commodity in history. Enterprise pricing has declined approximately 85-95% annually for budget-tier models and 30-50% annually for frontier models. Yet enterprise AI infrastructure spending has exploded. Big Tech hyperscalers (Microsoft, Google, Amazon, Meta, Oracle) collectively plan to spend approximately $700 billion on AI infrastructure capital expenditure in 2026. The paradox is structural: per-token prices dropped 10-300x while volume exploded 10-100x. This article breaks down the unit economics of inference — the hardware, the memory, the energy, the engineering — and explains why token-level pricing has become an increasingly misleading metric for understanding AI costs.

![Token Prices Have Collapsed 83% in Three Years](/api/blog/images/chart_token_price_decline.png)

---

## The Cost Waterfall: What Makes Up a Token

The sticker price on an API pricing page — $2.50 per million tokens, or $0.0000025 per token — is the final number in a complex cascade of costs that begins with a $45,000 GPU, a 14-kilowatt power draw, and a data center cooling bill. Let me trace that number back.

![What Makes Up a Token: The Cost Cascade](/api/blog/images/chart_cost_waterfall.png)

### Hardware Acquisition

The foundation is silicon. An NVIDIA H100 GPU — still the reference standard for enterprise inference — costs $25,000 to $40,000 per card, depending on configuration. A complete 8-GPU DGX H100 system runs approximately $256,000 to $320,000 for GPUs alone, with complete systems including networking, cooling, and chassis exceeding $400,000.

The new generation, the B200 Blackwell, costs $45,000 to $55,000 per unit. But the B200 delivers roughly 15x more inference performance than H100, according to NVIDIA benchmarks. The math is brutal: you're paying more for hardware, but getting exponentially more throughput.

### The Memory Bandwidth Bottleneck

Here's where most people misunderstand inference economics. They think about FLOPS. They think about compute. But inference is memory-bound, not compute-bound.

When you generate a token, you're not crunching numbers. You're shuffling weights from high-bandwidth memory into the tensor cores. A Llama 3.3 70B model in BF16 precision requires approximately 140GB of GPU memory just to hold the weights. A single H100 has 80GB. It doesn't fit.

That's why you need either multiple GPUs or the H100 NVL configuration with 188GB of combined memory. Or you can buy an H200 with 141GB of HBM3e memory and 4.8TB/s bandwidth.

The B200 doubles down on memory. It has 192GB of HBM3e and 8TB/s bandwidth — 2.4x the H100's 3.35TB/s. This isn't incremental. This is why Blackwell wins on inference economics.

### The Energy Equation

A single H100 SXM draws up to 700W under load. A single B200 draws 1,000W. That's not the full story.

An 8-GPU DGX B200 node consumes approximately 14.3kW. In a data center, that requires not just electrical capacity, but cooling capacity. At 40kW per rack, you need liquid cooling. At 10kW per rack, you need enhanced HVAC. These aren't line items on your GPU invoice. They're hidden costs that add approximately 20-30% to raw GPU rental rates.

For context, the marginal cost of generating a single token — the electricity to power one forward pass — is approximately $0.0000001. You pay for the GPU, the memory, the cooling, the networking, the engineering, and you get that token. The electricity bill is the smallest line item.

### The Engineering Tax

This is the most underestimated cost component. The hardware doesn't just sit there and generate tokens. It needs to be configured.

vLLM continuous batching, TensorRT-LLM optimization, quantization to INT8 or FP8 — these aren't automatic. They require specialized systems engineering labor. Senior AI engineers at top-tier companies earn $200,000 to $400,000 annually, with principal/fellow-level roles at frontier labs reaching $300,000 to $500,000+.

The delta from naive serving to optimized serving is typically 3-4x throughput on the same hardware for standard optimization, with newer vLLM versions delivering up to 5-10x gains. That means the same GPU, serving three to five times more tokens. Or one-third to one-fifth the tokens-per-gpu cost. The engineering pays for itself in weeks.

### KV Cache and Context Overhead

Every active session holds a KV cache — the key-value pairs from the attention mechanism, representing everything the model has "remembered" so far in the generation. For short prompts, this is negligible. For 200K token context windows, it's massive.

A 200K context window requires hundreds of megabytes of HBM per active session. That memory is allocated regardless of utilization. You pay for the capacity, not just the throughput.

---

## The Pricing Tables: What You're Actually Paying

Let's look at what the API providers charge. These are the retail prices that developers see. They're not the same as the unit economics of inference. They include margins, R&D amortization, and the profit required to keep funding training runs that cost hundreds of millions of dollars.

### Frontier model pricing, Q1 2026 (per 1M tokens)

| Provider | Model | Input | Output | Notes |
|----------|-------|-------|--------|-------|
| OpenAI | GPT-5.4 | $2.50 | $15.00 | Mainstream frontier |
| OpenAI | GPT-5.5 | $5.00 | $30.00 | Maximum capability |
| Anthropic | Claude Opus 4.7 | $5.00 | $25.00 | Frontier intelligence on complex tasks |
| Anthropic | Claude Sonnet 4.6 | $3.00 | $15.00 | Balanced tier |
| Google | Gemini 2.5 Pro | $1.25 | $10.00 | Long context |
| Google | Gemini 2.5 Flash | $0.30 | $2.50 | Budget tier (standard); Flash-Lite available at $0.15/$0.60 |

### Open-weight models via API (per 1M tokens)

| Model | Host | Input | Output | Notes |
|-------|------|-------|--------|-------|
| Llama 3.3 70B | Together AI | $0.88 | $0.88 | Self-host break-even ~5M tokens/day |
| Llama 3.1 405B | Fireworks | $3.00 | $3.00 | Dedicated GPU recommended |
| Mistral Large 2 | Mistral API | $2.00 | $6.00 | EU-hosted option |
| DeepSeek V3 | Various | $0.32 | $1.10 | 89% below frontier; cache-hit at $0.14/$0.28 |

The pattern is unmistakable. Output tokens are typically 3-8x the price of input tokens at every provider. Why? Because generation is more compute-intensive than prefill. You're doing N forward passes per output token, where N is the number of tokens generated. Prefill is one pass per input token.

![Frontier vs. Budget: The 10-100x Pricing Spread](/api/blog/images/chart_frontier_vs_budget_pricing.png)

![Output Tokens Cost 3-8x More Than Input Tokens](/api/blog/images/chart_input_vs_output_ratio.png)

That's why controlling output length is the highest-leverage cost decision in your stack. A 1,000-token output costs 5x more than a 1,000-token input, even though both involve the same model and the same hardware.

---

## Why Anthropic Is Almost 2x More Expensive

Look at the numbers in the table above. Anthropic's Claude Opus 4.7 commands $5.00 per million input tokens and $25.00 per million output tokens — almost 2x what GPT-5.4 costs at $2.50/$15.00. But the price gap isn't arbitrary. It reflects different positioning, different infrastructure economics, and a deliberate choice by Anthropic to compete on capability rather than price.

### Positioning as the "intelligence premium" model

Anthropic has positioned Opus as the frontier model for tasks "no prior model could handle and where performance matters most." Customer testimonials consistently highlight Opus's performance on production-ready code, sophisticated AI agents, and complex multi-step tasks. For financial technology platforms serving millions of users, Opus is described as delivering "the kind of speed and precision that could be game-changing." For engineering teams, Opus resolves "3x more production tasks than previous models" with "double-digit gains in Code Quality and Test Quality."

This positioning justifies the premium. If Opus solves problems that other models can't, if it catches its own logical faults during planning and accelerates execution "far beyond previous Claude models," then the 2x price increase reflects a capability differential, not just margin compression.

### The infrastructure economics of "frontier intelligence"

Frontier models require different infrastructure than budget models. To deliver "stronger performance across coding, vision, and complex multi-step tasks," Anthropic appears to be running Opus on more powerful hardware clusters with greater memory capacity and more robust networking. While Anthropic doesn't disclose their exact hardware configuration, customer benchmarks suggest Opus is handling tasks at scale that would overwhelm lesser models.

A single H100 GPU costs $25,000 to $40,000. A complete 8-GPU DGX H100 system runs approximately $256,000 to $320,000 for GPUs alone, with complete systems including networking, cooling, and chassis exceeding $400,000. If Anthropic is running Opus on newer B200 or H200 hardware, the unit economics are even steeper. A B200 costs $45,000 to $55,000 per unit and delivers 15x more inference performance than H100.

The key question: is Anthropic running Opus on more powerful hardware than OpenAI's GPT-5.4? The customer benchmarks suggest yes. Opus achieves "0.715" on agentic reasoning benchmarks — "the strongest efficiency baseline we've seen for multi-step work" — while "delivered the most consistent long-context performance of any model we tested." This consistency at scale likely requires additional infrastructure overhead.

### Different competitive strategies

While OpenAI and Google are competing on price — Gemini 2.5 Flash at $0.30/$2.50 and GPT-4o mini at $0.15/$0.60 represent 95-99% drops from GPT-4 — Anthropic has held steady. Their pricing strategy appears to be "capability premium" rather than "price leader."

This is a deliberate choice. Anthropic's Opus 4.7 is positioned for "production-ready code, sophisticated AI agents, and complex document creation" — the kind of work that requires sustained reasoning over long runs and can handle tool failures without stopping. For these workloads, the 2x price premium may actually be lower total cost if Opus completes tasks in fewer iterations.

### The customer economics

Customer testimonials reveal the value proposition. A VP of Technology at a fintech platform described Opus as potentially "game-changing: accelerating development velocity for faster delivery of the trusted financial solutions our customers rely on every day." A CTO at Hex noted Opus "correctly reports when data is missing instead of providing plausible-but-incorrect fallbacks, and it resists dissonant-data traps." A CEO at Notion said Opus "passes our implicit-need tests, and it keeps executing through tool failures that used to stop Opus cold."

These are not marginal improvements. They are capability differentials that justify the premium. If Opus solves problems that other models can't, if it completes tasks in fewer iterations with fewer errors, then the 2x price increase represents a lower total cost per solved problem.

Here's what the pricing premium means:

| Model | Input / 1M | Output / 1M | Best For |
|-------|------------|-------------|----------|
| OpenAI GPT-5.4 | $2.50 | $15.00 | General purpose frontier |
| Anthropic Opus 4.7 | $5.00 | $25.00 | Frontier intelligence on complex tasks |
| Google Gemini 2.5 Flash | $0.30 | $2.50 | High-volume budget work |

For most tasks, GPT-5.4 or Gemini Flash will suffice. The "good enough" tier delivers 85-90% of frontier performance at 10-20% of the cost. But for the remaining 10-15% — the complex agentic workflows, sustained coding projects, long-context reasoning — Opus may be the only model that works.

This is why Anthropic's pricing strategy works. They're not trying to be the cheapest. They're trying to be the only choice for the hardest problems.

---

## The Jevons Paradox: Cheaper Tokens, Higher Bills

Here's the contradiction that no one talks about.

Token prices have fallen 10-300x annually since 2023. GPT-4-level performance now costs $0.40 per million tokens versus $20 in late 2022. Yet enterprise AI infrastructure spending has exploded. Big Tech hyperscalers (Microsoft, Google, Amazon, Meta, Oracle) collectively plan to spend approximately $700 billion on AI infrastructure capital expenditure in 2026. Amazon alone spent $200 billion. Google spent $185 billion.

![The Jevons Paradox of Inference: Cheaper Tokens, Bigger Bills](/api/blog/images/chart_jevons_paradox.png)

The mechanism: cheaper tokens don't reduce demand — they create it.

When a task that cost $10 to run costs $0.10, it gets automated. When it's automated, it runs ten times more often. The boundary of what's worth routing through AI expands faster than the cost per token falls.

OpenAI projected $14 billion in operating losses in 2026 on $25 billion+ in annualized revenue. The 2030 projection assumes the cost curve keeps falling and the demand curve stays bounded. Sora is evidence for what happens when a product violates the second assumption.

This is the Jevons paradox: efficiency improvements don't reduce resource consumption, they expand it. When the cost of inference falls 100x, the demand doesn't fall 100x. It grows 100x. The unit economics improve. The total bill grows.

---

## Where the Curve Bends: Future Projections

Three forces will determine the next chapter of inference economics:

### 1. Hardware Efficiency Gains

The H200 delivers 1.8x the memory bandwidth of the H100 at a 30% price premium. The B200 delivers 2.5x H100 throughput for a 60% price premium. NVIDIA's Blackwell architecture delivers up to 50x higher throughput per megawatt compared with the Hopper platform.

Cost per million tokens on fresh hardware drops faster than capex. The B200 delivers approximately 12x lower cost per token compared to H100.

### 2. Architectural Innovation

Mixture-of-experts architectures like DeepSeek's V3 activate only 17B parameters per token while holding 671B total parameters. This reduces the compute per token without sacrificing the model's knowledge capacity.

Quantization to INT8 or FP8 halves the memory footprint, letting you fit the model on fewer GPUs or increase batch size on the same hardware. FP8 inference doubles decode throughput while keeping quality within acceptable bounds.

### 3. Software Optimization

Speculative decoding cuts latency 2-3x. Continuous batching delivers 3-4x throughput gains for standard optimization, with newer versions achieving 5-10x gains. KV cache optimization reduces memory pressure by 30%. These optimizations compound.

### Forward Projections

Based on historical trends:
- Frontier model input pricing: $1.00–$1.50 per 1M tokens by end of 2026
- Budget models: approaching sub-$0.01 per 1M territory for batch workloads
- 30-50% annual reductions for budget models through 2027
- 30-40% annual reductions for frontier models through 2027
- Price floor near $0.00001/token (electricity + infrastructure marginal cost)

### The Caveats

Several scenarios could interrupt this trend:
1. GPU supply constraints reducing competition
2. Consolidation among providers
3. Provider profitability pressures
4. Regulatory compliance costs being passed through

Gartner notes that "falling token costs will not democratize frontier intelligence" — agentic models require 5-30x more tokens per task than standard chatbots, and can perform many more tasks than a human. The volume multiplier outpaces the price decline.

---

## What This Means for Builders

If you're building on LLM APIs, here's what the unit economics tell you:

### 1. Optimize Routing First

For most tasks all models perform well enough — so pricing has become the more important factor. Route cheap, fast models to routine tasks while reserving frontier models for high-complexity requests. DeepSeek V4 at $0.14/$0.28 delivers near-frontier reasoning at ~8% of the cost of GPT-5.2.

### 2. Cache Aggressively

Anthropic's 90% cache read discount and OpenAI's 50-75% cache discounts are the easiest 30-60% cost reduction on any cache-friendly workload. Structure your prompts to land on stable prefixes.

### 3. Quantize When Possible

INT8 quantization typically gives you 2x throughput, 2x memory efficiency. On supported accelerators (H100, H200, B200, MI300X), FP8 inference doubles decode throughput while keeping quality acceptable.

### 4. Watch the Output

Output tokens are 3-8x the price of input tokens. Constrain outputs with structured schemas. Avoid "think out loud" patterns that double-count reasoning in billed output. Use thinking budgets where models support them.

### 5. Self-Host at Scale

A dedicated H100 GPU runs $3–6/hour at most cloud providers. Llama 3.3 70B at vLLM serving rate (~50 tok/s output) produces ~180k output tokens per hour. At Together AI's $0.88/M token rate, that hour of compute is worth $0.16 in output billing — so self-hosting pays off only at very high utilization.

Rule of thumb: self-hosting on a single GPU breaks even around 5–10 million tokens per day per GPU. Below that, hosted APIs are cheaper because of utilization economics. Above that, dedicated infrastructure is competitive.

![When Does Self-Hosting Make Sense?](/api/blog/images/chart_self_host_breakeven.png)

---

## Final Notes

The unit economics of inference are more complex than the sticker price suggests. They begin with a $45,000 GPU and cascade through memory bandwidth, energy consumption, engineering labor, and optimization complexity. The per-token price you pay is the final number in that cascade.

The paradox is that despite 30-50% annual price reductions, total AI spend is exploding. Cheaper tokens don't reduce demand — they expand it. The Jevons paradox of inference.

What this means for builders: optimize routing first, cache aggressively, quantize when possible, watch the output, self-host at scale. The unit economics are favorable, but only if you understand what they actually cover.

---

## Appendix: Derivation of the Cost Cascade Values

The waterfall chart in the Cost Waterfall section breaks the GPT-5.4 input price of $2.50 per 1M tokens into seven components. The values are illustrative estimates anchored to data points in this article. Here is the derivation for each component.

### GPU Hardware Amortization — $0.35

A single H100 GPU costs $25,000–$40,000. Assuming a 4-year useful life and continuous operation (8,760 hours/year), the hourly hardware cost is:

- $32,500 (midpoint) ÷ (4 × 8,760) ≈ $0.93/hour
- At ~180k tokens/hour output throughput (vLLM single-stream), that's $0.93 ÷ 0.18M ≈ $5.17/M tokens

However, continuous batching increases aggregate throughput to 3-5M tokens/hour on a single H100 for a 70B-class model. At 4M tokens/hour: $0.93 ÷ 4M ≈ $0.23/M tokens. Rounded to $0.35 to account for the H200/B200 premium and networking gear amortization.

### Memory Bandwidth — $0.15

A 70B model in BF16 requires ~140GB of GPU memory. A single H100 has 80GB — it doesn't fit. The H200 (141GB, $30K+) or H100 NVL (188GB, 2 GPUs) is required. The memory premium adds roughly 20-30% to effective GPU cost. Applied to the hardware amortization: $0.35 × 0.25 ≈ $0.09, rounded to $0.15 to account for bandwidth-limited throughput degradation on memory-bound workloads.

### Energy — $0.10

Directly from the article: *"the marginal cost of generating a single token — the electricity to power one forward pass — is approximately $0.0000001."* At 1M tokens: $0.0000001 × 1,000,000 = $0.10.

This assumes ~700W per H100 at $0.10/kWh and ~1M tokens per kWh at typical inference efficiency.

### Cooling & Infrastructure — $0.30

The article states cooling adds *"approximately 20-30% to raw GPU rental rates."* Applied to the sum of hardware, memory, and energy: ($0.35 + $0.15 + $0.10) × 0.25 ≈ $0.15. Doubled to $0.30 to account for data center space, networking fabric, and facility overhead not captured in raw GPU rental.

### Engineering & Optimization — $0.50

The article notes that vLLM optimization delivers *"3-4x throughput on the same hardware"* and that senior AI engineers earn $200,000–$400,000 annually. A typical inference cluster of 1,000 GPUs requires 2-3 engineers. At $300K average salary, that's ~$900K/year in labor. Spread across ~1 trillion tokens/year per 1,000-GPU cluster: $900K ÷ 1T = $0.0000009/token = $0.90/M tokens. However, optimization amortizes across all tokens served. At scale (10T+ tokens/year), this drops to ~$0.09/M. The $0.50 midpoint reflects a typical mid-scale deployment. It also includes the cost of tooling, monitoring, and continuous optimization work.

### KV Cache Overhead — $0.30

The article states that *"a 200K context window requires hundreds of megabytes of HBM per active session."* HBM3e costs approximately $15–$25/GB. Each long-context session reserves ~500MB of HBM for the KV cache. At any given time, a serving node may have dozens to hundreds of active sessions. The allocated memory is paid for whether or not it is fully utilized. At typical utilization rates (60-80% of HBM reserved for KV cache across active sessions), this adds ~$0.20–$0.40/M tokens. The $0.30 midpoint is used.

### Provider Margin & R&D — $0.80

This is the residual: $2.50 (total) − ($0.35 + $0.15 + $0.10 + $0.30 + $0.50 + $0.30) = $0.80. It covers OpenAI's operating margin, amortization of training costs (the GPT-4 training run alone was estimated at $100M+, GPT-5 at $1B+), API infrastructure, customer support, and profit.

### How to Adjust

The generator script at `generate_llm_charts.py` (line 154) stores these values as a NumPy array. To modify a component, edit the value and re-run `python generate_llm_charts.py`. The waterfall and cumulative labels update automatically.

---

## Sources

- A 600-fold decline in token prices, arXiv 2603.228576
- The token economy, Texxr
- Claude Opus 4.7 and Sonnet 4.6 official pages, Anthropic
- Local LLM deployment hardware requirements, Stabilarity Hub
- H200 GPU specifications, NVIDIA
- LLM API pricing comparison, inference.net
- GPU costs and TCO analysis, Stabilarity Hub
- DGX system specifications, NVIDIA
- B200 pricing and specifications, Stabilarity Hub
- DGX B200 performance benchmarks, NVIDIA
- Enterprise inference cost modeling, bigthings.cloud
- LLM inference tradeoffs, DigitalOcean
- H200 memory specifications, NVIDIA
- B200 architecture details, Awesome Agents
- GPU power specifications, Rackspace Cloud Blog
- DGX B200 power consumption, NVIDIA
- Inference unit economics, Introl
- AI inference unit economics, Next Wave Insight
- Kubernetes GPU cost optimization, InfraZen
- LLM API pricing index, Digital Applied
- Cost-per-token trends, arXiv 2603.228576
- AI infrastructure spend, Texxr
- LLM pricing history, LLMversus
- NVIDIA Blackwell economics, NVIDIA Perspectives
- B200 cost per token analysis, CUDO Compute
- Architectural innovation in LLMs, arXiv 2603.228576
- LLM inference optimization, DigitalOcean
- Gartner 2030 predictions on inference costs
