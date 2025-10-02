"""
hotkey.py — Global hotkey registration via Win32 RegisterHotKey.

Exports:
    start_alt_n_hotkey(callback) -> HotkeyRunner
        Registers Alt+N system-wide. On press, calls `callback()`.

Notes:
- To receive hotkeys while an elevated window is focused, run this program as admin.
- If Alt+N is already taken by another app, start_alt_n_hotkey raises RuntimeError.
"""

import threading
import win32con
import win32gui
import win32api

# Constants
MOD_ALT = win32con.MOD_ALT
VK_N = 0x4E  # 'N'
_HOTKEY_ID = 1

# Optional: reduce key-repeat storms (define MOD_NOREPEAT if not present)
try:
    MOD_NOREPEAT = win32con.MOD_NOREPEAT  # available on newer pywin32
except AttributeError:
    MOD_NOREPEAT = 0x4000  # documented Win32 flag


class HotkeyRunner:
    """Holds the worker thread and window handle; call .stop() to unregister/quit."""
    def __init__(self, thread: threading.Thread, hwnd: int):
        self._thread = thread
        self._hwnd = hwnd

    def stop(self) -> None:
        """Unregisters the hotkey and shuts down the message loop thread."""
        hwnd = self._hwnd
        self._hwnd = 0
        try:
            if hwnd:
                # Unregister first; then close the window and quit the message loop.
                try:
                    win32gui.UnregisterHotKey(hwnd, _HOTKEY_ID)
                except Exception:
                    pass
                try:
                    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                except Exception:
                    pass
        finally:
            if self._thread and self._thread.is_alive():
                # Give the message pump a moment to exit cleanly
                self._thread.join(timeout=1.0)


def start_alt_n_hotkey(callback) -> HotkeyRunner:
    """
    Registers Alt+N globally and invokes `callback()` on each press.
    Runs the Win32 message loop in a daemon thread. Returns a HotkeyRunner.
    Raises RuntimeError if Alt+N is already registered by another app.
    """
    state = {"hwnd": 0, "error": None}  # filled by thread after CreateWindow

    def thread_proc():
        # Window class and procedure
        wc = win32gui.WNDCLASS()
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "NorskLookupHotkeyWnd"

        def _wndproc(hWnd, msg, wParam, lParam):
            if msg == win32con.WM_HOTKEY and wParam == _HOTKEY_ID:
                try:
                    callback()
                except Exception:
                    # Swallow to keep the pump alive
                    pass
                return 0
            elif msg == win32con.WM_DESTROY:
                win32gui.PostQuitMessage(0)
                return 0
            return win32gui.DefWindowProc(hWnd, msg, wParam, lParam)

        wc.lpfnWndProc = _wndproc
        atom = win32gui.RegisterClass(wc)

        # Hidden message-only window works too, but a normal hidden window is fine
        hwnd = win32gui.CreateWindow(
            atom, "NorskLookupHidden", 0,
            0, 0, 0, 0,
            0, 0, wc.hInstance, None
        )
        state["hwnd"] = hwnd

        # Try to register Alt+N (with MOD_NOREPEAT if available)
        mods = MOD_ALT | MOD_NOREPEAT
        try:
            ok = win32gui.RegisterHotKey(hwnd, _HOTKEY_ID, mods, VK_N)
            if not ok:
                state["error"] = RuntimeError("Alt+N is already registered by another app")
                return
        except Exception as e:
            state["error"] = RuntimeError(f"Failed to register Alt+N: {e}")
            try:
                win32gui.DestroyWindow(hwnd)
            except Exception:
                pass
            return

        # Block here handling messages until WM_QUIT
        try:
            win32gui.PumpMessages()
        finally:
            # Ensure cleanup if the loop exits unexpectedly
            try:
                win32gui.UnregisterHotKey(hwnd, _HOTKEY_ID)
            except Exception:
                pass
            try:
                win32gui.DestroyWindow(hwnd)
            except Exception:
                pass

    t = threading.Thread(target=thread_proc, daemon=True)
    t.start()

    # Wait briefly for hwnd to be created so .stop() can work immediately
    for _ in range(100):
        if state["hwnd"] or state["error"]:
            break
        win32api.Sleep(10)

    if state["error"]:
        raise state["error"]

    return HotkeyRunner(thread=t, hwnd=state["hwnd"])
