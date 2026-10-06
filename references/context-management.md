# Context Management v1

How to keep the agent's context (and token cost) under control.

## 1. Proactive warning → fresh chat
- Before starting heavy work, or when the conversation feels long, check context usage (`muse.session_status`).
- **If usage exceeds 80%, warn the user first and propose starting a fresh chat.** Continue in the new chat only after the user approves.
- Context grows every turn (user messages + replies + tool results). It auto-compacts at the trigger threshold, but a fresh chat is cheaper than a compacted one for new work.

## 2. Base context diet
- The standing context (memory files, injected docs) loads every turn. Keep it tight.
- `MEMORY.md`: promote only what lasts; move one-off history to dated archive notes (`~/memory/archive/`). A periodic pass that cut 54KB → 5KB is the reference.
- What you cannot shrink (runtime-owned): system prompt, tool schemas. Don't try — work around them.

## 3. Verification by the producing agent
- When work is delegated to an external agent, that agent also performs the validation (rubric self-score, lint).
- The hub agent does NOT re-read and re-score the output — verification itself costs tokens. It only relays the reported score and publishes.

## 4. Routing heavy work out
- Light work (lookups, short replies, fixed pipelines): hub agent directly.
- Heavy work (deep writing, rewrites, analysis, design): external agent. See `references/agent-router.md`.
- If the external agent is unresponsive or busy, the hub falls back and does it directly.

## 5. What grows context fastest
Ranked by observed cost:
1. Base context (every turn — fixed cost)
2. Reading full files repeatedly (read once, or don't re-read delegated output)
3. Browser research dumps
4. Long briefs the hub writes itself (keep them short; let the external agent reuse)
5. Repeated validation passes
