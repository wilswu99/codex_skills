#!/usr/bin/env python3
"""Render Markdown and TeX math into a portable, offline HTML reading page."""

import argparse
import base64
import html
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import quote


def run(command, stdin=None):
    result = subprocess.run(command, input=stdin, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{command[0]} failed:\n{result.stderr.strip()}")
    return result.stdout


def positive_points(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("font size must be a positive number of points")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="UTF-8 Markdown source")
    parser.add_argument("--output", type=Path, help="HTML output (default: input with .html suffix)")
    parser.add_argument("--title", help="Browser tab title; not inserted into the message")
    parser.add_argument("--font-size", type=positive_points, default=13, help="Body font in points (default: 13)")
    args = parser.parse_args()
    source = args.input.expanduser().resolve()
    output = (args.output or source.with_suffix(".html")).expanduser().resolve()
    markdown = output.with_suffix(".md")
    if output in (source, markdown):
        raise ValueError("HTML output must differ from both the source and companion Markdown path")
    for program in ("pandoc", "node"):
        if not shutil.which(program):
            raise RuntimeError(f"Required dependency '{program}' is missing from PATH")
    assets = Path(__file__).resolve().parent.parent / "assets" / "katex"
    for name in ("katex.js", "katex.css", "fonts"):
        if not (assets / name).exists():
            raise RuntimeError(f"Bundled KaTeX asset is missing: {assets / name}")

    original = source.read_bytes()
    document = json.loads(run([
        "pandoc", "--from=markdown+tex_math_single_backslash+tex_math_dollars-smart",
        "--to=json",
    ], original.decode("utf-8")))
    math_nodes = []

    def visit(value):
        if isinstance(value, dict):
            if value.get("t") == "Math":
                math_nodes.append(value)
            elif value.get("t") == "Link":
                target = value["c"][-1]
                match = re.fullmatch(r"(/.*):(\d+)", target[0])
                if match:
                    target[0] = "file://" + quote(match[1], safe="/%") + "#L" + match[2]
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(document)
    if math_nodes:
        renderer = r"""
const katex = require(process.argv[1]);
let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  try {
    const result = JSON.parse(input).map(({tex, display}, index) => {
      try {
        return katex.renderToString(tex, {displayMode: display,
          throwOnError: true, strict: 'error', trust: false, output: 'htmlAndMathml'});
      } catch (error) {
        throw new Error(`Math expression ${index + 1}: ${error.message}`);
      }
    });
    process.stdout.write(JSON.stringify(result));
  } catch (error) {
    process.stderr.write(error.message + '\n');
    process.exitCode = 1;
  }
});
"""
        expressions = [{"tex": node["c"][1], "display": node["c"][0]["t"] == "DisplayMath"}
                       for node in math_nodes]
        rendered = json.loads(run(["node", "-e", renderer, str(assets / "katex.js")],
                                  json.dumps(expressions)))
        for node, markup in zip(math_nodes, rendered):
            node.clear()
            node.update(t="RawInline", c=["html", markup])

    body = run(["pandoc", "--from=json", "--to=html5"], json.dumps(document))
    css = (assets / "katex.css").read_text(encoding="utf-8")

    def embed_font(match):
        font = assets / match[1]
        mime = {".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf"}[font.suffix]
        encoded = base64.b64encode(font.read_bytes()).decode("ascii")
        return f"url(data:{mime};base64,{encoded})"

    css = re.sub(r"url\(['\"]?(fonts/[^)'\"]+)['\"]?\)", embed_font, css)
    styles = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; background: #fafaf8; color: #20242b;
       font: FONT_SIZEpt/1.7 system-ui, -apple-system, "Segoe UI", sans-serif; }
article { max-width: 920px; margin: 0 auto; padding: 48px 44px 72px;
          background: #fff; min-height: 100vh; overflow-wrap: break-word; }
p { margin: 0 0 1.15em; }
strong { font-weight: 680; color: #172b40; }
a { color: #205d9e; text-underline-offset: 3px; }
h1, h2, h3, h4 { line-height: 1.3; }
pre { padding: 1em; background: #f5f6f7; overflow-x: auto; }
code { font-size: 0.9em; }
blockquote { margin-left: 0; padding-left: 1em; border-left: 3px solid #d5dce3; }
table { border-collapse: collapse; display: block; max-width: 100%; overflow-x: auto; margin: 1em 0; }
th, td { border: 1px solid #d5dce3; padding: 0.4em 0.7em; text-align: left; }
th { background: #f5f6f7; }
img { max-width: 100%; }
.katex { font-size: 1.1em; }
.katex-display { overflow-x: auto; overflow-y: hidden; padding: 0.35em 0; margin: 1.1em 0; }
@media (max-width: 640px) {
  article { padding: 26px 20px 48px; }
}
@media print {
  body { background: white; }
  article { padding: 0; max-width: none; }
  .katex-display { break-inside: avoid; }
}
""".replace("FONT_SIZE", f"{args.font_size:g}")
    title = html.escape(args.title if args.title is not None else source.stem)
    page = ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
            f'<title>{title}</title>\n<style>{css}\n{styles}</style></head>'
            f'<body><article>{body}</article></body></html>\n')
    output.parent.mkdir(parents=True, exist_ok=True)
    if markdown != source:
        markdown.write_bytes(original)
    output.write_text(page, encoding="utf-8")
    print(json.dumps({"html": str(output), "markdown": str(markdown),
                      "uri": output.as_uri(), "math_count": len(math_nodes),
                      "font_points": args.font_size}))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError) as error:
        print(f"render_message: {error}", file=sys.stderr)
        sys.exit(1)
