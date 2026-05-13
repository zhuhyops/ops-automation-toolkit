#!/bin/bash
# ==============================================================================
# 脚本名称: linux_server_init.sh
# 适用系统: CentOS 7+ / Ubuntu 20.04+
# 核心功能: 基础环境初始化、SSH 安全加固、内核参数调优 (防 DDoS / 高并发优化)
# ==============================================================================

# 定义日志颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' 

info() { echo -e "${GREEN}[INFO] $1 ${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1 ${NC}"; }
error() { echo -e "${RED}[ERROR] $1 ${NC}"; exit 1; }

# 1. 权限检查
if [ "$EUID" -ne 0 ]; then
    error "请使用 root 权限运行此脚本！"
fi

# 2. 修改时区与时间同步
info "正在配置时区 (Asia/Shanghai)..."
timedatectl set-timezone Asia/Shanghai
# 安装并启动 chrony (新一代时间同步工具)
if command -v yum >/dev/null 2>&1; then
    yum install -y chrony > /dev/null 2>&1 && systemctl enable --now chronyd
elif command -v apt-get >/dev/null 2>&1; then
    apt-get update > /dev/null 2>&1 && apt-get install -y chrony > /dev/null 2>&1 && systemctl enable --now chrony
fi

# 3. SSH 安全加固
info "正在进行 SSH 安全加固 (禁用 DNS 反解, 强化配置)..."
[ -f /etc/ssh/sshd_config ] && cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sed -i 's/#UseDNS yes/UseDNS no/g' /etc/ssh/sshd_config
sed -i 's/UseDNS yes/UseDNS no/g' /etc/ssh/sshd_config
sed -i 's/#PermitEmptyPasswords no/PermitEmptyPasswords no/g' /etc/ssh/sshd_config
systemctl restart sshd || systemctl restart ssh

# 4. 内核参数调优 (核心：解决 TIME_WAIT 堆积与防 SYN 攻击)
info "正在优化系统内核参数 (sysctl)..."
cp /etc/sysctl.conf /etc/sysctl.conf.bak
cat >> /etc/sysctl.conf << EOF
# ------------------ 自动化调优参数 ------------------
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_keepalive_time = 600
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 8192
# ----------------------------------------------------
EOF
sysctl -p > /dev/null 2>&1

info "=========================================="
info "服务器初始化与安全加固已完成！"
info "=========================================="
