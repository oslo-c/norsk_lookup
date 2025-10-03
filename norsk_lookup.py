# Entry point: registers Alt+N hotkey and runs the Tk main loop.

import sys
import signal
import tkinter as tk

from gui import show_popup
from hotkey import start_alt_n_hotkey, HotkeyRunner
from selection import copy_selection

def main():
    root = tk.Tk()
    root.withdraw()  # background utility; no main window

    def on_hotkey():
        with open("debug.log", "a") as f:
            f.write("HOTKEY TRIGGERED\n")
        # Runs on the hotkey thread; schedule work on Tk's thread.
        def _do():
            text = copy_selection()
            with open("debug.log", "a") as f:
                f.write(f"Got text: {repr(text)}\n")
            if text:
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
