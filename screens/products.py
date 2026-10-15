"""Products — add/edit/delete, photos, stock adjustments."""
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app import theme
from database import db
from database.errors import DomainError
from screens.base import BaseScreen
from screens.widgets import build_topbar
from utils import auth, i18n
from utils.i18n import t

try:
    from PIL import Image, ImageTk  # noqa: F401
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class ProductsScreen(BaseScreen):
    topbar_color = theme.DARK

    def __init__(self, root, switch, user=None, logout=None):
        self.photo_path = None
        self.current_product_id = None
        self.current_product_type = None
        self._loading = False
        super().__init__(root, switch, user, logout=None)
        self.load_products()

    # ------------------------------------------------------------------
    def build_topbar(self):
        start, end = [], []
        if auth.can(self.user, "sell"):
            start.append((t("nav.back_to_sales"), theme.DARK_LIGHT,
                          lambda: self.switch("sales")))
        if auth.can(self.user, "view_history"):
            start.append((t("nav.history"), theme.DARK_LIGHT,
                          lambda: self.switch("history")))
        if auth.can(self.user, "manage_users"):
            end.append((t("nav.users"), theme.DARK_LIGHT,
                        lambda: self.switch("users")))
        if auth.can(self.user, "view_reports"):
            end.append((t("nav.reports_arrow"), theme.DARK_LIGHT,
                        lambda: self.switch("reports")))
        build_topbar(self.frame, color=self.topbar_color,
                     title_key="products.title",
                     buttons_start=start, buttons_end=end,
                     logout_callback=self.logout)

    def build_body(self):
        main = tk.Frame(self.frame, bg=theme.BG)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        form = tk.Frame(main, bg=theme.BG_CARD, relief="groove", bd=2,
                        width=theme.FORM_COL_W)
        form.pack(side=i18n.side_start(), fill="y", padx=(0, 10))
        form.pack_propagate(False)

        listing = tk.Frame(main, bg=theme.BG_CARD, relief="groove", bd=2)
        listing.pack(side=i18n.side_end(), fill="both", expand=True)

        self._build_form(form)
        self._build_listing(listing)

    # --- form -----------------------------------------------------------
    def _build_form(self, parent):
        tk.Label(parent, text=t("products.add_modify"),
                 bg=theme.BG_CARD, fg=theme.FG,
                 font=self.font(13, "bold")).pack(pady=(12, 8))

        self.entries = {}
        for label, key in (
            (t("products.barcode"), "barcode"),
            (t("products.name"), "name"),
            (t("products.buy_price"), "buy"),
            (t("products.sell_price"), "sell"),
            (t("products.stock"), "stock"),
        ):
            row = tk.Frame(parent, bg=theme.BG_CARD)
            row.pack(fill="x", padx=10, pady=4)
            tk.Label(row, text=label, width=14, anchor=i18n.anchor_start(),
                     bg=theme.BG_CARD, fg=theme.FG,
                     font=self.font(10)).pack(side=i18n.side_start())
            e = tk.Entry(row, font=self.font(10), bg=theme.BG_INPUT, fg=theme.FG,
                         relief="solid", bd=1, justify=i18n.justify_text())
            e.pack(side=i18n.side_start(), fill="x", expand=True, ipady=2)
            self.entries[key] = e

        self._build_unit_radios(parent)
        self._build_pack_fields(parent)
        self._build_cigarette_fields(parent)
        self._build_photo_and_actions(parent)

    def _build_unit_radios(self, parent):
        row = tk.Frame(parent, bg=theme.BG_CARD)
        row.pack(fill="x", padx=10, pady=4)
        tk.Label(row, text=t("products.unit_label"), width=14,
                 anchor=i18n.anchor_start(),
                 bg=theme.BG_CARD, fg=theme.FG,
                 font=self.font(10)).pack(side=i18n.side_start())

        self.unit_var = tk.StringVar(value="piece")
        frame = tk.Frame(row, bg=theme.BG_CARD)
        frame.pack(side=i18n.side_start(), anchor=i18n.anchor_start())
        for text, val, cmd in (
            (t("products.unit_piece"), "piece", self.toggle_pack_options),
            (t("products.unit_gram"), "gram", self.toggle_pack_options),
            (t("products.unit_pack"), "pack", self.toggle_pack_options),
            (t("products.unit_cigarette"), "cigarette", self.toggle_cigarette_options),
        ):
            tk.Radiobutton(frame, text=text, variable=self.unit_var,
                           value=val, command=cmd,
                           bg=theme.BG_CARD, fg=theme.FG,
                           activebackground=theme.BG_CARD,
                           selectcolor=theme.BG_CARD,
                           font=self.font(9)).pack(side=i18n.side_start())

    def _build_pack_fields(self, parent):
        self.pack_frame = tk.Frame(parent, bg=theme.BG_CARD)
        sub = tk.Frame(self.pack_frame, bg=theme.BG_CARD)
        sub.pack(fill="x", padx=10, pady=3)
        tk.Label(sub, text=t("products.single_price"), width=14,
                 anchor=i18n.anchor_start(), bg=theme.BG_CARD, fg=theme.FG,
                 font=self.font(10)).pack(side=i18n.side_start())
        self.single_price_entry = tk.Entry(sub, width=10, font=self.font(10),
                                           bg=theme.BG_INPUT, fg=theme.FG,
                                           relief="solid", bd=1,
                                           justify=i18n.justify_text())
        self.single_price_entry.pack(side=i18n.side_start(), ipady=2)
        self.single_price_entry.insert(0, "0")

        sub = tk.Frame(self.pack_frame, bg=theme.BG_CARD)
        sub.pack(fill="x", padx=10, pady=3)
        tk.Label(sub, text=t("products.pieces_per_pack"), width=14,
                 anchor=i18n.anchor_start(), bg=theme.BG_CARD, fg=theme.FG,
                 font=self.font(10)).pack(side=i18n.side_start())
        self.pieces_per_pack_entry = tk.Entry(sub, width=10, font=self.font(10),
                                              bg=theme.BG_INPUT, fg=theme.FG,
                                              relief="solid", bd=1,
                                              justify=i18n.justify_text())
        self.pieces_per_pack_entry.pack(side=i18n.side_start(), ipady=2)
        self.pieces_per_pack_entry.insert(0, "20")

    def _build_cigarette_fields(self, parent):
        self.cigarette_frame = tk.Frame(parent, bg=theme.BG_CARD)
        sub = tk.Frame(self.cigarette_frame, bg=theme.BG_CARD)
        sub.pack(fill="x", padx=10, pady=3)
        tk.Label(sub, text=t("products.cigarette_price"), width=14,
                 anchor=i18n.anchor_start(), bg=theme.BG_CARD, fg=theme.FG,
                 font=self.font(10)).pack(side=i18n.side_start())
        self.single_cigarette_entry = tk.Entry(sub, width=10, font=self.font(10),
                                               bg=theme.BG_INPUT, fg=theme.FG,
                                               relief="solid", bd=1,
                                               justify=i18n.justify_text())
        self.single_cigarette_entry.pack(side=i18n.side_start(), ipady=2)
        self.single_cigarette_entry.insert(0, "0")

        tk.Label(self.cigarette_frame, text=t("products.cig_stock_hint"),
                 bg=theme.BG_CARD, fg=theme.FG_MUTED, font=self.font(9),
                 justify=i18n.justify_text()
                 ).pack(pady=2, padx=10, anchor=i18n.anchor_start())

    def _build_photo_and_actions(self, parent):
        tk.Button(parent, text=t("btn.choose_photo"), font=self.font(10),
                  bg=theme.BG_SUBTLE, fg=theme.FG, relief="flat",
                  command=self.choose_photo).pack(pady=(10, 2))
        self.photo_label = tk.Label(parent, text=t("products.no_photo"),
                                    bg=theme.BG_CARD, fg=theme.FG_MUTED,
                                    font=self.font(9))
        self.photo_label.pack()

        actions = tk.Frame(parent, bg=theme.BG_CARD)
        actions.pack(pady=15)
        tk.Button(actions, text=t("btn.add"), bg=theme.GREEN, fg="white",
                  width=9, font=self.font(10, "bold"), relief="flat",
                  command=self.add_product).pack(side=i18n.side_start(), padx=3)
        tk.Button(actions, text=t("btn.modify"), bg=theme.ORANGE, fg="white",
                  width=9, font=self.font(10, "bold"), relief="flat",
                  command=self.update_product).pack(side=i18n.side_start(), padx=3)
        tk.Button(actions, text=t("btn.clear"), bg=theme.GRAY, fg="white",
                  width=9, font=self.font(10, "bold"), relief="flat",
                  command=self.clear_all).pack(side=i18n.side_start(), padx=3)

    # --- listing --------------------------------------------------------
    def _build_listing(self, parent):
        search = tk.Frame(parent, bg=theme.BG_CARD)
        search.pack(fill="x", padx=10, pady=8)
        tk.Label(search, text=t("products.search"), bg=theme.BG_CARD,
                 fg=theme.FG, font=self.font(10)).pack(side=i18n.side_start())
        self.search_entry = tk.Entry(search, font=self.font(10),
                                     bg=theme.BG_INPUT, fg=theme.FG,
                                     relief="solid", bd=1,
                                     justify=i18n.justify_text())
        self.search_entry.pack(side=i18n.side_start(), fill="x", expand=True,
                               padx=5, ipady=2)
        self.search_entry.bind("<KeyRelease>", self.search_products)

        ttk.Style().configure("Products.Treeview",
                              background="white", foreground="black",
                              fieldbackground="white",
                              font=self.font(10), rowheight=26)
        ttk.Style().configure("Products.Treeview.Heading",
                              font=self.font(10, "bold"),
                              background=theme.BG_SUBTLE, foreground="black")

        container = tk.Frame(parent, bg=theme.BG_CARD)
        container.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        columns = ("id", "barcode", "name", "buy", "sell", "unit", "stock", "ptype")
        headings = [t("products.col_id"), t("products.col_barcode"),
                    t("products.col_name"), t("products.col_buy"),
                    t("products.col_sell"), t("products.col_unit"),
                    t("products.col_stock"), t("products.col_type")]
        widths = [45, 100, 220, 80, 80, 70, 130, 80]
        self.tree = ttk.Treeview(container, columns=columns, show="headings",
                                 height=20, style="Products.Treeview")
        for col, hdr, w in zip(columns, headings, widths):
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=w,
                             anchor=(i18n.anchor_start()
                                     if col == "name" else "center"))
        v = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        h = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v.set, xscrollcommand=h.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        v.grid(row=0, column=1, sticky="ns")
        h.grid(row=1, column=0, sticky="ew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.select_product)

        footer = tk.Frame(parent, bg=theme.BG_CARD)
        footer.pack(fill="x", padx=10, pady=(0, 10))
        tk.Button(footer, text=t("btn.delete_selection"), bg=theme.RED,
                  fg="white", font=self.font(10, "bold"), relief="flat",
                  command=self.delete_product
                  ).pack(side=i18n.side_start(), padx=3)
        tk.Button(footer, text=t("btn.add_stock"), bg=theme.BLUE, fg="white",
                  font=self.font(10, "bold"), relief="flat",
                  command=self.add_stock
                  ).pack(side=i18n.side_start(), padx=3)

    # ------------------------------------------------------------------
    # Permissions helper
    # ------------------------------------------------------------------
    def _require_manage(self) -> bool:
        if not auth.can(self.user, "manage_products"):
            messagebox.showerror(t("msg.access_denied"), t("products.owner_only"))
            return False
        return True

    # ------------------------------------------------------------------
    # Pack / cigarette toggles
    # ------------------------------------------------------------------
    def toggle_pack_options(self):
        self.cigarette_frame.pack_forget()
        if self.unit_var.get() == "pack":
            self.pack_frame.pack(fill="x", pady=4,
                                 after=self.entries["stock"].master)
        else:
            self.pack_frame.pack_forget()

    def toggle_cigarette_options(self):
        self.pack_frame.pack_forget()
        if self.unit_var.get() == "cigarette":
            self.cigarette_frame.pack(fill="x", pady=4,
                                      after=self.entries["stock"].master)
        else:
            self.cigarette_frame.pack_forget()

    # ------------------------------------------------------------------
    # Photo
    # ------------------------------------------------------------------
    def choose_photo(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")])
        if path:
            self.photo_path = path
            self.photo_label.config(text=os.path.basename(path))

    # ------------------------------------------------------------------
    # Form → data
    # ------------------------------------------------------------------
    def _read_form(self, editing=False):
        barcode = self.entries["barcode"].get().strip()
        name = self.entries["name"].get().strip()
        if not name:
            raise ValueError(t("products.name_required"))
        buy_price = float(self.entries["buy"].get() or "0")
        sell_price = float(self.entries["sell"].get() or "0")
        if sell_price <= buy_price:
            raise ValueError(t("products.sell_gt_buy"))

        unit = self.unit_var.get()
        product_type = (self.current_product_type
                        if editing and self.current_product_type
                        else ("cigarette" if unit == "cigarette" else "normal"))
        stock_input = float(self.entries["stock"].get() or "0")
        single_price = 0.0
        pieces_per_pack = 20
        single_cig_price = 0.0
        if unit == "pack":
            single_price = float(self.single_price_entry.get() or "0")
            pieces_per_pack = int(float(self.pieces_per_pack_entry.get() or "20"))
            if pieces_per_pack <= 0:
                raise ValueError(t("products.pieces_gt_zero"))
            stock = stock_input * pieces_per_pack
        elif unit == "cigarette":
            single_cig_price = float(self.single_cigarette_entry.get() or "0")
            stock = stock_input
        else:
            stock = stock_input
        return {
            "barcode": barcode, "name": name,
            "buy_price": buy_price, "sell_price": sell_price,
            "unit": unit, "stock": stock,
            "single_price": single_price,
            "pieces_per_pack": pieces_per_pack,
            "product_type": product_type,
            "single_cigarette_price": single_cig_price,
        }

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    def add_product(self):
        if not self._require_manage():
            return
        try:
            data = self._read_form(editing=False)
            db.add_product(photo=self.photo_path, **data)
            messagebox.showinfo(t("msg.success"), t("products.success_added"))
            self.clear_all()
            self.load_products()
        except ValueError:
            messagebox.showerror(t("msg.error"), t("msg.invalid_numbers"))
        except DomainError as e:
            messagebox.showerror(t("msg.error"), t(e.key, **e.kwargs))
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    def update_product(self):
        if not self._require_manage():
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
        except DomainError as e:
            messagebox.showerror(t("msg.error"), t(e.key, **e.kwargs))
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    def delete_product(self):
        if not self._require_manage():
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(t("msg.warning"), t("products.select_first"))
            return
        if not messagebox.askyesno(t("msg.confirmation"),
                                   t("products.confirm_delete")):
            return
        product_id = int(self.tree.item(sel[0])["values"][0])
        try:
            db.delete_product(product_id)
            self.clear_all()
            self.load_products()
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    # ------------------------------------------------------------------
    # Selection / form fill
    # ------------------------------------------------------------------
    def select_product(self, event=None):
        if self._loading:
            return
        sel = self.tree.selection()
        if not sel:
            return
        values = self.tree.item(sel[0])["values"]
        if not values:
            return
        try:
            product_id = int(values[0])
        except (ValueError, TypeError):
            return
        product = next((p for p in db.get_all_products() if p[0] == product_id),
                       None)
        if product:
            self.clear_form()
            self._fill_form(product)

    def _fill_form(self, product):
        (pid, barcode, name, _photo, buy, sell, unit, stock,
         single_price, pieces_per_pack, _ptype, single_cig) = product
        self.entries["barcode"].insert(0, barcode or "")
        self.entries["name"].insert(0, name or "")
        self.entries["buy"].insert(0, f"{buy}")
        self.entries["sell"].insert(0, f"{sell}")
        self.unit_var.set(unit)
        if unit == "pack":
            self.pack_frame.pack(fill="x", pady=4,
                                 after=self.entries["stock"].master)
            self.single_price_entry.delete(0, tk.END)
            self.single_price_entry.insert(0, f"{single_price}")
            self.pieces_per_pack_entry.delete(0, tk.END)
            self.pieces_per_pack_entry.insert(0, str(pieces_per_pack))
            ppp = pieces_per_pack or 1
            self.entries["stock"].insert(
                0, f"{stock / ppp:.2f}".rstrip("0").rstrip("."))
        elif unit == "cigarette":
            self.cigarette_frame.pack(fill="x", pady=4,
                                      after=self.entries["stock"].master)
            self.single_cigarette_entry.delete(0, tk.END)
            self.single_cigarette_entry.insert(0, f"{single_cig}")
            self.entries["stock"].insert(0, f"{stock:.0f}")
        else:
            self.entries["stock"].insert(
                0, f"{stock:.2f}".rstrip("0").rstrip("."))
        self.current_product_id = pid
        self.current_product_type = _ptype
        if _photo:
            self.photo_path = _photo
            self.photo_label.config(text=os.path.basename(_photo))

    def clear_form(self):
        for e in self.entries.values():
            e.delete(0, tk.END)
        self.unit_var.set("piece")
        self.pack_frame.pack_forget()
        self.cigarette_frame.pack_forget()
        self.single_price_entry.delete(0, tk.END)
        self.single_price_entry.insert(0, "0")
        self.pieces_per_pack_entry.delete(0, tk.END)
        self.pieces_per_pack_entry.insert(0, "20")
        self.single_cigarette_entry.delete(0, tk.END)
        self.single_cigarette_entry.insert(0, "0")
        self.photo_path = None
        self.photo_label.config(text=t("products.no_photo"))
        self.current_product_id = None
        self.current_product_type = None

    def clear_all(self):
        self.clear_form()
        self.tree.selection_remove(self.tree.selection())

    # ------------------------------------------------------------------
    # Add stock dialog
    # ------------------------------------------------------------------
    def add_stock(self):
        if not self._require_manage():
            return
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning(t("msg.warning"), t("products.select_first"))
            return
        try:
            product_id = int(self.tree.item(sel[0])["values"][0])
        except (ValueError, TypeError):
            return
        product = next((p for p in db.get_all_products() if p[0] == product_id),
                       None)
        if not product:
            return
        unit, current_stock, ppp = product[6], product[7], (product[9] or 1)

        dlg = tk.Toplevel(self.root)
        dlg.title(t("products.add_stock_title"))
        dlg.geometry("380x340")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg=theme.BG)

        tk.Label(dlg, text=f"{t('lbl.product')}: {product[2]}",
                 font=self.font(10, "bold"),
                 bg=theme.BG, fg=theme.FG).pack(pady=10)

        def make_entry(label, default=None):
            tk.Label(dlg, text=label, font=self.font(10),
                     bg=theme.BG, fg=theme.FG).pack(pady=(8, 0))
            e = tk.Entry(dlg, font=self.font(10), width=12,
                         justify="center", bg="white", fg=theme.FG,
                         relief="solid", bd=1)
            e.pack(pady=3, ipady=3)
            if default is not None:
                e.insert(0, default)
            return e

        packs_e = pieces_e = qty_e = None
        if unit == "pack":
            packs = int(current_stock // ppp)
            pieces = int(current_stock % ppp)
            tk.Label(dlg, text=t("products.current_stock_pack",
                                  packs=packs, pieces=pieces),
                     font=self.font(10), bg=theme.BG, fg=theme.FG).pack()
            packs_e = make_entry(t("products.add_packs"))
            pieces_e = make_entry(t("products.add_pieces"), "0")
            packs_e.focus()
        elif unit == "cigarette":
            total = int(current_stock)
            tk.Label(dlg, text=t("products.current_stock_cig",
                                  packs=total // 20, units=total % 20),
                     font=self.font(10), bg=theme.BG, fg=theme.FG).pack()
            tk.Label(dlg, text=t("products.add_cig"),
                     font=self.font(10, "bold"),
                     bg=theme.BG, fg=theme.FG).pack(pady=(8, 0))
            tk.Label(dlg, text=t("products.add_cig_hint"), fg=theme.FG_MUTED,
                     bg=theme.BG, font=self.font(9)).pack()
            qty_e = make_entry(t("sales.qty"))
            qty_e.focus()
        elif unit == "gram":
            tk.Label(dlg, text=t("products.current_stock_g", stock=current_stock),
                     font=self.font(10), bg=theme.BG, fg=theme.FG).pack()
            qty_e = make_entry(t("products.add_g"))
            qty_e.focus()
        else:
            tk.Label(dlg, text=t("products.current_stock", stock=current_stock),
                     font=self.font(10), bg=theme.BG, fg=theme.FG).pack()
            qty_e = make_entry(t("products.qty_to_add"))
            qty_e.focus()

        def submit(event=None):
            try:
                if unit == "pack":
                    add_qty = (float(packs_e.get() or "0") * ppp
                               + float(pieces_e.get() or "0"))
                else:
                    add_qty = float(qty_e.get() or "0")
                if add_qty <= 0:
                    messagebox.showerror(t("msg.error"),
                                         t("products.positive_number"),
                                         parent=dlg)
                    return
                db.update_product(
                    product_id, product[1], product[2], product[3],
                    product[4], product[5], product[6], current_stock + add_qty,
                    product[8], product[9], product[10], product[11],
                )
                dlg.destroy()
                self.load_products()
                messagebox.showinfo(t("msg.success"), t("products.stock_added"))
            except ValueError:
                messagebox.showerror(t("msg.error"), t("msg.invalid_numbers"),
                                     parent=dlg)

        for e in (packs_e, pieces_e, qty_e):
            if e is not None:
                e.bind("<Return>", submit)
        tk.Button(dlg, text=t("btn.add"), bg=theme.GREEN, fg="white",
                  font=self.font(10, "bold"), width=10, relief="flat",
                  command=submit).pack(pady=15)
        dlg.wait_window()

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------
    def _format_stock(self, product):
        unit, stock, ppp = product[6], product[7], (product[9] or 1)
        if unit == "pack":
            return (f"{int(stock // ppp)} {t('unit.packs_short')} + "
                    f"{int(stock % ppp)} {t('unit.pieces_short')}")
        if unit == "gram":
            return f"{stock:g} g"
        if unit == "cigarette":
            total = int(stock)
            return (f"{total // 20} {t('unit.packs_short')} + "
                    f"{total % 20} {t('unit.pieces_short')}")
        return f"{int(stock)} {t('unit.pieces')}"

    def _insert_product(self, p):
        self.tree.insert("", "end", values=(
            p[0], p[1] or "", p[2],
            f"{p[4]:.2f} DT", f"{p[5]:.2f} DT",
            t(f"unit.{p[6]}"), self._format_stock(p),
            p[10] if len(p) > 10 else "normal",
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

    def on_show(self):
        self.load_products()