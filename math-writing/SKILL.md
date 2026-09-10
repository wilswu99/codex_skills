---
name: math-writing
description: Use whenever writing from scratch or fully rewriting mathematical papers, technical notes, and substantial proofs in LateX. Use for substantive mathematical exposition and readability revisions. Do not use for small edits or routine calculations.
---

# Math writing

Make the mathematical structure visible. A reader scanning definitions and result statements should recover all technical claims, their assumptions, and their relationships; proofs supply the derivations. These are Wilson's defaults, subject to the current task's instructions.

When writing a new document from scratch, use your model name (e.g. `GPT-6 Astra`) in the author field.
For rewrites, preserve the existing author.

## Structure the exposition

- Use explicit `definition`, `lemma`, `theorem`, `proposition`, `corollary`, `proof`, `remark`, and `example` environments where appropriate. Label definitions and result statements, and other blocks when they need cross-references.
- Keep prose outside these blocks for orientation: explain the goal, intuition, upcoming steps, or what has been established. Put definitions and technical assertions in statement blocks. Remarks and examples can explain or illustrate results, but a fact needed later belongs in a labeled result that can be cited.
- At the start of each section, explicitly reference the lemma(s) or theorem(s) it will establish and intuitively summarize their meaning. Make the rest of the section serve those goals. Continue this pattern in subsections when they have their own intermediate goals; foundational sections can point to the later results their definitions support.
- Order definitions and results so prerequisites are available before use. A forward reference in a section's roadmap is fine; a proof should not depend on an unstated result or a claim buried in another proof.
- Do not merely wrap a dense paragraph in a lemma environment. Identify its actual claim, state its hypotheses and conclusion, and separate the argument into a proof.

## Expose dependencies and notation

- State a non-elementary result imported from the literature in a labeled lemma or theorem before using it. Give the precise version and assumptions needed here. Its proof may be a citation, preferably with a theorem or page locator. Verify that the source supports the statement; do not invent a citation or strengthen a cited result silently.
- Common undergraduate or first-year graduate tools, such as Markov's inequality, Chernoff bounds, and Hölder's inequality, need not receive separate statement environments.
- Whenever using a previous result (lemma, theorem, proposition, or corollary), explicitly reference it with `\ref` or the document's equivalent cross-reference command. Make clear why its hypotheses hold, especially when changing conditioning, domains, or parameter ranges. Avoid vague substitutes such as “as above.”
- Use consistent notation. Define indices, dimensions, parameters, and randomness before use, and use a shared notation map when several editors work on a document.
- In the MLP setting, use `Z` for preactivations and `X` for postactivations. (For other settings, ignore this.)

## Develop proofs at a readable pace

- Break multi-step arguments into explicit steps, with intermediate equations wherever they clarify a transformation, estimate, or logical implication. Do not compress a difficult argument into a single sentence or a paragraph of pure prose.
- Explain what each important equation accomplishes and justify transitions. Avoid the opposite extreme of an unexplained wall of equations.
- State the hypotheses and quantifiers needed for the conclusion. Where material, make uniformity, constant dependencies, independence and conditioning, exceptional events, remainder bounds, and the order of limits explicit.
- Preserve the original mathematical meaning throughout an exposition rewrite. If a gap or error requires a changed hypothesis, conclusion, or algorithm, check the correction and dependent statements and explicitly report the substantive change. Do not conceal an unresolved issue behind polished prose.

## Rewrite and review a document

1. Read the whole requested document, including included source files, line by line. A flagged passage is an example, not a limit on a requested full rewrite. Map the main results, dependencies, notation, and existing environments before reorganizing.
2. Rewrite every part that needs it. Keep the requested scope: a local edit does not authorize unrelated changes across a paper.
3. When parallel section editing is useful, assign disjoint ownership and share notation, label conventions, section goals, and dependencies before editing. Coordinate interface changes. The root editor must read the assembled document and own its sequencing, references, and coherence from beginning to end.
4. For a substantial mathematical rewrite, send the complete diff to an independent reviewer subagent after assembling the rewrite, with access to the resulting document and relevant sources. Request both mathematical correctness and clarity checks: altered assumptions or conclusions, missing proof steps, circular dependencies, inaccurate imported results, inconsistent notation, and compressed exposition. If reviewer tools are unavailable, disclose that limitation and perform a separate review pass.
5. Evaluate and incorporate the reviewer's suggestions, checking any mathematical changes rather than accepting them blindly. Recheck affected dependencies and obtain focused follow-up review when a correction changes the argument materially.
6. For LaTeX, build the document with enough passes to resolve cross-references, check undefined or duplicate labels and relevant layout warnings, and update the expected PDF artifact. Run relevant existing mathematical or computational checks when the revision could affect their claims. Report remaining problems and any substantive corrections.
