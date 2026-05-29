# -*- coding: utf-8 -*-
"""AI 驱动层 - 自然语言操作 PDF"""
import os
import json
import fitz
from openai import OpenAI
from pathlib import Path

DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_API_URL = "https://api.deepseek.com/v1"
CONFIG_FILE = Path(__file__).parent.parent / "config" / "settings.json"


def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except:
            pass
    return {}


def save_config(config: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")


def get_api_key() -> str:
    config = load_config()
    return config.get("api_key", "") or os.environ.get("DEEPSEEK_API_KEY", "")


def get_model() -> str:
    config = load_config()
    return config.get("model", DEFAULT_MODEL)


def get_api_url() -> str:
    config = load_config()
    return config.get("api_url", DEFAULT_API_URL)


SYSTEM_PROMPT = """你是一个PDF智能助手。用户会用自然语言描述需求，你需要：

## 你的能力
1. **PDF信息查询** — 回答关于PDF的问题（页数、大小、内容等）
2. **PDF操作** — 合并、拆分、提取文本/图片、转Word/图片
3. **PDF美化** — 加水印、加页码、加密、解密、旋转、压缩
4. **批量处理** — 对多个PDF执行相同操作

## 输出规则
- 如果用户问问题 → 直接回答，简洁中文
- 如果用户要操作 → 先说明要做什么，然后执行
- 操作完成后告诉用户结果（文件保存在哪）

## 重要
- 输出要口语化，让不懂技术的人也能看懂
- 如果用户没说清楚，友好追问
"""


class PdfAIAgent:
    """PDF AI 智能体"""

    def __init__(self):
        self.client = None
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self._init_client()

    def _init_client(self):
        api_key = get_api_key()
        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=get_api_url())

    def is_ready(self) -> bool:
        return self.client is not None and bool(get_api_key())

    def set_api_key(self, key: str):
        config = load_config()
        config["api_key"] = key
        save_config(config)
        self._init_client()

    def set_model(self, model: str):
        config = load_config()
        config["model"] = model
        save_config(config)

    def chat(self, user_input: str, data_context: str = "") -> str:
        if not self.is_ready():
            return "⚠️ 请先在设置中配置 API Key（DeepSeek / OpenAI）"

        msgs = list(self.messages)
        if data_context:
            msgs.append({"role": "user", "content": f"当前PDF信息：\n{data_context}"})
        msgs.append({"role": "user", "content": user_input})

        try:
            resp = self.client.chat.completions.create(
                model=get_model(),
                messages=msgs,
                temperature=0.3,
                max_tokens=4096,
                stream=False,
            )
            reply = resp.choices[0].message.content
            self.messages.append({"role": "user", "content": user_input})
            self.messages.append({"role": "assistant", "content": reply})
            if len(self.messages) > 20:
                self.messages = [self.messages[0]] + self.messages[-18:]
            return reply
        except Exception as e:
            return f"❌ 调用 AI 失败：{e}\n\n请检查 API Key 和网络连接。"

    def analyze_file(self, filepath: str, question: str) -> str:
        """分析 PDF 文件"""
        try:
            from core.pdf_ops import PdfOps
            info = PdfOps.get_info(filepath)
            text_preview = PdfOps.extract_text(filepath)[:800]

            ctx = f"文件：{Path(filepath).name}\n"
            for k, v in info.items():
                ctx += f"{k}：{v}\n"
            ctx += f"\n内容预览：\n{text_preview}"

            return self.chat(question, data_context=ctx)
        except Exception as e:
            return f"❌ 读取文件失败：{e}"

    def reset_chat(self):
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
