"""Users — create, rename, activate/deactivate, change password."""
import tkinter as tk
from tkinter import messagebox, ttk

from app import theme
from screens.base import BaseScreen
from screens.widgets import build_topbar
from utils import auth, i18n
from utils.i18n import t


class UsersScreen(BaseScreen):
    topbar_color = theme.DARK

    def __init__(self, root, switch, user=None, logout=None):
        super().__init__(root, switch, user, logout=None)
        self.load_users()

    def build_topbar(self):
        start, end = [], []
        if auth.can(self.user, "sell"):
            start.append((t("nav.back_to_sales"), theme.DARK_LIGHT,
                          lambda: self.switch("sales")))
        if auth.can(self.user, "view_history"):
            start.append((t("nav.history"), theme.DARK_LIGHT,
                          lambda: self.switch("history")))
        if auth.can(self.user, "view_deleted_sales"):
            end.append((t("history.deleted_btn"), theme.RED_DARKER,
                        lambda: self.switch("deleted")))
        build_topbar(self.frame, color=self.topbar_color,
                     title_key="users.title",
                     buttons_start=start, buttons_end=end,
                     logout_callback=self.logout)

    def build_body(self):
        main = tk.Frame(self.frame, bg=theme.BG)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        form = tk.Frame(main, bg=theme.BG_CARD, relief="groove", bd=2,
                        width=340)
        form.pack(side=i18n.side_start(), fill="y", padx=(0, 10))
        form.pack_propagate(False)

        listing = tk.Frame(main, bg=theme.BG_CARD, relief="groove", bd=2)
        listing.pack(side=i18n.side_end(), fill="both", expand=True)

        self._build_form(form)
        self._build_listing(listing)

    # --- form -----------------------------------------------------------
    def _build_form(self, parent):
        tk.Label(parent, text=t("users.add_user"), bg=theme.BG_CARD,
                 fg=theme.FG, font=self.font(13, "bold")
                 ).pack(pady=(14, 8))

        self.entries = {}
        for label, key, show in (
            (t("users.username"), "username", None),
            (t("users.full_name"), "full_name", None),
            (t("users.password"), "password", "*"),
            (t("users.confirm"), "password2", "*"),
        ):
            row = tk.Frame(parent, bg=theme.BG_CARD)
            row.pack(fill="x", padx=10, pady=4)
            tk.Label(row, text=label, width=16, anchor=i18n.anchor_start(),
                     bg=theme.BG_CARD, fg=theme.FG,
                     font=self.font(10)).pack(side=i18n.side_start())
            e = tk.Entry(row, font=self.font(10), bg=theme.BG_INPUT,
                         fg=theme.FG, relief="solid", bd=1,
                         show=show if show else "",
                         justify=i18n.justify_text())
            e.pack(side=i18n.side_start(), fill="x", expand=True, ipady=2)
            self.entries[key] = e

        tk.Label(parent, text=t("users.role"), bg=theme.BG_CARD, fg=theme.FG,
                 font=self.font(10)
                 ).pack(anchor=i18n.anchor_start(), padx=10, pady=(8, 0))
        self.role_var = tk.StringVar(value="cashier")
        roles = tk.Frame(parent, bg=theme.BG_CARD)
        roles.pack(fill="x", padx=10, pady=2)
        for value, key in (("cashier", "users.role_cashier"),
                            ("owner", "users.role_owner")):
            tk.Radiobutton(roles, text=t(key), variable=self.role_var,
                           value=value, bg=theme.BG_CARD, fg=theme.FG,
                           activebackground=theme.BG_CARD,
                           selectcolor=theme.BG_CARD,
                           font=self.font(10)).pack(side=i18n.side_start())

        tk.Button(parent, text=t("users.create"), bg=theme.GREEN, fg="white",
                  font=self.font(10, "bold"), width=12, relief="flat",
                  command=self.create_user).pack(pady=18)

    # --- listing --------------------------------------------------------
    def _build_listing(self, parent):
        container = tk.Frame(parent, bg=theme.BG_CARD)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("id", "username", "full_name", "role", "active", "created")
        headings = [t("users.col_id"), t("users.col_username"),
                    t("users.col_full_name"), t("users.col_role"),
                    t("users.col_active"), t("users.col_created")]
        widths = [45, 140, 180, 100, 70, 140]
        self.tree = ttk.Treeview(container, columns=columns,
                                 show="headings", height=20)
        for col, hdr, w in zip(columns, headings, widths):
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=w,
                             anchor=(i18n.anchor_start()
                                     if col == "full_name" else "center"))
        v = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v.set)
        self.tree.pack(side=i18n.side_start(), fill="both", expand=True)
        v.pack(side=i18n.side_end(), fill="y")

        footer = tk.Frame(parent, bg=theme.BG_CARD)
        footer.pack(fill="x", padx=10, pady=(0, 10))
        for text_key, color, cmd in (
            ("users.rename", theme.PURPLE, self.rename_dialog),
            ("users.toggle_active", theme.ORANGE, self.toggle_active),
            ("users.change_password", theme.BLUE, self.change_password_dialog),
            ("users.delete", theme.RED, self.delete_selected),
        ):
            tk.Button(footer, text=t(text_key), bg=color, fg="white",
                      font=self.font(10, "bold"), relief="flat",
                      command=cmd).pack(side=i18n.side_start(), padx=3)
        tk.Label(footer, text=t("users.warn_owner"), bg=theme.BG_CARD,
                 fg=theme.ORANGE, font=self.font(9)
                 ).pack(side=i18n.side_end(), padx=5)

    # ------------------------------------------------------------------
    def _selected_user(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(t("msg.warning"), t("users.select_user"))
            return None
        return self.tree.item(sel[0])["values"]

    def create_user(self):
        username = self.entries["username"].get().strip()
        full_name = self.entries["full_name"].get().strip()
        password = self.entries["password"].get()
        password2 = self.entries["password2"].get()
        role = self.role_var.get()
        if not username or not password:
            messagebox.showwarning(t("msg.warning"), t("users.required_fields"))
            return
        if password != password2:
            messagebox.showwarning(t("msg.warning"), t("users.password_mismatch"))
            return
        if len(password) < 4:
            messagebox.showwarning(t("msg.warning"), t("users.password_short"))
            return
        try:
            auth.create_user(username, password, role, full_name)
            messagebox.showinfo(t("msg.success"),
                                t("users.created_ok", u=username))
            for e in self.entries.values():
                e.delete(0, tk.END)
            self.load_users()
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    def rename_dialog(self):
        values = self._selected_user()
        if not values:
            return
        user_id, old_username = int(values[0]), values[1]

        dlg = tk.Toplevel(self.root)
        dlg.title(t("users.rename_title", u=old_username))
        dlg.geometry("360x180")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg=theme.BG)

        tk.Label(dlg, text=t("users.new_name_for", u=old_username),
                 bg=theme.BG, fg=theme.FG, font=self.font(10)
                 ).pack(pady=(20, 4))
        entry = tk.Entry(dlg, font=self.font(10), width=26,
                         bg="white", fg=theme.FG, relief="solid", bd=1,
                         justify=i18n.justify_text())
        entry.pack(pady=6, ipady=3)
        entry.insert(0, old_username)
        entry.focus_set()
        entry.select_range(0, tk.END)

        def submit(event=None):
            new_name = entry.get().strip()
            if not new_name:
                messagebox.showerror(t("msg.error"), t("users.name_empty"),
                                     parent=dlg)
                return
            if new_name == old_username:
                dlg.destroy()
                return
            try:
                auth.rename_user(user_id, new_name)
            except ValueError as e:
                key = "err.rename_empty" if str(e) == "empty" else "err.rename_taken"
                messagebox.showerror(
                    t("msg.error"),
                    t(key, name=new_name) if key.endswith("taken") else t(key),
                    parent=dlg)
                return
            if self.user and self.user.get("id") == user_id:
                self.user["username"] = new_name
                try:
                    self.root.title(t("app.window_title",
                                       username=new_name,
                                       role=t(f"role.{self.user['role']}")))
                except tk.TclError:
                    pass
            messagebox.showinfo(t("msg.success"),
                                t("users.renamed_ok", u=new_name), parent=dlg)
            dlg.destroy()
            self.load_users()

        tk.Button(dlg, text=t("btn.save"), bg=theme.GREEN, fg="white",
                  font=self.font(10, "bold"), width=10, relief="flat",
                  command=submit).pack(pady=12)
        dlg.bind("<Return>", submit)
        dlg.bind("<KP_Enter>", submit)

    def toggle_active(self):
        values = self._selected_user()
        if not values:
            return
        user_id = int(values[0])
        if user_id == self.user["id"]:
            messagebox.showerror(t("msg.error"), t("users.cannot_disable_self"))
            return
        is_active = values[4] == t("users.active_yes")
        try:
            auth.set_user_active(user_id, not is_active)
            self.load_users()
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    def change_password_dialog(self):
        values = self._selected_user()
        if not values:
            return
        user_id, username = int(values[0]), values[1]

        dlg = tk.Toplevel(self.root)
        dlg.title(f"{t('users.change_password')} - {username}")
        dlg.geometry("320x180")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg=theme.BG)

        tk.Label(dlg, text=t("users.password_new"), bg=theme.BG,
                 font=self.font(10)).pack(pady=(20, 4))
        p1 = tk.Entry(dlg, show="*", font=self.font(10), width=22,
                      justify=i18n.justify_text())
        p1.pack(pady=4)
        p1.focus_set()
        tk.Label(dlg, text=t("users.confirm"), bg=theme.BG,
                 font=self.font(10)).pack(pady=(4, 4))
        p2 = tk.Entry(dlg, show="*", font=self.font(10), width=22,
                      justify=i18n.justify_text())
        p2.pack(pady=4)

        def submit():
            if p1.get() != p2.get():
                messagebox.showerror(t("msg.error"), t("users.password_mismatch"),
                                     parent=dlg)
                return
            if len(p1.get()) < 4:
                messagebox.showerror(t("msg.error"), t("users.password_short"),
                                     parent=dlg)
                return
            try:
                auth.change_password(user_id, p1.get())
                messagebox.showinfo(t("msg.success"),
                                    t("users.password_changed"), parent=dlg)
                dlg.destroy()
            except Exception as e:
                messagebox.showerror(t("msg.error"), str(e), parent=dlg)

        tk.Button(dlg, text=t("btn.save"), bg=theme.GREEN, fg="white",
                  font=self.font(10, "bold"), width=10, relief="flat",
                  command=submit).pack(pady=12)
        dlg.bind("<Return>", lambda e: submit())

    def delete_selected(self):
        values = self._selected_user()
        if not values:
            return
        user_id, username = int(values[0]), values[1]
        if user_id == self.user["id"]:
            messagebox.showerror(t("msg.error"), t("users.cannot_delete_self"))
            return
        if not messagebox.askyesno(t("msg.confirmation"),
                                   t("users.confirm_delete", u=username)):
            return
        try:
            auth.delete_user(user_id)
            self.load_users()
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    def load_users(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        yes, no = t("users.active_yes"), t("users.active_no")
        for uid, username, full_name, role, is_active, created in auth.list_users():
            self.tree.insert("", "end", values=(
                uid, username, full_name or "", t(f"role.{role}"),
                yes if is_active else no, created or "",
            ))

    def on_show(self):
        self.load_users()