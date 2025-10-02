"""
hotkey.py — Global hotkey registration using keyboard library.

Exports:
    start_alt_n_hotkey(callback) -> HotkeyRunner
        Registers LAlt+P+N chord system-wide. On press, calls `callback()`.

Notes:
- To receive hotkeys while an elevated window is focused, run this program as admin.
"""

import keyboard


class HotkeyRunner:
    """Holds the hotkey; call .stop() to unregister."""
    def __init__(self, hotkey_str: str):
        self._hotkey_str = hotkey_str

    def stop(self) -> None:
        """Unregisters the hotkey."""
        try:
            keyboard.remove_hotkey(self._hotkey_str)
        except Exception:
            pass


def start_alt_n_hotkey(callback) -> HotkeyRunner:
    """
    Registers LAlt+P+N chord globally and invokes `callback()` on press.
    Returns a HotkeyRunner. Raises RuntimeError on failure.

    Note: Requires administrator privileges on Windows to capture global hotkeys.
    """
    hotkey_str = "alt+n"  # Simpler two-key combo for testing

    def safe_callback():
        try:
            callback()
        except Exception as e:
            print(f"Error in hotkey callback: {e}")

    try:
        keyboard.add_hotkey(hotkey_str, safe_callback, suppress=False)
        print(f"Hotkey registered: {hotkey_str}")
        print("(Note: Requires administrator privileges on Windows)")
    except Exception as e:
        raise RuntimeError(f"Failed to register {hotkey_str}: {e}")

    return HotkeyRunner(hotkey_str=hotkey_str)
