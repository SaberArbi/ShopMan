# screens/users.py
import tkinter as tk
from tkinter import ttk, messagebox

from utils import auth, i18n
from utils.i18n import t


class UsersScreen:
    def __init__(self, root, switch_callback, user=None):
        self.root = root
        self.switch = switch_callback
        self.user = user
        self.frame = tk.Frame(root, bg='#f0f0f0')
        self.setup_ui()
        self.load_users()

    def _font(self, size, weight="normal"):
        return i18n.ui_font(size, weight)

    def setup_ui(self):
        FONT_TITLE = self._font(13, 'bold')
        FONT_BOLD  = self._font(10, 'bold')
        FONT_BODY  = self._font(10)
        FONT_SMALL = self._font(9)

        top = tk.Frame(self.frame, bg='#2c3e50', height=55)
        top.pack(fill='x')
        top.pack_propagate(False)

        left_btns = tk.Frame(top, bg='#2c3e50')
        left_btns.pack(side=i18n.side_start(), padx=8, pady=8)
        if auth.can(self.user, "sell"):
            tk.Button(left_btns, text=t("nav.back_to_sales"), bg='#34495e', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('sales')
                      ).pack(side=i18n.side_start(), padx=3)
        if auth.can(self.user, "view_history"):
            tk.Button(left_btns, text=t("nav.history"), bg='#34495e', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('history')
                      ).pack(side=i18n.side_start(), padx=3)

        tk.Label(top, text=t("users.title"), bg='#2c3e50', fg='white',
                 font=FONT_TITLE).pack(side='top', pady=10)

        right_btns = tk.Frame(top, bg='#2c3e50')
        right_btns.pack(side=i18n.side_end(), padx=8, pady=8)
        if auth.can(self.user, "view_deleted_sales"):
            tk.Button(right_btns, text=t("history.deleted_btn"), bg='#7f1d1d', fg='white',
                      font=FONT_BODY, width=11, relief='flat',
                      command=lambda: self.switch('deleted')
                      ).pack(side=i18n.side_end(), padx=3)

        main = tk.Frame(self.frame, bg='#f0f0f0')
        main.pack(fill='both', expand=True, padx=10, pady=10)

        # Left form / right list — use side_start for form so it lands at
        # the beginning of reading order (left in LTR, right in RTL).
        form = tk.Frame(main, bg='white', relief='groove', bd=2, width=340)
        form.pack(side=i18n.side_start(), fill='y', padx=(0, 10))
        form.pack_propagate(False)

        tk.Label(form, text=t("users.add_user"), bg='white', fg='#2c3e50',
                 font=FONT_TITLE).pack(pady=(14, 8))

        self.entries = {}
        for label, key, show in (
            (t("users.username"), 'username', None),
            (t("users.full_name"), 'full_name', None),
            (t("users.password"), 'password', '*'),
            (t("users.confirm"), 'password2', '*'),
        ):
            row = tk.Frame(form, bg='white')
            row.pack(fill='x', padx=10, pady=4)
            tk.Label(row, text=label, width=16, anchor=i18n.anchor_start(),
                     bg='white', fg='#2c3e50',
                     font=FONT_BODY).pack(side=i18n.side_start())
            e = tk.Entry(row, font=FONT_BODY, bg='#f8f9fa', fg='#2c3e50',
                         relief='solid', bd=1, show=show if show else '',
                         justify=i18n.justify_text())
            e.pack(side=i18n.side_start(), fill='x', expand=True, ipady=2)
            self.entries[key] = e

        tk.Label(form, text=t("users.role"), bg='white', fg='#2c3e50',
                 font=FONT_BODY).pack(anchor=i18n.anchor_start(),
                                      padx=10, pady=(8, 0))
        self.role_var = tk.StringVar(value='cashier')
        roles_frame = tk.Frame(form, bg='white')
        roles_frame.pack(fill='x', padx=10, pady=2)
        tk.Radiobutton(roles_frame, text=t("users.role_cashier"),
                       variable=self.role_var,
                       value='cashier', bg='white', fg='#2c3e50',
                       activebackground='white', selectcolor='white',
                       font=FONT_BODY).pack(side=i18n.side_start())
        tk.Radiobutton(roles_frame, text=t("users.role_owner"),
                       variable=self.role_var,
                       value='owner', bg='white', fg='#2c3e50',
                       activebackground='white', selectcolor='white',
                       font=FONT_BODY).pack(side=i18n.side_start())

        tk.Button(form, text=t("users.create"), bg='#27ae60', fg='white',
                  font=FONT_BOLD, width=12, relief='flat',
                  command=self.create_user).pack(pady=18)

        # Right: list
        listing = tk.Frame(main, bg='white', relief='groove', bd=2)
        listing.pack(side=i18n.side_end(), fill='both', expand=True)

        tree_container = tk.Frame(listing, bg='white')
        tree_container.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('id', 'username', 'full_name', 'role', 'active', 'created')
        headings = [
            t("users.col_id"), t("users.col_username"),
            t("users.col_full_name"), t("users.col_role"),
            t("users.col_active"), t("users.col_created"),
        ]
        self.tree = ttk.Treeview(tree_container, columns=columns,
                                 show='headings', height=20)
        widths = [45, 140, 180, 100, 70, 140]
        for col, hdr, w in zip(columns, headings, widths):
            self.tree.heading(col, text=hdr)
            self.tree.column(col, width=w,
                             anchor=(i18n.anchor_start()
                                     if col == 'full_name' else 'center'))

        vbar = ttk.Scrollbar(tree_container, orient='vertical',
                             command=self.tree.yview)
        self.tree.configure(yscrollcommand=vbar.set)
        self.tree.pack(side=i18n.side_start(), fill='both', expand=True)
        vbar.pack(side=i18n.side_end(), fill='y')

        footer = tk.Frame(listing, bg='white')
        footer.pack(fill='x', padx=10, pady=(0, 10))

        tk.Button(footer, text=t("users.rename"), bg='#8e44ad', fg='white',
                  font=FONT_BOLD, relief='flat',
                  command=self.rename_dialog).pack(side=i18n.side_start(), padx=3)
        tk.Button(footer, text=t("users.toggle_active"), bg='#f39c12', fg='white',
                  font=FONT_BOLD, relief='flat',
                  command=self.toggle_active).pack(side=i18n.side_start(), padx=3)
        tk.Button(footer, text=t("users.change_password"), bg='#3498db', fg='white',
                  font=FONT_BOLD, relief='flat',
                  command=self.change_password_dialog).pack(side=i18n.side_start(), padx=3)
        tk.Button(footer, text=t("users.delete"), bg='#e74c3c', fg='white',
                  font=FONT_BOLD, relief='flat',
                  command=self.delete_selected).pack(side=i18n.side_start(), padx=3)

        tk.Label(footer, text=t("users.warn_owner"),
                 bg='white', fg='#e67e22',
                 font=FONT_SMALL).pack(side=i18n.side_end(), padx=5)

    def create_user(self):
        username = self.entries['username'].get().strip()
        full_name = self.entries['full_name'].get().strip()
        password = self.entries['password'].get()
        password2 = self.entries['password2'].get()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showwarning(t("msg.warning"), t("users.required_fields"))
            return
        if password != password2:
            messagebox.showwarning(t("msg.warning"), t("users.password_mismatch"))
            return
        if len(password) < 4:
            messagebox.showwarning(t("msg.warning"), t("users.password_short"))
            return

        try:
            auth.create_user(username, password, role, full_name)
            messagebox.showinfo(t("msg.success"),
                                t("users.created_ok", u=username))
            for e in self.entries.values():
                e.delete(0, tk.END)
            self.load_users()
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    def rename_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(t("msg.warning"), t("users.select_user"))
            return
        values = self.tree.item(selected[0])['values']
        user_id = int(values[0])
        old_username = values[1]

        dlg = tk.Toplevel(self.root)
        dlg.title(t("users.rename_title", u=old_username))
        dlg.geometry("360x180")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg='#f0f0f0')

        tk.Label(dlg, text=t("users.new_name_for", u=old_username),
                 bg='#f0f0f0', fg='#2c3e50',
                 font=self._font(10)).pack(pady=(20, 4))
        entry = tk.Entry(dlg, font=self._font(10), width=26,
                         bg='white', fg='#2c3e50', relief='solid', bd=1,
                         justify=i18n.justify_text())
        entry.pack(pady=6, ipady=3)
        entry.insert(0, old_username)
        entry.focus_set()
        entry.select_range(0, tk.END)

        def submit(event=None):
            new_name = entry.get().strip()
            if not new_name:
                messagebox.showerror(t("msg.error"), t("users.name_empty"),
                                     parent=dlg)
                return
            if new_name == old_username:
                dlg.destroy()
                return
            try:
                auth.rename_user(user_id, new_name)
            except Exception as e:
                messagebox.showerror(t("msg.error"), str(e), parent=dlg)
                return
            if self.user and self.user.get('id') == user_id:
                self.user['username'] = new_name
                try:
                    self.root.title(t("app.window_title",
                                       username=self.user['username'],
                                       role=t(f"role.{self.user['role']}")))
                except tk.TclError:
                    pass
            messagebox.showinfo(t("msg.success"),
                                t("users.renamed_ok", u=new_name), parent=dlg)
            dlg.destroy()
            self.load_users()

        tk.Button(dlg, text=t("btn.save"), bg='#27ae60', fg='white',
                  font=self._font(10, 'bold'), width=10, relief='flat',
                  command=submit).pack(pady=12)
        dlg.bind('<Return>', submit)
        dlg.bind('<KP_Enter>', submit)

    def toggle_active(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(t("msg.warning"), t("users.select_user"))
            return
        values = self.tree.item(selected[0])['values']
        user_id = int(values[0])
        if user_id == self.user['id']:
            messagebox.showerror(t("msg.error"), t("users.cannot_disable_self"))
            return
        is_active = (values[4] == t("users.active_yes"))
        try:
            auth.set_user_active(user_id, not is_active)
            self.load_users()
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    def change_password_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(t("msg.warning"), t("users.select_user"))
            return
        values = self.tree.item(selected[0])['values']
        user_id = int(values[0])
        username = values[1]

        dlg = tk.Toplevel(self.root)
        dlg.title(f"{t('users.change_password')} - {username}")
        dlg.geometry("320x180")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg='#f0f0f0')

        tk.Label(dlg, text=t("users.password_new"), bg='#f0f0f0',
                 font=self._font(10)).pack(pady=(20, 4))
        p1 = tk.Entry(dlg, show='*', font=self._font(10), width=22,
                      justify=i18n.justify_text())
        p1.pack(pady=4)
        p1.focus_set()

        tk.Label(dlg, text=t("users.confirm"), bg='#f0f0f0',
                 font=self._font(10)).pack(pady=(4, 4))
        p2 = tk.Entry(dlg, show='*', font=self._font(10), width=22,
                      justify=i18n.justify_text())
        p2.pack(pady=4)

        def submit():
            if p1.get() != p2.get():
                messagebox.showerror(t("msg.error"),
                                     t("users.password_mismatch"), parent=dlg)
                return
            if len(p1.get()) < 4:
                messagebox.showerror(t("msg.error"),
                                     t("users.password_short"), parent=dlg)
                return
            try:
                auth.change_password(user_id, p1.get())
                messagebox.showinfo(t("msg.success"),
                                    t("users.password_changed"), parent=dlg)
                dlg.destroy()
            except Exception as e:
                messagebox.showerror(t("msg.error"), str(e), parent=dlg)

        tk.Button(dlg, text=t("btn.save"), bg='#27ae60', fg='white',
                  font=self._font(10, 'bold'), width=10, relief='flat',
                  command=submit).pack(pady=12)
        dlg.bind('<Return>', lambda e: submit())

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(t("msg.warning"), t("users.select_user"))
            return
        values = self.tree.item(selected[0])['values']
        user_id = int(values[0])
        username = values[1]
        if user_id == self.user['id']:
            messagebox.showerror(t("msg.error"), t("users.cannot_delete_self"))
            return
        if not messagebox.askyesno(t("msg.confirmation"),
                                   t("users.confirm_delete", u=username)):
            return
        try:
            auth.delete_user(user_id)
            self.load_users()
        except Exception as e:
            messagebox.showerror(t("msg.error"), str(e))

    def load_users(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        yes = t("users.active_yes")
        no = t("users.active_no")
        for (uid, username, full_name, role, is_active, created_at) in auth.list_users():
            self.tree.insert('', 'end', values=(
                uid, username, full_name or '',
                t(f"role.{role}"),
                yes if is_active else no,
                created_at or '',
            ))

    def show(self):
        self.frame.pack(fill='both', expand=True)
        self.load_users()

    def hide(self):
        self.frame.pack_forget()
