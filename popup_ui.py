"""
Popup UI module - handles displaying text in popup windows.
"""

import tkinter as tk
import ctypes
import ctypes.wintypes
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class MonitorInfo:
    """Information about a monitor's position and dimensions."""
    left: int
    top: int
    right: int
    bottom: int
    
    @property
    def width(self) -> int:
        return self.right - self.left
    
    @property
    def height(self) -> int:
        return self.bottom - self.top
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if a point is within this monitor."""
        return self.left <= x < self.right and self.top <= y < self.bottom


class MonitorHelper:
    """Helper class for multi-monitor support on Windows."""
    
    @staticmethod
    def get_all_monitors() -> List[MonitorInfo]:
        """Get information about all connected monitors."""
        monitors = []
        
        def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            """Callback for EnumDisplayMonitors."""
            rect = lprcMonitor.contents
            monitors.append(MonitorInfo(
                left=rect.left,
                top=rect.top,
                right=rect.right,
                bottom=rect.bottom
            ))
            return 1  # Continue enumeration
        
        # Define callback type
        MonitorEnumProc = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_ulong,
            ctypes.c_ulong,
            ctypes.POINTER(ctypes.wintypes.RECT),
            ctypes.c_double
        )
        
        # Call EnumDisplayMonitors
        callback_func = MonitorEnumProc(callback)
        ctypes.windll.user32.EnumDisplayMonitors(None, None, callback_func, 0)
        
        return monitors
    
    @staticmethod
    def get_monitor_at_point(x: int, y: int) -> Optional[MonitorInfo]:
        """Get the monitor that contains the given point."""
        monitors = MonitorHelper.get_all_monitors()
        
        for monitor in monitors:
            if monitor.contains_point(x, y):
                return monitor
        
        # Fallback to first monitor if point not found
        return monitors[0] if monitors else None
    
    @staticmethod
    def get_cursor_position() -> Tuple[int, int]:
        """Get the current cursor position in screen coordinates."""
        point = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        return point.x, point.y


class PopupConfig:
    """Configuration for popup appearance."""
    
    def __init__(
        self,
        bg_color: str = "#1e1e1e",
        fg_color: str = "white",
        border_color: str = "black",
        font_family: str = "Consolas",
        font_size: int = 11,
        padding_x: int = 12,
        padding_y: int = 8,
        auto_close_ms: Optional[int] = None,  # None means stay open until unfocused
        focus_poll_ms: int = 150,  # How often to check focus
        offset_x: int = 10,
        offset_y: int = 10
    ):
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.border_color = border_color
        self.font_family = font_family
        self.font_size = font_size
        self.padding_x = padding_x
        self.padding_y = padding_y
        self.auto_close_ms = auto_close_ms
        self.focus_poll_ms = focus_poll_ms
        self.offset_x = offset_x
        self.offset_y = offset_y


class PopupManager:
    """Manages popup windows for displaying text."""
    
    def __init__(self, root: tk.Tk, config: Optional[PopupConfig] = None):
        """
        Initialize the popup manager.
        
        Args:
            root: The Tk root window
            config: Optional popup configuration
        """
        self.root = root
        self.config = config or PopupConfig()
        self.current_popup = None
        self._focus_check_id = None
    
    def show(self, text: str):
        """
        Display text in a popup near the cursor.
        
        Args:
            text: The text to display
        """
        # Close existing popup
        self.close_current()
        
        if not text:
            return
        
        # Create and configure popup
        popup = self._create_popup(text)
        self._position_popup(popup)
        self._setup_focus_tracking(popup)
        self._setup_click_to_close(popup)
        
        # Only setup auto-close if configured
        if self.config.auto_close_ms is not None:
            self._setup_auto_close(popup)
        
        self.current_popup = popup
    
    def close_current(self):
        """Close the current popup if it exists."""
        # Cancel any pending focus checks
        if self._focus_check_id:
            try:
                self.root.after_cancel(self._focus_check_id)
            except:
                pass
            self._focus_check_id = None
        
        if self.current_popup:
            try:
                self.current_popup.destroy()
            except:
                pass
            self.current_popup = None
    
    def _create_popup(self, text: str) -> tk.Toplevel:
        """Create the popup window with styled content."""
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(bg=self.config.border_color)
        
        # Create border frame
        border = tk.Frame(popup, bg=self.config.border_color, bd=1)
        border.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Inner frame
        inner = tk.Frame(border, bg=self.config.bg_color)
        inner.pack(fill="both", expand=True)
        
        # Text label
        label = tk.Label(
            inner,
            text=text,
            bg=self.config.bg_color,
            fg=self.config.fg_color,
            font=(self.config.font_family, self.config.font_size),
            padx=self.config.padding_x,
            pady=self.config.padding_y,
            anchor="w",
            justify="left"
        )
        label.pack()
        
        # Store label for click binding
        popup._label = label
        
        return popup
    
    def _position_popup(self, popup: tk.Toplevel):
        """Position popup near cursor, ensuring it stays on screen."""
        popup.update_idletasks()
        
        # Get actual cursor position using Windows API
        cursor_x, cursor_y = MonitorHelper.get_cursor_position()
        
        # Find which monitor the cursor is on
        monitor = MonitorHelper.get_monitor_at_point(cursor_x, cursor_y)
        
        if monitor is None:
            # Fallback to old behavior if we can't detect monitors
            self._position_popup_fallback(popup)
            return
        
        # Start position near cursor
        x = cursor_x + self.config.offset_x
        y = cursor_y + self.config.offset_y
        
        # Get popup dimensions
        width = popup.winfo_width()
        height = popup.winfo_height()
        
        # Keep popup within the current monitor's bounds
        if x + width > monitor.right:
            x = monitor.right - width - 10
        if x < monitor.left:
            x = monitor.left + 10
        
        if y + height > monitor.bottom:
            y = monitor.bottom - height - 10
        if y < monitor.top:
            y = monitor.top + 10
        
        popup.geometry(f"+{x}+{y}")
    
    def _position_popup_fallback(self, popup: tk.Toplevel):
        """Fallback positioning method (original behavior)."""
        x = popup.winfo_pointerx() + self.config.offset_x
        y = popup.winfo_pointery() + self.config.offset_y
        
        width = popup.winfo_width()
        height = popup.winfo_height()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        
        if x + width > screen_width:
            x = screen_width - width - 10
        if y + height > screen_height:
            y = screen_height - height - 10
        
        popup.geometry(f"+{x}+{y}")
    
    def _setup_auto_close(self, popup: tk.Toplevel):
        """Setup automatic closing after timeout."""
        def close_if_exists():
            if popup.winfo_exists():
                popup.destroy()
        
        popup.after(self.config.auto_close_ms, close_if_exists)
    
    def _setup_focus_tracking(self, popup: tk.Toplevel):
        """Setup focus tracking to close popup when it loses focus or on any outside click."""
        
        # Track if we're currently processing a click
        popup._processing_click = False
        
        def on_global_click(event=None):
            """Handle any mouse click globally."""
            if popup._processing_click:
                return
            
            popup._processing_click = True
            
            try:
                if not popup.winfo_exists():
                    return
                
                # Get current mouse position
                mouse_x = popup.winfo_pointerx()
                mouse_y = popup.winfo_pointery()
                
                # Get popup bounds
                popup_x = popup.winfo_rootx()
                popup_y = popup.winfo_rooty()
                popup_width = popup.winfo_width()
                popup_height = popup.winfo_height()
                
                # Check if click is outside popup bounds
                if not (popup_x <= mouse_x <= popup_x + popup_width and
                        popup_y <= mouse_y <= popup_y + popup_height):
                    popup.destroy()
            except:
                pass
            finally:
                popup._processing_click = False
        
        # Bind to the root window to catch all clicks
        def setup_global_binding():
            try:
                # Bind to the main application root
                root = popup._root()
                if root:
                    root.bind_all("<Button-1>", on_global_click, add="+")
                    root.bind_all("<Button-2>", on_global_click, add="+")
                    root.bind_all("<Button-3>", on_global_click, add="+")
                    
                    # Store binding info for cleanup
                    popup._global_bindings = True
            except:
                pass
        
        # Setup bindings after popup is fully displayed
        popup.after(50, setup_global_binding)
        
        # Cleanup bindings when popup is destroyed
        def cleanup_bindings():
            try:
                root = popup._root()
                if root and hasattr(popup, '_global_bindings'):
                    root.unbind_all("<Button-1>")
                    root.unbind_all("<Button-2>")
                    root.unbind_all("<Button-3>")
            except:
                pass
        
        popup.bind("<Destroy>", lambda e: cleanup_bindings())
        
        # Also handle focus loss as backup
        def on_focus_out(event=None):
            popup.after(100, lambda: close_if_unfocused())
        
        def close_if_unfocused():
            try:
                if popup.winfo_exists():
                    focused = popup.focus_displayof()
                    if focused is None or focused.winfo_toplevel() != popup:
                        popup.destroy()
            except:
                pass
        
        popup.bind("<FocusOut>", on_focus_out)
    
    def _setup_click_to_close(self, popup: tk.Toplevel):
        """Setup click-to-close functionality."""
        def close_popup(event=None):
            popup.destroy()
        
        popup.bind("<Button-1>", close_popup)
        popup._label.bind("<Button-1>", close_popup)