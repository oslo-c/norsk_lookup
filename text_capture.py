"""
Text capture module - handles getting selected text via UI Automation.
"""

import sys
from typing import Optional

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
    
    def __init__(self):
        """Initialize the text capture system."""
        self._uia = None
    
    def _get_uia(self):
        """Lazy initialization of UI Automation."""
        if self._uia is None:
            self._uia = comtypes.client.CreateObject(
                "{ff48dba4-60ef-4201-aa87-54103eef594e}",
                interface=UIA.IUIAutomation
            )
        return self._uia
    
    def get_selected_text(self) -> Optional[str]:
        """
        Get selected text from the focused control.
        
        Returns:
            Selected text if found, None otherwise.
        """
        try:
            uia = self._get_uia()
            element = uia.GetFocusedElement()
            
            if not element:
                return None
            
            # Try TextPattern first
            text = self._try_text_pattern(element)
            if text:
                return text
            
            # Try TextPattern2 (newer API)
            text = self._try_text_pattern2(element)
            if text:
                return text
                
        except Exception as e:
            # Silent failure - return None
            pass
        
        return None
    
    def _try_text_pattern(self, element) -> Optional[str]:
        """Try to get text using TextPattern."""
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
        return None
    
    def _try_text_pattern2(self, element) -> Optional[str]:
        """Try to get text using TextPattern2 (newer API)."""
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
        return None