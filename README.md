# 📦 VideoAudit-Pipeline

基于 Python + Tkinter + FFprobe 构建的视频自动化合规审计与数据处理流水线系统。

---

## 🧠 项目简介

VideoAudit-Pipeline 是一款用于视频文件自动化分析与审计的工具，支持视频抽样检测、结构化结果输出以及多通道数据分发。

适用于视频数据批量检测、合规审计、文件质量校验等场景。

---

## ⚙️ 核心功能

- 📌 视频时序抽样分析（基于 FFprobe）
- 📊 自动生成结构化审计报告（CSV / JSON）
- 📁 本地自动生成 report 输出目录
- 🌐 支持审计结果 TCP 上传至远程服务器
- 🖥️ Tkinter 图形化界面（轻量级操作）
- 📦 Windows x64 一键可执行版本（exe）

---

## 📁 输出结构说明

程序运行后，在被测试视频文件所在目录生成如下结构：

```text
videoaudit_demo_dataset/
├── report/
│   ├── audit_report.csv
│   └── audit_report.json
```

---

## 🚀 运行方式

### 方法一：直接运行 exe（推荐）

下载 Release 包后直接运行：`p-audit.exe`

### 方法二：源码运行

```bash
# 1. 安装多媒体核心依赖
pip install -r requirements.txt

# 2. 启动自动化审计流水线
python VideoAudit-Pipeline.py
```
🧩 打包方案

若需要自行重构并重新编译二进制沙盒，请在英文终端环境执行以下 PyInstaller 构建指令：
```pyinstaller -F -w --add-binary "ffprobe.exe;." VideoAudit-Pipeline.py```

⚠️ 说明

FFprobe 依赖通过打包方式内置

项目运行无需额外环境配置（Windows x64）

📦 Release

提供 Windows x64 可执行版本（ZIP 分发）：

v1.0.0 正式发布
