#!/usr/bin/env python3
"""Publish AI Blockchain article to WordPress with cover image and inline charts."""
import sys, os, re, base64, json
import xmlrpc.client

# Load .env
import dotenv
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv.load_dotenv(os.path.join(_SCRIPT_DIR, ".env"))

WP_XMLRPC_URL = os.getenv("WP_XMLRPC_URL", "https://www.tianao1128.online/xmlrpc.php")
WP_USER = os.getenv("WP_USER", "tianao1128")
WP_PASS = os.getenv("WP_PASS", "")

def md_to_html(md_text: str) -> str:
    """Convert Markdown to HTML using markdown library (with extensions)."""
    try:
        import markdown as md_lib
        return md_lib.markdown(md_text, extensions=['extra', 'codehilite', 'nl2br'])
    except ImportError:
        import warnings
        warnings.warn("markdown library not installed. Run: pip install markdown")
        return _md_to_html_fallback(md_text)


def _md_to_html_fallback(md_text: str) -> str:
    """Minimal fallback converter – handles **bold**, links, headers, lists."""
    lines = md_text.strip().split('\n')
    html_lines = []
    in_ul = False
    in_ol = False
    num_pattern = re.compile(r'^(\d+)\.\s')

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
            html_lines.append(f'<h3>{_ai_inline(line[4:])}</h3>')
            i += 1; continue
        if line.startswith('## '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f'<h2>{_ai_inline(line[3:])}</h2>')
            i += 1; continue
        if line.startswith('# '):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if in_ol: html_lines.append('</ol>'); in_ol = False
            html_lines.append(f'<h1>{_ai_inline(line[2:])}</h1>')
            i += 1; continue

        if num_pattern.match(line):
            if in_ul: html_lines.append('</ul>'); in_ul = False
            if not in_ol: html_lines.append('<ol>'); in_ol = True
            content = num_pattern.sub('', line, count=1)
            html_lines.append(f'<li>{_ai_inline(content.strip())}</li>')
            i += 1; continue

        if line.strip().startswith('- '):
            if in_ol: html_lines.append('</ol>'); in_ol = False
            if not in_ul: html_lines.append('<ul>'); in_ul = True
            content = line.strip()[2:]
            html_lines.append(f'<li>{_ai_inline(content.strip())}</li>')
            i += 1; continue

        if in_ul: html_lines.append('</ul>'); in_ul = False
        if in_ol: html_lines.append('</ol>'); in_ol = False
        html_lines.append(f'<p>{_ai_inline(line.strip())}</p>')
        i += 1

    if in_ul: html_lines.append('</ul>')
    if in_ol: html_lines.append('</ol>')
    return '\n'.join(html_lines)


