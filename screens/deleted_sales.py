"""Trash — restore or permanently delete soft-deleted sales."""
import tkinter as tk
from tkinter import messagebox, ttk

from app import theme
from database import db
from database.errors import DomainError
from screens.base import BaseScreen
from screens.widgets import DateRangeFilter, ScrollableTreeview, build_topbar
from utils import auth, i18n
from utils.i18n import t


class DeletedSalesScreen(BaseScreen):
    topbar_color = theme.RED_DARKER

    def __init__(self, root, switch, user=None, logout=None):
        self._active_range = (None, None)
        super().__init__(root, switch, user, logout=None)
        self.reload()

    def build_topbar(self):
        start, end = [], []
        start.append((t("nav.back_to_history"), theme.RED_DARK,
                      lambda: self.switch("history")))
        if auth.can(self.user, "view_reports"):
            start.append((t("nav.reports_arrow"), theme.RED_DARK,
                          lambda: self.switch("reports")))
        if auth.can(self.user, "manage_users"):
            end.append((t("nav.users_arrow"), theme.RED_DARK,
                        lambda: self.switch("users")))
        if auth.can(self.user, "sell"):
            end.append((t("nav.sales_arrow"), theme.RED_DARK,
                        lambda: self.switch("sales")))
        build_topbar(self.frame, color=self.topbar_color,
                     title_key="deleted.title",
                     buttons_start=start, buttons_end=end,
                     logout_callback=self.logout)

    def build_body(self):
        main = tk.Frame(self.frame, bg=theme.BG)
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self.filter = DateRangeFilter(
            main,
            from_key="deleted.deleted_from", to_key="deleted.to",
            on_apply=self.apply_filter,
            on_clear=self.clear_filter,
            on_refresh=self.reload,
        )
        self.filter.pack(fill="x", pady=(0, 5))

        tk.Button(self.filter, text=t("deleted.view_all"), bg=theme.GRAY,
                  fg="white", font=self.font(9), command=self.clear_filter
                  ).pack(side=i18n.side_start(), padx=5)

        summary = tk.Frame(self.filter, bg=theme.BG_CARD)
        summary.pack(side=i18n.side_end(), padx=10, pady=6)
        self.total_label = tk.Label(summary, text=f'{t("lbl.total")}: 0.00 DT',
                                    bg=theme.BG_CARD, font=self.font(10, "bold"))
        self.total_label.pack(side=i18n.side_start(), padx=5)
        self.count_label = tk.Label(summary, text=f'{t("lbl.articles")}: 0',
                                    bg=theme.BG_CARD, font=self.font(10, "bold"))
        self.count_label.pack(side=i18n.side_start(), padx=5)

        self.tree_widget = ScrollableTreeview(
            main,
            columns=("ddate", "dtime", "by", "count", "total", "profit"),
            headings=[t("deleted.col_deleted_at"), t("deleted.col_time"),
                      t("deleted.col_by"), t("deleted.col_items"),
                      t("deleted.col_total"), t("deleted.col_profit")],
            widths=[110, 70, 120, 80, 110, 110],
        )
        self.tree_widget.pack(fill="both", expand=True)
        self.tree_widget.bind("<Double-1>", self.view_details)
        self.tree = self.tree_widget.tree

        self._build_footer(main)

    def _build_footer(self, parent):
        footer = tk.Frame(parent, bg=theme.BG)
        footer.pack(fill="x", pady=5)

        # Restore (anyone who can view deleted sales)
        tk.Button(footer, text=t("deleted.restore_selection"),
                  bg=theme.GREEN, fg="white",
                  font=self.font(10), width=22,
                  command=self.restore_selected
                  ).pack(side=i18n.side_start(), padx=5)

        # NEW: permanent delete (owner only — needs hard_delete_sale)
        if auth.can(self.user, "hard_delete_sale"):
            tk.Button(footer, text=t("deleted.hard_delete_selection"),
                      bg=theme.RED, fg="white",
                      font=self.font(10), width=24,
                      command=self.hard_delete_selected
                      ).pack(side=i18n.side_start(), padx=5)

        tk.Button(footer, text=t("btn.details"), bg=theme.BLUE, fg="white",
                  font=self.font(10), width=15,
                  command=self.show_details_selected
                  ).pack(side=i18n.side_start(), padx=5)

        tk.Label(footer, text=t("deleted.restore_hint"),
                 bg=theme.BG, fg=theme.ORANGE,
                 font=self.font(9)).pack(side=i18n.side_end(), padx=5)

    # ------------------------------------------------------------------
    def reload(self):
        self.tree_widget.clear()
        start, end = self._active_range
        groups = db.get_deleted_groups(start, end)
        total_amount = 0.0
        total_lines = 0
        for deleted_at, count, amount, profit, username in groups:
            date_part = deleted_at[:10] if deleted_at else ""
            time_part = (deleted_at[11:16]
                         if deleted_at and len(deleted_at) > 16 else "")
            self.tree_widget.insert_row((
                date_part, time_part, username, count,
                f"{amount:.2f}", f"{profit:.2f}",
            ), tags=(deleted_at,))
            total_amount += amount or 0
            total_lines += count or 0
        self.total_label.config(text=f'{t("lbl.total")}: {total_amount:.2f} DT')
        self.count_label.config(text=f'{t("lbl.articles")}: {total_lines}')

    def apply_filter(self):
        try:
            self._active_range = self.filter.get_range()
        except ValueError as e:
            messagebox.showerror(t("msg.error"), str(e))
            return
        self.reload()

    def clear_filter(self):
        self._active_range = (None, None)
        self.reload()

    # ------------------------------------------------------------------
    def restore_selected(self):
        if not auth.can(self.user, "view_deleted_sales"):
            messagebox.showerror(t("msg.access_denied"), t("msg.no_permission"))
            return
        stamps = self.tree_widget.selection_tags()
        if not stamps:
            messagebox.showwarning(t("msg.warning"),
                                   t("deleted.select_to_restore"))
            return
        if not messagebox.askyesno(
            t("msg.confirmation"),
            t("deleted.confirm_restore", n=len(stamps)),
        ):
            return
        errors = []
        for ts in stamps:
            try:
                db.restore_sales_by_deletion_timestamp(ts)
            except DomainError as e:
                errors.append(f"{ts}: {t(e.key, **e.kwargs)}")
            except Exception as e:
                errors.append(f"{ts}: {e}")
        self._report_bulk(errors, stamps, "deleted.restore_ok")

    # NEW -----------------------------------------------------------------
    def hard_delete_selected(self):
        if not auth.can(self.user, "hard_delete_sale"):
            messagebox.showerror(t("msg.access_denied"),
                                 t("history.owner_only_hard"))
            return
        stamps = self.tree_widget.selection_tags()
        if not stamps:
            messagebox.showwarning(t("msg.warning"),
                                   t("deleted.select_item"))
            return
        if not messagebox.askyesno(
            t("msg.confirmation"),
            t("deleted.confirm_hard", n=len(stamps)),
        ):
            return
        errors = []
        for ts in stamps:
            try:
                db.hard_delete_sales_by_timestamp(ts)
            except DomainError as e:
                errors.append(f"{ts}: {t(e.key, **e.kwargs)}")
            except Exception as e:
                errors.append(f"{ts}: {e}")
        self._report_bulk(errors, stamps, "deleted.hard_deleted_ok")

    # ------------------------------------------------------------------
    def _report_bulk(self, errors, stamps, success_key):
        if errors:
            messagebox.showerror(t("msg.error"), "\n".join(errors[:5]))
        else:
            messagebox.showinfo(t("msg.success"),
                                t(success_key, n=len(stamps)))
        self.reload()

    # ------------------------------------------------------------------
    def show_details_selected(self):
        stamps = self.tree_widget.selection_tags()
        if not stamps:
            messagebox.showwarning(t("msg.warning"), t("deleted.select_item"))
            return
        self.show_details_for_timestamp(stamps[0])

    def view_details(self, event=None):
        sel = self.tree.selection()
        if sel:
            ts = self.tree.item(sel[0], "tags")[0]
            self.show_details_for_timestamp(ts)

    def show_details_for_timestamp(self, deleted_at):
        if not db.get_deleted_sales_by_deletion_timestamp(deleted_at):
            messagebox.showinfo(t("msg.info"), t("deleted.nothing_to_show"))
            return

        popup = tk.Toplevel(self.root)
        popup.title(t("deleted.details_title", ts=deleted_at))
        popup.geometry("720x520")
        popup.transient(self.root)
        popup.update_idletasks()
        popup.grab_set()

        tk.Label(popup, text=t("deleted.deleted_on", ts=deleted_at),
                 font=self.font(12, "bold")).pack(pady=6)

        columns = ("id", "sdate", "product", "qty", "unit",
                   "total", "profit", "by", "reason")
        tree = ttk.Treeview(popup, columns=columns, show="headings", height=12)
        headings = {
            "id": (t("history.col_id"), 0),
            "sdate": (t("deleted.col_sale_of"), 130),
            "product": (t("history.col_product"), 180),
            "qty": (t("history.col_qty"), 50),
            "unit": (t("history.col_unit"), 60),
            "total": (t("history.col_total"), 80),
            "profit": (t("history.col_profit"), 80),
            "by": (t("deleted.col_by"), 100),
            "reason": (t("deleted.col_reason"), 140),
        }
        for col, (label, w) in headings.items():
            tree.heading(col, text=label)
            tree.column(col, width=w,
                        anchor=(i18n.anchor_start()
                                if col in ("product", "reason") else "center"),
                        stretch=(col in ("product", "reason")))
        tree.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        def rebuild():
            for row in tree.get_children():
                tree.delete(row)
            rows = db.get_deleted_sales_by_deletion_timestamp(deleted_at)
            for (sale_id, orig_date, product, qty, unit, total, profit,
                 username, reason) in rows:
                qty_str = (f"{qty:.0f} g" if unit in ("gram", "g")
                           else f"{qty:.0f}")
                tree.insert("", "end", values=(
                    sale_id, orig_date, product[:28], qty_str, unit,
                    f"{total:.2f} DT", f"{profit:.2f} DT",
                    username, reason or "",
                ))
            if not rows:
                messagebox.showinfo(t("msg.info"), t("deleted.no_more_items"),
                                    parent=popup)
                popup.destroy()
                self.reload()

        rebuild()

        def _selected_sale_id():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning(t("msg.warning"),
                                       t("deleted.select_item"), parent=popup)
                return None
            return tree.item(sel[0])["values"][0]

        def restore_one():
            sale_id = _selected_sale_id()
            if sale_id is None:
                return
            if not messagebox.askyesno(
                t("msg.confirmation"),
                t("deleted.confirm_restore_one"), parent=popup):
                return
            try:
                db.restore_sale(sale_id)
            except DomainError as e:
                messagebox.showerror(t("msg.error"), t(e.key, **e.kwargs),
                                     parent=popup)
                return
            except Exception as e:
                messagebox.showerror(t("msg.error"), str(e), parent=popup)
                return
            self.reload()
            rebuild()

        # NEW: permanent delete of a single line from inside the popup
        def hard_delete_one():
            sale_id = _selected_sale_id()
            if sale_id is None:
                return
            if not messagebox.askyesno(
                t("msg.confirmation"),
                t("deleted.confirm_hard_one"), parent=popup):
                return
            try:
                db.delete_sale(sale_id)
            except DomainError as e:
                messagebox.showerror(t("msg.error"), t(e.key, **e.kwargs),
                                     parent=popup)
                return
            except Exception as e:
                messagebox.showerror(t("msg.error"), str(e), parent=popup)
                return
            self.reload()
            rebuild()

        btns = tk.Frame(popup)
        btns.pack(fill="x", padx=10, pady=(0, 8))
        tk.Button(btns, text=t("deleted.restore_one"), bg=theme.GREEN,
                  fg="white", command=restore_one
                  ).pack(side=i18n.side_start(), padx=5)
        if auth.can(self.user, "hard_delete_sale"):
            tk.Button(btns, text=t("deleted.hard_delete_one"),
                      bg=theme.RED, fg="white", command=hard_delete_one
                      ).pack(side=i18n.side_start(), padx=5)
        tk.Button(btns, text=t("btn.close"), bg=theme.GRAY, fg="white",
                  command=popup.destroy).pack(side=i18n.side_end(), padx=5)

    def on_show(self):
        self.reload()