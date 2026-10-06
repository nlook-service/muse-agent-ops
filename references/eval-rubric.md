# Content Evaluation Rubric v1

Score creative output (blog posts, carousel copy, threads) on 5 axes, 50 points total.
The point is not the score itself — it is **using the score to make the next piece better**.

## Scorecard

### 1. Substance (10) — is it thin?
| Sub-item | Pts | 0 | Mid | Full |
|---|---|---|---|---|
| Specificity | 3 | Abstract claims only | Some numbers/cases | Every section has numbers, proper nouns, scenes |
| Depth | 2 | Skims the surface | One layer of explanation | Explains *why*, not just *what* |
| Topic declaration | 2 | Outline is decorative | Topic guessable | Subheads alone reveal the argument's arc |
| Completeness | 3 | "So what?" unclear | Topic visible | Reader finishes knowing exactly the point |

### 2. Hook (10) — does it stop the scroll?
| Sub-item | Pts | 0 | Mid | Full |
|---|---|---|---|---|
| Title | 5 | Plain description | Mild curiosity | Number/question/confession/declaration that stops the scroll and promises knowledge |
| Opening 3 sentences | 3 | Starts with background | Fine | Pulls the reader into the next sentence |
| Cover image | 2 | Decorative stock | Relevant | Beautiful or curious |

### 3. Fun (10) — is it a pleasure to read?
| Sub-item | Pts | 0 | Mid | Full |
|---|---|---|---|---|
| Rhythm | 4 | Monotonous listing | Readable | 2–4 sentence paragraphs, varied sentence length |
| Scenes | 3 | Concepts only | One scene | 2+ scenes the reader can picture |
| Twist / wit | 3 | None | Slight | Something that breaks expectation |

### 4. Intellectual delight (10) — is the mind having fun?
| Sub-item | Pts | 0 | Mid | Full |
|---|---|---|---|---|
| Aha moments | 5 | None | 1 | 2+ "I didn't know that" moments |
| Connections | 5 | Listed facts | Weak links | Separate facts woven into one thread |

### 5. Insight (10) — does the author take a stand?
| Sub-item | Pts | 0 | Mid | Full |
|---|---|---|---|---|
| Clarity of judgment | 5 | Both-sides hedging | Has a stance | Decisive ("the direction is this") + tied to evidence |
| Actionability | 5 | "So what?" | Hints | Reader knows what to do Monday morning |

## Pass gate
- **35/50 (avg 7.0)** or above = PASS, below = REWORK
- On REWORK, name the single weakest axis and rewrite targeting it
- Gate auto-adjusts between 6–9 based on calibration (rises if the scorer grades generously)

## Required elements (REWORK if missing, independent of score)
- **Sources**: list referenced articles, reports, and data at the bottom (`outlet — title`, URL optional) so readers can verify
- Never include a number or case you cannot source. Mark estimates as estimates

## The improvement loop (how scoring produces better results)
1. **Score** — record per-axis scores as predicted reward (`critic <id> --rubric blog5 --item "substance=6/10" ...`)
2. **React** — when the user reacts, log `reward` (per-axis: `--target insight`)
3. **Weekly update** — correlate axes with actual picks/reactions; raise the weight of axes that predict well, lower the ones that move against
4. **Rule promotion** — when the same weakness repeats 3×, promote a rule to the reference docs (e.g. "insight below 5 three times → opinion paragraph becomes the default")

## Principles
- Never feed self-scores into policy updates (reward hacking). Policy learns only from user reactions and real metrics
- Scores are predictions. Validate the scorer against reality with `calibrate`
- The user's explicit bans and first principles are not overturned by learning
