#!/usr/bin/env python3
"""RWA Morning Report Publisher
Converts RWA morning report Markdown to HTML via WordPress REST API.

Usage:
    python3 rwa_publish_wp.py [markdown_file_path]

If no path is given, finds today's rwa_morning_YYYYMMDD.md in the same directory.
If today's file doesn't exist, returns an error (auto-generate should be done by the automation).
"""

import re
import sys
import os
import base64
import dotenv
from datetime import datetime, timezone, timedelta

# --- Load .env from workspace root ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv.load_dotenv(os.path.join(_SCRIPT_DIR, ".env"))

# --- Config (from env, with fallbacks) ---
WP_URL = os.getenv("WP_URL", "https://www.tianao1128.online/wp-json/wp/v2/posts")
WP_XMLRPC_URL = os.getenv("WP_XMLRPC_URL", "https://www.tianao1128.online/xmlrpc.php")
WP_USER = os.getenv("WP_USER", "tianao1128")
WP_PASS = os.getenv("WP_PASS", "")
WP_CATEGORY = int(os.getenv("WP_CATEGORY_ID", "4"))
SCRIPT_DIR = _SCRIPT_DIR


def find_morning_report():
    """Find today's morning report file."""
    tz = timezone(timedelta(hours=8))
    today = datetime.now(tz).strftime("%Y%m%d")
    filename = f"rwa_morning_{today}.md"
    filepath = os.path.join(SCRIPT_DIR, filename)
    if os.path.exists(filepath):
        return filepath
    # Also try common naming variants
    for variant in [f"rwa_morning_report_{today}.md"]:
        path = os.path.join(SCRIPT_DIR, variant)
        if os.path.exists(path):
            return path
    return None


def md_to_html(md_text: str) -> str:
    """Convert RWA morning report Markdown to HTML."""
    lines = md_text.strip().split('\n')
    html_lines = []
    in_ul = False
    in_blockquote = False
    in_ol = False
    num_pattern = re.compile(r'^(\d+)\.\s')

    i = 0
    while i < len(lines):
        line = lines[i]

        # Horizontal rule
        if line.strip() == '---':
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            if in_ol:
                html_lines.append('</ol>')
                in_ol = False
            if in_blockquote:
                html_lines.append('</blockquote>')
                in_blockquote = False
            html_lines.append('<hr>')
            i += 1
            continue

        # Blockquote
        if line.startswith('> '):
            if not in_blockquote:
                html_lines.append('<blockquote>')
                in_blockquote = True
            content = line[2:].strip()
            content = md_inline_format(content)
            html_lines.append(f'<p>{content}</p>')
            i += 1
            continue
        elif line.startswith('>') and not line.startswith('> '):
            if not in_blockquote:
                html_lines.append('<blockquote>')
                in_blockquote = True
            content = line[1:].strip()
            content = md_inline_format(content)
            html_lines.append(f'<p>{content}</p>')
            i += 1
            continue
        elif in_blockquote and not line.startswith('>'):
            html_lines.append('</blockquote>')
            in_blockquote = False

        # Empty line
        if not line.strip():
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            if in_ol:
                html_lines.append('</ol>')
                in_ol = False
            i += 1
            continue

        # Heading ##
        if line.startswith('## '):
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            if in_ol:
                html_lines.append('</ol>')
                in_ol = False
            content = line[3:].strip()
            content = md_inline_format(content)
            html_lines.append(f'<h2>{content}</h2>')
            i += 1
            continue

        # Heading ###
        if line.startswith('### '):
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            if in_ol:
                html_lines.append('</ol>')
                in_ol = False
            content = line[4:].strip()
            content = md_inline_format(content)
            html_lines.append(f'<h3>{content}</h3>')
            i += 1
            continue

        # Numbered list item (1. text)
        if num_pattern.match(line):
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            if not in_ol:
                html_lines.append('<ol>')
                in_ol = True
            content = num_pattern.sub('', line, count=1)
            content = md_inline_format(content)
            html_lines.append(f'<li>{content}</li>')
            i += 1
            continue

        # Bullet list item (- text)
        if line.strip().startswith('- ') or line.strip().startswith('   - '):
            if in_ol:
                html_lines.append('</ol>')
                in_ol = False
            if not in_ul:
                html_lines.append('<ul>')
                in_ul = True
            content = line.strip()[2:].strip()
            content = md_inline_format(content)
            html_lines.append(f'<li>{content}</li>')
            i += 1
            continue

        # Any other numbered item
        o = num_pattern.match(line.strip())
        if o:
            if in_ul:
                html_lines.append('</ul>')
                in_ul = False
            if not in_ol:
                html_lines.append('<ol>')
                in_ol = True
            content = num_pattern.sub('', line.strip(), count=1)
            content = md_inline_format(content)
            html_lines.append(f'<li>{content}</li>')
            i += 1
            continue

        # Regular paragraph
        if in_ul:
            html_lines.append('</ul>')
            in_ul = False
        if in_ol:
            html_lines.append('</ol>')
            in_ol = False
        content = md_inline_format(line.strip())
        html_lines.append(f'<p>{content}</p>')
        i += 1

    # Close open tags
    if in_ul:
        html_lines.append('</ul>')
    if in_ol:
        html_lines.append('</ol>')
    if in_blockquote:
        html_lines.append('</blockquote>')

    return '\n'.join(html_lines)


def md_inline_format(text: str) -> str:
    """Handle inline Markdown formatting."""
    # Bold: **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Links: [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Inline code: `text`
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


