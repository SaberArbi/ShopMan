"""Reports container — a notebook of tabs."""
import tkinter as tk
from tkinter import ttk

from app import theme
from screens.base import BaseScreen
from screens.widgets import build_topbar
from utils import auth, i18n
from utils.i18n import t

from .tab_summary import SummaryTab
from .tab_products import TopProductsTab
from .tab_stock import StockTab
from .tab_export import ExportTab


class ReportsScreen(BaseScreen):
    topbar_color = theme.PURPLE

    # Shared state for the tabs (mainly the low-stock threshold).
    low_stock_threshold = 10

    def build_topbar(self):
        start, end = [], []
        if auth.can(self.user, "sell"):
            start.append((t("nav.back_to_sales"), theme.PURPLE_LIGHT,
                          lambda: self.switch("sales")))
        if auth.can(self.user, "view_history"):
            start.append((t("nav.history"), theme.PURPLE_LIGHT,
                          lambda: self.switch("history")))
        if auth.can(self.user, "view_deleted_sales"):
            start.append((t("history.deleted_btn"), theme.RED_DARKER,
                          lambda: self.switch("deleted")))
        if auth.can(self.user, "manage_products"):
            end.append((t("nav.products_arrow"), theme.PURPLE_LIGHT,
                        lambda: self.switch("products")))
        if auth.can(self.user, "manage_users"):
            end.append((t("nav.users"), theme.PURPLE_LIGHT,
                        lambda: self.switch("users")))
        build_topbar(self.frame, color=self.topbar_color,
                     title_key="reports.title",
                     buttons_start=start, buttons_end=end,
                     logout_callback=self.logout)

    def build_body(self):
        nb = ttk.Notebook(self.frame)
        nb.pack(fill="both", expand=True, padx=5, pady=5)

        for tab_cls, key in (
            (SummaryTab, "reports.tab_summary"),
            (TopProductsTab, "reports.tab_products"),
            (StockTab, "reports.tab_stock"),
            (ExportTab, "reports.tab_export"),
        ):
            tab = tab_cls(nb, self)
            nb.add(tab, text=t(key))

    def on_show(self):
        pass