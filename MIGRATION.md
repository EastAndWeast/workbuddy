# RWA 内容自动化迁移指南

从当前 WorkBuddy 迁移到新 WorkBuddy / OpenClaw 的完整操作手册。

---

## 一、迁移全景图

```
当前机器                              新机器
┌──────────────────┐                 ┌──────────────────┐
│  10 条自动化任务    │──JSON 导出────▶│  逐条 automation   │
│  (prompt+调度)     │                 │  _update create   │
├──────────────────┤                 ├──────────────────┤
│  5 个 Python 脚本  │──Git 同步────▶│  修改硬编码路径     │
│  (发布/封面/转换)   │                 │  + 凭证            │
├──────────────────┤                 ├──────────────────┤
│  3 个 Skills      │──手动安装────▶│  skills 目录       │
│  (rwa-policy 等)   │                 │                   │
├──────────────────┤                 ├──────────────────┤
│  lark-cli 认证    │──重新登录────▶│  lark-cli login   │
├──────────────────┤                 ├──────────────────┤
│  外部 API 凭证    │──随脚本迁移──▶│  同上（明文存储）   │
│  (WP / OpenClaw)  │                 │                   │
├──────────────────┤                 ├──────────────────┤
│  工作区记忆文件    │──Git 同步────▶│  .workbuddy/memory/ │
│  (.workbuddy/)    │                 │                   │
└──────────────────┘                 └──────────────────┘
```

---

## 二、迁移清单（按顺序执行）

### Step 1: Git 同步工作区

```bash
# 当前机器：推送到 GitHub
cd /Users/bruce/WorkBuddy/Claw
git add -A
git commit -m "Pre-migration snapshot"
git push origin main

# 新机器：克隆
git clone <your-github-repo-url> /path/to/new-workspace/Claw
```

**已包含的文件：**
- `automations-export.json` — 10 条自动化完整 prompt
- `requirements.txt` — Python 依赖
- `rwa_publish_wp.py` — WordPress 发布脚本
- `rwa_generate_cover.py` — 封面图生成
- `convert_md_to_html.py` — Markdown → HTML
- `rwa_auto_publish.py` — 飞书消息监听+WordPress 发布
- `rwa_video_generator.py` — 视频生成（Edge TTS + Pillow + moviepy）
- `.workbuddy/memory/` — 工作区日记
- `.workbuddy/automations/*/memory.md` — 自动化执行记忆

### Step 2: 修改硬编码路径

脚本中有大量硬编码路径，需要全局替换：

| 原路径 | 替换为 |
|--------|--------|
| `/Users/bruce/WorkBuddy/Claw` | 新机器上的工作区路径（如 `/home/user/Claw`） |
| `/Users/bruce/.npm-global/bin/lark-cli` | 新机器上的 lark-cli 路径（用 `which lark-cli` 确认） |

**涉及的文件（5个脚本）：**
- `rwa_publish_wp.py` — L19-21（WP 凭证）、L30（SCRIPT_DIR）
- `rwa_generate_cover.py` — L13-14（OpenClaw API）、L15（OUTPUT_DIR）、L20-21（WP 凭证）
- `rwa_auto_publish.py` — L16-20（飞书+WP 凭证）、L24（lark-cli 路径）
- `convert_md_to_html.py` — 无硬编码路径 ✅
- `rwa_video_generator.py` — 需检查 Edge TTS 依赖

### Step 3: 安装 Python 依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 视频生成器额外依赖（如需）
pip install edge-tts Pillow moviepy
```

### Step 4: 安装 lark-cli

```bash
npm install -g @larksuiteo/lark-cli
lark-cli login --as bot
# 输入飞书 App ID: cli_aa9ac6cf93385cb5
# 输入飞书 App Secret: 9N9vyRWWX6CZZK4F3RPCEcw03y78Wdxr
```

验证：`lark-cli --as bot whoami`

### Step 5: 安装 Skills

```bash
# rwa-policy-research（核心，早报+时评依赖）
# 方式1: 从 GitHub 安装（如果有公开 repo）
# 方式2: 手动复制 ~/.workbuddy/skills/ 目录

# 当前机器的 skills 列表：
# - ~/.workbuddy/skills/rwa-policy-research/
# - ~/.workbuddy/skills/ai-blockchain-writer/
# - ~/.workbuddy/skills/baoyu-comic/

# 从当前机器打包：
tar czf skills-backup.tar.gz -C ~/.workbuddy/skills .

