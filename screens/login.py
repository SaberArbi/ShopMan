"""Modal login dialog with language selector."""
import tkinter as tk
from tkinter import messagebox, ttk

from utils import auth, i18n
from utils.i18n import t


class LoginDialog:
    def __init__(self, root):
        self.root = root
        self.user = None

        self.top = tk.Toplevel(root)
        self.top.resizable(False, False)
        self.top.configure(bg="#f0f0f0")
        self._build()

        self.top.bind("<Return>", lambda e: self.login())
        self.top.bind("<KP_Enter>", lambda e: self.login())
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)

        self.top.update_idletasks()
        self.top.deiconify()
        self.top.lift()
        try:
            self.top.attributes("-topmost", True)
            self.top.after(250, lambda: self.top.attributes("-topmost", False))
        except tk.TclError:
            pass
        self.username.focus_set()
        try:
            self.top.grab_set()
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    def _build(self):
        for w in self.top.winfo_children():
            w.destroy()

        self.top.title(t("login.title"))
        self.top.geometry("440x360")

        tk.Label(self.top, text=t("app.title"),
                 font=i18n.ui_font(16, "bold"),
                 bg="#f0f0f0", fg="#2c3e50").pack(pady=(18, 2))
        tk.Label(self.top, text=t("login.subtitle"),
                 font=i18n.ui_font(9),
                 bg="#f0f0f0", fg="#7f8c8d").pack(pady=(0, 12))

        self._build_lang_selector()
        self._build_credentials()

        tk.Button(self.top, text=t("login.connect"),
                  bg="#27ae60", fg="white",
                  font=i18n.ui_font(10, "bold"), width=15,
                  command=self.login).pack(pady=18)

    def _build_lang_selector(self):
        frame = tk.Frame(self.top, bg="#f0f0f0")
        frame.pack(pady=(0, 12))
        tk.Label(frame, text=t("login.language"),
                 bg="#f0f0f0", fg="#2c3e50",
                 font=i18n.ui_font(10)).pack(side=i18n.side_start(),
                                             padx=(0, 6))

        self._lang_codes = list(i18n.LANGUAGES.keys())
        names = [i18n.LANGUAGES[c] for c in self._lang_codes]
        current = i18n.get_language()
        self.lang_var = tk.StringVar(
            value=i18n.LANGUAGES.get(current, names[0]))

        self.lang_combo = ttk.Combobox(
            frame, textvariable=self.lang_var, values=names,
            state="readonly", width=14,
            font=i18n.ui_font(10), justify=i18n.justify_text(),
        )
        self.lang_combo.pack(side=i18n.side_start())
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_language_change)

    def _build_credentials(self):
        form = tk.Frame(self.top, bg="#f0f0f0")
        form.pack(pady=6)

        rtl = i18n.is_rtl()
        label_col, entry_col = (1, 0) if rtl else (0, 1)
        label_sticky = i18n.anchor_start()

        tk.Label(form, text=t("login.username"), bg="#f0f0f0",
                 font=i18n.ui_font(10)
                 ).grid(row=0, column=label_col, sticky=label_sticky,
                        padx=6, pady=6)
        self.username = tk.Entry(form, width=22, font=i18n.ui_font(10),
                                 justify=i18n.justify_text())
        self.username.grid(row=0, column=entry_col, padx=6, pady=6)

        tk.Label(form, text=t("login.password"), bg="#f0f0f0",
                 font=i18n.ui_font(10)
                 ).grid(row=1, column=label_col, sticky=label_sticky,
                        padx=6, pady=6)
        self.password = tk.Entry(form, width=22, show="*",
                                 font=i18n.ui_font(10),
                                 justify=i18n.justify_text())
        self.password.grid(row=1, column=entry_col, padx=6, pady=6)

    # ------------------------------------------------------------------
    def _on_language_change(self, event=None):
        for code, name in i18n.LANGUAGES.items():
            if name == self.lang_var.get():
                i18n.set_language(code)
                break
        old_user = self.username.get() if hasattr(self, "username") else ""
        old_pwd = self.password.get() if hasattr(self, "password") else ""
        self._build()
        if old_user:
            self.username.insert(0, old_user)
        if old_pwd:
            self.password.insert(0, old_pwd)
        self.username.focus_set()

    def login(self):
        username = self.username.get().strip()
        password = self.password.get()
        if not username or not password:
            messagebox.showerror(t("msg.error"), t("login.error_empty"),
                                 parent=self.top)
            return
        user = auth.authenticate(username, password)
        if not user:
            messagebox.showerror(t("msg.error"), t("login.error_invalid"),
                                 parent=self.top)
            self.password.delete(0, tk.END)
            return
        self.user = user
        self._close()

    def cancel(self):
        self.user = None
        self._close()

    def _close(self):
        try:
            self.top.grab_release()
        except tk.TclError:
            pass
        self.top.destroy()

    def show(self):
        self.root.wait_window(self.top)
        return self.user