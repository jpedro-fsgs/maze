import tkinter as tk
import platform

def apply_state_patch():
    """Apply safe_state monkey patch to tk.Tk.state to avoid 'zoomed' on non-Windows."""
    _original_state = tk.Tk.state
    def safe_state(self, mode=None):
        if mode == 'zoomed' and platform.system() != 'Windows':
            mode = 'normal'
        return _original_state(self, mode)
    tk.Tk.state = safe_state

apply_state_patch()
