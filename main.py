#!/usr/bin/env python3
"""
Text Display Utility - Shows highlighted text in popup without touching clipboard
Hotkey: Alt+P+N
"""

import sys
import ctypes
import ctypes.wintypes
import threading
import time
import tkinter as tk
from typing import Optional

# Windows API constants
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
VK_MENU = 0x12  # Alt
VK_P = 0x50
VK_N = 0x4E

# For getting selected text via UI Automation
try:
    import comtypes.client
    import comtypes.gen.UIAutomationClient as UIA
    UI_AUTOMATION_AVAILABLE = True
except ImportError:
    UI_AUTOMATION_AVAILABLE = False
    print("WARNING: comtypes not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "comtypes"])
    import comtypes.client
    import comtypes.gen.UIAutomationClient as UIA
    UI_AUTOMATION_AVAILABLE = True


class TextCapture:
    """Gets selected text using UI Automation - no clipboard interaction."""
    
    @staticmethod
    def get_selected_text() -> Optional[str]:
        """Get selected text from the focused control."""
        try:
            # Initialize UI Automation
            uia = comtypes.client.CreateObject(
                "{ff48dba4-60ef-4201-aa87-54103eef594e}",
                interface=UIA.IUIAutomation
            )
            
            # Get focused element
            element = uia.GetFocusedElement()
            if not element:
                return None
            
            # Try to get text selection via TextPattern
            try:
                text_pattern = element.GetCurrentPattern(UIA.UIA_TextPatternId)
                if text_pattern:
                    text_pattern = text_pattern.QueryInterface(UIA.IUIAutomationTextPattern)
                    selection = text_pattern.GetSelection()
                    if selection and selection.Length > 0:
                        range_obj = selection.GetElement(0)
                        text = range_obj.GetText(-1)
                        if text and text.strip():
                            return text.strip()
            except:
                pass
            
            # Try TextPattern2 (newer API)
            try:
                pattern = element.GetCurrentPattern(UIA.UIA_TextPattern2Id)
                if pattern:
                    pattern = pattern.QueryInterface(UIA.IUIAutomationTextPattern2)
                    selection = pattern.GetSelection()
                    if selection and selection.Length > 0:
                        range_obj = selection.GetElement(0)
                        text = range_obj.GetText(-1)
                        if text and text.strip():
                            return text.strip()
            except:
                pass
                
        except Exception:
            pass
        
        return None


class PopupManager:
    """Manages popup windows."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.current_popup = None
    
    def show(self, text: str):
        """Display text in a popup near the cursor."""
        # Close existing popup
        if self.current_popup:
            try:
                self.current_popup.destroy()
            except:
                pass
        
        if not text:
            return
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.configure(bg="black")
        
        # Create border frame
        border = tk.Frame(popup, bg="black", bd=1)
        border.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Inner frame
        inner = tk.Frame(border, bg="#1e1e1e")
        inner.pack(fill="both", expand=True)
        
        # Text label
        label = tk.Label(
            inner,
            text=text,
            bg="#1e1e1e",
            fg="white",
            font=("Consolas", 11),
            padx=12,
            pady=8,
            anchor="w",
            justify="left"
        )
        label.pack()
        
        # Position near cursor
        popup.update_idletasks()
        x = popup.winfo_pointerx() + 10
        y = popup.winfo_pointery() + 10
        
        # Ensure it fits on screen
        width = popup.winfo_width()
        height = popup.winfo_height()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        
        if x + width > screen_width:
            x = screen_width - width - 10
        if y + height > screen_height:
            y = screen_height - height - 10
            
        popup.geometry(f"+{x}+{y}")
        
        # Auto-close after 3 seconds
        popup.after(3000, lambda: popup.destroy() if popup.winfo_exists() else None)
        
        # Close on click
        popup.bind("<Button-1>", lambda e: popup.destroy())
        label.bind("<Button-1>", lambda e: popup.destroy())
        
        self.current_popup = popup


class HotkeyMonitor:
    """Monitors keyboard for Alt+P+N combination."""
    
    def __init__(self, callback):
        self.callback = callback
        self.keys_pressed = set()
        self.running = True
        
    def check_keys(self):
        """Check if Alt+P+N are all pressed."""
        # Use GetAsyncKeyState to check key states
        alt = ctypes.windll.user32.GetAsyncKeyState(VK_MENU) & 0x8000
        p = ctypes.windll.user32.GetAsyncKeyState(VK_P) & 0x8000
        n = ctypes.windll.user32.GetAsyncKeyState(VK_N) & 0x8000
        
        if alt and p and n:
            if 'triggered' not in self.keys_pressed:
                self.keys_pressed.add('triggered')
                self.callback()
        else:
            self.keys_pressed.discard('triggered')
    
    def run(self):
        """Monitor loop."""
        while self.running:
            self.check_keys()
            time.sleep(0.05)  # Check 20 times per second
    
    def stop(self):
        """Stop monitoring."""
        self.running = False


class TextDisplayApp:
    """Main application."""
    
    def __init__(self):
        # Create hidden Tk root
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Create popup manager
        self.popup = PopupManager(self.root)
        
        # Create hotkey monitor
        self.monitor = HotkeyMonitor(self.on_hotkey)
        self.monitor_thread = None
        
    def on_hotkey(self):
        """Handle hotkey press."""
        # Get selected text
        text = TextCapture.get_selected_text()
        
        if text:
            # Show popup on main thread
            self.root.after(0, lambda: self.popup.show(text))
    
    def run(self):
        """Run the application."""
        print("Text Display Utility Started")
        print("Select text and press Alt+P+N to display it")
        print("Press Ctrl+C to exit")
        print("-" * 40)
        
        # Start monitor in background thread
        self.monitor_thread = threading.Thread(target=self.monitor.run, daemon=True)
        self.monitor_thread.start()
        
        try:
            # Run Tk event loop
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.monitor.stop()
            if self.monitor_thread:
                self.monitor_thread.join(timeout=0.5)


def main():
    """Entry point."""
    try:
        app = TextDisplayApp()
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())