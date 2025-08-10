#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integrated Workflow Test Script for Offset Curve Deformer System

This script tests the complete workflow from inputCurveOptimizer to offsetCurveDeformer
using the Python wrapper classes.

Usage:
    In Maya Script Editor:
        exec(open("path/to/test_integrated_workflow.py").read())
    
    Or as a module:
        from test_integrated_workflow import IntegratedWorkflowTester
        tester = IntegratedWorkflowTester()
        tester.run_all_tests()
"""

import sys
import logging
from typing import Dict, List, Optional, Tuple

# Maya imports
try:
    import maya.cmds as cmds
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False
    print("❌ Maya environment not available")

# Local imports
try:
    from src.inputCurveOptimizer.curve_optimizer import InputCurveOptimizerWrapper
    from src.offsetCurveDeformer.offset_generator import OffsetCurveDeformerWrapper
    WRAPPERS_AVAILABLE = True
except ImportError as e:
    WRAPPERS_AVAILABLE = False
    print(f"❌ Python wrappers not available: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegratedWorkflowTester:
    """Test the integrated workflow of inputCurveOptimizer and offsetCurveDeformer"""
    
    def __init__(self):
        self.test_results = {}
        self.scene_objects = {
            'curves': [],
            'meshes': [],
            'joints': []
        }
        
        if not MAYA_AVAILABLE:
            logger.error("Maya environment not available")
            return
            
        if not WRAPPERS_AVAILABLE:
            logger.error("Python wrappers not available")
            return
            
        logger.info("✅ IntegratedWorkflowTester initialized successfully")
    
    def check_plugin_availability(self) -> Dict[str, bool]:
        """Check if required plugins are available"""
        results = {}
        
        try:
            # Check inputCurveOptimizer plugin
            if cmds.pluginInfo("inputCurveOptimizer", query=True, loaded=True):
                results['inputCurveOptimizer'] = True
                logger.info("✅ inputCurveOptimizer plugin is loaded")
            else:
                results['inputCurveOptimizer'] = False
                logger.warning("⚠️ inputCurveOptimizer plugin is not loaded")
                
            # Check offsetCurveDeformer plugin
            if cmds.pluginInfo("offsetCurveDeformer", query=True, loaded=True):
                results['offsetCurveDeformer'] = True
                logger.info("✅ offsetCurveDeformer plugin is loaded")
            else:
                results['offsetCurveDeformer'] = False
                logger.warning("⚠️ offsetCurveDeformer plugin is not loaded")
                
        except Exception as e:
            logger.error(f"Error checking plugin availability: {e}")
            results['error'] = str(e)
            
        return results
    
    def create_test_scene(self) -> bool:
        """Create a simple test scene with basic geometry"""
        try:
            logger.info("Creating test scene...")
            
            # Create a simple mesh
            mesh = cmds.polyCube(name="testMesh", width=2, height=2, depth=2)[0]
            self.scene_objects['meshes'].append(mesh)
            
            # Create a simple curve
            curve = cmds.curve(name="testCurve", p=[(0,0,0), (1,1,1), (2,0,0), (3,1,1), (4,0,0)])
            self.scene_objects['curves'].append(curve)
            
            # Create a simple joint chain
            joint1 = cmds.joint(name="testJoint1", p=(0,0,0))
            joint2 = cmds.joint(name="testJoint2", p=(1,1,1))
            joint3 = cmds.joint(name="testJoint3", p=(2,0,0))
            self.scene_objects['joints'].extend([joint1, joint2, joint3])
            
            logger.info(f"✅ Test scene created: {len(self.scene_objects['meshes'])} meshes, "
                       f"{len(self.scene_objects['curves'])} curves, {len(self.scene_objects['joints'])} joints")
            return True
            
        except Exception as e:
            logger.error(f"Error creating test scene: {e}")
            return False
    
    def test_input_curve_optimizer_workflows(self) -> Dict[str, bool]:
        """Test all inputCurveOptimizer workflow methods"""
        results = {}
        
        if not WRAPPERS_AVAILABLE:
            logger.error("Cannot test inputCurveOptimizer: wrappers not available")
            return {'error': 'Wrappers not available'}
        
        try:
            optimizer = InputCurveOptimizerWrapper()
            
            # Test 1: Mesh to curve workflow
            logger.info("Testing mesh to curve workflow...")
            try:
                if self.scene_objects['meshes']:
                    mesh = self.scene_objects['meshes'][0]
                    result = optimizer.workflow_mesh_to_curve(mesh)
                    results['mesh_to_curve'] = result['success']
                    if result['success']:
                        logger.info(f"✅ Mesh to curve workflow: {result['message']}")
                    else:
                        logger.warning(f"⚠️ Mesh to curve workflow: {result['message']}")
                else:
                    results['mesh_to_curve'] = False
                    logger.warning("⚠️ No meshes available for testing")
            except Exception as e:
                results['mesh_to_curve'] = False
                logger.error(f"❌ Mesh to curve workflow error: {e}")
            
            # Test 2: Curve optimization workflow
            logger.info("Testing curve optimization workflow...")
            try:
                if self.scene_objects['curves']:
                    curve = self.scene_objects['curves'][0]
                    result = optimizer.workflow_curve_optimization(curve)
                    results['curve_optimization'] = result['success']
                    if result['success']:
                        logger.info(f"✅ Curve optimization workflow: {result['message']}")
                    else:
                        logger.warning(f"⚠️ Curve optimization workflow: {result['message']}")
                else:
                    results['curve_optimization'] = False
                    logger.warning("⚠️ No curves available for testing")
            except Exception as e:
                results['curve_optimization'] = False
                logger.error(f"❌ Curve optimization workflow error: {e}")
            
            # Test 3: Skeleton to curve workflow
            logger.info("Testing skeleton to curve workflow...")
            try:
                if self.scene_objects['joints']:
                    joints = self.scene_objects['joints']
                    result = optimizer.workflow_skeleton_to_curve(joints)
                    results['skeleton_to_curve'] = result['success']
                    if result['success']:
                        logger.info(f"✅ Skeleton to curve workflow: {result['message']}")
                    else:
                        logger.warning(f"⚠️ Skeleton to curve workflow: {result['message']}")
                else:
                    results['skeleton_to_curve'] = False
                    logger.warning("⚠️ No joints available for testing")
            except Exception as e:
                results['skeleton_to_curve'] = False
                logger.error(f"❌ Skeleton to curve workflow error: {e}")
            
            # Test 4: Batch optimization workflow
            logger.info("Testing batch optimization workflow...")
            try:
                if self.scene_objects['curves']:
                    curves = self.scene_objects['curves']
                    result = optimizer.workflow_batch_optimization(curves)
                    results['batch_optimization'] = result['success']
                    if result['success']:
                        logger.info(f"✅ Batch optimization workflow: {result['message']}")
                    else:
                        logger.warning(f"⚠️ Batch optimization workflow: {result['message']}")
                else:
                    results['batch_optimization'] = False
                    logger.warning("⚠️ No curves available for testing")
            except Exception as e:
                results['batch_optimization'] = False
                logger.error(f"❌ Batch optimization workflow error: {e}")
            
            # Test 5: Get workflow status
            logger.info("Testing workflow status...")
            try:
                status = optimizer.get_workflow_status()
                results['workflow_status'] = True
                logger.info(f"✅ Workflow status: {status}")
            except Exception as e:
                results['workflow_status'] = False
                logger.error(f"❌ Workflow status error: {e}")
            
            # Test 6: Cleanup workflow
            logger.info("Testing workflow cleanup...")
            try:
                result = optimizer.cleanup_workflow()
                results['workflow_cleanup'] = result['success']
                if result['success']:
                    logger.info(f"✅ Workflow cleanup: {result['message']}")
                else:
                    logger.warning(f"⚠️ Workflow cleanup: {result['message']}")
            except Exception as e:
                results['workflow_cleanup'] = False
                logger.error(f"❌ Workflow cleanup error: {e}")
                
        except Exception as e:
            logger.error(f"Error testing inputCurveOptimizer workflows: {e}")
            results['error'] = str(e)
            
        return results
    
    def test_offset_curve_deformer_workflows(self) -> Dict[str, bool]:
        """Test all offsetCurveDeformer workflow methods"""
        results = {}
        
        if not WRAPPERS_AVAILABLE:
            logger.error("Cannot test offsetCurveDeformer: wrappers not available")
            return {'error': 'Wrappers not available'}
        
        try:
            deformer = OffsetCurveDeformerWrapper()
            
            # Test 1: Create and bind workflow
            logger.info("Testing create and bind workflow...")
            try:
                if self.scene_objects['curves'] and self.scene_objects['meshes']:
                    curve = self.scene_objects['curves'][0]
                    mesh = self.scene_objects['meshes'][0]
                    result = deformer.workflow_create_and_bind(curve, mesh)
                    results['create_and_bind'] = result['success']
                    if result['success']:
                        logger.info(f"✅ Create and bind workflow: {result['message']}")
                    else:
                        logger.warning(f"⚠️ Create and bind workflow: {result['message']}")
                else:
                    results['create_and_bind'] = False
                    logger.warning("⚠️ No curves or meshes available for testing")
            except Exception as e:
                results['create_and_bind'] = False
                logger.error(f"❌ Create and bind workflow error: {e}")
            
            # Test 2: Advanced deformation workflow
            logger.info("Testing advanced deformation workflow...")
            try:
                result = deformer.workflow_advanced_deformation()
                results['advanced_deformation'] = result['success']
                if result['success']:
                    logger.info(f"✅ Advanced deformation workflow: {result['message']}")
                else:
                    logger.warning(f"⚠️ Advanced deformation workflow: {result['message']}")
            except Exception as e:
                results['advanced_deformation'] = False
                logger.error(f"❌ Advanced deformation workflow error: {e}")
            
            # Test 3: Pose blending workflow
            logger.info("Testing pose blending workflow...")
            try:
                if self.scene_objects['joints']:
                    target_joint = self.scene_objects['joints'][0]
                    result = deformer.workflow_pose_blending(target_joint, 0.5)
                    results['pose_blending'] = result['success']
                    if result['success']:
                        logger.info(f"✅ Pose blending workflow: {result['message']}")
                    else:
                        logger.warning(f"⚠️ Pose blending workflow: {result['message']}")
                else:
                    results['pose_blending'] = False
                    logger.warning("⚠️ No joints available for testing")
            except Exception as e:
                results['pose_blending'] = False
                logger.error(f"❌ Pose blending workflow error: {e}")
            
            # Test 4: Rebinding workflow
            logger.info("Testing rebinding workflow...")
            try:
                result = deformer.workflow_rebinding()
                results['rebinding'] = result['success']
                if result['success']:
                    logger.info(f"✅ Rebinding workflow: {result['message']}")
                else:
                    logger.warning(f"⚠️ Rebinding workflow: {result['message']}")
            except Exception as e:
                results['rebinding'] = False
                logger.error(f"❌ Rebinding workflow error: {e}")
            
            # Test 5: Debug and optimization workflow
            logger.info("Testing debug and optimization workflow...")
            try:
                result = deformer.workflow_debug_and_optimization()
                results['debug_and_optimization'] = result['success']
                if result['success']:
                    logger.info(f"✅ Debug and optimization workflow: {result['message']}")
                else:
                    logger.warning(f"⚠️ Debug and optimization workflow: {result['message']}")
            except Exception as e:
                results['debug_and_optimization'] = False
                logger.error(f"❌ Debug and optimization workflow error: {e}")
            
            # Test 6: Get workflow status
            logger.info("Testing workflow status...")
            try:
                status = deformer.get_workflow_status()
                results['workflow_status'] = True
                logger.info(f"✅ Workflow status: {status}")
            except Exception as e:
                results['workflow_status'] = False
                logger.error(f"❌ Workflow status error: {e}")
            
            # Test 7: Cleanup workflow
            logger.info("Testing workflow cleanup...")
            try:
                result = deformer.cleanup_workflow()
                results['workflow_cleanup'] = result['success']
                if result['success']:
                    logger.info(f"✅ Workflow cleanup: {result['message']}")
                else:
                    logger.warning(f"⚠️ Workflow cleanup: {result['message']}")
            except Exception as e:
                results['workflow_cleanup'] = False
                logger.error(f"❌ Workflow cleanup error: {e}")
                
        except Exception as e:
            logger.error(f"Error testing offsetCurveDeformer workflows: {e}")
            results['error'] = str(e)
            
        return results
    
    def test_integrated_workflow(self) -> Dict[str, bool]:
        """Test the complete integrated workflow"""
        results = {}
        
        logger.info("🚀 Testing complete integrated workflow...")
        
        try:
            # Step 1: Create test scene
            if not self.create_test_scene():
                results['scene_creation'] = False
                logger.error("❌ Failed to create test scene")
                return results
            results['scene_creation'] = True
            
            # Step 2: Test inputCurveOptimizer workflows
            logger.info("📊 Testing inputCurveOptimizer workflows...")
            optimizer_results = self.test_input_curve_optimizer_workflows()
            results['input_curve_optimizer'] = optimizer_results
            
            # Step 3: Test offsetCurveDeformer workflows
            logger.info("📊 Testing offsetCurveDeformer workflows...")
            deformer_results = self.test_offset_curve_deformer_workflows()
            results['offset_curve_deformer'] = deformer_results
            
            # Step 4: Test end-to-end workflow
            logger.info("🔄 Testing end-to-end workflow...")
            try:
                # This would test the complete pipeline
                # For now, we'll just check if both systems are working
                end_to_end_success = (
                    any(optimizer_results.get(k, False) for k in ['mesh_to_curve', 'curve_optimization']) and
                    any(deformer_results.get(k, False) for k in ['create_and_bind', 'advanced_deformation'])
                )
                results['end_to_end_workflow'] = end_to_end_success
                
                if end_to_end_success:
                    logger.info("✅ End-to-end workflow test passed")
                else:
                    logger.warning("⚠️ End-to-end workflow test had issues")
                    
            except Exception as e:
                results['end_to_end_workflow'] = False
                logger.error(f"❌ End-to-end workflow error: {e}")
            
            logger.info("🎯 Integrated workflow test completed")
            
        except Exception as e:
            logger.error(f"Error in integrated workflow test: {e}")
            results['error'] = str(e)
            
        return results
    
    def cleanup_test_scene(self) -> bool:
        """Clean up the test scene"""
        try:
            logger.info("Cleaning up test scene...")
            
            # Delete test objects
            for obj_list in self.scene_objects.values():
                for obj in obj_list:
                    try:
                        if cmds.objExists(obj):
                            cmds.delete(obj)
                    except Exception as e:
                        logger.warning(f"Could not delete {obj}: {e}")
            
            # Clear lists
            for key in self.scene_objects:
                self.scene_objects[key] = []
            
            logger.info("✅ Test scene cleaned up")
            return True
            
        except Exception as e:
            logger.error(f"Error cleaning up test scene: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Dict[str, bool]]:
        """Run all tests and return comprehensive results"""
        logger.info("🧪 Starting comprehensive test suite...")
        
        all_results = {}
        
        # Check plugin availability
        logger.info("🔍 Checking plugin availability...")
        all_results['plugin_availability'] = self.check_plugin_availability()
        
        # Test integrated workflow
        logger.info("🚀 Testing integrated workflow...")
        all_results['integrated_workflow'] = self.test_integrated_workflow()
        
        # Cleanup
        logger.info("🧹 Cleaning up...")
        self.cleanup_test_scene()
        
        logger.info("🎯 All tests completed")
        return all_results
    
    def print_results(self, results: Dict[str, Dict[str, bool]]):
        """Print test results in a formatted way"""
        print("\n" + "="*80)
        print("🧪 INTEGRATED WORKFLOW TEST RESULTS")
        print("="*80)
        
        if not MAYA_AVAILABLE:
            print("❌ Maya environment not available")
            print("   Please run this script in Maya's Script Editor")
            return
            
        if not WRAPPERS_AVAILABLE:
            print("❌ Python wrappers not available")
            print("   Please check the import paths and wrapper availability")
            return
        
        # Plugin availability
        print("\n🔌 PLUGIN AVAILABILITY:")
        if 'plugin_availability' in results:
            plugin_results = results['plugin_availability']
            for plugin, available in plugin_results.items():
                if plugin != 'error':
                    status = "✅ Available" if available else "❌ Not Available"
                    print(f"   {plugin}: {status}")
                else:
                    print(f"   Error: {plugin_results[plugin]}")
        
        # Integrated workflow results
        print("\n🚀 INTEGRATED WORKFLOW RESULTS:")
        if 'integrated_workflow' in results:
            workflow_results = results['integrated_workflow']
            
            # Scene creation
            if 'scene_creation' in workflow_results:
                status = "✅ Success" if workflow_results['scene_creation'] else "❌ Failed"
                print(f"   Scene Creation: {status}")
            
            # InputCurveOptimizer results
            if 'input_curve_optimizer' in workflow_results:
                print("   📊 InputCurveOptimizer:")
                optimizer_results = workflow_results['input_curve_optimizer']
                for test, result in optimizer_results.items():
                    if test != 'error':
                        status = "✅ Pass" if result else "❌ Fail"
                        print(f"     {test}: {status}")
                    else:
                        print(f"     Error: {optimizer_results[test]}")
            
            # OffsetCurveDeformer results
            if 'offset_curve_deformer' in workflow_results:
                print("   📊 OffsetCurveDeformer:")
                deformer_results = workflow_results['offset_curve_deformer']
                for test, result in deformer_results.items():
                    if test != 'error':
                        status = "✅ Pass" if result else "❌ Fail"
                        print(f"     {test}: {status}")
                    else:
                        print(f"     Error: {deformer_results[test]}")
            
            # End-to-end workflow
            if 'end_to_end_workflow' in workflow_results:
                status = "✅ Success" if workflow_results['end_to_end_workflow'] else "❌ Failed"
                print(f"   End-to-End Workflow: {status}")
        
        print("\n" + "="*80)
        print("📋 Test Summary:")
        
        # Calculate success rates
        total_tests = 0
        passed_tests = 0
        
        if 'integrated_workflow' in results:
            workflow_results = results['integrated_workflow']
            
            # Count optimizer tests
            if 'input_curve_optimizer' in workflow_results:
                optimizer_results = workflow_results['input_curve_optimizer']
                for test, result in optimizer_results.items():
                    if test != 'error':
                        total_tests += 1
                        if result:
                            passed_tests += 1
            
            # Count deformer tests
            if 'offset_curve_deformer' in workflow_results:
                deformer_results = workflow_results['offset_curve_deformer']
                for test, result in deformer_results.items():
                    if test != 'error':
                        total_tests += 1
                        if result:
                            passed_tests += 1
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            print(f"   Total Tests: {total_tests}")
            print(f"   Passed: {passed_tests}")
            print(f"   Failed: {total_tests - passed_tests}")
            print(f"   Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print("   🎉 Overall Result: EXCELLENT")
            elif success_rate >= 60:
                print("   👍 Overall Result: GOOD")
            elif success_rate >= 40:
                print("   ⚠️ Overall Result: FAIR")
            else:
                print("   ❌ Overall Result: NEEDS IMPROVEMENT")
        else:
            print("   No tests were executed")
        
        print("="*80)


def main():
    """Main function to run the test suite"""
    print("🧪 Integrated Workflow Test Suite")
    print("="*50)
    
    if not MAYA_AVAILABLE:
        print("❌ This script must be run in Maya's Script Editor")
        print("   Please copy and paste the contents into Maya's Script Editor")
        return
    
    if not WRAPPERS_AVAILABLE:
        print("❌ Python wrappers are not available")
        print("   Please check the import paths and ensure wrappers are properly installed")
        return
    
    # Create tester and run tests
    tester = IntegratedWorkflowTester()
    results = tester.run_all_tests()
    
    # Print results
    tester.print_results(results)
    
    print("\n🎯 Test completed! Check the results above.")
    print("   For detailed logs, check the Maya Script Editor output.")


if __name__ == "__main__":
    main()
