# Entry point: registers Alt+N and runs the Tk main loop.

import sys
import signal
import tkinter as tk

from gui import show_popup
from hotkey import start_alt_n_hotkey, HotkeyRunner
from selection import copy_selection
# from dictionary import lookup_and_format  # plug in later

def main():
    root = tk.Tk()
    root.withdraw()  # background utility; no main window

    def on_hotkey():
        # Runs on the hotkey thread; schedule work on Tk's thread.
        def _do():
            text = copy_selection()
            if text:
                # For now, just show the selection itself.
                # Later: formatted = lookup_and_format(text)
                show_popup(root, text)
        root.after(0, _do)

    runner: HotkeyRunner = start_alt_n_hotkey(on_hotkey)

    # Graceful exit via Ctrl+C during dev
    def _shutdown(*_):
        try:
            runner.stop()
        finally:
            root.quit()
    signal.signal(signal.SIGINT, _shutdown)

    try:
        root.mainloop()
    finally:
        runner.stop()

if __name__ == "__main__":
    sys.exit(main())
