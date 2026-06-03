# Neural-Matrix-sim 

A step-by-step evolution of agent-based simulation — from bare demographic modelling to full neural-network-driven NPCs. Each file in this repo is a distinct generation of the engine, building progressively more complex behaviour on top of the last.

---

## Project Philosophy

This project was built to answer one question: *what is the minimum amount of machinery needed to make a simulated agent feel alive?*

The answer turned out to be more than just randomness. It required economics, biology, mortality risk, social class, neural decision-making, and reinforcement learning — added one layer at a time, across five generations of code.

---

## Generation Overview

```
War_simulator.py       → Gen 0: Nation-level conflict & peace learning
Life_simulator.py      → Gen 1: Population demographics, metabolism, class mobility
Sandbox_life.py        → Gen 2: Persistent AI agent, cross-session memory, lineage tracking
Brained_NPC.py         → Gen 3: Neural brains, migration decisions, reinforcement
NPC_advanced.py        → Gen 4: Transit authority, marital regimes, divorce engine
```

---

## Gen 0 — `War_simulator.py`

> **Hand-built from scratch.**

A two-nation conflict simulator that models how military powers decide between war and diplomacy over time. Nations aren't static — they *learn* from outcomes.

**Core mechanics:**
- Configurable military might and peace preference per nation
- Probabilistic yearly conflict rolls
- Three post-war psychological responses: Revanchist Grudge, Hegemonic Submission, Stalemate Deterrence
- Pyrrhic victory detection — winners who pay too high a cost become more peace-seeking
- Peace calibration drifts over time based on accumulated experience

**What it demonstrates:** Emergent diplomacy from simple feedback rules. Two nations with identical starting stats can end in very different places depending on early conflict luck.

---

## Gen 1 — `Life_simulator.py`

A full demographic simulation across three continental sectors (Europe, Asia, Africa). Introduces individual civilians with biometric state, a food/energy metabolism loop, and social class mobility.

**Core mechanics:**
- `Civilian` class with energy, food supply, savings, age, and attraction drive
- Overcrowding detection per sector with dynamic energy drain penalties
- Mortality from starvation, overcrowding, old age, and disease (class-weighted risk)
- Procedural courtship with diminishing fertility returns and twin/triplet rolls
- Social class transitions (Poor → Middle → Wealthy and back) based on savings and energy
- `SimulationTracker` demographic ledger with full JSON export

**Economy modes:** Barter or cash-based, selectable at runtime.

---

## Gen 2 — `Sandbox_life.py`

Introduces a single persistent AI agent running alongside the NPC population. This agent has a brain that persists between runs via disk storage, accumulating learned behaviour across separate simulation sessions — the first appearance of a neural network in the project.

**Core mechanics:**
- `AISandboxBrain` — 5-weight sigmoid brain, saved to `ai_sandbox_brain.json` after each run
- AI makes real-time decisions on courtship consent and continental migration
- Consent probability computed from `[energy, savings, density, age, partner_class]` inputs
- Reinforcement: `update_weights()` called with `+20.0` on successful birth, `-0.5` on failed match, `-0.1` on rejection
- Migration triggered when brain output exceeds 0.75 and savings cover travel cost
- Full lineage tracking: children IDs, marriage history, courtship rejections, biometric snapshots
- Outputs `ai_lineage_report.json` — a complete life biography of the AI agent

---

## Gen 3 — `Brained_NPC.py`

Scales the neural approach from one agent to the entire population. Every NPC now carries its own `NPCBrain`, brains are inherited by children, and outcomes feed back into weight updates via operant conditioning.

**Core mechanics:**
- `NPCBrain.think()` — sigmoid activation over `[energy, savings, density, age, context]`
- Neural migration decisions: agents move when their brain output exceeds a threshold
- `apply_behavioral_reinforcement()` — operant conditioning based on outcomes:
  - `STATIONARY_INTEREST_GAIN`: rewards staying put when savings grow
  - `MIGRATION_TAX_PUNISHMENT`: penalizes impulsive moves that drain savings
  - `OVERCROWDED_SUFFOCATION`: trains escape instincts in high-density zones
- Weight inheritance: children receive averaged parent brain weights, then mutated via Gaussian noise
- Central bank dividend system that rewards stationary wealth accumulation
- Random world events (natural disasters, disease outbreaks)
- Per-agent biography JSON written to `lobby/` (living) or `cemetery/` (dead) directories
- Analytics CSV export via pandas with brain weight columns included

---

## Gen 4 — `NPC_advanced.py`

The most complex generation. Adds a full intercontinental transit economy and marital property law on top of the neural population. NPCs now book tickets, face cancellations, and choose between two legal financial regimes when they marry.

**Core mechanics:**
- `TransitAuthority` (ITA) with a fleet of planes and ships, each with capacity limits and dynamic pricing
- Final-call confirmation: sick or broke NPCs cancel last-minute, paying a penalty
- Overbooking protection: bumped passengers get rescheduled, not killed
- Spouse co-travel: married partners board together automatically
- `NPCBrain` upgraded to an 8×8 weight matrix with `tanh` activation — 8 inputs, 8 outputs
- Procedural courtship with marital property regime selection:
  - **Communist regime**: pooled savings, split equally on divorce
  - **Separate regime**: independent finances throughout
- Staggered divorce engine: couples re-evaluate compatibility each year
- Per-agent JSON biographies + CSV stats file

---

## Output Files

