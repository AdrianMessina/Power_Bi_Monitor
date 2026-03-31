"""
Script de prueba para verificar que todos los imports funcionan
"""
import sys
from pathlib import Path

print("=" * 60)
print("TESTING MODULE IMPORTS")
print("=" * 60)

# Test 1: Documentation Generator
print("\n1. Testing Documentation Generator...")
sys.path.clear()
sys.path.append(str(Path.cwd()))
docgen_core_path = Path("apps_core/docgen_core")
sys.path.insert(0, str(docgen_core_path))
try:
    from core.parsers import create_parser, FormatDetector, PowerBIFormat
    print("   ✅ Documentation Generator imports OK")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 2: DAX Optimizer
print("\n2. Testing DAX Optimizer...")
sys.path.clear()
sys.path.append(str(Path.cwd()))
dax_core_path = Path("apps_core/dax_core")
sys.path.insert(0, str(dax_core_path))
try:
    from core import extract_measures_from_pbip
    print("   ✅ DAX Optimizer imports OK")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 3: Power BI Analyzer
print("\n3. Testing Power BI Analyzer...")
sys.path.clear()
sys.path.append(str(Path.cwd()))
analyzer_core_path = Path("apps_core/analyzer_core")
sys.path.insert(0, str(analyzer_core_path))
try:
    from core import analyze_powerbi_file
    print("   ✅ Power BI Analyzer imports OK")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# Test 4: BI Bot
print("\n4. Testing BI Bot...")
sys.path.clear()
sys.path.append(str(Path.cwd()))
bot_core_path = Path("apps_core/bot_core")
sys.path.insert(0, str(bot_core_path))
try:
    from core.xmla_connector import XMLAConnector
    print("   ✅ BI Bot imports OK")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
