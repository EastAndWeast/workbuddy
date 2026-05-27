#!/usr/bin/env python3
"""
RWA 日报 → 视频 自动生成器（免费方案）
========================================
技术栈：Edge TTS（语音） + Pillow（画面） + moviepy（合成）
完全不依赖付费 API，所有环节零成本。

用法：
  python3 rwa_video_generator.py /tmp/rwa_morning_20260525.md
  python3 rwa_video_generator.py /tmp/rwa_morning_20260525.md --voice zh-CN-YunxiNeural --output output.mp4
"""

import asyncio
import json
import os
import re
import shutil
import sys
import tempfile
import textwrap
from pathlib import Path

# ============================================================
# 配置
# ============================================================

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 24

# 字体（macOS 系统自带，中文效果好）
FONT_BOLD = "/System/Library/Fonts/PingFang.ttc"
FONT_REGULAR = "/System/Library/Fonts/PingFang.ttc"

# 配色方案 —— RWA 金融专业风格
COLORS = {
    "title_bg": "#0C1A2B",       # 深蓝黑 标题页
    "title_text": "#FFFFFF",
    "section_bg": "#1A3A5C",    # 深蓝 分段标题
    "section_text": "#FFFFFF",
    "body_bg": "#F8F9FA",       # 浅灰 正文
    "body_text": "#1A1A2E",
    "quote_bg": "#E8F0FE",      # 浅蓝 引用
    "quote_text": "#2C3E50",
    "quote_bar": "#3498DB",
    "focus_bg": "#FFF3E0",      # 暖橙 今日焦点
    "focus_text": "#E65100",
    "data_bg": "#F5F5F5",       # 数据区
    "data_text": "#333333",
    "accent": "#E74C3C",        # 强调红
    "subtitle_bg": "rgba(0,0,0,0.7)",
    "subtitle_text": "#FFFFFF",
    "footer_bg": "#1A1A2E",
    "footer_text": "#8899AA",
}

# Edge TTS 默认语音
DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"

# ============================================================
# 1. Markdown 解析 → 场景列表
# ============================================================

def parse_markdown(md_text: str) -> list[dict]:
    """把 Markdown 拆成视频场景序列"""
    scenes = []
    lines = md_text.strip().split("\n")

    current_type = None
    current_lines = []

    def flush():
        nonlocal current_lines, current_type
        if not current_lines:
            return
        text = "\n".join(current_lines).strip()
        if text:
            scenes.append({"type": current_type, "text": text})
        current_lines = []
        current_type = None

    for line in lines:
        stripped = line.strip()

        # 空行 → 触发刷新（但连续空行合并）
        if not stripped:
            flush()
            continue

        # 标题 H1
        if stripped.startswith("# ") and not stripped.startswith("## "):
            flush()
            current_type = "title"
            current_lines = [stripped[2:].strip()]

        # 标题 H2
        elif stripped.startswith("## "):
            flush()
            current_type = "section"
            current_lines = [stripped[3:].strip()]

        # 引用块
        elif stripped.startswith("> "):
            if current_type != "quote":
                flush()
                current_type = "quote"
            clean = stripped[2:].strip()
            if clean.startswith("**") and clean.endswith("**"):
                clean = clean[2:-2]
            current_lines.append(clean)

        # 分隔线 → 跳过
        elif stripped == "---":
            flush()

        # 表格
        elif stripped.startswith("|"):
            if current_type != "table":
                flush()
                current_type = "table"
            current_lines.append(stripped)

        # 空引用的来源行
        elif stripped.startswith("> 来源"):
            if current_type != "quote":
                flush()
                current_type = "quote"
            current_lines.append(stripped[2:].strip())

        # 粗体标题行（今日焦点类）
        elif stripped.startswith("**") and stripped.endswith("**"):
            flush()
            current_type = "focus_title"
            current_lines = [stripped[2:-2].strip()]

        # 普通正文
        else:
            if current_type not in ("body", "quote", "table", None):
                flush()
            current_type = current_type or "body"
            # 去掉 inline markdown
            clean = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)
            clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
            current_lines.append(clean)

    flush()

    # 把表格渲染成纯文本
    processed = []
    for s in scenes:
        if s["type"] == "table":
            s["type"] = "data"
            # 简化表格 → 去掉分隔行
            rows = [row for row in s["text"].split("\n")
                    if not all(c in "-| :" for c in row)]
            s["text"] = "\n".join(rows)
        processed.append(s)

    return processed


