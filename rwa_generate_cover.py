#!/usr/bin/env python3
"""
RWA 早报封面图生成脚本
用法: python3 rwa_generate_cover.py <wordpress_url | md_file_path>
      python3 rwa_generate_cover.py <md_file_path> --quality low

输入可以是 WordPress 文章链接或本地 Markdown 文件。
"""
import sys, os, re, json, base64, requests, time
from datetime import datetime

# ── 配置 ──────────────────────────────────────────
API_URL     = "https://openclaw-api.com/v1/images/generations"
API_KEY     = "sk-Ah7eNGHDCBefNXejDZ6U10rcuHbAQ8yGPTz8kQqCKRONmH5U"
OUTPUT_DIR  = os.path.dirname(os.path.abspath(__file__))
IMAGE_SIZE  = "1024x1536"       # 2:3 竖版长图
DEFAULT_Q   = "low"             # low/medium/high，建议 prod 用 medium
MAX_RETRIES = 2                 # API 调用重试次数

WP_USER = "tianao1128"
WP_PASS = "Z0IfWp8I2PNdKEeDgopRCXmU"

# ── Prompt 模板 ───────────────────────────────────
COVER_PROMPT_TEMPLATE = """Generate a clean, professional vertical cover image for a daily financial newsletter. Style: modern morning news magazine cover, 9:16 portrait orientation.

Layout specifications:
- Top section: A bold banner/header with the text "RWA 早报" in large, elegant Chinese typography
- Below header: the date "{date}" in smaller refined text
- Center section: A prominent headline area displaying "{focus_title}" as the main feature story
- Below that: a section with key highlights / bullet-style teasers:
  {teasers}
- Bottom section: The brand logo "AURELLIX" in clean, sophisticated typography
- Color scheme: Deep navy blue (#0a1628) background with gold (#c9a84c) and white accents
- Visual style: Elevate financial data visualization aesthetic — subtle geometric patterns, fine line art, no photorealistic elements
- Mood: Professional, authoritative, premium — like Bloomberg Businessweek or The Economist covers
- Aspect ratio: strictly 2:3 vertical portrait
- IMPORTANT: All text must be in Chinese (except the brand name AURELLIX)"""


# ── 从 Markdown / HTML 提取内容 ────────────────────
def extract_content(text: str, is_html: bool = False) -> dict:
    """从文本中提取标题、焦点、快讯"""
    info = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "focus_title": "RWA 行业今日要闻",
        "teasers": ["• RWA 行业最新动态", "• 监管政策深度解读", "• 链上资产数据追踪"],
        "title": ""
    }
    
    if is_html:
        # HTML 预处理：去掉标签提取纯文本
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '\n', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&[a-z]+;', ' ', text)
        # 合并多个换行
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
    
    # ── 实际 MD 格式匹配 ─────────────────────────
    # 格式一: ## 【RWA 早报】2026-05-26  → 然后 ### N. 标题
    # 格式二: # RWA 早报 | 2026-05-26  → 🔥 今日焦点 + 📰 昨日快讯
    
    # 1. 提取标题和日期
    title_m = re.search(r'【?RWA\s*早报】?\s*(?:\||[|｜])\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})', text)
    if not title_m:
        title_m = re.search(r'【?RWA\s*早报】?\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})', text)
    if not title_m:
        title_m = re.search(r'RWA\s*早报.*?(\d{4}[-/]\d{1,2}[-/]\d{1,2})', text)
    if title_m:
        info["date"] = title_m.group(1).replace('/', '-')
        info["title"] = f"RWA 早报 | {info['date']}"
    
    # 2. 提取新闻条目：### N. 标题 或 ## N. 标题
    headlines = []
    for m in re.finditer(r'^#{2,3}\s*\d+\.\s*(.+)$', text, re.MULTILINE):
        headline = m.group(1).strip()
        headline = re.sub(r'\*\*', '', headline)
        if len(headline) > 3 and '来源' not in headline:
            headlines.append(headline)
    
    # 焦点 = 第一条新闻标题
    if headlines:
        info["focus_title"] = headlines[0][:80]
        # Teaser = 所有新闻标题
        info["teasers"] = [f"• {h[:55]}" for h in headlines[:5]]
    
    # 如果上述格式没匹配到，尝试格式二的「今日焦点」+「快讯」
    if info["focus_title"] == "RWA 行业今日要闻":
        focus_m = re.search(
            r'🔥\s*今日焦点\s*\n+(.+?)(?=\n---|\n##|\n📰|\n📊|\n💬)',
            text, re.DOTALL
        )
        if focus_m:
            lines = [l.strip() for l in focus_m.group(1).split('\n') if l.strip()]
            lines = [l for l in lines if not l.startswith('>') and '来源' not in l]
            if lines:
                focus = re.sub(r'\*\*', '', lines[0])
                focus = re.sub(r'^\d+\.\s*', '', focus)
                if len(focus) > 5:
                    info["focus_title"] = focus[:80]
    
    if len(info["teasers"]) <= 1:
        news_m = re.search(
            r'📰\s*昨日快讯\s*\n+(.+?)(?=\n---|\n##|\n📊|\n💬)',
            text, re.DOTALL
        )
        fallback = []
        if news_m:
            for tm in re.finditer(r'\*\*\d+\.\s*(.+?)\*\*', news_m.group(1)):
                t = tm.group(1).strip()[:60]
                if t and len(t) > 3:
                    fallback.append(f"• {t}")
        if fallback:
            info["teasers"] = fallback[:5]
    
    return info


