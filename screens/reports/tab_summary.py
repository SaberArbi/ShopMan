"""Sales summary tab."""
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from app import theme
from database import db
from utils import i18n
from utils.i18n import t

MONO_FONT = "TkFixedFont"


class SummaryTab(ttk.Frame):
    def __init__(self, parent, screen):
        super().__init__(parent)
        self.screen = screen

        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        box = ttk.LabelFrame(main, text=t("reports.period"), padding=10)
        box.pack(fill="x", pady=5)

        today = datetime.now().strftime("%Y-%m-%d")
        self.start_date = self._field(box, 0, t("lbl.from"), 12, today)
        self.start_time = self._field(box, 0, None, 6, "00:00", col=2)
        self.end_date = self._field(box, 1, t("lbl.to"), 12, today)
        self.end_time = self._field(box, 1, None, 6, "23:59", col=2)

        btns = ttk.Frame(box)
        btns.grid(row=2, column=0, columnspan=3, pady=10)
        ttk.Button(btns, text=t("reports.load_summary"),
                   command=self.load).pack(side="left", padx=5)
        ttk.Button(btns, text=t("reports.today"),
                   command=self.set_today).pack(side="left", padx=5)

        wrap = ttk.Frame(main)
        wrap.pack(fill="both", expand=True, pady=10)
        self.text = tk.Text(wrap, height=10, bg=theme.BG_INPUT, fg=theme.FG,
                            insertbackground=theme.FG, font=MONO_FONT,
                            relief="sunken", bd=1, wrap="none")
        v = ttk.Scrollbar(wrap, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=v.set)
        self.text.pack(side="left", fill="both", expand=True)
        v.pack(side="right", fill="y")

    def _field(self, parent, row, label, width, default, col=1):
        if label:
            ttk.Label(parent, text=label).grid(row=row, column=0,
                                                sticky="e", padx=5, pady=5)
        e = ttk.Entry(parent, width=width, justify=i18n.justify_text())
        e.grid(row=row, column=col, padx=5, pady=5)
        e.insert(0, default)
        return e

    def set_today(self):
        today = datetime.now().strftime("%Y-%m-%d")
        for e, v in ((self.start_date, today), (self.start_time, "00:00"),
                     (self.end_date, today), (self.end_time, "23:59")):
            e.delete(0, tk.END)
            e.insert(0, v)

    def load(self):
        try:
            start = f"{self.start_date.get().strip()} {self.start_time.get().strip()}:00"
            end = f"{self.end_date.get().strip()} {self.end_time.get().strip()}:59"
            datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror(t("msg.error"), t("reports.invalid_datetime"))
            return
        if start > end:
            messagebox.showerror(t("msg.error"), t("reports.start_after_end"))
            return

        total, profit, count = db.get_period_summary_datetime(start, end)
        self.text.delete(1.0, tk.END)
        self.text.insert(1.0, (
            f"{'=' * 52}\n"
            f"  {t('reports.summary_header', start=start, end=end)}\n"
            f"{'=' * 52}\n"
            f"  {t('reports.total_sales')}      : {total:>14.2f} DT\n"
            f"  {t('reports.total_profit')}    : {profit:>14.2f} DT\n"
            f"  {t('reports.transactions')}      : {count:>14}\n"
            f"{'=' * 52}\n"
        ))