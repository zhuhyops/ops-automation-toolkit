#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : log_analyzer.py
@Desc    : Nginx/Apache 访问日志异常检测与 Webhook 告警脚本
@Author  : zhuhy-ops
@Role    : DevSecOps 自动化监控组件
"""

import re
import json
import time
import requests
from collections import Counter

# ================= 生产环境配置区 =================
LOG_FILE_PATH = "/var/log/nginx/access.log"
THRESHOLD_REQUESTS = 100 # 触发高频预警的单 IP 访问次数
WEBHOOK_URL = "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN_HERE" # 替换为真实企业微信/钉钉/飞书 Webhook

# 简易 WAF 规则库 (正则特征匹配)
MALICIOUS_PAYLOADS = [
    r"union.*select",   # SQL 注入特征
    r"<script.*?>",     # XSS 攻击特征
    r"/etc/passwd",     # 任意文件读取特征
    r"\.env"            # 敏感文件扫描
]
# ==================================================

def parse_logs():
    """解析日志文件，提取请求 IP 与恶意 Payload"""
    ip_list = []
    malicious_requests = []
    
    # 核心优化：提前编译正则表达式，极大提升大文件循环匹配的性能
    ip_pattern = re.compile(r'^(?P<ip>\d{1,3}(\.\d{1,3}){3})')
    payload_patterns = [re.compile(p, re.IGNORECASE) for p in MALICIOUS_PAYLOADS]

    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                ip_match = ip_pattern.search(line)
                if ip_match:
                    ip = ip_match.group('ip')
                    ip_list.append(ip)
                
                # 遍历匹配高危特征
                for pattern in payload_patterns:
                    if pattern.search(line):
                        malicious_requests.append({
                            "ip": ip if ip_match else "Unknown",
                            "payload": line.strip()
                        })
                        break # 匹配到一个特征即跳出，防止单行日志重复记录
                        
        return ip_list, malicious_requests
    except FileNotFoundError:
        print(f"[Error] 日志文件不存在，请检查路径: {LOG_FILE_PATH}")
        return [], []

def send_webhook_alert(title, text):
    """通过 Webhook 将异常信息推送到企业 IM 群组"""
    headers = {'Content-Type': 'application/json'}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": f"## {title} \n\n {text} \n\n > **预警时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }
    try:
        response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(data), timeout=5)
        if response.status_code == 200:
            print("[Info] 告警推送成功，请查看 IM 软件！")
        else:
            print(f"[Error] 告警推送失败，API 状态码: {response.status_code}")
    except Exception as e:
        print(f"[Error] 网络请求异常: {e}")

def main():
    print("[Info] 启动安全日志自动化审计流程...")
    ip_list, malicious_requests = parse_logs()
    
    if not ip_list:
        return

    # 1. 业务逻辑：统计高频访问 IP (识别 CC 攻击或暴力破解)
    ip_counts = Counter(ip_list)
    abnormal_ips = {ip: count for ip, count in ip_counts.items() if count >= THRESHOLD_REQUESTS}
    
    alert_msg = ""
    
    if abnormal_ips:
        alert_msg += "### 🔴 高频异常流量 (疑似 CC/爆破)\n"
        for ip, count in abnormal_ips.items():
            alert_msg += f"- IP: **{ip}** ，请求次数: **{count}** (建议联动 iptables 封堵)\n"
            
    if malicious_requests:
        alert_msg += "\n### ☠️ 高危攻击特征 (疑似 Web 渗透)\n"
        # 截取前 5 条发送，防止单次 Payload 过长导致推流失败
        for req in malicious_requests[:5]:
            alert_msg += f"- 攻击源: `{req['ip']}` | 触发动作: `{req['payload'][:60]}...`\n"
            
    # 2. 触发推送机制
    if alert_msg:
        send_webhook_alert("【安全运营】生产环境入侵告警", alert_msg)
    else:
        print("[Info] 审计完毕，当前业务环境运行平稳。")

if __name__ == "__main__":
    main()