def fetch_content(source: str) -> tuple:
    """从 URL 或文件读取内容。返回 (text, is_html)"""
    if source.startswith("http"):
        # 优先尝试 WP REST API
        post_id = None
        m = re.search(r'p=(\d+)', source)
        if not m:
            m = re.search(r'/archives/(\d+)', source)
        if not m:
            # 尝试从 URL path 的最后一段提取 slug，然后用 WP API 搜索
            slug = source.rstrip('/').split('/')[-1]
            if slug:
                try:
                    from base64 import b64encode
                    credentials = b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
                    resp = requests.get(
                        f"https://www.tianao1128.online/wp-json/wp/v2/posts",
                        params={"slug": slug},
                        headers={"Authorization": f"Basic {credentials}"},
                        timeout=15
                    )
                    if resp.status_code == 200 and resp.json():
                        post_id = resp.json()[0]["id"]
                except Exception:
                    pass
        
        if post_id:
            m = type('obj', (object,), {'group': lambda self, i: str(post_id)})
        
        if m:
            post_id = m.group(1) if hasattr(m, 'group') else m
            try:
                from base64 import b64encode
                credentials = b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
                resp = requests.get(
                    f"https://www.tianao1128.online/wp-json/wp/v2/posts/{post_id}",
                    headers={"Authorization": f"Basic {credentials}"},
                    timeout=15
                )
                if resp.status_code == 200:
                    data = resp.json()
                    title = data.get("title", {}).get("rendered", "")
                    content = data.get("content", {}).get("rendered", "")
                    full_text = f"# {title}\n\n{content}"
                    print(f"      ✅ 通过 WP REST API 获取文章 (ID={post_id})")
                    return (full_text, True)
            except Exception as e:
                print(f"      ⚠️ WP API 失败: {e}，回退到 HTML 抓取")
        
        # 回退：直接抓取 HTML
        resp = requests.get(source, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        print(f"      通过 HTML 抓取获取内容 ({len(resp.text)} 字节)")
        return (resp.text, True)
    else:
        with open(source, 'r', encoding='utf-8') as f:
            return (f.read(), False)


def generate_image(prompt: str, quality: str) -> str:
    """调用 OpenClaw gpt-image-2 API 生成图片（通过 curl，避免 chunked encoding 问题）"""
    import subprocess
    
    # 构造 JSON payload
    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "n": 1,
        "size": IMAGE_SIZE,
        "quality": quality
    }
    
    # 写入临时 JSON 文件（避免命令行转义问题）
    json_path = os.path.join(OUTPUT_DIR, "_cover_payload.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)
    
    # 输出文件路径
    date_str = datetime.now().strftime("%Y%m%d")
    resp_file = os.path.join(OUTPUT_DIR, f"_cover_resp_{date_str}.json")
    output_path = os.path.join(OUTPUT_DIR, f"rwa_morning_cover_{date_str}.png")

    print(f"[3/4] 调用 API 生成封面图...")
    print(f"      Prompt 长度: {len(prompt)} 字符")
    print(f"      尺寸: {IMAGE_SIZE}")
    print(f"      质量: {quality}")

    cmd = [
        'curl', '-s', '-o', resp_file,
        '--noproxy', '*',
        '--max-time', '600',
        '--retry', '3',
        '--retry-delay', '10',
        '--retry-all-errors',
        '-X', 'POST',
        API_URL,
        '-H', f'Authorization: Bearer {API_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', f'@{json_path}',
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)

    # 清理临时 payload
    if os.path.exists(json_path):
        os.remove(json_path)

    if result.returncode != 0:
        print(f"      ❌ curl 失败: exit code {result.returncode}")
        raise RuntimeError(f"curl failed: {result.returncode}")

    # 检查响应文件
    if not os.path.exists(resp_file):
        print("      ❌ 响应文件未生成")
        raise RuntimeError("Response file not created")

    file_size = os.path.getsize(resp_file)
    print(f"      响应文件大小: {file_size} bytes")

    if file_size < 10:
        with open(resp_file, 'r') as f:
            content = f.read()
        print(f"      响应内容: {content[:200]}")
        raise RuntimeError(f"Response too small ({file_size} bytes): {content[:200]}")

    # 解析响应 JSON
    try:
        with open(resp_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"      ❌ JSON 解析失败: {e}")
        with open(resp_file, 'r') as f:
            print(f"      响应内容: {f.read()[:500]}")
        raise

    # 检查 API 错误
    if "error" in data:
        err_msg = data["error"].get("message", str(data["error"]))
        print(f"      ❌ API 返回错误: {err_msg[:300]}")
        raise RuntimeError(f"API error: {err_msg[:300]}")
    if "data" not in data:
        print(f"      ❌ 响应缺少 data 字段")
        print(f"      响应 keys: {list(data.keys())}")
        print(f"      响应内容: {json.dumps(data, ensure_ascii=False)[:500]}")
        raise RuntimeError("Missing 'data' in API response")

    b64 = data["data"][0]["b64_json"]
    usage = data.get("usage", {})
    print(f"      ✅ 生成成功，token 用量: {usage.get('total_tokens', 'N/A')}")
    
    # 解码保存 PNG
    img_data = base64.b64decode(b64)
    with open(output_path, 'wb') as f:
        f.write(img_data)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"      💾 已保存: {output_path} ({size_kb:.1f} KB)")

    # 清理临时响应文件
    if os.path.exists(resp_file):
        os.remove(resp_file)

    return output_path


