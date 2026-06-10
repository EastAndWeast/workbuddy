#!/usr/bin/env python3
"""Convert Markdown to HTML using the markdown library.

Usage:
    python3 convert_md_to_html.py <input.md> [output.html]

If output path is omitted, writes alongside input as .html.
"""

import sys
import os
import re


def md_to_html(md_text: str) -> str:
    """Convert Markdown to HTML using markdown library (with extensions)."""
    try:
        import markdown as md_lib
        return md_lib.markdown(md_text, extensions=['extra', 'codehilite', 'nl2br'])
    except ImportError:
        print("⚠️  markdown library not found, using basic fallback.")
        print("   Install it:  pip install markdown")
        return _md_to_html_fallback(md_text)


def _md_to_html_fallback(md_text: str) -> str:
    """Minimal fallback converter – handles **bold**, links, headers, lists."""
    lines = md_text.strip().split('\n')
    html_lines = []
    in_ul = False
    in_ol = False
    num_pattern = re.compile(r'^(\d+)\.\s')

    def _inline(text: str) -> str:
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        return text

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.strip() == '---':
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append('<hr>')
            i += 1; continue

        if not line.strip():
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            i += 1; continue

        if line.startswith('### '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f'<h3>{_inline(line[4:])}</h3>')
            i += 1; continue
        if line.startswith('## '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f'<h2>{_inline(line[3:])}</h2>')
            i += 1; continue
        if line.startswith('# '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f'<h1>{_inline(line[2:])}</h1>')
            i += 1; continue

        if num_pattern.match(line):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if not in_ol: html_lines.append('<ol>'); in_ol = True
            content = num_pattern.sub('', line, count=1)
            html_lines.append(f'<li>{_inline(content.strip())}</li>')
            i += 1; continue

        if line.strip().startswith('- '):
            if in_ol: html_lines.append('</ol>'); in_ol = False
            if not in_ul: html_lines.append('<ul>'); in_ul = True
            content = line.strip()[2:]
            html_lines.append(f'<li>{_inline(content.strip())}</li>')
            i += 1; continue

        if in_ul: html_lines.append('</ul>'); in_ul = False
        if in_ol: html_lines.append('</ol>'); in_ol = False
        html_lines.append(f'<p>{_inline(line.strip())}</p>')
        i += 1

    if in_ul: html_lines.append('</ul>')
    if in_ol: html_lines.append('</ol>')
    return '\n'.join(html_lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 convert_md_to_html.py <input.md> [output.html]")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.exists(input_path):
        print(f"ERROR: File not found: {input_path}")
        sys.exit(1)

    output_path = sys.argv[2] if len(sys.argv) > 2 else input_path.rsplit('.', 1)[0] + '.html'

    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    html = md_to_html(md_text)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ HTML conversion done -> {output_path}")
    print(f"   Input:  {len(md_text)} chars")
    print(f"   Output: {len(html)} chars")
    if '**' in html:
        print("⚠️  Warning: ** markers still present in output!")


if __name__ == '__main__':
    main()
