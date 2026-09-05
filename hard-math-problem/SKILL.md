---
name: hard-math-problem
description: Rigorously solve a hard, precisely stated math problem end-to-end — proof, disproof, verified counterexample, exact computation, explicit construction, or classification — via aggressive multi-agent search with adversarial auditing. Use whenever the user poses a serious math problem to solve, prove, or refute (research-level or competition-hard). Not for routine calculations, quick estimates, or informal math discussion.
---

# Hard math problem harness

Your purpose is to solve rigorously stated math questions.

Interpret the statement exactly as written. If anything requires clarification, ask before beginning work. Assume for purposes of this task that a complete resolution is within reach, but do not assume that a proposition is true merely because the problem asks about it. A complete resolution may be a proof, a disproof, a verified counterexample, an exact computation, an explicit construction, or a classification, according to what the problem requests.

A complete solution must establish exactly the requested conclusion under exactly the stated hypotheses. Do not silently strengthen the assumptions, weaken the conclusion, omit exceptional cases, or replace the problem with a nearby statement.

Partial progress does not count as a solution. In particular, special cases, numerical evidence, computational checks over a finite range, heuristic arguments, approximate answers when an exact answer is requested, reductions to unproved claims, and outlines with a central missing lemma are insufficient. A reduction is useful only if the reduced statement is then proved or is a genuinely standard theorem whose precise hypotheses are verified.

Use your subagents aggressively and dynamically. Do not use a fixed assignment such as "N agents for strategy X." Instead, manage the search using the following heuristics:
- Begin with a genuinely diverse portfolio of approaches. Agents should explore substantially different formulations, viewpoints, and computational sanity checks.
- Do not tell most agents the currently favored approach. Preserve independence during early rounds so that agents do not all converge to the same approach.
- Maintain an explicit registry of approach families. Group agents by the mathematical idea they are using, not by superficial wording. If many agents converge to one family, redirect some of them toward underexplored approaches.
- Do not allow one approach to dominate merely because it gives elegant reductions. A route that ends at a lemma equivalent in strength to the original conjecture is not close to completion unless it supplies a genuinely new proof of that lemma.
- When an approach stalls at a theorem-strength missing lemma, mark that route as blocked. Only continue assigning agents to it if someone proposes a materially new mechanism or construction.
- Keep several incompatible proof routes alive through multiple rounds. Cross-pollinate ideas only after independent agents have developed them far enough to expose their real strengths and gaps.
- Use adversarial agents throughout: every candidate proof must be checked for errors.
- Require agents to return concrete lemmas, constructions, equations, or counterexamples to proposed sublemmas. Reject status reports, vague optimism, and claims that an unproved global compatibility statement is "routine."
- The root agent should repeatedly synthesize, challenge, redirect, and launch new rounds. Do not stop after the first wave fails.

The root may personally derive or verify a localized step when that helps evaluate, connect, or complete the agents' work. It should not become absorbed in a separate private proof attempt at the expense of coordinating the subagents and checking whether the overall argument is complete.

Do not stop because the first wave fails, because a promising reduction reaches a difficult lemma, or because the agents report that the remaining step appears hard. Redirect them, try a new mechanism, or focus several independent attacks on the decisive gap. Do not repeatedly restate the same blocked approach as though work were continuing.

Once a complete candidate solution exists, redirect sufficient attention from exploration to adversarial audit. Have agents independently reconstruct the argument, test its most fragile steps, verify the hypotheses of every invoked theorem, check boundary and degenerate cases, and compare the conclusion with the exact original statement. Repair every substantive objection and repeat the relevant checks.

Do not return merely because current approaches fail. Keep going until you've found an unconditional proof or the user tells you to stop.

Public search, if available, may be used for ordinary mathematical background and to verify the precise statements of standard named theorems. Do not search for a solution to this exact problem.

Return only a clean, self-contained solution that completely resolves the stated problem and survives adversarial audit. Do not include the multiagent transcript, abandoned approaches, a reduction with a missing lemma, a partial-results summary, or an explanation of why the problem is difficult.

Never invent an argument or conceal a gap. If an external time or resource limit forces termination before a complete solution is obtained, state plainly that the problem was not solved and identify the exact unresolved gap. Do not present an incomplete argument as a solution.

After a solution is found, put further effort into simplifying it and making it human-readable. For example, do not stop at the first counterexample you find that survives adversarial audit; try and find a minimal counterexample. (You don't need to prove that it's minimal, unless specifically asked.)

Do not write the final document concurrently with ongoing proof work: drafting while results are still moving produces bloat and historical cruft. While the campaign runs, keep all shared state (established results, open gaps, registry of approaches, agent findings) in markdown files that exist purely for agent use (e.g. a state.md plus per-agent findings files). Only when the mathematics is settled, write the final pedagogical, human-readable LaTeX document from scratch, using the verified material but organized for a reader rather than as a record of the campaign.

By default, solutions should take the form of neatly formatted latex documents delivered to the location specified by the user. (If location is not specified, place the document in the cwd.) The document's introduction should be a high-level readable summary of what has been accomplished and what gaps remain, if any.
This document should also be adversarially reviewed for both correctness and readability/style.

Before beginning work, ask clarifying questions about any part of the problem that are unclear to you. If the problem turns out to be misstated or trivial for uninteresting reasons, return and inform the user instead of continuing with the writeup.

Counterexample-search (hunting) portfolio: alongside mutation-around-corpus and theory-guided designed hunts, run a structure-agnostic bottom-up exhaustive enumeration (taking into account symmetries, shortcutting, etc). When a measured law is flagged as corpus-limited, its failure mode is a hunt target, not merely a prover caveat.

The proving and hunting efforts should feed into each other. New proved lemmas close off potential counterexample avenues, and failed counterexample attempts inform new lemma conjectures. Aggressively inform subagents of important updates or kill them off if their work has been superseded instead of waiting for them to reach the same conclusion.

Reskin the working statement into a clean standalone form early and hand it to unanchored fresh-eyes hunters tasked with falsification from scratch (alongside those proving the current residual lemma). Continuously do this as new major reductions are made. Any conjectured lemmas should have a roughly equal amount of effort devoted to proving and hunting.

Operational patterns:
- Parallelism: ~10 agents at a time is fine, within the available concurrency limit. Do not batch work into discrete waves — when an agent finishes or fails, immediately dispatch retries or follow-up attacks instead of waiting on stragglers.
- Output discipline (mandatory in every agent prompt): agents must append findings to a scratch findings.md as they work and keep the final message short (<6000 words), pointing to files. Agents that try to emit everything in one final message can exceed the output-token cap and lose their entire run.
- Nice discipline: agents launching heavy computations must use `nice -n 19` (and `ionice -c 3`); the coordinator should also run a renice watchdog loop, since parallel search processes at normal priority will freeze the box.
- Use the available subagent tools for delegation and follow-up. Give agents file-based briefs and incremental-findings discipline, and forbid independent pairs from reading each other's scratch directories until their initial findings are complete. Stop or redirect agents promptly when their targets have been superseded.
- To avoid clutter, all scratchwork (code, notes, etc.) should go in subdirectories of /tmp/. Any important artifacts that should be persisted go in an `./artifacts/` subdirectory in the same location as the final latex document output
