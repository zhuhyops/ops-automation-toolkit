# 企业级 Linux 运维自动化与 DevSecOps 工具集
> **Author:** zhuhy-ops
> **Role:** DevSecOps / Cloud-Native Operation Engineer

## 🚀 项目架构简介 (Architecture Overview)
本项目脱胎于真实的生产环境运维痛点，旨在通过标准化的 Shell 与 Python 脚本，以及云原生编排清单，解决中小企业在系统初始化、日志审计及高可用集群交付中的效率与安全问题。

## 📂 核心武器库 (Toolkit Modules)

### 1. [系统安全与初始化加固](./linux-init-security-harden/)
* 涵盖 CentOS/Ubuntu 生产环境下的标准化交付。
* **核心亮点:** 包含 TCP/IP 状态回收优化（缓解高并发 `TIME_WAIT`）及 SSH 防爆破基线加固。

### 2. [日志监控与预警机器人](./python-log-monitor-bot/)
* 针对 Nginx/Apache 访问日志的轻量级 DevSecOps 审计组件。
* **核心亮点:** 基于 Python 正则预编译与高频聚合算法，实现针对 CC 攻击、SQLi/XSS 等恶意 Payload 的秒级提取，并联动 Webhook 触发应急响应。

### 3. [云原生轻量级编排架构](./k3s-container-stack/)
* 针对资源受限环境下的 Docker 与 K3s 容器化交付清单。
* **核心亮点:** 严格定义 Pod 资源软硬件限制 (`limits/requests`) 与 `LivenessProbe` 探针，防止 OOM 溢出，保障核心业务的秒级自愈。

## 🛠 技术栈 (Tech Stack)
* **OS & Network:** Linux (CentOS/Ubuntu), LVM, iptables/firewalld, Nginx
* **Scripting:** Shell (Bash), Python (Requests, re, collections)
* **Cloud-Native:** Docker, K3s, YAML, docker-compose
