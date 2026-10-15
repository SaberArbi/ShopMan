# screens/reports.py
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

from database import db_operations as db
from utils import auth, last_report, i18n
from utils.i18n import t


LOW_STOCK_REPORT_CAP = 40

MONO_FONT = "TkFixedFont"

TEXT_BG = '#f8f9fa'
TEXT_FG = '#2c3e50'


class ReportsScreen:
    def __init__(self, root, switch_callback, user=None):
        self.root = root
        self.switch = switch_callback
        self.user = user
        self.frame = tk.Frame(root, bg='#f0f0f0')
        self.low_stock_threshold = 10

        self.setup_ui()

    def _font(self, size, weight="normal"):
        return i18n.ui_font(size, weight)

    def setup_ui(self):
        FONT_TITLE = self._font(13, 'bold')
        FONT_BOLD  = self._font(10, 'bold')
        FONT_BODY  = self._font(10)
        FONT_SMALL = self._font(9)

        top = tk.Frame(self.frame, bg='#8e44ad', height=55)
        top.pack(fill='x')
        top.pack_propagate(False)

        # ---- Start side ----
        left_btns = tk.Frame(top, bg='#8e44ad')
        left_btns.pack(side=i18n.side_start(), padx=8, pady=8)

        if auth.can(self.user, "sell"):
            tk.Button(left_btns, text=t("nav.back_to_sales"), bg='#9b59b6', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('sales')
                      ).pack(side=i18n.side_start(), padx=3)
        if auth.can(self.user, "view_history"):
            tk.Button(left_btns, text=t("nav.history"), bg='#9b59b6', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('history')
                      ).pack(side=i18n.side_start(), padx=3)
        if auth.can(self.user, "view_deleted_sales"):
            tk.Button(left_btns, text=t("history.deleted_btn"), bg='#7f1d1d', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('deleted')
                      ).pack(side=i18n.side_start(), padx=3)

        tk.Label(top, text=t("reports.title"), bg='#8e44ad', fg='white',
                 font=FONT_TITLE).pack(side='top', pady=10)

        # ---- End side ----
        right_btns = tk.Frame(top, bg='#8e44ad')
        right_btns.pack(side=i18n.side_end(), padx=8, pady=8)

        if auth.can(self.user, "manage_products"):
            tk.Button(right_btns, text=t("nav.products_arrow"), bg='#9b59b6', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('products')
                      ).pack(side=i18n.side_end(), padx=3)
        if auth.can(self.user, "manage_users"):
            tk.Button(right_btns, text=t("nav.users"), bg='#9b59b6', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('users')
                      ).pack(side=i18n.side_end(), padx=3)

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        self.tab_summary = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_summary, text=t("reports.tab_summary"))
        self.setup_summary_tab()

        self.tab_products = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_products, text=t("reports.tab_products"))
        self.setup_products_tab()

        self.tab_stock = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_stock, text=t("reports.tab_stock"))
        self.setup_stock_tab()

        self.tab_export = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_export, text=t("reports.tab_export"))
        self.setup_export_tab()

    # ----- Summary tab -----
    def setup_summary_tab(self):
        main = ttk.Frame(self.tab_summary, padding=10)
        main.pack(fill='both', expand=True)

        box = ttk.LabelFrame(main, text=t("reports.period"), padding=10)
        box.pack(fill='x', pady=5)

        ttk.Label(box, text=t("lbl.from")).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.sum_start_date = ttk.Entry(box, width=12, justify=i18n.justify_text())
        self.sum_start_date.grid(row=0, column=1, padx=5, pady=5)
        self.sum_start_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.sum_start_time = ttk.Entry(box, width=6, justify=i18n.justify_text())
        self.sum_start_time.grid(row=0, column=2, padx=5, pady=5)
        self.sum_start_time.insert(0, '00:00')

        ttk.Label(box, text=t("lbl.to")).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.sum_end_date = ttk.Entry(box, width=12, justify=i18n.justify_text())
        self.sum_end_date.grid(row=1, column=1, padx=5, pady=5)
        self.sum_end_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.sum_end_time = ttk.Entry(box, width=6, justify=i18n.justify_text())
        self.sum_end_time.grid(row=1, column=2, padx=5, pady=5)
        self.sum_end_time.insert(0, '23:59')

        btns = ttk.Frame(box)
        btns.grid(row=2, column=0, columnspan=3, pady=10)
        ttk.Button(btns, text=t("reports.load_summary"),
                   command=self.load_summary).pack(side='left', padx=5)
        ttk.Button(btns, text=t("reports.today"),
                   command=self.set_today_summary).pack(side='left', padx=5)

        text_wrap = ttk.Frame(main)
        text_wrap.pack(fill='both', expand=True, pady=10)
        self.summary_text = tk.Text(text_wrap, height=10,
                                    bg=TEXT_BG, fg=TEXT_FG,
                                    insertbackground=TEXT_FG,
                                    font=MONO_FONT,
                                    relief='sunken', bd=1, wrap='none')
        vbar = ttk.Scrollbar(text_wrap, orient='vertical',
                             command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=vbar.set)
        self.summary_text.pack(side='left', fill='both', expand=True)
        vbar.pack(side='right', fill='y')

    def set_today_summary(self):
        today = datetime.now().strftime('%Y-%m-%d')
        for entry, value in (
            (self.sum_start_date, today), (self.sum_start_time, '00:00'),
            (self.sum_end_date, today),   (self.sum_end_time, '23:59'),
        ):
            entry.delete(0, tk.END)
            entry.insert(0, value)

    def load_summary(self):
        try:
            start = f"{self.sum_start_date.get().strip()} {self.sum_start_time.get().strip()}:00"
            end = f"{self.sum_end_date.get().strip()} {self.sum_end_time.get().strip()}:59"
            datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror(t("msg.error"), t("reports.invalid_datetime"))
            return

        if start > end:
            messagebox.showerror(t("msg.error"), t("reports.start_after_end"))
            return

        total, profit, count = db.get_period_summary_datetime(start, end)

        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(1.0, (
            f"{'=' * 52}\n"
            f"  {t('reports.summary_header', start=start, end=end)}\n"
            f"{'=' * 52}\n"
            f"  {t('reports.total_sales')}      : {total:>14.2f} DT\n"
            f"  {t('reports.total_profit')}    : {profit:>14.2f} DT\n"
            f"  {t('reports.transactions')}      : {count:>14}\n"
            f"{'=' * 52}\n"
        ))

    # ----- Top products tab -----
    def setup_products_tab(self):
        FONT_BOLD = self._font(10, 'bold')
        FONT_BODY = self._font(10)

        main = ttk.Frame(self.tab_products, padding=10)
        main.pack(fill='both', expand=True)

        box = ttk.LabelFrame(main, text=t("reports.period_optional"), padding=10)
        box.pack(fill='x', pady=5)

        ttk.Label(box, text=t("lbl.from")).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.prod_start_date = ttk.Entry(box, width=12, justify=i18n.justify_text())
        self.prod_start_date.grid(row=0, column=1, padx=5, pady=5)
        self.prod_start_time = ttk.Entry(box, width=6, justify=i18n.justify_text())
        self.prod_start_time.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(box, text=t("lbl.to")).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.prod_end_date = ttk.Entry(box, width=12, justify=i18n.justify_text())
        self.prod_end_date.grid(row=1, column=1, padx=5, pady=5)
        self.prod_end_time = ttk.Entry(box, width=6, justify=i18n.justify_text())
        self.prod_end_time.grid(row=1, column=2, padx=5, pady=5)

        limit_frame = ttk.Frame(box)
        limit_frame.grid(row=2, column=0, columnspan=3, pady=5)
        ttk.Label(limit_frame, text=t("reports.num_products")).pack(side='left', padx=5)
        self.prod_limit = ttk.Entry(limit_frame, width=5, justify='center')
        self.prod_limit.pack(side='left', padx=5)
        self.prod_limit.insert(0, '10')

        btns = ttk.Frame(box)
        btns.grid(row=3, column=0, columnspan=3, pady=10)
        ttk.Button(btns, text=t("reports.load_top"),
                   command=self.load_top_products).pack(side='left', padx=5)
        ttk.Button(btns, text=t("reports.clear_period"),
                   command=self.clear_top_products_period).pack(side='left', padx=5)

        columns = ('product', 'qty', 'revenue', 'profit')
        headings = [t("reports.col_product"), t("reports.col_qty"),
                    t("reports.col_revenue"), t("reports.col_profit")]

        style = ttk.Style()
        style.configure('Reports.Treeview',
                        background='white', foreground='black',
                        fieldbackground='white',
                        font=FONT_BODY, rowheight=26)
        style.configure('Reports.Treeview.Heading',
                        font=FONT_BOLD, background='#ecf0f1',
                        foreground='black')

        tree_wrap = ttk.Frame(main)
        tree_wrap.pack(fill='both', expand=True, pady=10)
        self.products_tree = ttk.Treeview(tree_wrap, columns=columns,
                                          show='headings', height=15,
                                          style='Reports.Treeview')
        for col, hdr in zip(columns, headings):
            self.products_tree.heading(col, text=hdr)
            self.products_tree.column(
                col,
                width=200 if col == 'product' else 110,
                anchor=(i18n.anchor_start() if col == 'product' else 'center'))
        vbar = ttk.Scrollbar(tree_wrap, orient='vertical',
                             command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=vbar.set)
        self.products_tree.pack(side='left', fill='both', expand=True)
        vbar.pack(side='right', fill='y')

    def clear_top_products_period(self):
        for e in (self.prod_start_date, self.prod_start_time,
                  self.prod_end_date, self.prod_end_time):
            e.delete(0, tk.END)

    def load_top_products(self):
        for row in self.products_tree.get_children():
            self.products_tree.delete(row)

        try:
            limit = int(self.prod_limit.get() or '10')
        except ValueError:
            limit = 10

        start_dt = end_dt = None
        if self.prod_start_date.get().strip() and self.prod_start_time.get().strip():
            try:
                start_dt = f"{self.prod_start_date.get().strip()} {self.prod_start_time.get().strip()}:00"
                datetime.strptime(start_dt, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror(t("msg.error"), t("reports.invalid_datetime"))
                return

        if self.prod_end_date.get().strip() and self.prod_end_time.get().strip():
            try:
                end_dt = f"{self.prod_end_date.get().strip()} {self.prod_end_time.get().strip()}:59"
                datetime.strptime(end_dt, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror(t("msg.error"), t("reports.invalid_datetime"))
                return

        if start_dt and end_dt and start_dt > end_dt:
            messagebox.showerror(t("msg.error"), t("reports.start_after_end"))
            return

        for name, qty, revenue, profit in db.get_top_products_datetime(limit, start_dt, end_dt):
            self.products_tree.insert('', 'end', values=(
                name[:45], f"{qty:g}", f"{revenue:.2f}", f"{profit:.2f}",
            ))

    # ----- Stock tab -----
    def setup_stock_tab(self):
        main = ttk.Frame(self.tab_stock, padding=10)
        main.pack(fill='both', expand=True)

        ctrl = ttk.Frame(main)
        ctrl.pack(fill='x', pady=5)
        ttk.Label(ctrl, text=t("reports.low_stock_threshold")).pack(side='left', padx=5)
        self.threshold_entry = ttk.Entry(ctrl, width=5, justify='center')
        self.threshold_entry.pack(side='left', padx=5)
        self.threshold_entry.insert(0, str(self.low_stock_threshold))
        ttk.Button(ctrl, text=t("reports.refresh_btn"),
                   command=self.load_stock).pack(side='left', padx=10)

        text_wrap = ttk.Frame(main)
        text_wrap.pack(fill='both', expand=True, pady=10)
        self.stock_text = tk.Text(text_wrap, height=15,
                                  bg=TEXT_BG, fg=TEXT_FG,
                                  insertbackground=TEXT_FG,
                                  font=MONO_FONT,
                                  relief='sunken', bd=1, wrap='none')
        vbar = ttk.Scrollbar(text_wrap, orient='vertical',
                             command=self.stock_text.yview)
        self.stock_text.configure(yscrollcommand=vbar.set)
        self.stock_text.pack(side='left', fill='both', expand=True)
        vbar.pack(side='right', fill='y')

    def _current_threshold(self):
        try:
            value = int(self.threshold_entry.get())
            if value < 0:
                raise ValueError
            return value
        except (ValueError, AttributeError):
            return self.low_stock_threshold

    def load_stock(self):
        threshold = self._current_threshold()
        self.low_stock_threshold = threshold

        total_value, low_stock = db.get_stock_status(threshold)

        self.stock_text.delete(1.0, tk.END)
        self.stock_text.insert(1.0,
            t("reports.stock_value", v=total_value) + "\n\n"
            + t("reports.low_stock_header", t=threshold) + "\n")
        if low_stock:
            for name, stock, unit in low_stock:
                self.stock_text.insert(
                    tk.END,
                    f"  • {name} : {stock:g} {t(f'unit.{unit}')}\n")
        else:
            self.stock_text.insert(tk.END, t("reports.no_low_stock") + "\n")

    # ----- Export tab -----
    def setup_export_tab(self):
        main = ttk.Frame(self.tab_export, padding=10)
        main.pack(fill='both', expand=True)

        box = ttk.LabelFrame(main, text=t("reports.report_period"), padding=10)
        box.pack(fill='x', pady=5)

        ttk.Label(box, text=t("lbl.from")).grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.export_start_date = ttk.Entry(box, width=12, justify=i18n.justify_text())
        self.export_start_date.grid(row=0, column=1, padx=5, pady=5)
        self.export_start_date.insert(
            0, (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'))
        self.export_start_time = ttk.Entry(box, width=6, justify=i18n.justify_text())
        self.export_start_time.grid(row=0, column=2, padx=5, pady=5)
        self.export_start_time.insert(0, '00:00')

        ttk.Label(box, text=t("lbl.to")).grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.export_end_date = ttk.Entry(box, width=12, justify=i18n.justify_text())
        self.export_end_date.grid(row=1, column=1, padx=5, pady=5)
        self.export_end_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.export_end_time = ttk.Entry(box, width=6, justify=i18n.justify_text())
        self.export_end_time.grid(row=1, column=2, padx=5, pady=5)
        self.export_end_time.insert(0, '23:59')

        btns = ttk.Frame(box)
        btns.grid(row=2, column=0, columnspan=3, pady=10)
        ttk.Button(btns, text=t("reports.generate"),
                   command=self.generate_report).pack(side='left', padx=5)
        ttk.Button(btns, text=t("reports.from_last"),
                   command=self.set_from_last_report).pack(side='left', padx=5)
        ttk.Button(btns, text=t("reports.open_folder"),
                   command=self.open_reports_folder).pack(side='left', padx=5)

        preview_wrap = ttk.LabelFrame(main, text=t("reports.preview"), padding=5)
        preview_wrap.pack(fill='both', expand=True, pady=10)

        inner = ttk.Frame(preview_wrap)
        inner.pack(fill='both', expand=True)

        self.preview_text = tk.Text(inner, height=14,
                                    bg=TEXT_BG, fg=TEXT_FG,
                                    insertbackground=TEXT_FG,
                                    font=MONO_FONT,
                                    wrap='none')
        vbar = ttk.Scrollbar(inner, orient='vertical',
                             command=self.preview_text.yview)
        hbar = ttk.Scrollbar(inner, orient='horizontal',
                             command=self.preview_text.xview)
        self.preview_text.configure(yscrollcommand=vbar.set,
                                    xscrollcommand=hbar.set)

        self.preview_text.grid(row=0, column=0, sticky='nsew')
        vbar.grid(row=0, column=1, sticky='ns')
        hbar.grid(row=1, column=0, sticky='ew')

        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)

    def set_from_last_report(self):
        last_end = last_report.load_last_report()
        if not last_end:
            messagebox.showinfo(t("msg.info"), t("reports.no_previous"))
            return

        try:
            dt = datetime.strptime(last_end, "%Y-%m-%d %H:%M:%S") + timedelta(seconds=1)
        except ValueError:
            messagebox.showerror(t("msg.error"), t("reports.corrupt_last"))
            return

        now = datetime.now()

        self.export_start_date.delete(0, tk.END)
        self.export_start_date.insert(0, dt.strftime('%Y-%m-%d'))
        self.export_start_time.delete(0, tk.END)
        self.export_start_time.insert(0, dt.strftime('%H:%M'))

        self.export_end_date.delete(0, tk.END)
        self.export_end_date.insert(0, now.strftime('%Y-%m-%d'))
        self.export_end_time.delete(0, tk.END)
        self.export_end_time.insert(0, now.strftime('%H:%M'))

    def open_reports_folder(self):
        reports_dir = self._reports_dir()
        if not os.path.exists(reports_dir):
            messagebox.showinfo(t("msg.info"), t("reports.no_reports_yet"))
            return
        try:
            if sys.platform.startswith('linux'):
                subprocess.Popen(['xdg-open', reports_dir])
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', reports_dir])
            else:
                os.startfile(reports_dir)  # noqa: S606
        except Exception as e:
            messagebox.showerror(t("msg.error"), t("reports.cannot_open", e=e))

    def _reports_dir(self):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)),
                            'reports')

    def generate_report(self):
        try:
            start_dt = f"{self.export_start_date.get().strip()} {self.export_start_time.get().strip()}:00"
            end_dt = f"{self.export_end_date.get().strip()} {self.export_end_time.get().strip()}:59"
            datetime.strptime(start_dt, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(end_dt, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror(t("msg.error"), t("reports.invalid_datetime"))
            return

        if start_dt > end_dt:
            messagebox.showerror(t("msg.error"), t("reports.start_after_end"))
            return

        total, profit, count = db.get_period_summary_datetime(start_dt, end_dt)
        top_products = db.get_top_products_datetime(10, start_dt, end_dt)
        threshold = self._current_threshold()
        self.low_stock_threshold = threshold
        total_value, low_stock = db.get_stock_status(threshold)

        lines = []
        lines.append("=" * 70)
        lines.append(t("reports.report_title"))
        lines.append("=" * 70)
        lines.append(t("reports.report_from", d=start_dt))
        lines.append(t("reports.report_to", d=end_dt))
        lines.append(t("reports.report_generated",
                       d=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        lines.append(t("reports.report_by",
                       u=self.user['username'] if self.user else '?'))
        lines.append("")
        lines.append(t("reports.report_sales_summary"))
        lines.append("-" * 50)
        lines.append(t("reports.report_total_sales", v=total))
        lines.append(t("reports.report_total_profit", v=profit))
        lines.append(t("reports.report_num_trans", n=count))
        lines.append("")
        lines.append(t("reports.report_top10"))
        lines.append("-" * 50)

        if top_products:
            for i, (name, qty, revenue, prof) in enumerate(top_products, 1):
                lines.append(
                    f"{i:>2}. {name[:32]:32}  "
                    f"{qty:>6g} pcs  "
                    f"{revenue:>9.2f} DT  "
                    f"{prof:>9.2f} DT"
                )
        else:
            lines.append(t("reports.report_no_sales"))

        lines.append("")
        lines.append(t("reports.report_stock"))
        lines.append("-" * 50)
        lines.append(t("reports.report_stock_value", v=total_value))
        lines.append("")
        lines.append(t("reports.report_low_stock", t=threshold))

        if not low_stock:
            lines.append(t("reports.report_none"))
        else:
            for name, stock, unit in low_stock[:LOW_STOCK_REPORT_CAP]:
                lines.append(f"  • {name} : {stock:g} {t(f'unit.{unit}')}")
            hidden = len(low_stock) - LOW_STOCK_REPORT_CAP
            if hidden > 0:
                lines.append(t("reports.report_hidden", n=hidden))

        lines.append("")
        lines.append("=" * 70)
        lines.append(t("reports.report_success"))
        lines.append("=" * 70)
        lines.append("")

        report = "\n".join(lines)

        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, report)

        reports_dir = self._reports_dir()
        os.makedirs(reports_dir, exist_ok=True)

        safe_start = start_dt.replace(' ', '_').replace(':', '')
        safe_end = end_dt.replace(' ', '_').replace(':', '')
        filename = f"rapport_{safe_start}_{safe_end}.txt"
        filepath = os.path.join(reports_dir, filename)

        counter = 1
        while os.path.exists(filepath):
            filepath = os.path.join(
                reports_dir, f"rapport_{safe_start}_{safe_end}_{counter}.txt")
            counter += 1

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
        except OSError as e:
            messagebox.showerror(t("msg.error"),
                                 t("reports.cannot_write", e=e))
            return

        last_report.save_last_report(end_dt)

        messagebox.showinfo(t("msg.success"),
                            t("reports.report_saved", path=filepath))

    def show(self):
        self.frame.pack(fill='both', expand=True)

    def hide(self):
        self.frame.pack_forget()
