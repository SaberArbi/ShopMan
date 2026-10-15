# screens/history.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import db_operations as db
from utils import auth, i18n
from utils.i18n import t


class HistoryScreen:
    def __init__(self, root, switch_callback, user=None):
        self.root = root
        self.switch = switch_callback
        self.user = user
        self.frame = tk.Frame(root, bg='#f0f0f0')

        self._active_range = (None, None)
        self.setup_ui()
        self.filter_sales()

    def _font(self, size, weight="normal"):
        return i18n.ui_font(size, weight)

    def setup_ui(self):
        FONT_BOLD = self._font(10, 'bold')
        FONT_BODY = self._font(9)

        top = tk.Frame(self.frame, bg='#34495e', height=45)
        top.pack(fill='x')
        top.pack_propagate(False)

        if auth.can(self.user, "sell"):
            tk.Button(top, text=t("nav.back_to_sales"), bg='#2c3e50', fg='white',
                      font=FONT_BODY,
                      command=lambda: self.switch('sales')
                      ).pack(side=i18n.side_start(), padx=5, pady=8)

        tk.Label(top, text=t("history.title"), bg='#34495e', fg='white',
                 font=self._font(12, 'bold')).pack(side='top', pady=10)

        if auth.can(self.user, "view_deleted_sales"):
            tk.Button(top, text=t("history.deleted_btn"), bg='#7f1d1d', fg='white',
                      font=FONT_BODY,
                      command=lambda: self.switch('deleted')
                      ).pack(side=i18n.side_end(), padx=5, pady=8)

        if auth.can(self.user, "view_reports"):
            tk.Button(top, text=t("nav.reports_arrow"), bg='#2c3e50', fg='white',
                      font=FONT_BODY,
                      command=lambda: self.switch('reports')
                      ).pack(side=i18n.side_end(), padx=5, pady=8)

        main = tk.Frame(self.frame, bg='#f0f0f0')
        main.pack(fill='both', expand=True, padx=5, pady=5)

        filter_frame = tk.Frame(main, bg='white', relief='groove', bd=1)
        filter_frame.pack(fill='x', pady=(0, 5))

        today = datetime.now().strftime('%Y-%m-%d')

        # --- Start ---
        start_frame = tk.Frame(filter_frame, bg='white')
        start_frame.pack(side=i18n.side_start(), padx=10, pady=6)
        tk.Label(start_frame, text=t("lbl.from"), bg='white',
                 font=FONT_BODY).pack(side=i18n.side_start())

        self.start_date = tk.Entry(start_frame, width=10, font=FONT_BODY,
                                   justify=i18n.justify_text())
        self.start_date.pack(side=i18n.side_start(), padx=2)
        self.start_date.insert(0, today)

        self.start_time = tk.Entry(start_frame, width=5, font=FONT_BODY,
                                   justify=i18n.justify_text())
        self.start_time.pack(side=i18n.side_start(), padx=2)
        self.start_time.insert(0, '00:00')

        # --- End ---
        end_frame = tk.Frame(filter_frame, bg='white')
        end_frame.pack(side=i18n.side_start(), padx=10, pady=6)
        tk.Label(end_frame, text=t("lbl.to"), bg='white',
                 font=FONT_BODY).pack(side=i18n.side_start())

        self.end_date = tk.Entry(end_frame, width=10, font=FONT_BODY,
                                 justify=i18n.justify_text())
        self.end_date.pack(side=i18n.side_start(), padx=2)
        self.end_date.insert(0, today)

        self.end_time = tk.Entry(end_frame, width=5, font=FONT_BODY,
                                 justify=i18n.justify_text())
        self.end_time.pack(side=i18n.side_start(), padx=2)
        self.end_time.insert(0, '23:59')

        tk.Button(filter_frame, text=t("btn.filter"), bg='#3498db', fg='white',
                  font=FONT_BODY, command=self.filter_sales
                  ).pack(side=i18n.side_start(), padx=5)
        tk.Button(filter_frame, text=t("btn.clear_filter"), bg='#95a5a6', fg='white',
                  font=FONT_BODY, command=self.clear_filter
                  ).pack(side=i18n.side_start(), padx=5)
        tk.Button(filter_frame, text=t("btn.refresh"), bg='#3498db', fg='white',
                  font=FONT_BODY, width=2, command=self.refresh
                  ).pack(side=i18n.side_start(), padx=5)
        tk.Button(filter_frame, text=t("btn.verify"), bg='#f39c12', fg='white',
                  font=FONT_BODY, command=self.verify_sales
                  ).pack(side=i18n.side_start(), padx=5)

        summary_frame = tk.Frame(filter_frame, bg='white')
        summary_frame.pack(side=i18n.side_end(), padx=10, pady=6)
        self.total_sales_label = tk.Label(summary_frame,
                                          text=f'{t("lbl.total")}: 0 DT',
                                          bg='white', font=FONT_BOLD)
        self.total_sales_label.pack(side=i18n.side_start(), padx=5)
        self.total_profit_label = tk.Label(summary_frame,
                                           text=f'{t("lbl.profit")}: 0 DT',
                                           bg='white', font=FONT_BOLD,
                                           fg='#27ae60')
        self.total_profit_label.pack(side=i18n.side_start(), padx=5)
        self.trans_count_label = tk.Label(summary_frame,
                                          text=f'{t("lbl.sales_count")}: 0',
                                          bg='white', font=FONT_BOLD)
        self.trans_count_label.pack(side=i18n.side_start(), padx=5)

        tree_container = tk.Frame(main, bg='white', relief='groove', bd=1)
        tree_container.pack(fill='both', expand=True)

        columns = ('date', 'time', 'count', 'total', 'profit')
        self.tree = ttk.Treeview(tree_container, columns=columns,
                                 show='headings',
                                 selectmode='extended', height=20)
        headings = [
            t("history.col_date"), t("history.col_time"),
            t("history.col_count"), t("history.col_total"),
            t("history.col_profit"),
        ]
        col_widths = [110, 70, 70, 110, 110]
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

        if auth.can(self.user, "soft_delete_sale"):
            tk.Button(btn_frame, text=t("history.btn_soft_delete"),
                      bg='#e67e22', fg='white',
                      font=self._font(10), width=18,
                      command=self.delete_selected_soft
                      ).pack(side=i18n.side_start(), padx=5)

        if auth.can(self.user, "hard_delete_sale"):
            tk.Button(btn_frame, text=t("history.btn_hard_delete"),
                      bg='#e74c3c', fg='white',
                      font=self._font(10), width=22,
                      command=self.delete_selected_hard
                      ).pack(side=i18n.side_start(), padx=5)

        tk.Button(btn_frame, text=t("btn.details_sale"), bg='#3498db', fg='white',
                  font=self._font(10), width=15,
                  command=self.show_details_selected
                  ).pack(side=i18n.side_start(), padx=5)

        tk.Label(btn_frame, text=t("history.hint"),
                 bg='#f0f0f0', fg='#e67e22',
                 font=FONT_BODY).pack(side=i18n.side_end(), padx=5)

    # ------------------------------------------------------------------
    def load_history(self, start_dt=None, end_dt=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        self._active_range = (start_dt, end_dt)
        groups = db.get_grouped_sales(start_dt, end_dt)

        total_amount = 0.0
        total_profit = 0.0

        for timestamp, count, amount, profit in groups:
            date_part = timestamp[:10]
            time_part = timestamp[11:16] if len(timestamp) > 16 else timestamp[11:]

            self.tree.insert('', 'end', values=(
                date_part, time_part, count,
                f"{amount:.2f}", f"{profit:.2f}",
            ), tags=(timestamp,))

            total_amount += amount
            total_profit += profit

        self.total_sales_label.config(
            text=f'{t("lbl.total")}: {total_amount:.2f} DT')
        self.total_profit_label.config(
            text=f'{t("lbl.profit")}: {total_profit:.2f} DT')
        self.trans_count_label.config(
            text=f'{t("lbl.sales_count")}: {len(groups)}')

    def filter_sales(self):
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

        self.load_history(start_str, end_str)

    def clear_filter(self):
        today = datetime.now().strftime('%Y-%m-%d')
        for entry, value in (
            (self.start_date, today), (self.start_time, '00:00'),
            (self.end_date, today),   (self.end_time, '23:59'),
        ):
            entry.delete(0, tk.END)
            entry.insert(0, value)
        self.filter_sales()

    def refresh(self):
        self.load_history(*self._active_range)

    # ------------------------------------------------------------------
    def get_selected_timestamps(self):
        timestamps = []
        for item in self.tree.selection():
            tags = self.tree.item(item, 'tags')
            if tags:
                timestamps.append(tags[0])
        return timestamps

    # ------------------------------------------------------------------
    def delete_selected_soft(self):
        if not auth.can(self.user, "soft_delete_sale"):
            messagebox.showerror(t("msg.access_denied"), t("msg.no_permission"))
            return

        timestamps = self.get_selected_timestamps()
        if not timestamps:
            messagebox.showwarning(t("msg.warning"),
                                   t("history.select_to_delete"))
            return

        if not messagebox.askyesno(
            t("msg.confirmation"),
            t("history.confirm_soft", n=len(timestamps))
        ):
            return

        errors = []
        for ts in timestamps:
            try:
                db.soft_delete_sales_by_timestamp(ts, self.user['id'])
            except Exception as e:
                errors.append(f"{ts}: {e}")

        if errors:
            messagebox.showerror(t("msg.error"), '\n'.join(errors[:5]))
        else:
            messagebox.showinfo(t("msg.success"),
                                t("history.deleted_ok", n=len(timestamps)))

        self.refresh()

    def delete_selected_hard(self):
        if not auth.can(self.user, "hard_delete_sale"):
            messagebox.showerror(t("msg.access_denied"),
                                 t("history.owner_only_hard"))
            return

        timestamps = self.get_selected_timestamps()
        if not timestamps:
            messagebox.showwarning(t("msg.warning"),
                                   t("history.select_to_delete"))
            return

        if not messagebox.askyesno(
            t("msg.confirmation"),
            t("history.confirm_hard", n=len(timestamps))
        ):
            return

        errors = []
        for ts in timestamps:
            try:
                db.hard_delete_sales_by_timestamp(ts)
            except Exception as e:
                errors.append(f"{ts}: {e}")

        if errors:
            messagebox.showerror(t("msg.error"), '\n'.join(errors[:5]))
        else:
            messagebox.showinfo(t("msg.success"),
                                t("history.deleted_ok", n=len(timestamps)))

        self.refresh()

    # ------------------------------------------------------------------
    def show_details_selected(self):
        timestamps = self.get_selected_timestamps()
        if not timestamps:
            messagebox.showwarning(t("msg.warning"), t("history.select_sale"))
            return
        self.show_details_for_timestamp(timestamps[0])

    def view_details(self, event=None):
        selected = self.tree.selection()
        if selected:
            ts = self.tree.item(selected[0], 'tags')[0]
            self.show_details_for_timestamp(ts)

    def show_details_for_timestamp(self, timestamp):
        sales = db.get_sales_by_timestamp(timestamp)
        if not sales:
            messagebox.showinfo(t("msg.info"), t("history.no_items"))
            return

        popup = tk.Toplevel(self.root)
        popup.title(t("history.details_title", ts=timestamp))
        popup.geometry("620x500")
        popup.transient(self.root)
        popup.update_idletasks()
        popup.grab_set()

        tk.Label(popup, text=t("history.sale_of", ts=timestamp),
                 font=self._font(12, 'bold')).pack(pady=6)

        columns = ('id', 'product', 'qty', 'unit', 'total', 'profit')
        tree = ttk.Treeview(popup, columns=columns, show='headings', height=10)
        headings = {
            'id': (t("history.col_id"), 0),
            'product': (t("history.col_product"), 220),
            'qty': (t("history.col_qty"), 80),
            'unit': (t("history.col_unit"), 70),
            'total': (t("history.col_total"), 80),
            'profit': (t("history.col_profit"), 80),
        }
        for col, (label, width) in headings.items():
            tree.heading(col, text=label)
            tree.column(col, width=width,
                        anchor='center' if col != 'product' else i18n.anchor_start(),
                        stretch=(col == 'product'))
        tree.pack(fill='both', expand=True, padx=10, pady=(0, 5))

        summary = tk.Frame(popup)
        summary.pack(fill='x', padx=10, pady=5)
        total_lbl = tk.Label(summary, text="", font=self._font(10, 'bold'))
        total_lbl.pack(side=i18n.side_start(), padx=10)
        profit_lbl = tk.Label(summary, text="", font=self._font(10, 'bold'),
                              fg='#27ae60')
        profit_lbl.pack(side=i18n.side_start(), padx=10)

        def rebuild():
            for row in tree.get_children():
                tree.delete(row)
            rows = db.get_sales_by_timestamp(timestamp)
            tot = 0.0
            prof = 0.0
            for sale_id, product, qty, unit, total, profit in rows:
                qty_str = (f"{qty:.0f} g" if unit in ('gram', 'g')
                           else f"{qty:.0f}")
                tree.insert('', 'end', values=(
                    sale_id, product[:34], qty_str, unit,
                    f"{total:.2f} DT", f"{profit:.2f} DT",
                ))
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

        btn_frame = tk.Frame(popup)
        btn_frame.pack(fill='x', padx=10, pady=(0, 8))

        def delete_selected_item():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning(t("msg.warning"),
                                       t("deleted.select_item"), parent=popup)
                return
            sale_id = tree.item(selected[0])['values'][0]

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
                    db.soft_delete_sale(sale_id, self.user['id'])
                except Exception as e:
                    messagebox.showerror(t("msg.error"), str(e), parent=popup)
                    return
            else:
                messagebox.showerror(t("msg.access_denied"),
                                     t("msg.no_permission"), parent=popup)
                return
            self.refresh()
            rebuild()

        if auth.can(self.user, "soft_delete_sale"):
            label = (t("history.btn_hard_delete")
                     if auth.can(self.user, "hard_delete_sale")
                     else t("history.delete_item"))
            tk.Button(btn_frame, text=label,
                      bg='#e74c3c', fg='white',
                      command=delete_selected_item
                      ).pack(side=i18n.side_start(), padx=5)

        tk.Button(btn_frame, text=t("btn.close"), bg='#95a5a6', fg='white',
                  command=popup.destroy).pack(side=i18n.side_end(), padx=5)

    # ------------------------------------------------------------------
    def verify_sales(self):
        all_total, all_profit, grouped_total, grouped_profit = \
            db.verify_sales_aggregates()
        ok = abs(all_total - grouped_total) < 0.01
        messagebox.showinfo(
            t("history.verify_title"),
            t("history.verify_total", t=all_total) + "\n"
            + t("history.verify_grouped", t=grouped_total) + "\n"
            + t("history.verify_profit", p=all_profit) + "\n"
            + t("history.verify_grouped_profit", p=grouped_profit) + "\n\n"
            + (t("history.verify_ok") if ok else t("history.verify_bad"))
        )

    # ------------------------------------------------------------------
    def show(self):
        self.frame.pack(fill='both', expand=True)
        self.refresh()

    def hide(self):
        self.frame.pack_forget()
