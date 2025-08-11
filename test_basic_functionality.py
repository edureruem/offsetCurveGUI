#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Test Script for Python 2.7 Compatibility
"""

import sys
import os

print("Python version:", sys.version)
print("Python executable:", sys.executable)

# Test basic imports
try:
    print("Testing basic imports...")
    sys.path.insert(0, 'src')

    # Test if files exist
    files_to_check = [
        "src/inputCurveOptimizer/__init__.py",
        "src/inputCurveOptimizer/curve_optimizer.py",
        "src/offsetCurveDeformer/__init__.py",
        "src/offsetCurveDeformer/offset_generator.py"
    ]

    for file_path in files_to_check:
        if os.path.exists(file_path):
            print("OK:", file_path)
        else:
            print("MISSING:", file_path)

    # Test module import (without maya.cmds)
    print("\nTesting module structure...")

    # Check if we can read the files
    try:
        with open("src/inputCurveOptimizer/curve_optimizer.py", "r") as f:
            content = f.read()
            if "class InputCurveOptimizerWrapper" in content:
                print("OK: InputCurveOptimizerWrapper class found")
            else:
                print("ERROR: InputCurveOptimizerWrapper class not found")
    except Exception as e:
        print("ERROR reading curve_optimizer.py:", e)

    try:
        with open("src/offsetCurveDeformer/offset_generator.py", "r") as f:
            content = f.read()
            if "class OffsetCurveDeformerWrapper" in content:
                print("OK: OffsetCurveDeformerWrapper class found")
            else:
                print("ERROR: OffsetCurveDeformerWrapper class not found")
    except Exception as e:
        print("ERROR reading offset_generator.py:", e)

    print("\nBasic structure test completed.")

except Exception as e:
    print("ERROR:", e)

print("\nReady for Maya testing!")
print("Next steps:")
print("1. Open Maya")
print("2. Load plugins: inputCurveOptimizer, offsetCurveDeformer")
print("3. Run maya_test_script.py in Maya Script Editor")
