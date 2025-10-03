# Selection capture using Windows UI Automation

import comtypes.client
import comtypes.gen.UIAutomationClient as UIA


def copy_selection() -> str:
    """
    Uses Windows UI Automation to read selected text from the focused element.
    No clipboard interaction - preserves clipboard state.
    """
    try:
        # Initialize UI Automation
        uia = comtypes.client.CreateObject("{ff48dba4-60ef-4201-aa87-54103eef594e}", interface=UIA.IUIAutomation)

        # Get focused element
        element = uia.GetFocusedElement()
        if not element:
            return ""

        # Try TextPattern first (most common for rich text controls)
        try:
            text_pattern = element.GetCurrentPattern(UIA.UIA_TextPatternId)
            if text_pattern:
                text_pattern = text_pattern.QueryInterface(UIA.IUIAutomationTextPattern)
                selection = text_pattern.GetSelection()
                if selection and selection.Length > 0:
                    range_obj = selection.GetElement(0)
                    range_obj = range_obj.QueryInterface(UIA.IUIAutomationTextRange)
                    text = range_obj.GetText(-1)
                    if text and text.strip():
                        return text.strip()
        except:
            pass

        # Try TextPattern2 (newer API)
        try:
            text_pattern2 = element.GetCurrentPattern(UIA.UIA_TextPattern2Id)
            if text_pattern2:
                text_pattern2 = text_pattern2.QueryInterface(UIA.IUIAutomationTextPattern2)
                selection = text_pattern2.GetSelection()
                if selection and selection.Length > 0:
                    range_obj = selection.GetElement(0)
                    range_obj = range_obj.QueryInterface(UIA.IUIAutomationTextRange)
                    text = range_obj.GetText(-1)
                    if text and text.strip():
                        return text.strip()
        except:
            pass

        # Try ValuePattern (for simple edit boxes)
        try:
            value_pattern = element.GetCurrentPattern(UIA.UIA_ValuePatternId)
            if value_pattern:
                value_pattern = value_pattern.QueryInterface(UIA.IUIAutomationValuePattern)
                text = value_pattern.CurrentValue
                if text and text.strip():
                    return text.strip()
        except:
            pass

        # Try LegacyIAccessiblePattern (MSAA fallback for old controls)
        try:
            legacy_pattern = element.GetCurrentPattern(UIA.UIA_LegacyIAccessiblePatternId)
            if legacy_pattern:
                legacy_pattern = legacy_pattern.QueryInterface(UIA.IUIAutomationLegacyIAccessiblePattern)
                text = legacy_pattern.CurrentValue
                if text and text.strip():
                    return text.strip()
        except:
            pass

    except Exception as e:
        pass

    return ""
