"""Top-level application: auth, screen registry, navigation, shutdown."""
import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

from database import migrations, schema
from database.connection import DB_PATH
from screens.login import LoginDialog
from screens.sales import SalesScreen
from screens.products import ProductsScreen
from screens.reports import ReportsScreen
from screens.history import HistoryScreen
from screens.users import UsersScreen
from screens.deleted_sales import DeletedSalesScreen
from utils import auth, backup, i18n
from utils.i18n import t


def _ensure_database() -> None:
    if not os.path.exists(DB_PATH):
        schema.create_tables()
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name='products'")
        if not cur.fetchone():
            schema.create_tables()
    finally:
        conn.close()


def _setup_ttk_style(root: tk.Tk) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Treeview", rowheight=26, font=i18n.ui_font(9))
    style.configure("Treeview.Heading", font=i18n.ui_font(9, "bold"))
    style.configure("TNotebook.Tab",
                    font=i18n.ui_font(9, "bold"), padding=[10, 3])


# (screen name, required permission, screen class)
_SCREEN_BUILDERS = (
    ("sales",    "sell",               SalesScreen),
    ("reports",  "view_reports",       ReportsScreen),
    ("history",  "view_history",       HistoryScreen),
    ("products", "manage_products",    ProductsScreen),
    ("users",    "manage_users",       UsersScreen),
    ("deleted",  "view_deleted_sales", DeletedSalesScreen),
)

_OPEN_ORDER = ("sales", "history", "reports", "products", "users", "deleted")


class StockManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.user = None
        self.screens: dict[str, object] = {}
        self.current_screen: str | None = None

        _ensure_database()
        migrations.ensure_auth_schema()
        _setup_ttk_style(self.root)
        backup.start_auto_backup()

        if not self._do_login():
            self.root.destroy()
            return
        if not self._build_screens():
            self.root.destroy()
            return

        self._open_first_available()
        self.root.deiconify()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ------------------------------------------------------------------
    # Login / build / teardown
    # ------------------------------------------------------------------
    def _do_login(self) -> bool:
        login = LoginDialog(self.root)
        self.user = login.show()
        return bool(self.user)

    def _build_screens(self) -> bool:
        self.root.title(t("app.window_title",
                           username=self.user["username"],
                           role=t(f"role.{self.user['role']}")))
        self.root.geometry("1400x850")
        self.root.minsize(1100, 700)

        for name, permission, cls in _SCREEN_BUILDERS:
            if auth.can(self.user, permission):
                self.screens[name] = cls(self.root, self.switch_screen,
                                          self.user, self.logout)

        if not self.screens:
            messagebox.showerror(t("msg.error"), t("startup.no_screen"))
            return False
        return True

    def _open_first_available(self) -> None:
        for name in _OPEN_ORDER:
            if name in self.screens:
                self.current_screen = name
                self.screens[name].show()
                return

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    def switch_screen(self, screen_name: str) -> None:
        if screen_name not in self.screens:
            messagebox.showwarning(t("msg.access_denied"),
                                   t("startup.permission_denied"))
            return
        if self.current_screen and self.current_screen in self.screens:
            self.screens[self.current_screen].hide()
        self.screens[screen_name].show()
        self.current_screen = screen_name

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------
    def logout(self) -> None:
        if not messagebox.askyesno(t("msg.confirmation"), t("logout.confirm")):
            return

        # Best-effort backup before we tear everything down.
        try:
            backup.do_backup()
        except Exception as e:
            print(f"Backup on logout failed: {e}")

        # Destroy every screen's frame.
        for screen in self.screens.values():
            try:
                screen.hide()
                screen.frame.destroy()
            except Exception:
                pass
        self.screens.clear()
        self.current_screen = None
        self.user = None

        # Hide the main window, show login again.
        self.root.withdraw()
        if not self._do_login():
            self.root.destroy()
            return
        if not self._build_screens():
            self.root.destroy()
            return

        self._open_first_available()
        self.root.deiconify()

    # ------------------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------------------
    def on_closing(self) -> None:
        try:
            backup.do_backup()
        except Exception as e:
            print(f"Backup on exit failed: {e}")
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()