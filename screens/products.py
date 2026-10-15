# screens/products.py
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from database import db_operations as db
from utils import auth, i18n
from utils.i18n import t

try:
    from PIL import Image, ImageTk  # noqa: F401
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


DARK_BG   = '#2c3e50'
DARK_FG   = 'white'
LIGHT_BG  = 'white'
LIGHT_FG  = '#2c3e50'
MUTED_FG  = '#7f8c8d'


class ProductsScreen:
    def __init__(self, root, switch_callback, user=None):
        self.root = root
        self.switch = switch_callback
        self.user = user
        self.frame = tk.Frame(root, bg='#f0f0f0')

        self.photo_path = None
        self.current_product_id = None
        self.current_product_type = None
        self._loading = False

        self.setup_ui()
        self.load_products()

    def _font(self, size, weight="normal"):
        return i18n.ui_font(size, weight)

    def _require_manage_products(self):
        if not auth.can(self.user, "manage_products"):
            messagebox.showerror(t("msg.access_denied"),
                                 t("products.owner_only"))
            return False
        return True

    def setup_ui(self):
        FONT_TITLE = self._font(13, 'bold')
        FONT_BOLD  = self._font(10, 'bold')
        FONT_BODY  = self._font(10)
        FONT_SMALL = self._font(9)

        top = tk.Frame(self.frame, bg=DARK_BG, height=55)
        top.pack(fill='x')
        top.pack_propagate(False)

        left_btns = tk.Frame(top, bg=DARK_BG)
        left_btns.pack(side=i18n.side_start(), padx=8, pady=8)
        if auth.can(self.user, "sell"):
            tk.Button(left_btns, text=t("nav.back_to_sales"), bg='#34495e', fg=DARK_FG,
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('sales')
                      ).pack(side=i18n.side_start(), padx=3)
        if auth.can(self.user, "view_history"):
            tk.Button(left_btns, text=t("nav.history"), bg='#34495e', fg=DARK_FG,
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('history')
                      ).pack(side=i18n.side_start(), padx=3)

        tk.Label(top, text=t("products.title"), bg=DARK_BG, fg=DARK_FG,
                 font=FONT_TITLE).pack(side='top', pady=10)

        right_btns = tk.Frame(top, bg=DARK_BG)
        right_btns.pack(side=i18n.side_end(), padx=8, pady=8)
        if auth.can(self.user, "manage_users"):
            tk.Button(right_btns, text=t("nav.users"), bg='#34495e', fg=DARK_FG,
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('users')
                      ).pack(side=i18n.side_end(), padx=3)
        if auth.can(self.user, "view_reports"):
            tk.Button(right_btns, text=t("nav.reports_arrow"), bg='#34495e', fg=DARK_FG,
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('reports')
                      ).pack(side=i18n.side_end(), padx=3)

        main = tk.Frame(self.frame, bg='#f0f0f0')
        main.pack(fill='both', expand=True, padx=10, pady=10)

        # Form on start side, list on end side
        left = tk.Frame(main, bg=LIGHT_BG, relief='groove', bd=2, width=380)
        left.pack(side=i18n.side_start(), fill='y', padx=(0, 10))
        left.pack_propagate(False)

        tk.Label(left, text=t("products.add_modify"), bg=LIGHT_BG, fg=LIGHT_FG,
                 font=FONT_TITLE).pack(pady=(12, 8))

        self.entries = {}
        for label, key in (
            (t("products.barcode"), 'barcode'),
            (t("products.name"), 'name'),
            (t("products.buy_price"), 'buy'),
            (t("products.sell_price"), 'sell'),
            (t("products.stock"), 'stock'),
        ):
            row = tk.Frame(left, bg=LIGHT_BG)
            row.pack(fill='x', padx=10, pady=4)
            tk.Label(row, text=label, width=14, anchor=i18n.anchor_start(),
                     bg=LIGHT_BG, fg=LIGHT_FG,
                     font=FONT_BODY).pack(side=i18n.side_start())
            e = tk.Entry(row, font=FONT_BODY,
                         bg='#f8f9fa', fg='#2c3e50',
                         relief='solid', bd=1,
                         justify=i18n.justify_text())
            e.pack(side=i18n.side_start(), fill='x', expand=True, ipady=2)
            self.entries[key] = e

        row = tk.Frame(left, bg=LIGHT_BG)
        row.pack(fill='x', padx=10, pady=4)
        tk.Label(row, text=t("products.unit_label"), width=14,
                 anchor=i18n.anchor_start(),
                 bg=LIGHT_BG, fg=LIGHT_FG,
                 font=FONT_BODY).pack(side=i18n.side_start())

        self.unit_var = tk.StringVar(value='piece')
        unit_frame = tk.Frame(row, bg=LIGHT_BG)
        unit_frame.pack(side=i18n.side_start(), anchor=i18n.anchor_start())
        for text, val, cmd in (
            (t("products.unit_piece"),     'piece',     self.toggle_pack_options),
            (t("products.unit_gram"),      'gram',      self.toggle_pack_options),
            (t("products.unit_pack"),      'pack',      self.toggle_pack_options),
            (t("products.unit_cigarette"), 'cigarette', self.toggle_cigarette_options),
        ):
            tk.Radiobutton(unit_frame, text=text, variable=self.unit_var,
                           value=val, command=cmd,
                           bg=LIGHT_BG, fg=LIGHT_FG,
                           activebackground=LIGHT_BG,
                           selectcolor=LIGHT_BG,
                           font=FONT_SMALL).pack(side=i18n.side_start())

        self.pack_frame = tk.Frame(left, bg=LIGHT_BG)

        sub = tk.Frame(self.pack_frame, bg=LIGHT_BG)
        sub.pack(fill='x', padx=10, pady=3)
        tk.Label(sub, text=t("products.single_price"), width=14,
                 anchor=i18n.anchor_start(),
                 bg=LIGHT_BG, fg=LIGHT_FG,
                 font=FONT_BODY).pack(side=i18n.side_start())
        self.single_price_entry = tk.Entry(sub, width=10, font=FONT_BODY,
                                           bg='#f8f9fa', fg='#2c3e50',
                                           relief='solid', bd=1,
                                           justify=i18n.justify_text())
        self.single_price_entry.pack(side=i18n.side_start(), ipady=2)
        self.single_price_entry.insert(0, '0')

        sub = tk.Frame(self.pack_frame, bg=LIGHT_BG)
        sub.pack(fill='x', padx=10, pady=3)
        tk.Label(sub, text=t("products.pieces_per_pack"), width=14,
                 anchor=i18n.anchor_start(),
                 bg=LIGHT_BG, fg=LIGHT_FG,
                 font=FONT_BODY).pack(side=i18n.side_start())
        self.pieces_per_pack_entry = tk.Entry(sub, width=10, font=FONT_BODY,
                                              bg='#f8f9fa', fg='#2c3e50',
                                              relief='solid', bd=1,
                                              justify=i18n.justify_text())
        self.pieces_per_pack_entry.pack(side=i18n.side_start(), ipady=2)
        self.pieces_per_pack_entry.insert(0, '20')

        self.cigarette_frame = tk.Frame(left, bg=LIGHT_BG)

        sub = tk.Frame(self.cigarette_frame, bg=LIGHT_BG)
        sub.pack(fill='x', padx=10, pady=3)
        tk.Label(sub, text=t("products.cigarette_price"), width=14,
                 anchor=i18n.anchor_start(),
                 bg=LIGHT_BG, fg=LIGHT_FG,
                 font=FONT_BODY).pack(side=i18n.side_start())
        self.single_cigarette_entry = tk.Entry(sub, width=10, font=FONT_BODY,
                                               bg='#f8f9fa', fg='#2c3e50',
                                               relief='solid', bd=1,
                                               justify=i18n.justify_text())
        self.single_cigarette_entry.pack(side=i18n.side_start(), ipady=2)
        self.single_cigarette_entry.insert(0, '0')

        tk.Label(self.cigarette_frame,
                 text=t("products.cig_stock_hint"),
                 bg=LIGHT_BG, fg=MUTED_FG, font=FONT_SMALL,
                 justify=i18n.justify_text()
                 ).pack(pady=2, padx=10, anchor=i18n.anchor_start())

        tk.Button(left, text=t("btn.choose_photo"), font=FONT_BODY,
                  bg='#ecf0f1', fg=LIGHT_FG, relief='flat',
                  command=self.choose_photo).pack(pady=(10, 2))
        self.photo_label = tk.Label(left, text=t("products.no_photo"),
                                    bg=LIGHT_BG, fg=MUTED_FG, font=FONT_SMALL)
        self.photo_label.pack()

        actions = tk.Frame(left, bg=LIGHT_BG)
        actions.pack(pady=15)

        tk.Button(actions, text=t("btn.add"), bg='#27ae60', fg='white',
                  width=9, font=FONT_BOLD, relief='flat',
                  command=self.add_product).pack(side=i18n.side_start(), padx=3)
        tk.Button(actions, text=t("btn.modify"), bg='#f39c12', fg='white',
                  width=9, font=FONT_BOLD, relief='flat',
                  command=self.update_product).pack(side=i18n.side_start(), padx=3)
        tk.Button(actions, text=t("btn.clear"), bg='#95a5a6', fg='white',
                  width=9, font=FONT_BOLD, relief='flat',
                  command=self.clear_all).pack(side=i18n.side_start(), padx=3)

        right = tk.Frame(main, bg=LIGHT_BG, relief='groove', bd=2)
        right.pack(side=i18n.side_end(), fill='both', expand=True)

        search_frame = tk.Frame(right, bg=LIGHT_BG)
        search_frame.pack(fill='x', padx=10, pady=8)
        tk.Label(search_frame, text=t("products.search"), bg=LIGHT_BG,
                 fg=LIGHT_FG, font=FONT_BODY).pack(side=i18n.side_start())
        self.search_entry = tk.Entry(search_frame, font=FONT_BODY,
                                     bg='#f8f9fa', fg='#2c3e50',
                                     relief='solid', bd=1,
                                     justify=i18n.justify_text())
        self.search_entry.pack(side=i18n.side_start(), fill='x', expand=True,
                               padx=5, ipady=2)
        self.search_entry.bind('<KeyRelease>', self.search_products)

        style = ttk.Style()
        style.configure('Products.Treeview',
                        background=LIGHT_BG, foreground='black',
                        fieldbackground=LIGHT_BG,
                        font=FONT_BODY, rowheight=26)
        style.configure('Products.Treeview.Heading',
                        font=FONT_BOLD, background='#ecf0f1',
                        foreground='black')

        tree_container = tk.Frame(right, bg=LIGHT_BG)
        tree_container.pack(fill='both', expand=True, padx=10, pady=(0, 8))

        columns = ('id', 'barcode', 'name', 'buy', 'sell', 'unit', 'stock', 'ptype')
        headings = [
            t("products.col_id"), t("products.col_barcode"),
            t("products.col_name"), t("products.col_buy"),
            t("products.col_sell"), t("products.col_unit"),
            t("products.col_stock"), t("products.col_type"),
        ]
        self.tree = ttk.Treeview(tree_container, columns=columns,
                                 show='headings', height=20,
                                 style='Products.Treeview')
        widths = [45, 100, 220, 80, 80, 70, 130, 80]
        for col, hdr, w in zip(columns, headings, widths):
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=w,
                             anchor=(i18n.anchor_start()
                                     if col == 'name' else 'center'))

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

        self.tree.bind('<<TreeviewSelect>>', self.select_product)

        footer = tk.Frame(right, bg=LIGHT_BG)
        footer.pack(fill='x', padx=10, pady=(0, 10))

        tk.Button(footer, text=t("btn.delete_selection"), bg='#e74c3c', fg='white',
                  font=FONT_BOLD, relief='flat',
                  command=self.delete_product
                  ).pack(side=i18n.side_start(), padx=3)
        tk.Button(footer, text=t("btn.add_stock"), bg='#3498db', fg='white',
                  font=FONT_BOLD, relief='flat',
                  command=self.add_stock
                  ).pack(side=i18n.side_start(), padx=3)

    # --- Same methods as before: toggle_pack_options, toggle_cigarette_options,
    #     choose_photo, _read_form, add_product, update_product, delete_product,
    #     select_product, _fill_form, clear_form, clear_all, add_stock,
    #     _format_stock, _insert_product, load_products, search_products,
    #     show, hide ---
    # The bodies are unchanged; only the GUI-building bits above needed RTL.

    def toggle_pack_options(self):
        self.cigarette_frame.pack_forget()
        if self.unit_var.get() == 'pack':
            self.pack_frame.pack(fill='x', pady=4,
                                 after=self.entries['stock'].master)
        else:
            self.pack_frame.pack_forget()

    def toggle_cigarette_options(self):
        self.pack_frame.pack_forget()
        if self.unit_var.get() == 'cigarette':
            self.cigarette_frame.pack(fill='x', pady=4,
                                      after=self.entries['stock'].master)
        else:
            self.cigarette_frame.pack_forget()

    def choose_photo(self):
        path = filedialog.askopenfilename(
            filetypes=[('Images', '*.png *.jpg *.jpeg *.gif')])
        if path:
            self.photo_path = path
            self.photo_label.config(text=os.path.basename(path))

    def _read_form(self, editing=False):
        barcode = self.entries['barcode'].get().strip()
        name = self.entries['name'].get().strip()
        if not name:
            raise Exception(t("products.name_required"))
        buy_price = float(self.entries['buy'].get() or '0')
        sell_price = float(self.entries['sell'].get() or '0')
        if sell_price <= buy_price:
            raise Exception(t("products.sell_gt_buy"))
        unit = self.unit_var.get()
        if editing and self.current_product_type:
            product_type = self.current_product_type
        else:
            product_type = 'cigarette' if unit == 'cigarette' else 'normal'
        stock_input = float(self.entries['stock'].get() or '0')
        single_price = 0.0
        pieces_per_pack = 20
        single_cigarette_price = 0.0
        if unit == 'pack':
            single_price = float(self.single_price_entry.get() or '0')
            pieces_per_pack = int(float(self.pieces_per_pack_entry.get() or '20'))
            if pieces_per_pack <= 0:
                raise Exception(t("products.pieces_gt_zero"))
            stock = stock_input * pieces_per_pack
        elif unit == 'cigarette':
            single_cigarette_price = float(self.single_cigarette_entry.get() or '0')
            stock = stock_input
        else:
            stock = stock_input
        return {
            'barcode': barcode, 'name': name,
            'buy_price': buy_price, 'sell_price': sell_price,
            'unit': unit, 'stock': stock,
            'single_price': single_price,
            'pieces_per_pack': pieces_per_pack,
            'product_type': product_type,
            'single_cigarette_price': single_cigarette_price,
        }

    def add_product(self):
        if not self._require_manage_products():
            return
        try:
            data = self._read_form(editing=False)
            db.add_product(photo=self.photo_path, **data)
            messagebox.showinfo(t("msg.success"), t("products.success_added"))
            self.clear_all()
            self.load_products()
        except ValueError:
            messagebox.showerror(t("msg.error"), t("msg.invalid_numbers"))
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    def update_product(self):
        if not self._require_manage_products():
            return
        if not self.current_product_id:
            messagebox.showwarning(t("msg.warning"), t("products.select_first"))
            return
        try:
            data = self._read_form(editing=True)
            if not self.photo_path:
                for p in db.get_all_products():
                    if p[0] == self.current_product_id:
                        self.photo_path = p[3]
                        break
            db.update_product(self.current_product_id,
                              photo=self.photo_path, **data)
            messagebox.showinfo(t("msg.success"), t("products.success_updated"))
            self.clear_all()
            self.load_products()
        except ValueError:
            messagebox.showerror(t("msg.error"), t("msg.invalid_numbers"))
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    def delete_product(self):
        if not self._require_manage_products():
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(t("msg.warning"), t("products.select_first"))
            return
        if not messagebox.askyesno(t("msg.confirmation"),
                                   t("products.confirm_delete")):
            return
        product_id = int(self.tree.item(selected[0])['values'][0])
        try:
            db.delete_product(product_id)
            self.clear_all()
            self.load_products()
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    def select_product(self, event=None):
        if self._loading:
            return
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0])['values']
        if not values:
            return
        try:
            product_id = int(values[0])
        except (ValueError, TypeError):
            return
        product = next((p for p in db.get_all_products() if p[0] == product_id), None)
        if not product:
            return
        self.clear_form()
        self._fill_form(product)

    def _fill_form(self, product):
        (pid, barcode, name, _photo, buy, sell, unit, stock,
         single_price, pieces_per_pack, _ptype, single_cig_price) = product
        self.entries['barcode'].insert(0, barcode or '')
        self.entries['name'].insert(0, name or '')
        self.entries['buy'].insert(0, f"{buy}")
        self.entries['sell'].insert(0, f"{sell}")
        self.unit_var.set(unit)
        if unit == 'pack':
            self.pack_frame.pack(fill='x', pady=4,
                                 after=self.entries['stock'].master)
            self.single_price_entry.delete(0, tk.END)
            self.single_price_entry.insert(0, f"{single_price}")
            self.pieces_per_pack_entry.delete(0, tk.END)
            self.pieces_per_pack_entry.insert(0, str(pieces_per_pack))
            ppp = pieces_per_pack or 1
            self.entries['stock'].insert(0, f"{stock / ppp:.2f}".rstrip('0').rstrip('.'))
        elif unit == 'cigarette':
            self.cigarette_frame.pack(fill='x', pady=4,
                                      after=self.entries['stock'].master)
            self.single_cigarette_entry.delete(0, tk.END)
            self.single_cigarette_entry.insert(0, f"{single_cig_price}")
            self.entries['stock'].insert(0, f"{stock:.0f}")
        else:
            self.entries['stock'].insert(0, f"{stock:.2f}".rstrip('0').rstrip('.'))
        self.current_product_id = pid
        self.current_product_type = _ptype
        if _photo:
            self.photo_path = _photo
            self.photo_label.config(text=os.path.basename(_photo))

    def clear_form(self):
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.unit_var.set('piece')
        self.pack_frame.pack_forget()
        self.cigarette_frame.pack_forget()
        self.single_price_entry.delete(0, tk.END)
        self.single_price_entry.insert(0, '0')
        self.pieces_per_pack_entry.delete(0, tk.END)
        self.pieces_per_pack_entry.insert(0, '20')
        self.single_cigarette_entry.delete(0, tk.END)
        self.single_cigarette_entry.insert(0, '0')
        self.photo_path = None
        self.photo_label.config(text=t("products.no_photo"))
        self.current_product_id = None
        self.current_product_type = None

    def clear_all(self):
        self.clear_form()
        self.tree.selection_remove(self.tree.selection())

    def add_stock(self):
        if not self._require_manage_products():
            return
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(t("msg.warning"), t("products.select_first"))
            return
        try:
            product_id = int(self.tree.item(selected[0])['values'][0])
        except (ValueError, TypeError):
            return
        product = next((p for p in db.get_all_products() if p[0] == product_id), None)
        if not product:
            return
        unit = product[6]
        current_stock = product[7]
        ppp = product[9] or 1

        dialog = tk.Toplevel(self.root)
        dialog.title(t("products.add_stock_title"))
        dialog.geometry("380x340")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg='#f0f0f0')

        tk.Label(dialog, text=f"{t('lbl.product')}: {product[2]}",
                 font=self._font(10, 'bold'),
                 bg='#f0f0f0', fg=LIGHT_FG).pack(pady=10)

        def make_entry(label, default=None):
            tk.Label(dialog, text=label, font=self._font(10),
                     bg='#f0f0f0', fg=LIGHT_FG).pack(pady=(8, 0))
            e = tk.Entry(dialog, font=self._font(10), width=12,
                         justify='center',
                         bg='white', fg='#2c3e50', relief='solid', bd=1)
            e.pack(pady=3, ipady=3)
            if default is not None:
                e.insert(0, default)
            return e

        packs_entry = pieces_entry = qty_entry = None
        if unit == 'pack':
            packs = int(current_stock // ppp)
            pieces = int(current_stock % ppp)
            tk.Label(dialog,
                     text=t("products.current_stock_pack", packs=packs, pieces=pieces),
                     font=self._font(10),
                     bg='#f0f0f0', fg=LIGHT_FG).pack()
            packs_entry = make_entry(t("products.add_packs"))
            pieces_entry = make_entry(t("products.add_pieces"), "0")
            packs_entry.focus()
        elif unit == 'cigarette':
            total_cig = int(current_stock)
            tk.Label(dialog,
                     text=t("products.current_stock_cig",
                            packs=total_cig // 20, units=total_cig % 20),
                     font=self._font(10),
                     bg='#f0f0f0', fg=LIGHT_FG).pack()
            tk.Label(dialog, text=t("products.add_cig"),
                     font=self._font(10, 'bold'),
                     bg='#f0f0f0', fg=LIGHT_FG).pack(pady=(8, 0))
            tk.Label(dialog, text=t("products.add_cig_hint"), fg=MUTED_FG,
                     bg='#f0f0f0', font=self._font(9)).pack()
            qty_entry = make_entry(t("sales.qty"))
            qty_entry.focus()
        elif unit == 'gram':
            tk.Label(dialog, text=t("products.current_stock_g", stock=current_stock),
                     font=self._font(10), bg='#f0f0f0', fg=LIGHT_FG).pack()
            qty_entry = make_entry(t("products.add_g"))
            qty_entry.focus()
        else:
            tk.Label(dialog, text=t("products.current_stock", stock=current_stock),
                     font=self._font(10), bg='#f0f0f0', fg=LIGHT_FG).pack()
            qty_entry = make_entry(t("products.qty_to_add"))
            qty_entry.focus()

        def submit(event=None):
            try:
                if unit == 'pack':
                    add_packs = float(packs_entry.get() or '0')
                    add_pieces = float(pieces_entry.get() or '0')
                    add_qty = add_packs * ppp + add_pieces
                else:
                    add_qty = float(qty_entry.get() or '0')
                if add_qty <= 0:
                    messagebox.showerror(t("msg.error"),
                                         t("products.positive_number"),
                                         parent=dialog)
                    return
                new_stock = current_stock + add_qty
                db.update_product(
                    product_id,
                    product[1], product[2], product[3],
                    product[4], product[5], product[6], new_stock,
                    product[8], product[9], product[10], product[11],
                )
                dialog.destroy()
                self.load_products()
                messagebox.showinfo(t("msg.success"), t("products.stock_added"))
            except ValueError:
                messagebox.showerror(t("msg.error"), t("msg.invalid_numbers"),
                                     parent=dialog)

        for e in (packs_entry, pieces_entry, qty_entry):
            if e is not None:
                e.bind('<Return>', submit)

        tk.Button(dialog, text=t("btn.add"), bg='#27ae60', fg='white',
                  font=self._font(10, 'bold'), width=10, relief='flat',
                  command=submit).pack(pady=15)
        dialog.wait_window()

    def _format_stock(self, product):
        unit = product[6]
        stock = product[7]
        ppp = product[9] or 1
        if unit == 'pack':
            return f"{int(stock // ppp)} {t('unit.packs_short')} + {int(stock % ppp)} {t('unit.pieces_short')}"
        if unit == 'gram':
            return f"{stock:g} g"
        if unit == 'cigarette':
            total = int(stock)
            return f"{total // 20} {t('unit.packs_short')} + {total % 20} {t('unit.pieces_short')}"
        return f"{int(stock)} {t('unit.pieces')}"

    def _insert_product(self, p):
        self.tree.insert('', 'end', values=(
            p[0], p[1] or '', p[2],
            f"{p[4]:.2f} DT", f"{p[5]:.2f} DT",
            t(f"unit.{p[6]}"),
            self._format_stock(p),
            p[10] if len(p) > 10 else 'normal',
        ))

    def load_products(self):
        self._loading = True
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            for p in db.get_all_products():
                self._insert_product(p)
        finally:
            self._loading = False

    def search_products(self, event=None):
        term = self.search_entry.get().strip()
        if not term:
            self.load_products()
            return
        self._loading = True
        try:
            for row in self.tree.get_children():
                self.tree.delete(row)
            for p in db.search_products_by_name(term):
                self._insert_product(p)
        finally:
            self._loading = False

    def show(self):
        self.frame.pack(fill='both', expand=True)
        self.load_products()

    def hide(self):
        self.frame.pack_forget()
