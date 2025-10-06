"""
Generate comtypes type libraries before building with PyInstaller.
This ensures the UIAutomation COM types are available in the compiled exe.
"""

import comtypes.client

print("Generating comtypes type libraries...")
print("This may take a moment...")

# Force generation of UIAutomation type library
try:
    comtypes.client.GetModule('UIAutomationCore.dll')
    print("✓ UIAutomationCore type library generated")
except Exception as e:
    print(f"✗ Failed to generate UIAutomationCore: {e}")

# Also try the CLSID directly
try:
    uia = comtypes.client.CreateObject(
        "{ff48dba4-60ef-4201-aa87-54103eef594e}",
        interface=comtypes.client.GetModule('UIAutomationCore.dll').IUIAutomation
    )
    print("✓ UIAutomation COM object created successfully")
except Exception as e:
    print(f"✗ Failed to create UIAutomation object: {e}")

print("\nDone! You can now build with PyInstaller.")
print("The generated files are in your comtypes cache.")
input("\nPress Enter to exit...")