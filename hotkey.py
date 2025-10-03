"""
hotkey.py — Global hotkey detection using low-level keyboard hook.

Exports:
    start_alt_n_hotkey(callback) -> HotkeyRunner
        Detects Alt+P+N pressed simultaneously. On press, calls `callback()`.

Notes:
- Uses low-level keyboard hook to detect Alt+P+N all pressed at the same time.
- To receive hotkeys while an elevated window is focused, run this program as admin.
"""

import threading
import win32gui
import win32con
import win32api
from ctypes import windll, CFUNCTYPE, c_int, c_void_p, byref
from ctypes.wintypes import DWORD, WPARAM, LPARAM, MSG


# Virtual key codes
VK_MENU = 0x12  # Alt key
VK_P = 0x50
VK_N = 0x4E

# Hook constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105

# Keyboard hook callback type
HOOKPROC = CFUNCTYPE(c_int, c_int, WPARAM, LPARAM)


class HotkeyRunner:
    """Holds the keyboard hook; call .stop() to unregister."""
    def __init__(self, thread, hook_id):
        self._thread = thread
        self._hook_id = hook_id
        self._stop_event = threading.Event()

    def stop(self) -> None:
        """Unregisters the keyboard hook and stops the thread."""
        self._stop_event.set()
        if self._hook_id:
            try:
                windll.user32.UnhookWindowsHookEx(self._hook_id)
            except:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)


def start_alt_n_hotkey(callback) -> HotkeyRunner:
    """
    Detects Alt+P+N pressed simultaneously and invokes `callback()`.
    Returns a HotkeyRunner.
    """
    state = {
        "hook_id": None,
        "error": None,
        "keys_pressed": set(),
        "triggered": False
    }
    stop_event = threading.Event()

    def thread_proc():
        # Keep reference to avoid garbage collection
        def low_level_keyboard_proc(nCode, wParam, lParam):
            # CRITICAL: Always call CallNextHookEx to prevent blocking keyboard input
            # Must be done before ANY processing to ensure keyboard events propagate
            try:
                if nCode >= 0:
                    try:
                        # Read the virtual key code from lParam (first DWORD)
                        vk = DWORD.from_address(lParam).value

                        # Track key presses
                        if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                            state["keys_pressed"].add(vk)

                            # Check if Alt is held down
                            alt_pressed = windll.user32.GetAsyncKeyState(VK_MENU) & 0x8000
                            p_pressed = windll.user32.GetAsyncKeyState(VK_P) & 0x8000
                            n_pressed = windll.user32.GetAsyncKeyState(VK_N) & 0x8000

                            # If all three keys are pressed and we haven't triggered yet
                            if alt_pressed and p_pressed and n_pressed and not state["triggered"]:
                                state["triggered"] = True
                                print("Alt+P+N detected!")
                                try:
                                    callback()
                                except Exception as e:
                                    print(f"Callback error: {e}")

                        elif wParam in (WM_KEYUP, WM_SYSKEYUP):
                            state["keys_pressed"].discard(vk)
                            # Reset trigger when any of the keys is released
                            if vk in (VK_MENU, VK_P, VK_N):
                                state["triggered"] = False
                    except Exception as e:
                        print(f"Hook processing error: {e}")
            except:
                pass

            # ALWAYS call the next hook, regardless of what happened above
            return windll.user32.CallNextHookEx(state["hook_id"], nCode, wParam, lParam)

        # Create the hook callback and keep it alive
        hook_proc = HOOKPROC(low_level_keyboard_proc)
        state["hook_proc"] = hook_proc  # Prevent garbage collection

        # Install the hook
        try:
            hook_id = windll.user32.SetWindowsHookExW(
                WH_KEYBOARD_LL,
                hook_proc,
                None,  # NULL for low-level hooks
                0
            )

            if not hook_id:
                error_code = windll.kernel32.GetLastError()
                state["error"] = RuntimeError(f"Failed to install keyboard hook (error {error_code})")
                return

            state["hook_id"] = hook_id
            print("Registered low-level keyboard hook for Alt+P+N")
        except Exception as e:
            state["error"] = RuntimeError(f"Exception installing hook: {e}")
            return

        # Message loop
        msg = MSG()
        while not stop_event.is_set():
            result = windll.user32.PeekMessageW(byref(msg), None, 0, 0, 1)  # PM_REMOVE = 1
            if result:
                windll.user32.TranslateMessage(byref(msg))
                windll.user32.DispatchMessageW(byref(msg))
            else:
                win32api.Sleep(10)

    t = threading.Thread(target=thread_proc, daemon=True)
    t.start()

    # Wait for hook installation
    for _ in range(100):
        if state["hook_id"] or state["error"]:
            break
        win32api.Sleep(10)

    if state["error"]:
        raise state["error"]

    runner = HotkeyRunner(t, state["hook_id"])
    runner._stop_event = stop_event
    return runner
