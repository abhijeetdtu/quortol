# When More Emotion Makes a Voice Stop Pausing

Text-to-speech systems often expose controls with inviting names: *emotion*, *exaggeration*, *guidance*. The names suggest clean dimensions. Turn one knob and the voice becomes more expressive. Turn another and it follows the reference speaker more faithfully. Punctuation, pronunciation, and pacing should remain where they were.

That is not what happened in our Chatterbox audiobook pipeline.

After adding sentiment-responsive emotional tuning, a narrator that had previously stopped at full stops began running through them. The first suspicion fell on sentence chunking. We had recently replaced a simple regular-expression splitter with NLTK's Punkt sentence tokenizer, and the timing of the regression made NLTK an obvious suspect. Yet the text still contained its punctuation. Were the periods being removed somewhere deeper in the pipeline? Were sentences being packed differently? Or had the emotional controls changed more than emotion?

We answered the question with a controlled experiment: one book, one cloned voice, fixed text chunks, fixed random seeds, five baseline settings, four tuning variants, 480 generated audio files, and a separate acoustic evaluation pass.

The result was clear. NLTK was not removing punctuation, and ordinary sentence packing had not recently changed. The baseline Chatterbox parameters themselves strongly controlled pace and silence. Sentiment-based tuning then introduced passage-specific, nonlinear changes that could erase more than a second of pause in one passage and add a second in another. The parameter named `exaggeration` was especially unreliable for long-form narration.

This is how we isolated the problem, what we measured, and what the results imply for anyone building an audiobook pipeline on Chatterbox.

---

## The Pipeline and the Regression

The test pipeline used the original English Chatterbox model with a cloned narrator voice. Its broad sequence was:

1. Read and normalize the source text.
2. Detect sentences with NLTK Punkt.
3. Pack consecutive sentences into chunks no longer than 250 characters.
4. Split an individually oversized sentence at a nearby clause boundary.
5. Generate one WAV file per chunk.
6. Stitch the chunk WAVs together, inserting 150 milliseconds of silence between chunks.

The sentiment feature analyzed chunks with NLTK VADER. It converted passage-level emotional intensity into two Chatterbox parameters:

- Raise `exaggeration` by as much as `0.30 × intensity × strength`.
- Lower `cfg_weight` by as much as `0.20 × intensity × strength`.

Changes between adjacent chunks were rate-limited, but the cumulative value could still move meaningfully away from the baseline.

This design followed Chatterbox's own broad guidance. The project describes `0.5` exaggeration and `0.5` CFG as defaults. For dramatic speech, it suggests higher exaggeration and lower CFG. It also warns that higher exaggeration tends to speed up speech, while lower CFG may compensate with slower, more deliberate pacing. The important word is *may*. These are creative controls inside an autoregressive generation process, not independent sliders for emotion and tempo. ([Chatterbox repository and tuning guidance](https://github.com/resemble-ai/chatterbox#original-chatterbox-tips))

Our working audiobook command used a baseline of `0.7/0.7`: exaggeration 0.7 and CFG weight 0.7. The sentiment system then raised exaggeration and lowered CFG for emotionally stronger passages.

The audible regression was missing or weakened sentence pauses, particularly inside chunks containing multiple complete sentences.

---

## First Hypothesis: NLTK Was Removing Full Stops

It was not.

The sentence tokenizer preserves terminal punctuation in its returned strings. The project's tests also explicitly verified that periods and question marks survived tokenization. Long-sentence clause splitting retained punctuation as well. The preprocessing step normalized whitespace, but it did not strip full stops.

We ran the complete source text of John McPhee's *The Control of Nature* through both the current NLTK splitter and the former regular-expression splitter at a 250-character maximum.

| Segmentation method | Detected sentences | Final packed chunks |
|---|---:|---:|
| NLTK Punkt | 4,667 | 2,554 |
| Previous regex | 4,740 | 2,552 |

NLTK made 73 fewer sentence boundaries because it handled abbreviations and context differently. But after packing, the difference was only two chunks across a 475,825-character normalized text. Approximately 92% of both sets of chunks ended in sentence-like punctuation.

