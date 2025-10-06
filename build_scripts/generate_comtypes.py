"""
Generate comtypes type libraries before building with PyInstaller.
This ensures the UIAutomation COM types are available in the compiled exe.
"""

import sys
import os

print("=" * 60)
print("Generating comtypes type libraries...")
print("=" * 60)

# Import comtypes
try:
    import comtypes.client
    print("✓ comtypes imported successfully")
except ImportError as e:
    print(f"✗ Failed to import comtypes: {e}")
    print("  Run: pip install comtypes")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Show cache location
try:
    import comtypes.gen
    cache_dir = os.path.dirname(comtypes.gen.__file__)
    print(f"✓ comtypes cache location: {cache_dir}")
except Exception as e:
    print(f"✗ Could not find comtypes cache: {e}")

# Force generation of UIAutomation type library
print("\nGenerating UIAutomation type libraries...")
try:
    module = comtypes.client.GetModule('UIAutomationCore.dll')
    print("✓ UIAutomationCore type library generated")
    print(f"  Module: {module}")
except Exception as e:
    print(f"✗ Failed to generate UIAutomationCore: {e}")

# Verify the UIAutomationClient was created
try:
    import comtypes.gen.UIAutomationClient as UIA
    print("✓ UIAutomationClient module can be imported")
    print(f"  Has IUIAutomation: {hasattr(UIA, 'IUIAutomation')}")
except ImportError as e:
    print(f"✗ Failed to import UIAutomationClient: {e}")

# Try to create the actual COM object
print("\nTesting COM object creation...")
try:
    uia = comtypes.client.CreateObject(
        "{ff48dba4-60ef-4201-aa87-54103eef594e}",
        interface=comtypes.client.GetModule('UIAutomationCore.dll').IUIAutomation
    )
    print("✓ UIAutomation COM object created successfully")
except Exception as e:
    print(f"✗ Failed to create UIAutomation object: {e}")

print("\n" + "=" * 60)
print("Generation complete!")
print("=" * 60)
print("\nThe generated files are in your comtypes cache.")
print("You can now build with PyInstaller.")
print("\nPress Enter to exit...")
input()