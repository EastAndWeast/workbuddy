import re
import json

with open("/Users/bruce/WorkBuddy/Claw/rwa_morning_20260526.md", "r", encoding="utf-8") as f:
    md = f.read()

# Convert Markdown to HTML
html = md

# Title: # -> h1
html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

# Subtitle: ## -> h2  
html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)

# Bold: **text** -> <strong>text</strong>
html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

# Inline code: `text` -> <code>text</code>
html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

# Links: [text](url) -> <a href="url">text</a>
html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', html)

# Blockquotes: > -> <blockquote>
lines = html.split('\n')
new_lines = []
in_blockquote = False
for line in lines:
    if line.startswith('> '):
        if not in_blockquote:
            new_lines.append('<blockquote>')
            in_blockquote = True
        new_lines.append(line[2:] + '<br>')
    else:
        if in_blockquote:
            new_lines.append('</blockquote>')
            in_blockquote = False
        new_lines.append(line)

if in_blockquote:
    new_lines.append('</blockquote>')

html = '\n'.join(new_lines)

# Horizontal rule: --- -> <hr>
html = re.sub(r'^---$', '<hr>', html, flags=re.MULTILINE)

# Bullet lists: - -> <li> (wrap in <ul>)
html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

# Wrap consecutive <li> in <ul>
def wrap_ul(match):
    return '<ul>' + match.group(0) + '</ul>'
html = re.sub(r'(?:<li>.*?</li>\n?)+', wrap_ul, html, flags=re.DOTALL)

# Paragraphs: wrap non-tag lines in <p>
final_lines = []
for line in html.split('\n'):
    stripped = line.strip()
    if stripped and not stripped.startswith('<') and not stripped.endswith('>'):
        final_lines.append('<p>' + stripped + '</p>')
    else:
        final_lines.append(line)

html_final = '\n'.join(final_lines)

# Write HTML to file
with open("/Users/bruce/WorkBuddy/Claw/rwa_morning_20260526.html", "w", encoding="utf-8") as f:
    f.write(html_final)

print("HTML conversion done")
print("Length:", len(html_final))