# ============================================================
# 2. TTS 语音生成（Edge TTS，免费）
# ============================================================

async def generate_tts(text: str, output_path: str, voice: str = DEFAULT_VOICE):
    """用 Edge TTS 生成语音文件"""
    import edge_tts

    # TTS 友好的文本清洗
    clean = text.strip()
    clean = re.sub(r"[#>*_~`|]", "", clean)
    clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
    clean = re.sub(r"\s+", " ", clean)
    # 去除 emoji（Edge TTS 会朗读 emoji 的 unicode 名）
    clean = re.sub(r'[\U0001F300-\U0001F9FF]', '', clean)
    clean = re.sub(r'[\U0001F600-\U0001F64F]', '', clean)
    clean = re.sub(r'[\U0001F680-\U0001F6FF]', '', clean)
    clean = re.sub(r'[\U0001F1E0-\U0001F1FF]', '', clean)
    clean = re.sub(r'[\u2600-\u27BF]', '', clean)
    clean = re.sub(r'[\uFE0F]', '', clean)
    clean = clean.strip()

    if not clean or len(clean) < 3:
        return 0.0

    communicate = edge_tts.Communicate(clean, voice)
    await communicate.save(output_path)

    # 获取音频时长
    from moviepy import AudioFileClip
    with AudioFileClip(output_path) as ac:
        duration = ac.duration
    return duration


# ============================================================
# 3. 画面生成（Pillow，免费）
# ============================================================

def load_font(size: int, bold: bool = False) -> object:
    """加载中文字体"""
    from PIL import ImageFont
    font_path = FONT_BOLD if bold else FONT_REGULAR
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()


def draw_text_card(
    text: str,
    scene_type: str,
    bg_color: str = None,
    width: int = VIDEO_WIDTH,
    height: int = VIDEO_HEIGHT,
) -> str:
    """用 Pillow 生成一帧画面，返回图片路径"""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (width, height), bg_color or COLORS["body_bg"])
    draw = ImageDraw.Draw(img)

    if scene_type == "title":
        _draw_title_slide(draw, text, width, height)
    elif scene_type == "section":
        _draw_section_slide(draw, text, width, height)
    elif scene_type == "quote":
        _draw_quote_slide(draw, text, width, height)
    elif scene_type == "focus_title":
        _draw_focus_slide(draw, text, width, height)
    elif scene_type == "data":
        _draw_data_slide(draw, text, width, height)
    else:  # body
        _draw_body_slide(draw, text, width, height)

    out = tempfile.mktemp(suffix=".png")
    img.save(out, "PNG")
    return out


