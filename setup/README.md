# Global hotkey via Win32 RegisterHotKey (reliable, OS-delivered).

import threading
import win32con, win32api, win32gui

MOD_ALT = win32con.MOD_ALT
VK_N = 0x4E
_HOTKEY_ID = 1

class HotkeyRunner:
    def __init__(self, thread: threading.Thread, hwnd: int):
        self._thread = thread
        self._hwnd = hwnd

    def stop(self):
        try:
            # Unregister and close the window, which ends PumpMessages.
            win32api.UnregisterHotKey(self._hwnd, _HOTKEY_ID)
        except Exception:
            pass
        try:
            if self._hwnd:
                win32gui.PostMessage(self._hwnd, win32con.WM_CLOSE, 0, 0)
        except Exception:
            pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

def start_alt_n_hotkey(callback) -> HotkeyRunner:
    """
    Registers Alt+N globally and calls `callback()` on each press.
    Runs the message loop in a background thread.
    Returns a HotkeyRunner with stop().
    """

    def thread_proc():
        # Create a tiny hidden window to receive WM_HOTKEY
        wc = win32gui.WNDCLASS()
        wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "NorskLookupHotkeyWnd"
        def _wndproc(hWnd, msg, wParam, lParam):
            if msg == win32con.WM_HOTKEY and wParam == _HOTKEY_ID:
                try:
                    callback()
                except Exception:
                    pass
                return 0
            return win32gui.DefWindowProc(hWnd, msg, wParam, lParam)
        wc.lpfnWndProc = _wndproc
        atom = win32gui.RegisterClass(wc)
        hwnd = win32gui.CreateWindow(
            atom, "hidden", 0, 0, 0, 0, 0,
            0, 0, wc.hInstance, None
        )

        # Try to register Alt+N
        ok = win32api.RegisterHotKey(hwnd, _HOTKEY_ID, MOD_ALT, VK_N)
        if not ok:
            # Clean up then raise (caught in outer scope)
            win32gui.DestroyWindow(hwnd)
            raise RuntimeError("Alt+N is already registered by another app")

        # Store hwnd where stop() can find it
        _runner_state["hwnd"] = hwnd

        # Message loop (blocks this thread)
        try:
            win32gui.PumpMessages()
        finally:
            try:
                win32api.UnregisterHotKey(hwnd, _HOTKEY_ID)
            except Exception:
                pass
            try:
                win32gui.DestroyWindow(hwnd)
            except Exception:
                pass

    _runner_state = {"hwnd": 0}
    t = threading.Thread(target=thread_proc, daemon=True)
    t.start()

    # Wait briefly for hwnd creation
    for _ in range(100):
        if _runner_state["hwnd"]:
            break
        win32api.Sleep(10)

    return HotkeyRunner(thread=t, hwnd=_runner_state["hwnd"])
