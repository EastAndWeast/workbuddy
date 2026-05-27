# RWA 政策日报 - 自动化说明

## 完整流程

```
每天 19:00 (Cron)
    ↓
自动执行 rwa-policy-research skill
    ↓
生成 Mode B 深度分析报告
    ↓
lark-cli 创建飞书文档（v1 + --title）
    ↓
发送飞书消息给 Bruce（open_id: ou_3cadaa20ce7e2a1e22cce9eabbd89346）
    ↓
Bruce 审核 → 回复消息/发 IM 给 AI：「通过」
    ↓
AI 收到"通过" → 立即推送文章到 WordPress（正式发布，非草稿）
```

## 自动化任务

| 项目 | 内容 |
|------|------|
| 任务 ID | `automation-1779468165411` |
| 名称 | RWA 政策日报 - 生成并推送审核 |
| 频率 | 每天 19:00 |
| Cron | `REQ=DAILY;BYHOUR=19;BYMINUTE=0` |
| 状态 | ACTIVE |

## 审核通过后的触发方式

Bruce 在飞书/IM 中发消息给 AI，内容包含以下任一关键词即触发发布：
- `通过`
- `发布`
- `publish`
- `同意`
- `OK` / `ok`

## WordPress 发布配置

| 项目 | 值 |
|------|-----|
| 域名 | `https://www.tianao1128.online` |
| 接口 | `/wp-json/wp/v2/posts` |
| 认证 | 应用密码 `Z0IfWp8I2PNdKEeDgopRCXmU` |
| 用户名 | `tianao1128` |
| 发布状态 | `publish`（正式发布，非草稿） |
| 分类 | `[1]`（默认分类） |

## 飞书配置

| 项目 | 值 |
|------|-----|
| App ID | `cli_aa9ac6cf93385cb5` |
| 用户 open_id | `ou_3cadaa20ce7e2a1e22cce9eabbd89346` |
| 文档创建 | `lark-cli docs +create --api-version v1 --title "..."` |
| ⚠️ 注意 | v2 的 --title 有 bug，必须用 v1 |

## 手动触发发布

如果自动化未触发，Bruce 可以手动发消息：
> "通过，发布 https://my.feishu.cn/docx/XXX"

AI 会：
1. 读取飞书文档内容
2. 转换为 HTML
3. POST 到 WordPress `/wp-json/wp/v2/posts`
4. 返回文章链接
