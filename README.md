# A character-and-BPE GPT for classical Arabic poetry

Building a small GPT from scratch on ~55,000 verses of classical Arabic, and
then asking a question the tutorials skip: **how should the text be cut up
before the model ever sees it, and how does that choice interact with the size
of the embedding space?**

The short version of what we found: it interacts a lot, and the two choices
cannot be made one after the other.

---

## Part 1 — The corpus

**Source.** [ARBML/MetRec](https://github.com/ARBML/MetRec) (MIT licence):
~55k verses scraped from الديوان, originally labelled by poetic meter. The
poetry is classical, so it is in the public domain. We drop the meter labels and
keep only the text.

Each line is one verse in the traditional two-hemistich form:

```
يا ضيف طيف ما هداه لمضجعي # الا لهيب في الحشي يتوقد
        صدر (first half)   #   عجز (second half)
```

The `#` is kept deliberately. It is a strong, perfectly regular structural
signal, and a small model picks it up quickly — it is the easiest way to see
whether the model has learned *anything* about form.

**Cleaning** (`prepare_arabic.py`): strip meter labels, NFKC-normalise
presentation forms, remove tatweel (the decorative kashida ـ), drop non-Arabic
characters, and collapse orthographic variants that the corpus is inconsistent
about: `إأآٱ → ا`, `ى → ي`, `ة → ه`. That last collapse matters later.

Two variants are produced:

| | verses | characters | distinct chars |
|---|---|---|---|
| `arabic_poems.txt` (no tashkeel) | 55,075 | 2,653,532 | 34 |
| `arabic_poems_tashkeel.txt` | 55,248 | 3,439,922 | 42 |

**Tashkeel** (تشكيل) are the short-vowel marks — fatha, damma, kasra, sukun,
shadda, tanwin. Everyday written Arabic omits them; poetry often keeps them
because they determine the meter. They are *combining* codepoints, so keeping
them makes the text ~30% longer in codepoints without making it longer in
letters.

---

## Part 2 — The model

A standard decoder-only transformer, following Karpathy's nanoGPT. Working
implementation in `chaaer_gpt.py`; the notebook contains the same thing in a
more configurable form.

### Self-attention

Each head projects the input into keys, queries and values, scores every
position against every earlier position, and takes a weighted average of the
values:

```
wei = q @ k.transpose(-2,-1) * head_size**-0.5
wei = wei.masked_fill(tril[:T,:T] == 0, -inf)     # causal mask
out = softmax(wei) @ v
```

The `head_size**-0.5` keeps the pre-softmax variance at ~1 regardless of head
width; without it, softmax saturates and gradients die. The lower-triangular
mask is what makes the model a *language* model — position *t* cannot see
position *t+1*.

Multiple heads run in parallel and their outputs are concatenated. Concatenation
alone leaves the channels unmixed, so a **projection** afterwards is what lets
heads actually combine information.

### The block

```python
x = x + self.sa(self.ln1(x))      # attention
x = x + self.ffwd(self.ln2(x))    # position-wise MLP, 4x expansion
```

Two details carry most of the weight:

- **Residual connections** (`x + ...`). Gradients flow straight through the
  addition to every earlier layer, which is the only reason a deep stack trains
  at all. Without them, adding layers makes results *worse*.
- **Pre-norm**. LayerNorm is applied to the *input* of each sublayer, not the
  output. This is why no learning-rate warmup is needed.

Attention moves information *between* positions; the MLP is where each position
computes on what it just gathered. Alternating the two is the whole design.

### Weight tying

```python
self.lm_head.weight = self.token_embedding_table.weight
```

The input embedding and the output projection are the same matrix. Both are
learning the same "what does this token mean" geometry, so sharing them removes
`vocab_size × n_embd` parameters and usually *improves* loss. With a 2048-token
vocabulary that is a large fraction of a small model.

---

## Part 3 — Tokenization

### Grapheme clusters first

Arabic diacritics are combining codepoints: `كَتَبَ` is 6 codepoints but 3
visible letters. A character-level model therefore spends half its context on
marks, and has to learn from scratch that a mark may only follow a letter and
never another mark.

So before anything else, each base letter is glued to its trailing marks and
*that* becomes the atomic symbol:

```
'كَتَبَ'  ->  ['كَ', 'تَ', 'بَ']
```

### BPE on top

Byte-Pair Encoding is a compression algorithm repurposed as a tokenizer. The
entire method:

1. Split the text into atoms (here: grapheme clusters).
2. Count every adjacent pair; find the most frequent.
3. Merge it into a new single symbol; add it to the vocabulary.
4. Repeat until the vocabulary reaches the target size.

No linguistics is involved — it simply notices which pairs keep co-occurring.
On this corpus it discovers real Arabic morphology by itself: `وَال`, `لِل`,
`ها`, and function words like `عَلَيهِ`.

Because the corpus is *inconsistently vocalised* — the same word appears both
bare and fully marked — BPE learns **both forms as separate tokens**. At vocab
2048, 1414 tokens carry tashkeel and 634 do not. The model gets marked and
unmarked variants in one vocabulary without any special handling.

Result at vocab 2048: **1.89 characters per token**, so sequences are roughly
half as long as character-level for the same text.

### Two implementation notes worth keeping

**The round-trip assertion.**

```python
assert tok.decode(tok.encode(text)) == text
```

This caught a genuine bug: the corpus contains *orphan diacritics* — a mark with
no base letter, on lines that literally begin `ِما`. The first cluster regex
required a base character, so those were silently deleted. The assertion matters
twice over: it prevents silent data loss, and it is what makes the bits-per-
character conversion below mathematically exact.

**Out-of-vocabulary fallback.** A cluster never seen in training (a vocalised
prompt fed to a tokenizer fitted on unvocalised text) is not in the vocabulary.
Rather than raising, `encode` falls back to individual codepoints. In-domain
text is unaffected.

**Speed.** Naive BPE recounts every pair after every merge and did not finish in
ten minutes. Keeping incremental pair counts plus an index from pair → words
containing it brings it to ~30 seconds.

---

## Part 4 — Measuring anything at all

This is the part that makes the rest of the study valid, and it is easy to get
wrong.

**Cross-entropy per token is not comparable across tokenizers.** A model that
has learned *nothing* scores `ln(34) = 3.53` on a character vocabulary and
`ln(2048) = 7.63` on a BPE vocabulary. And this is not an initialisation
artifact that training removes — it is a **units problem**. When one token
carries 1.9 characters, each prediction is doing 1.9× as much work, so a trained
BPE model shows a higher per-token loss than a trained char model *even when it
is the better model of Arabic*.

Measured on two identically-trained models, 600 iterations each:

| | val loss (nats/token) | bits per character |
|---|---|---|
| char | **2.46** | 3.55 |
| BPE-1024 | 4.02 | **3.45** |

The per-token column ranks char first by a wide margin. The BPC column ranks BPE
first. **One of these is backwards**, and it is the one everybody reads by
default.

### The fix

Because the tokenizer is lossless and deterministic, the chain rule gives

$$-\log P(\text{corpus}) = \sum_i -\log P(t_i \mid t_{<i}) = \mathcal{L} \times N_\text{tokens}$$

and that total is *tokenizer-independent* — chopping the text differently cannot
change the probability the model assigns to it. Dividing by a unit both schemes
share gives

$$\mathrm{BPC} = \mathcal{L}_{\text{nats/token}} \times \frac{N_\text{tokens}}{N_\text{chars}} \times \frac{1}{\ln 2}$$

A *nat* is a bit measured with `ln` instead of `log₂`; the `/ln 2` is pure unit
conversion.

### What BPC means concretely

Cross-entropy *is* code length (Shannon). A model at 3.4 BPC would compress this
text to 3.4 bits per character in an arithmetic coder. So classical compressors
are directly comparable and anchor the numbers:

| | bits/char |
|---|---|
| UTF-8 on disk | 14.16 |
| uniform guess over 34 chars | 5.09 |
| gzip | 4.65 |
| lzma | 3.66 |
| **small GPT, 600 iterations** | **3.45** |
| bzip2 | 3.44 |

A 340k-parameter model trained for under a minute already beats gzip and matches
bzip2. Shannon estimated English at ~1 bit/char for a human reader, so there is
a long way to go — but the number is now interpretable instead of abstract.

---

## Part 5 — The studies

### Study 1: how many merges?

Sweep vocabulary size (0 merges = character level) and measure BPC. The
tokenizer is fitted on the **training split only** — fitting it on the whole
corpus would leak validation text into the vocabulary.

Expect BPC to fall and then flatten. The flattening point is where extra
vocabulary stops buying compression and starts costing embedding parameters and
rare, undertrained tokens.

### Study 2: the 2D grid — and why it must be 2D

The obvious plan is: find the best vocabulary, then find the best `n_embd`. That
plan is **coordinate descent**, and it reaches the joint minimum only if the two
variables do not interact — i.e. if the valley of the loss surface runs parallel
to an axis. If the valley runs *diagonally*, coordinate descent stalls at a
point that is optimal along each axis separately and optimal in neither jointly.

There is a concrete mechanism forcing a diagonal valley here: the **softmax
bottleneck**. `lm_head` maps `n_embd → vocab_size`, so the matrix of achievable
log-probabilities has rank at most `n_embd`. A larger vocabulary genuinely
*requires* a larger `n_embd` to be representable. The parameters are coupled by
construction.

Preliminary evidence, from a reduced grid:

| n_embd | vocab = char | vocab = 1024 |
|---|---|---|
| 64 | **3.860** | 3.907 |
| 128 | 3.744 | **3.656** |

At width 64 character-level wins; at width 128 BPE-1024 wins. **The ranking
inverts.** Sequential optimisation would have returned a different answer
depending on which width happened to be fixed first. Note also that vocab 1024
at width 64 is *worse* than character level — more vocabulary actively hurts a
model too narrow to represent it. That is the bottleneck biting.

The notebook therefore sweeps `(vocab_size, n_embd)` **jointly**, on two
surfaces:

- **raw** — `n_layer` fixed. Bigger vocab ⇒ more parameters. Honest but confounded.
- **parameter-matched** — `n_layer` chosen per cell so total parameters land near
  a fixed budget, holding capacity constant so vocabulary is the only variable.

It reports, for each vocabulary, which `n_embd` won and which alternatives were
within one seed-standard-deviation of it, plus the gap between the
coordinate-descent answer and the joint answer.

### Study 3: the 2×2 — tashkeel × tokenizer

|             | char | BPE |
|-------------|------|-----|
| no tashkeel | A    | B   |
| tashkeel    | C    | D   |

Identical model configuration in all four cells, so the only thing varying is
how the text is represented. All four are prompted with **سميرة**.

**A trap in that prompt.** `سميرة` ends in *ta marbuta* (ة), which does **not**
appear in either corpus — the cleaner normalises ة → ه. Feeding the raw string
would make the tokenizer silently drop the final letter, leaving `سمير`
(*Samir*, a different and masculine name). The prompt is therefore put through
exactly the same normalisation as the training text. The notebook prints the
raw → used mapping so the substitution is visible rather than silent.

---

## Files

| file | what it is |
|---|---|
| `arabic_gpt_study.ipynb` | **the main deliverable** — self-contained Colab notebook running all three studies |
| `chaaer_gpt.py` | standalone finished GPT, trains on the plain corpus |
| `prepare_arabic.py` | downloads and cleans the corpus |
| `arabic_bpe.py` | grapheme-cluster BPE tokenizer |
| `study_core.py` | model + training + BPC used by the studies |
| `arabic_poems.txt` | cleaned corpus, no tashkeel |
| `arabic_poems_tashkeel.txt` | cleaned corpus, with tashkeel |

### Running it

Upload `arabic_gpt_study.ipynb` to Colab, set **Runtime → Change runtime type →
T4 GPU**, and Run All. Everything else downloads itself; nothing needs
installing. Roughly 60–90 minutes at full settings, or set `QUICK = True` for a
~10 minute check that it runs.

After Study 2, set `BEST_VOCAB` and `BEST_EMBD` to the winning cell before
running Study 3, so the 2×2 uses the measured optimum.

Outputs: `fig1_merges.png`, `fig2_grid.png`, `fig3_2x2.png`,
`samples_samira.txt`, and JSON for each study.

---

## Caveats

**Read the samples from the file, not the notebook.** Colab and most terminals
reorder right-to-left text when it is mixed with Latin characters and will
misrepresent whether the output is any good.

**This corpus is small.** ~1.8M BPE tokens against multi-million-parameter
models is far below the Chinchilla-optimal ratio of roughly 20 tokens per
parameter. Every cell in the grid is data-limited, so where the train/val gap is
wide you are measuring overfitting, not capacity.

**Check gaps against seed noise.** Differences of ~0.1 BPC are reported with
standard deviations over 3 seeds for a reason. A gap smaller than one standard
deviation is not evidence of anything.

**BPC is not a judge of poetry.** It measures how surprised the model was. A
model can compress well and still produce metrically broken, semantically empty
verse. The samples are there because the number cannot tell you that.

---

## References

- Vaswani et al., *Attention Is All You Need* (2017) — the architecture.
- Karpathy, *Let's build GPT: from scratch, in code, spelled out* — the
  implementation this follows.
- Sennrich et al., *Neural Machine Translation of Rare Words with Subword Units*
  (2016) — BPE as a tokenizer.
- Kaplan et al., *Scaling Laws for Neural Language Models* (2020) — loss depends
  mostly on non-embedding parameter count, and is remarkably flat with respect
  to the depth/width ratio. The source of the "aspect ratio ≈ 128" and
  "head dimension ≈ 64" rules of thumb used here.
- Yang et al., *Breaking the Softmax Bottleneck* (2018) — the rank argument that
  couples `vocab_size` to `n_embd`.
- Lan et al., *ALBERT* (2020) — factorised embeddings, the option in
  `study_core.py` for decoupling vocabulary size from hidden width.
- Alyafeai & Al-Shaibani, *MetRec* (2020) — the corpus.