NLTK did make occasional questionable decisions around quotations. It could separate quoted dialogue in ways that sounded awkward when synthesized. That was worth fixing, but it could not explain a book-wide pacing regression.

The test also surfaced two older pipeline behaviors:

- Paragraph breaks were erased during whitespace normalization.
- Multiple complete sentences were commonly combined into one synthesis request.

With 4,667 detected sentences packed into 2,554 chunks, the average generation unit contained about 1.8 sentences. The explicit 150-millisecond stitch pause existed only between chunks. Full stops inside a chunk were left entirely to Chatterbox.

This made packing a plausible *mechanism* for missing pauses, but not a recent cause. The packing logic that combines sentences under the character limit was unchanged from the committed implementation. The recent oversized-sentence change merely replaced fixed-width slicing with safer splits at semicolons, colons, em dashes, commas, and spaces.

The text path had not deleted the pauses. The model had changed how it performed them.

---

## A Controlled A/B Test

We began with three representative chunks:

- Quoted dialogue containing two sentences.
- A dialogue-to-narration transition containing three sentences.
- A conventional two-sentence narration passage.

For each chunk, we generated four versions:

1. **Baseline:** fixed exaggeration and CFG.
2. **Exaggeration only:** sentiment-adjusted exaggeration, baseline CFG.
3. **CFG only:** baseline exaggeration, sentiment-adjusted CFG.
4. **Emotion:** both sentiment adjustments.

Every variant used the same source text, voice reference, temperature, top-p, min-p, repetition penalty, and random seed. We reset both the PyTorch and CUDA random seeds before every render. The model was loaded once so that initialization did not differ between variants.

The most audible failure appeared in chunk 11. Its parameter changes were small:

- Exaggeration: `0.700 → 0.727`
- CFG weight: `0.700 → 0.682`

Yet the acoustic result was large. Using a silence threshold of −45 dBFS and counting quiet runs of at least 60 milliseconds:

| Variant | Internal pause time | Total quiet time | Audio duration |
|---|---:|---:|---:|
| Baseline | 3.48 s | 4.12 s | 16.20 s |
| Exaggeration only | 1.87 s | 2.24 s | 14.08 s |
| CFG only | 2.84 s | 3.22 s | 14.84 s |
| Both | 2.42 s | 2.97 s | 14.44 s |

The first major pause in the baseline was approximately 1.72 seconds. It fell to 0.88 seconds with exaggeration only and roughly 0.70 seconds with CFG only. With both adjustments it was 0.68 seconds. Exaggeration-only removed 46% of all internal quiet time and sounded worst in listening.

The control passages mattered. Emotional tuning did not always reduce pauses. In another two-sentence chunk, the sentence pause increased slightly. That ruled out a deterministic punctuation failure. It showed a nonlinear generation effect: the same direction of parameter change could produce opposite timing outcomes in different passages.

---

## The Wider Experiment

Three chunks could reveal a failure but not characterize it. We expanded the experiment across the book.

### Sampling

We selected 24 multi-sentence chunks evenly across the complete text. This deliberately emphasized the case at issue: punctuation boundaries occurring *inside* a Chatterbox generation request.

### Baselines

We tested five matched baseline pairs:

- `exaggeration=0.3`, `cfg_weight=0.3`
- `exaggeration=0.4`, `cfg_weight=0.4`
- `exaggeration=0.5`, `cfg_weight=0.5`
- `exaggeration=0.6`, `cfg_weight=0.6`
- `exaggeration=0.7`, `cfg_weight=0.7`

At every baseline, the same four variants were generated: baseline, exaggeration-only, CFG-only, and combined emotion.

The entire sweep ran inside one Python process with one loaded Chatterbox model. Chunk selection and seed assignment were fixed. Before each baseline and variant, the same per-chunk seed was restored. This produced:

> 24 chunks × 5 baselines × 4 variants = 480 WAV files

### Generation parameters

The non-tested generation settings remained fixed:

| Parameter | Value |
|---|---:|
| Maximum chunk length | 250 characters |
| Temperature | 0.8 |
| Top-p | 1.0 |
| Min-p | 0.05 |
| Repetition penalty | 1.2 |
| Sentiment strength | 1.0 |
| Device | CUDA |

