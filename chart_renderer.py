#!/usr/bin/env python3
"""通用图表渲染引擎 — 读取 JSON 规格文件自动生成数据图表。

JSON 规格格式：
{
  "charts": [
    {
      "type": "bar" | "bar_h" | "pie" | "line" | "contrast",
      "title": "图表标题",
      "subtitle": "可选副标题",
      "data": {
        "labels": ["标签1", "标签2", ...],
        "values": [100, 200, ...],            # bar/bar_h/line/contrast
        "colors": ["#E63946", ...],            # 可选，默认自动配色
        "value_labels": ["$6.1B", "$52M", ...] # 可选，自定义值标签
      },
      "annotate": "标注文本",                  # 可选，带箭头的注释框
      "annotate_xy": [x, y],                   # 注释起点坐标
      "annotate_text_xy": [x, y],              # 注释文字坐标
      "position_hint": "二、行业现状",          # 嵌入位置提示（供 AI 参考）
      "width": 10,                             # 可选，默认10
      "height": 5.5,                           # 可选，默认5.5
      "dpi": 150                               # 可选，默认150
    }
  ]
}
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import json
import sys
import os

# ── 中文字体配置 ──────────────────────────────
def _find_chinese_font():
    """Search system fonts for a Chinese-capable font."""
    for m in fm.findSystemFonts():
        try:
            prop = fm.FontProperties(fname=m)
            name = prop.get_name()
            if any(kw in name.lower() for kw in ['pingfang', 'heiti', 'cjk', 'yahei', 'hei', 'noto sans sc']):
                return m
        except:
            continue
    return None

_font_path = _find_chinese_font()
if _font_path:
    _font_prop = fm.FontProperties(fname=_font_path)
    plt.rcParams['font.family'] = _font_prop.get_name()
else:
    plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

# ── 配色方案 ──────────────────────────────────
PALETTE = {
    'primary':   '#264653',  # 深蓝绿 — 主标题/主轴
    'highlight': '#E63946',  # 红 — 重点/涨/对比高值
    'positive':  '#2A9D8F',  # 绿 — 跌/正面/对比低值
    'accent':    '#F4A261',  # 橙 — 辅色/第二重点
    'light':     '#E9C46A',  # 金黄 — 亮色
    'neutral':   '#888888',  # 灰 — 历史/非重点
    'bg':        '#F8F9FA',  # 浅灰 — 背景
}

# 自动配色序列（按重要性递减）
AUTO_COLORS = [
    PALETTE['highlight'],  # 第1项用红（最重要）
    PALETTE['positive'],   # 第2项用绿（对比）
    PALETTE['primary'],    # 第3项用深蓝绿
    PALETTE['accent'],     # 第4项用橙
    PALETTE['neutral'],    # 第5项用灰
    PALETTE['light'],      # 第6项用金
]


def _auto_colors(n):
    """Generate n colors, cycling AUTO_COLORS if needed."""
    colors = []
    for i in range(n):
        colors.append(AUTO_COLORS[i % len(AUTO_COLORS)])
    return colors


def _render_bar_h(spec):
    """横向柱状图 — 适合多项目对比."""
    data = spec['data']
    labels = data['labels']
    values = data['values']
    colors = data.get('colors', _auto_colors(len(labels)))
    value_labels = data.get('value_labels', None)
    title = spec.get('title', '')
    subtitle = spec.get('subtitle', '')
    annotate = spec.get('annotate', None)
    annotate_xy = spec.get('annotate_xy', None)
    annotate_text_xy = spec.get('annotate_text_xy', None)
    w = spec.get('width', 10)
    h = spec.get('height', 5.5)
    dpi = spec.get('dpi', 150)

    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(PALETTE['bg'])
    ax.set_facecolor(PALETTE['bg'])

    bars = ax.barh(labels, values, color=colors, height=0.65, edgecolor='white', linewidth=0.5)

    # Value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        vlabel = value_labels[i] if value_labels and i < len(value_labels) else f'{val}'
        ax.text(bar.get_width() + max(values) * 0.02, bar.get_y() + bar.get_height()/2,
                vlabel, va='center', ha='left', fontsize=12, fontweight='bold', color='#333333')

    ax.set_xlim(0, max(values) * 1.4)
    full_title = title
    if subtitle:
        full_title += f'\n{subtitle}'
    ax.set_title(full_title, fontsize=16, fontweight='bold', pad=15, color=PALETTE['primary'])
    ax.set_xlabel('数值', fontsize=12, color='#666666')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.spines['left'].set_color('#CCCCCC')
    ax.tick_params(axis='both', colors='#666666')

    if annotate:
        xy = annotate_xy if annotate_xy else (values[0], 0)
        xytext = annotate_text_xy if annotate_text_xy else (max(values) * 0.7, len(labels) * 0.3)
        ax.annotate(annotate, xy=xy, xytext=xytext,
                    fontsize=10, color=PALETTE['highlight'],
                    arrowprops=dict(arrowstyle='->', color=PALETTE['highlight'], lw=1.5),
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE0E0',
                              edgecolor=PALETTE['highlight'], alpha=0.8))

    plt.tight_layout()
    return fig, dpi


def _render_bar(spec):
    """纵向柱状图 — 适合少量项目对比."""
    data = spec['data']
    labels = data['labels']
    values = data['values']
    colors = data.get('colors', _auto_colors(len(labels)))
    value_labels = data.get('value_labels', None)
    title = spec.get('title', '')
    subtitle = spec.get('subtitle', '')
    annotate = spec.get('annotate', None)
    annotate_xy = spec.get('annotate_xy', None)
    annotate_text_xy = spec.get('annotate_text_xy', None)
    w = spec.get('width', 8)
    h = spec.get('height', 5)
    dpi = spec.get('dpi', 150)

    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(PALETTE['bg'])
    ax.set_facecolor(PALETTE['bg'])

    bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor='white', linewidth=0.5)

    # Value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        vlabel = value_labels[i] if value_labels and i < len(value_labels) else f'{val}'
        y_offset = max(values) * 0.03
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + y_offset,
                vlabel, ha='center', va='bottom', fontsize=14, fontweight='bold', color='#333333')

    ax.set_ylim(0, max(values) * 1.5)
    full_title = title
    if subtitle:
        full_title += f'\n{subtitle}'
    ax.set_title(full_title, fontsize=16, fontweight='bold', pad=15, color=PALETTE['primary'])
    ax.set_ylabel('数值', fontsize=12, color='#666666')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.spines['left'].set_color('#CCCCCC')
    ax.tick_params(axis='both', colors='#666666')

    if annotate:
        xy = annotate_xy if annotate_xy else (0, values[0])
        xytext = annotate_text_xy if annotate_text_xy else (len(labels) * 0.6, max(values) * 0.7)
        ax.annotate(annotate, xy=xy, xytext=xytext,
                    fontsize=11, fontweight='bold', color=PALETTE['highlight'],
                    arrowprops=dict(arrowstyle='->', color=PALETTE['highlight'], lw=2),
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE0E0',
                              edgecolor=PALETTE['highlight'], alpha=0.85))

    plt.tight_layout()
    return fig, dpi


def _render_pie(spec):
    """饼图 — 适合占比分布."""
    data = spec['data']
    labels = data['labels']
    values = data['values']
    colors = data.get('colors', _auto_colors(len(labels)))
    title = spec.get('title', '')
    subtitle = spec.get('subtitle', '')
    annotate = spec.get('annotate', None)
    w = spec.get('width', 8)
    h = spec.get('height', 5)
    dpi = spec.get('dpi', 150)

    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(PALETTE['bg'])
    ax.set_facecolor(PALETTE['bg'])

    explode = [0.05] + [0] * (len(values) - 1)  # 突出第一项
    wedges, texts, autotexts = ax.pie(
        values, explode=explode, labels=labels, colors=colors,
        autopct='%1.0f%%', startangle=90,
        textprops={'fontsize': 13, 'color': '#333333'},
        pctdistance=0.55,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    for at in autotexts:
        at.set_fontsize(15)
        at.set_fontweight('bold')
        at.set_color('white')

    full_title = title
    if subtitle:
        full_title += f'\n{subtitle}'
    ax.set_title(full_title, fontsize=16, fontweight='bold', pad=20, color=PALETTE['primary'])

    if annotate:
        ax.annotate(annotate, xy=(0.7, -0.1), xytext=(1.3, -0.3),
                    fontsize=10, color=PALETTE['highlight'],
                    arrowprops=dict(arrowstyle='->', color=PALETTE['highlight'], lw=1.5),
                    bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFE0E0',
                              edgecolor=PALETTE['highlight'], alpha=0.8))

    plt.tight_layout()
    return fig, dpi


def _render_line(spec):
    """折线图 — 适合趋势数据."""
    data = spec['data']
    labels = data['labels']
    values = data['values']
    colors = data.get('colors', [PALETTE['primary']])
    title = spec.get('title', '')
    subtitle = spec.get('subtitle', '')
    annotate = spec.get('annotate', None)
    annotate_xy = spec.get('annotate_xy', None)
    annotate_text_xy = spec.get('annotate_text_xy', None)
    w = spec.get('width', 10)
    h = spec.get('height', 5)
    dpi = spec.get('dpi', 150)

    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(PALETTE['bg'])
    ax.set_facecolor(PALETTE['bg'])

    ax.plot(range(len(labels)), values, color=colors[0], linewidth=2.5, marker='o',
            markersize=6, markerfacecolor=colors[0], markeredgecolor='white')

    # Data point labels
    for i, (val, lbl) in enumerate(zip(values, labels)):
        ax.annotate(f'{val}', xy=(i, val), xytext=(i, val + max(values) * 0.08),
                    fontsize=9, ha='center', color='#333333', fontweight='bold')

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=11)
    full_title = title
    if subtitle:
        full_title += f'\n{subtitle}'
    ax.set_title(full_title, fontsize=16, fontweight='bold', pad=15, color=PALETTE['primary'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#CCCCCC')
    ax.spines['left'].set_color('#CCCCCC')
    ax.tick_params(axis='both', colors='#666666')
    ax.grid(axis='y', alpha=0.3, color='#CCCCCC')

    if annotate:
        xy = annotate_xy if annotate_xy else (0, values[0])
        xytext = annotate_text_xy if annotate_text_xy else (len(labels) * 0.5, max(values) * 0.7)
        ax.annotate(annotate, xy=xy, xytext=xytext,
                    fontsize=10, color=PALETTE['highlight'],
                    arrowprops=dict(arrowstyle='->', color=PALETTE['highlight'], lw=1.5),
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE0E0',
                              edgecolor=PALETTE['highlight'], alpha=0.8))

    plt.tight_layout()
    return fig, dpi


def _render_contrast(spec):
    """对比柱状图 — 两个极端值对比，带比例标注."""
    # Reuse bar renderer but add contrast-specific defaults
    data = spec['data']
    if len(data['values']) == 2:
        if 'colors' not in data:
            data['colors'] = [PALETTE['highlight'], PALETTE['accent']]
    return _render_bar(spec)


# ── 渲染器映射 ─────────────────────────────────
RENDERERS = {
    'bar':      _render_bar,
    'bar_h':    _render_bar_h,
    'pie':      _render_pie,
    'line':     _render_line,
    'contrast': _render_contrast,
}


def render_charts(spec_path, output_dir=None):
    """Read JSON spec file and render all charts. Returns list of output PNG paths."""
    with open(spec_path, 'r', encoding='utf-8') as f:
        spec = json.load(f)

    if output_dir is None:
        output_dir = os.path.dirname(spec_path)

    charts = spec.get('charts', [])
    if not charts:
        print("⚠️  No charts found in spec file.")
        return []

    output_paths = []
    for i, chart_spec in enumerate(charts):
        chart_type = chart_spec.get('type', 'bar')
        renderer = RENDERERS.get(chart_type)
        if not renderer:
            print(f"⚠️  Unknown chart type '{chart_type}', skipping chart {i+1}.")
            continue

        fig, dpi = renderer(chart_spec)

        # Generate filename
        title_slug = chart_spec.get('title', f'chart_{i+1}').replace(' ', '_')[:30]
        filename = f"chart_{i+1}_{title_slug}.png"
        filepath = os.path.join(output_dir, filename)

        fig.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close(fig)
        output_paths.append(filepath)
        print(f"✅ Chart {i+1} ({chart_type}): {filepath}")

    return output_paths


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 chart_renderer.py <spec.json> [output_dir]")
        sys.exit(1)

    spec_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    paths = render_charts(spec_path, output_dir)
    print(f"\n📊 Generated {len(paths)} charts")
    for p in paths:
        print(f"  → {p}")