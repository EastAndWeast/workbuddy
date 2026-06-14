#!/usr/bin/env python3
"""
Article Cover Engine - 文章封面图自动生成引擎
完整链路：Markdown 文章 → AI 生成纯视觉提示词 → gpt-image-2 生成图 → 下载 → WordPress 封面（可选）

核心理念：封面图不含任何文字，纯视觉表达，适配多语言场景。
"""

import sys
import os
import re
import json
import base64
import subprocess
import requests
import argparse
from datetime import datetime

# ── 配置来源：命令行参数 / 环境变量 / secrets 文件 ──────────
SECRETS_FILE = os.path.expanduser("~/.workbuddy/secrets/openai_image.json")

def load_secrets():
    """加载 API 凭据"""
    if os.path.exists(SECRETS_FILE):
        with open(SECRETS_FILE) as f:
            return json.load(f)
    return {}

SECRETS = load_secrets()
API_BASE = os.getenv("COVER_API_BASE", SECRETS.get("baseURL", ""))
API_KEY = os.getenv("COVER_API_KEY", SECRETS.get("apiKey", ""))
API_URL = f"{API_BASE.rstrip('/')}/v1/images/generations"
IMAGE_SIZE = "1792x1024"  # 横幅 16:9（接近 2.35:1 影院比例，gpt-image-2 最宽选项）
IMAGE_MODEL = "gpt-image-2"

# ── WordPress 配置（可选，不配则跳过上传）────────────────
WP_URL = os.getenv("WP_URL", "")
WP_API = f"{WP_URL.rstrip('/')}/wp-json/wp/v2" if WP_URL else ""
WP_USER = os.getenv("WP_USER", "")
WP_PASS = os.getenv("WP_PASS", "")


# ═══════════════════════════════════════════════════════════════
# Step 1: 文章内容 → 纯视觉提示词（NO TEXT）
# ═══════════════════════════════════════════════════════════════