The test harness wrote a manifest containing the exact text, chunk index, seed, sentiment score, passage intensity, parameter values, audio duration, and file path for every render. It supported resume so interrupted sweeps could reuse finished WAVs.

---

## Evaluation Method

The separate evaluator read all 480 WAVs and measured each one consistently.

### Silence and pace

Audio was divided into 10-millisecond windows. A window below −45 dBFS was considered quiet. Consecutive quiet windows counted as a pause when they lasted at least 60 milliseconds. Leading and trailing silence were excluded from the internal-pause measure.

From these windows we calculated:

- Total internal pause time
- Internal pause ratio
- Pause count
- Median and maximum pause duration
- Words per second over the complete WAV
- Words per second over estimated active audio

This was intentionally broader than a punctuation metric. It counted quiet runs between words and clauses as well as sentences. Therefore it measured delivery density, not full-stop accuracy by itself. A forced-alignment system would be needed to assign every measured pause to a specific punctuation mark.

### Pitch and voicing

We estimated fundamental frequency using voiced-frame autocorrelation and recorded:

- Median F0
- F0 standard deviation
- 10th-to-90th-percentile F0 range
- Voiced-frame ratio

The lightweight estimator was selected so hundreds of files could be evaluated quickly without downloading another model. Absolute F0-range values should be treated cautiously because autocorrelation can choose a harmonic or octave multiple. Median F0 and within-method comparisons are more useful than treating every estimated maximum as a literal vocal pitch.

### Energy and artifacts

We also measured:

- RMS level
- RMS dynamic range
- Peak amplitude
- Clipped-sample ratio
- DC offset
- Zero-crossing rate
- Spectral centroid
- Spectral flatness
- A pooled log-spectrum timbre similarity against the voice reference

The timbre measure is a lightweight acoustic proxy, not a neural speaker-verification score. Optional hooks were added for Whisper-based WER/CER and a WavLM speaker embedding model, but the reported sweep did not run those heavyweight optional models. Accordingly, the experiment can speak confidently about timing and broad acoustic behavior, but not claim a validated MOS, intelligibility score, or neural speaker-identity score.

---

## Result One: Baseline Controls Pace More Than Sentiment Does

The untuned baseline produced a strong monotonic change in duration, pace, pause time, and median pitch.

| Baseline | Total duration, 24 chunks | Average chunk | Internal pauses | Pause ratio | Speaking rate |
|---:|---:|---:|---:|---:|---:|
| 0.3 | 6:27.92 | 16.16 s | 2.64 s | 15.8% | 2.32 words/s |
| 0.4 | 6:08.84 | 15.37 s | 2.35 s | 14.8% | 2.44 words/s |
| 0.5 | 5:47.08 | 14.46 s | 2.09 s | 13.9% | 2.59 words/s |
| 0.6 | 5:26.16 | 13.59 s | 1.77 s | 12.8% | 2.75 words/s |
| 0.7 | 5:15.60 | 13.15 s | 1.54 s | 11.6% | 2.87 words/s |

Moving from `0.3/0.3` to `0.7/0.7` increased average speaking rate by about 24% and reduced average internal pause time by about 42%. The lower setting was 72.32 seconds, or 22.9%, longer over the same 24 chunks. Even `0.5/0.5` was 31.48 seconds, or 10%, longer than `0.7/0.7`.

The baseline also shifted pitch. Mean median F0 rose from approximately 119 Hz at 0.3 to 135 Hz at 0.7. Voiced-frame ratio increased from roughly 68% to 72%, consistent with a denser delivery containing less silence.

The original `0.7/0.7` audiobook configuration was not merely “more guided” than the default. It was an inherently faster, more continuously voiced operating point.

---

## Result Two: The Distributions Tell the Real Story

Averages hide the reason the emotional system sounded unreliable. Across the 24 untuned chunks, the 10th percentile, median, and 90th percentile behaved as follows.

### Speaking-rate distribution

