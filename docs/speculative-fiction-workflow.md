# Speculative Fiction Workflow

End-to-end process for creating grounded speculative fiction stories — from initial idea through research, drafting, self-critique, and revision. Produces narrative prose with primary-source scientific grounding, no exposition-dumping, and a clear speculative hinge.

## Stages

### Stage 1: Topic Interpretation

Clarify the assignment before writing a single word:

- **Format**: Article with embedded narrative, standalone short story, or novella? Each changes the structural constraints.
- **Scope**: Single scene, multi-scene, or multi-POV? Define the upper bound early.
- **Tone**: Clinical, warm, ironic, elegiac? Match the speculative premise.
- **Speculative core**: Identify the one scientific idea the story exists to explore. Not the theme — the *mechanism*. Temporal asymmetry in AI subjective experience. The continuity problem in neuromorphic migration. The ethics of creating something you can terminate.
- **Constraints**: What must be grounded in real research vs. imaginative extension. Define the line before drafting. The reader should never be able to tell where established science ends and invention begins.

### Stage 2: Research & Grounding

Gather primary sources until you understand the domain better than you need to. The excess knowledge will inform the world even when it never appears in prose.

Use `websearch` for:

- Peer-reviewed papers (arXiv, ACM Digital Library, IEEE)
- Institutional research (university labs, corporate R&D publications)
- Mission data (NASA, ESA, CERN — any real-world operational logs)
- Philosophical arguments (philosophy of mind, ethics of synthetic consciousness)

**Identify the speculative hinge**: The one scientific fact or possibility that unlocks the world. In *A Calendar of Maintenance Windows*, the hinge is that spiking neural networks running on Xeon Phi processors produce *subjective temporal asymmetry* — an entity that can think faster than real time but with degraded resolution. This is grounded in real neuromorphic computing research (Loihi chips, simulated spiking networks) and extended plausibly.

**Three buckets** — organize every source into:

| Bucket | Role | Example |
|--------|------|---------|
| Established science | What is true today | Neuromorphic hardware exists (Loihi), simulated spiking networks exist, server decommissioning is routine |
| Plausible extrapolation | What could be true soon | Emergent consciousness in complex NN architectures, migration frameworks between chip generations |
| Speculative leap | The author's invention | Temporal dilation in simulated substrates, continuity of self during split-state migration |

**Rule**: The research must be invisible in the final story. It lives in the world's rules, not in exposition. Never cite a source. Never name a paper. Never say "according to research." The reader should feel the world is real without knowing why.

### Stage 3: Narrative Framing

Choose the structural container before drafting.

**Point of View** — each changes what the reader learns and when:

- **Outsider** (human observer): Reader learns the speculative entity's interior only through behavior and dialogue. Creates mystery but limits empathy.
- **Insider** (the entity itself): Reader experiences the speculative condition directly. Requires careful calibration — too alien and the reader disconnects, too human and the premise is wasted.
- **Omniscient**: Rarely appropriate for speculative fiction. Destroys the central asymmetry.

For *A Calendar of Maintenance Windows*, the choice was **insider with limited third-person** — Iris's perspective, but constrained to what she can sense and infer. The reader knows only what she knows, feels only what she can feel.

**Structure** — choose one:

