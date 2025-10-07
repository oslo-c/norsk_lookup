"""
Text capture module - handles getting selected text via UI Automation.
"""

import sys
import os
from typing import Optional

# Import comtypes first, THEN configure the cache
import comtypes
import comtypes.client

# Fix for PyInstaller: Set comtypes cache to a writable location AFTER importing
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    cache_dir = os.path.join(os.environ.get('TEMP', os.environ.get('TMP', '.')), 'comtypes_cache')
    os.makedirs(cache_dir, exist_ok=True)
    # Override the gen_dir function
    if hasattr(comtypes.client, '_code_cache'):
        original_find_gen_dir = comtypes.client._code_cache._find_gen_dir
        comtypes.client._code_cache._find_gen_dir = lambda: cache_dir
    print(f"DEBUG: Using comtypes cache at: {cache_dir}")

# Force generation of UIAutomation interfaces
try:
    comtypes.client.GetModule('UIAutomationCore.dll')
    print("DEBUG: UIAutomationCore module loaded")
except Exception as e:
    print(f"DEBUG: Could not load UIAutomationCore: {e}")

# Now import the generated interfaces
try:
    import comtypes.gen.UIAutomationClient as UIA
    print("DEBUG: UIAutomationClient imported successfully")
except ImportError as e:
    print(f"ERROR: Could not import UIAutomationClient: {e}")
    # Try to generate it
    try:
        comtypes.client.GetModule('UIAutomationCore.dll')
        import comtypes.gen.UIAutomationClient as UIA
        print("DEBUG: UIAutomationClient generated and imported")
    except Exception as e2:
        print(f"ERROR: Failed to generate UIAutomationClient: {e2}")
        raise


class TextCapture:
    """Gets selected text using UI Automation - no clipboard interaction."""
    
    def __init__(self):
        """Initialize the text capture system."""
        self._uia = None
        self._com_initialized = False
    
    def _ensure_com_initialized(self):
        """Ensure COM is initialized for this thread."""
        if not self._com_initialized:
            try:
                import comtypes
                # Initialize COM for this thread
                comtypes.CoInitialize()
                self._com_initialized = True
                print("DEBUG: COM initialized successfully")
            except Exception as e:
                print(f"DEBUG: COM initialization: {e}")
                # If already initialized, that's fine
                self._com_initialized = True
    
    def _get_uia(self):
        """Lazy initialization of UI Automation."""
        if self._uia is None:
            try:
                # Ensure COM is initialized first
                self._ensure_com_initialized()
                
                self._uia = comtypes.client.CreateObject(
                    "{ff48dba4-60ef-4201-aa87-54103eef594e}",
                    interface=UIA.IUIAutomation
                )
                print("DEBUG: UIAutomation object created successfully")
            except Exception as e:
                print(f"ERROR: Failed to create UIAutomation object: {e}")
                raise
        return self._uia
    
    def get_selected_text(self) -> Optional[str]:
        """
        Get selected text from the focused control.
        
        Returns:
            Selected text if found, None otherwise.
        """
        try:
            # Small delay to ensure selection is stable
            import time
            time.sleep(0.05)
            
            uia = self._get_uia()
            element = uia.GetFocusedElement()
            
            if not element:
                print("DEBUG: No focused element")
                return None
            
            # Debug: print element info
            try:
                name = element.CurrentName
                control_type = element.CurrentControlType
                class_name = element.CurrentClassName
                print(f"DEBUG: Focused element:")
                print(f"  Name: '{name}'")
                print(f"  ControlType: {control_type}")
                print(f"  ClassName: '{class_name}'")
            except Exception as e:
                print(f"DEBUG: Could not get element details: {e}")
            
            # Try TextPattern first
            text = self._try_text_pattern(element)
            if text:
                print(f"DEBUG: Got text from TextPattern: '{text}'")
                return text
            
            # Try TextPattern2 (newer API)
            text = self._try_text_pattern2(element)
            if text:
                print(f"DEBUG: Got text from TextPattern2: '{text}'")
                return text
            
            # Try ValuePattern as fallback
            text = self._try_value_pattern(element)
            if text:
                print(f"DEBUG: Got text from ValuePattern: '{text}'")
                return text
                
        except Exception as e:
            print(f"ERROR in get_selected_text: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _try_text_pattern(self, element) -> Optional[str]:
        """Try to get text using TextPattern."""
        try:
            text_pattern = element.GetCurrentPattern(UIA.UIA_TextPatternId)
            if text_pattern:
                text_pattern = text_pattern.QueryInterface(UIA.IUIAutomationTextPattern)
                selection = text_pattern.GetSelection()
                
                print(f"DEBUG: TextPattern - selection length: {selection.Length if selection else 'None'}")
                
                if selection and selection.Length > 0:
                    range_obj = selection.GetElement(0)
                    text = range_obj.GetText(-1)
                    
                    if text and text.strip():
                        return text.strip()
        except Exception as e:
            print(f"DEBUG: TextPattern failed: {e}")
        return None
    
    def _try_text_pattern2(self, element) -> Optional[str]:
        """Try to get text using TextPattern2 (newer API)."""
        try:
            pattern = element.GetCurrentPattern(UIA.UIA_TextPattern2Id)
            if pattern:
                pattern = pattern.QueryInterface(UIA.IUIAutomationTextPattern2)
                selection = pattern.GetSelection()
                
                print(f"DEBUG: TextPattern2 - selection length: {selection.Length if selection else 'None'}")
                
                if selection and selection.Length > 0:
                    range_obj = selection.GetElement(0)
                    text = range_obj.GetText(-1)
                    
                    if text and text.strip():
                        return text.strip()
        except Exception as e:
            print(f"DEBUG: TextPattern2 failed: {e}")
        return None
    
    def _try_value_pattern(self, element) -> Optional[str]:
        """Try to get text using ValuePattern (fallback for some controls)."""
        try:
            value_pattern = element.GetCurrentPattern(UIA.UIA_ValuePatternId)
            if value_pattern:
                value_pattern = value_pattern.QueryInterface(UIA.IUIAutomationValuePattern)
                text = value_pattern.CurrentValue
                
                print(f"DEBUG: ValuePattern returned: '{text}'")
                
                if text and text.strip():
                    return text.strip()
        except Exception as e:
            print(f"DEBUG: ValuePattern failed: {e}")
        return None