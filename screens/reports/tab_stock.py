"""Stock status tab."""
import tkinter as tk
from tkinter import ttk

from app import theme
from database import db
from utils.i18n import t

MONO_FONT = "TkFixedFont"


class StockTab(ttk.Frame):
    def __init__(self, parent, screen):
        super().__init__(parent)
        self.screen = screen

        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        ctrl = ttk.Frame(main)
        ctrl.pack(fill="x", pady=5)
        ttk.Label(ctrl, text=t("reports.low_stock_threshold")).pack(side="left",
                                                                   padx=5)
        self.threshold = ttk.Entry(ctrl, width=5, justify="center")
        self.threshold.pack(side="left", padx=5)
        self.threshold.insert(0, str(self.screen.low_stock_threshold))
        ttk.Button(ctrl, text=t("reports.refresh_btn"),
                   command=self.load).pack(side="left", padx=10)

        wrap = ttk.Frame(main)
        wrap.pack(fill="both", expand=True, pady=10)
        self.text = tk.Text(wrap, height=15, bg=theme.BG_INPUT, fg=theme.FG,
                            insertbackground=theme.FG, font=MONO_FONT,
                            relief="sunken", bd=1, wrap="none")
        v = ttk.Scrollbar(wrap, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=v.set)
        self.text.pack(side="left", fill="both", expand=True)
        v.pack(side="right", fill="y")

    def _threshold(self) -> int:
        try:
            value = int(self.threshold.get())
            if value < 0:
                raise ValueError
            return value
        except (ValueError, AttributeError):
            return self.screen.low_stock_threshold

    def load(self):
        threshold = self._threshold()
        self.screen.low_stock_threshold = threshold
        total_value, low_stock = db.get_stock_status(threshold)

        self.text.delete(1.0, tk.END)
        self.text.insert(1.0, t("reports.stock_value", v=total_value) + "\n\n"
                              + t("reports.low_stock_header", t=threshold) + "\n")
        if low_stock:
            for name, stock, unit in low_stock:
                self.text.insert(
                    tk.END, f"  • {name} : {stock:g} {t(f'unit.{unit}')}\n")
        else:
            self.text.insert(tk.END, t("reports.no_low_stock") + "\n")