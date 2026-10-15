"""Reusable widgets: build_topbar, DateRangeFilter, ScrollableTreeview."""
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from app import theme
from utils import i18n
from utils.i18n import t


# ---------------------------------------------------------------------------
# Topbar
# ---------------------------------------------------------------------------
def build_topbar(parent, *, color, title_key, buttons_start=(),
                 buttons_end=(), logout_callback=None):
    """Standard 55px topbar: start buttons | title | end buttons | logout."""
    top = tk.Frame(parent, bg=color, height=theme.TOPBAR_H)
    top.pack(fill="x")
    top.pack_propagate(False)

    top.grid_rowconfigure(0, weight=1)
    top.grid_columnconfigure(0, weight=1)
    top.grid_columnconfigure(1, weight=0)
    top.grid_columnconfigure(2, weight=1)

    if i18n.is_rtl():
        start_col, end_col = 2, 0
        start_sticky, end_sticky = "e", "w"
    else:
        start_col, end_col = 0, 2
        start_sticky, end_sticky = "w", "e"

    # --- start side ---
    start = tk.Frame(top, bg=color)
    start.grid(row=0, column=start_col, sticky=start_sticky, padx=8, pady=8)
    for text, bg, cmd in buttons_start:
        tk.Button(start, text=text, bg=bg, fg="white",
                  font=i18n.ui_font(10), width=11, relief="flat",
                  command=cmd).pack(side=i18n.side_start(), padx=3)

    # --- title ---
    tk.Label(top, text=t(title_key), bg=color, fg="white",
             font=i18n.ui_font(13, "bold")
             ).grid(row=0, column=1, padx=20)

    # --- end side ---
    end = tk.Frame(top, bg=color)
    end.grid(row=0, column=end_col, sticky=end_sticky, padx=8, pady=8)
    for text, bg, cmd in buttons_end:
        tk.Button(end, text=text, bg=bg, fg="white",
                  font=i18n.ui_font(10), width=11, relief="flat",
                  command=cmd).pack(side=i18n.side_end(), padx=3)

    # --- logout (always outermost on the end side) ---
    if logout_callback:
        tk.Button(end, text=t("logout.button"), bg=theme.LOGOUT, fg="white",
                  font=i18n.ui_font(9), width=8, relief="flat",
                  command=logout_callback
                  ).pack(side=i18n.side_end(), padx=3)

    return top


# ---------------------------------------------------------------------------
# Date range filter
# ---------------------------------------------------------------------------
class DateRangeFilter(tk.Frame):
    """From [date] [time]  To [date] [time]  [Filter] [Clear] [↻]"""

    def __init__(self, parent, *, bg=theme.BG_CARD,
                 from_key="lbl.from", to_key="lbl.to",
                 on_apply=None, on_clear=None, on_refresh=None,
                 show_verify=False, on_verify=None):
        super().__init__(parent, bg=bg, relief="groove", bd=1)
        self._bg = bg
        self._on_apply = on_apply
        today = datetime.now().strftime("%Y-%m-%d")

        # --- From ---
        f = tk.Frame(self, bg=bg)
        f.pack(side=i18n.side_start(), padx=10, pady=6)
        tk.Label(f, text=t(from_key), bg=bg,
                 font=i18n.ui_font(9)).pack(side=i18n.side_start())
        self.start_date = self._entry(f, 10, today)
        self.start_time = self._entry(f, 5, "00:00")

        # --- To ---
        e = tk.Frame(self, bg=bg)
        e.pack(side=i18n.side_start(), padx=10, pady=6)
        tk.Label(e, text=t(to_key), bg=bg,
                 font=i18n.ui_font(9)).pack(side=i18n.side_start())
        self.end_date = self._entry(e, 10, today)
        self.end_time = self._entry(e, 5, "23:59")

        # --- Actions ---
        tk.Button(self, text=t("btn.filter"), bg=theme.BLUE, fg="white",
                  font=i18n.ui_font(9), command=self._apply
                  ).pack(side=i18n.side_start(), padx=5)
        tk.Button(self, text=t("btn.clear_filter"), bg=theme.GRAY, fg="white",
                  font=i18n.ui_font(9), command=self._clear
                  ).pack(side=i18n.side_start(), padx=5)
        if on_refresh:
            tk.Button(self, text=t("btn.refresh"), bg=theme.BLUE, fg="white",
                      font=i18n.ui_font(9), width=2, command=on_refresh
                      ).pack(side=i18n.side_start(), padx=5)
        if show_verify and on_verify:
            tk.Button(self, text=t("btn.verify"), bg=theme.ORANGE, fg="white",
                      font=i18n.ui_font(9), command=on_verify
                      ).pack(side=i18n.side_start(), padx=5)

    # --- helpers -------------------------------------------------------
    def _entry(self, parent, width, default):
        e = tk.Entry(parent, width=width, font=i18n.ui_font(9),
                     justify=i18n.justify_text())
        e.pack(side=i18n.side_start(), padx=2)
        e.insert(0, default)
        return e

    def _apply(self):
        try:
            self.get_range()
        except ValueError as msg:
            from tkinter import messagebox
            messagebox.showerror(t("msg.error"), str(msg))
            return
        if self._on_apply:
            self._on_apply()

    def _clear(self):
        today = datetime.now().strftime("%Y-%m-%d")
        for e, v in ((self.start_date, today), (self.start_time, "00:00"),
                     (self.end_date, today), (self.end_time, "23:59")):
            e.delete(0, tk.END)
            e.insert(0, v)
        if self._on_clear:
            self._on_clear()
        elif self._on_apply:
            self._on_apply()

    # --- public API ----------------------------------------------------
    def get_range(self) -> tuple[str, str]:
        """Return ("YYYY-MM-DD HH:MM:00", "YYYY-MM-DD HH:MM:59")."""
        start = f"{self.start_date.get().strip()} {self.start_time.get().strip()}:00"
        end = f"{self.end_date.get().strip()} {self.end_time.get().strip()}:59"
        try:
            datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(t("reports.invalid_datetime"))
        if start > end:
            raise ValueError(t("reports.start_after_end"))
        return start, end

    def peek_range(self):
        """Same as get_range but returns (None, None) on bad input."""
        try:
            return self.get_range()
        except ValueError:
            return None, None


# ---------------------------------------------------------------------------
# Scrollable treeview
# ---------------------------------------------------------------------------
class ScrollableTreeview(tk.Frame):
    """Treeview + both scrollbars, correctly gridded."""

    def __init__(self, parent, *, columns, headings, widths, height=20,
                 anchors=None, selectmode="extended", style=None):
        super().__init__(parent, bg=theme.BG_CARD, relief="groove", bd=1)
        anchors = anchors or {}

        self.tree = ttk.Treeview(self, columns=columns, show="headings",
                                 selectmode=selectmode, height=height,
                                 style=style or "Treeview")
        for col, hdr, w in zip(columns, headings, widths):
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=w,
                             anchor=anchors.get(col, "center"))

        v = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        h = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v.set, xscrollcommand=h.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        v.grid(row=0, column=1, sticky="ns")
        h.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def clear(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

    def insert_row(self, values, tags=()):
        return self.tree.insert("", "end", values=values, tags=tags)

    def selection_tags(self):
        """Return the first tag of every selected row (usually the timestamp)."""
        out = []
        for item in self.tree.selection():
            tags = self.tree.item(item, "tags")
            if tags:
                out.append(tags[0])
        return out

    def bind(self, event, handler):      # noqa: A003
        self.tree.bind(event, handler)