| Baseline | 10th percentile | Median | 90th percentile |
|---:|---:|---:|---:|
| 0.3 | 2.00 | 2.32 | 2.76 words/s |
| 0.4 | 2.09 | 2.46 | 2.78 words/s |
| 0.5 | 2.24 | 2.57 | 2.97 words/s |
| 0.6 | 2.34 | 2.72 | 3.31 words/s |
| 0.7 | 2.33 | 2.84 | 3.15 words/s |

### Internal-pause distribution

| Baseline | 10th percentile | Median | 90th percentile |
|---:|---:|---:|---:|
| 0.3 | 1.40 s | 2.16 s | 4.42 s |
| 0.4 | 1.12 s | 2.14 s | 3.55 s |
| 0.5 | 1.04 s | 2.01 s | 3.06 s |
| 0.6 | 0.97 s | 1.78 s | 2.47 s |
| 0.7 | 0.80 s | 1.47 s | 2.33 s |

The 0.3 baseline created the longest tail: some chunks became very slow. The 0.7 baseline compressed the distribution toward short pauses. The 0.5 baseline preserved a median pause ratio similar to 0.3 and 0.4 while constraining the longest-pause tail.

This is why 0.5 emerged as the most plausible starting point. It was not the maximum of any single metric. It was the middle of several relevant distributions.

---

## Result Three: Exaggeration Was the Least Reliable Adjustment

We counted how many of the 24 chunks lost at least 250 milliseconds of internal pause time relative to the untuned version at the same baseline.

| Baseline | Exaggeration only | CFG only | Both |
|---:|---:|---:|---:|
| 0.3 | 8 | 6 | 8 |
| 0.4 | 11 | 7 | 10 |
| 0.5 | 11 | 7 | 9 |
| 0.6 | 8 | 5 | 9 |
| 0.7 | 10 | 4 | 9 |

Exaggeration-only produced significant pause loss in eight to eleven of the 24 chunks at every baseline. CFG-only was consistently safer by this measure, especially at 0.6 and 0.7, but “safer” did not mean deterministic.

Combined emotional tuning was highly passage-dependent. Its worst pause losses were:

| Baseline | Largest pause loss in one chunk |
|---:|---:|
| 0.3 | 1.21 s |
| 0.4 | 2.69 s |
| 0.5 | 1.31 s |
| 0.6 | 1.00 s |
| 0.7 | 0.63 s |

At baseline 0.4, one passage lost 2.69 seconds even though the average combined effect at that baseline was only a 0.13-second reduction. That gap between average behavior and worst-case behavior is exactly what makes an audiobook sound unpredictably edited. Most passages can be acceptable while a few conspicuous boundaries collapse.

CFG did sometimes compensate for exaggeration, as the Chatterbox guidance suggests. But the compensation was not stable across text. The model was not performing arithmetic in which “faster exaggeration plus slower CFG equals original pace.” Both values altered token generation, and their interaction depended on the passage.

---

## Result Four: “More Emotional” Did Not Produce a Consistent Acoustic Signature

If sentiment tuning were operating as intended, stronger emotional settings should have produced a reasonably consistent pattern: perhaps a wider pitch range, more energy variation, or a predictable change in speaking rate.

We did not observe that consistency.

Depending on the passage, combined tuning could:

- Add or remove roughly a second of internal silence.
- Raise or lower median pitch.
- Speed up or slow down the delivery.
- Increase or decrease dynamic range.

The direction and magnitude of pause change had almost no useful correlation with either VADER compound sentiment or the calculated passage intensity. The controls changed the audio, but the sentiment score did not reliably predict *how*.

Other indicators were reassuring but did not rescue the emotional method:

- No sustained clipping trend appeared at any baseline.
- Spectral flatness stayed near 0.23–0.24, with no clear noise trend.
- Spectral centroid stayed broadly around 2.56–2.63 kHz.
- Loudness dynamics remained similar across baselines.
- The timbre proxy moved by less than roughly 0.003 cosine similarity in paired comparisons, indicating little average voice-color drift.

In other words, emotional tuning was not obviously corrupting the waveform or replacing the speaker. Its failure was subtler: it changed phrasing and timing in ways that were difficult to predict and conspicuous to a listener.

---

## Why Fixed Seeds Matter—and What They Do Not Guarantee

