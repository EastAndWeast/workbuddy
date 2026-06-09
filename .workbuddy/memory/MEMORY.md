# 项目记忆 - Claw Workspace

## 自动化配置修复记录

### 2026-06-09: RWA 晚间时评自动化修复

**问题**: RWA 时政分析自动化（automation-1779468165411）连续 5 天失败（2026-06-05 至 2026-06-09）

**根因**:
1. **模型不可用**（2026-06-08）: 配置的 `deepseek-v4-pro` 模型实际调用 `claude-sonnet-4-20250514`，但该模型 service info not found
2. **内容安全误判**（2026-06-05, 06-06, 06-07）: 搜索到政策/监管内容后，模型误触发安全拒绝
3. **服务端 500 错误**（2026-06-09）: 纯服务端故障

**修复**:
- 模型从 `deepseek-v4-pro` 切换为 `auto`
- 手动触发时评生成成功（2026-06-09 18:55）

**教训**:
- 使用 `auto` 模型可以减少单模型依赖导致的不可用问题
- 内容安全误判需要通过加强 prompt 中的安全边界表述来降低概率

## 飞书群 chat_id 对照表

| 用途 | chat_id |
|------|---------|
| RWA 早报审核群 | `oc_b81de3a111b45394b2c1dca20dc33038` |
| RWA 时评审核群 | `oc_29c8d746be4f75efd4eca6f5286819ed` |
| AI×区块链审核群 | `oc_01cdbb1c0f9f454f9774f5a6d492e531` |

## WordPress 发布配置

- 发布脚本:
  - RWA 文章: `/Users/bruce/WorkBuddy/Claw/rwa_auto_publish.py`
  - AI×区块链文章: `/Users/bruce/WorkBuddy/Claw/publish_ai_blockchain.py`
- 配置文件: `/Users/bruce/WorkBuddy/Claw/.env` (WP_URL, WP_USER, WP_PASS)
- 网站 URL: https://www.tianao1128.online

## 文件命名规范

| 类型 | 文件名格式 | 示例 |
|------|-----------|------|
| RWA 早报 | `rwa_report_YYYYMMDD.md` | `rwa_report_20260609.md` |
| RWA 行业早报 | `rwa_industry_YYYYMMDD.md` | `rwa_industry_20260609.md` |
| RWA 时评 | `rwa_evening_YYYYMMDD.md` | `rwa_evening_20260609.md` |
| AI×区块链 | `ai_blockchain_YYYYMMDD.md` | `ai_blockchain_20260609.md` |
