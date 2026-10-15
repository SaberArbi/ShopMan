# 📦 Stock Manager

> A tiny point-of-sale and inventory app for small shops.
> Scan it. Sell it. Count it. Go home on time.

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![UI](https://img.shields.io/badge/UI-Tkinter-orange)
![DB](https://img.shields.io/badge/database-SQLite-lightgrey)
![i18n](https://img.shields.io/badge/languages-EN%20%7C%20FR%20%7C%20AR-green)
![License](https://img.shields.io/badge/license-MIT-brightgreen)
![Vibes](https://img.shields.io/badge/vibecoded-100%25-ff69b4)

---

## 🎯 What is this?

**Stock Manager** is a desktop app that runs a small shop's counter: ring up sales with a barcode scanner (or the keyboard), keep stock honest, see how the day went, and undo mistakes without panic.

It runs on the Python standard library. No server, no cloud, no subscription. Just a single SQLite file and a window.

## 🤖 The honest part: it's vibecoded

This project was **vibecoded**: built in conversation with AI, iterated on feel and feedback, and shaped by what a real shop counter needs rather than by a grand architecture document.

**Why does it exist?** To earn a little money on a small scale, and that money is **feeding a bigger project** I'm building on the side. Think of Stock Manager as the scrappy little sibling that pays the rent while the big one grows up.

What that means for you:

- ✅ It works, and it's used for real sales.
- ✅ The code is readable, commented where it matters, and kept tidy.
- ⚠️ It hasn't been through a formal audit or a test suite. Treat it like a good prototype that went to work, and **back up your data** (the app helps, see below).
- 🙏 Bug reports and PRs are very welcome.

## ✨ Features

| | |
|---|---|
| 🛒 **Fast sales screen** | Barcode scan (digits) or name search (letters). Space bar to pay. Built for speed at the counter. |
| 📱 **Telecom top-ups** | One-key shortcuts **F1–F6** for Telecom / Orange / Ooredoo credit (1.3 DT and 5.9 DT). |
| ⚖️ **Flexible units** | Sell by piece, by weight (g / kg), by pack, or cigarettes by single stick or full pack. |
| 🗂️ **Product management** | Add, edit, search, restock. Optional product photos. |
| 🧾 **Sales history** | Grouped by cart, filterable by date and time, with per-item details. |
| 🗑️ **Trash (corbeille)** | Soft-deleted sales can be restored with stock re-adjusted. Owners can also delete permanently. |
| 📊 **Reports** | Period summary, top products, low-stock alerts, and exportable text reports. "Since last report" in one click. |
| 👥 **Users & roles** | **Owner** (everything) and **Cashier** (sell, view history and reports, soft delete). PBKDF2-hashed passwords. |
| 💾 **Automatic backups** | Hourly, on exit, and after each sale. The app keeps the last 10 automatic backups. |
| 🌍 **Three languages** | English, Français, العربية, with proper **RTL layout** and Arabic text shaping. |

## 🚀 Quick start

```bash
git clone https://github.com/<your-username>/stock-manager.git
cd stock-manager
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

The database (`stock.db`) is created automatically on first launch, along with the default telecom products.

> **Requirements:** Python 3.9+ with Tkinter. On some Linux distros you may need `sudo dnf install python3-tkinter` (Fedora) or `sudo apt install python3-tk` (Debian/Ubuntu).

### 🔑 First login

| Username | Password |
|---|---|
| `owner` | `owner123` |

**Change this password immediately** from the Users screen. Seriously. Right now. We'll wait.

## ⌨️ Keyboard shortcuts (Sales screen)

| Key | Action |
|---|---|
| `F1` – `F6` | Add Telecom / Orange / Ooredoo credit to cart |
| `Space` | Pay (when the cart is not empty and you're not typing) |
| `↓` | Jump into search results |
| `Enter` | Select result / confirm popup |
| `U` | Switch unit in a quantity popup |
| `Esc` | Cancel popup or search |

## 🌐 Languages & Arabic support

Switch language on the login screen. The choice is saved in `settings.json`.

For correct Arabic letter shaping and right-to-left ordering in Tk, install the optional libraries (already listed in `requirements.txt`):

```bash
pip install arabic-reshaper python-bidi
```

Without them the app still runs, but Arabic text may look disconnected.

## 🗺️ Project structure

```
stock_manager/
├── main.py              # Entry point & screen switching
├── database/
│   ├── db_setup.py      # First-run table creation
│   └── db_operations.py # All SQL lives here
├── screens/             # One file per screen
│   ├── sales.py
│   ├── products.py
│   ├── history.py
│   ├── deleted_sales.py
│   ├── reports.py
│   ├── users.py
│   └── login.py
├── utils/
│   ├── auth.py          # Users, roles, permissions, hashing
│   ├── i18n.py          # Translations + RTL helpers
│   ├── backup.py        # Hourly & on-exit backups
│   ├── helpers.py
│   └── last_report.py
├── assets/products/     # Product photos
├── backups/             # Auto-generated, git-ignored
└── reports/             # Generated reports, git-ignored
```

## 🔒 Good to know

- Your data (`stock.db`, `backups/`, `reports/`, `settings.json`) is **git-ignored on purpose**. Never commit a shop's sales.
- Keep a copy of `backups/` somewhere other than the same machine (USB drive, cloud folder). A backup on the same disk won't help if the disk dies.
- `create_tables()` in `db_setup.py` drops and recreates the `products` and `sales` tables. It only runs when the database is missing or has no `products` table, but be careful if you call it by hand.

## 🛣️ Ideas for later

- Receipt printing
- CSV / Excel export
- Stock-movement log (who changed what, and when)
- Automated tests

Got another idea? Open an issue.

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first. The short version: open an issue for big changes, keep PRs focused, and don't break translations (every user-facing string goes through `t("key")` in all three languages).

## 📄 License

[MIT](LICENSE) © 2026 Saber Arbi

---

<p align="center">
  Built with ☕, vibes, and a bigger dream in the background.<br>
  If this app helps your shop, that's the best kind of win. 🧡
</p>