def _ai_inline(text: str) -> str:
    """Handle inline Markdown: **bold**, [link](url), `code`."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    return text


def upload_media(filepath: str) -> dict:
    """Upload image to WordPress media library via XML-RPC. Returns dict with id, url."""
    with open(filepath, 'rb') as f:
        file_data = f.read()

    filename = os.path.basename(filepath)
    mime = 'image/png'
    if filename.endswith('.jpg') or filename.endswith('.jpeg'):
        mime = 'image/jpeg'

    data = {
        'name': filename,
        'type': mime,
        'bits': xmlrpc.client.Binary(file_data),
        'overwrite': False,
    }

    result = xmlrpc.client.ServerProxy(WP_XMLRPC_URL).wp.uploadFile(
        1, WP_USER, WP_PASS, data
    )
    print(f"[Media] Uploaded: {result.get('url')}")
    print(f"[Media] Media ID: {result.get('id')}")
    return {
        'id': int(result.get('id')),
        'url': result.get('url', ''),
        'link': result.get('url', '')
    }


def generate_charts(spec_path: str, output_dir: str) -> list:
    """Call chart_renderer.py to generate charts from JSON spec. Returns list of PNG paths."""
    renderer_script = os.path.join(os.path.dirname(__file__), 'chart_renderer.py')
    if not os.path.exists(renderer_script):
        print(f"⚠️  Chart renderer not found: {renderer_script}")
        return []

    import subprocess
    result = subprocess.run(
        [sys.executable, renderer_script, spec_path, output_dir],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"⚠️  Chart generation error: {result.stderr}")
        return []

    # Parse output to find generated file paths
    paths = []
    for line in result.stdout.split('\n'):
        if line.startswith('  → '):
            paths.append(line[4:].strip())
    return paths


def embed_charts_in_markdown(md_text: str, chart_urls: list, spec_path: str) -> str:
    """Embed chart images into markdown text based on position hints from spec."""
    if not chart_urls or not os.path.exists(spec_path):
        return md_text

    with open(spec_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)

    charts = spec.get('charts', [])
    lines = md_text.split('\n')
    result_lines = []
    embedded = set()

    for line in lines:
        result_lines.append(line)

        # Check if this line is a section header that matches any position_hint
        for i, chart_spec in enumerate(charts):
            if i in embedded:
                continue
            hint = chart_spec.get('position_hint', '')
            if not hint:
                continue

            # Match section headers like "### 二、行业现状" or "### 行业现状"
            if hint in line or line.strip().endswith(hint):
                if i < len(chart_urls):
                    chart_url = chart_urls[i]
                    chart_title = chart_spec.get('title', '')
                    # Insert chart image after the section header
                    result_lines.append(f'\n![{chart_title}]({chart_url})\n')
                    embedded.add(i)
                    break

    # Embed any remaining charts at the end of the article (before reference sources)
    for i, chart_spec in enumerate(charts):
        if i not in embedded and i < len(chart_urls):
            chart_url = chart_urls[i]
            chart_title = chart_spec.get('title', '')
            # Find "参考来源" or end of content
            for j, line in enumerate(result_lines):
                if '参考来源' in line or '**参考来源**' in line:
                    result_lines.insert(j, f'\n![{chart_title}]({chart_url})\n')
                    embedded.add(i)
                    break
            else:
                result_lines.append(f'\n![{chart_title}]({chart_url})\n')
                embedded.add(i)

    return '\n'.join(result_lines)


def publish_post(title: str, html_content: str, category: str, featured_media_id: int = 0) -> dict:
    """Publish post via XML-RPC."""
    post_data = {
        "post_type": "post",
        "post_status": "publish",
        "post_title": title,
        "post_content": html_content,
        "terms_names": {"category": [category]},
    }
    if featured_media_id > 0:
        post_data["_thumbnail_id"] = featured_media_id

    xml_body = xmlrpc.client.dumps(
        (1, WP_USER, WP_PASS, post_data),
        methodname="wp.newPost",
    )

    import urllib.request
    req = urllib.request.Request(
        WP_XMLRPC_URL,
        data=xml_body.encode("utf-8"),
        headers={"Content-Type": "text/xml", "User-Agent": "WorkBuddy/1.0"},
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=120)
    result = xmlrpc.client.loads(resp.read().decode("utf-8"))
    post_id = str(result[0][0])
    link = f"https://www.tianao1128.online/?p={post_id}"
    return {"id": post_id, "link": link}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 publish_ai_blockchain.py <md_file> [cover_image]")
        sys.exit(1)

    md_path = sys.argv[1]
    cover_path = sys.argv[2] if len(sys.argv) > 2 else None

    # Derive chart spec path from md path
    base_path = md_path.replace('.md', '')
    spec_path = f"{base_path}_charts.json"
    output_dir = os.path.dirname(md_path) or '.'

    with open(md_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    title_match = re.search(r'^#{1,2}\s*(.+?)$', md_text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(md_path)
    print(f"Title: {title}")

    # Step 1: Generate charts if spec exists
    chart_urls = []
    chart_files = []
    if os.path.exists(spec_path):
        print(f"\n[Charts] Found spec: {spec_path}")
        chart_files = generate_charts(spec_path, output_dir)

        if chart_files:
            print(f"\n[Charts] Uploading {len(chart_files)} charts to WordPress...")
            for chart_file in chart_files:
                media_info = upload_media(chart_file)
                chart_urls.append(media_info['url'])

            # Embed charts into markdown
            md_text = embed_charts_in_markdown(md_text, chart_urls, spec_path)
            print(f"[Charts] Embedded {len(chart_urls)} charts into article")
    else:
        print(f"[Charts] No spec found: {spec_path}, skipping chart generation")

    # Step 2: Convert to HTML
    html_content = md_to_html(md_text)
    print(f"HTML size: {len(html_content)} chars")

    # Save HTML
    html_path = md_path.replace('.md', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML saved: {html_path}")

    # Step 3: Upload cover
    media_id = 0
    if cover_path and os.path.exists(cover_path):
        print(f"\n[Cover] Uploading: {cover_path}")
        media_info = upload_media(cover_path)
        media_id = media_info['id']
    elif cover_path:
        print(f"⚠️  Cover not found: {cover_path}")

    # Step 4: Publish
    print(f"\n[Publishing] Publishing to WordPress...")
    category = "AI×区块链"
    result = publish_post(title, html_content, category, media_id)
    print(f"\n✅ Published!")
    print(f"Post ID: {result['id']}")
    print(f"URL: {result['link']}")
    if media_id > 0:
        print(f"Featured Media ID: {media_id}")
    if chart_urls:
        print(f"Charts: {len(chart_urls)} embedded")
        for i, url in enumerate(chart_urls, 1):
            print(f"  Chart {i}: {url}")
