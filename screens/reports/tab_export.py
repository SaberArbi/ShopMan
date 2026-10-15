"""Export report tab — generate, save, preview."""
import os
import subprocess
import sys
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

from app import theme
from database import db
from utils import i18n, last_report
from utils.i18n import t

MONO_FONT = "TkFixedFont"
LOW_STOCK_REPORT_CAP = 40


class ExportTab(ttk.Frame):
    def __init__(self, parent, screen):
        super().__init__(parent)
        self.screen = screen

        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        box = ttk.LabelFrame(main, text=t("reports.report_period"), padding=10)
        box.pack(fill="x", pady=5)

        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        self.start_date = self._field(box, 0, t("lbl.from"), 12, week_ago)
        self.start_time = self._field(box, 0, None, 6, "00:00", col=2)
        self.end_date = self._field(box, 1, t("lbl.to"), 12, today)
        self.end_time = self._field(box, 1, None, 6, "23:59", col=2)

        btns = ttk.Frame(box)
        btns.grid(row=2, column=0, columnspan=3, pady=10)
        ttk.Button(btns, text=t("reports.generate"),
                   command=self.generate).pack(side="left", padx=5)
        ttk.Button(btns, text=t("reports.from_last"),
                   command=self.set_from_last).pack(side="left", padx=5)
        ttk.Button(btns, text=t("reports.open_folder"),
                   command=self.open_folder).pack(side="left", padx=5)

        wrap = ttk.LabelFrame(main, text=t("reports.preview"), padding=5)
        wrap.pack(fill="both", expand=True, pady=10)
        inner = ttk.Frame(wrap)
        inner.pack(fill="both", expand=True)

        self.preview = tk.Text(inner, height=14, bg=theme.BG_INPUT, fg=theme.FG,
                               insertbackground=theme.FG, font=MONO_FONT,
                               wrap="none")
        v = ttk.Scrollbar(inner, orient="vertical", command=self.preview.yview)
        h = ttk.Scrollbar(inner, orient="horizontal", command=self.preview.xview)
        self.preview.configure(yscrollcommand=v.set, xscrollcommand=h.set)
        self.preview.grid(row=0, column=0, sticky="nsew")
        v.grid(row=0, column=1, sticky="ns")
        h.grid(row=1, column=0, sticky="ew")
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)

    def _field(self, parent, row, label, width, default, col=1):
        if label:
            ttk.Label(parent, text=label).grid(row=row, column=0,
                                                sticky="e", padx=5, pady=5)
        e = ttk.Entry(parent, width=width, justify=i18n.justify_text())
        e.grid(row=row, column=col, padx=5, pady=5)
        e.insert(0, default)
        return e

    # ------------------------------------------------------------------
    @staticmethod
    def _reports_dir() -> str:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))), "reports")

    def set_from_last(self):
        last_end = last_report.load_last_report()
        if not last_end:
            messagebox.showinfo(t("msg.info"), t("reports.no_previous"))
            return
        try:
            dt = (datetime.strptime(last_end, "%Y-%m-%d %H:%M:%S")
                  + timedelta(seconds=1))
        except ValueError:
            messagebox.showerror(t("msg.error"), t("reports.corrupt_last"))
            return
        now = datetime.now()
        for e, v in ((self.start_date, dt.strftime("%Y-%m-%d")),
                     (self.start_time, dt.strftime("%H:%M")),
                     (self.end_date, now.strftime("%Y-%m-%d")),
                     (self.end_time, now.strftime("%H:%M"))):
            e.delete(0, tk.END)
            e.insert(0, v)

    def open_folder(self):
        d = self._reports_dir()
        if not os.path.exists(d):
            messagebox.showinfo(t("msg.info"), t("reports.no_reports_yet"))
            return
        try:
            if sys.platform.startswith("linux"):
                subprocess.Popen(["xdg-open", d])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", d])
            else:
                os.startfile(d)  # noqa: S606
        except Exception as e:
            messagebox.showerror(t("msg.error"), t("reports.cannot_open", e=e))

    def generate(self):
        try:
            start_dt = (f"{self.start_date.get().strip()} "
                        f"{self.start_time.get().strip()}:00")
            end_dt = (f"{self.end_date.get().strip()} "
                      f"{self.end_time.get().strip()}:59")
            datetime.strptime(start_dt, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(end_dt, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror(t("msg.error"), t("reports.invalid_datetime"))
            return
        if start_dt > end_dt:
            messagebox.showerror(t("msg.error"), t("reports.start_after_end"))
            return

        report = self._build_report(start_dt, end_dt)
        self.preview.delete(1.0, tk.END)
        self.preview.insert(1.0, report)

        path = self._save(report, start_dt, end_dt)
        if not path:
            return
        last_report.save_last_report(end_dt)
        messagebox.showinfo(t("msg.success"),
                            t("reports.report_saved", path=path))

    def _build_report(self, start_dt, end_dt) -> str:
        total, profit, count = db.get_period_summary_datetime(start_dt, end_dt)
        top = db.get_top_products_datetime(10, start_dt, end_dt)
        threshold = self.screen.low_stock_threshold
        total_value, low_stock = db.get_stock_status(threshold)

        lines = [
            "=" * 70,
            t("reports.report_title"),
            "=" * 70,
            t("reports.report_from", d=start_dt),
            t("reports.report_to", d=end_dt),
            t("reports.report_generated",
              d=datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            t("reports.report_by",
              u=self.screen.user["username"] if self.screen.user else "?"),
            "",
            t("reports.report_sales_summary"),
            "-" * 50,
            t("reports.report_total_sales", v=total),
            t("reports.report_total_profit", v=profit),
            t("reports.report_num_trans", n=count),
            "",
            t("reports.report_top10"),
            "-" * 50,
        ]
        if top:
            for i, (name, qty, revenue, prof) in enumerate(top, 1):
                lines.append(f"{i:>2}. {name[:32]:32}  {qty:>6g} pcs  "
                             f"{revenue:>9.2f} DT  {prof:>9.2f} DT")
        else:
            lines.append(t("reports.report_no_sales"))

        lines += [
            "", t("reports.report_stock"), "-" * 50,
            t("reports.report_stock_value", v=total_value),
            "", t("reports.report_low_stock", t=threshold),
        ]
        if not low_stock:
            lines.append(t("reports.report_none"))
        else:
            for name, stock, unit in low_stock[:LOW_STOCK_REPORT_CAP]:
                lines.append(f"  • {name} : {stock:g} {t(f'unit.{unit}')}")
            hidden = len(low_stock) - LOW_STOCK_REPORT_CAP
            if hidden > 0:
                lines.append(t("reports.report_hidden", n=hidden))

        lines += ["", "=" * 70, t("reports.report_success"), "=" * 70, ""]
        return "\n".join(lines)

    def _save(self, report, start_dt, end_dt) -> str | None:
        d = self._reports_dir()
        os.makedirs(d, exist_ok=True)
        safe_start = start_dt.replace(" ", "_").replace(":", "")
        safe_end = end_dt.replace(" ", "_").replace(":", "")
        path = os.path.join(d, f"rapport_{safe_start}_{safe_end}.txt")
        counter = 1
        while os.path.exists(path):
            path = os.path.join(
                d, f"rapport_{safe_start}_{safe_end}_{counter}.txt")
            counter += 1
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(report)
        except OSError as e:
            messagebox.showerror(t("msg.error"),
                                 t("reports.cannot_write", e=e))
            return None
        return path