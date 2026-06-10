#!/usr/bin/env python3
"""Prepare AI blockchain article for WordPress publishing."""
import os
import re
import json
import dotenv

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv.load_dotenv(os.path.join(_SCRIPT_DIR, ".env"))

with open(os.path.join(_SCRIPT_DIR, 'ai_blockchain_20260610.md'), 'r') as f:
    content = f.read()

title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
title = title_match.group(1).strip() if title_match else 'AIx区块链 | 2026-06-10'

# Simple markdown to HTML
lines = content.split('\n')
html_lines = []
in_code = False
for line in lines:
    if line.startswith('```'):
        if in_code:
            html_lines.append('</pre>')
            in_code = False
        else:
            html_lines.append('<pre>')
            in_code = True
        continue
    if in_code:
        html_lines.append(line)
        continue
    if line.startswith('#### '):
        html_lines.append(f'<h4>{line[5:]}</h4>')
    elif line.startswith('### '):
        html_lines.append(f'<h3>{line[4:]}</h3>')
    elif line.startswith('## '):
        html_lines.append(f'<h2>{line[3:]}</h2>')
    elif line.startswith('# '):
        html_lines.append(f'<h1>{line[2:]}</h1>')
    elif line.strip() == '---':
        html_lines.append('<hr>')
    elif line.strip() == '':
        html_lines.append('')
    else:
        html_lines.append(f'<p>{line}</p>')

html_content = '\n'.join(html_lines)

post_data = {
    'title': title,
    'content': html_content,
    'status': 'publish',
    'categories': [4]
}

output_path = '/tmp/wp_post_ai_blockchain.json'
with open(output_path, 'w') as f:
    json.dump(post_data, f, ensure_ascii=False)

print(f'Title: {title}')
print(f'Output: {output_path}')
print('Ready.')
