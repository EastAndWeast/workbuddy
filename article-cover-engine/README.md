# Article Cover Engine - 文章封面图自动生成引擎

为行业文章自动生成杂志海报风格的纯视觉封面图（无文字），通过 gpt-image-2 API 生成，可选上传至 WordPress 媒体库。

## 特性

- 纯视觉封面，不含任何文字，适配多语言
- 自动识别 AI / 区块链 / 金融 / 科技四大行业，匹配对应视觉风格
- 暖亮金色调 + 杂志海报质感（Bloomberg / The Economist / The Defiant 风格）
- 1792 × 1024 横幅比例
- 可选 WordPress 自动上传

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置 API 凭据

创建文件 `~/.workbuddy/secrets/openai_image.json`：

```json
{
  "baseURL": "https://your-api-endpoint.com",
  "apiKey": "sk-xxxxxxxxxxxxxxxxxxxxxx"
}
```

或通过环境变量：

```bash
export COVER_API_BASE="https://your-api-endpoint.com"
export COVER_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxx"
```

> API 需兼容 OpenAI gpt-image-2 接口格式（`/v1/images/generations`）。

### 3. 生成封面

```bash
python3 scripts/cover_engine.py your_article.md
```

生成的封面图会保存在文章同目录下，文件名格式 `article_cover_YYYYMMDD.png`。

### 4.（可选）配置 WordPress 上传

```bash
export WP_URL="https://your-wordpress-site.com"
export WP_USER="your-username"
export WP_PASS="your-application-password"
```

配置后封面图会自动上传到 WordPress 媒体库。

## 使用示例

```bash
# 基本用法
python3 scripts/cover_engine.py article.md

# 指定高质量
python3 scripts/cover_engine.py article.md --quality high

# 仅预览提示词，不生成图片
python3 scripts/cover_engine.py article.md --prompt-only

# 生成并设为 WordPress 文章封面
python3 scripts/cover_engine.py article.md --post-id 123
```

## 行业自动识别

| 行业 | 触发词 | 视觉风格参考 |
|------|--------|-------------|
| AI | AI、大模型、GPT、LLM、深度学习 | MIT Technology Review, HBR, VentureBeat |
| 区块链 | 区块链、crypto、Web3、DeFi、NFT | The Defiant, Blockworks, CoinDesk |
| 金融 | 银行、证券、央行、RWA、稳定币 | Bloomberg Markets, The Economist, FT |
| 科技 | 云计算、大数据、5G、芯片 | Wired, Fast Company, MIT Tech Review |

## 参数说明

| 参数 | 说明 | 可选值 |
|------|------|--------|
| `article` | Markdown 文件路径（必填） | - |
| `--quality, -q` | 图片质量 | `low` / `medium`（默认）/ `high` |
| `--prompt-only` | 仅生成提示词，不调 API | - |
| `--post-id` | WordPress 文章 ID，设置封面 | 整数 |

## 输出

```json
{
  "image_path": "/path/to/article_cover_20260612.png",
  "media_id": 798,
  "media_url": "https://example.com/wp-content/uploads/.../cover.png",
  "article_title": "你的文章标题"
}
```

## 安装为 WorkBuddy Skill

将整个 `article-cover-engine` 文件夹复制到 `~/.workbuddy/skills/` 目录即可：

```bash
cp -r article-cover-engine ~/.workbuddy/skills/
```

## License

MIT