| File | Source | Contents |
|---|---|---|
| `simulation_ledger.json` | `Life_simulator.py` | Full demographic registry of every NPC |
| `simulation_agent_data.csv` | `Brained_NPC.py` | Per-agent stats including brain weight columns |
| `regime_simulation_agent_data.csv` | `NPC_advanced.py` | Agent stats with marital regime column |
| `ai_sandbox_brain.json` | `Sandbox_life.py` | Persisted AI brain weights (cross-session memory) |
| `ai_lineage_report.json` | `Sandbox_life.py` | AI agent's complete life history |
| `lobby/*.json` | Gen 2 & 3 | Biography files for agents still alive at simulation end |
| `cemetery/*.json` | Gen 2 & 3 | Biography files for deceased agents |

---

## Sample AI Lineage Output

```json
{
  "agent_assigned_gender": "F",
  "total_kids_count": 4,
  "final_status": "Dead",
  "cause_of_death": "Energy Exhaustion (Overcrowding / Starvation)",
  "year_of_death": 5,
  "biometric_history_log": [
    { "year": 1, "age": 18, "energy": 100, "savings_bank_balance": 0.0 },
    { "year": 5, "age": 22, "energy": 10,  "savings_bank_balance": 0.0 }
  ]
}
```

---

## Running the Simulations

Each file is a standalone script. Run them in order to follow the evolution, or jump straight to any generation.

```bash
# Gen 0 — War simulator
python War_simulator.py

# Gen 1 — Life simulator (prompts for population size and economy mode)
python Life_simulator.py

# Gen 2 — Persistent AI sandbox agent
python Sandbox_life.py

# Gen 3 — Neural NPCs with reinforcement
python Brained_NPC.py

# Gen 4 — Transit authority and marital regimes
python NPC_advanced.py
```

**Dependencies:** Standard library only (`random`, `json`, `os`, `math`, `shutil`). `pandas` is optional in Gen 2 for CSV export.

---

## What's Next

- Increase neural network dimensionality and layer depth
- Add attention-style context-sensitive decision weighting
- Replace JSON biography storage with NumPy binary (`.npy` / `memmap`) for scale
- Approximate nearest-neighbour indexing (FAISS / Annoy) for large-population courtship matching
- Cross-generational trait inheritance graphs

---

## Observed Findings

These are real patterns extracted from actual simulation runs, studied by pulling random agents from `lobby/` and `cemetery/`, extrapolating from the sample to the generation as a whole.

### War Simulator (Gen 0)

- **Equal powers, both peace-leaning (>50%):** Peace almost always wins out by the end. Diplomatic resolutions compound — each successful negotiation raises both sides' peace calibration, creating a self-reinforcing loop that makes further conflict increasingly unlikely. End-state peace preference converges toward 100%.
- **Dominant power prefers peace, weaker power is hostile:** Even with an aggressive smaller nation, the larger one's willingness to absorb costs and negotiate pulls the outcome toward peace over a long enough timeline. The weaker side's hostility gradually loses leverage.
- **Both powers hostile (<50% peace, roughly equal):** No stabilising force emerges. They fight until one side's military might is ground down to the floor. The simulation produces a clear hegemon or a mutual ruin scenario — diplomacy never gets a foothold.

### Life Simulator (Gen 1)

- Primarily used as a jumping-off point to test agent behaviour before adding neural machinery.
- **Barter economy is a meat grinder** — without cash reserves to buy food in emergencies, agents spiral into energy exhaustion fast, producing high early mortality rates.

### Sandbox Life (Gen 2)

- Introduced the first neural marriage decision. In testing, **the AI agent never rejected a marriage proposal** — its brain consistently output a consent probability above 0.5 regardless of partner quality or personal state.

### Brained NPC (Gen 3)

- With brains distributed across the whole population, **agents began rejecting reproduction** even within successful marriages — the second neural output controlling childbirth would fall below the threshold.
- Despite that, **male-biased or female-biased starting populations outperformed 50/50 splits in total population growth.** This was studied by pulling samples from both `lobby/` (survivors) and `cemetery/` (deceased) and extrapolating the pattern across the generation.

### NPC Advanced (Gen 4)

- Simulations consistently collapse around year 70 — the entire population dies off, with the cemetery accumulating nearly everyone by that point.
- The **pre-booking transit system** changes agent behaviour meaningfully: rather than panicking and immediately fleeing overcrowded regions, agents now plan 1–3 years ahead. Seats are limited and slightly overbooked, so booking early is a gamble — and at departure time, the agent gets one final chance to cancel if their finances or energy have deteriorated.
- When an agent boards, their **spouse is automatically carried along**, keeping families together across continental moves.
- **Marital property regimes** — Communist (pooled finances) vs. Separate (independent balances) — affect long-term survival differently. Divorce is modelled and can extend individual lifespan by freeing agents from draining partnerships.

---

## Disclaimer

This project is built purely for **educational and research purposes** — to explore emergent behaviour, reinforcement learning, and agent-based modelling from first principles.

The simulations are abstract computational models. The mechanics of mortality, class, reproduction, migration, and conflict are **gross simplifications** designed to produce interesting system dynamics, not to model or represent real human lives, societies, demographics, or geopolitics. Any resemblance to real-world outcomes is coincidental and should not be interpreted, cited, or extrapolated as commentary on actual populations or political systems.

---

## Author

Built by [@itzvarunv](https://github.com/itzvarunv) as a self-directed exploration of emergent behaviour, neural plasticity, and agent-based modelling from first principles.
