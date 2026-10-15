"""BaseScreen: shared chrome for every screen (topbar, frame, show/hide)."""
import tkinter as tk

from app import theme
from utils import i18n


class BaseScreen:
    """Subclass and implement `build_body()` and (optionally) `build_topbar()`."""

    topbar_color = theme.DARK

    def __init__(self, root, switch_callback, user=None, logout=None):
        self.root = root
        self.switch = switch_callback
        self.user = user
        self.logout = logout              # ← new
        self.frame = tk.Frame(root, bg=theme.BG)
        self.build()

    # ------------------------------------------------------------------
    def build(self):
        self.build_topbar()
        self.build_body()

    def build_topbar(self):
        """Override to customise. Default: empty bar with title."""

    def build_body(self):
        raise NotImplementedError

    # ------------------------------------------------------------------
    def font(self, size: int, weight: str = "normal"):
        return i18n.ui_font(size, weight)

    # ------------------------------------------------------------------
    def show(self):
        self.frame.pack(fill="both", expand=True)
        self.on_show()

    def hide(self):
        self.frame.pack_forget()
        self.on_hide()

    def on_show(self):
        """Called after the screen becomes visible."""

    def on_hide(self):
        """Called before the screen is hidden."""