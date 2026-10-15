# screens/deleted_sales.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import db_operations as db
from utils import auth, i18n
from utils.i18n import t


class DeletedSalesScreen:
    def __init__(self, root, switch_callback, user=None):
        self.root = root
        self.switch = switch_callback
        self.user = user
        self.frame = tk.Frame(root, bg='#f0f0f0')
        self._active_range = (None, None)
        self.setup_ui()
        self.reload()

    def _font(self, size, weight="normal"):
        return i18n.ui_font(size, weight)

    def setup_ui(self):
        FONT_BOLD  = self._font(10, 'bold')
        FONT_BODY  = self._font(9)

        top = tk.Frame(self.frame, bg='#7f1d1d', height=45)
        top.pack(fill='x')
        top.pack_propagate(False)

        # ---- Start side ----
        tk.Button(top, text=t("nav.back_to_history"), bg='#991b1b', fg='white',
                  font=FONT_BODY,
                  command=lambda: self.switch('history')
                  ).pack(side=i18n.side_start(), padx=5, pady=8)

        if auth.can(self.user, "view_reports"):
            tk.Button(top, text=t("nav.reports_arrow"), bg='#991b1b', fg='white',
                      font=FONT_BODY,
                      command=lambda: self.switch('reports')
                      ).pack(side=i18n.side_start(), padx=5, pady=8)

        tk.Label(top, text=t("deleted.title"),
                 bg='#7f1d1d', fg='white',
                 font=self._font(12, 'bold')).pack(side='top', pady=10)

        # ---- End side ----
        if auth.can(self.user, "manage_users"):
            tk.Button(top, text=t("nav.users_arrow"), bg='#991b1b', fg='white',
                      font=FONT_BODY,
                      command=lambda: self.switch('users')
                      ).pack(side=i18n.side_end(), padx=5, pady=8)

        if auth.can(self.user, "sell"):
            tk.Button(top, text=t("nav.sales_arrow"), bg='#991b1b', fg='white',
                      font=FONT_BODY,
                      command=lambda: self.switch('sales')
                      ).pack(side=i18n.side_end(), padx=5, pady=8)

        main = tk.Frame(self.frame, bg='#f0f0f0')
        main.pack(fill='both', expand=True, padx=5, pady=5)

        filter_frame = tk.Frame(main, bg='white', relief='groove', bd=1)
        filter_frame.pack(fill='x', pady=(0, 5))

        today = datetime.now().strftime('%Y-%m-%d')

        start_frame = tk.Frame(filter_frame, bg='white')
        start_frame.pack(side=i18n.side_start(), padx=10, pady=6)
        tk.Label(start_frame, text=t("deleted.deleted_from"), bg='white',
                 font=FONT_BODY).pack(side=i18n.side_start())
        self.start_date = tk.Entry(start_frame, width=10, font=FONT_BODY,
                                   justify=i18n.justify_text())
        self.start_date.pack(side=i18n.side_start(), padx=2)
        self.start_date.insert(0, today)
        self.start_time = tk.Entry(start_frame, width=5, font=FONT_BODY,
                                   justify=i18n.justify_text())
        self.start_time.pack(side=i18n.side_start(), padx=2)
        self.start_time.insert(0, '00:00')

        end_frame = tk.Frame(filter_frame, bg='white')
        end_frame.pack(side=i18n.side_start(), padx=10, pady=6)
        tk.Label(end_frame, text=t("deleted.to"), bg='white',
                 font=FONT_BODY).pack(side=i18n.side_start())
        self.end_date = tk.Entry(end_frame, width=10, font=FONT_BODY,
                                 justify=i18n.justify_text())
        self.end_date.pack(side=i18n.side_start(), padx=2)
        self.end_date.insert(0, today)
        self.end_time = tk.Entry(end_frame, width=5, font=FONT_BODY,
                                 justify=i18n.justify_text())
        self.end_time.pack(side=i18n.side_start(), padx=2)
        self.end_time.insert(0, '23:59')

        tk.Button(filter_frame, text=t("deleted.filter"), bg='#3498db', fg='white',
                  font=FONT_BODY, command=self.apply_filter
                  ).pack(side=i18n.side_start(), padx=5)
        tk.Button(filter_frame, text=t("deleted.view_all"), bg='#95a5a6', fg='white',
                  font=FONT_BODY, command=self.clear_filter
                  ).pack(side=i18n.side_start(), padx=5)
        tk.Button(filter_frame, text=t("btn.refresh"), bg='#3498db', fg='white',
                  font=FONT_BODY, width=2, command=self.reload
                  ).pack(side=i18n.side_start(), padx=5)

        summary_frame = tk.Frame(filter_frame, bg='white')
        summary_frame.pack(side=i18n.side_end(), padx=10, pady=6)
        self.total_label = tk.Label(summary_frame,
                                    text=f'{t("lbl.total")}: 0.00 DT',
                                    bg='white', font=FONT_BOLD)
        self.total_label.pack(side=i18n.side_start(), padx=5)
        self.count_label = tk.Label(summary_frame,
                                    text=f'{t("lbl.articles")}: 0',
                                    bg='white', font=FONT_BOLD)
        self.count_label.pack(side=i18n.side_start(), padx=5)

        tree_container = tk.Frame(main, bg='white', relief='groove', bd=1)
        tree_container.pack(fill='both', expand=True)

        columns = ('ddate', 'dtime', 'by', 'count', 'total', 'profit')
        self.tree = ttk.Treeview(tree_container, columns=columns,
                                 show='headings',
                                 selectmode='extended', height=20)
        headings = [
            t("deleted.col_deleted_at"), t("deleted.col_time"),
            t("deleted.col_by"), t("deleted.col_items"),
            t("deleted.col_total"), t("deleted.col_profit"),
        ]
        col_widths = [110, 70, 120, 80, 110, 110]
        for col, hdr, width in zip(columns, headings, col_widths):
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=width, anchor='center')

        v_scroll = ttk.Scrollbar(tree_container, orient='vertical',
                                 command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient='horizontal',
                                 command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set,
                            xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        self.tree.bind('<Double-1>', self.view_details)

        btn_frame = tk.Frame(main, bg='#f0f0f0')
        btn_frame.pack(fill='x', pady=5)

        tk.Button(btn_frame, text=t("deleted.restore_selection"),
                  bg='#27ae60', fg='white',
                  font=self._font(10), width=22,
                  command=self.restore_selected
                  ).pack(side=i18n.side_start(), padx=5)

        tk.Button(btn_frame, text=t("btn.details"), bg='#3498db', fg='white',
                  font=self._font(10), width=15,
                  command=self.show_details_selected
                  ).pack(side=i18n.side_start(), padx=5)

        tk.Label(btn_frame,
                 text=t("deleted.restore_hint"),
                 bg='#f0f0f0', fg='#e67e22',
                 font=FONT_BODY).pack(side=i18n.side_end(), padx=5)

    def reload(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        start_dt, end_dt = self._active_range
        groups = db.get_deleted_groups(start_dt, end_dt)

        total_amount = 0.0
        total_lines = 0

        for (deleted_at, count, amount, profit, username) in groups:
            date_part = deleted_at[:10] if deleted_at else ''
            time_part = (deleted_at[11:16]
                         if deleted_at and len(deleted_at) > 16 else '')
            self.tree.insert('', 'end', values=(
                date_part, time_part, username, count,
                f"{amount:.2f}", f"{profit:.2f}",
            ), tags=(deleted_at,))
            total_amount += amount or 0
            total_lines += count or 0

        self.total_label.config(text=f'{t("lbl.total")}: {total_amount:.2f} DT')
        self.count_label.config(text=f'{t("lbl.articles")}: {total_lines}')

    def apply_filter(self):
        try:
            start_str = f"{self.start_date.get().strip()} {self.start_time.get().strip()}:00"
            end_str = f"{self.end_date.get().strip()} {self.end_time.get().strip()}:59"
            datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror(t("msg.error"), t("reports.invalid_datetime"))
            return
        if start_str > end_str:
            messagebox.showerror(t("msg.error"), t("reports.start_after_end"))
            return
        self._active_range = (start_str, end_str)
        self.reload()

    def clear_filter(self):
        self._active_range = (None, None)
        self.reload()

    def _selected_deletion_timestamps(self):
        result = []
        for item in self.tree.selection():
            tags = self.tree.item(item, 'tags')
            if tags:
                result.append(tags[0])
        return result

    def restore_selected(self):
        if not auth.can(self.user, "view_deleted_sales"):
            messagebox.showerror(t("msg.access_denied"), t("msg.no_permission"))
            return
        stamps = self._selected_deletion_timestamps()
        if not stamps:
            messagebox.showwarning(t("msg.warning"),
                                   t("deleted.select_to_restore"))
            return
        if not messagebox.askyesno(
            t("msg.confirmation"),
            t("deleted.confirm_restore", n=len(stamps))
        ):
            return
        errors = []
        for ts in stamps:
            try:
                db.restore_sales_by_deletion_timestamp(ts)
            except Exception as e:
                errors.append(f"{ts}: {e}")
        if errors:
            messagebox.showerror(t("msg.error"), '\n'.join(errors[:5]))
        else:
            messagebox.showinfo(t("msg.success"),
                                t("deleted.restore_ok", n=len(stamps)))
        self.reload()

    def show_details_selected(self):
        stamps = self._selected_deletion_timestamps()
        if not stamps:
            messagebox.showwarning(t("msg.warning"), t("deleted.select_item"))
            return
        self.show_details_for_timestamp(stamps[0])

    def view_details(self, event=None):
        selected = self.tree.selection()
        if selected:
            ts = self.tree.item(selected[0], 'tags')[0]
            self.show_details_for_timestamp(ts)

    def show_details_for_timestamp(self, deleted_at):
        sales = db.get_deleted_sales_by_deletion_timestamp(deleted_at)
        if not sales:
            messagebox.showinfo(t("msg.info"), t("deleted.nothing_to_show"))
            return

        popup = tk.Toplevel(self.root)
        popup.title(t("deleted.details_title", ts=deleted_at))
        popup.geometry("720x520")
        popup.transient(self.root)
        popup.update_idletasks()
        popup.grab_set()

        tk.Label(popup, text=t("deleted.deleted_on", ts=deleted_at),
                 font=self._font(12, 'bold')).pack(pady=6)

        columns = ('id', 'sdate', 'product', 'qty', 'unit',
                   'total', 'profit', 'by', 'reason')
        tree = ttk.Treeview(popup, columns=columns, show='headings', height=12)
        headings = {
            'id': (t("history.col_id"), 0),
            'sdate': (t("deleted.col_sale_of"), 130),
            'product': (t("history.col_product"), 180),
            'qty': (t("history.col_qty"), 50),
            'unit': (t("history.col_unit"), 60),
            'total': (t("history.col_total"), 80),
            'profit': (t("history.col_profit"), 80),
            'by': (t("deleted.col_by"), 100),
            'reason': (t("deleted.col_reason"), 140),
        }
        for col, (label, width) in headings.items():
            tree.heading(col, text=label)
            tree.column(col, width=width,
                        anchor=(i18n.anchor_start()
                                if col in ('product', 'reason') else 'center'),
                        stretch=(col in ('product', 'reason')))
        tree.pack(fill='both', expand=True, padx=10, pady=(0, 5))

        def rebuild():
            for row in tree.get_children():
                tree.delete(row)
            rows = db.get_deleted_sales_by_deletion_timestamp(deleted_at)
            for (sale_id, orig_date, product, qty, unit, total, profit,
                 username, reason) in rows:
                qty_str = (f"{qty:.0f} g" if unit in ('gram', 'g')
                           else f"{qty:.0f}")
                tree.insert('', 'end', values=(
                    sale_id, orig_date, product[:28], qty_str, unit,
                    f"{total:.2f} DT", f"{profit:.2f} DT",
                    username, reason or '',
                ))
            if not rows:
                messagebox.showinfo(t("msg.info"), t("deleted.no_more_items"),
                                    parent=popup)
                popup.destroy()
                self.reload()

        rebuild()

        def restore_one():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning(t("msg.warning"),
                                       t("deleted.select_item"), parent=popup)
                return
            sale_id = tree.item(selected[0])['values'][0]
            if not messagebox.askyesno(
                t("msg.confirmation"),
                t("deleted.confirm_restore_one"), parent=popup):
                return
            try:
                db.restore_sale(sale_id)
            except Exception as e:
                messagebox.showerror(t("msg.error"), str(e), parent=popup)
                return
            self.reload()
            rebuild()

        btn_frame = tk.Frame(popup)
        btn_frame.pack(fill='x', padx=10, pady=(0, 8))

        tk.Button(btn_frame, text=t("deleted.restore_one"),
                  bg='#27ae60', fg='white',
                  command=restore_one).pack(side=i18n.side_start(), padx=5)
        tk.Button(btn_frame, text=t("btn.close"), bg='#95a5a6', fg='white',
                  command=popup.destroy).pack(side=i18n.side_end(), padx=5)

    def show(self):
        self.frame.pack(fill='both', expand=True)
        self.reload()

    def hide(self):
        self.frame.pack_forget()