def extract_article_essence(text: str) -> dict:
    """从文章中提取核心主题和情感基调，用于生成图片提示词"""
    # 提取标题
    title = ""
    title_match = re.search(r'^#\s+(.+)$', text, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    
    # 提取核心段落（前800字）
    clean = re.sub(r'\*\*|#|>|-', '', text)
    clean = re.sub(r'\n{3,}', '\n\n', clean)
    essence = clean[:800]
    
    # 检测主题关键词
    themes = []
    keywords_map = {
        "regulation": ["监管", "法规", "政策", "合规", "SEC", "CFTC", "立法", "税", "TDS",
                       "regulation", "compliance", "legislation", "tax", "policy"],
        "finance": ["美元", "稳定币", "银行", "利率", "国债", "债券", "基金", "资产", "投资", "资本",
                    "stablecoin", "bank", "interest rate", "bond", "fund", "asset", "investment"],
        "technology": ["区块链", "智能合约", "DeFi", "代币化", "token", "AI", "协议", "Layer", "链上",
                       "blockchain", "smart contract", "protocol", "on-chain", "tokenization"],
        "market": ["交易", "市场", "牛市", "熊市", "价格", "行情", "波动", "市值", "TVL",
                   "trading", "market", "bull", "bear", "price", "volume", "cap"],
        "geopolitical": ["印度", "美国", "中国", "欧洲", "日本", "新加坡", "迪拜", "香港", "全球",
                         "India", "US", "China", "Europe", "Japan", "Singapore", "Dubai", "global"],
        "risk": ["洗钱", "逃税", "制裁", "罚款", "禁止", "处罚", "漏洞", "黑客",
                 "money laundering", "sanction", "fine", "ban", "penalty", "hack"],
    }

    for theme, keywords in keywords_map.items():
        if any(kw in text for kw in keywords):
            themes.append(theme)

    if not themes:
        themes = ["finance", "technology"]

    # 检测所属行业
    industries = []
    industry_map = {
        "AI": ["AI", "人工智能", "大模型", "机器学习", "深度学习", "deep learning", "LLM",
                "GPT", "agent", "智能体", "neural", "神经网络", "强化学习", "生成式"],
        "区块链": ["区块链", "crypto", "Web3", "DeFi", "NFT", "token", "链上", "公链",
                   "共识", "节点", "矿工", "DApp", "去中心化", "加密货", "代币", "Layer"],
        "金融": ["银行", "证券", "基金", "股票", "债券", "利率", "央行", "美联储",
                "SEC", "稳定币", "RWA", "资产", "投资", "财富", "保险", "信贷"],
        "科技": ["科技", "云计算", "大数据", "物联网", "5G", "量子", "芯片", "自动驾驶",
                "SaaS", "数字化", "云计算", "边缘计算", "数据中心", "软件", "硬件"],
    }
    for industry, keywords in industry_map.items():
        if any(kw in text for kw in keywords):
            industries.append(industry)

    if not industries:
        if "technology" in themes:
            industries.append("科技")
        if "finance" in themes or "market" in themes:
            industries.append("金融")

    return {
        "title": title or "Article Analysis",
        "themes": themes,
        "industries": industries,
        "essence": essence,
    }


def generate_visual_prompt(article_text: str) -> str:
    """将文章内容转换为纯视觉提示词"""
    info = extract_article_essence(article_text)
    title = info["title"]
    themes = info["themes"]
    industries = info.get("industries", [])
    
    visual_direction = _pick_visual_direction(themes, title, industries)
    prompt = _build_prompt(visual_direction, title)
    
    return prompt


def _pick_visual_direction(themes: list, title: str, industries: list = None) -> dict:
    """根据主题 + 行业选择视觉方向"""
    
    if industries is None:
        industries = []
    
    # 行业视觉参考映射
    industry_reference_map = {
        "AI": "premium AI industry publications — MIT Technology Review, Harvard Business Review tech edition, VentureBeat AI section. Emphasize intellectual depth, neural-inspired visual language, and the elegance of artificial intelligence.",
        "区块链": "premium Web3/crypto industry publications — The Defiant, Blockworks, CoinDesk magazine covers, Decrypt editorial. Sophisticated blockchain visual language: distributed network aesthetics, cryptographic elegance, decentralized future tone.",
        "金融": "premium financial industry publications — Bloomberg Markets, The Economist, Financial Times, Fortune magazine. Institutional gravitas with warmth: market data as art, capital flow as visual poetry, Wall Street meets contemporary editorial.",
        "科技": "premium technology industry publications — Wired magazine, Fast Company, MIT Technology Review, Protocol. Innovation-forward visual language: future infrastructure, digital-physical convergence, the aesthetics of progress.",
    }
    
    ref_parts = []
    for ind in industries:
        if ind in industry_reference_map:
            ref_parts.append(industry_reference_map[ind])
    industry_ref = " ".join(ref_parts) if ref_parts else (
        "premium Web3 and crypto industry publications like The Defiant and Blockworks — sophisticated, modern, and visually striking."
    )
    
    # 默认配置
    direction = {
        "style": "premium editorial magazine cover illustration",
        "color_primary": "warm amber, golden hour tones, and soft cream",
        "color_secondary": "coral terracotta and warm white accents",
        "mood": "inviting, premium, sophisticated, forward-looking",
        "elements": [
            "elegant layered financial district architecture in warm sunset light",
            "subtle abstract market data flowing as golden light streams",
            "polished marble and glass surfaces reflecting warm ambient glow",
            "editorial-grade composition with sophisticated depth of field"
        ],
        "composition": "cinematic 2.35:1 widescreen magazine cover layout with strong central focal point and elegant negative space for cover text placement",
        "industry_reference": industry_ref,
    }
    
    # 监管/政策类
    if "regulation" in themes and "risk" in themes:
        direction["style"] = "premium investigative editorial magazine cover illustration"
        direction["color_primary"] = "warm burgundy and brass gold with soft cream highlights"
        direction["color_secondary"] = "warm ivory and subtle terracotta accents"
        direction["mood"] = "serious yet warm, authoritative, investigative, premium"
        direction["elements"] = [
            "elegant classical architecture details in warm golden light",
            "refined marble textures with soft amber illumination",
            "subtle scale-of-justice motifs rendered as warm-toned editorial illustration",
            "dramatic yet warm light emerging from rich amber shadows, high-end magazine aesthetic"
        ]
    elif "regulation" in themes:
        direction["style"] = "authoritative editorial policy magazine cover illustration"
        direction["color_primary"] = "warm deep blue and amber gold"
        direction["color_secondary"] = "soft cream and warm coral accents"
        direction["mood"] = "authoritative, measured, warm and forward-looking"
        direction["elements"] = [
            "institutional architecture silhouettes bathed in warm golden hour light",
            "elegant document and framework patterns in warm tones",
            "flowing golden light streams suggesting regulatory frameworks",
            "balanced editorial composition conveying order, trust, and warmth"
        ]
    
    # 科技/AI类
    if "technology" in themes:
        direction["style"] = "premium technology magazine cover illustration, Bloomberg Businessweek meets Wired aesthetic"
        direction["color_primary"] = "warm charcoal and amber gold with electric teal accents"
        direction["color_secondary"] = "soft cream and warm copper highlights"
        direction["mood"] = "cutting-edge, intellectual, warm and innovative"
        direction["elements"] = [
            "elegant neural network and blockchain nodes rendered in warm golden light",
            "hexagonal mesh patterns with amber glow and teal highlights",
            "glowing connection lines forming sophisticated editorial compositions",
            "layered depth suggesting infinite technological space, warm ambient lighting"
        ]
    
    # 地缘政治类
    if "geopolitical" in themes:
        direction["style"] = "premium global affairs magazine cover illustration, The Economist meets Monocle aesthetic"
        direction["color_primary"] = "warm golden hour teal and rich amber"
        direction["color_secondary"] = "soft cream and warm copper accents"
        direction["mood"] = "panoramic, strategic, worldly, warm and sophisticated"
        direction["elements"] = [
            "elegant world map contours rendered in warm golden light",
            "interconnected network lines spanning the composition in amber glow",
            "warm gradient color fields suggesting different global regions",
            "sophisticated upward momentum motifs, premium editorial quality"
        ]
    
    # 金融/市场类
    if "finance" in themes and "market" in themes:
        direction["style"] = "premium financial magazine cover illustration, Bloomberg Markets aesthetic"
        direction["color_primary"] = "warm charcoal and rich emerald with golden amber highlights"
        direction["color_secondary"] = "soft cream and warm copper"
        direction["mood"] = "dynamic, analytical, sophisticated, warm and engaging"
        direction["elements"] = [
            "elegant candlestick chart formations rendered in warm golden light",
            "flowing liquidity wave patterns in amber and emerald tones",
            "refined ascending trend lines with warm gradient lighting",
            "volumetric data structures in editorial 3D space, premium magazine quality"
        ]
    
    return direction


def _build_prompt(direction: dict, title: str) -> str:
    """构建最终的图片生成 prompt"""

    style_desc = direction["style"]
    colors = direction["color_primary"]
    mood = direction["mood"]
    elements = "\n  - ".join(direction["elements"])
    industry_ref = direction.get("industry_reference", 
        "premium Web3 and crypto industry publications like The Defiant and Blockworks — sophisticated, modern, and visually striking.")

    prompt = f"""CRITICAL INSTRUCTION: This image MUST contain NO text, NO words, NO letters, NO numbers, NO typography of any kind. Pure visual illustration only.

A {style_desc}. The overall aesthetic references {industry_ref} {mood} tone.

Color palette: {colors} with {direction['color_secondary']}. The overall image should feel WARM and BRIGHT — avoid cold or dark tones. Use golden hour lighting, warm ambient glow, and rich inviting colors throughout.

Visual elements (editorial illustration quality, NOT abstract — should feel like a real magazine cover image):
  - {elements}

Composition: {direction['composition']}. Ultra-high-end editorial quality, suitable for a premium financial magazine cover. Professional magazine-grade lighting with beautiful warm bokeh and depth of field. Clean, sophisticated composition with clear focal point. No text overlays, no labels, no captions, no watermarks. No photorealistic human faces (silhouettes and editorial illustrations only)."""
    
    return prompt


# ═══════════════════════════════════════════════════════════════
# Step 2: 调用 gpt-image-2 生成图片
# ═══════════════════════════════════════════════════════════════

def generate_image(prompt: str, quality: str = "medium", output_dir: str = None) -> str:
    """调用 gpt-image-2 API 生成封面图"""
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))
    
    if not API_KEY:
        raise RuntimeError(
            "API Key 未配置。请设置环境变量 COVER_API_KEY 或创建 "
            f"{SECRETS_FILE} 文件，格式：{{\"baseURL\": \"...\", \"apiKey\": \"sk-...\"}}"
        )
    
    date_str = datetime.now().strftime("%Y%m%d")
    resp_file = os.path.join(output_dir, f"_cover_resp_{date_str}.json")
    output_path = os.path.join(output_dir, f"article_cover_{date_str}.png")
    
    print(f"[Image] 调用 gpt-image-2 API...")
    print(f"[Image] Prompt 长度: {len(prompt)} 字符")
    print(f"[Image] 尺寸: {IMAGE_SIZE}, 质量: {quality}")
    
    payload = {
        "model": IMAGE_MODEL,
        "prompt": prompt,
        "n": 1,
        "size": IMAGE_SIZE,
        "quality": quality,
    }
    
    json_path = os.path.join(output_dir, "_cover_payload.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)
    
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
    if os.path.exists(json_path):
        os.remove(json_path)
    
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: exit code {result.returncode}")
    
    if not os.path.exists(resp_file) or os.path.getsize(resp_file) < 10:
        raise RuntimeError("Empty or missing response file")
    
    with open(resp_file) as f:
        data = json.load(f)
    
    if "error" in data:
        raise RuntimeError(f"API error: {data['error'].get('message', str(data['error']))}")
    
    if "data" not in data:
        raise RuntimeError(f"Missing 'data' in response. Keys: {list(data.keys())}")
    
    img_entry = data["data"][0]
    from_url = False
    
    if "b64_json" in img_entry:
        img_data = base64.b64decode(img_entry["b64_json"])
    elif "url" in img_entry:
        print(f"[Image] 从 URL 下载图片: {img_entry['url'][:80]}...")
        download_cmd = [
            'curl', '-s', '-o', output_path,
            '--noproxy', '*',
            '--max-time', '120',
            '--retry', '3',
            '--retry-delay', '5',
            img_entry['url']
        ]
        dl_result = subprocess.run(download_cmd, capture_output=True, text=True, timeout=180)
        if dl_result.returncode != 0:
            raise RuntimeError(f"Download failed: {dl_result.returncode}")
        if not os.path.exists(output_path) or os.path.getsize(output_path) < 100:
            raise RuntimeError("Downloaded file is empty or too small")
        from_url = True
    else:
        raise RuntimeError(f"Unknown image format. Keys: {list(img_entry.keys())}")
    
    if not from_url:
        with open(output_path, 'wb') as f:
            f.write(img_data)
    
    size_kb = os.path.getsize(output_path) / 1024
    print(f"[Image] ✅ 已保存: {output_path} ({size_kb:.1f} KB)")
    
    if os.path.exists(resp_file):
        os.remove(resp_file)
    
    return output_path


# ═══════════════════════════════════════════════════════════════
# Step 3: 上传到 WordPress 媒体库（可选）
# ═══════════════════════════════════════════════════════════════

def _wp_enabled():
    """检查 WordPress 配置是否完整"""
    return bool(WP_URL and WP_USER and WP_PASS)


def get_wp_auth():
    """生成 WordPress Basic Auth header"""
    credentials = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    return {
        "Authorization": f"Basic {credentials}",
        "User-Agent": "Article-Cover-Engine/1.0",
    }


def upload_to_wordpress(image_path: str) -> dict:
    """上传图片到 WordPress 媒体库"""
    if not _wp_enabled():
        print("[WP] ⚠️ WordPress 未配置，跳过上传。设置 WP_URL/WP_USER/WP_PASS 环境变量即可启用。")
        return None

    filename = os.path.basename(image_path)
    
    with open(image_path, 'rb') as f:
        img_data = f.read()
    
    headers = get_wp_auth()
    files = {
        'file': (filename, img_data, 'image/png')
    }
    
    resp = requests.post(
        f"{WP_API}/media",
        headers=headers,
        files=files,
        timeout=120
    )
    
    if resp.status_code not in [200, 201]:
        print(f"[WP] ❌ 上传失败: HTTP {resp.status_code}")
        print(f"[WP] Response: {resp.text[:500]}")
        return None
    
    media = resp.json()
    media_id = media.get("id")
    media_url = media.get("source_url", "")
    print(f"[WP] ✅ 媒体上传成功: ID={media_id}, URL={media_url}")
    
    return {"id": media_id, "url": media_url}


def set_featured_image(post_id: int, media_id: int) -> bool:
    """设置文章封面图"""
    if not _wp_enabled():
        print("[WP] ⚠️ WordPress 未配置，跳过设置封面。")
        return False

    headers = get_wp_auth()
    headers["Content-Type"] = "application/json"
    
    resp = requests.post(
        f"{WP_API}/posts/{post_id}",
        headers=headers,
        json={"featured_media": media_id},
        timeout=30
    )
    
    if resp.status_code in [200, 201]:
        print(f"[WP] ✅ 封面图已设置: post={post_id}, media={media_id}")
        return True
    else:
        print(f"[WP] ❌ 设置封面失败: HTTP {resp.status_code}")
        print(f"[WP] Response: {resp.text[:300]}")
        return False


# ═══════════════════════════════════════════════════════════════
# Step 4: 完整流程
# ═══════════════════════════════════════════════════════════════

def run_full_pipeline(article_path: str, quality: str = "medium", post_id: int = None):
    """
    完整封面图生成流程
    
    Args:
        article_path: Markdown 文件路径
        quality: 图片质量 (low/medium/high)
        post_id: 可选，已有的 WP 文章 ID，用于直接设置封面
    """
    print("=" * 60)
    print("Article Cover Engine - 文章封面图生成引擎")
    print("=" * 60)
    
    # Step 1: 读取文章
    print(f"\n[1/4] 读取文章: {article_path}")
    with open(article_path, 'r', encoding='utf-8') as f:
        article_text = f.read()
    print(f"      文章长度: {len(article_text)} 字符")
    
    info = extract_article_essence(article_text)
    print(f"      标题: {info['title'][:60]}")
    print(f"      行业: {', '.join(info.get('industries', [])) or '通用'}")
    print(f"      主题: {', '.join(info['themes'])}")
    
    # Step 2: 生成提示词
    print(f"\n[2/4] 生成纯视觉提示词...")
    prompt = generate_visual_prompt(article_text)
    print(f"      Prompt 长度: {len(prompt)} 字符")
    print(f"      Prompt 预览:\n{prompt[:300]}...")
    
    # Step 3: 调用 API 生成图片
    print(f"\n[3/4] 生成封面图...")
    output_dir = os.path.dirname(os.path.abspath(article_path))
    image_path = generate_image(prompt, quality, output_dir)
    
    # Step 4: 上传到 WordPress（可选）
    print(f"\n[4/4] 上传到 WordPress...")
    media = upload_to_wordpress(image_path)
    
    if media and post_id:
        set_featured_image(post_id, media["id"])
    
    print("\n" + "=" * 60)
    print("✅ 完成！")
    print(f"   封面图: {image_path}")
    if media:
        print(f"   WP 媒体 ID: {media['id']}")
        print(f"   WP 媒体 URL: {media['url']}")
    print("=" * 60)
    
    return {
        "image_path": image_path,
        "media_id": media.get("id") if media else None,
        "media_url": media.get("url") if media else None,
        "prompt": prompt,
        "article_title": info["title"],
    }


# ═══════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Article Cover Engine - 文章封面图生成引擎")
    parser.add_argument("article", help="Markdown 文件路径")
    parser.add_argument("--quality", "-q", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--post-id", type=int, help="WordPress 文章 ID，用于设置封面")
    parser.add_argument("--prompt-only", action="store_true", help="仅生成提示词，不生成图片")
    args = parser.parse_args()
    
    if args.prompt_only:
        with open(args.article, 'r', encoding='utf-8') as f:
            text = f.read()
        prompt = generate_visual_prompt(text)
        print(prompt)
    else:
        result = run_full_pipeline(args.article, args.quality, args.post_id)
        print("\n--- RESULT ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))
