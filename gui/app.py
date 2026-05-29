# -*- coding: utf-8 -*-
"""PDF 智能工具箱 — 傻瓜式 AI 界面"""
import sys, os, threading, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from core.ai_agent import PdfAIAgent, get_api_key, load_config, save_config, get_model, get_api_url
from core.pdf_ops import PdfOps

# ─── 主题 ───
COLOR_BG = "#F5F5F5"
COLOR_PRIMARY = "#C0392B"  # PDF 红
COLOR_PRIMARY_DARK = "#A93226"
COLOR_WHITE = "#FFFFFF"
COLOR_USER_MSG = "#FDEDEC"
COLOR_AI_MSG = "#FFFFFF"
COLOR_WARN = "#FFF3E0"
FONT = ("微软雅黑", 10)
FONT_TITLE = ("微软雅黑", 18, "bold")
FONT_CHAT = ("微软雅黑", 10)


class PdfSmartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📄 PDF 智能工具箱 — 说人话操作 PDF")
        self.root.geometry("850x680")
        self.root.minsize(700, 550)
        self.root.configure(bg=COLOR_BG)

        self.filepath = ""
        self.ai = PdfAIAgent()
        self._build_ui()
        self._check_api_key()

    def _build_ui(self):
        # 顶部标题栏
        header = tk.Frame(self.root, bg=COLOR_PRIMARY, height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="📄 PDF 智能工具箱", font=FONT_TITLE,
                 bg=COLOR_PRIMARY, fg=COLOR_WHITE).pack(side="left", padx=20, pady=10)

        tk.Button(header, text="⚙️", font=("微软雅黑", 14),
                  bg=COLOR_PRIMARY, fg=COLOR_WHITE, bd=0,
                  cursor="hand2", command=self._show_settings).pack(side="right", padx=15)

        # 文件选择栏
        file_frame = tk.Frame(self.root, bg=COLOR_BG, height=40)
        file_frame.pack(fill="x", padx=15, pady=(10, 0))
        file_frame.pack_propagate(False)

        self.btn_file = tk.Button(file_frame, text="📁 选择 PDF 文件",
                                  font=("微软雅黑", 10, "bold"),
                                  bg=COLOR_WHITE, fg="#333", bd=1,
                                  relief="solid", cursor="hand2",
                                  command=self._select_file)
        self.btn_file.pack(side="left")

        self.file_label = tk.Label(file_frame, text="未选择文件（不选也能聊）",
                                   font=FONT, bg=COLOR_BG, fg="#888")
        self.file_label.pack(side="left", padx=10)

        # 聊天区域
        chat_frame = tk.Frame(self.root, bg=COLOR_WHITE, bd=1, relief="solid")
        chat_frame.pack(fill="both", expand=True, padx=15, pady=(8, 5))

        self.chat_canvas = tk.Canvas(chat_frame, bg=COLOR_WHITE, bd=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(chat_frame, orient="vertical", command=self.chat_canvas.yview)
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.chat_canvas.pack(side="left", fill="both", expand=True)

        self.chat_container = tk.Frame(self.chat_canvas, bg=COLOR_WHITE)
        self.chat_window = self.chat_canvas.create_window(
            (0, 0), window=self.chat_container, anchor="nw",
            width=self.chat_canvas.winfo_width())
        self.chat_container.bind("<Configure>", self._on_chat_resize)
        self.chat_canvas.bind("<Configure>", self._on_canvas_resize)

        # 快捷操作栏
        input_frame = tk.Frame(self.root, bg=COLOR_BG, height=60)
        input_frame.pack(fill="x", padx=15, pady=(0, 12))
        input_frame.pack_propagate(False)

        quick_frame = tk.Frame(input_frame, bg=COLOR_BG)
        quick_frame.pack(side="top", fill="x", pady=(0, 5))

        quick_btns = [
            ("📄 信息", "这个 PDF 有多少页"),
            ("🔗 合并", "帮我选几个 PDF 合并"),
            ("✂️ 拆分", "每页拆成一个文件"),
            ("💧 水印", "加上「机密」水印"),
            ("🔢 页码", "加页码"),
            ("📝 转 Word", "转成 Word"),
        ]
        for text, hint in quick_btns:
            btn = tk.Button(quick_frame, text=text, font=("微软雅黑", 9),
                            bg=COLOR_WHITE, fg="#555", bd=1,
                            relief="solid", cursor="hand2",
                            command=lambda h=hint: self._quick_action(h))
            btn.pack(side="left", padx=(0, 5))

        # 输入框
        input_row = tk.Frame(input_frame, bg=COLOR_BG)
        input_row.pack(side="bottom", fill="x")

        self.entry = tk.Entry(input_row, font=FONT_CHAT, bd=1,
                              relief="solid", bg=COLOR_WHITE)
        self.entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.entry.bind("<Return>", lambda e: self._send())
        self.entry.focus()

        self.btn_send = tk.Button(input_row, text="发送 💬",
                                  font=("微软雅黑", 10, "bold"),
                                  bg=COLOR_PRIMARY, fg=COLOR_WHITE,
                                  bd=0, cursor="hand2", padx=15,
                                  command=self._send)
        self.btn_send.pack(side="right", padx=(8, 0))

        # 状态栏
        self.status_bar = tk.Label(self.root, text="就绪 ✅",
                                   font=("微软雅黑", 9),
                                   bg=COLOR_BG, fg="#888", anchor="w")
        self.status_bar.pack(fill="x", padx=15, pady=(0, 5))

        # 欢迎消息
        self._add_ai("👋 你好！我是 PDF 智能助手。\n\n"
                     "你可以这样跟我说：\n"
                     "• 「这个 PDF 有多少页？」\n"
                     "• 「把每页拆成单独的文件」\n"
                     "• 「加上「机密」水印」\n"
                     "• 「转成 Word 文档」\n"
                     "• 「合并这几个 PDF」\n\n"
                     "先点上面 📁 选个 PDF 文件，或者直接开聊！")

    # ─── 消息渲染 ───

    def _add_user(self, text):
        frame = tk.Frame(self.chat_container, bg=COLOR_WHITE)
        frame.pack(fill="x", padx=10, pady=(5, 0))
        tk.Label(frame, text="🧑 你", font=("微软雅黑", 9, "bold"),
                 bg=COLOR_WHITE, fg="#333").pack(anchor="e")
        bubble = tk.Frame(frame, bg=COLOR_USER_MSG)
        bubble.pack(anchor="e", pady=(2, 0))
        tk.Label(bubble, text=text, font=FONT_CHAT, bg=COLOR_USER_MSG,
                 fg="#333", wraplength=500, justify="left",
                 padx=14, pady=8).pack()

    def _add_ai(self, text):
        frame = tk.Frame(self.chat_container, bg=COLOR_WHITE)
        frame.pack(fill="x", padx=10, pady=(5, 0))
        tk.Label(frame, text="🤖 AI 助手", font=("微软雅黑", 9, "bold"),
                 bg=COLOR_WHITE, fg=COLOR_PRIMARY).pack(anchor="w")
        bubble = tk.Frame(frame, bg=COLOR_AI_MSG, bd=1, relief="solid",
                          highlightbackground="#E0E0E0", highlightthickness=1)
        bubble.pack(anchor="w", pady=(2, 0))
        tk.Label(bubble, text=text, font=FONT_CHAT, bg=COLOR_AI_MSG,
                 fg="#333", wraplength=520, justify="left",
                 padx=14, pady=8).pack()
        self.root.after(50, self._scroll_bottom)

    def _add_sys(self, text):
        frame = tk.Frame(self.chat_container, bg=COLOR_WHITE)
        frame.pack(fill="x", padx=10, pady=(2, 0))
        tk.Label(frame, text=text, font=("微软雅黑", 9),
                 bg=COLOR_WARN, fg="#E65100",
                 wraplength=600, padx=10, pady=4).pack(anchor="center")

    def _scroll_bottom(self):
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def _on_chat_resize(self, e):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

    def _on_canvas_resize(self, e):
        self.chat_canvas.itemconfig(self.chat_window, width=e.width - 4)

    # ─── 交互 ───

    def _select_file(self):
        fp = filedialog.askopenfilename(
            title="选择 PDF 文件",
            filetypes=[("PDF 文件", "*.pdf"), ("所有文件", "*.*")])
        if fp:
            self.filepath = fp
            name = Path(fp).name
            self.file_label.config(text=f"已选择: {name}", fg="#333")
            self._add_sys(f"📎 已加载: {name}")

    def _quick_action(self, hint):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, hint)
        self._send()

    def _send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._add_user(text)
        self.btn_send.config(state="disabled", text="思考中...")
        self.status_bar.config(text="🤔 AI 思考中...")
        threading.Thread(target=self._process, args=(text,), daemon=True).start()

    def _process(self, text):
        try:
            ctx = ""
            if self.filepath:
                info = PdfOps.get_info(self.filepath)
                ctx = f"当前PDF：{Path(self.filepath).name}\n"
                for k, v in info.items():
                    ctx += f"{k}：{v}\n"
            reply = self.ai.chat(text, ctx)
            self.root.after(0, self._show_reply, reply)
        except Exception as e:
            self.root.after(0, self._show_reply, f"❌ 出错了：{e}")

    def _show_reply(self, reply):
        self._add_ai(reply)
        self.btn_send.config(state="normal", text="发送 💬")
        self.status_bar.config(text="就绪 ✅")

    # ─── 设置 ───

    def _check_api_key(self):
        if not get_api_key():
            self.root.after(500, self._show_settings)

    def _show_settings(self):
        """显示设置窗口"""
        win = tk.Toplevel(self.root)
        win.title("设置")
        win.geometry("480x300")
        win.resizable(False, False)
        win.configure(bg=COLOR_WHITE)
        win.transient(self.root)
        win.grab_set()

        key_var = tk.StringVar(value=get_api_key())
        model_var = tk.StringVar(value=get_model() or "deepseek-v4-flash")
        url_var = tk.StringVar(value=get_api_url())

        def save():
            config = load_config()
            config["api_key"] = key_var.get().strip()
            config["model"] = model_var.get().strip() or "deepseek-v4-flash"
            config["api_url"] = url_var.get().strip() or DEFAULT_API_URL
            save_config(config)
            self.ai._init_client()
            self._add_sys("✅ 设置已保存")
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", save)

        tk.Label(win, text="⚙️ 设置", font=FONT_TITLE,
                 bg=COLOR_WHITE, fg="#333").pack(pady=(15, 5))
        tk.Label(win, text="配置 API Key 后才能使用智能对话",
                 font=("微软雅黑", 9), bg=COLOR_WHITE, fg="#888").pack()

        tk.Label(win, text="API Key（DeepSeek / OpenAI）", font=FONT,
                 bg=COLOR_WHITE, fg="#333", anchor="w").pack(fill="x", padx=25, pady=(10, 2))
        tk.Entry(win, textvariable=key_var, font=FONT_CHAT,
                 bd=1, relief="solid", show="*").pack(padx=25, ipady=4, fill="x")

        tk.Label(win, text="模型", font=FONT,
                 bg=COLOR_WHITE, fg="#333", anchor="w").pack(fill="x", padx=25, pady=(8, 2))
        tk.Entry(win, textvariable=model_var, font=FONT_CHAT,
                 bd=1, relief="solid").pack(padx=25, ipady=4, fill="x")

        tk.Label(win, text="API 地址", font=FONT,
                 bg=COLOR_WHITE, fg="#333", anchor="w").pack(fill="x", padx=25, pady=(8, 2))
        tk.Entry(win, textvariable=url_var, font=FONT_CHAT,
                 bd=1, relief="solid").pack(padx=25, ipady=4, fill="x")

        tk.Button(win, text="💾 保存", font=("微软雅黑", 12, "bold"),
                  bg=COLOR_PRIMARY, fg=COLOR_WHITE, bd=0,
                  cursor="hand2", padx=30, pady=6,
                  command=save).pack(pady=(15, 0))


def main():
    root = tk.Tk()
    PdfSmartApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
