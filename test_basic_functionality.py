#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Basic Functionality Test Script for Offset Curve Deformer System

This script tests the basic functionality without requiring Maya.
It simulates the Maya environment and tests the wrapper classes.
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def test_imports():
    """Test if modules can be imported"""
    print("=" * 60)
    print(" IMPORT TEST")
    print("=" * 60)
    
    try:
        # Test inputCurveOptimizer import
        print("Testing inputCurveOptimizer import...")
        from inputCurveOptimizer.curve_optimizer import InputCurveOptimizerWrapper
        print("✅ InputCurveOptimizerWrapper imported successfully")
        
        # Test offsetCurveDeformer import
        print("Testing offsetCurveDeformer import...")
        from offsetCurveDeformer.offset_generator import OffsetCurveDeformerWrapper
        print("✅ OffsetCurveDeformerWrapper imported successfully")
        
        return True
        
    except ImportError as e:
        print("❌ Import failed: %s" % e)
        return False
    except Exception as e:
        print("❌ Unexpected error: %s" % e)
        return False

def test_class_creation():
    """Test if wrapper classes can be instantiated"""
    print("\n" + "=" * 60)
    print(" CLASS INSTANTIATION TEST")
    print("=" * 60)
    
    try:
        # Test InputCurveOptimizerWrapper
        print("Testing InputCurveOptimizerWrapper instantiation...")
        from inputCurveOptimizer.curve_optimizer import InputCurveOptimizerWrapper
        
        # Mock Maya environment
        class MockMayaCmds:
            @staticmethod
            def pluginInfo(plugin_name, query=True, loaded=True):
                return False
            @staticmethod
            def loadPlugin(plugin_name):
                return True
        
        # Replace maya.cmds with mock
        import inputCurveOptimizer.curve_optimizer
        inputCurveOptimizer.curve_optimizer.cmds = MockMayaCmds()
        
        optimizer = InputCurveOptimizerWrapper()
        print("✅ InputCurveOptimizerWrapper created successfully")
        
        # Test basic methods
        print("Testing basic methods...")
        status = optimizer.get_workflow_status()
        print("✅ Workflow status retrieved: %s" % status)
        
        return True
        
    except Exception as e:
        print("❌ Class instantiation failed: %s" % e)
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n" + "=" * 60)
    print(" FILE STRUCTURE TEST")
    print("=" * 60)
    
    required_files = [
        "src/inputCurveOptimizer/__init__.py",
        "src/inputCurveOptimizer/curve_optimizer.py",
        "src/offsetCurveDeformer/__init__.py",
        "src/offsetCurveDeformer/offset_generator.py",
        "maya_test_script.py",
        "maya_gui_test.py",
        "test_integrated_workflow.py",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print("✅ %s" % file_path)
        else:
            print("❌ %s (missing)" % file_path)
            missing_files.append(file_path)
    
    if missing_files:
        print("\n⚠️ Missing files: %s" % missing_files)
        return False
    else:
        print("\n✅ All required files present")
        return True

def test_python_compatibility():
    """Test Python 2.7 compatibility"""
    print("\n" + "=" * 60)
    print(" PYTHON COMPATIBILITY TEST")
    print("=" * 60)
    
    print("Python version: %s" % sys.version)
    print("Python executable: %s" % sys.executable)
    
    # Test basic syntax
    try:
        # Test string formatting
        test_string = "Test %s" % "string"
        print("✅ String formatting: %s" % test_string)
        
        # Test class inheritance
        class TestClass(object):
            pass
        print("✅ Class inheritance: %s" % TestClass)
        
        # Test list comprehension
        test_list = [i for i in range(3)]
        print("✅ List comprehension: %s" % test_list)
        
        return True
        
    except Exception as e:
        print("❌ Python compatibility test failed: %s" % e)
        return False

def main():
    """Main test function"""
    print("OFFSET CURVE DEFORMER SYSTEM - BASIC FUNCTIONALITY TEST")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Python Compatibility", test_python_compatibility),
        ("Module Imports", test_imports),
        ("Class Instantiation", test_class_creation)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print("\nRunning %s test..." % test_name)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print("❌ Test failed with exception: %s" % e)
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print(" TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print("%s: %s" % (test_name, status))
        if result:
            passed += 1
    
    print("\nResults: %d/%d tests passed" % (passed, total))
    
    if passed == total:
        print("All tests passed! The system is ready for Maya testing.")
        print("\nNext steps:")
        print("1. Open Maya")
        print("2. Load the required plugins")
        print("3. Run maya_test_script.py in Maya's Script Editor")
    else:
        print("Some tests failed. Please check the errors above.")
        print("\nThe system may not be ready for Maya testing yet.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