def publish_to_wp(title: str, html_content: str, category: str = "RWA") -> dict:
    """Publish post to WordPress using XML-RPC (more reliable than REST for larger payloads)."""
    import urllib.request
    import xmlrpc.client

    post_data = {
        "post_type": "post",
        "post_status": "publish",
        "post_title": title,
        "post_content": html_content,
        "terms_names": {"category": [category]},
    }
    xml_body = xmlrpc.client.dumps(
        (1, WP_USER, WP_PASS, post_data),
        methodname="wp.newPost",
    )

    req = urllib.request.Request(
        WP_XMLRPC_URL,
        data=xml_body.encode("utf-8"),
        headers={
            "Content-Type": "text/xml",
            "User-Agent": "WorkBuddy-RWA-Publisher/1.0",
        },
        method="POST",
    )

    try:
        resp = urllib.request.urlopen(req, timeout=120)
        result = xmlrpc.client.loads(resp.read().decode("utf-8"))
        post_id = result[0][0]  # Extract post ID from XML-RPC response
        post_id_str = str(post_id)
        # Construct WP link
        link = f"https://www.tianao1128.online/?p={post_id_str}"
        return {"id": post_id_str, "link": link}
    except Exception as e:
        print(f"ERROR: XML-RPC publish failed: {e}")
        if hasattr(e, "read"):
            print(e.read().decode("utf-8", errors="replace")[:500])
        return None


def main():
    # Determine file path
    if len(sys.argv) > 1:
        md_path = sys.argv[1]
        if not os.path.exists(md_path):
            print(f"ERROR: File not found: {md_path}")
            sys.exit(1)
    else:
        md_path = find_morning_report()
        if not md_path:
            print("ERROR: No morning report found for today.")
            print("Usage: python3 rwa_publish_wp.py <path_to_md_file>")
            sys.exit(1)

    # Read Markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Extract title from first heading
    title_match = re.search(r'^##\s*(.+)', md_text, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        # Fallback title from filename
        basename = os.path.basename(md_path)
        title = basename.replace('.md', '').replace('_', ' ').title()

    print(f"Publishing: {title}")
    print(f"Source file: {md_path}")

    # Convert to HTML
    html_content = md_to_html(md_text)
    print(f"HTML size: {len(html_content)} chars")

    # Save HTML for debugging
    html_path = md_path.replace('.md', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML saved to: {html_path}")

    # Publish
    result = publish_to_wp(title, html_content, "RWA")

    if result:
        post_id = result.get('id', '?')
        post_link = result.get('link', 'unknown')
        print(f"\n✅ Published successfully!")
        print(f"Post ID: {post_id}")
        print(f"URL: {post_link}")
        return result, md_path
    else:
        print("\n❌ Publish failed")
        sys.exit(1)


def generate_cover(md_path: str, quality: str = "medium", brand: str = "RWA 早报") -> str:
    """Generate a cover image for the report."""
    cover_script = os.path.join(SCRIPT_DIR, "rwa_generate_cover.py")
    if not os.path.exists(cover_script):
        print("⚠️  rwa_generate_cover.py not found, skipping cover generation")
        return None
    
    import subprocess
    print(f"\n[Cover] Generating cover image (quality={quality}, brand={brand})...")
    result = subprocess.run(
        [sys.executable, cover_script, md_path, "--quality", quality, "--brand", brand],
        capture_output=True, text=True, timeout=600
    )
    
    if result.returncode == 0:
        # Extract path from last line
        for line in result.stdout.strip().split('\n'):
            if '完成！封面图:' in line:
                path = line.split('封面图:')[-1].strip()
                print(f"[Cover] ✅ {path}")
                return path
        # Fallback: try to find the file
        print(f"[Cover] Script output:\n{result.stdout[-500:]}")
    else:
        print(f"[Cover] ❌ Failed:\n{result.stderr[-500:]}")
    return None


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="RWA Morning Report Publisher")
    parser.add_argument("md_path", nargs="?", help="Path to Markdown file")
    parser.add_argument("--generate-cover", action="store_true", help="Generate cover image after publishing")
    parser.add_argument("--cover-quality", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--cover-brand", default="RWA 早报", help="Cover brand template (default: RWA 早报)")
    parser.add_argument("--category", default="RWA", help="WordPress category name (default: RWA)")
    args = parser.parse_args()
    
    # Determine file path
    if args.md_path:
        md_path = args.md_path
        if not os.path.exists(md_path):
            print(f"ERROR: File not found: {md_path}")
            sys.exit(1)
    else:
        md_path = find_morning_report()
        if not md_path:
            print("ERROR: No morning report found for today.")
            print("Usage: python3 rwa_publish_wp.py <path_to_md_file>")
            sys.exit(1)

    category = args.category

    # Read Markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Extract title from first heading (## or #)
    title_match = re.search(r'^#{1,2}\s*(.+?)(?:\s*\|.+)?$', md_text, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        basename = os.path.basename(md_path)
        title = basename.replace('.md', '').replace('_', ' ').title()

    print(f"Publishing: {title}")
    print(f"Source file: {md_path}")

    # Convert to HTML
    html_content = md_to_html(md_text)
    print(f"HTML size: {len(html_content)} chars")

    # Save HTML for debugging
    html_path = md_path.replace('.md', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML saved to: {html_path}")

    # Publish
    result = publish_to_wp(title, html_content, category)

    if not result:
        print("\n❌ Publish failed")
        sys.exit(1)
    
    post_id = result.get('id', '?')
    post_link = result.get('link', 'unknown')
    print(f"\n✅ Published successfully!")
    print(f"Post ID: {post_id}")
    print(f"URL: {post_link}")

    # Generate cover if requested
    if args.generate_cover:
        cover_path = generate_cover(md_path, args.cover_quality, args.cover_brand)
        if cover_path:
            print(f"\nCOVER_IMAGE={cover_path}")

    # Print final summary
    print(f"\nWP_URL={post_link}")
    print(f"WP_ID={post_id}")
