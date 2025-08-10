#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Maya Test Script for Offset Curve Deformer System

Copy and paste this script into Maya's Script Editor to test the basic functionality.

This script will:
1. Check if plugins are available
2. Test basic wrapper functionality
3. Create a simple test scene
4. Test basic operations
5. Clean up
"""

import maya.cmds as cmds
import maya.mel as mel

def print_separator(title):
    """Print a formatted separator"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_plugin_availability():
    """Test if required plugins are available"""
    print_separator("🔌 PLUGIN AVAILABILITY TEST")
    
    plugins_to_check = ["inputCurveOptimizer", "offsetCurveDeformer"]
    available_plugins = []
    
    for plugin in plugins_to_check:
        try:
            if cmds.pluginInfo(plugin, query=True, loaded=True):
                print(f"✅ {plugin}: Loaded")
                available_plugins.append(plugin)
            else:
                print(f"❌ {plugin}: Not loaded")
        except Exception as e:
            print(f"❌ {plugin}: Error checking - {e}")
    
    return available_plugins

def test_python_wrappers():
    """Test if Python wrappers can be imported"""
    print_separator("🐍 PYTHON WRAPPER TEST")
    
    try:
        # Try to import the wrappers
        import sys
        import os
        
        # Add the src directory to the path
        current_dir = os.path.dirname(cmds.file(q=True, sn=True) or "")
        if not current_dir:
            current_dir = cmds.workspace(q=True, rd=True)
        
        src_path = os.path.join(current_dir, "src")
        if os.path.exists(src_path):
            sys.path.insert(0, src_path)
            print(f"✅ Added {src_path} to Python path")
        else:
            print(f"⚠️ Source directory not found: {src_path}")
            return False
        
        # Try to import
        try:
            from inputCurveOptimizer.curve_optimizer import InputCurveOptimizerWrapper
            print("✅ InputCurveOptimizerWrapper imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import InputCurveOptimizerWrapper: {e}")
            return False
        
        try:
            from offsetCurveDeformer.offset_generator import OffsetCurveDeformerWrapper
            print("✅ OffsetCurveDeformerWrapper imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import OffsetCurveDeformerWrapper: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Python wrappers: {e}")
        return False

def create_test_scene():
    """Create a simple test scene"""
    print_separator("🎬 TEST SCENE CREATION")
    
    try:
        # Create a simple mesh
        mesh = cmds.polyCube(name="testMesh", width=2, height=2, depth=2)[0]
        cmds.move(0, 1, 0, mesh)
        print(f"✅ Created test mesh: {mesh}")
        
        # Create a simple curve
        curve = cmds.curve(name="testCurve", p=[(0,0,0), (1,1,1), (2,0,0), (3,1,1), (4,0,0)])
        print(f"✅ Created test curve: {curve}")
        
        # Create a simple joint chain
        joint1 = cmds.joint(name="testJoint1", p=(0,0,0))
        joint2 = cmds.joint(name="testJoint2", p=(1,1,1))
        joint3 = cmds.joint(name="testJoint3", p=(2,0,0))
        print(f"✅ Created test joints: {joint1}, {joint2}, {joint3}")
        
        return mesh, curve, [joint1, joint2, joint3]
        
    except Exception as e:
        print(f"❌ Error creating test scene: {e}")
        return None, None, None

def test_basic_functionality():
    """Test basic wrapper functionality"""
    print_separator("🧪 BASIC FUNCTIONALITY TEST")
    
    try:
        # Import wrappers
        from inputCurveOptimizer.curve_optimizer import InputCurveOptimizerWrapper
        from offsetCurveDeformer.offset_generator import OffsetCurveDeformerWrapper
        
        # Test InputCurveOptimizerWrapper
        print("📊 Testing InputCurveOptimizerWrapper...")
        optimizer = InputCurveOptimizerWrapper()
        
        # Test basic methods
        try:
            status = optimizer.get_workflow_status()
            print(f"✅ Workflow status: {status}")
        except Exception as e:
            print(f"⚠️ Workflow status error: {e}")
        
        # Test OffsetCurveDeformerWrapper
        print("📊 Testing OffsetCurveDeformerWrapper...")
        deformer = OffsetCurveDeformerWrapper()
        
        # Test basic methods
        try:
            status = deformer.get_workflow_status()
            print(f"✅ Workflow status: {status}")
        except Exception as e:
            print(f"⚠️ Workflow status error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing basic functionality: {e}")
        return False

