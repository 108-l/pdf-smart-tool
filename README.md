# 📄 PDF 智能工具箱

> **说人话操作 PDF。** 双击启动 → 打字聊天 → 出结果。

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🎯 这是什么？

一个 **会聊天的 PDF 工具**。不用学操作、不用查教程——

**打开软件，像跟人说话一样告诉它你要做什么，它自动搞定。**

```text
你： "把这个 PDF 每页拆成单独的文件"
AI： ✅ 已拆成 12 个文件，保存在同目录下

你： "加上「机密」水印"
AI： ✅ 水印已添加，生成新文件
```

---

## ✨ 功能

| 你说 | 它做 |
|------|------|
| "这个 PDF 有多少页？" | 显示页数、大小、作者等信息 |
| "每页拆成单独的文件" | 按页拆分 PDF |
| "合并这几个 PDF" | 多个 PDF 合成一个 |
| "转成 Word" | PDF → Word 文档 |
| "提取里面的图片" | 抽出所有图片 |
| "加上水印" | 添加文字水印（机密/草稿等） |
| "加页码" | 自动添加页码 |
| "加密" | 设置密码保护 |
| "压缩" | 减小文件体积 |

---

## 🚀 3 秒上手

```bash
1. 下载本项目 → 解压
2. 双击 → 启动GUI.bat（自动装依赖）
3. 输入 API Key → 开始聊天操作 PDF
```

### 获取 API Key

1. 访问 [DeepSeek 官网](https://platform.deepseek.com) → 注册 → 创建 API Key
2. 在软件设置中粘贴 Key → 保存

---

## 📁 项目结构

```
pdf-smart-tool/
├── 🚀 启动GUI.bat       # 双击启动
├── 📖 使用说明书.txt
├── 📚 README.md
├── 📄 LICENSE
├── 📦 requirements.txt
│
├── core/
│   ├── ai_agent.py      # 🤖 AI 智能对话引擎
│   └── pdf_ops.py       # 📄 PDF 核心操作
│
├── features/            # 预留扩展
├── gui/app.py           # 🖥️ 图形界面
└── config/settings.json # ⚙️ 配置文件
```

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.10+ | 运行环境 |
| PyMuPDF | PDF 解析引擎 |
| pypdf | 合并/拆分/加密 |
| pdf2docx | PDF → Word |
| reportlab | 生成水印/页码 |
| openai | AI 对话 |
| tkinter | 图形界面 |

---

## 📝 对比

| 对比项 | PDF 智能工具箱 | 传统 PDF 工具 |
|--------|---------------|-------------|
| 学习成本 | 0 — 会打字就行 | 高 — 要学操作 |
| 操作方式 | 自然语言聊天 | 菜单/按钮 |
| 处理速度 | AI 秒级 | 手动操作 |
| 水印/页码 | 一句话搞定 | 手动配置 |

---

## 📄 License

MIT License — 随便用、随便改、随便卖。

---

**⭐ 有用的话点个 Star！**