def _draw_title_slide(draw, text, w, h):
    """标题页：深色背景 + 大标题"""
    margin = 120
    font_title = load_font(64, bold=True)
    font_sub = load_font(28, bold=False)

    # 副标题行
    lines = text.split("\n")
    main_title = lines[0].strip()
    subtitle = ""
    for line in lines[1:]:
        stripped = line.strip()
        if stripped and len(stripped) > 5:
            subtitle = stripped
            break

    # 绘制装饰条
    draw.rectangle([margin, h // 2 - 120, margin + 6, h // 2 + 80], fill=COLORS["accent"])

    # 主标题
    y = h // 2 - 80
    for wrapped in _wrap_text(main_title, font_title, w - margin * 2 - 40):
        draw.text((margin + 30, y), wrapped, fill=COLORS["title_text"], font=font_title)
        y += 80

    # 副标题
    if subtitle:
        y = h // 2 + 40
        for wrapped in _wrap_text(subtitle, font_sub, w - margin * 2 - 40):
            draw.text((margin + 30, y), wrapped, fill="#8899AA", font=font_sub)
            y += 36

    # 底部署名
    footer = "RWA 日报 · 由 WorkBuddy AI 生成"
    bbox = draw.textbbox((0, 0), footer, font=font_sub)
    draw.text((w - margin - bbox[2], h - 60), footer, fill="#556677", font=font_sub)


def _draw_section_slide(draw, text, w, h):
    """分段标题：纯色背景 + 编号 + 标题"""
    font = load_font(52, bold=True)
    text_clean = text.strip()

    # 居中绘制
    y_center = h // 2 - 30
    for wrapped in _wrap_text(text_clean, font, w - 200):
        bbox = draw.textbbox((0, 0), wrapped, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((w - tw) // 2, y_center), wrapped, fill=COLORS["section_text"], font=font)
        y_center += 70


def _draw_body_slide(draw, text, w, h):
    """正文页：白色/浅灰背景 + 大字正文"""
    font_text = load_font(36, bold=False)
    font_bold = load_font(36, bold=True)

    margin_x = 160
    margin_y = 120
    max_w = w - margin_x * 2
    max_lines = 12

    paragraphs = text.split("\n")
    y = margin_y

    for para in paragraphs:
        para = para.strip()
        if not para:
            y += 20
            continue
        if y > h - 120:
            break

        # 处理加粗片段（用 ** 标记的）
        if "**" in para:
            # 简化：整段用 bold 字体
            parts = re.split(r"(\*\*.*?\*\*)", para)
            x = margin_x
            line_buf = ""
            line_chars = []
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    inner = part[2:-2]
                    for ch in inner:
                        line_chars.append((ch, True))
                else:
                    for ch in part:
                        line_chars.append((ch, False))

            # 简单按字符数折行
            current = ""
            current_bolds = []
            for ch, is_bold in line_chars:
                test = current + ch
                bbox = draw.textbbox((0, 0), test, font=font_bold)
                if bbox[2] - bbox[0] > max_w:
                    _draw_line_mixed(draw, current, current_bolds, margin_x, y, font_text, font_bold, COLORS["body_text"])
                    y += 50
                    current = ch
                    current_bolds = [is_bold]
                else:
                    current += ch
                    current_bolds.append(is_bold)
            if current:
                _draw_line_mixed(draw, current, current_bolds, margin_x, y, font_text, font_bold, COLORS["body_text"])
                y += 50
        else:
            for wrapped in _wrap_text(para, font_text, max_w):
                draw.text((margin_x, y), wrapped, fill=COLORS["body_text"], font=font_text)
                y += 50


def _draw_line_mixed(draw, text, bolds, x, y, font_reg, font_bold, color):
    """绘制混合粗细的一行文字"""
    if not text:
        return
    # 简化：整行用 regular（moviepy 字幕会做加粗）
    draw.text((x, y), text, fill=color, font=font_reg)


def _draw_quote_slide(draw, text, w, h):
    """引用/点评页：左边色条 + 引文"""
    font = load_font(34, bold=False)
    bar_x = 140
    text_x = 180
    max_w = w - text_x - 140

    # 左侧色条
    draw.rectangle([bar_x, 160, bar_x + 6, h - 160], fill=COLORS["quote_bar"])

    y = 200
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            y += 16
            continue
        for wrapped in _wrap_text(line, font, max_w):
            if y > h - 120:
                break
            color = COLORS["quote_text"]
            if "来源" in wrapped:
                color = "#8899AA"
            draw.text((text_x, y), wrapped, fill=color, font=font)
            y += 48


def _draw_focus_slide(draw, text, w, h):
    """今日焦点：醒目样式"""
    font = load_font(42, bold=True)
    margin = 140

    y = h // 2 - 40
    for wrapped in _wrap_text(text.strip(), font, w - margin * 2):
        bbox = draw.textbbox((0, 0), wrapped, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((w - tw) // 2, y), wrapped, fill=COLORS["focus_text"], font=font)
        y += 60


def _draw_data_slide(draw, text, w, h):
    """数据表格页"""
    font_header = load_font(32, bold=True)
    font_cell = load_font(28, bold=False)

    rows = text.strip().split("\n")
    if not rows:
        return

    # 跳过纯分隔行
    clean_rows = []
    for row in rows:
        if all(c in "-| :" for c in row):
            continue
        clean_rows.append(row)
    rows = clean_rows

    # 计算列宽
    all_cells = [[c.strip() for c in r.split("|")[1:-1]] for r in rows]
    col_widths = [0] * max(len(r) for r in all_cells)
    for row in all_cells:
        for i, cell in enumerate(row):
            bbox = draw.textbbox((0, 0), cell, font=font_cell)
            col_widths[i] = max(col_widths[i], bbox[2] - bbox[0] + 40)

    total_w = sum(col_widths)
    start_x = (w - total_w) // 2
    line_h = 52
    y = h // 2 - len(rows) * line_h // 2

    for ri, row in enumerate(all_cells):
        x = start_x
        font = font_header if ri == 0 else font_cell
        color = COLORS["accent"] if ri == 0 else COLORS["data_text"]
        for ci, cell in enumerate(row):
            draw.text((x + 20, y), cell, fill=color, font=font)
            x += col_widths[ci]
        y += line_h
        # 表头下划线
        if ri == 0:
            draw.line(
                [(start_x, y + 4), (start_x + total_w, y + 4)],
                fill=COLORS["accent"], width=2
            )
            y += 8


def _wrap_text(text: str, font, max_width: int) -> list[str]:
    """中文自动换行"""
    lines = []
    current = ""
    for ch in text:
        test = current + ch
        bbox = font.getbbox(test) if hasattr(font, 'getbbox') else (0, 0, len(test) * font.size // 2, font.size)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = ch
        else:
            current += ch
    if current:
        lines.append(current)
    return lines


# ============================================================
# 4. 视频合成（moviepy）
# ============================================================

def compose_video(
    scenes: list[dict],
    audio_dir: str,
    image_dir: str,
    output_path: str,
):
    """把画面和音频合成为 MP4"""
    from moviepy import (
        AudioFileClip,
        ColorClip,
        CompositeVideoClip,
        ImageClip,
        TextClip,
        concatenate_videoclips,
    )
    from PIL import ImageFont

    clips = []
    font_subtitle = FONT_REGULAR

    for i, scene in enumerate(scenes):
        audio_file = os.path.join(audio_dir, f"{i:04d}.mp3")
        image_file = os.path.join(image_dir, f"{i:04d}.png")

        if not os.path.exists(image_file):
            continue

        # 获取音频时长
        has_audio = os.path.exists(audio_file) and os.path.getsize(audio_file) > 100
        if has_audio:
            try:
                audio_clip = AudioFileClip(audio_file)
                duration = audio_clip.duration
            except Exception:
                duration = 3.0
                audio_clip = None
        else:
            duration = 2.0
            audio_clip = None

        duration = max(duration, 1.5)

        # 画面
        img_clip = ImageClip(image_file, duration=duration)

        # 字幕：屏幕底部
        subtitle_text = scene["text"].strip()
        subtitle_text = re.sub(r"[#>*_`|]", "", subtitle_text)
        subtitle_text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", subtitle_text)
        subtitle_text = re.sub(r"\s+", " ", subtitle_text)
        # 截断过长字幕
        if len(subtitle_text) > 120:
            subtitle_text = subtitle_text[:120] + "..."

        subtitle_clips = []
        if subtitle_text:
            try:
                txt = TextClip(
                    text=subtitle_text,
                    font=font_subtitle,
                    font_size=28,
                    color="white",
                    stroke_color="black",
                    stroke_width=2,
                    method="caption",
                    size=(VIDEO_WIDTH - 200, None),
                )
                txt = txt.with_position(("center", VIDEO_HEIGHT - 100))
                txt = txt.with_duration(duration)
                subtitle_clips.append(txt)
            except Exception:
                pass

        # 进度条（底部细线）
        bar_bg = ColorClip(
            size=(VIDEO_WIDTH, 4),
            color=(60, 60, 60),
        ).with_position((0, VIDEO_HEIGHT - 4)).with_duration(duration)
        bar_fg = ColorClip(
            size=(int(VIDEO_WIDTH * (i + 1) / max(len(scenes), 1)), 4),
            color=(231, 76, 60),
        ).with_position((0, VIDEO_HEIGHT - 4)).with_duration(duration)

        # 组合
        layers = [img_clip, bar_bg, bar_fg] + subtitle_clips
        if audio_clip:
            layers[0] = img_clip.with_audio(audio_clip)

        comp = CompositeVideoClip(layers)
        clips.append(comp)

    if not clips:
        print("错误：没有可用的视频片段")
        return

    final = concatenate_videoclips(clips, method="compose")
    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="2000k",
        threads=4,
    )
    print(f"\n✅ 视频已生成：{output_path}")


# ============================================================
# 5. 主流程
# ============================================================

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="RWA 日报 → 视频生成器")
    parser.add_argument("input", help="输入的 Markdown 文件路径")
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Edge TTS 语音（默认: {DEFAULT_VOICE}）")
    parser.add_argument("--output", default=None, help="输出的 MP4 文件路径")
    parser.add_argument("--dry-run", action="store_true", help="只解析不生成")
    args = parser.parse_args()

    # 读取 Markdown
    md_path = Path(args.input)
    if not md_path.exists():
        print(f"错误：文件不存在 - {md_path}")
        sys.exit(1)

    md_text = md_path.read_text(encoding="utf-8")
    scenes = parse_markdown(md_text)

    print(f"\n📄 解析完成：{len(scenes)} 个场景")
    for i, s in enumerate(scenes):
        preview = s["text"][:60].replace("\n", " ")
        print(f"  [{i:02d}] {s['type']:12s} | {preview}...")

    if args.dry_run:
        print("\n🔍 Dry run 完成（未生成视频）")
        return

    # 确定输出路径
    if args.output:
        output_path = args.output
    else:
        stem = md_path.stem
        output_path = str(md_path.parent / f"{stem}.mp4")

    # 临时目录
    tmpdir = tempfile.mkdtemp(prefix="rwa_video_")
    audio_dir = os.path.join(tmpdir, "audio")
    image_dir = os.path.join(tmpdir, "image")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    try:
        # Phase 1: 生成语音（并发生成，加速）
        print(f"\n🎙️  生成语音（{args.voice}）...")
        tasks = []
        for i, scene in enumerate(scenes):
            audio_path = os.path.join(audio_dir, f"{i:04d}.mp3")
            tasks.append(generate_tts(scene["text"], audio_path, args.voice))

        durations = await asyncio.gather(*tasks)
        total_dur = sum(d for d in durations if d)
        print(f"  ✅ 语音完成，总时长约 {total_dur:.0f} 秒")

        # Phase 2: 生成画面
        print(f"\n🖼️  生成画面...")
        bg_map = {
            "title": COLORS["title_bg"],
            "section": COLORS["section_bg"],
            "quote": COLORS["quote_bg"],
            "focus_title": COLORS["focus_bg"],
            "data": COLORS["data_bg"],
            "body": COLORS["body_bg"],
        }
        for i, scene in enumerate(scenes):
            bg = bg_map.get(scene["type"], COLORS["body_bg"])
            img_path = draw_text_card(scene["text"], scene["type"], bg_color=bg)
            # 移到目标位置
            dest = os.path.join(image_dir, f"{i:04d}.png")
            shutil.move(img_path, dest)
        print(f"  ✅ 画面完成")

        # Phase 3: 合成视频
        print(f"\n🎬 合成视频...")
        compose_video(scenes, audio_dir, image_dir, output_path)

        # 输出信息
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"\n📊 视频信息：")
        print(f"   文件：{output_path}")
        print(f"   大小：{size_mb:.1f} MB")
        print(f"   场景数：{len(scenes)}")
        print(f"   时长：约 {total_dur:.0f} 秒")

    finally:
        # 清理临时文件
        shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
