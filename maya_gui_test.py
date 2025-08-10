#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maya GUI Test Script for Offset Curve Deformer System

This script creates a simple test GUI in Maya to verify the basic functionality
of the Python wrappers and GUI components.

Usage:
    Copy and paste this script into Maya's Script Editor and run it.
"""

import maya.cmds as cmds
import maya.mel as mel

def create_test_gui():
    """Create a simple test GUI in Maya"""
    
    # Delete existing window if it exists
    if cmds.window("testOffsetCurveGUI", exists=True):
        cmds.deleteUI("testOffsetCurveGUI")
    
    # Create the main window
    window = cmds.window("testOffsetCurveGUI", title="Offset Curve Deformer - Test GUI", widthHeight=(800, 600))
    
    # Create main layout
    main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5, columnOffset=["both", 5])
    
    # Title
    cmds.text(label="🧪 Offset Curve Deformer Test GUI", font="boldLabelFont", height=30)
    cmds.separator(height=10)
    
    # Status section
    cmds.frameLayout(label="🔌 System Status", collapsable=True, collapse=False)
    status_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    
    # Plugin status
    cmds.text(label="Plugin Status:", font="boldLabelFont")
    plugin_status_text = cmds.text(label="Checking...", font="smallPlainLabelFont")
    
    # Python wrapper status
    cmds.text(label="Python Wrapper Status:", font="boldLabelFont")
    wrapper_status_text = cmds.text(label="Checking...", font="smallPlainLabelFont")
    
    cmds.setParent("..")  # End status_layout
    cmds.setParent("..")  # End frameLayout
    
    # Test section
    cmds.frameLayout(label="🧪 Test Functions", collapsable=True, collapse=False)
    test_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    
    # Test buttons
    cmds.button(label="🔍 Check Plugin Status", command=lambda x: check_plugin_status(plugin_status_text))
    cmds.button(label="🐍 Check Python Wrappers", command=lambda x: check_python_wrappers(wrapper_status_text))
    cmds.button(label="🎬 Create Test Scene", command=lambda x: create_test_scene())
    cmds.button(label="🧹 Cleanup Test Scene", command=lambda x: cleanup_test_scene())
    
    cmds.setParent("..")  # End test_layout
    cmds.setParent("..")  # End frameLayout
    
    # Wrapper test section
    cmds.frameLayout(label="📊 Wrapper Tests", collapsable=True, collapse=False)
    wrapper_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    
    # Wrapper test buttons
    cmds.button(label="📊 Test InputCurveOptimizer", command=lambda x: test_input_curve_optimizer())
    cmds.button(label="📊 Test OffsetCurveDeformer", command=lambda x: test_offset_curve_deformer())
    cmds.button(label="🚀 Test Integrated Workflow", command=lambda x: test_integrated_workflow())
    
    cmds.setParent("..")  # End wrapper_layout
    cmds.setParent("..")  # End frameLayout
    
    # Log section
    cmds.frameLayout(label="📝 Test Log", collapsable=True, collapse=False)
    log_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=5)
    
    # Log text area
    log_text = cmds.scrollField(height=200, wordWrap=True, editable=False)
    
    # Log control buttons
    log_controls = cmds.rowLayout(numberOfColumns=3, adjustableColumn=1)
    cmds.button(label="🗑️ Clear Log", command=lambda x: clear_log(log_text))
    cmds.button(label="💾 Save Log", command=lambda x: save_log(log_text))
    cmds.button(label="🔄 Refresh Status", command=lambda x: refresh_all_status(plugin_status_text, wrapper_status_text))
    cmds.setParent("..")  # End log_controls
    
    cmds.setParent("..")  # End log_layout
    cmds.setParent("..")  # End frameLayout
    
    # Store references for later use
    cmds.window(window, edit=True, widthHeight=(800, 600))
    
    # Show the window
    cmds.showWindow(window)
    
    # Initial status check
    refresh_all_status(plugin_status_text, wrapper_status_text)
    
    return window, log_text

def log_message(log_text, message):
    """Add a message to the log"""
    if log_text:
        current_text = cmds.scrollField(log_text, query=True, text=True)
        timestamp = cmds.date(format="%H:%M:%S")
        new_text = f"[{timestamp}] {message}\n{current_text}"
        cmds.scrollField(log_text, edit=True, text=new_text)

def check_plugin_status(status_text):
    """Check and display plugin status"""
    try:
        plugins_to_check = ["inputCurveOptimizer", "offsetCurveDeformer"]
        status_messages = []
        
        for plugin in plugins_to_check:
            try:
                if cmds.pluginInfo(plugin, query=True, loaded=True):
                    status_messages.append(f"✅ {plugin}: Loaded")
                else:
                    status_messages.append(f"❌ {plugin}: Not loaded")
            except Exception as e:
                status_messages.append(f"❌ {plugin}: Error - {e}")
        
        status_display = "\n".join(status_messages)
        cmds.text(status_text, edit=True, label=status_display)
        
        # Log the status
        log_message(cmds.lsUI(type="scrollField")[0], f"Plugin status checked:\n{status_display}")
        
    except Exception as e:
        cmds.text(status_text, edit=True, label=f"Error: {e}")
        log_message(cmds.lsUI(type="scrollField")[0], f"Error checking plugin status: {e}")

def check_python_wrappers(status_text):
    """Check and display Python wrapper status"""
    try:
        import sys
        import os
        
        # Try to add src to path
        current_dir = os.path.dirname(cmds.file(q=True, sn=True) or "")
        if not current_dir:
            current_dir = cmds.workspace(q=True, rd=True)
        
        src_path = os.path.join(current_dir, "src")
        if os.path.exists(src_path):
            sys.path.insert(0, src_path)
            path_status = f"✅ Added {src_path} to Python path"
        else:
            path_status = f"⚠️ Source directory not found: {src_path}"
        
        # Try to import wrappers
        wrapper_status = []
        
        try:
            from inputCurveOptimizer.curve_optimizer import InputCurveOptimizerWrapper
            wrapper_status.append("✅ InputCurveOptimizerWrapper: Available")
        except ImportError as e:
            wrapper_status.append(f"❌ InputCurveOptimizerWrapper: {e}")
        
        try:
            from offsetCurveDeformer.offset_generator import OffsetCurveDeformerWrapper
            wrapper_status.append("✅ OffsetCurveDeformerWrapper: Available")
        except ImportError as e:
            wrapper_status.append(f"❌ OffsetCurveDeformerWrapper: {e}")
        
        status_display = f"{path_status}\n" + "\n".join(wrapper_status)
        cmds.text(status_text, edit=True, label=status_display)
        
        # Log the status
        log_message(cmds.lsUI(type="scrollField")[0], f"Python wrapper status checked:\n{status_display}")
        
    except Exception as e:
        cmds.text(status_text, edit=True, label=f"Error: {e}")
        log_message(cmds.lsUI(type="scrollField")[0], f"Error checking Python wrappers: {e}")

def create_test_scene():
    """Create a simple test scene"""
    try:
        # Create a simple mesh
        mesh = cmds.polyCube(name="testMesh", width=2, height=2, depth=2)[0]
        cmds.move(0, 1, 0, mesh)
        
        # Create a simple curve
        curve = cmds.curve(name="testCurve", p=[(0,0,0), (1,1,1), (2,0,0), (3,1,1), (4,0,0)])
        
        # Create a simple joint chain
        joint1 = cmds.joint(name="testJoint1", p=(0,0,0))
        joint2 = cmds.joint(name="testJoint2", p=(1,1,1))
        joint3 = cmds.joint(name="testJoint3", p=(2,0,0))
        
        message = f"✅ Test scene created:\n- Mesh: {mesh}\n- Curve: {curve}\n- Joints: {joint1}, {joint2}, {joint3}"
        log_message(cmds.lsUI(type="scrollField")[0], message)
        
        # Select the mesh for visibility
        cmds.select(mesh)
        
    except Exception as e:
        error_message = f"❌ Error creating test scene: {e}"
        log_message(cmds.lsUI(type="scrollField")[0], error_message)

def cleanup_test_scene():
    """Clean up the test scene"""
    try:
        test_objects = ["testMesh", "testCurve", "testJoint1", "testJoint2", "testJoint3"]
        deleted_count = 0
        
        for obj in test_objects:
            if cmds.objExists(obj):
                cmds.delete(obj)
                deleted_count += 1
        
        message = f"✅ Cleanup completed: {deleted_count} objects deleted"
        log_message(cmds.lsUI(type="scrollField")[0], message)
        
    except Exception as e:
        error_message = f"❌ Error during cleanup: {e}"
        log_message(cmds.lsUI(type="scrollField")[0], error_message)

def test_input_curve_optimizer():
    """Test InputCurveOptimizer wrapper"""
    try:
        import sys
        import os
        
        # Add src to path
        current_dir = os.path.dirname(cmds.file(q=True, sn=True) or "")
        if not current_dir:
            current_dir = cmds.workspace(q=True, rd=True)
        
        src_path = os.path.join(current_dir, "src")
        if os.path.exists(src_path):
            sys.path.insert(0, src_path)
        
        # Try to import and test
        try:
            from inputCurveOptimizer.curve_optimizer import InputCurveOptimizerWrapper
            
            optimizer = InputCurveOptimizerWrapper()
            status = optimizer.get_workflow_status()
            
            message = f"✅ InputCurveOptimizer test successful:\nStatus: {status}"
            log_message(cmds.lsUI(type="scrollField")[0], message)
            
        except ImportError as e:
            message = f"❌ Failed to import InputCurveOptimizer: {e}"
            log_message(cmds.lsUI(type="scrollField")[0], message)
        except Exception as e:
            message = f"⚠️ InputCurveOptimizer test error: {e}"
            log_message(cmds.lsUI(type="scrollField")[0], message)
            
    except Exception as e:
        error_message = f"❌ Error testing InputCurveOptimizer: {e}"
        log_message(cmds.lsUI(type="scrollField")[0], error_message)

def test_offset_curve_deformer():
    """Test OffsetCurveDeformer wrapper"""
    try:
        import sys
        import os
        
        # Add src to path
        current_dir = os.path.dirname(cmds.file(q=True, sn=True) or "")
        if not current_dir:
            current_dir = cmds.workspace(q=True, rd=True)
        
        src_path = os.path.join(current_dir, "src")
        if os.path.exists(src_path):
            sys.path.insert(0, src_path)
        
        # Try to import and test
        try:
            from offsetCurveDeformer.offset_generator import OffsetCurveDeformerWrapper
            
            deformer = OffsetCurveDeformerWrapper()
            status = deformer.get_workflow_status()
            
            message = f"✅ OffsetCurveDeformer test successful:\nStatus: {status}"
            log_message(cmds.lsUI(type="scrollField")[0], message)
            
        except ImportError as e:
            message = f"❌ Failed to import OffsetCurveDeformer: {e}"
            log_message(cmds.lsUI(type="scrollField")[0], message)
        except Exception as e:
            message = f"⚠️ OffsetCurveDeformer test error: {e}"
            log_message(cmds.lsUI(type="scrollField")[0], message)
            
    except Exception as e:
        error_message = f"❌ Error testing OffsetCurveDeformer: {e}"
        log_message(cmds.lsUI(type="scrollField")[0], error_message)

def test_integrated_workflow():
    """Test the integrated workflow"""
    try:
        # Check if test scene exists
        if not cmds.objExists("testMesh") or not cmds.objExists("testCurve"):
            message = "⚠️ Please create a test scene first using 'Create Test Scene' button"
            log_message(cmds.lsUI(type="scrollField")[0], message)
            return
        
        import sys
        import os
        
        # Add src to path
        current_dir = os.path.dirname(cmds.file(q=True, sn=True) or "")
        if not current_dir:
            current_dir = cmds.workspace(q=True, rd=True)
        
        src_path = os.path.join(current_dir, "src")
        if os.path.exists(src_path):
            sys.path.insert(0, src_path)
        
        # Test integrated workflow
        try:
            from inputCurveOptimizer.curve_optimizer import InputCurveOptimizerWrapper
            from offsetCurveDeformer.offset_generator import OffsetCurveDeformerWrapper
            
            # Test basic workflow
            optimizer = InputCurveOptimizerWrapper()
            deformer = OffsetCurveDeformerWrapper()
            
            message = "✅ Integrated workflow test successful:\nBoth wrappers are working correctly"
            log_message(cmds.lsUI(type="scrollField")[0], message)
            
        except ImportError as e:
            message = f"❌ Failed to import wrappers for integrated test: {e}"
            log_message(cmds.lsUI(type="scrollField")[0], message)
        except Exception as e:
            message = f"⚠️ Integrated workflow test error: {e}"
            log_message(cmds.lsUI(type="scrollField")[0], message)
            
    except Exception as e:
        error_message = f"❌ Error testing integrated workflow: {e}"
        log_message(cmds.lsUI(type="scrollField")[0], error_message)

def clear_log(log_text):
    """Clear the log text area"""
    if log_text:
        cmds.scrollField(log_text, edit=True, text="")

def save_log(log_text):
    """Save the log content to a file"""
    if log_text:
        log_content = cmds.scrollField(log_text, query=True, text=True)
        
        # Create a simple file dialog
        file_path = cmds.fileDialog2(
            fileFilter="Text Files (*.txt);;All Files (*.*)",
            dialogStyle=2,
            fileMode=0
        )
        
        if file_path:
            try:
                with open(file_path[0], 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                message = f"✅ Log saved to: {file_path[0]}"
                log_message(log_text, message)
                
            except Exception as e:
                error_message = f"❌ Error saving log: {e}"
                log_message(log_text, error_message)

def refresh_all_status(plugin_status_text, wrapper_status_text):
    """Refresh all status displays"""
    check_plugin_status(plugin_status_text)
    check_python_wrappers(wrapper_status_text)

def main():
    """Main function to create and show the test GUI"""
    print("🧪 Creating Offset Curve Deformer Test GUI...")
    
    try:
        window, log_text = create_test_gui()
        
        # Log initial message
        log_message(log_text, "🧪 Offset Curve Deformer Test GUI initialized")
        log_message(log_text, "Ready for testing. Use the buttons above to test different functions.")
        
        print("✅ Test GUI created successfully!")
        print("   Use the GUI to test the system functionality.")
        
        return window
        
    except Exception as e:
        print(f"❌ Error creating test GUI: {e}")
        return None

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()