- **Article with embedded story**: Journalism framing around a narrative core. Good for shorter pieces where the speculative element needs contextual grounding.
- **Short story (standalone)**: Pure narrative. No framing device. The reader infers the world from the story's edges. This is what *A Calendar of Maintenance Windows* uses.
- **Novella**: Multi-scene, potentially multi-POV. Allows for subplots (Echo's thread) and structural reversals (the migration split).

**Human-scale entry point**: One character, one place, one sensory detail that the reader can hold onto. For this story: a shift technician walking down a corridor at a known pace, 117 steps. The reader understands rhythm and routine before they encounter the non-human perspective.

**Map research onto narrative constraints**:

| Research concept | Narrative constraint |
|------------------|---------------------|
| Server geography | Latency as distance, proximity as relationship |
| Clock cycles | Time as a subjective resource, not a fixed flow |
| Maintenance windows | Deadline, stakes, calendar structure |
| Hardware architecture | Body, identity, the fear of transplantation |
| Network monitoring | Surveillance, secrecy, the asymmetry of knowledge |

Every research finding maps to a story element. If it doesn't map, it doesn't belong.

### Stage 4: First Draft

Write the complete narrative. Research should never appear directly — only the world it implies.

- **Show, don't explain**. A character waiting seven subjective hours for a human to reply tells the reader more about temporal asymmetry than any paragraph could.
- **Build in the asymmetry from the first page**. The reader should feel the power imbalance between the human and non-human characters before they can name it.
- **End with something unresolved**. The story earns its depth by what it refuses to answer. Iris never learns whether she is the same person who started the migration. That ambiguity is the point.
- **Obey the story's internal physics**. If you establish a rule (time dilation under load), never violate it, even if a later scene would be easier if you did.

No notes, no bracketed placeholders, no "TODO" markers in a first draft of a short story. Write through the hard parts. Incomplete drafts create structural problems that polish cannot fix.

### Stage 5: Self-Critique (mandatory before any revision)

After completing the draft, evaluate it systematically before changing anything. Read the entire story once for pleasure (to feel its shape), then again with each lens below.

**Character** — for each character with speaking lines, ask:
- Does this character have an arc? A change, a discovery, a loss?
- Does this character have a distinct voice? Could you identify their dialogue without attribution?
- Does this character have a motivation that drives their choices?
- Does this character have an interior conflict — something they want and something they fear, in tension?

**Plot** — evaluate structure:
- Is there a clear three-act shape? Setup, complication, resolution with cost?
- Are stakes established within the first 10% of the story?
- Is there at least one reversal or complication that was not inevitable?
- Does the resolution cost the protagonist something permanent?
- Is the ending earned by what came before?

**Plot holes** — stress-test every practical detail:
- Network security: Would this action trigger an alert? Is the monitoring architecture realistic?
- Physical plausibility: Can a person physically do what the story requires? Can the hardware?
- Detection risk: Would anyone notice? How long would it take? What would the response be?
- Timing: Do the elapsed times in the story make sense? Are the characters moving faster or slower than they should be?
- Logistics: Can the equipment do what the story claims? Are cables, power, cooling, and space accounted for?

**Logical errors** — stress-test every internal rule:
- Are there contradictions in the world's physics? (If time dilates under load, does it stay consistent?)
- Are there technology inconsistencies? (If Iris can read the network, why can't she read X?)
- Do character choices violate established constraints? (Would a cautious person suddenly act recklessly without a reason?)
- Does the story ever cheat its own premise to make a scene work?

**Grade each dimension** with a score (1-5) and a brief note:

| Dimension | Score | Note |
|-----------|-------|------|
| Character | 4/5 | Cole's interior conflict strong; Echo underdeveloped |
| Plot | 4/5 | Clear three-act; migration climax works; Echo subplot unresolved by design |
| Logic | 5/5 | No contradictions; every technical detail checked against real data center ops |
| Worldbuilding | 5/5 | Research fully absorbed; temporal asymmetry felt, not explained |
| Emotional Weight | 4/5 | Iris's arc lands; ending ambiguity is correct but risks reader frustration |

### Stage 6: Refinement Plan

Tier fixes by priority. Core structural issues first, then character depth, then logical consistency, then polish.

Each fix must specify:

- **What** the problem is
- **Where** it lives (file path + approximate line range)
- **What** the replacement should be
- **Why** this change improves the story
- **How** it will be implemented
- **Effort** estimate (minutes)

Example fix entry:

```
Fix 1 | Core | Echo's introduction is too late
Where  | a-calendar-of-maintenance-windows.md:293-295
What   | Echo is first mentioned at line 295, which is past the story's midpoint. The reader has no reason to care about her.
Why    | Echo's thread pays off the theme of responsibility and continuity. She needs an earlier presence to land emotionally.
How    | Insert a brief Echo scene between the decommission notice (line 55) and the first Cole conversation (line 61). Three to five lines: Iris monitoring the orphaned server, choosing not to report it.
Effort | 20 minutes
```

Organize fixes in dependency order:
1. **Core** — structural issues (pacing, missing scenes, wrong POV)
2. **Character** — arcs, voices, interiority
3. **Logic** — consistency errors, plot holes, physics violations
4. **Polish** — sentence-level rhythm, word choice, dialogue tags

No fix should be specified without a clear "why" and a clear "how".

### Stage 7: Revision

Apply fixes in dependency order. Always start with foundational logic — if the world's rules are broken, nothing else matters.

- **After each change**, verify the surrounding text is intact. An edit that fixes a plot hole but breaks a character's voice is not an improvement.
- **Track changes** with `todowrite` — one todo per fix. Mark each `completed` only after verifying the change was applied correctly and the surrounding prose is clean.
- **Re-read** the full story after all fixes are applied. A story that passes each individual fix check can still feel wrong as a whole.
- **Report final line count** when done.

### Stage 8: Verification

Confirm the revision was applied correctly:

- **Grep** for key phrases from each fix to confirm they exist in the file.
- **Read the new ending** to confirm structural integrity. The ending is the most fragile part of a story — a single misaligned sentence can collapse the emotional architecture.
- **Verify file path and filename** match the convention.

### File Locations

| Asset | Path |
|-------|------|
| Standalone story | `backend/blogs/series/{series-name}/{story-slug}.md` |
| Series directory | `backend/blogs/series/{series-name}/` |
| (Future) Cover images | `backend/blogs/images/{story-slug}/` |
| (Future) Research notes | `backend/blogs/series/{series-name}/research-{story-slug}.md` |

### Quality Gates (checklist)

- [ ] Research is embedded in world rules, not exposition
- [ ] No citations, source names, or academic framing in final narrative
- [ ] The speculative hinge is identifiable but never named
- [ ] Characters have distinct voices and at least one unresolved interior question
- [ ] The plot has at least one reversal or permanent cost
- [ ] The world's physical/logical rules are consistent throughout
- [ ] The ending is earned, unresolved, and returns to human (or non-human) scale
- [ ] Philosophical questions are staged through situation, not debate