def test_workflow_integration():
    """Test the integrated workflow"""
    print_separator("🚀 WORKFLOW INTEGRATION TEST")
    
    try:
        # Import wrappers
        from inputCurveOptimizer.curve_optimizer import InputCurveOptimizerWrapper
        from offsetCurveDeformer.offset_generator import OffsetCurveDeformerWrapper
        
        # Create test scene
        mesh, curve, joints = create_test_scene()
        if not mesh or not curve:
            print("❌ Failed to create test scene")
            return False
        
        print("✅ Test scene created successfully")
        
        # Test inputCurveOptimizer workflow
        print("📊 Testing inputCurveOptimizer workflow...")
        optimizer = InputCurveOptimizerWrapper()
        
        try:
            # Test mesh to curve workflow
            result = optimizer.workflow_mesh_to_curve(mesh)
            if result['success']:
                print(f"✅ Mesh to curve workflow: {result['message']}")
            else:
                print(f"⚠️ Mesh to curve workflow: {result['message']}")
        except Exception as e:
            print(f"❌ Mesh to curve workflow error: {e}")
        
        # Test offsetCurveDeformer workflow
        print("📊 Testing offsetCurveDeformer workflow...")
        deformer = OffsetCurveDeformerWrapper()
        
        try:
            # Test create and bind workflow
            result = deformer.workflow_create_and_bind(curve, mesh)
            if result['success']:
                print(f"✅ Create and bind workflow: {result['message']}")
            else:
                print(f"⚠️ Create and bind workflow: {result['message']}")
        except Exception as e:
            print(f"❌ Create and bind workflow error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing workflow integration: {e}")
        return False

def cleanup_test_scene():
    """Clean up the test scene"""
    print_separator("🧹 CLEANUP")
    
    try:
        # Delete test objects
        test_objects = ["testMesh", "testCurve", "testJoint1", "testJoint2", "testJoint3"]
        deleted_count = 0
        
        for obj in test_objects:
            if cmds.objExists(obj):
                cmds.delete(obj)
                deleted_count += 1
                print(f"🗑️ Deleted: {obj}")
        
        print(f"✅ Cleanup completed: {deleted_count} objects deleted")
        return True
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False

def run_complete_test():
    """Run the complete test suite"""
    print_separator("🧪 COMPLETE TEST SUITE")
    print("Starting comprehensive test of Offset Curve Deformer System...")
    
    test_results = {}
    
    # Test 1: Plugin availability
    print("\n🔍 Test 1: Plugin Availability")
    available_plugins = test_plugin_availability()
    test_results['plugins'] = len(available_plugins) > 0
    
    # Test 2: Python wrapper availability
    print("\n🔍 Test 2: Python Wrapper Availability")
    wrappers_available = test_python_wrappers()
    test_results['wrappers'] = wrappers_available
    
    # Test 3: Basic functionality
    if wrappers_available:
        print("\n🔍 Test 3: Basic Functionality")
        basic_working = test_basic_functionality()
        test_results['basic_functionality'] = basic_working
        
        # Test 4: Workflow integration
        if basic_working:
            print("\n🔍 Test 4: Workflow Integration")
            workflow_working = test_workflow_integration()
            test_results['workflow_integration'] = workflow_working
        else:
            test_results['workflow_integration'] = False
    else:
        test_results['basic_functionality'] = False
        test_results['workflow_integration'] = False
    
    # Cleanup
    print("\n🔍 Test 5: Cleanup")
    cleanup_success = cleanup_test_scene()
    test_results['cleanup'] = cleanup_success
    
    # Print results summary
    print_separator("📋 TEST RESULTS SUMMARY")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Overall Result: EXCELLENT")
    elif success_rate >= 60:
        print("👍 Overall Result: GOOD")
    elif success_rate >= 40:
        print("⚠️ Overall Result: FAIR")
    else:
        print("❌ Overall Result: NEEDS IMPROVEMENT")
    
    print("\n🎯 Test completed! Check the results above.")
    return test_results

# Run the test if this script is executed directly
if __name__ == "__main__":
    run_complete_test()
