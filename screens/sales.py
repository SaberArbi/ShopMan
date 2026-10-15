"""Sales screen — scan/search, cart, checkout, telecom shortcuts."""
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from app import theme
from database import db
from screens.base import BaseScreen
from screens.widgets import build_topbar
from utils import auth, backup, i18n
from utils.i18n import t


TELECOM_SHORTCUTS = {
    "F1": "TELECOM 1.3", "F2": "TELECOM 5.9",
    "F3": "ORANGE 1.3",  "F4": "ORANGE 5.9",
    "F5": "OOREDOO 1.3", "F6": "OOREDOO 5.9",
}

OPERATOR_GRID = [
    ("#3498db", "TELECOM 1.3", "F1"),
    ("#3498db", "TELECOM 5.9", "F2"),
    ("#f39c12", "ORANGE 1.3",  "F3"),
    ("#f39c12", "ORANGE 5.9",  "F4"),
    ("#e74c3c", "OOREDOO 1.3", "F5"),
    ("#e74c3c", "OOREDOO 5.9", "F6"),
]


class SalesScreen(BaseScreen):
    topbar_color = theme.GREEN

    def __init__(self, root, switch, user=None, logout=None):
        # Cart / state — must exist before build() runs
        self.cart = []
        self.active_popup = None
        self.notification_label = None
        self.telecom_products = []
        self.telecom_by_name = {}
        self.search_results = []
        self.search_listbox_products = []
        self.after_id = None
        self.state = "SCAN"
        self.tooltip = None
        super().__init__(root, switch, user, logout=None)
        self.load_telecom_products()
        self.setup_keyboard_shortcuts()

    # ------------------------------------------------------------------
    # Topbar
    # ------------------------------------------------------------------
    def build_topbar(self):
        start_btns, end_btns = [], []
        if auth.can(self.user, "manage_products"):
            start_btns.append((t("nav.products"), theme.GREEN_LIGHT,
                               lambda: self.switch("products")))
        if auth.can(self.user, "view_history"):
            start_btns.append((t("nav.history"), theme.GREEN_LIGHT,
                               lambda: self.switch("history")))
        if auth.can(self.user, "manage_users"):
            start_btns.append((t("nav.users"), theme.GREEN_LIGHT,
                               lambda: self.switch("users")))
        if auth.can(self.user, "view_deleted_sales"):
            end_btns.append((t("history.deleted_btn"), theme.RED_DARKER,
                             lambda: self.switch("deleted")))
        if auth.can(self.user, "view_reports"):
            end_btns.append((t("nav.reports"), theme.GREEN_LIGHT,
                             lambda: self.switch("reports")))
        build_topbar(self.frame, color=self.topbar_color,
                     title_key="sales.title",
                     buttons_start=start_btns, buttons_end=end_btns
                     ,
                     logout_callback=self.logout)

    # ------------------------------------------------------------------
    # Body
    # ------------------------------------------------------------------
    def build_body(self):
        main = tk.Frame(self.frame, bg=theme.BG)
        main.pack(fill="both", expand=True, padx=5, pady=5)

        scan = tk.Frame(main, bg=theme.BG, width=theme.SCAN_COL_W)
        scan.pack(side=i18n.side_start(), fill="both", padx=(0, 5))
        scan.pack_propagate(False)

        cart = tk.Frame(main, bg=theme.BG_CARD, relief="groove", bd=1)
        cart.pack(side=i18n.side_end(), fill="both", expand=True)

        self._build_scan_column(scan)
        self._build_cart_column(cart)
        self.set_state("SCAN")

    # --- scan column ---------------------------------------------------
    def _build_scan_column(self, parent):
        # State indicator
        self.state_frame = tk.Frame(parent, bg=theme.DARK_LIGHT, height=26)
        self.state_frame.pack(fill="x", pady=(0, 3))
        self.state_frame.pack_propagate(False)
        self.state_label = tk.Label(self.state_frame, text="",
                                    bg=theme.DARK_LIGHT, fg="white",
                                    font=self.font(9))
        self.state_label.pack(pady=4)

        self._build_scanner(parent)
        self._build_telecom(parent)

        shortcuts = tk.Frame(parent, bg=theme.DARK_LIGHT, height=26)
        shortcuts.pack(fill="x", pady=(5, 0))
        shortcuts.pack_propagate(False)
        tk.Label(shortcuts, text=t("sales.shortcuts_bar"),
                 bg=theme.DARK_LIGHT, fg="white",
                 font=self.font(9)).pack(pady=4)

        self.notification_frame = tk.Frame(parent, bg=theme.BG, height=26)
        self.notification_frame.pack(fill="x")
        self.notification_frame.pack_propagate(False)

    def _build_scanner(self, parent):
        frame = tk.Frame(parent, bg=theme.BG_CARD, relief="groove", bd=1)
        frame.pack(fill="x", pady=(0, 5))

        tk.Label(frame, text=t("sales.scanner_search"), bg=theme.BG_CARD,
                 fg=theme.FG, font=self.font(10, "bold")).pack(pady=3)

        hints = tk.Frame(frame, bg=theme.BG_CARD)
        hints.pack(fill="x", padx=5)
        tk.Label(hints, text=t("sales.hint_scan"), bg=theme.BG_CARD,
                 fg=theme.FG_MUTED, font=self.font(9)
                 ).pack(side=i18n.side_start(), padx=2)
        tk.Label(hints, text=t("sales.hint_search"), bg=theme.BG_CARD,
                 fg=theme.FG_MUTED, font=self.font(9)
                 ).pack(side=i18n.side_end(), padx=2)

        self.barcode_entry = tk.Entry(frame, font=self.font(14),
                                      bg=theme.BG_INPUT, fg=theme.FG,
                                      relief="solid", bd=1,
                                      justify=i18n.justify_text())
        self.barcode_entry.pack(fill="x", padx=5, pady=5, ipady=3)
        self.barcode_entry.bind("<KeyRelease>", self.on_barcode_key)
        self.barcode_entry.bind("<Return>", self.process_barcode)
        self.barcode_entry.bind("<Down>", self.focus_search_results)
        self.barcode_entry.bind("<space>", self.on_barcode_space)

        self.search_frame = tk.Frame(parent, bg=theme.BG_CARD,
                                     relief="solid", bd=1)
        self.search_listbox = tk.Listbox(self.search_frame, height=6,
                                         font=self.font(10),
                                         selectbackground=theme.BLUE,
                                         selectforeground="white",
                                         bg=theme.BG_CARD, fg=theme.FG)
        self.search_listbox.pack(fill="both", expand=True, padx=1, pady=1)
        self.search_listbox.bind("<Button-1>", self.on_search_click)
        self.search_listbox.bind("<Double-Button-1>", self.select_from_search)
        self.search_listbox.bind("<Return>", self.select_from_search)
        self.search_listbox.bind("<KP_Enter>", self.select_from_search)
        self.search_listbox.bind("<Escape>", lambda e: self._dismiss_search())

    def _build_telecom(self, parent):
        frame = tk.Frame(parent, bg=theme.BG_CARD, relief="groove", bd=1)
        frame.pack(fill="x", pady=(0, 5))

        tk.Label(frame, text=t("sales.telecom_shortcuts"), bg=theme.BG_CARD,
                 fg=theme.FG, font=self.font(10, "bold")).pack(pady=3)

        grid = tk.Frame(frame, bg=theme.BG_CARD)
        grid.pack(pady=4)
        rtl = i18n.is_rtl()
        for i, (color, name, key) in enumerate(OPERATOR_GRID):
            r, c = i // 2, i % 2
            if rtl:
                c = 1 - c
            btn = tk.Button(grid, text=f"[{key}] {name}",
                            bg=color, fg="white",
                            font=self.font(9), width=15, height=1,
                            relief="flat",
                            command=lambda n=name: self.add_telecom_to_cart(n))
            btn.grid(row=r, column=c, padx=2, pady=2)
            self._attach_tooltip(btn, f"Raccourci: {key}")

    # --- cart column ---------------------------------------------------
    def _build_cart_column(self, parent):
        header = tk.Frame(parent, bg=theme.BG_CARD)
        header.pack(fill="x", padx=5, pady=5)
        tk.Label(header, text=t("sales.cart"), bg=theme.BG_CARD,
                 fg=theme.FG, font=self.font(10, "bold")
                 ).pack(side=i18n.side_start())
        tk.Label(header, text=t("sales.cart_pay_hint"), bg=theme.BG_CARD,
                 fg=theme.GREEN, font=self.font(10, "bold")
                 ).pack(side=i18n.side_end())

        container = tk.Frame(parent, bg=theme.BG_CARD)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        ttk.Style().configure("Cart.Treeview",
                              background="white", foreground="black",
                              fieldbackground="white",
                              font=self.font(10), rowheight=26)
        ttk.Style().configure("Cart.Treeview.Heading",
                              font=self.font(10, "bold"),
                              background=theme.BG_SUBTLE, foreground="black")

        columns = ("Produit", "Qté", "Unité", "Prix", "Total")
        headings = [t("lbl.product"), t("lbl.quantity"), t("lbl.unit"),
                    t("sales.price"), t("lbl.total")]
        widths = [260, 90, 70, 80, 90]
        self.cart_tree = ttk.Treeview(container, columns=columns,
                                      show="headings", height=20,
                                      style="Cart.Treeview")
        for col, hdr, w in zip(columns, headings, widths):
            self.cart_tree.heading(col, text=hdr)
            self.cart_tree.column(col, width=w, minwidth=w, anchor="center")
        scroll = ttk.Scrollbar(container, orient="vertical",
                               command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=scroll.set)
        self.cart_tree.pack(side=i18n.side_start(), fill="both", expand=True)
        scroll.pack(side=i18n.side_end(), fill="y")

        actions = tk.Frame(parent, bg=theme.BG_CARD)
        actions.pack(fill="x", padx=5, pady=5)
        tk.Button(actions, text=t("sales.btn_remove"), bg=theme.RED, fg="white",
                  font=self.font(10, "bold"), width=9, relief="flat",
                  command=self.remove_from_cart
                  ).pack(side=i18n.side_start(), padx=2)
        tk.Button(actions, text=t("sales.btn_clear"), bg=theme.GRAY, fg="white",
                  font=self.font(10, "bold"), width=9, relief="flat",
                  command=self.clear_cart
                  ).pack(side=i18n.side_start(), padx=2)
        pay = tk.Button(actions, text=t("sales.btn_pay"),
                        bg=theme.GREEN, fg="white",
                        font=self.font(12, "bold"), width=15, relief="flat",
                        command=self.complete_sale)
        pay.pack(side=i18n.side_end(), padx=2)
        self._attach_tooltip(pay, "Raccourci: ESPACE")

        total = tk.Frame(parent, bg=theme.BG_CARD)
        total.pack(fill="x", padx=5, pady=5)
        tk.Label(total, text=t("lbl.total") + ":", bg=theme.BG_CARD,
                 fg=theme.FG, font=self.font(14)
                 ).pack(side=i18n.side_start())
        self.total_label = tk.Label(total, text="0.00 DT", bg=theme.BG_CARD,
                                    fg=theme.GREEN, font=self.font(14, "bold"))
        self.total_label.pack(side=i18n.side_end())

    # ------------------------------------------------------------------
    # Tooltip
    # ------------------------------------------------------------------
    def _attach_tooltip(self, widget, text):
        def enter(_):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            tk.Label(self.tooltip, text=text, bg="#ffffe0",
                     relief="solid", bd=1).pack()

        def leave(_):
            if self.tooltip and self.tooltip.winfo_exists():
                self.tooltip.destroy()
                self.tooltip = None

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    # ------------------------------------------------------------------
    # Telecom products
    # ------------------------------------------------------------------
    def load_telecom_products(self):
        self.telecom_products = db.get_telecom_products()
        self.telecom_by_name = {p[1]: p for p in self.telecom_products}

    # ------------------------------------------------------------------
    # Keyboard shortcuts
    # ------------------------------------------------------------------
    def setup_keyboard_shortcuts(self):
        self._unbind_shortcuts()
        for key in TELECOM_SHORTCUTS:
            self.frame.bind_all(f"<{key}>", self.on_telecom_key)
        self.frame.bind_all("<space>", self.on_pay_key)
        self.frame.bind_all("<Escape>", self.on_escape)

    def _unbind_shortcuts(self):
        for key in TELECOM_SHORTCUTS:
            self.frame.unbind_all(f"<{key}>")
        self.frame.unbind_all("<space>")
        self.frame.unbind_all("<Escape>")

    def _barcode_focused(self):
        try:
            return self.root.focus_get() is self.barcode_entry
        except (KeyError, tk.TclError):
            return False

    def on_telecom_key(self, event):
        if self.state == "POPUP_ACTIVE":
            return
        name = TELECOM_SHORTCUTS.get(event.keysym)
        if name:
            self.add_telecom_to_cart(name)
        return "break"

    def on_barcode_space(self, event):
        if self.barcode_entry.get() == "":
            if self.cart:
                self.complete_sale()
            return "break"
        return None

    def on_pay_key(self, event):
        if self.state in ("POPUP_ACTIVE", "SEARCHING"):
            return
        if self._barcode_focused():
            return
        if self.cart:
            self.complete_sale()
        return "break"

    def on_escape(self, event):
        if self.state == "POPUP_ACTIVE":
            self.on_popup_close()
        elif self.state == "SEARCHING":
            self._dismiss_search()
            self.barcode_entry.delete(0, tk.END)
            self.set_state("SCAN")
        return "break"

    # ------------------------------------------------------------------
    # State machine
    # ------------------------------------------------------------------
    def set_state(self, new_state):
        self.state = new_state
        colors = {"SCAN": theme.DARK_LIGHT,
                  "SEARCHING": theme.ORANGE,
                  "POPUP_ACTIVE": theme.PURPLE_LIGHT}
        labels = {"SCAN": "sales.state_scan",
                  "SEARCHING": "sales.state_searching",
                  "POPUP_ACTIVE": "sales.state_popup"}
        color = colors.get(new_state, theme.DARK_LIGHT)
        self.state_label.config(text=t(labels.get(new_state, "sales.state_scan")),
                                bg=color)
        self.state_frame.config(bg=color)

    # ------------------------------------------------------------------
    # Scan / search
    # ------------------------------------------------------------------
    def on_barcode_key(self, event):
        if self.after_id:
            self.frame.after_cancel(self.after_id)
            self.after_id = None
        if self.state == "POPUP_ACTIVE":
            return
        if event.keysym == "Down" and self.search_frame.winfo_ismapped():
            self.focus_search_results()
            return
        value = self.barcode_entry.get()
        if value.isdigit():
            self.set_state("SCAN")
            self._dismiss_search()
            return
        if len(value) >= 1:
            self.set_state("SEARCHING")
            self.after_id = self.frame.after(
                250, lambda: self.search_products(value))
        else:
            self.set_state("SCAN")
            self._dismiss_search()

    def focus_search_results(self, event=None):
        if self.search_frame.winfo_ismapped() and self.search_listbox.size() > 0:
            self.search_listbox.focus_set()
            self.search_listbox.selection_clear(0, tk.END)
            self.search_listbox.selection_set(0)
            return "break"

    @staticmethod
    def validate_numeric(char):
        return char.isdigit() or char == ""

    @staticmethod
    def validate_decimal(char):
        return char.isdigit() or char == "."

    def search_products(self, term):
        term = term.strip()
        if not term:
            self._dismiss_search()
            return
        products = db.search_products_by_name(term)
        self.search_results = products
        self.search_listbox_products = products
        if not products:
            self._dismiss_search()
            return
        self.search_listbox.delete(0, tk.END)
        for p in products[:8]:
            self.search_listbox.insert(tk.END, f"{p[2][:30]}  —  {p[5]:.2f} DT")
        self.search_frame.pack(fill="x", pady=(0, 5),
                               after=self.barcode_entry.master)

    def _dismiss_search(self):
        self.search_frame.pack_forget()
        self.search_results = []
        self.search_listbox_products = []

    def on_search_click(self, event):
        self.select_from_search()

    def select_from_search(self, event=None):
        sel = self.search_listbox.curselection()
        if not sel or not self.search_listbox_products:
            return
        idx = sel[0]
        if idx >= len(self.search_listbox_products):
            return
        product = self.search_listbox_products[idx]
        self._dismiss_search()
        self.barcode_entry.delete(0, tk.END)
        self.set_state("SCAN")
        self._open_product_popup(product)

    def process_barcode(self, event=None):
        barcode = self.barcode_entry.get().strip()
        if not barcode:
            return
        product = db.get_product_by_barcode(barcode)
        self.barcode_entry.delete(0, tk.END)
        if not product:
            self.show_notification(t("sales.not_found"), is_error=True)
            return
        self._open_product_popup(product)

    # ------------------------------------------------------------------
    # Product popups
    # ------------------------------------------------------------------
    def _open_product_popup(self, product):
        ptype = product[10] if len(product) > 10 else "normal"
        unit = product[6]
        if ptype == "cigarette":
            self.show_cigarette_popup(product)
        elif unit == "gram":
            self.show_gram_popup(product)
        elif unit == "pack":
            self.show_pack_popup(product)
        else:
            ok = self.add_to_cart(product, 1, "piece", 1,
                                  product[5], product[5] - product[4])
            if ok:
                self.show_notification(t("sales.added", name=product[2]))

    def _quantity_popup(self, product, *, title, header_lines,
                        unit_options, default_unit, compute, stock_check=None):
        if self.active_popup and self.active_popup.winfo_exists():
            self.active_popup.destroy()
        self.set_state("POPUP_ACTIVE")
        self._unbind_shortcuts()

        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry(f"{theme.DIALOG_W}x{theme.DIALOG_H}")
        popup.transient(self.root)
        popup.grab_set()
        popup.focus_force()
        popup.configure(bg=theme.BG)
        self.active_popup = popup

        x = self.barcode_entry.winfo_rootx()
        y = self.barcode_entry.winfo_rooty() + self.barcode_entry.winfo_height() + 5
        popup.geometry(f"+{x}+{y}")

        tk.Label(popup, text="\n".join(header_lines),
                 font=self.font(11, "bold"),
                 bg=theme.BG, fg=theme.FG,
                 justify="center").pack(pady=8)

        unit_var = tk.StringVar(value=default_unit)
        unit_frame = tk.Frame(popup, bg=theme.BG)
        unit_frame.pack(pady=4)
        tk.Label(unit_frame, text=t("sales.sell_in"), font=self.font(10),
                 bg=theme.BG, fg=theme.FG
                 ).pack(side=i18n.side_start(), padx=5)
        for label, value in unit_options:
            tk.Radiobutton(unit_frame, text=label, variable=unit_var,
                           value=value, font=self.font(10),
                           bg=theme.BG, fg=theme.FG,
                           activebackground=theme.BG,
                           selectcolor=theme.BG
                           ).pack(side=i18n.side_start(), padx=4)

        tk.Label(popup, text=t("sales.qty"), font=self.font(10),
                 bg=theme.BG, fg=theme.FG).pack(pady=(8, 2))
        vcmd = (popup.register(self.validate_decimal), "%S")
        entry = tk.Entry(popup, font=self.font(16), width=12,
                         justify="center", validate="key",
                         validatecommand=vcmd,
                         bg="white", fg=theme.FG, relief="solid", bd=1)
        entry.pack(pady=4, ipady=4)
        entry.focus()
        entry.select_range(0, tk.END)

        preview_frame = tk.Frame(popup, bg=theme.BG)
        preview_frame.pack(pady=6)
        tk.Label(preview_frame, text=t("lbl.total") + ": ",
                 font=self.font(12), bg=theme.BG, fg=theme.FG
                 ).pack(side=i18n.side_start())
        preview_label = tk.Label(preview_frame, text="0.00 DT",
                                 font=self.font(12, "bold"),
                                 bg=theme.BG, fg=theme.GREEN)
        preview_label.pack(side=i18n.side_start())

        warning_label = tk.Label(popup, text="", font=self.font(9),
                                 bg=theme.BG, fg=theme.RED)
        warning_label.pack()

        def update_preview(*_):
            warning_label.config(text="")
            try:
                qty = float(entry.get() or "0")
                result = compute(qty, unit_var.get())
                preview_label.config(text=f"{result['total']:.2f} DT")
                if stock_check:
                    msg = stock_check(qty, unit_var.get())
                    if msg:
                        warning_label.config(text=msg)
            except (ValueError, KeyError):
                preview_label.config(text="0.00 DT")

        entry.bind("<KeyRelease>", update_preview)
        unit_var.trace_add("write", update_preview)

        tk.Label(popup, text=t("sales.popup_hint"),
                 fg=theme.FG_MUTED, bg=theme.BG,
                 font=self.font(9)).pack(pady=4)

        def cycle_unit():
            values = [v for _, v in unit_options]
            idx = values.index(unit_var.get())
            unit_var.set(values[(idx + 1) % len(values)])

        def do_add():
            try:
                qty = float(entry.get() or "0")
            except ValueError:
                return
            if qty <= 0:
                return
            if stock_check:
                msg = stock_check(qty, unit_var.get())
                if msg:
                    messagebox.showerror(t("msg.error"), msg, parent=popup)
                    return
            try:
                result = compute(qty, unit_var.get())
            except (ValueError, KeyError):
                return
            ok = self.add_to_cart(
                product, result["pieces_qty"], result["unit_display"],
                result["display_qty"], result["total"], result["profit"],
            )
            if ok:
                self.show_notification(t("sales.added_qty",
                                          qty=result["display_qty"],
                                          unit=result["unit_display"]))
            popup.destroy()
            self.on_popup_close()

        popup.bind("<Key-u>", lambda e: cycle_unit())
        popup.bind("<Key-U>", lambda e: cycle_unit())
        popup.bind("<Return>", lambda e: do_add())
        popup.bind("<KP_Enter>", lambda e: do_add())
        popup.bind("<Escape>", lambda e: self.on_popup_close())

        btns = tk.Frame(popup, bg=theme.BG)
        btns.pack(pady=10)
        tk.Button(btns, text=t("btn.add"), command=do_add,
                  bg=theme.GREEN, fg="white", width=10,
                  font=self.font(10, "bold"), relief="flat"
                  ).pack(side=i18n.side_start(), padx=5)
        tk.Button(btns, text=t("btn.cancel"), command=self.on_popup_close,
                  bg=theme.GRAY, fg="white", width=10,
                  font=self.font(10, "bold"), relief="flat"
                  ).pack(side=i18n.side_start(), padx=5)

    def show_gram_popup(self, product):
        price_kg, buy_kg = product[5], product[4]

        def compute(qty, unit):
            if unit == "g":
                return dict(pieces_qty=qty, display_qty=qty, unit_display="g",
                            total=(qty / 1000) * price_kg,
                            profit=(qty / 1000) * (price_kg - buy_kg))
            return dict(pieces_qty=qty * 1000, display_qty=qty,
                        unit_display="kg",
                        total=qty * price_kg,
                        profit=qty * (price_kg - buy_kg))

        self._quantity_popup(
            product,
            title=t("sales.popup_weight_title"),
            header_lines=[product[2], t("sales.price_per_kg", p=price_kg)],
            unit_options=[(t("sales.opt_grams"), "g"),
                          (t("sales.opt_kilograms"), "kg")],
            default_unit="g",
            compute=compute,
        )

    def show_pack_popup(self, product):
        ppp = product[9] or 1
        price_pack = product[5]
        price_unit = product[8] if product[8] > 0 else price_pack / ppp
        buy_pack = product[4]
        buy_unit = buy_pack / ppp

        def compute(qty, unit):
            if unit == "pack":
                return dict(pieces_qty=qty * ppp, display_qty=qty,
                            unit_display="pack",
                            total=qty * price_pack,
                            profit=qty * (price_pack - buy_pack))
            return dict(pieces_qty=qty, display_qty=qty,
                        unit_display="unité",
                        total=qty * price_unit,
                        profit=qty * (price_unit - buy_unit))

        self._quantity_popup(
            product,
            title=t("sales.popup_pack_title"),
            header_lines=[product[2],
                          t("sales.pack_price", p=price_pack),
                          t("sales.unit_price", p=price_unit)],
            unit_options=[(t("sales.opt_packs"), "pack"),
                          (t("sales.opt_units"), "unité")],
            default_unit="unité",
            compute=compute,
        )

    def show_cigarette_popup(self, product):
        PACK = 20
        stock_cig = int(product[7])
        pack_price = product[5]
        single_price = (product[11]
                        if len(product) > 11 and product[11] > 0
                        else pack_price / PACK)
        buy_pack = product[4]
        single_cost = (product[11]
                       if len(product) > 11 and product[11] > 0
                       else buy_pack / PACK)

        def compute(qty, unit):
            if unit == "pack":
                return dict(pieces_qty=qty * PACK, display_qty=qty,
                            unit_display="pack",
                            total=qty * pack_price,
                            profit=qty * (pack_price - buy_pack))
            return dict(pieces_qty=qty, display_qty=qty,
                        unit_display="unité",
                        total=qty * single_price,
                        profit=qty * (single_price - single_cost))

        def stock_check(qty, unit):
            needed = qty * PACK if unit == "pack" else qty
            if needed > stock_cig:
                return t("msg.stock_insufficient", available=stock_cig)
            return None

        self._quantity_popup(
            product,
            title=t("sales.popup_cigarette_title"),
            header_lines=[product[2],
                          t("sales.stock_cigarettes", n=stock_cig),
                          t("sales.pack_price", p=pack_price),
                          t("sales.unit_price", p=single_price)],
            unit_options=[(t("sales.opt_packs"), "pack"),
                          (t("sales.opt_units"), "unité")],
            default_unit="unité",
            compute=compute,
            stock_check=stock_check,
        )

    def on_popup_close(self):
        if self.active_popup and self.active_popup.winfo_exists():
            self.active_popup.destroy()
        self.active_popup = None
        self.set_state("SCAN")
        self.setup_keyboard_shortcuts()
        self.barcode_entry.focus_set()

    # ------------------------------------------------------------------
    # Cart
    # ------------------------------------------------------------------
    def add_telecom_to_cart(self, name):
        full_name = name + " DT"
        product = self.telecom_by_name.get(full_name)
        if not product:
            self.show_notification(t("sales.not_found_full", name=full_name),
                                   is_error=True)
            return
        full_product = (product[0], None, product[1], None,
                        product[2], product[3], "piece", 999999,
                        0, 1, "telecom", 0)
        ok = self.add_to_cart(full_product, 1, "piece", 1,
                              product[3], product[3] - product[2])
        if ok:
            self.show_notification(t("sales.added", name=product[1]))
        self.barcode_entry.focus_set()

    def add_to_cart(self, product, pieces_qty, unit_display, display_qty,
                    price, profit):
        ptype = product[10] if len(product) > 10 else "normal"
        is_telecom = ptype == "telecom"
        if not is_telecom and product[7] < pieces_qty:
            self.show_notification(t("msg.stock_only", stock=product[7]),
                                   is_error=True)
            return False

        for i, (p, q, tot, pr, u, dq) in enumerate(self.cart):
            if p[0] == product[0] and u == unit_display:
                new_pieces = q + pieces_qty
                if not is_telecom and product[7] < new_pieces:
                    self.show_notification(t("msg.stock_only", stock=product[7]),
                                           is_error=True)
                    return False
                self.cart[i] = (p, new_pieces, tot + price, pr + profit,
                                u, dq + display_qty)
                self.update_cart()
                return True

        self.cart.append((product, pieces_qty, price, profit,
                          unit_display, display_qty))
        self.update_cart()
        return True

    def remove_from_cart(self):
        sel = self.cart_tree.selection()
        if not sel:
            return
        idx = self.cart_tree.index(sel[0])
        if 0 <= idx < len(self.cart):
            self.cart.pop(idx)
            self.update_cart()
            self.barcode_entry.focus_set()

    def clear_cart(self):
        self.cart = []
        self.update_cart()
        self.barcode_entry.focus_set()

    def update_cart(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        total = 0.0
        for product, _p, line_total, _pr, unit, dq in self.cart:
            unit_price = line_total / dq if dq > 0 else line_total
            self.cart_tree.insert("", "end", values=(
                product[2][:32], f"{dq:g}", unit,
                f"{unit_price:.2f}", f"{line_total:.2f}",
            ))
            total += line_total
        self.total_label.config(text=f"{total:.2f} DT")

    # ------------------------------------------------------------------
    # Checkout
    # ------------------------------------------------------------------
    def complete_sale(self, event=None):
        if not auth.can(self.user, "sell"):
            messagebox.showerror(t("msg.access_denied"), t("msg.no_permission"))
            return
        if not self.cart:
            self.show_notification(t("sales.cart_empty"), is_error=True)
            return
        for product, pieces_qty, *_ in self.cart:
            ptype = product[10] if len(product) > 10 else "normal"
            if ptype == "telecom":
                continue
            if product[7] < pieces_qty:
                self.show_notification(
                    t("msg.stock_insufficient", available=product[7]),
                    is_error=True)
                return

        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = 0.0
        try:
            for product, pieces_qty, line_total, profit, _u, _dq in self.cart:
                db.add_sale(product[0], pieces_qty, profit, line_total, date=stamp)
                total += line_total
        except Exception as e:
            messagebox.showerror(t("msg.error"), t("sales.save_error", e=e))
            return
        backup.do_backup()
        self.show_notification(t("sales.cash_in", total=total))
        self.clear_cart()

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------
    def show_notification(self, message, is_error=False):
        if self.notification_label and self.notification_label.winfo_exists():
            self.notification_label.destroy()
        color = theme.RED if is_error else theme.GREEN
        self.notification_label = tk.Label(self.notification_frame, text=message,
                                           bg=color, fg="white",
                                           font=self.font(9))
        self.notification_label.pack(fill="both", expand=True)
        self.frame.after(2200, self.hide_notification)

    def hide_notification(self):
        if self.notification_label and self.notification_label.winfo_exists():
            self.notification_label.destroy()
        self.notification_label = None

    # ------------------------------------------------------------------
    def on_show(self):
        self.load_telecom_products()
        self.set_state("SCAN")
        self.setup_keyboard_shortcuts()
        self.barcode_entry.focus_set()

    def on_hide(self):
        self._unbind_shortcuts()
        if self.active_popup and self.active_popup.winfo_exists():
            self.active_popup.destroy()
        self.active_popup = None