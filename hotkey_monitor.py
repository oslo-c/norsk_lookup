"""
Hotkey monitoring module - handles keyboard input detection.
"""

import ctypes
import time
import threading
from typing import Callable, Set, List, Tuple
from dataclasses import dataclass


# Windows Virtual Key Codes
VK_MENU = 0x12  # Alt
VK_CONTROL = 0x11  # Ctrl
VK_SHIFT = 0x10  # Shift


@dataclass
class Hotkey:
    """Represents a keyboard hotkey combination."""
    keys: Tuple[int, ...]
    description: str
    
    def is_pressed(self) -> bool:
        """Check if all keys in the combination are currently pressed."""
        for key in self.keys:
            if not (ctypes.windll.user32.GetAsyncKeyState(key) & 0x8000):
                return False
        return True


class HotkeyMonitor:
    """Monitors keyboard for specific hotkey combinations."""
    
    def __init__(self, hotkey: Hotkey, callback: Callable[[], None], poll_rate: float = 0.05):
        """
        Initialize the hotkey monitor.
        
        Args:
            hotkey: The hotkey combination to monitor
            callback: Function to call when hotkey is pressed
            poll_rate: How often to check keys (in seconds)
        """
        self.hotkey = hotkey
        self.callback = callback
        self.poll_rate = poll_rate
        self.running = False
        self.triggered = False
        self._thread = None
    
    def start(self):
        """Start monitoring in a background thread."""
        if self.running:
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self, timeout: float = 0.5):
        """
        Stop monitoring.
        
        Args:
            timeout: Maximum time to wait for thread to stop
        """
        if not self.running:
            return
        
        self.running = False
        if self._thread:
            self._thread.join(timeout=timeout)
            self._thread = None
    
    def _monitor_loop(self):
        """Main monitoring loop - runs in background thread."""
        while self.running:
            self._check_hotkey()
            time.sleep(self.poll_rate)
    
    def _check_hotkey(self):
        """Check if the hotkey is pressed and trigger callback if needed."""
        if self.hotkey.is_pressed():
            if not self.triggered:
                self.triggered = True
                try:
                    self.callback()
                except Exception as e:
                    # Log but don't crash the monitor
                    print(f"Error in hotkey callback: {e}")
        else:
            self.triggered = False


class MultiHotkeyMonitor:
    """Monitors multiple hotkeys simultaneously."""
    
    def __init__(self, poll_rate: float = 0.05):
        """
        Initialize the multi-hotkey monitor.
        
        Args:
            poll_rate: How often to check keys (in seconds)
        """
        self.poll_rate = poll_rate
        self.hotkeys: List[Tuple[Hotkey, Callable]] = []
        self.running = False
        self.triggered_states: Set[int] = set()
        self._thread = None
    
    def register(self, hotkey: Hotkey, callback: Callable[[], None]):
        """
        Register a new hotkey.
        
        Args:
            hotkey: The hotkey combination to monitor
            callback: Function to call when hotkey is pressed
        """
        self.hotkeys.append((hotkey, callback))
    
    def start(self):
        """Start monitoring all registered hotkeys."""
        if self.running:
            return
        
        self.running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self, timeout: float = 0.5):
        """
        Stop monitoring.
        
        Args:
            timeout: Maximum time to wait for thread to stop
        """
        if not self.running:
            return
        
        self.running = False
        if self._thread:
            self._thread.join(timeout=timeout)
            self._thread = None
    
    def _monitor_loop(self):
        """Main monitoring loop - runs in background thread."""
        while self.running:
            self._check_all_hotkeys()
            time.sleep(self.poll_rate)
    
    def _check_all_hotkeys(self):
        """Check all registered hotkeys."""
        for idx, (hotkey, callback) in enumerate(self.hotkeys):
            if hotkey.is_pressed():
                if idx not in self.triggered_states:
                    self.triggered_states.add(idx)
                    try:
                        callback()
                    except Exception as e:
                        print(f"Error in hotkey callback: {e}")
            else:
                self.triggered_states.discard(idx)


# Common key code constants for convenience
class VirtualKeys:
    """Common virtual key codes for Windows."""
    ALT = VK_MENU
    CTRL = VK_CONTROL
    SHIFT = VK_SHIFT
    
    # Letters
    A = 0x41
    B = 0x42
    C = 0x43
    D = 0x44
    E = 0x45
    F = 0x46
    G = 0x47
    H = 0x48
    I = 0x49
    J = 0x4A
    K = 0x4B
    L = 0x4C
    M = 0x4D
    N = 0x4E
    O = 0x4F
    P = 0x50
    Q = 0x51
    R = 0x52
    S = 0x53
    T = 0x54
    U = 0x55
    V = 0x56
    W = 0x57
    X = 0x58
    Y = 0x59
    Z = 0x5A