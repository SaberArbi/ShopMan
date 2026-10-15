"""Sales history — filter, view, soft/hard delete, verify."""
import tkinter as tk
from tkinter import messagebox, ttk

from app import theme
from database import db
from database.errors import DomainError
from screens.base import BaseScreen
from screens.widgets import DateRangeFilter, ScrollableTreeview, build_topbar
from utils import auth, i18n
from utils.i18n import t


class HistoryScreen(BaseScreen):
    topbar_color = theme.DARK_LIGHT

    def __init__(self, root, switch, user=None, logout=None):
        self._active_range = (None, None)
        super().__init__(root, switch, user, logout=None)
        self.apply_filter()

    def build_topbar(self):
        start, end = [], []
        if auth.can(self.user, "sell"):
            start.append((t("nav.back_to_sales"), theme.DARK,
                          lambda: self.switch("sales")))
        if auth.can(self.user, "view_deleted_sales"):
            end.append((t("history.deleted_btn"), theme.RED_DARKER,
                        lambda: self.switch("deleted")))
        if auth.can(self.user, "view_reports"):
            end.append((t("nav.reports_arrow"), theme.DARK,
                        lambda: self.switch("reports")))
        build_topbar(self.frame, color=self.topbar_color,
                     title_key="history.title",
                     buttons_start=start, buttons_end=end,
                     logout_callback=self.logout)


    def build_body(self):
        main = tk.Frame(self.frame, bg=theme.BG)
        main.pack(fill="both", expand=True, padx=5, pady=5)

        self.filter = DateRangeFilter(
            main, on_apply=self.apply_filter,
            on_clear=self._clear_filter,
            on_refresh=self.refresh,
            show_verify=True, on_verify=self.verify_sales,
        )
        self.filter.pack(fill="x", pady=(0, 5))

        # summary labels attached to the filter's right side
        summary = tk.Frame(self.filter, bg=theme.BG_CARD)
        summary.pack(side=i18n.side_end(), padx=10, pady=6)
        self.total_label = tk.Label(summary, text=f'{t("lbl.total")}: 0 DT',
                                    bg=theme.BG_CARD, font=self.font(10, "bold"))
        self.total_label.pack(side=i18n.side_start(), padx=5)
        self.profit_label = tk.Label(summary, text=f'{t("lbl.profit")}: 0 DT',
                                     bg=theme.BG_CARD, fg=theme.GREEN,
                                     font=self.font(10, "bold"))
        self.profit_label.pack(side=i18n.side_start(), padx=5)
        self.count_label = tk.Label(summary, text=f'{t("lbl.sales_count")}: 0',
                                    bg=theme.BG_CARD, font=self.font(10, "bold"))
        self.count_label.pack(side=i18n.side_start(), padx=5)

        self.tree_widget = ScrollableTreeview(
            main,
            columns=("date", "time", "count", "total", "profit"),
            headings=[t("history.col_date"), t("history.col_time"),
                      t("history.col_count"), t("history.col_total"),
                      t("history.col_profit")],
            widths=[110, 70, 70, 110, 110],
        )
        self.tree_widget.pack(fill="both", expand=True)
        self.tree_widget.bind("<Double-1>", self.view_details)
        self.tree = self.tree_widget.tree

        self._build_footer(main)

    def _build_footer(self, parent):
        footer = tk.Frame(parent, bg=theme.BG)
        footer.pack(fill="x", pady=5)
        if auth.can(self.user, "soft_delete_sale"):
            tk.Button(footer, text=t("history.btn_soft_delete"),
                      bg=theme.ORANGE, fg="white",
                      font=self.font(10), width=18,
                      command=self.delete_selected_soft
                      ).pack(side=i18n.side_start(), padx=5)
        if auth.can(self.user, "hard_delete_sale"):
            tk.Button(footer, text=t("history.btn_hard_delete"),
                      bg=theme.RED, fg="white",
                      font=self.font(10), width=22,
                      command=self.delete_selected_hard
                      ).pack(side=i18n.side_start(), padx=5)
        tk.Button(footer, text=t("btn.details_sale"), bg=theme.BLUE, fg="white",
                  font=self.font(10), width=15,
                  command=self.show_details_selected
                  ).pack(side=i18n.side_start(), padx=5)
        tk.Label(footer, text=t("history.hint"), bg=theme.BG, fg=theme.ORANGE,
                 font=self.font(9)).pack(side=i18n.side_end(), padx=5)

    # ------------------------------------------------------------------
    def load_history(self, start_dt=None, end_dt=None):
        self.tree_widget.clear()
        self._active_range = (start_dt, end_dt)
        groups = db.get_grouped_sales(start_dt, end_dt)
        total_amount = total_profit = 0.0
        for timestamp, count, amount, profit in groups:
            date_part = timestamp[:10]
            time_part = (timestamp[11:16] if len(timestamp) > 16
                         else timestamp[11:])
            self.tree_widget.insert_row(
                (date_part, time_part, count, f"{amount:.2f}", f"{profit:.2f}"),
                tags=(timestamp,))
            total_amount += amount
            total_profit += profit

        self.total_label.config(text=f'{t("lbl.total")}: {total_amount:.2f} DT')
        self.profit_label.config(text=f'{t("lbl.profit")}: {total_profit:.2f} DT')
        self.count_label.config(text=f'{t("lbl.sales_count")}: {len(groups)}')

    def apply_filter(self):
        try:
            start, end = self.filter.get_range()
        except ValueError as e:
            messagebox.showerror(t("msg.error"), str(e))
            return
        self.load_history(start, end)

    def _clear_filter(self):
        self.apply_filter()

    def refresh(self):
        self.load_history(*self._active_range)

    # ------------------------------------------------------------------
    def delete_selected_soft(self):
        if not auth.can(self.user, "soft_delete_sale"):
            messagebox.showerror(t("msg.access_denied"), t("msg.no_permission"))
            return
        stamps = self.tree_widget.selection_tags()
        if not stamps:
            messagebox.showwarning(t("msg.warning"),
                                   t("history.select_to_delete"))
            return
        if not messagebox.askyesno(t("msg.confirmation"),
                                   t("history.confirm_soft", n=len(stamps))):
            return
        errors = []
        for ts in stamps:
            try:
                db.soft_delete_sales_by_timestamp(ts, self.user["id"])
            except DomainError as e:
                errors.append(f"{ts}: {t(e.key, **e.kwargs)}")
            except Exception as e:
                errors.append(f"{ts}: {e}")
        self._report_bulk(errors, stamps)

    def delete_selected_hard(self):
        if not auth.can(self.user, "hard_delete_sale"):
            messagebox.showerror(t("msg.access_denied"),
                                 t("history.owner_only_hard"))
            return
        stamps = self.tree_widget.selection_tags()
        if not stamps:
            messagebox.showwarning(t("msg.warning"),
                                   t("history.select_to_delete"))
            return
        if not messagebox.askyesno(t("msg.confirmation"),
                                   t("history.confirm_hard", n=len(stamps))):
            return
        errors = []
        for ts in stamps:
            try:
                db.hard_delete_sales_by_timestamp(ts)
            except DomainError as e:
                errors.append(f"{ts}: {t(e.key, **e.kwargs)}")
            except Exception as e:
                errors.append(f"{ts}: {e}")
        self._report_bulk(errors, stamps)

    def _report_bulk(self, errors, stamps):
        if errors:
            messagebox.showerror(t("msg.error"), "\n".join(errors[:5]))
        else:
            messagebox.showinfo(t("msg.success"),
                                t("history.deleted_ok", n=len(stamps)))
        self.refresh()

    # ------------------------------------------------------------------
    def show_details_selected(self):
        stamps = self.tree_widget.selection_tags()
        if not stamps:
            messagebox.showwarning(t("msg.warning"), t("history.select_sale"))
            return
        self.show_details_for_timestamp(stamps[0])

    def view_details(self, event=None):
        sel = self.tree.selection()
        if sel:
            ts = self.tree.item(sel[0], "tags")[0]
            self.show_details_for_timestamp(ts)

    def show_details_for_timestamp(self, timestamp):
        if not db.get_sales_by_timestamp(timestamp):
            messagebox.showinfo(t("msg.info"), t("history.no_items"))
            return

        popup = tk.Toplevel(self.root)
        popup.title(t("history.details_title", ts=timestamp))
        popup.geometry("620x500")
        popup.transient(self.root)
        popup.update_idletasks()
        popup.grab_set()

        tk.Label(popup, text=t("history.sale_of", ts=timestamp),
                 font=self.font(12, "bold")).pack(pady=6)

        columns = ("id", "product", "qty", "unit", "total", "profit")
        tree = ttk.Treeview(popup, columns=columns, show="headings", height=10)
        for col, label, w, anchor, stretch in (
            ("id", t("history.col_id"), 0, "center", False),
            ("product", t("history.col_product"), 220, i18n.anchor_start(), True),
            ("qty", t("history.col_qty"), 80, "center", False),
            ("unit", t("history.col_unit"), 70, "center", False),
            ("total", t("history.col_total"), 80, "center", False),
            ("profit", t("history.col_profit"), 80, "center", False),
        ):
            tree.heading(col, text=label)
            tree.column(col, width=w, anchor=anchor, stretch=stretch)
        tree.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        summary = tk.Frame(popup)
        summary.pack(fill="x", padx=10, pady=5)
        total_lbl = tk.Label(summary, text="", font=self.font(10, "bold"))
        total_lbl.pack(side=i18n.side_start(), padx=10)
        profit_lbl = tk.Label(summary, text="", font=self.font(10, "bold"),
                              fg=theme.GREEN)
        profit_lbl.pack(side=i18n.side_start(), padx=10)

        def rebuild():
            for row in tree.get_children():
                tree.delete(row)
            rows = db.get_sales_by_timestamp(timestamp)
            tot = prof = 0.0
            for sale_id, product, qty, unit, total, profit in rows:
                qty_str = (f"{qty:.0f} g" if unit in ("gram", "g")
                           else f"{qty:.0f}")
                tree.insert("", "end", values=(
                    sale_id, product[:34], qty_str, unit,
                    f"{total:.2f} DT", f"{profit:.2f} DT"))
                tot += total
                prof += profit
            total_lbl.config(text=f"{t('lbl.total')}: {tot:.2f} DT")
            profit_lbl.config(text=f"{t('lbl.profit')}: {prof:.2f} DT")
            if not rows:
                messagebox.showinfo(t("msg.info"), t("history.no_items"),
                                    parent=popup)
                popup.destroy()
                self.refresh()

        rebuild()

        def delete_selected_item():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning(t("msg.warning"),
                                       t("deleted.select_item"), parent=popup)
                return
            sale_id = tree.item(sel[0])["values"][0]
            if auth.can(self.user, "hard_delete_sale"):
                if not messagebox.askyesno(
                    t("msg.confirmation"),
                    t("history.delete_item_confirm_hard"), parent=popup):
                    return
                try:
                    db.delete_sale(sale_id)
                except Exception as e:
                    messagebox.showerror(t("msg.error"), str(e), parent=popup)
                    return
            elif auth.can(self.user, "soft_delete_sale"):
                if not messagebox.askyesno(
                    t("msg.confirmation"),
                    t("history.delete_item_confirm"), parent=popup):
                    return
                try:
                    db.soft_delete_sale(sale_id, self.user["id"])
                except Exception as e:
                    messagebox.showerror(t("msg.error"), str(e), parent=popup)
                    return
            else:
                messagebox.showerror(t("msg.access_denied"),
                                     t("msg.no_permission"), parent=popup)
                return
            self.refresh()
            rebuild()

        btns = tk.Frame(popup)
        btns.pack(fill="x", padx=10, pady=(0, 8))
        if auth.can(self.user, "soft_delete_sale"):
            label = (t("history.btn_hard_delete")
                     if auth.can(self.user, "hard_delete_sale")
                     else t("history.delete_item"))
            tk.Button(btns, text=label, bg=theme.RED, fg="white",
                      command=delete_selected_item
                      ).pack(side=i18n.side_start(), padx=5)
        tk.Button(btns, text=t("btn.close"), bg=theme.GRAY, fg="white",
                  command=popup.destroy).pack(side=i18n.side_end(), padx=5)

    # ------------------------------------------------------------------
    def verify_sales(self):
        at, ap, gt, gp = db.verify_sales_aggregates()
        ok = abs(at - gt) < 0.01
        messagebox.showinfo(
            t("history.verify_title"),
            "\n".join((
                t("history.verify_total", t=at),
                t("history.verify_grouped", t=gt),
                t("history.verify_profit", p=ap),
                t("history.verify_grouped_profit", p=gp),
                "",
                t("history.verify_ok") if ok else t("history.verify_bad"),
            )),
        )

    def on_show(self):
        self.refresh()