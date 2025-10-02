# Popup GUI utilities (Tkinter)

import tkinter as tk

def show_popup(root: tk.Tk, text: str, ms: int = 4000) -> None:
    if not text.strip():
        return
    win = tk.Toplevel(root)
    win.overrideredirect(True)           # borderless
    win.attributes("-topmost", True)
    win.configure(bg="white")

    # Close on unfocus
    def on_focus_out(e):
        win.destroy()

    win.bind("<FocusOut>", on_focus_out)
    win.bind("<Escape>", lambda e: win.destroy())
    win.bind("<Button-1>", lambda e: win.destroy())

    # Content
    frame = tk.Frame(win, bg="white", bd=1, relief="solid")
    frame.pack(fill="both", expand=True)
    title = tk.Label(frame, text="Selected:", bg="white", anchor="w")
    title.configure(font=("Segoe UI", 9))
    title.pack(fill="x", padx=10, pady=(8, 0))
    body = tk.Label(frame, text=text, bg="white", justify="left", wraplength=360)
    body.configure(font=("Segoe UI", 12))
    body.pack(fill="both", expand=True, padx=10, pady=(2, 10))

    # Position near mouse
    x, y = win.winfo_pointerx(), win.winfo_pointery()
    win.geometry(f"+{x+12}+{y+12}")

    # Give focus to the popup so FocusOut works
    win.focus_force()