def main():
    import argparse
    parser = argparse.ArgumentParser(description="RWA 早报封面图生成")
    parser.add_argument("source", help="WordPress 文章 URL 或 Markdown 文件路径")
    parser.add_argument("--quality", "-q", default=DEFAULT_Q, choices=["low", "medium", "high"],
                       help=f"图片质量 (默认: {DEFAULT_Q})")
    args = parser.parse_args()
    
    # 1. 获取内容
    print(f"[1/4] 获取文章内容...")
    content, is_html = fetch_content(args.source)
    
    # 2. 提取关键信息
    print(f"[2/4] 提取关键信息...")
    info = extract_content(content, is_html)
    print(f"      日期: {info['date']}")
    print(f"      焦点: {info['focus_title'][:60]}")
    print(f"      快讯: {len(info['teasers'])} 条")
    for t in info["teasers"]:
        print(f"        {t[:60]}")
    
    # 3. 构造 prompt
    prompt = COVER_PROMPT_TEMPLATE.format(
        date=info["date"],
        focus_title=info["focus_title"],
        teasers="\n  ".join(info["teasers"])
    )
    
    # 4. 生成图片
    output_path = generate_image(prompt, args.quality)
    
    print(f"\n🎉 完成！封面图: {output_path}")
    return output_path


if __name__ == "__main__":
    main()
