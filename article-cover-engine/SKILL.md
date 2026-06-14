---
name: article-cover-engine
description: "文章封面图自动生成引擎。从 Markdown 文章自动提取主题与行业（AI/区块链/金融/科技），生成纯视觉提示词（无文字），调用 gpt-image-2 API 生成 1792x1024 横幅杂志风格封面图，可选上传至 WordPress 媒体库。触发场景：用户需要为文章生成封面图时、发布文章到 WordPress 需要封面时。"
---

# Article Cover Engine - 文章封面图自动生成引擎

## 功能

- **纯视觉封面**：图片不含任何文字，适配多语言场景
- **行业自动感知**：根据文章内容自动识别 AI/区块链/金融/科技行业，匹配对应视觉出版物风格
- **暖亮色调**：温暖金色调 + 柔和奶油色，明亮不沉闷
- **杂志海报质感**：Bloomberg Markets × The Economist × The Defiant 风格
- **横幅比例**：1792 × 1024（接近 2.35:1 影院比例）
- **可选 WordPress 上传**：配置 WP 凭据后自动上传到媒体库

## 前置条件

### 1. 图像生成 API 凭据（必需）

方式一：创建 secrets 文件 `~/.workbuddy/secrets/openai_image.json`：

```json
{
  "baseURL": "https://your-api-endpoint.com",
  "apiKey": "sk-xxxxxxxxxxxxxxxxxxxxxx"
}
```

方式二：通过环境变量：

```bash
export COVER_API_BASE="https://your-api-endpoint.com"
export COVER_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxx"
```

API 需兼容 OpenAI gpt-image-2 接口格式（`/v1/images/generations`）。

### 2. WordPress 配置（可选）

不配置也能生成图片，只是不会自动上传。设置以下环境变量即可启用：

```bash
export WP_URL="https://your-wordpress-site.com"
export WP_USER="your-username"
export WP_PASS="your-application-password"
```

### 3. Python 依赖

```bash
pip install requests
```

## 使用方法

### 基本用法

```bash
python3 scripts/cover_engine.py article.md
```

### 指定图片质量

```bash
python3 scripts/cover_engine.py article.md --quality high
```

质量选项：`low` / `medium`（默认）/ `high`

### 仅预览提示词（不生成图片）

```bash
python3 scripts/cover_engine.py article.md --prompt-only
```

### 生成并设为 WordPress 文章封面

```bash
python3 scripts/cover_engine.py article.md --post-id 123
```

## 行业匹配参考

| 行业 | 触发词 | 视觉出版物参考 |
|------|--------|---------------|
| **AI** | AI、大模型、GPT、LLM、深度学习、智能体 | MIT Technology Review, HBR, VentureBeat |
| **区块链** | 区块链、crypto、Web3、DeFi、NFT、token | The Defiant, Blockworks, CoinDesk, Decrypt |
| **金融** | 银行、证券、央行、RWA、稳定币、利率 | Bloomberg Markets, The Economist, FT, Fortune |
| **科技** | 云计算、大数据、5G、芯片、数字化 | Wired, Fast Company, MIT Technology Review |

## 视觉风格规范

- **色调**：暖金色 + 琥珀 + 柔软奶油色，明亮热烈
- **质感**：编辑级杂志插图，非纯抽象几何
- **比例**：1792 × 1024 横幅（接近 2.35:1）
- **文字**：绝对禁止任何文字、字母、数字
- **人脸**：禁止真人照片面部（剪影和编辑插画允许）

## 输出

脚本完成后输出 JSON 结果，包含：
- `image_path` — 本地图片路径
- `media_id` — WordPress 媒体库 ID（如已配置）
- `media_url` — WordPress 可访问的图片 URL（如已配置）
- `article_title` — 文章标题
