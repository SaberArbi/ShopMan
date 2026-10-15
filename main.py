#!/usr/bin/env python3
"""
Stock Manager — entry point.
"""
# ---------------------------------------------------------------------------
# IMPORTANT: set the locale BEFORE importing tkinter.
# If Tk starts under LC_CTYPE=C / POSIX, bidi reordering and Arabic shaping
# are silently disabled even when the font supports them.
# ---------------------------------------------------------------------------
import os
import locale

os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("LANG", "C.UTF-8")
try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from database import db_setup
from database.db_operations import DB_PATH
from screens.login import LoginDialog
from screens.products import ProductsScreen
from screens.sales import SalesScreen
from screens.reports import ReportsScreen
from screens.history import HistoryScreen
from screens.users import UsersScreen
from screens.deleted_sales import DeletedSalesScreen
from utils import auth, backup, i18n
from utils.i18n import t


def _setup_ttk_style(root: tk.Tk) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use('clam')
    except tk.TclError:
        pass

    # Row height must accommodate Arabic script ascenders/descenders.
    style.configure('Treeview',
                    rowheight=26,
                    font=i18n.ui_font(9))
    style.configure('Treeview.Heading',
                    font=i18n.ui_font(9, 'bold'))
    style.configure('TNotebook.Tab',
                    font=i18n.ui_font(9, 'bold'),
                    padding=[10, 3])


def _ensure_database() -> None:
    if not os.path.exists(DB_PATH):
        db_setup.create_tables()
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='products'"
        )
        if not cur.fetchone():
            db_setup.create_tables()
    finally:
        conn.close()


class StockManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.user = None

        _ensure_database()
        auth.ensure_auth_schema()

        login = LoginDialog(self.root)
        self.user = login.show()
        if not self.user:
            self.root.destroy()
            return

        self.root.title(t("app.window_title",
                           username=self.user['username'],
                           role=t(f"role.{self.user['role']}")))
        self.root.geometry("1400x850")
        self.root.minsize(1100, 700)

        _setup_ttk_style(self.root)

        backup.start_auto_backup()

        # Build only the screens the user can access.
        self.screens = {}
        if auth.can(self.user, "sell"):
            self.screens['sales'] = SalesScreen(
                self.root, self.switch_screen, self.user)
        if auth.can(self.user, "view_reports"):
            self.screens['reports'] = ReportsScreen(
                self.root, self.switch_screen, self.user)
        if auth.can(self.user, "view_history"):
            self.screens['history'] = HistoryScreen(
                self.root, self.switch_screen, self.user)
        if auth.can(self.user, "manage_products"):
            self.screens['products'] = ProductsScreen(
                self.root, self.switch_screen, self.user)
        if auth.can(self.user, "manage_users"):
            self.screens['users'] = UsersScreen(
                self.root, self.switch_screen, self.user)
        if auth.can(self.user, "view_deleted_sales"):
            self.screens['deleted'] = DeletedSalesScreen(
                self.root, self.switch_screen, self.user)

        if not self.screens:
            messagebox.showerror(
                t("msg.error"), t("startup.no_screen"))
            self.root.destroy()
            return

        for name in ('sales', 'history', 'reports',
                     'products', 'users', 'deleted'):
            if name in self.screens:
                self.current_screen = name
                self.screens[name].show()
                break

        self.root.deiconify()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def switch_screen(self, screen_name: str) -> None:
        if screen_name not in self.screens:
            messagebox.showwarning(
                t("msg.access_denied"),
                t("startup.permission_denied")
            )
            return

        if self.current_screen and self.current_screen in self.screens:
            self.screens[self.current_screen].hide()

        self.screens[screen_name].show()
        self.current_screen = screen_name

    def on_closing(self) -> None:
        try:
            from utils.backup import do_backup
            do_backup()
        except Exception as e:
            print(f"Backup on exit failed: {e}")
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = StockManager()
    if app.user:
        app.run()
