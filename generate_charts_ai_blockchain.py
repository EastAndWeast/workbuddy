#!/usr/bin/env python3
"""为 AI×区块链文章生成内联数据图表"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import sys

# 尝试加载中文字体
chinese_fonts = ['PingFang SC', 'Heiti SC', 'STHeiti', 'Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC']
font_found = None
for fname in chinese_fonts:
    matches = fm.findSystemFonts()
    for m in matches:
        try:
            prop = fm.FontProperties(fname=m)
            if prop.get_name() == fname:
                font_found = m
                break
        except:
            continue
    if font_found:
        break

# fallback: search by file path
if not font_found:
    for m in fm.findSystemFonts():
        try:
            prop = fm.FontProperties(fname=m)
            name = prop.get_name()
            if any(kw in name.lower() for kw in ['pingfang', 'heiti', 'cjk', 'yahei', 'hei']):
                font_found = m
                break
        except:
            continue

if font_found:
    plt.rcParams['font.family'] = fm.FontProperties(fname=font_found).get_name()
    plt.rcParams['axes.unicode_minus'] = False
else:
    # Use a safe fallback
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False

output_dir = '/Users/bruce/WorkBuddy/Claw'

# Color palette - financial / magazine style
C_RED = '#E63946'      # 涨 / 重点 / 印度
C_GREEN = '#2A9D8F'    # 跌 / 对比 / 日本
C_BLUE = '#264653'     # 主色
C_ORANGE = '#F4A261'   # 辅色
C_LIGHT = '#E9C46A'    # 亮色
C_BG = '#F8F9FA'       # 背景

# ============================================
# Chart 1: 加密税率对比 — 印度 vs 各国
# ============================================
fig, ax = plt.subplots(figsize=(10, 5.5))
fig.patch.set_facecolor(C_BG)
ax.set_facecolor(C_BG)

countries = ['印度\n(含附加税)', '印度\n(基础)', '日本\n(改革后)', '美国\n(长持)', '新加坡', '美国\n(短持)', '日本\n(改革前)', '迪拜\n(UAE)']
rates = [31.2, 30, 20, 15, 0, 37, 55, 0]
colors = [C_RED, C_RED, C_GREEN, C_BLUE, C_GREEN, C_ORANGE, '#888888', C_GREEN]

bars = ax.barh(countries, rates, color=colors, height=0.65, edgecolor='white', linewidth=0.5)

# Add value labels
for bar, rate in zip(bars, rates):
    label = f'{rate}%' if rate > 0 else '0% (免税)'
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, label,
            va='center', ha='left', fontsize=12, fontweight='bold', color='#333333')

ax.set_xlim(0, 65)
ax.set_title('全球主要市场加密资产税率对比', fontsize=16, fontweight='bold', pad=15, color=C_BLUE)
ax.set_xlabel('有效税率 (%)', fontsize=12, color='#666666')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#CCCCCC')
ax.spines['left'].set_color('#CCCCCC')
ax.tick_params(axis='both', colors='#666666')

# Add annotation box
ax.annotate('印度31.2% vs 日本改革后20%\n税率差距直接驱动资本流向',
            xy=(31.2, 0), xytext=(42, 2.5),
            fontsize=10, color=C_RED,
            arrowprops=dict(arrowstyle='->', color=C_RED, lw=1.5),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE0E0', edgecolor=C_RED, alpha=0.8))

plt.tight_layout()
chart1_path = os.path.join(output_dir, 'chart_tax_comparison_20260611.png')
fig.savefig(chart1_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print(f"✅ Chart 1 saved: {chart1_path}")

# ============================================
# Chart 2: 61亿美元外流 vs 5200万美元税收 — 投入产出荒谬比
# ============================================
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor(C_BG)
ax.set_facecolor(C_BG)

categories = ['年均资本外流', '年均实际征税']
values = [6100, 52]  # 百万美元
colors_bar = [C_RED, C_ORANGE]

bars = ax.bar(categories, values, color=colors_bar, width=0.5, edgecolor='white', linewidth=0.5)

# Value labels
for bar, val in zip(bars, values):
    if val >= 1000:
        label = f'${val/1000:.1f}B'
    else:
        label = f'${val}M'
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 80,
            label, ha='center', va='bottom', fontsize=14, fontweight='bold', color='#333333')

ax.set_ylim(0, 7500)
ax.set_title('印度加密税：投入产出荒谬比', fontsize=16, fontweight='bold', pad=15, color=C_BLUE)
ax.set_ylabel('金额（百万美元）', fontsize=12, color='#666666')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#CCCCCC')
ax.spines['left'].set_color('#CCCCCC')
ax.tick_params(axis='both', colors='#666666')

# Ratio annotation
ax.annotate('外流/征税 = 117:1\n每收1美元税，117美元逃出海外',
            xy=(0, 6100), xytext=(1.2, 5000),
            fontsize=11, fontweight='bold', color=C_RED,
            arrowprops=dict(arrowstyle='->', color=C_RED, lw=2),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFE0E0', edgecolor=C_RED, alpha=0.85))

plt.tight_layout()
chart2_path = os.path.join(output_dir, 'chart_outflow_vs_tax_20260611.png')
fig.savefig(chart2_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print(f"✅ Chart 2 saved: {chart2_path}")

# ============================================
# Chart 3: 印度加密交易量分布 — 90% 海外 vs 10% 国内
# ============================================
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor(C_BG)
ax.set_facecolor(C_BG)

# Pie chart
sizes = [90, 10]
labels = ['海外平台\n(Binance等)', '印度国内\n(WazirX等)']
colors_pie = [C_RED, C_GREEN]
explode = (0.05, 0)

wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors_pie,
                                    autopct='%1.0f%%', startangle=90,
                                    textprops={'fontsize': 13, 'color': '#333333'},
                                    pctdistance=0.55,
                                    wedgeprops={'edgecolor': 'white', 'linewidth': 2})

for autotext in autotexts:
    autotext.set_fontsize(15)
    autotext.set_fontweight('bold')
    autotext.set_color('white')

ax.set_title('印度加密交易量分布\n(2022.7-2023.7)', fontsize=16, fontweight='bold', pad=20, color=C_BLUE)

# Annotation
ax.annotate('420亿美元流向海外\n仅43.7亿卢比留在国内',
            xy=(0.7, -0.1), xytext=(1.3, -0.3),
            fontsize=10, color=C_RED,
            arrowprops=dict(arrowstyle='->', color=C_RED, lw=1.5),
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFE0E0', edgecolor=C_RED, alpha=0.8))

plt.tight_layout()
chart3_path = os.path.join(output_dir, 'chart_volume_distribution_20260611.png')
fig.savefig(chart3_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print(f"✅ Chart 3 saved: {chart3_path}")

print("\n📊 全部3张图表已生成完毕")
