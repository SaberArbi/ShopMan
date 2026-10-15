# screens/sales.py
import tkinter as tk
from tkinter import ttk, messagebox

from database import db_operations as db
from utils import auth, helpers, i18n
from utils.i18n import t


TELECOM_SHORTCUTS = {
    'F1': 'TELECOM 1.3',
    'F2': 'TELECOM 5.9',
    'F3': 'ORANGE 1.3',
    'F4': 'ORANGE 5.9',
    'F5': 'OOREDOO 1.3',
    'F6': 'OOREDOO 5.9',
}


class SalesScreen:
    def __init__(self, root, switch_callback, user=None):
        self.root = root
        self.switch = switch_callback
        self.user = user
        self.frame = tk.Frame(root, bg='#f0f0f0')

        self.cart = []
        self.active_popup = None
        self.notification_label = None
        self.telecom_products = []
        self.telecom_by_name = {}
        self.search_results = []
        self.search_listbox_products = []
        self.after_id = None
        self.state = "SCAN"

        self.load_telecom_products()
        self.setup_ui()
        self.setup_keyboard_shortcuts()

    def _font(self, size, weight="normal"):
        return i18n.ui_font(size, weight)

    def load_telecom_products(self):
        self.telecom_products = db.get_telecom_products()
        self.telecom_by_name = {p[1]: p for p in self.telecom_products}

    def setup_ui(self):
        FONT_TITLE = self._font(13, 'bold')
        FONT_BOLD  = self._font(10, 'bold')
        FONT_BODY  = self._font(10)
        FONT_SMALL = self._font(9)

        # ============================================================
        # TOP BAR — uses grid for reliable left/center/right layout
        # ============================================================
        top = tk.Frame(self.frame, bg='#27ae60', height=55)
        top.pack(fill='x')
        top.pack_propagate(False)

        top.grid_rowconfigure(0, weight=1)
        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=0)
        top.grid_columnconfigure(2, weight=1)

        rtl = i18n.is_rtl()
        # Column mapping flips under RTL
        if rtl:
            start_col, end_col = 2, 0
            start_sticky, end_sticky = 'e', 'w'
        else:
            start_col, end_col = 0, 2
            start_sticky, end_sticky = 'w', 'e'

        # --- START-side buttons (Produits / Historique / Utilisateurs) ---
        start_btns = tk.Frame(top, bg='#27ae60')
        start_btns.grid(row=0, column=start_col, sticky=start_sticky,
                        padx=8, pady=8)

        if auth.can(self.user, "manage_products"):
            tk.Button(start_btns, text=t("nav.products"),
                      bg='#2ecc71', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('products')
                      ).pack(side=i18n.side_start(), padx=3)
        if auth.can(self.user, "view_history"):
            tk.Button(start_btns, text=t("nav.history"),
                      bg='#2ecc71', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('history')
                      ).pack(side=i18n.side_start(), padx=3)
        if auth.can(self.user, "manage_users"):
            tk.Button(start_btns, text=t("nav.users"),
                      bg='#2ecc71', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('users')
                      ).pack(side=i18n.side_start(), padx=3)

        # --- Center title ---
        tk.Label(top, text=t("sales.title"), bg='#27ae60', fg='white',
                 font=FONT_TITLE).grid(row=0, column=1, padx=20)

        # --- END-side buttons (Corbeille / Rapports) ---
        end_btns = tk.Frame(top, bg='#27ae60')
        end_btns.grid(row=0, column=end_col, sticky=end_sticky,
                      padx=8, pady=8)

        if auth.can(self.user, "view_deleted_sales"):
            tk.Button(end_btns, text=t("history.deleted_btn"),
                      bg='#7f1d1d', fg='white',
                      font=FONT_BODY, width=13, relief='flat',
                      command=lambda: self.switch('deleted')
                      ).pack(side=i18n.side_start(), padx=3)
        if auth.can(self.user, "view_reports"):
            tk.Button(end_btns, text=t("nav.reports"),
                      bg='#2ecc71', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('reports')
                      ).pack(side=i18n.side_start(), padx=3)

        # ============================================================
        # Main area
        # ============================================================
        main = tk.Frame(self.frame, bg='#f0f0f0')
        main.pack(fill='both', expand=True, padx=5, pady=5)

        scan_col = tk.Frame(main, bg='#f0f0f0', width=360)
        scan_col.pack(side=i18n.side_start(), fill='both', padx=(0, 5))
        scan_col.pack_propagate(False)

        cart_col = tk.Frame(main, bg='white', relief='groove', bd=1)
        cart_col.pack(side=i18n.side_end(), fill='both', expand=True)

        # State indicator
        self.state_frame = tk.Frame(scan_col, bg='#34495e', height=26)
        self.state_frame.pack(fill='x', pady=(0, 3))
        self.state_frame.pack_propagate(False)
        self.state_label = tk.Label(self.state_frame, text="",
                                    bg='#34495e', fg='white', font=FONT_SMALL)
        self.state_label.pack(pady=4)

        # Scan/search
        barcode_frame = tk.Frame(scan_col, bg='white', relief='groove', bd=1)
        barcode_frame.pack(fill='x', pady=(0, 5))

        tk.Label(barcode_frame, text=t("sales.scanner_search"), bg='white',
                 fg='#2c3e50', font=FONT_BOLD).pack(pady=3)

        hint_frame = tk.Frame(barcode_frame, bg='white')
        hint_frame.pack(fill='x', padx=5)
        tk.Label(hint_frame, text=t("sales.hint_scan"), bg='white',
                 fg='#7f8c8d', font=FONT_SMALL
                 ).pack(side=i18n.side_start(), padx=2)
        tk.Label(hint_frame, text=t("sales.hint_search"), bg='white',
                 fg='#7f8c8d', font=FONT_SMALL
                 ).pack(side=i18n.side_end(), padx=2)

        self.barcode_entry = tk.Entry(barcode_frame,
                                      font=self._font(14),
                                      bg='#f8f9fa', fg='#2c3e50',
                                      relief='solid', bd=1,
                                      justify=i18n.justify_text())
        self.barcode_entry.pack(fill='x', padx=5, pady=5, ipady=3)
        self.barcode_entry.bind('<KeyRelease>', self.on_barcode_key)
        self.barcode_entry.bind('<Return>', self.process_barcode)
        self.barcode_entry.bind('<Down>', self.focus_search_results)
        self.barcode_entry.bind('<space>', self.on_barcode_space)

        self.search_frame = tk.Frame(scan_col, bg='white',
                                     relief='solid', bd=1)
        self.search_listbox = tk.Listbox(self.search_frame, height=6,
                                         font=FONT_BODY,
                                         selectbackground='#3498db',
                                         selectforeground='white',
                                         bg='white', fg='#2c3e50')
        self.search_listbox.pack(fill='both', expand=True, padx=1, pady=1)
        self.search_listbox.bind('<Button-1>', self.on_search_click)
        self.search_listbox.bind('<Double-Button-1>', self.select_from_search)
        self.search_listbox.bind('<Return>', self.select_from_search)
        self.search_listbox.bind('<KP_Enter>', self.select_from_search)
        self.search_listbox.bind('<Escape>',
                                 lambda e: self._dismiss_search())

        telecom_frame = tk.Frame(scan_col, bg='white',
                                 relief='groove', bd=1)
        telecom_frame.pack(fill='x', pady=(0, 5))

        tk.Label(telecom_frame, text=t("sales.telecom_shortcuts"), bg='white',
                 fg='#2c3e50', font=FONT_BOLD).pack(pady=3)

        grid = tk.Frame(telecom_frame, bg='white')
        grid.pack(pady=4)

        operators = [
            ('#3498db', 'TELECOM 1.3', 'F1'),
            ('#3498db', 'TELECOM 5.9', 'F2'),
            ('#f39c12', 'ORANGE 1.3', 'F3'),
            ('#f39c12', 'ORANGE 5.9', 'F4'),
            ('#e74c3c', 'OOREDOO 1.3', 'F5'),
            ('#e74c3c', 'OOREDOO 5.9', 'F6'),
        ]
        for i, (color, name, key) in enumerate(operators):
            r, c = i // 2, i % 2
            if rtl:
                c = 1 - c
            btn = tk.Button(grid, text=f'[{key}] {name}',
                            bg=color, fg='white',
                            font=FONT_SMALL, width=15, height=1, relief='flat',
                            command=lambda n=name: self.add_telecom_to_cart(n))
            btn.grid(row=r, column=c, padx=2, pady=2)
            self.create_tooltip(btn, f"Raccourci: {key}")

        shortcuts_frame = tk.Frame(scan_col, bg='#34495e', height=26)
        shortcuts_frame.pack(fill='x', pady=(5, 0))
        shortcuts_frame.pack_propagate(False)
        tk.Label(shortcuts_frame, text=t("sales.shortcuts_bar"),
                 bg='#34495e', fg='white', font=FONT_SMALL).pack(pady=4)

        self.notification_frame = tk.Frame(scan_col, bg='#f0f0f0', height=26)
        self.notification_frame.pack(fill='x')
        self.notification_frame.pack_propagate(False)

        # Cart header
        cart_header = tk.Frame(cart_col, bg='white')
        cart_header.pack(fill='x', padx=5, pady=5)
        tk.Label(cart_header, text=t("sales.cart"), bg='white', fg='#2c3e50',
                 font=FONT_BOLD).pack(side=i18n.side_start())
        tk.Label(cart_header, text=t("sales.cart_pay_hint"), bg='white',
                 fg='#27ae60', font=FONT_BOLD).pack(side=i18n.side_end())

        cart_container = tk.Frame(cart_col, bg='white')
        cart_container.pack(fill='both', expand=True, padx=5, pady=5)

        style = ttk.Style()
        style.configure('Cart.Treeview',
                        background='white', foreground='black',
                        fieldbackground='white',
                        font=FONT_BODY, rowheight=26)
        style.configure('Cart.Treeview.Heading',
                        font=FONT_BOLD, background='#ecf0f1',
                        foreground='black')

        columns = ('Produit', 'Qté', 'Unité', 'Prix', 'Total')
        self.cart_tree = ttk.Treeview(cart_container, columns=columns,
                                      show='headings', height=20,
                                      style='Cart.Treeview')
        headings = [
            t("lbl.product"), t("lbl.quantity"), t("lbl.unit"),
            t("sales.price"), t("lbl.total"),
        ]
        widths = [260, 90, 70, 80, 90]
        for col, hdr, w in zip(columns, headings, widths):
            self.cart_tree.heading(col, text=hdr)
            self.cart_tree.column(col, width=w, minwidth=w, anchor='center')

        cart_scroll = ttk.Scrollbar(cart_container, orient='vertical',
                                    command=self.cart_tree.yview)
        self.cart_tree.configure(yscrollcommand=cart_scroll.set)
        self.cart_tree.pack(side=i18n.side_start(), fill='both', expand=True)
        cart_scroll.pack(side=i18n.side_end(), fill='y')

        cart_actions = tk.Frame(cart_col, bg='white')
        cart_actions.pack(fill='x', padx=5, pady=5)

        tk.Button(cart_actions, text=t("sales.btn_remove"), bg='#e74c3c',
                  fg='white', font=FONT_BOLD, width=9, relief='flat',
                  command=self.remove_from_cart
                  ).pack(side=i18n.side_start(), padx=2)
        tk.Button(cart_actions, text=t("sales.btn_clear"), bg='#95a5a6',
                  fg='white', font=FONT_BOLD, width=9, relief='flat',
                  command=self.clear_cart
                  ).pack(side=i18n.side_start(), padx=2)

        pay_btn = tk.Button(cart_actions, text=t("sales.btn_pay"),
                            bg='#27ae60', fg='white',
                            font=self._font(12, 'bold'),
                            width=15, relief='flat',
                            command=self.complete_sale)
        pay_btn.pack(side=i18n.side_end(), padx=2)
        self.create_tooltip(pay_btn, "Raccourci: ESPACE")

        total_frame = tk.Frame(cart_col, bg='white')
        total_frame.pack(fill='x', padx=5, pady=5)
        tk.Label(total_frame, text=t("lbl.total") + ':', bg='white',
                 fg='#2c3e50', font=self._font(14)
                 ).pack(side=i18n.side_start())
        self.total_label = tk.Label(total_frame, text='0.00 DT', bg='white',
                                    fg='#27ae60',
                                    font=self._font(14, 'bold'))
        self.total_label.pack(side=i18n.side_end())

        self.set_state("SCAN")

    # ============================================================
    # Everything below is unchanged behavior
    # ============================================================
    def create_tooltip(self, widget, text):
        def enter(_event):
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            tk.Label(self.tooltip, text=text, bg='#ffffe0',
                     relief='solid', bd=1).pack()

        def leave(_event):
            if hasattr(self, 'tooltip') and self.tooltip.winfo_exists():
                self.tooltip.destroy()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

    def setup_keyboard_shortcuts(self):
        self.unbind_shortcuts()
        for key in TELECOM_SHORTCUTS:
            self.frame.bind_all(f'<{key}>', self.on_telecom_key)
        self.frame.bind_all('<space>', self.on_pay_key)
        self.frame.bind_all('<Escape>', self.on_escape)

    def unbind_shortcuts(self):
        for key in TELECOM_SHORTCUTS:
            self.frame.unbind_all(f'<{key}>')
        self.frame.unbind_all('<space>')
        self.frame.unbind_all('<Escape>')

    def _barcode_has_focus(self):
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
        if self.barcode_entry.get() == '':
            if self.cart:
                self.complete_sale()
            return "break"
        return None

    def on_pay_key(self, event):
        if self.state in ("POPUP_ACTIVE", "SEARCHING"):
            return
        if self._barcode_has_focus():
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

    def set_state(self, new_state):
        self.state = new_state
        if new_state == "SCAN":
            self.state_label.config(text=t("sales.state_scan"))
            self.state_frame.config(bg='#34495e')
            self.state_label.config(bg='#34495e')
        elif new_state == "SEARCHING":
            self.state_label.config(text=t("sales.state_searching"))
            self.state_frame.config(bg='#f39c12')
            self.state_label.config(bg='#f39c12')
        elif new_state == "POPUP_ACTIVE":
            self.state_label.config(text=t("sales.state_popup"))
            self.state_frame.config(bg='#9b59b6')
            self.state_label.config(bg='#9b59b6')

    def on_barcode_key(self, event):
        if self.after_id:
            self.frame.after_cancel(self.after_id)
            self.after_id = None
        if self.state == "POPUP_ACTIVE":
            return
        if event.keysym == 'Down' and self.search_frame.winfo_ismapped():
            self.focus_search_results()
            return
        value = self.barcode_entry.get()
        if value.isdigit():
            self.set_state("SCAN")
            self._dismiss_search()
            return
        if len(value) >= 1:
            self.set_state("SEARCHING")
            self.after_id = self.frame.after(250,
                                             lambda: self.search_products(value))
        else:
            self.set_state("SCAN")
            self._dismiss_search()

    def focus_search_results(self, event=None):
        if self.search_frame.winfo_ismapped() and self.search_listbox.size() > 0:
            self.search_listbox.focus_set()
            self.search_listbox.selection_clear(0, tk.END)
            self.search_listbox.selection_set(0)
            return "break"

    def validate_numeric(self, char):
        return char.isdigit() or char == ""

    def validate_decimal(self, char):
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
            self.search_listbox.insert(tk.END,
                                       f"{p[2][:30]}  —  {p[5]:.2f} DT")
        self.search_frame.pack(fill='x', pady=(0, 5),
                               after=self.barcode_entry.master)

    def _dismiss_search(self):
        self.search_frame.pack_forget()
        self.search_results = []
        self.search_listbox_products = []

    def on_search_click(self, event):
        self.select_from_search()

    def select_from_search(self, event=None):
        selection = self.search_listbox.curselection()
        if not selection or not self.search_listbox_products:
            return
        idx = selection[0]
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

    def _open_product_popup(self, product):
        product_type = product[10] if len(product) > 10 else 'normal'
        unit = product[6]
        if product_type == 'cigarette':
            self.show_cigarette_popup(product)
        elif unit == 'gram':
            self.show_gram_popup(product)
        elif unit == 'pack':
            self.show_pack_popup(product)
        else:
            ok = self.add_to_cart(product, 1, 'piece', 1,
                                  product[5], product[5] - product[4])
            if ok:
                self.show_notification(t("sales.added", name=product[2]))

    def _quantity_popup(self, product, *, title, header_lines,
                        unit_options, default_unit, compute, stock_check=None):
        if self.active_popup and self.active_popup.winfo_exists():
            self.active_popup.destroy()
        self.set_state("POPUP_ACTIVE")
        self.unbind_shortcuts()

        FONT_BOLD  = self._font(10, 'bold')
        FONT_BODY  = self._font(10)
        FONT_SMALL = self._font(9)

        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.geometry("430x380")
        popup.transient(self.root)
        popup.grab_set()
        popup.focus_force()
        popup.configure(bg='#f0f0f0')
        self.active_popup = popup

        x = self.barcode_entry.winfo_rootx()
        y = self.barcode_entry.winfo_rooty() + \
            self.barcode_entry.winfo_height() + 5
        popup.geometry(f"+{x}+{y}")

        tk.Label(popup, text="\n".join(header_lines),
                 font=self._font(11, 'bold'),
                 bg='#f0f0f0', fg='#2c3e50',
                 justify='center').pack(pady=8)

        unit_var = tk.StringVar(value=default_unit)
        unit_frame = tk.Frame(popup, bg='#f0f0f0')
        unit_frame.pack(pady=4)
        tk.Label(unit_frame, text=t("sales.sell_in"), font=FONT_BODY,
                 bg='#f0f0f0', fg='#2c3e50'
                 ).pack(side=i18n.side_start(), padx=5)
        for label, value in unit_options:
            tk.Radiobutton(unit_frame, text=label, variable=unit_var,
                           value=value, font=FONT_BODY,
                           bg='#f0f0f0', fg='#2c3e50',
                           activebackground='#f0f0f0',
                           selectcolor='#f0f0f0'
                           ).pack(side=i18n.side_start(), padx=4)

        tk.Label(popup, text=t("sales.qty"), font=FONT_BODY,
                 bg='#f0f0f0', fg='#2c3e50').pack(pady=(8, 2))
        vcmd = (popup.register(self.validate_decimal), '%S')
        entry = tk.Entry(popup, font=self._font(16), width=12,
                         justify='center', validate='key',
                         validatecommand=vcmd,
                         bg='white', fg='#2c3e50', relief='solid', bd=1)
        entry.pack(pady=4, ipady=4)
        entry.focus()
        entry.select_range(0, tk.END)

        preview_frame = tk.Frame(popup, bg='#f0f0f0')
        preview_frame.pack(pady=6)
        tk.Label(preview_frame, text=t("lbl.total") + ': ',
                 font=self._font(12),
                 bg='#f0f0f0', fg='#2c3e50'
                 ).pack(side=i18n.side_start())
        preview_label = tk.Label(preview_frame, text="0.00 DT",
                                 font=self._font(12, 'bold'),
                                 bg='#f0f0f0', fg='#27ae60')
        preview_label.pack(side=i18n.side_start())

        warning_label = tk.Label(popup, text="", font=FONT_SMALL,
                                 bg='#f0f0f0', fg='#e74c3c')
        warning_label.pack()

        def update_preview(*_):
            warning_label.config(text="")
            try:
                qty = float(entry.get() or '0')
                result = compute(qty, unit_var.get())
                preview_label.config(text=f"{result['total']:.2f} DT")
                if stock_check:
                    msg = stock_check(qty, unit_var.get())
                    if msg:
                        warning_label.config(text=msg)
            except (ValueError, KeyError):
                preview_label.config(text="0.00 DT")

        entry.bind('<KeyRelease>', update_preview)
        unit_var.trace_add('write', update_preview)

        tk.Label(popup, text=t("sales.popup_hint"),
                 fg='#7f8c8d', bg='#f0f0f0',
                 font=FONT_SMALL).pack(pady=4)

        def cycle_unit():
            values = [v for _, v in unit_options]
            idx = values.index(unit_var.get())
            unit_var.set(values[(idx + 1) % len(values)])

        def do_add():
            try:
                qty = float(entry.get() or '0')
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
                product,
                result['pieces_qty'],
                result['unit_display'],
                result['display_qty'],
                result['total'],
                result['profit'],
            )
            if ok:
                self.show_notification(
                    t("sales.added_qty",
                      qty=result['display_qty'],
                      unit=result['unit_display']))
            popup.destroy()
            self.on_popup_close()

        popup.bind('<Key-u>', lambda e: cycle_unit())
        popup.bind('<Key-U>', lambda e: cycle_unit())
        popup.bind('<Return>', lambda e: do_add())
        popup.bind('<KP_Enter>', lambda e: do_add())
        popup.bind('<Escape>', lambda e: self.on_popup_close())

        btn_frame = tk.Frame(popup, bg='#f0f0f0')
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text=t("btn.add"), command=do_add,
                  bg='#27ae60', fg='white', width=10,
                  font=FONT_BOLD, relief='flat'
                  ).pack(side=i18n.side_start(), padx=5)
        tk.Button(btn_frame, text=t("btn.cancel"),
                  command=self.on_popup_close,
                  bg='#95a5a6', fg='white', width=10,
                  font=FONT_BOLD, relief='flat'
                  ).pack(side=i18n.side_start(), padx=5)

    def show_gram_popup(self, product):
        price_per_kg = product[5]
        buy_per_kg = product[4]

        def compute(qty, unit):
            if unit == 'g':
                return dict(pieces_qty=qty, display_qty=qty, unit_display='g',
                            total=(qty / 1000) * price_per_kg,
                            profit=(qty / 1000) * (price_per_kg - buy_per_kg))
            return dict(pieces_qty=qty * 1000, display_qty=qty,
                        unit_display='kg',
                        total=qty * price_per_kg,
                        profit=qty * (price_per_kg - buy_per_kg))

        self._quantity_popup(
            product,
            title=t("sales.popup_weight_title"),
            header_lines=[product[2],
                          t("sales.price_per_kg", p=price_per_kg)],
            unit_options=[(t("sales.opt_grams"), 'g'),
                          (t("sales.opt_kilograms"), 'kg')],
            default_unit='g',
            compute=compute,
        )

    def show_pack_popup(self, product):
        ppp = product[9] or 1
        price_per_pack = product[5]
        price_per_unit = (product[8] if product[8] > 0
                          else price_per_pack / ppp)
        buy_per_pack = product[4]
        buy_per_unit = buy_per_pack / ppp

        def compute(qty, unit):
            if unit == 'pack':
                return dict(pieces_qty=qty * ppp, display_qty=qty,
                            unit_display='pack',
                            total=qty * price_per_pack,
                            profit=qty * (price_per_pack - buy_per_pack))
            return dict(pieces_qty=qty, display_qty=qty,
                        unit_display='unité',
                        total=qty * price_per_unit,
                        profit=qty * (price_per_unit - buy_per_unit))

        self._quantity_popup(
            product,
            title=t("sales.popup_pack_title"),
            header_lines=[product[2],
                          t("sales.pack_price", p=price_per_pack),
                          t("sales.unit_price", p=price_per_unit)],
            unit_options=[(t("sales.opt_packs"), 'pack'),
                          (t("sales.opt_units"), 'unité')],
            default_unit='unité',
            compute=compute,
        )

    def show_cigarette_popup(self, product):
        PACK = 20
        stock_cigarettes = int(product[7])
        pack_price = product[5]
        single_price = (product[11]
                        if len(product) > 11 and product[11] > 0
                        else pack_price / PACK)
        buy_per_pack = product[4]
        single_cost = (product[11]
                       if len(product) > 11 and product[11] > 0
                       else buy_per_pack / PACK)

        def compute(qty, unit):
            if unit == 'pack':
                return dict(pieces_qty=qty * PACK, display_qty=qty,
                            unit_display='pack',
                            total=qty * pack_price,
                            profit=qty * (pack_price - buy_per_pack))
            return dict(pieces_qty=qty, display_qty=qty,
                        unit_display='unité',
                        total=qty * single_price,
                        profit=qty * (single_price - single_cost))

        def stock_check(qty, unit):
            needed = qty * PACK if unit == 'pack' else qty
            if needed > stock_cigarettes:
                return t("msg.stock_insufficient",
                         available=stock_cigarettes)
            return None

        self._quantity_popup(
            product,
            title=t("sales.popup_cigarette_title"),
            header_lines=[product[2],
                          t("sales.stock_cigarettes", n=stock_cigarettes),
                          t("sales.pack_price", p=pack_price),
                          t("sales.unit_price", p=single_price)],
            unit_options=[(t("sales.opt_packs"), 'pack'),
                          (t("sales.opt_units"), 'unité')],
            default_unit='unité',
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

    def add_telecom_to_cart(self, name):
        full_name = name + " DT"
        product = self.telecom_by_name.get(full_name)
        if not product:
            self.show_notification(
                t("sales.not_found_full", name=full_name), is_error=True)
            return
        full_product = (
            product[0], None, product[1], None,
            product[2], product[3], 'piece', 999999,
            0, 1, 'telecom', 0,
        )
        ok = self.add_to_cart(full_product, 1, 'piece', 1,
                              product[3], product[3] - product[2])
        if ok:
            self.show_notification(t("sales.added", name=product[1]))
        self.barcode_entry.focus_set()

    def add_to_cart(self, product, pieces_qty, unit_display, display_qty,
                    price, profit):
        product_type = product[10] if len(product) > 10 else 'normal'
        is_telecom = (product_type == 'telecom')
        if not is_telecom and product[7] < pieces_qty:
            self.show_notification(
                t("msg.stock_only", stock=product[7]), is_error=True)
            return False
        for i, (p, q, tot, pr, u, dq) in enumerate(self.cart):
            if p[0] == product[0] and u == unit_display:
                new_pieces = q + pieces_qty
                if not is_telecom and product[7] < new_pieces:
                    self.show_notification(
                        t("msg.stock_only", stock=product[7]),
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
        selected = self.cart_tree.selection()
        if not selected:
            return
        idx = self.cart_tree.index(selected[0])
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
        for product, _pieces, line_total, _profit, unit_used, display_qty in self.cart:
            unit_price = (line_total / display_qty
                          if display_qty > 0 else line_total)
            self.cart_tree.insert('', 'end', values=(
                product[2][:32],
                f"{display_qty:g}",
                unit_used,
                f"{unit_price:.2f}",
                f"{line_total:.2f}",
            ))
            total += line_total
        self.total_label.config(text=f"{total:.2f} DT")

    def complete_sale(self, event=None):
        if not auth.can(self.user, "sell"):
            messagebox.showerror(t("msg.access_denied"),
                                 t("msg.no_permission"))
            return
        if not self.cart:
            self.show_notification(t("sales.cart_empty"), is_error=True)
            return
        for product, pieces_qty, *_rest in self.cart:
            product_type = product[10] if len(product) > 10 else 'normal'
            if product_type == 'telecom':
                continue
            if product[7] < pieces_qty:
                self.show_notification(
                    t("msg.stock_insufficient", available=product[7]),
                    is_error=True)
                return
        from datetime import datetime
        cart_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = 0.0
        try:
            for product, pieces_qty, line_total, profit, _u, _dq in self.cart:
                db.add_sale(product[0], pieces_qty, profit, line_total,
                            date=cart_timestamp)
                total += line_total
        except Exception as e:
            messagebox.showerror(t("msg.error"),
                                 t("sales.save_error", e=e))
            return
        helpers.auto_backup()
        self.show_notification(t("sales.cash_in", total=total))
        self.clear_cart()

    def show_notification(self, message, is_error=False):
        if self.notification_label and self.notification_label.winfo_exists():
            self.notification_label.destroy()
        color = '#e74c3c' if is_error else '#27ae60'
        self.notification_label = tk.Label(self.notification_frame,
                                           text=message,
                                           bg=color, fg='white',
                                           font=self._font(9))
        self.notification_label.pack(fill='both', expand=True)
        self.frame.after(2200, self.hide_notification)

    def hide_notification(self):
        if self.notification_label and self.notification_label.winfo_exists():
            self.notification_label.destroy()
        self.notification_label = None

    def show(self):
        self.frame.pack(fill='both', expand=True)
        self.load_telecom_products()
        self.set_state("SCAN")
        self.setup_keyboard_shortcuts()
        self.barcode_entry.focus_set()

    def hide(self):
        self.frame.pack_forget()
        self.unbind_shortcuts()
        if self.active_popup and self.active_popup.winfo_exists():
            self.active_popup.destroy()
        self.active_popup = None
