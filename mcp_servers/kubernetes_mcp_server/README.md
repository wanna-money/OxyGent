# Kubernetes MCP 服务器

## 概述

Kubernetes MCP 服务器为 OxyGent 提供完整的 Kubernetes 集群管理功能，支持配置管理、核心资源操作和 Helm 模板化部署。

## 快速开始

### 1. 安装依赖

```bash
pip install -r mcp_servers/kubernetes_mcp_server/requirements.txt
```

### 2. 设置环境变量

注： 无K8S环境时，可以通过k8s `kind`在本地快速启动: https://kind.sigs.k8s.io/

```bash
# 备份本地环境变量
cp .env.example .env.example.bak

# 使用本mcp的环境变量文件
cp mcp_servers/kubernetes_mcp_server/.env.example.example .env.example
```

### 3. 基础使用

```bash

# 启动服务器 (stdio 模式)
python -m mcp_servers.kubernetes_mcp_server.server --transport stdio

# 在 OxyGent 中使用
python mcp_servers/kubernetes_mcp_server/kubernetes_demo.py
```

## 功能特性

### 🔧 配置工具集 (config)
- 查看 kubeconfig 配置和上下文
- 列出所有可用的集群上下文
- 切换当前上下文

### 🚀 核心工具集 (core)
- **Pods**: 列出、查看、获取日志、执行命令
- **Nodes**: 查看节点状态和资源使用
- **Namespaces**: 管理命名空间
- **Resources**: 通用资源操作
- **Events**: 查看集群事件

### ⚙️ Helm 工具集 (helm)
- 使用 Jinja2 模板渲染 Helm 风格配置
- 部署和卸载应用
- 无需 Helm 二进制依赖

## 使用示例

### 基础集群管理
```python
# 完整功能示例
python examples/mcp_tools/kubernetes_demo.py
```


## 配置选项

### 环境变量
- `K8S_MCP_TRANSPORT`: 传输模式 (stdio/sse/streamable-http)
- `K8S_MCP_TOOLSETS`: 启用的工具集 (config,core,helm)
- `K8S_MCP_READ_ONLY`: 只读模式
- `K8S_MCP_DISABLE_DESTRUCTIVE`: 禁用破坏性操作
- `KUBECONFIG`: kubeconfig 文件路径

### 命令行参数
```bash
python -m mcp_servers.kubernetes_mcp_server.server \
  --transport stdio \
  --toolsets config,core,helm \
  --read-only \
  --disable-destructive
```

## 安全模式

### 只读模式
```bash
--read-only
```
- 禁用所有写操作
- 仅支持查看和监控
- 适合生产环境

### 禁用破坏性操作
```bash
--disable-destructive
```
- 保留创建和更新
- 禁用删除操作
- 适合测试环境

