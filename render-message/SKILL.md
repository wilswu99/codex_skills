---
name: render-message
description: "Render a conversation message or Markdown with typeset LaTeX equations as a local HTML page in a new qutebrowser window. Use when Wilson asks to render an answer or read it outside the terminal, and by default for assistant messages containing more than one equation."
---

# Render Message

Use the bundled renderer instead of rediscovering Markdown or math-rendering tools.

## Wilson's preferences

- **Automatically render and open assistant messages containing more than one equation**, without waiting for a separate rendering request. Count equations whether inline or displayed; a mere mention of a variable is not an equation. Wilson can override this default for a particular response.
- Use **13pt body text** by default (about 17.3 CSS pixels), with the established light background, readable line spacing, centered text column, and typeset equations. A request for another size overrides this default.
- Preserve the message's wording, equations, emphasis, and links. For an "exact message" request, do not add a visible title, summarize, or re-explain the answer. A browser-tab title is fine.
- Open the result in a **new qutebrowser window** with the normal browser profile, both for explicit requests and for the automatic equation threshold above.
- These defaults apply to conversation messages, not unrelated documents. Messages below the equation threshold stay in chat unless rendering is requested.

## Render

Save the requested message, or the complete drafted response that triggers automatic rendering, as UTF-8 Markdown in a unique directory under `/tmp`, for example `/tmp/rendered-message-<id>/message.md`. Copy the Markdown source, including `\(...\)` and `\[...\]` math delimiters, rather than escaping it for display. Use a file-writing tool or a quoted heredoc so LaTeX backslashes, backticks, and dollar signs survive unchanged.

Run the helper shipped next to this skill:

```sh
python /home/wilson/.codex/skills/render-message/scripts/render_message.py /tmp/rendered-message-<id>/message.md --title 'Rendered message'
```

Optional arguments are `--output /path/to/message.html` and `--font-size 13` (points). The helper reports JSON containing the Markdown path, HTML path, file URI, rendered-math count, and font size. It preserves a Markdown companion to the HTML.

The helper uses installed `pandoc` and `node`, with bundled KaTeX assets. It renders equations into HTML and MathML before opening the page and embeds the CSS and fonts. **No network, CDN, browser JavaScript, or asset search is needed.** Unsupported math is an error to resolve, not a reason to silently show raw LaTeX. Source links such as `/path/file.tex:123` become browser file links with `#L123`; that fragment is not guaranteed to scroll a plain-text viewer to the line.

## Open

For an explicit browser request or automatic rendering, use the reported URI:

```sh
qutebrowser --target window file:///tmp/rendered-message-<id>/message.html
```

In this workspace-only sandbox, an ordinary qutebrowser launch is known to fail when creating `/run/user/1000/qutebrowser`. Use the execution tool's desktop-capable escalation for the authorized launch instead of repeating that failed sandbox attempt. Do not change global browser settings or switch to a temporary profile as a workaround. A successful GUI launch may leave the execution session running; do not terminate it merely to finish the turn.

A successful render and launch are sufficient for routine requests. Check further only if an error occurs or the user reports a display issue. Reply briefly that the window opened; do not repeat the full message in the terminal. If opening is blocked, retain and link the rendered HTML and report the actual blocker.
