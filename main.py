#!/usr/bin/env python3
"""Stock Manager — entry point."""
import os
import locale

# Must run BEFORE tkinter is imported, so Arabic shaping and bidi work.
os.environ.setdefault("LC_ALL", "C.UTF-8")
os.environ.setdefault("LANG", "C.UTF-8")
try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

from app.router import StockManager


def main() -> None:
    app = StockManager()
    if app.user:
        app.run()


if __name__ == "__main__":
    main()