Autoregressive TTS is stochastic. If baseline and emotional variants are generated with unrelated random samples, a cadence difference cannot be attributed cleanly to the parameters. Resetting the same seed before every paired render removed that obvious source of confounding.

But a fixed seed does not force two parameter settings to choose the same speech tokens. Once the probability distribution changes, the same random draw can cross a different decision boundary. From that point onward, sequences can diverge substantially. This is not a flaw in the experiment; it is the behavior being measured. A tiny conditioning change can push the model onto a different prosodic path.

The controlled conclusion is therefore not that exaggeration mathematically removes a fixed number of milliseconds. It is that changing exaggeration materially increases the probability of a different cadence, and that these cadence changes are often undesirable in multi-sentence narration.

---

## What We Would Measure Next

The current evaluator measures delivery density well, but total internal silence is not the same as punctuation fidelity. The next evaluation layer should align generated speech to the known text and calculate:

- Median pause after every period, question mark, and exclamation mark.
- Percentage of full stops with less than 150 milliseconds of silence.
- False pauses inside words or syntactic clauses.
- Sentence-by-sentence speaking rate.
- Sentence-final pitch movement and pitch reset after punctuation.

Whisper transcription would add word error rate, character error rate, omissions, repetitions, and hallucinations. A speaker-verification model such as WavLM or ECAPA-TDNN would replace the lightweight timbre proxy with a neural speaker-similarity score. A no-reference MOS predictor could help screen obvious degradation, although no automated MOS score should overrule a listening panel on literary narration.

The strongest final validation would be a blind paired listening test. Listeners should rate naturalness, voice fidelity, phrasing, appropriate expressiveness, and whether the delivery feels rushed or overacted. The automated sweep narrows the parameter space; it does not make aesthetic judgment unnecessary.

---

## Practical Recommendation

For this voice and this long-form nonfiction material:

1. Start at `exaggeration=0.5` and `cfg_weight=0.5`, Chatterbox's documented default pair.
2. Disable sentiment-driven exaggeration for the production audiobook.
3. Compare the plain 0.4 and 0.5 baselines by blind listening before committing to the full book.
4. If dynamic tuning must remain, test a much weaker CFG-only adjustment. Treat it as experimental, not guaranteed pacing control.
5. Preserve paragraph boundaries during preprocessing.
6. If sentence pauses must be guaranteed, synthesize at sentence boundaries and stitch explicit silence. Do not expect a creative-control parameter to enforce punctuation timing.
7. Add cache manifests that bind every generated chunk to its exact text, segmentation version, voice, seed, and synthesis parameters before allowing resume.

The recommendation is deliberately conservative. Baseline 0.3 produced the most silence but also the longest tail and slowest narration. Baseline 0.7 was compact and energetic but too rushed. Baseline 0.5 provided the best quantitative compromise: moderate pace, preserved pauses, controlled pause variance, stable broad timbre, and no clipping trend.

Most importantly, the experiment changed the diagnosis. The tempting fix was to remove NLTK. The evidence showed that would have targeted the wrong subsystem. NLTK preserved punctuation. Packing was an existing exposure, not a new regression. The audible change came from asking a generative model to reinterpret the performance on every chunk.

---

## The Broader Lesson

Names on model parameters are promises made by interfaces, not laws obeyed by models.

`exaggeration` sounds like a control over emotional amplitude. `cfg_weight` sounds like a control over adherence. In Chatterbox they influence the speech-token distribution, and the token distribution determines everything downstream: emphasis, pitch, rate, hesitation, sentence closure, and duration. The controls are useful precisely because they can alter a performance globally. That is also why they are dangerous in a long-form pipeline that needs local guarantees.

An audiobook has two different requirements:

- **Creative variation:** the narrator should not sound flat.
- **Structural invariants:** the narrator must finish sentences, preserve intelligibility, and pause where prose requires it.

Creative model controls can serve the first requirement. They cannot safely enforce the second. Structural invariants need structural mechanisms: preserved text boundaries, explicit generation units, deterministic stitching, cache validation, and tests tied to punctuation.

The missing pause was not a tokenizer bug. It was a systems-design lesson hiding in 1.04 seconds of silence.

