# Tortured Phrases Detection

Tortured phrases are machine-paraphrased synonyms produced by older paraphrasing tools
(SpinBot, article spinners) and paper mills. They are DISTINCT from LLM-generated text —
LLMs generally don't produce these because they understand semantics.

Over 42,500 papers have been flagged and 3,000+ retracted based on tortured phrases.

## How to Use

Scan the manuscript for any phrases from the lists below. A SINGLE confirmed tortured
phrase is a MAJOR flag — these do not occur in legitimate writing.

## High-Confidence Tortured Phrases

These are well-documented substitutions. Any occurrence is near-definitive evidence
of paper mill origin.

| Tortured phrase | Intended term |
|----------------|---------------|
| amino corrosive | amino acid |
| anaerobic devastation | anaerobic digestion |
| artificial intelligence network | artificial neural network |
| big number crunching | big data analytics |
| boiling acid | hydrochloric acid |
| brand name protein | branded protein |
| browning focus point | Brownian focal point |
| compound hydrogen | hydrogen compound |
| counterfeit neural systems | artificial neural networks |
| deep learning framework | deep learning model |
| dim going | dark matter |
| enormous information | big data |
| false neural system | artificial neural network |
| fitness demonstrating | genetic modeling |
| glucose bigotry / glucose narrow-mindedness | glucose intolerance |
| grand neural system | large neural network |
| hard silver | sterling silver |
| harsh corrosive | strong acid |
| huge information preparing | big data processing |
| human experience disclosure | human exposure assessment |
| inherited recurrence | genetic recurrence |
| Internet of Things framework | IoT system |
| natural forces | chemical reactions |
| profound learning | deep learning |
| sham neural system | artificial neural network |
| shrewd gadgets / brilliant gadgets | smart devices |
| sign of rapidity | velocity vector |
| warm water | hot water (thermal) |
| writing soft copy | writing digitally |

## Pattern-Based Detection

Beyond specific phrases, look for these patterns that indicate machine paraphrasing:

### Synonym substitution of technical terms
The paraphraser doesn't understand that technical terms are fixed vocabulary:
- "convolutional neural network" → "convolutionary brain system"
- "random forest" → "arbitrary woodland"
- "support vector machine" → "bolster vector machine"
- "Internet of Things" → "Web of Things" / "System of Things"
- "machine learning" → "apparatus learning" / "gadget learning"

### Awkward circumlocution
Simple concepts described in unnecessarily complex ways:
- "water" → "the aqueous medium"
- "patients" → "the clinical subjects under observation"
- "data" → "the informational substrate"

### Field-specific terms replaced with general synonyms
- Medical: drug names replaced with chemical descriptions
- CS: algorithm names paraphrased
- Physics: standard notation described verbally

## Scoring

| Finding | Flag weight |
|---------|------------|
| 1+ confirmed tortured phrase | **MAJOR** (paper mill indicator) |
| Consistent synonym-substitution pattern for technical terms | **MAJOR** |
| Occasional awkward phrasing without clear pattern | Investigate further, not conclusive |

## Important Distinction: Tortured Phrases vs. LLM Markers vs. Non-Native English

| Signal | Source | Example |
|--------|--------|---------|
| Tortured phrase | Paper mill / spinner tool | "amino corrosive" for "amino acid" |
| LLM marker | ChatGPT / Claude / etc. | "delve into the intricacies" |
| Non-native English | Human ESL writer | "we made experiment on 50 subjects" |

These are three different phenomena with different implications:
- **Tortured phrase** → likely paper mill, MAJOR integrity flag
- **LLM marker** → possibly AI-generated, needs density assessment
- **Non-native English** → human writing, NOT a red flag

Do NOT confuse non-native English grammar errors with tortured phrases.
Tortured phrases are semantically wrong (wrong word entirely), while non-native
English has correct vocabulary but imperfect grammar.
