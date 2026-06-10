#!/usr/bin/env python3
"""Re-publish AI blockchain article to WordPress with proper markdown conversion."""
import os
import re
import json
import subprocess
import dotenv

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv.load_dotenv(os.path.join(_SCRIPT_DIR, ".env"))

WP_URL = os.getenv("WP_URL")
WP_USER = os.getenv("WP_USER")
WP_PASS = os.getenv("WP_PASS")

# Read markdown
with open(os.path.join(_SCRIPT_DIR, 'ai_blockchain_20260610.md'), 'r') as f:
    content = f.read()

# Extract title
title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
title = title_match.group(1).strip() if title_match else 'AIx区块链 | 2026-06-10'

# Convert markdown to HTML using markdown library
import markdown as md
html_content = md.markdown(content, extensions=['extra', 'codehilite', 'nl2br'])

# Prepare post data
post_data = {
    'title': title,
    'content': html_content,
    'status': 'publish',
    'categories': [4]
}

# Write to temp file
output_path = '/tmp/wp_post_ai_blockchain_v2.json'
with open(output_path, 'w') as f:
    json.dump(post_data, f, ensure_ascii=False)

print(f'Title: {title}')
print(f'Output: {output_path}')
print(f'HTML length: {len(html_content)} chars')
print('Ready to update WordPress (POST to /posts/769).')