# 新机器解压：
mkdir -p ~/.workbuddy/skills
tar xzf skills-backup.tar.gz -C ~/.workbuddy/skills
```

### Step 6: 导入自动化

读取 `automations-export.json`，逐条执行 `automation_update create`。

**关键修改点（每条自动化都需要）：**

1. **`cwds` 路径** — 改为新机器路径
2. **prompt 中的路径** — 搜索替换所有 `/Users/bruce/WorkBuddy/Claw`
3. **prompt 中的 lark-cli 路径** — 替换为新机器路径
4. **prompt 中的 automation ID** — 新机器会生成新 ID，需要同步更新 prompt 中引用的 memory 路径

⚠️ **automation ID 问题**：
当前 prompt 中硬编码了 automation ID（如 `automation-1779468949931`），
用于指定 memory 路径。新机器创建时会分配新 ID，需要：
- 先创建自动化，获取新 ID
- 再更新 prompt 中的 ID 引用

### Step 7: 验证

按时间顺序测试至少一个完整链路：

```
07:00 早报生成 → 07:05 飞书发布 → 用户"通过" → WordPress 发布
```

---

## 三、外部服务凭证清单

| 服务 | 用途 | 凭证位置 |
|------|------|---------|
| WordPress REST API | 发布文章+上传封面 | `rwa_publish_wp.py` L20-21 |
| WordPress REST API | 封面图生成脚本 | `rwa_generate_cover.py` L20-21 |
| OpenClaw API | AI 封面图生成 | `rwa_generate_cover.py` L13-14 |
| 飞书 App | lark-cli 认证 | `rwa_auto_publish.py` L16-17 |
| GitHub PAT | 每日备份推送 | git remote URL（已嵌入） |

---

## 四、飞书群 ID 清单

| 群 | Chat ID | 用途 |
|----|---------|------|
| RWA 早报（07:00WB） | `oc_b81de3a111b45394b2c1dca20dc33038` | 早报+行业早报审核 |
| RWA 时评 | `oc_29c8d746be4f75efd4eca6f5286819ed` | 时评审核 |
| AI×区块链 20点30 | `oc_01cdbb1c0f9f454f9774f5a6d492e531` | AI×区块链文章审核 |

**注意**：群 ID 是飞书内部的，不需要迁移。但 bot 需要已被邀请进这些群。

---

## 五、模型配置

| 自动化 | model_id | 备注 |
|--------|----------|------|
| RWA 早报每日生成 | `auto` | |
| RWA 早报飞书发布 | `auto` | |
| RWA 早报兜底检查 | （默认） | |
| RWA 行业早报生成 | `auto` | |
| RWA 行业早报飞书发布 | `auto` | |
| RWA 时政分析 | `deepseek-v4-pro` | ⚠️ 确认新机器支持 |
| RWA 时评飞书发布 | `auto` | |
| AI×区块链 文章生成 | （默认） | |
| AI×区块链 飞书发布 | `auto` | |
| GitHub 每日备份 | `auto` | |

---

## 六、OpenClaw 特殊说明

如果迁移到 OpenClaw（非 WorkBuddy 原版），需要额外确认：

1. **自动化系统** — OpenClaw 是否支持 `automation_update` 工具？调度机制是否一致？
2. **lark-cli Skills** — OpenClaw 是否内置 lark-* connector skills？还是需要手动安装？
3. **模型选择** — `deepseek-v4-pro` 在 OpenClaw 上是否可用？
4. **路径约定** — OpenClaw 的工作区路径结构是否与 WorkBuddy 一致？
5. **`{{date}}` / `{{date_compact}}`** — 模板变量是否同样支持？

---

## 七、一键导入脚本（新机器执行）

```python
#!/usr/bin/env python3
"""一键导入自动化到新机器。"""
import json

# 读取导出文件
with open('automations-export.json') as f:
    automations = json.load(f)

# 修改这里为新机器的配置
NEW_CWD = "/path/to/new-workspace/Claw"
NEW_LARK_CLI = "/usr/local/bin/lark-cli"  # 或 which lark-cli 的结果

for auto in automations:
    # 替换路径
    name = auto['name']
    prompt = auto['prompt']
    cwds = auto['cwds']

    # 替换 prompt 中的路径
    prompt = prompt.replace('/Users/bruce/WorkBuddy/Claw', NEW_CWD)
    prompt = prompt.replace('/Users/bruce/.npm-global/bin/lark-cli', NEW_LARK_CLI)
    cwds = cwds.replace('/Users/bruce/WorkBuddy/Claw', NEW_CWD)

    print(f"\n=== {name} ===")
    print(f"  scheduleType: {auto['scheduleType']}")
    print(f"  rrule: {auto['rrule']}")
    print(f"  model_id: {auto.get('model_id', 'default')}")
    print(f"  cwds: {cwds}")
    print(f"  prompt length: {len(prompt)} chars")
    print("  ⚠️ 需要手动执行 automation_update create")
    # 注意: 创建后会得到新 ID, 需要回去更新 prompt 中的 memory 路径
```

---

## 八、简化版：如果只是换机器

如果新机器同样是 WorkBuddy（不是 OpenClaw），迁移最简路径：

```bash
# 1. Git clone 工作区
git clone <repo> ~/WorkBuddy/Claw
cd ~/WorkBuddy/Claw

# 2. 全局替换路径
sed -i '' 's|/Users/bruce/WorkBuddy/Claw|/new/path/to/Claw|g' *.py
sed -i '' 's|/Users/bruce/.npm-global/bin/lark-cli|$(which lark-cli)|g' *.py

# 3. 安装依赖
pip install -r requirements.txt

# 4. 登录飞书
lark-cli login --as bot

# 5. 复制 skills
# （从老机器 scp ~/.workbuddy/skills/* 新机器:~/.workbuddy/skills/）

# 6. 导入自动化
# 读取 automations-export.json，逐条 automation_update create
```

**实际手动操作 ≤ 4 步**（pip install、lark-cli login、复制 skills、导入自动化），其余 Git 搞定。
