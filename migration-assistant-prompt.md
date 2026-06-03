# WorkBuddy 迁移助手 — 粘贴到新 WorkBuddy 即可

> 把以下「用户提示词」部分复制粘贴到新 WorkBuddy 的对话框里，AI 会自动完成所有配置。

---

## 用户提示词（复制这一段 ↓）

```
你好，我要把 RWA 自动化任务从另一台机器迁移过来。工作区代码已经 git clone 到当前目录了。

请你帮我完成以下迁移工作：

## 第一步：确认工作区位置
先确认当前工作区的完整路径（用 pwd 获取）。

## 第二步：安装 Python 依赖
运行：
```bash
pip install -r requirements.txt
```

## 第三步：配置 .env 文件
工作区根目录有一个 `.env.example` 文件，请读取它，然后问我以下信息（一个一个问，不要一次全问）：

1. WordPress 站点地址（如 https://www.example.com）
2. WordPress 用户名
3. WordPress Application Password
4. 飞书 App ID（cli_ 开头）
5. 飞书 App Secret
6. 飞书审核群中你的 open_id（ou_ 开头）
7. 封面图 API Key（如不需要封面图生成，可跳过）

收到每个回答后，直接帮我创建 `.env` 文件，填入对应值。

## 第四步：验证配置
创建完 .env 后，运行验证脚本确认所有环境变量正确加载：
```bash
cd <工作区路径> && python3 -c "
import dotenv, os
dotenv.load_dotenv('.env')
for k in ['WP_URL','WP_USER','WP_PASS','WP_XMLRPC_URL','WP_CATEGORY_ID',
          'FEISHU_APP_ID','FEISHU_APP_SECRET','FEISHU_AUDIT_USER_OPEN_ID',
          'COVER_API_URL','COVER_API_KEY']:
    v = os.getenv(k, 'NOT SET')
    if 'PASS' in k or 'SECRET' in k or 'KEY' in k:
        v = v[:6] + '...' if len(v) > 6 else v
    print(f'  {k}: {v}')
print('ALL OK' if all(os.getenv(k) for k in ['WP_USER','WP_PASS','FEISHU_APP_ID']) else 'MISSING CONFIG')
"
```

## 第五步：导入自动化任务
工作区有一个 `automations-export.json` 文件，里面是 10 条自动化任务的定义。

请逐条导入，但注意以下修改：
1. **cwds 路径**：把所有 `/Users/bruce/WorkBuddy/Claw` 替换为当前工作区的实际路径
2. **prompt 里的路径**：把 prompt 中所有 `/Users/bruce/WorkBuddy/Claw` 替换为当前工作区的实际路径
3. **prompt 里的 automation ID**：创建自动化后拿到新 ID，需要把 prompt 中引用的旧 automation ID（格式为 `automation-1779XXXXXXXXX`）替换为新 ID
4. **model_id**：如果 `deepseek-v4-pro` 不可用，改为 `auto`

对于 automation ID 的处理方式：
- 先创建自动化
- 拿到新 ID 后，更新该自动化的 prompt，把旧 ID 替换为新 ID

## 第六步：飞书认证（如果需要）
如果自动化涉及飞书操作，提醒我运行：
```bash
lark-cli login --as bot
```

## 完成后
给我一份清单，列出：
- 所有已导入的自动化（名称 + 时间 + ID）
- 所有配置项（隐藏密码）
- 还需要我手动做什么（如果有）
```

---

## 说明

把上面 ``` ``` 里的内容复制到新 WorkBuddy 的对话框，AI 会：

1. 自动找到工作区路径
2. 安装依赖
3. 一个个问你凭证信息，帮你创建 .env
4. 导入全部 10 条自动化，自动替换路径和 ID
5. 验证配置
6. 给你一份完整的迁移报告

**你唯一需要做的**：回答它问你的几个凭证信息（WordPress 地址/密码、飞书 App ID 等），剩下的它全搞定。
