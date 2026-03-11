"""
Devta AI System - Chat UI
==========================
Dark-mode Tkinter chat window with:
- Scrollable message history (user + Devta bubbles)
- Text input box for typing at bottom (always visible)
- Microphone status indicator
- System tray icon (minimize to tray)
"""

import threading
import tkinter as tk
from tkinter import scrolledtext
import datetime
from config import UI_THEME


class DevtaUI:
    def __init__(self, on_user_message=None, on_close=None):
        self.on_user_message = on_user_message or (lambda t: None)
        self.on_close        = on_close        or (lambda: None)

        self.root = tk.Tk()
        self.root.title("✦ Devta — AI Assistant")
        self.root.geometry("560x760")
        self.root.minsize(420, 500)
        self.root.configure(bg=UI_THEME["bg"])
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)

        # Bring window to front on start
        self.root.lift()
        self.root.focus_force()

        self._build_ui()
        self._set_icon()

    # ──────────────────────────────────────────
    #  UI Construction
    # ──────────────────────────────────────────
    def _build_ui(self):
        T  = UI_THEME
        ff = T["font_family"]
        fs = T["font_size"]

        # ── Header bar ──────────────────────────
        header = tk.Frame(self.root, bg="#0a0a1a", pady=8)
        header.pack(fill=tk.X, side=tk.TOP)

        tk.Label(
            header, text="✦ DEVTA", bg="#0a0a1a",
            fg=T["accent"], font=(ff, 16, "bold"), padx=16
        ).pack(side=tk.LEFT)

        self.status_label = tk.Label(
            header, text="● Standby", bg="#0a0a1a",
            fg=T["muted"], font=(ff, 9)
        )
        self.status_label.pack(side=tk.RIGHT, padx=16)

        # ── Bottom input area (packed BEFORE chat so it stays at bottom) ──
        bottom = tk.Frame(self.root, bg="#0a0a1a")
        bottom.pack(fill=tk.X, side=tk.BOTTOM)

        # Mic status label
        mic_bar = tk.Frame(bottom, bg=UI_THEME["bg"])
        mic_bar.pack(fill=tk.X, padx=10, pady=(4, 0))

        self.mic_label = tk.Label(
            mic_bar,
            text="🎤 Mic: Always On  |  Say 'Hello Devta' to activate",
            bg=UI_THEME["bg"], fg=T["muted"], font=(ff, 8)
        )
        self.mic_label.pack(side=tk.LEFT)

        # Input row
        input_row = tk.Frame(bottom, bg="#0a0a1a", pady=8)
        input_row.pack(fill=tk.X, padx=10, pady=(2, 10))

        self.input_var = tk.StringVar()
        self.input_box = tk.Entry(
            input_row,
            textvariable=self.input_var,
            bg="#1e1e3a", fg=T["text"],
            insertbackground=T["accent"],
            font=(ff, fs),
            relief=tk.FLAT,
            bd=1,
            highlightthickness=1,
            highlightbackground="#3a3a5a",
            highlightcolor=T["accent"]
        )
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True,
                            ipady=10, padx=(6, 4))
        self.input_box.bind("<Return>", self._on_enter)
        self.input_box.bind("<FocusIn>",  lambda e: self.input_box.configure(bg="#232345", highlightbackground=T["accent"]))
        self.input_box.bind("<FocusOut>", lambda e: self.input_box.configure(bg="#1e1e3a", highlightbackground="#3a3a5a"))

        self.send_btn = tk.Button(
            input_row, text="Send ➤",
            bg=T["accent"], fg="white",
            activebackground="#9a7de0",
            font=(ff, fs, "bold"),
            relief=tk.FLAT, bd=0,
            padx=16, pady=8,
            cursor="hand2",
            command=self._on_enter
        )
        self.send_btn.pack(side=tk.RIGHT, padx=(4, 6))

        # ── Chat area (fills all remaining space) ──
        chat_frame = tk.Frame(self.root, bg=T["bg"])
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 0))

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            bg=T["chat_bg"], fg=T["text"],
            font=(ff, fs), wrap=tk.WORD,
            relief=tk.FLAT, borderwidth=0,
            state=tk.DISABLED, cursor="arrow",
            padx=10, pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Text tags for styling
        self.chat_display.tag_configure(
            "user", foreground="#7eb8f7",
            font=(ff, fs, "bold"), lmargin1=10, lmargin2=10
        )
        self.chat_display.tag_configure(
            "devta", foreground="#c4a8ff",
            font=(ff, fs, "bold"), lmargin1=10, lmargin2=10
        )
        self.chat_display.tag_configure(
            "message", foreground=T["text"],
            font=(ff, fs), lmargin1=22, lmargin2=22
        )
        self.chat_display.tag_configure(
            "timestamp", foreground=T["muted"],
            font=(ff, 8), lmargin1=22
        )
        self.chat_display.tag_configure(
            "system", foreground=T["muted"],
            font=(ff, 9, "italic"), lmargin1=10
        )

        # Welcome message
        self.add_devta_message(
            "Namaste! 🙏 Main Devta hoon — aapka personal AI assistant. "
            "Neeche type karo ya 'Hello Devta' bol ke mujhse baat karo!"
        )

        # Focus input box immediately
        self.root.after(200, self.input_box.focus_set)

    # ──────────────────────────────────────────
    #  Message Display
    # ──────────────────────────────────────────
    def add_user_message(self, text: str):
        self._append_message("👤 You", text, "user")

    def add_devta_message(self, text: str):
        self._append_message("✦ Devta", text, "devta")

    def add_system_message(self, text: str):
        self.root.after(0, self._write, f"  ⚙ {text}\n", "system")

    def _append_message(self, sender: str, text: str, tag: str):
        ts = datetime.datetime.now().strftime("%H:%M")

        def _write_all():
            self.chat_display.configure(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"\n{sender}\n", tag)
            self.chat_display.insert(tk.END, f"{text}\n", "message")
            self.chat_display.insert(tk.END, f"{ts}\n", "timestamp")
            self.chat_display.configure(state=tk.DISABLED)
            self.chat_display.see(tk.END)

        self.root.after(0, _write_all)

    def _write(self, text: str, tag: str = "message"):
        self.chat_display.configure(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text, tag)
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    # ──────────────────────────────────────────
    #  Status & Mic Indicator
    # ──────────────────────────────────────────
    def set_status(self, text: str, color: str = None):
        color = color or UI_THEME["muted"]
        self.root.after(0, lambda: self.status_label.configure(
            text=f"● {text}", fg=color))

    def set_listening(self, active: bool):
        if active:
            self.root.after(0, lambda: self.mic_label.configure(
                text="🎤 Listening... speak now!", fg="#7eb8f7"))
            self.set_status("Listening", "#7eb8f7")
        else:
            self.root.after(0, lambda: self.mic_label.configure(
                text="🎤 Mic: Always On  |  Say 'Hello Devta' to activate",
                fg=UI_THEME["muted"]))
            self.set_status("Standby", UI_THEME["muted"])

    def set_thinking(self, active: bool):
        if active:
            self.set_status("Thinking...", UI_THEME["accent"])
        else:
            self.set_status("Standby", UI_THEME["muted"])

    # ──────────────────────────────────────────
    #  Input Handling
    # ──────────────────────────────────────────
    def _on_enter(self, event=None):
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self.add_user_message(text)
        threading.Thread(
            target=self.on_user_message, args=(text,), daemon=True
        ).start()

    # ──────────────────────────────────────────
    #  Window / Tray
    # ──────────────────────────────────────────
    def _on_window_close(self):
        self.root.withdraw()
        self._try_tray()

    def _try_tray(self):
        try:
            import pystray
            from PIL import Image, ImageDraw

            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([8, 8, 56, 56], fill="#7c5cbf")
            draw.text((22, 18), "D", fill="white")

            def show_window(icon, item):
                icon.stop()
                self.root.after(0, self.root.deiconify)
                self.root.after(100, self.root.lift)

            def quit_app(icon, item):
                icon.stop()
                self.root.after(0, self._quit)

            menu = pystray.Menu(
                pystray.MenuItem("Open Devta", show_window, default=True),
                pystray.MenuItem("Quit", quit_app)
            )
            icon = pystray.Icon("Devta", img, "Devta AI", menu)
            threading.Thread(target=icon.run, daemon=True).start()
        except Exception:
            self._quit()

    def _quit(self):
        self.on_close()
        self.root.destroy()

    # ──────────────────────────────────────────
    #  Run
    # ──────────────────────────────────────────
    def run(self):
        """Start the Tkinter main loop (blocking — call from main thread)."""
        self.root.mainloop()

    def _set_icon(self):
        try:
            from PIL import Image, ImageDraw, ImageTk
            img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse([4, 4, 60, 60], fill="#7c5cbf")
            draw.text((20, 16), "D", fill="white")
            photo = ImageTk.PhotoImage(img)
            self.root.iconphoto(True, photo)
        except Exception:
            pass
