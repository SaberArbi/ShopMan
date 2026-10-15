"""Top products tab."""
from datetime import datetime
from tkinter import messagebox, ttk

from app import theme
from database import db
from utils import i18n
from utils.i18n import t


class TopProductsTab(ttk.Frame):
    def __init__(self, parent, screen):
        super().__init__(parent)
        self.screen = screen

        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        box = ttk.LabelFrame(main, text=t("reports.period_optional"), padding=10)
        box.pack(fill="x", pady=5)

        self.start_date = self._field(box, 0, t("lbl.from"), 12)
        self.start_time = self._field(box, 0, None, 6, col=2)
        self.end_date = self._field(box, 1, t("lbl.to"), 12)
        self.end_time = self._field(box, 1, None, 6, col=2)

        limit = ttk.Frame(box)
        limit.grid(row=2, column=0, columnspan=3, pady=5)
        ttk.Label(limit, text=t("reports.num_products")).pack(side="left", padx=5)
        self.limit = ttk.Entry(limit, width=5, justify="center")
        self.limit.pack(side="left", padx=5)
        self.limit.insert(0, "10")

        btns = ttk.Frame(box)
        btns.grid(row=3, column=0, columnspan=3, pady=10)
        ttk.Button(btns, text=t("reports.load_top"),
                   command=self.load).pack(side="left", padx=5)
        ttk.Button(btns, text=t("reports.clear_period"),
                   command=self.clear_period).pack(side="left", padx=5)

        ttk.Style().configure("Reports.Treeview",
                              background="white", foreground="black",
                              fieldbackground="white",
                              font=i18n.ui_font(10), rowheight=26)
        ttk.Style().configure("Reports.Treeview.Heading",
                              font=i18n.ui_font(10, "bold"),
                              background=theme.BG_SUBTLE, foreground="black")

        wrap = ttk.Frame(main)
        wrap.pack(fill="both", expand=True, pady=10)
        columns = ("product", "qty", "revenue", "profit")
        headings = [t("reports.col_product"), t("reports.col_qty"),
                    t("reports.col_revenue"), t("reports.col_profit")]
        self.tree = ttk.Treeview(wrap, columns=columns, show="headings",
                                 height=15, style="Reports.Treeview")
        for col, hdr in zip(columns, headings):
            self.tree.heading(col, text=hdr)
            self.tree.column(col,
                             width=200 if col == "product" else 110,
                             anchor=(i18n.anchor_start()
                                     if col == "product" else "center"))
        v = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v.set)
        self.tree.pack(side="left", fill="both", expand=True)
        v.pack(side="right", fill="y")

    def _field(self, parent, row, label, width, default="", col=1):
        if label:
            ttk.Label(parent, text=label).grid(row=row, column=0,
                                                sticky="e", padx=5, pady=5)
        e = ttk.Entry(parent, width=width, justify=i18n.justify_text())
        e.grid(row=row, column=col, padx=5, pady=5)
        if default:
            e.insert(0, default)
        return e

    def clear_period(self):
        for e in (self.start_date, self.start_time,
                  self.end_date, self.end_time):
            e.delete(0, tk.END)

    def load(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            limit = int(self.limit.get() or "10")
        except ValueError:
            limit = 10

        start_dt = end_dt = None
        if self.start_date.get().strip() and self.start_time.get().strip():
            try:
                start_dt = (f"{self.start_date.get().strip()} "
                            f"{self.start_time.get().strip()}:00")
                datetime.strptime(start_dt, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror(t("msg.error"), t("reports.invalid_datetime"))
                return
        if self.end_date.get().strip() and self.end_time.get().strip():
            try:
                end_dt = (f"{self.end_date.get().strip()} "
                          f"{self.end_time.get().strip()}:59")
                datetime.strptime(end_dt, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror(t("msg.error"), t("reports.invalid_datetime"))
                return
        if start_dt and end_dt and start_dt > end_dt:
            messagebox.showerror(t("msg.error"), t("reports.start_after_end"))
            return

        for name, qty, revenue, profit in db.get_top_products_datetime(
                limit, start_dt, end_dt):
            self.tree.insert("", "end", values=(
                name[:45], f"{qty:g}", f"{revenue:.2f}", f"{profit:.2f}"))