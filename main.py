#!/usr/bin/env python3
"""
Norwegian-English Dictionary Lookup - Shows translations in popup.

This is the main entry point that coordinates all components.
"""

import sys
import tkinter as tk
import threading

from text_capture import TextCapture
from popup_ui import PopupManager, PopupConfig, MonitorHelper
from hotkey_monitor import HotkeyMonitor, Hotkey, VirtualKeys
from lexin_api import LexinAPI


class TextDisplayApp:
    """Main application coordinator."""
    
    def __init__(self, hotkey: Hotkey = None, popup_config: PopupConfig = None):
        """
        Initialize the application.
        
        Args:
            hotkey: Custom hotkey configuration (default: Alt+P+N)
            popup_config: Custom popup styling configuration
        """
        # Create hidden Tk root
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Initialize components
        self.text_capture = TextCapture()
        self.popup_manager = PopupManager(self.root, popup_config)
        self.lexin_api = LexinAPI()
        
        # Setup hotkey (default: Alt+P+N)
        if hotkey is None:
            hotkey = Hotkey(
                keys=(VirtualKeys.ALT, VirtualKeys.P, VirtualKeys.N),
                description="Alt+P+N"
            )
        
        self.hotkey = hotkey
        self.monitor = HotkeyMonitor(hotkey, self._on_hotkey_pressed)
    
    def _on_hotkey_pressed(self):
        """Handle hotkey activation."""
        # Get selected text
        text = self.text_capture.get_selected_text()
        
        if text:
            # Clean up the text - get first word if multiple words selected
            word = text.strip().split()[0] if text.strip() else text.strip()
            
            # Capture cursor position immediately
            cursor_pos = MonitorHelper.get_cursor_position()
            
            # Show immediate "Thinking..." popup at the captured position
            self.root.after(0, lambda: self.popup_manager.show("Thinking...", position=cursor_pos))
            
            # Look up translation in background thread
            def lookup_translation():
                # Look up in Lexin dictionary
                translations = self.lexin_api.lookup(word, max_results=3)
                
                # Format the display text
                if translations:
                    display_text = self.lexin_api.format_results(translations, include_definitions=False)
                else:
                    # Fallback to showing the selected text if no translation found
                    display_text = f"'{word}' - No translation found"
                
                # Update popup on main thread (without passing position - it will reuse the stored one)
                self.root.after(0, lambda: self.popup_manager.show(display_text))
            
            # Start lookup in background thread
            thread = threading.Thread(target=lookup_translation, daemon=True)
            thread.start()
    
    def run(self):
        """Run the application."""
        self._print_startup_info()
        
        # Start hotkey monitoring
        self.monitor.start()
        
        try:
            # Run Tk event loop
            self.root.mainloop()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self._cleanup()
    
    def _print_startup_info(self):
        """Print startup information to console."""
        print("Norwegian-English Dictionary Lookup Started")
        print(f"Hotkey: {self.hotkey.description}")
        print("Select a Norwegian word and press the hotkey to translate it")
        print("Press Ctrl+C to exit")
        print("-" * 40)
    
    def _cleanup(self):
        """Clean up resources."""
        self.monitor.stop()
        self.popup_manager.close_current()


def main():
    """Entry point for the application."""
    try:
        # You can customize the app here
        # Example with custom hotkey:
        # custom_hotkey = Hotkey(
        #     keys=(VirtualKeys.CTRL, VirtualKeys.SHIFT, VirtualKeys.T),
        #     description="Ctrl+Shift+T"
        # )
        # app = TextDisplayApp(hotkey=custom_hotkey)
        
        # Example with custom popup styling:
        # custom_config = PopupConfig(
        #     bg_color="#2d2d2d",
        #     fg_color="#00ff00",
        #     font_size=12
        # )
        # app = TextDisplayApp(popup_config=custom_config)
        
        # Default configuration
        app = TextDisplayApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())