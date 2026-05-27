#!/usr/bin/env python3
"""
RWA Policy Research - WordPress Auto-Publish Handler
监听飞书消息，当用户回复"通过"时自动发布到 WordPress
"""

import os
import sys
import json
import time
import subprocess
import re
from datetime import datetime

# Config
FEISHU_APP_ID = "cli_aa9ac6cf93385cb5"
FEISHU_APP_SECRET = "9N9vyRWWX6CZZK4F3RPCEcw03y78Wdxr"
WP_URL = "https://www.tianao1128.online/wp-json/wp/v2"
WP_USER = "tianao1128"
WP_PASS = "Z0If Wp8I2PNdKEeDgopRCXmU"

def get_latest_feishu_message(open_id):
    """获取用户最新消息"""
    cmd = f"LARK_CLI_NO_PROXY=1 npx lark-cli api GET '/open-apis/im/v1/messages?container_id={open_id}&page_size=5'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def is_approved(message_text):
    """判断是否包含通过指令"""
    keywords = ["通过", "发布", "publish", "同意", "OK", "ok"]
    return any(kw in message_text for kw in keywords)

def find_latest_rwa_doc():
    """找到最近创建的 RWA 飞书文档"""
    cmd = "LARK_CLI_NO_PROXY=1 npx lark-cli docs +search --api-version v1 --keyword 'RWA 时评'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout

def convert_feishu_to_html(doc_url):
    """将飞书文档转换为 HTML"""
    # 获取文档内容
    doc_id = doc_url.split("/")[-1]
    cmd = f"LARK_CLI_NO_PROXY=1 npx lark-cli docs +fetch --api-version v1 --doc '{doc_id}' --scope full"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    content = result.stdout
    
    # 简单转换：飞书富文本 -> HTML
    html = content
    html = re.sub(r'<doc>', '<div>', html)
    html = re.sub(r'</doc>', '</div>', html)
    html = re.sub(r'<section>', '<div style="margin-bottom:20px;">', html)
    html = re.sub(r'</section>', '</div>', html)
    
    return html

def extract_title(html):
    """从 HTML 提取标题"""
    m = re.search(r'<h[12][^>]*>(.*?)</h[12]>', html)
    return m.group(1) if m else "RWA 政策分析"

def publish_to_wordpress(title, content, excerpt=""):
    """发布文章到 WordPress"""
    post_data = {
        "title": title,
        "content": content,
        "status": "publish",
        "excerpt": excerpt,
        "categories": [1]
    }
    
    # 写入临时文件
    tmp_file = "/tmp/wp_post_latest.json"
    with open(tmp_file, 'w') as f:
        json.dump(post_data, f, ensure_ascii=False)
    
    # 发布
    cmd = f"""curl -sk -u "{WP_USER}:{WP_PASS}" \
        -H "Content-Type: application/json; charset=UTF-8" \
        -d @{tmp_file} \
        "{WP_URL}/posts\""""
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    try:
        resp = json.loads(result.stdout)
        post_id = resp.get('id')
        link = resp.get('link', '')
        return True, f"发布成功！文章链接：{link}"
    except:
        return False, f"发布失败：{result.stdout[:200]}"

def main():
    """主流程：检查用户回复并自动发布"""
    user_open_id = "ou_3cadaa20ce7e2a1e22cce9eabbd89346"
    
    print("=== RWA 自动发布监听 ===")
    print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 获取最新消息
    print("检查飞书消息...")
    msg_data = get_latest_feishu_message(user_open_id)
    
    if not is_approved(msg_data):
        print("未检测到'通过'指令，退出。")
        return
    
    print("检测到'通过'指令！开始发布流程...")
    
    # 找到最新的 RWA 文档
    print("查找最新 RWA 文档...")
    doc_info = find_latest_rwa_doc()
    doc_url = re.search(r'https://my\.feishu\.cn/docx/[A-Za-z0-9]+', doc_info)
    
    if not doc_url:
        print("未找到最近的 RWA 文档，请手动指定。")
        return
    
    doc_url = doc_url.group(0)
    print(f"找到文档：{doc_url}")
    
    # 转换为 HTML
    print("转换文档内容...")
    html = convert_feishu_to_html(doc_url)
    title = extract_title(html)
    
    # 发布到 WordPress
    print(f"发布到 WordPress：{title}")
    success, msg = publish_to_wordpress(title, html)
    
    print(msg)
    
    # 发送飞书通知
    if success:
        notify_cmd = f"""LARK_CLI_NO_PROXY=1 npx lark-cli im +send \
            --receiver '{user_open_id}' \
            --msg-type text \
            --content '{msg}'"""
        subprocess.run(notify_cmd, shell=True)
    
    print("\n=== 完成 ===")

if __name__ == "__main__":
    main()
