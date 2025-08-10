#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maya 2020 Compatible PySide2 Main Window
Workflow-based GUI with clear selection steps
"""

import sys
import time
from typing import Dict, Any, List, Tuple, Optional

# Maya environment check
try:
    import maya.cmds as cmds
    import maya.OpenMaya as om
    import maya.mel as mel
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

# Python 래퍼들 import
try:
    from src.inputCurveOptimizer.curve_optimizer import InputCurveOptimizer
    from src.offsetCurveDeformer.offset_generator import OffsetCurveDeformer
    WRAPPERS_AVAILABLE = True
except ImportError:
    WRAPPERS_AVAILABLE = False
    print("Warning: Python wrappers not available")

# PySide2 imports
try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    import sys
    import os
except ImportError:
    print("PySide2 not found.")
    sys.exit(1)

class MayaMainWindow(QMainWindow):
    def __init__(self):
        super(MayaMainWindow, self).__init__()
        self.setWindowTitle("Offset Curve Deformer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Maya 씬 상태
        self.scene_objects = {
            'curves': [],
            'meshes': [],
            'joints': []
        }
        
        # 선택된 오브젝트
        self.selected_curve = None
        self.selected_mesh = None
        
        # 디포머 연결 정보
        self.deformer_connections = {}
        
        # 플러그인 상태 초기화
        self.plugin_status = self.check_plugin_status()
        
        # Python 래퍼들 초기화
        self.init_wrappers()
        
        self.init_ui()
        self.setup_connections()
        self.refresh_scene()
        
        # GUI 로드 후 플러그인 상태 경고 표시
        self.show_plugin_warnings()
    
    def init_wrappers(self):
        """Python 래퍼들 초기화"""
        if WRAPPERS_AVAILABLE and MAYA_AVAILABLE:
            try:
                self.curve_optimizer = InputCurveOptimizer()
                self.offset_deformer = OffsetCurveDeformer()
                self.log_message("✅ Python wrappers initialized successfully")
            except Exception as e:
                self.log_message(f"❌ Error initializing wrappers: {str(e)}")
                self.curve_optimizer = None
                self.offset_deformer = None
        else:
            self.curve_optimizer = None
            self.offset_deformer = None
            if not WRAPPERS_AVAILABLE:
                self.log_message("⚠️ Python wrappers not available")
            if not MAYA_AVAILABLE:
                self.log_message("⚠️ Maya environment not available")
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # 메인 탭 위젯
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 🚀 워크플로우 탭 (가장 중요한 탭을 첫 번째로)
        self.create_workflow_tab()
        
        # 🔌 Plugin Status 탭
        plugin_tab = self.create_plugin_status_tab()
        self.tab_widget.addTab(plugin_tab, "🔌 Plugin Status")
        
        # 📁 Scene Objects 탭
        scene_tab = self.create_scene_objects_tab()
        self.tab_widget.addTab(scene_tab, "📁 Scene Objects")
        
        # 🔄 Offset Deformer Settings 탭
        deformer_tab = self.create_deformer_settings_tab()
        self.tab_widget.addTab(deformer_tab, "🔄 Offset Deformer")
        
        # 🔗 Binding & Connections 탭
        binding_tab = self.create_binding_tab()
        self.tab_widget.addTab(binding_tab, "🔗 Binding & Connections")
        
        # 로그 및 상태
        log_group = self.create_log_group()
        main_layout.addWidget(log_group)
    
    def create_scene_objects_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 📋 Scene Overview 그룹
        overview_group = QGroupBox("📋 Scene Overview")
        overview_layout = QHBoxLayout(overview_group)
        
        # 전체 오브젝트 수 표시
        self.total_curves_label = QLabel("Curves: 0")
        self.total_meshes_label = QLabel("Meshes: 0")
        self.total_joints_label = QLabel("Joints: 0")
        
        overview_layout.addWidget(self.total_curves_label)
        overview_layout.addWidget(self.total_meshes_label)
        overview_layout.addWidget(self.total_joints_label)
        overview_layout.addStretch()
        
        # 새로고침 버튼
        refresh_btn = QPushButton("🔄 Refresh Scene")
        refresh_btn.clicked.connect(self.refresh_scene)
        overview_layout.addWidget(refresh_btn)
        
        # 🎯 Curves 그룹 (곡선 관리)
        curves_group = QGroupBox("🎯 Curves")
        curves_layout = QVBoxLayout(curves_group)
        
        # 곡선 설명
        curves_info = QLabel("NURBS 곡선들을 선택하여 디포머에 연결할 수 있습니다.")
        curves_info.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 5px;")
        curves_layout.addWidget(curves_info)
        
        self.curves_list = QListWidget()
        self.curves_list.itemSelectionChanged.connect(self.on_curve_selection_changed)
        curves_layout.addWidget(self.curves_list)
        
        curves_buttons = QHBoxLayout()
        add_curve_btn = QPushButton("➕ Add Selected")
        del_curve_btn = QPushButton("➖ Remove")
        add_curve_btn.clicked.connect(self.add_curve)
        del_curve_btn.clicked.connect(self.remove_curve)
        curves_buttons.addWidget(add_curve_btn)
        curves_buttons.addWidget(del_curve_btn)
        curves_layout.addLayout(curves_buttons)
        
        # 🎯 Meshes 그룹 (메시 관리)
        meshes_group = QGroupBox("🎯 Meshes")
        meshes_layout = QVBoxLayout(meshes_group)
        
        # 메시 설명
        meshes_info = QLabel("폴리곤 메시들을 선택하여 디포머를 적용할 수 있습니다.")
        meshes_info.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 5px;")
        meshes_layout.addWidget(meshes_info)
        
        self.meshes_list = QListWidget()
        self.meshes_list.itemSelectionChanged.connect(self.on_mesh_selection_changed)
        meshes_layout.addWidget(self.meshes_list)
        
        meshes_buttons = QHBoxLayout()
        add_mesh_btn = QPushButton("➕ Add Selected")
        del_mesh_btn = QPushButton("➖ Remove")
        add_mesh_btn.clicked.connect(self.add_mesh)
        del_mesh_btn.clicked.connect(self.remove_mesh)
        meshes_buttons.addWidget(add_mesh_btn)
        meshes_buttons.addWidget(del_mesh_btn)
        meshes_layout.addLayout(meshes_buttons)
        
        # 🎯 Joints 그룹 (조인트 관리)
        joints_group = QGroupBox("🎯 Joints")
        joints_layout = QVBoxLayout(joints_group)
        
        # 조인트 설명
        joints_info = QLabel("스켈레톤 조인트들을 선택하여 곡선 생성에 사용할 수 있습니다.")
        joints_info.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 5px;")
        joints_layout.addWidget(joints_info)
        
        self.joints_list = QListWidget()
        joints_layout.addWidget(self.joints_list)
        
        joints_buttons = QHBoxLayout()
        add_joint_btn = QPushButton("➕ Add Selected")
        del_joint_btn = QPushButton("➖ Remove")
        add_joint_btn.clicked.connect(self.add_joint)
        del_joint_btn.clicked.connect(self.remove_joint)
        joints_buttons.addWidget(add_joint_btn)
        joints_buttons.addWidget(del_joint_btn)
        joints_layout.addLayout(joints_buttons)
        
        # 메인 레이아웃에 추가
        layout.addWidget(overview_group)
        
        # 오브젝트 그룹들을 가로로 배치
        objects_layout = QHBoxLayout()
        objects_layout.addWidget(curves_group)
        objects_layout.addWidget(meshes_group)
        objects_layout.addWidget(joints_group)
        layout.addLayout(objects_layout)
        
        return widget
    
    def create_plugin_status_tab(self):
        """플러그인 상태 확인 탭 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 플러그인 상태 표시 그룹
        status_group = QGroupBox("🔌 Plugin Status")
        status_layout = QVBoxLayout(status_group)
        
        # offsetCurveDeformer 상태
        self.offset_status_label = QLabel("❌ offsetCurveDeformer: Not Loaded")
        self.offset_status_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.offset_status_label)
        
        # inputCurveOptimizer 상태
        self.input_status_label = QLabel("❌ inputCurveOptimizer: Not Loaded")
        self.input_status_label.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.input_status_label)
        
        # 전체 상태
        self.overall_status_label = QLabel("⚠️ Some plugins are not loaded")
        self.overall_status_label.setStyleSheet("color: orange; font-weight: bold;")
        status_layout.addWidget(self.overall_status_label)
        
        status_layout.addSpacing(20)
        
        # 플러그인 로드 버튼
        load_btn = QPushButton("🔄 Load Plugins Manually")
        load_btn.clicked.connect(self.load_plugins_manually)
        load_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; font-weight: bold; }")
        status_layout.addWidget(load_btn)
        
        # 상태 새로고침 버튼
        refresh_btn = QPushButton("🔄 Refresh Status")
        refresh_btn.clicked.connect(self.refresh_plugin_status)
        refresh_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; padding: 10px; }")
        status_layout.addWidget(refresh_btn)
        
        status_layout.addSpacing(20)
        
        # 플러그인 정보 그룹
        info_group = QGroupBox("ℹ️ Plugin Information")
        info_layout = QVBoxLayout(info_group)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(200)
        info_text.setPlainText(
            "Maya 플러그인 상태:\n\n"
            "• offsetCurveDeformer: C++ 플러그인 (.mll)\n"
            "  - Offset Curve 생성 알고리즘\n"
            "  - Arc Segment, B-Spline 방식 지원\n"
            "  - 볼륨 보존, 슬라이딩 효과, 포즈 블렌딩\n\n"
            "• inputCurveOptimizer: C++ 플러그인 (.mll)\n"
            "  - 입력 커브 최적화 도구\n"
            "  - 메시에서 곡선 자동 생성\n"
            "  - 디포머용 곡선 최적화\n"
            "  - 스켈레톤에서 곡선 생성\n"
            "  - 배치 최적화 및 특허 기반 곡률 분석\n\n"
            "⚠️ 이 플러그인들이 로드되지 않으면 GUI가 제대로 작동하지 않습니다!"
        )
        info_layout.addWidget(info_text)
        
        # Python 래퍼 상태 그룹
        wrapper_group = QGroupBox("🐍 Python Wrapper Status")
        wrapper_layout = QVBoxLayout(wrapper_group)
        
        self.wrapper_status_label = QLabel("Python Wrappers: Checking...")
        self.wrapper_status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;")
        wrapper_layout.addWidget(self.wrapper_status_label)
        
        # 래퍼 상태 업데이트
        if WRAPPERS_AVAILABLE:
            self.wrapper_status_label.setText("✅ Python Wrappers: Available")
            self.wrapper_status_label.setStyleSheet("padding: 5px; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724;")
        else:
            self.wrapper_status_label.setText("❌ Python Wrappers: Not Available")
            self.wrapper_status_label.setStyleSheet("padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;")
        
        # Maya 환경 상태
        maya_group = QGroupBox("🎬 Maya Environment")
        maya_layout = QVBoxLayout(maya_group)
        
        if MAYA_AVAILABLE:
            maya_status = "✅ Maya Environment: Available"
            maya_style = "padding: 5px; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724;"
        else:
            maya_status = "❌ Maya Environment: Not Available"
            maya_style = "padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;"
        
        maya_status_label = QLabel(maya_status)
        maya_status_label.setStyleSheet(maya_style)
        maya_layout.addWidget(maya_status_label)
        
        # 레이아웃에 추가
        layout.addWidget(status_group)
        layout.addWidget(info_group)
        layout.addWidget(wrapper_group)
        layout.addWidget(maya_group)
        layout.addStretch()
        
        return widget
    
    def create_deformer_settings_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 🎯 Basic Settings 그룹 (핵심 설정)
        basic_group = QGroupBox("🎯 Basic Settings")
        basic_layout = QVBoxLayout(basic_group)
        
        # Offset Mode
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Offset Mode:"))
        self.offset_mode_combo = QComboBox()
        self.offset_mode_combo.addItems(["Arc Segment", "B-Spline"])
        self.offset_mode_combo.setCurrentText("Arc Segment")
        mode_layout.addWidget(self.offset_mode_combo)
        basic_layout.addLayout(mode_layout)
        
        # Falloff Radius
        falloff_layout = QHBoxLayout()
        falloff_layout.addWidget(QLabel("Falloff Radius:"))
        self.falloff_spin = QDoubleSpinBox()
        self.falloff_spin.setRange(0.001, 100.0)
        self.falloff_spin.setValue(10.0)
        self.falloff_spin.setSingleStep(0.1)
        falloff_layout.addWidget(self.falloff_spin)
        basic_layout.addLayout(falloff_layout)
        
        # Max Influences
        max_influences_layout = QHBoxLayout()
        max_influences_layout.addWidget(QLabel("Max Influences:"))
        self.max_influences_spin = QSpinBox()
        self.max_influences_spin.setRange(1, 10)
        self.max_influences_spin.setValue(4)
        max_influences_layout.addWidget(self.max_influences_spin)
        basic_layout.addLayout(max_influences_layout)
        
        # 🎨 Deformation Control 그룹 (변형 제어)
        deformation_group = QGroupBox("🎨 Deformation Control")
        deformation_layout = QVBoxLayout(deformation_group)
        
        # Volume Strength
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume Strength:"))
        self.volume_strength_spin = QDoubleSpinBox()
        self.volume_strength_spin.setRange(0.0, 5.0)
        self.volume_strength_spin.setValue(1.0)
        self.volume_strength_spin.setSingleStep(0.1)
        volume_layout.addWidget(self.volume_strength_spin)
        deformation_layout.addLayout(volume_layout)
        
        # Slide Effect
        slide_layout = QHBoxLayout()
        slide_layout.addWidget(QLabel("Slide Effect:"))
        self.slide_effect_spin = QDoubleSpinBox()
        self.slide_effect_spin.setRange(-2.0, 2.0)
        self.slide_effect_spin.setValue(0.0)
        self.slide_effect_spin.setSingleStep(0.1)
        slide_layout.addWidget(self.slide_effect_spin)
        deformation_layout.addLayout(slide_layout)
        
        # 🌀 Transformation Distribution 그룹 (변환 분포)
        distribution_group = QGroupBox("🌀 Transformation Distribution")
        distribution_layout = QVBoxLayout(distribution_group)
        
        # Rotation Distribution
        rotation_layout = QHBoxLayout()
        rotation_layout.addWidget(QLabel("Rotation Distribution:"))
        self.rotation_distribution_spin = QDoubleSpinBox()
        self.rotation_distribution_spin.setRange(0.0, 2.0)
        self.rotation_distribution_spin.setValue(0.5)
        self.rotation_distribution_spin.setSingleStep(0.1)
        rotation_layout.addWidget(self.rotation_distribution_spin)
        distribution_layout.addLayout(rotation_layout)
        
        # Scale Distribution
        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Scale Distribution:"))
        self.scale_distribution_spin = QDoubleSpinBox()
        self.scale_distribution_spin.setRange(0.0, 2.0)
        self.scale_distribution_spin.setValue(0.5)
        self.scale_distribution_spin.setSingleStep(0.1)
        scale_layout.addWidget(self.scale_distribution_spin)
        distribution_layout.addLayout(scale_layout)
        
        # Twist Distribution
        twist_layout = QHBoxLayout()
        twist_layout.addWidget(QLabel("Twist Distribution:"))
        self.twist_distribution_spin = QDoubleSpinBox()
        self.twist_distribution_spin.setRange(0.0, 2.0)
        self.twist_distribution_spin.setValue(0.5)
        self.twist_distribution_spin.setSingleStep(0.1)
        twist_layout.addWidget(self.twist_distribution_spin)
        distribution_layout.addLayout(twist_layout)
        
        # Axial Sliding
        axial_layout = QHBoxLayout()
        axial_layout.addWidget(QLabel("Axial Sliding:"))
        self.axial_sliding_spin = QDoubleSpinBox()
        self.axial_sliding_spin.setRange(-1.0, 1.0)
        self.axial_sliding_spin.setValue(0.0)
        self.axial_sliding_spin.setSingleStep(0.1)
        axial_layout.addWidget(self.axial_sliding_spin)
        distribution_layout.addLayout(axial_layout)
        
        # ⚙️ Performance & Debug 그룹 (성능 및 디버그)
        performance_group = QGroupBox("⚙️ Performance & Debug")
        performance_layout = QVBoxLayout(performance_group)
        
        self.parallel_check = QCheckBox("Use Parallel Processing")
        self.debug_display_check = QCheckBox("Debug Display")
        
        self.parallel_check.setChecked(True)
        
        performance_layout.addWidget(self.parallel_check)
        performance_layout.addWidget(self.debug_display_check)
        
        # 🔧 Advanced Features 그룹 (고급 기능)
        advanced_group = QGroupBox("🔧 Advanced Features")
        advanced_layout = QVBoxLayout(advanced_group)
        
        # Pose Blending
        pose_blend_layout = QHBoxLayout()
        pose_blend_layout.addWidget(QLabel("Enable Pose Blending:"))
        self.pose_blend_check = QCheckBox()
        pose_blend_layout.addWidget(self.pose_blend_check)
        advanced_layout.addLayout(pose_blend_layout)
        
        # Pose Target
        pose_target_layout = QHBoxLayout()
        pose_target_layout.addWidget(QLabel("Pose Target:"))
        self.pose_target_spin = QDoubleSpinBox()
        self.pose_target_spin.setRange(0.0, 1.0)
        self.pose_target_spin.setValue(0.0)
        self.pose_target_spin.setSingleStep(0.1)
        pose_target_layout.addWidget(self.pose_target_spin)
        advanced_layout.addLayout(pose_target_layout)
        
        # Pose Weight
        pose_weight_layout = QHBoxLayout()
        pose_weight_layout.addWidget(QLabel("Pose Weight:"))
        self.pose_weight_spin = QDoubleSpinBox()
        self.pose_weight_spin.setRange(0.0, 1.0)
        self.pose_weight_spin.setValue(0.5)
        self.pose_weight_spin.setSingleStep(0.1)
        pose_weight_layout.addWidget(self.pose_weight_spin)
        advanced_layout.addLayout(pose_weight_layout)
        
        # 레이아웃에 추가 (논리적 순서로)
        layout.addWidget(basic_group)
        layout.addWidget(deformation_group)
        layout.addWidget(distribution_group)
        layout.addWidget(performance_group)
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        return widget
    
    def create_binding_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 📋 Selection Status 그룹 (선택 상태)
        selection_group = QGroupBox("📋 Selection Status")
        selection_layout = QVBoxLayout(selection_group)
        
        # 선택된 오브젝트 정보
        self.selected_curve_label = QLabel("Selected Curve: None")
        self.selected_curve_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;")
        self.selected_mesh_label = QLabel("Selected Mesh: None")
        self.selected_mesh_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;")
        
        selection_layout.addWidget(self.selected_curve_label)
        selection_layout.addWidget(self.selected_mesh_label)
        
        # 🔗 Connected Deformers 그룹 (연결된 디포머들)
        deformers_group = QGroupBox("🔗 Connected Deformers")
        deformers_layout = QVBoxLayout(deformers_group)
        
        # 디포머 정보 설명
        deformers_info = QLabel("현재 씬에서 사용 중인 offsetCurveDeformer 노드들입니다.")
        deformers_info.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 5px;")
        deformers_layout.addWidget(deformers_info)
        
        self.deformers_list = QListWidget()
        deformers_layout.addWidget(self.deformers_list)
        
        # 디포머 새로고침 버튼
        refresh_deformers_btn = QPushButton("🔄 Refresh Deformers")
        refresh_deformers_btn.clicked.connect(self.find_connected_deformers)
        deformers_layout.addWidget(refresh_deformers_btn)
        
        # 🎯 Binding Actions 그룹 (바인딩 액션)
        actions_group = QGroupBox("🎯 Binding Actions")
        actions_layout = QVBoxLayout(actions_group)
        
        # 바인딩 설명
        binding_info = QLabel("선택된 메시와 곡선을 디포머로 연결합니다.")
        binding_info.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 10px;")
        actions_layout.addWidget(binding_info)
        
        # 바인딩 버튼들
        bind_btn = QPushButton("🔗 Bind Selected")
        bind_btn.setStyleSheet("font-weight: bold; padding: 8px; background-color: #4CAF50; color: white;")
        bind_btn.clicked.connect(self.bind_selected)
        
        paint_weights_btn = QPushButton("🎨 Paint Weights")
        paint_weights_btn.setStyleSheet("padding: 8px; background-color: #2196F3; color: white;")
        paint_weights_btn.clicked.connect(self.paint_weights)
        
        actions_layout.addWidget(bind_btn)
        actions_layout.addWidget(paint_weights_btn)
        
        # 📊 Connection Info 그룹 (연결 정보)
        connection_info_group = QGroupBox("📊 Connection Info")
        connection_info_layout = QVBoxLayout(connection_info_group)
        
        # 연결된 메시와 조인트 정보
        self.connected_meshes_label = QLabel("Connected Meshes: 0")
        self.connected_joints_label = QLabel("Connected Joints: 0")
        
        connection_info_layout.addWidget(self.connected_meshes_label)
        connection_info_layout.addWidget(self.connected_joints_label)
        
        # 연결된 메시 리스트
        self.connected_meshes_list = QListWidget()
        self.connected_meshes_list.setMaximumHeight(80)
        connection_info_layout.addWidget(QLabel("Connected Meshes:"))
        connection_info_layout.addWidget(self.connected_meshes_list)
        
        # 연결된 조인트 리스트
        self.connected_joints_list = QListWidget()
        self.connected_joints_list.setMaximumHeight(80)
        connection_info_layout.addWidget(QLabel("Connected Joints:"))
        connection_info_layout.addWidget(self.connected_joints_list)
        
        # 연결 정보 새로고침 버튼
        refresh_connections_btn = QPushButton("🔄 Refresh Connections")
        refresh_connections_btn.clicked.connect(self.find_connected_meshes_and_joints)
        connection_info_layout.addWidget(refresh_connections_btn)
        
        # 레이아웃에 추가
        layout.addWidget(selection_group)
        layout.addWidget(deformers_group)
        layout.addWidget(actions_group)
        layout.addWidget(connection_info_group)
        layout.addStretch()
        
        return widget
    
    def create_log_group(self):
        group = QGroupBox("📝 Log & Status")
        layout = QVBoxLayout(group)
        
        # 로그 컨트롤 버튼들
        log_controls = QHBoxLayout()
        
        clear_log_btn = QPushButton("🗑️ Clear Log")
        clear_log_btn.clicked.connect(lambda: self.log_text.clear())
        clear_log_btn.setStyleSheet("padding: 5px; background-color: #dc3545; color: white;")
        
        save_log_btn = QPushButton("💾 Save Log")
        save_log_btn.clicked.connect(self.save_log)
        save_log_btn.setStyleSheet("padding: 5px; background-color: #28a745; color: white;")
        
        log_controls.addWidget(clear_log_btn)
        log_controls.addWidget(save_log_btn)
        log_controls.addStretch()
        
        layout.addLayout(log_controls)
        
        # 로그 텍스트 영역
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("font-family: 'Consolas', 'Monaco', monospace; font-size: 10px;")
        layout.addWidget(self.log_text)
        
        return group
    
    def setup_connections(self):
        # Arc/B-Spline 라디오 버튼 연결
        self.offset_mode_combo.currentTextChanged.connect(self.on_method_changed)
        
        # 설정 변경 시 디포머 업데이트
        self.falloff_spin.valueChanged.connect(self.update_deformer_settings)
        self.max_influences_spin.valueChanged.connect(self.update_deformer_settings)
        self.volume_strength_spin.valueChanged.connect(self.update_deformer_settings)
        self.slide_effect_spin.valueChanged.connect(self.update_deformer_settings)
        self.rotation_distribution_spin.valueChanged.connect(self.update_deformer_settings)
        self.scale_distribution_spin.valueChanged.connect(self.update_deformer_settings)
        self.twist_distribution_spin.valueChanged.connect(self.update_deformer_settings)
        self.axial_sliding_spin.valueChanged.connect(self.update_deformer_settings)
        self.parallel_check.toggled.connect(self.update_deformer_settings)
        self.debug_display_check.toggled.connect(self.update_deformer_settings)
        self.pose_blend_check.toggled.connect(self.update_deformer_settings)
        self.pose_target_spin.valueChanged.connect(self.update_deformer_settings)
        self.pose_weight_spin.valueChanged.connect(self.update_deformer_settings)
    
    def refresh_scene(self):
        """씬의 모든 오브젝트를 새로고침"""
        self.log_message("Refreshing scene objects...")
        
        # 커브 찾기
        curves = cmds.ls(type="nurbsCurve")
        self.scene_objects['curves'] = [cmds.listRelatives(c, parent=True)[0] for c in curves if cmds.listRelatives(c, parent=True)]
        self.update_list_widget(self.curves_list, self.scene_objects['curves'])
        self.total_curves_label.setText(f"Curves: {len(self.scene_objects['curves'])}")
        
        # 메시 찾기
        meshes = cmds.ls(type="mesh")
        self.scene_objects['meshes'] = [cmds.listRelatives(m, parent=True)[0] for m in meshes if cmds.listRelatives(m, parent=True)]
        self.update_list_widget(self.meshes_list, self.scene_objects['meshes'])
        self.total_meshes_label.setText(f"Meshes: {len(self.scene_objects['meshes'])}")
        
        # 조인트 찾기
        joints = cmds.ls(type="joint")
        self.scene_objects['joints'] = joints
        self.update_list_widget(self.joints_list, self.scene_objects['joints'])
        self.total_joints_label.setText(f"Joints: {len(self.scene_objects['joints'])}")
        
        self.log_message(f"Found {len(self.scene_objects['curves'])} curves, {len(self.scene_objects['meshes'])} meshes, {len(self.scene_objects['joints'])} joints")
    
    def update_list_widget(self, list_widget, items):
        """리스트 위젯 업데이트"""
        list_widget.clear()
        for item in items:
            list_widget.addItem(item)
    
    def add_curve(self):
        """커브 수동 추가"""
        selection = cmds.ls(selection=True)
        if not selection:
            self.log_message("Please select a curve to add")
            return
        
        for obj in selection:
            if obj not in self.scene_objects['curves']:
                self.scene_objects['curves'].append(obj)
        
        self.update_list_widget(self.curves_list, self.scene_objects['curves'])
        self.total_curves_label.setText(f"Curves: {len(self.scene_objects['curves'])}")
        self.log_message(f"Added {len(selection)} curve(s)")
    
    def remove_curve(self):
        """선택된 커브 제거"""
        current_item = self.curves_list.currentItem()
        if current_item:
            curve_name = current_item.text()
            if curve_name in self.scene_objects['curves']:
                self.scene_objects['curves'].remove(curve_name)
                self.update_list_widget(self.curves_list, self.scene_objects['curves'])
                self.total_curves_label.setText(f"Curves: {len(self.scene_objects['curves'])}")
                self.log_message(f"Removed curve: {curve_name}")
    
    def add_mesh(self):
        """메시 수동 추가"""
        selection = cmds.ls(selection=True)
        if not selection:
            self.log_message("Please select a mesh to add")
            return
        
        for obj in selection:
            if obj not in self.scene_objects['meshes']:
                self.scene_objects['meshes'].append(obj)
        
        self.update_list_widget(self.meshes_list, self.scene_objects['meshes'])
        self.total_meshes_label.setText(f"Meshes: {len(self.scene_objects['meshes'])}")
        self.log_message(f"Added {len(selection)} mesh(es)")
    
    def remove_mesh(self):
        """선택된 메시 제거"""
        current_item = self.meshes_list.currentItem()
        if current_item:
            mesh_name = current_item.text()
            if mesh_name in self.scene_objects['meshes']:
                self.scene_objects['meshes'].remove(mesh_name)
                self.update_list_widget(self.meshes_list, self.scene_objects['meshes'])
                self.total_meshes_label.setText(f"Meshes: {len(self.scene_objects['meshes'])}")
                self.log_message(f"Removed mesh: {mesh_name}")
    
    def add_joint(self):
        """조인트 수동 추가"""
        selection = cmds.ls(selection=True)
        if not selection:
            self.log_message("Please select a joint to add")
            return
        
        for obj in selection:
            if obj not in self.scene_objects['joints']:
                self.scene_objects['joints'].append(obj)
        
        self.update_list_widget(self.joints_list, self.scene_objects['joints'])
        self.total_joints_label.setText(f"Joints: {len(self.scene_objects['joints'])}")
        self.log_message(f"Added {len(selection)} joint(s)")
    
    def remove_joint(self):
        """선택된 조인트 제거"""
        current_item = self.joints_list.currentItem()
        if current_item:
            joint_name = current_item.text()
            if joint_name in self.scene_objects['joints']:
                self.scene_objects['joints'].remove(joint_name)
                self.update_list_widget(self.joints_list, self.scene_objects['joints'])
                self.total_joints_label.setText(f"Joints: {len(self.scene_objects['joints'])}")
                self.log_message(f"Removed joint: {joint_name}")
    
    def on_curve_selection_changed(self):
        """커브 선택 변경 시 호출 - 연결된 디포머 노드들과 관련 메시/조인트를 자동으로 찾아서 리스트에 표시"""
        current_item = self.curves_list.currentItem()
        if current_item:
            self.selected_curve = current_item.text()
            self.selected_curve_label.setText(f"Selected Curve: {self.selected_curve}")
            
            # 연결된 디포머 노드들 자동 찾기
            self.find_connected_deformers()
            
            # 연결된 메시와 조인트들도 자동으로 찾아서 리스트에 표시
            self.find_connected_meshes_and_joints()
            
            self.log_message(f"Selected curve: {self.selected_curve}")
    
    def on_mesh_selection_changed(self):
        """메시 선택 변경 시 호출"""
        current_item = self.meshes_list.currentItem()
        if current_item:
            self.selected_mesh = current_item.text()
            self.selected_mesh_label.setText(f"Selected Mesh: {self.selected_mesh}")
            self.log_message(f"Selected mesh: {self.selected_mesh}")
    
    def find_connected_deformers(self):
        """선택된 커브에 연결된 디포머 노드들을 자동으로 찾아서 리스트에 표시"""
        if not self.selected_curve:
            self.deformers_list.clear()
            return
        
        # 커브의 custom attributes에서 message 플러그로 연결된 노드들 찾기
        connected_nodes = []
        
        # 커브의 모든 커스텀 속성 확인
        custom_attrs = cmds.listAttr(self.selected_curve, userDefined=True)
        if custom_attrs:
            for attr in custom_attrs:
                if cmds.getAttr(f"{self.selected_curve}.{attr}", type=True) == "message":
                    # message 속성에 연결된 노드 찾기
                    connections = cmds.listConnections(f"{self.selected_curve}.{attr}", source=True, destination=False)
                    if connections:
                        connected_nodes.extend(connections)
        
        # 커브에 직접 연결된 디포머들도 찾기
        history = cmds.listHistory(self.selected_curve, interestLevel=2)
        if history:
            for node in history:
                if cmds.objectType(node) in ["offsetCurveDeformer", "blendShape", "cluster", "lattice", "deformBend", "deformTwist", "deformSine"]:
                    if node not in connected_nodes:
                        connected_nodes.append(node)
        
        # 커브의 출력 연결 확인 (다른 노드의 입력으로 사용되는 경우)
        output_connections = cmds.listConnections(self.selected_curve, source=False, destination=True)
        if output_connections:
            for node in output_connections:
                if cmds.objectType(node) in ["offsetCurveDeformer", "blendShape", "cluster", "lattice", "deformBend", "deformTwist", "deformSine"]:
                    if node not in connected_nodes:
                        connected_nodes.append(node)
        
        # 리스트 업데이트
        self.deformers_list.clear()
        for node in connected_nodes:
            self.deformers_list.addItem(node)
        
        self.log_message(f"Found {len(connected_nodes)} connected deformer nodes")
    
    def find_connected_meshes_and_joints(self):
        """선택된 커브와 연결된 메시와 조인트들을 자동으로 찾아서 리스트에 표시"""
        if not self.selected_curve:
            return
        
        connected_meshes = []
        connected_joints = []
        
        # 1. 커브에 직접 연결된 메시 찾기 (커브가 메시의 입력으로 사용되는 경우)
        output_connections = cmds.listConnections(self.selected_curve, source=False, destination=True)
        if output_connections:
            for node in output_connections:
                # 메시 노드인지 확인
                if cmds.objectType(node) == "mesh":
                    mesh_parent = cmds.listRelatives(node, parent=True)
                    if mesh_parent and mesh_parent[0] not in connected_meshes:
                        connected_meshes.append(mesh_parent[0])
                # 메시의 부모가 메시인 경우 (그룹화된 메시)
                elif cmds.objectType(node) == "transform":
                    mesh_children = cmds.listRelatives(node, type="mesh")
                    if mesh_children and node not in connected_meshes:
                        connected_meshes.append(node)
        
        # 2. 커브와 연결된 디포머를 통해 간접적으로 연결된 메시 찾기
        deformers = self.get_deformer_connections()
        for deformer in deformers:
            # 디포머에 연결된 메시 찾기
            deformer_connections = cmds.listConnections(deformer, source=False, destination=True)
            if deformer_connections:
                for node in deformer_connections:
                    if cmds.objectType(node) == "mesh":
                        mesh_parent = cmds.listRelatives(node, parent=True)
                        if mesh_parent and mesh_parent[0] not in connected_meshes:
                            connected_meshes.append(mesh_parent[0])
                    elif cmds.objectType(node) == "transform":
                        mesh_children = cmds.listRelatives(node, type="mesh")
                        if mesh_children and node not in connected_meshes:
                            connected_meshes.append(node)
        
        # 3. 커브와 연결된 조인트 찾기 (스켈레톤 기반 애니메이션)
        # 커브의 부모가 조인트인 경우
        curve_parent = cmds.listRelatives(self.selected_curve, parent=True)
        if curve_parent:
            parent_type = cmds.objectType(curve_parent[0])
            if parent_type == "joint" and curve_parent[0] not in connected_joints:
                connected_joints.append(curve_parent[0])
        
        # 커브의 자식이 조인트인 경우
        curve_children = cmds.listRelatives(self.selected_curve, children=True, type="joint")
        if curve_children:
            for joint in curve_children:
                if joint not in connected_joints:
                    connected_joints.append(joint)
        
        # 4. 커브의 커스텀 속성에서 연결된 메시/조인트 정보 확인
        custom_attrs = cmds.listAttr(self.selected_curve, userDefined=True)
        if custom_attrs:
            for attr in custom_attrs:
                attr_type = cmds.getAttr(f"{self.selected_curve}.{attr}", type=True)
                if attr_type == "message":
                    connections = cmds.listConnections(f"{self.selected_curve}.{attr}", source=True, destination=False)
                    if connections:
                        for node in connections:
                            node_type = cmds.objectType(node)
                            if node_type == "mesh":
                                mesh_parent = cmds.listRelatives(node, parent=True)
                                if mesh_parent and mesh_parent[0] not in connected_meshes:
                                    connected_meshes.append(mesh_parent[0])
                            elif node_type == "joint" and node not in connected_joints:
                                connected_joints.append(node)
        
        # 5. 리스트 업데이트
        self.update_connected_meshes_list(connected_meshes)
        self.update_connected_joints_list(connected_joints)
        
        self.log_message(f"Found {len(connected_meshes)} connected meshes and {len(connected_joints)} connected joints")
    
    def update_plugin_status_display(self):
        """플러그인 상태 표시 업데이트"""
        # offsetCurveDeformer 상태
        if self.plugin_status['offsetCurveDeformer']:
            self.offset_status_label.setText("✅ offsetCurveDeformer: Loaded")
            self.offset_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.offset_status_label.setText("❌ offsetCurveDeformer: Not Loaded")
            self.offset_status_label.setStyleSheet("color: red; font-weight: bold;")
        
        # inputCurveOptimizer 상태
        if self.plugin_status['inputCurveOptimizer']:
            self.input_status_label.setText("✅ inputCurveOptimizer: Loaded")
            self.input_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.input_status_label.setText("❌ inputCurveOptimizer: Not Loaded")
            self.input_status_label.setStyleSheet("color: red; font-weight: bold;")
        
        # 전체 상태
        if self.plugin_status['all_loaded']:
            self.overall_status_label.setText("🎉 All plugins are loaded!")
            self.overall_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.overall_status_label.setText("⚠️ Some plugins are not loaded")
            self.overall_status_label.setStyleSheet("color: orange; font-weight: bold;")
    
    def refresh_plugin_status(self):
        """플러그인 상태 새로고침"""
        self.log_message("🔄 Refreshing plugin status...")
        self.plugin_status = self.check_plugin_status()
        self.update_plugin_status_display()
        
        if self.plugin_status['all_loaded']:
            self.log_message("🎉 All plugins are now loaded!")
            # 모든 플러그인이 로드되면 경고 메시지 숨기기
            self.overall_status_label.setText("🎉 All plugins are loaded!")
            self.overall_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.log_message("⚠️ Some plugins are still not loaded")
            # 플러그인이 로드되지 않은 경우 경고 표시
            self.overall_status_label.setText("⚠️ Some plugins are not loaded")
            self.overall_status_label.setStyleSheet("color: orange; font-weight: bold;")
    
    def get_deformer_connections(self):
        """현재 디포머 리스트에서 노드 이름들 반환"""
        deformer_nodes = []
        for i in range(self.deformers_list.count()):
            item = self.deformers_list.item(i)
            if item:
                deformer_nodes.append(item.text())
        return deformer_nodes
    
    def update_connected_meshes_list(self, connected_meshes):
        """연결된 메시 리스트 업데이트"""
        self.connected_meshes_list.clear()
        for mesh in connected_meshes:
            self.connected_meshes_list.addItem(mesh)
        
        # 연결된 메시 수 업데이트
        self.connected_meshes_label.setText(f"Connected Meshes: {len(connected_meshes)}")
    
    def update_connected_joints_list(self, connected_joints):
        """연결된 조인트 리스트 업데이트"""
        self.connected_joints_list.clear()
        for joint in connected_joints:
            self.connected_joints_list.addItem(joint)
        
        # 연결된 조인트 수 업데이트
        self.connected_joints_label.setText(f"Connected Joints: {len(connected_joints)}")
    
    def bind_selected(self):
        """선택된 커브와 메시를 바인딩"""
        if not self.selected_curve or not self.selected_mesh:
            self.log_message("Please select both a curve and a mesh")
            return
        
        # 플러그인 상태 확인
        if not self.plugin_status['all_loaded']:
            self.log_message("❌ Cannot bind: Required plugins are not loaded")
            QMessageBox.warning(self, "플러그인 오류", 
                              "필수 플러그인이 로드되지 않았습니다.\n"
                              "Plugin Status 탭에서 플러그인을 로드하세요.")
            return
        
        # Python 래퍼 확인
        if not self.offset_deformer:
            self.log_message("❌ Cannot bind: Python wrapper not available")
            QMessageBox.warning(self, "래퍼 오류", 
                              "Python 래퍼를 사용할 수 없습니다.\n"
                              "래퍼 초기화를 확인하세요.")
            return
        
        try:
            # Python 래퍼를 사용하여 디포머 생성
            deformer_name = f"offsetDeformer_{self.selected_mesh}"
            
            # 디포머 생성
            deformer = self.offset_deformer.create_deformer(
                mesh_name=self.selected_mesh,
                deformer_name=deformer_name
            )
            
            if not deformer:
                self.log_message("❌ Failed to create deformer")
                return
            
            # 실제 C++ 플러그인 파라미터 설정
            # Offset Mode (0: Arc Segment, 1: B-Spline)
            mode = 0 if self.offset_mode_combo.currentText() == "Arc Segment" else 1
            self.offset_deformer.set_offset_mode(deformer, mode)
            
            # Core Settings
            self.offset_deformer.set_falloff_radius(deformer, self.falloff_spin.value())
            self.offset_deformer.set_max_influences(deformer, self.max_influences_spin.value())
            
            # Artist Control Settings
            self.offset_deformer.set_volume_strength(deformer, self.volume_strength_spin.value())
            self.offset_deformer.set_slide_effect(deformer, self.slide_effect_spin.value())
            self.offset_deformer.set_distribution_parameters(
                deformer,
                rotation=self.rotation_distribution_spin.value(),
                scale=self.scale_distribution_spin.value(),
                twist=self.twist_distribution_spin.value()
            )
            self.offset_deformer.set_axial_sliding(deformer, self.axial_sliding_spin.value())
            
            # Options
            self.offset_deformer.set_parallel_processing(deformer, self.parallel_check.isChecked())
            self.offset_deformer.set_debug_display(deformer, self.debug_display_check.isChecked())
            
            # Advanced Features
            self.offset_deformer.set_pose_blending(
                deformer,
                enable=self.pose_blend_check.isChecked(),
                target=self.pose_target_spin.value(),
                weight=self.pose_weight_spin.value()
            )
            
            # 커브 연결
            self.offset_deformer.connect_curves(deformer, [self.selected_curve])
            
            # 커스텀 속성에 디포머 연결 정보 저장
            if not cmds.attributeQuery("connectedDeformers", node=self.selected_curve, exists=True):
                cmds.addAttr(self.selected_curve, longName="connectedDeformers", dataType="string")
            
            current_deformers = cmds.getAttr(f"{self.selected_curve}.connectedDeformers") or ""
            if deformer_name not in current_deformers:
                new_deformers = f"{current_deformers},{deformer_name}" if current_deformers else deformer_name
                cmds.setAttr(f"{self.selected_curve}.connectedDeformers", new_deformers, type="string")
            
            self.log_message(f"Successfully bound {self.selected_mesh} to {self.selected_curve}")
            self.find_connected_deformers()  # 디포머 리스트 자동 업데이트
            
        except Exception as e:
            self.log_message(f"Error during binding: {str(e)}")
    
    def paint_weights(self):
        """가중치 페인팅 모드 활성화"""
        if not self.selected_mesh:
            self.log_message("Please select a mesh first")
            return
        
        # 플러그인 상태 확인
        if not self.plugin_status['all_loaded']:
            self.log_message("❌ Cannot paint weights: Required plugins are not loaded")
            QMessageBox.warning(self, "플러그인 오류", 
                              "필수 플러그인이 로드되지 않았습니다.\n"
                              "Plugin Status 탭에서 플러그인을 로드하세요.")
            return
        
        try:
            # Maya의 가중치 페인팅 도구 활성화
            cmds.ArtPaintSkinWeightsTool()
            self.log_message(f"Weight painting mode activated for {self.selected_mesh}")
        except Exception as e:
            self.log_message(f"Error activating weight painting: {str(e)}")
    
    def on_method_changed(self):
        """오프셋 방식 변경 시 호출"""
        mode = self.offset_mode_combo.currentText()
        if mode == "Arc Segment":
            self.log_message("Switched to Arc Segment method (mode 0)")
        else:
            self.log_message("Switched to B-Spline method (mode 1)")
    
    def update_deformer_settings(self):
        """디포머 설정 업데이트"""
        self.log_message("Deformer settings updated")
        # 여기서 실제 디포머 노드의 파라미터를 업데이트할 수 있습니다
    
    def check_plugin_status(self):
        """Maya 플러그인 상태 확인"""
        plugin_status = {
            'offsetCurveDeformer': False,
            'inputCurveOptimizer': False,
            'all_loaded': False
        }
        
        try:
            # Maya가 사용 가능한 경우에만 플러그인 상태 확인
            if MAYA_AVAILABLE:
                # offsetCurveDeformer 플러그인 확인
                try:
                    # 플러그인이 로드되어 있는지 확인
                    loaded_plugins = cmds.pluginInfo(query=True, listPlugins=True)
                    if 'offsetCurveDeformer' in loaded_plugins:
                        plugin_status['offsetCurveDeformer'] = True
                        self.log_message("✅ offsetCurveDeformer plugin is loaded")
                    else:
                        self.log_message("❌ offsetCurveDeformer plugin is not loaded")
                except Exception as e:
                    self.log_message(f"Error checking offsetCurveDeformer: {str(e)}")
                
                # inputCurveOptimizer 플러그인 확인
                try:
                    loaded_plugins = cmds.pluginInfo(query=True, listPlugins=True)
                    if 'inputCurveOptimizer' in loaded_plugins:
                        plugin_status['inputCurveOptimizer'] = True
                        self.log_message("✅ inputCurveOptimizer plugin is loaded")
                    else:
                        self.log_message("❌ inputCurveOptimizer plugin is not loaded")
                except Exception as e:
                    self.log_message(f"Error checking inputCurveOptimizer: {str(e)}")
                
                # 전체 상태 업데이트
                plugin_status['all_loaded'] = (
                    plugin_status['offsetCurveDeformer'] and 
                    plugin_status['inputCurveOptimizer']
                )
                
                if plugin_status['all_loaded']:
                    self.log_message("🎉 All required plugins are loaded!")
                else:
                    self.log_message("⚠️ Some required plugins are not loaded")
            else:
                self.log_message("Maya environment not available")
                
        except Exception as e:
            self.log_message(f"Error during plugin status check: {str(e)}")
        
        return plugin_status
    
    def show_plugin_warnings(self):
        """플러그인 상태에 따른 경고 메시지 표시"""
        if not self.plugin_status['all_loaded']:
            warning_msg = "⚠️ 플러그인 경고\n\n"
            
            if not self.plugin_status['offsetCurveDeformer']:
                warning_msg += "• offsetCurveDeformer 플러그인이 로드되지 않았습니다.\n"
                warning_msg += "  이 플러그인은 오프셋 커브 생성에 필수적입니다.\n\n"
            
            if not self.plugin_status['inputCurveOptimizer']:
                warning_msg += "• inputCurveOptimizer 플러그인이 로드되지 않았습니다.\n"
                warning_msg += "  이 플러그인은 입력 커브 최적화에 필수적입니다.\n\n"
            
            warning_msg += "해결 방법:\n"
            warning_msg += "1. Maya의 Plug-in Manager에서 플러그인을 수동으로 로드하세요.\n"
            warning_msg += "2. 또는 'Load Plugins Manually' 버튼을 클릭하세요.\n"
            warning_msg += "3. 플러그인이 로드된 후 'Refresh Status' 버튼을 클릭하세요."
            
            # 경고 다이얼로그 표시
            QMessageBox.warning(self, "플러그인 경고", warning_msg)
            
            # 로그에도 경고 메시지 추가
            self.log_message("⚠️ GUI 로드 시 플러그인 경고가 표시되었습니다.")
    
    def load_plugins_manually(self):
        """플러그인 수동 로드 시도"""
        self.log_message("🔄 Attempting to load plugins manually...")
        
        try:
            if MAYA_AVAILABLE:
                # offsetCurveDeformer 플러그인 로드 시도
                if not self.plugin_status['offsetCurveDeformer']:
                    try:
                        cmds.loadPlugin("offsetCurveDeformer")
                        self.log_message("✅ offsetCurveDeformer plugin loaded successfully")
                    except Exception as e:
                        self.log_message(f"❌ Failed to load offsetCurveDeformer: {str(e)}")
                
                # inputCurveOptimizer 플러그인 로드 시도
                if not self.plugin_status['inputCurveOptimizer']:
                    try:
                        cmds.loadPlugin("inputCurveOptimizer")
                        self.log_message("✅ inputCurveOptimizer plugin loaded successfully")
                    except Exception as e:
                        self.log_message(f"❌ Failed to load inputCurveOptimizer: {str(e)}")
                
                # 상태 새로고침
                self.refresh_plugin_status()
            else:
                self.log_message("Maya environment not available")
                
        except Exception as e:
            self.log_message(f"Error during manual plugin loading: {str(e)}")
    
    def save_log(self):
        """로그를 파일로 저장"""
        try:
            from PySide2.QtWidgets import QFileDialog
            import os
            import datetime
            
            # 기본 파일명 생성
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"offset_curve_deformer_log_{timestamp}.txt"
            
            # 파일 저장 다이얼로그
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Log File", 
                default_filename, 
                "Text Files (*.txt);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                
                self.log_message(f"✅ Log saved to: {file_path}")
                
        except Exception as e:
            self.log_message(f"❌ Error saving log: {str(e)}")
    
    def log_message(self, message):
        """로그 메시지 추가"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # 스크롤을 맨 아래로
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def create_workflow_tab(self):
        """워크플로우 탭 생성"""
        workflow_widget = QWidget()
        workflow_layout = QVBoxLayout(workflow_widget)
        
        # 워크플로우 제목
        title_label = QLabel("🚀 통합 워크플로우")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        workflow_layout.addWidget(title_label)
        
        # 워크플로우 설명
        desc_label = QLabel("inputCurveOptimizer와 offsetCurveDeformer를 통합하여 사용하는 워크플로우입니다.")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("margin: 5px; color: #666;")
        workflow_layout.addWidget(desc_label)
        
        # 워크플로우 그룹
        workflow_group = QGroupBox("📋 워크플로우 단계")
        workflow_group_layout = QVBoxLayout(workflow_group)
        
        # 1단계: 곡선 생성
        step1_group = QGroupBox("1단계: 곡선 생성 (inputCurveOptimizer)")
        step1_layout = QFormLayout(step1_group)
        
        self.mesh_input = QLineEdit()
        self.mesh_input.setPlaceholderText("메시 이름을 입력하거나 선택된 오브젝트 사용")
        step1_layout.addRow("메시:", self.mesh_input)
        
        self.optimization_mode_combo = QComboBox()
        self.optimization_mode_combo.addItems(["adaptive", "uniform", "curvature_based"])
        step1_layout.addRow("최적화 모드:", self.optimization_mode_combo)
        
        self.curvature_threshold_spin = QDoubleSpinBox()
        self.curvature_threshold_spin.setRange(0.001, 1.0)
        self.curvature_threshold_spin.setValue(0.1)
        self.curvature_threshold_spin.setSingleStep(0.01)
        step1_layout.addRow("곡률 임계값:", self.curvature_threshold_spin)
        
        self.max_control_points_spin = QSpinBox()
        self.max_control_points_spin.setRange(10, 100)
        self.max_control_points_spin.setValue(30)
        step1_layout.addRow("최대 제어점 수:", self.max_control_points_spin)
        
        self.generate_curve_btn = QPushButton("곡선 생성")
        self.generate_curve_btn.clicked.connect(self.generate_curve_from_mesh)
        step1_layout.addRow("", self.generate_curve_btn)
        
        workflow_group_layout.addWidget(step1_group)
        
        # 2단계: 디포머 적용
        step2_group = QGroupBox("2단계: 디포머 적용 (offsetCurveDeformer)")
        step2_layout = QFormLayout(step2_group)
        
        self.curve_input = QLineEdit()
        self.curve_input.setPlaceholderText("생성된 곡선 이름")
        step2_layout.addRow("곡선:", self.curve_input)
        
        self.workflow_offset_mode_combo = QComboBox()
        self.workflow_offset_mode_combo.addItems(["arc", "bspline"])
        step2_layout.addRow("오프셋 모드:", self.workflow_offset_mode_combo)
        
        self.workflow_falloff_spin = QDoubleSpinBox()
        self.workflow_falloff_spin.setRange(0.001, 100.0)
        self.workflow_falloff_spin.setValue(2.0)
        self.workflow_falloff_spin.setSingleStep(0.1)
        step2_layout.addRow("영향 반경:", self.workflow_falloff_spin)
        
        self.workflow_max_influences_spin = QSpinBox()
        self.workflow_max_influences_spin.setRange(1, 50)
        self.workflow_max_influences_spin.setValue(15)
        step2_layout.addRow("최대 영향 수:", self.workflow_max_influences_spin)
        
        self.apply_deformer_btn = QPushButton("디포머 적용")
        self.apply_deformer_btn.clicked.connect(self.apply_deformer_workflow)
        step2_layout.addRow("", self.apply_deformer_btn)
        
        workflow_group_layout.addWidget(step2_group)
        
        # 3단계: 고급 설정
        step3_group = QGroupBox("3단계: 고급 설정")
        step3_layout = QFormLayout(step3_group)
        
        self.volume_strength_spin = QDoubleSpinBox()
        self.volume_strength_spin.setRange(0.0, 5.0)
        self.volume_strength_spin.setValue(1.5)
        self.volume_strength_spin.setSingleStep(0.1)
        step3_layout.addRow("볼륨 보존:", self.volume_strength_spin)
        
        self.slide_effect_spin = QDoubleSpinBox()
        self.slide_effect_spin.setRange(-2.0, 2.0)
        self.slide_effect_spin.setValue(0.3)
        self.slide_effect_spin.setSingleStep(0.1)
        step3_layout.addRow("슬라이딩 효과:", self.slide_effect_spin)
        
        self.rotation_dist_spin = QDoubleSpinBox()
        self.rotation_dist_spin.setRange(0.0, 2.0)
        self.rotation_dist_spin.setValue(1.2)
        self.rotation_dist_spin.setSingleStep(0.1)
        step3_layout.addRow("회전 분포:", self.rotation_dist_spin)
        
        self.scale_dist_spin = QDoubleSpinBox()
        self.scale_dist_spin.setRange(0.0, 2.0)
        self.scale_dist_spin.setValue(0.8)
        self.scale_dist_spin.setSingleStep(0.1)
        step3_layout.addRow("스케일 분포:", self.scale_dist_spin)
        
        self.twist_dist_spin = QDoubleSpinBox()
        self.twist_dist_spin.setRange(0.0, 2.0)
        self.twist_dist_spin.setValue(1.0)
        self.twist_dist_spin.setSingleStep(0.1)
        step3_layout.addRow("트위스트 분포:", self.twist_dist_spin)
        
        self.apply_advanced_btn = QPushButton("고급 설정 적용")
        self.apply_advanced_btn.clicked.connect(self.apply_advanced_settings)
        step3_layout.addRow("", self.apply_advanced_btn)
        
        workflow_group_layout.addWidget(step3_group)
        
        # 워크플로우 실행 버튼
        workflow_buttons_layout = QHBoxLayout()
        
        self.run_full_workflow_btn = QPushButton("🚀 전체 워크플로우 실행")
        self.run_full_workflow_btn.setStyleSheet("font-weight: bold; padding: 10px;")
        self.run_full_workflow_btn.clicked.connect(self.run_full_workflow)
        workflow_buttons_layout.addWidget(self.run_full_workflow_btn)
        
        self.test_workflow_btn = QPushButton("🧪 워크플로우 테스트")
        self.test_workflow_btn.clicked.connect(self.test_workflow)
        workflow_buttons_layout.addWidget(self.test_workflow_btn)
        
        self.cleanup_workflow_btn = QPushButton("🧹 정리")
        self.cleanup_workflow_btn.clicked.connect(self.cleanup_workflow)
        workflow_buttons_layout.addWidget(self.cleanup_workflow_btn)
        
        workflow_group_layout.addLayout(workflow_buttons_layout)
        
        # 상태 표시
        self.workflow_status_label = QLabel("워크플로우 상태: 대기 중")
        self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;")
        workflow_group_layout.addWidget(self.workflow_status_label)
        
        workflow_layout.addWidget(workflow_group)
        
        # 탭에 추가
        self.tab_widget.addTab(workflow_widget, "🚀 워크플로우")

    def generate_curve_from_mesh(self):
        """메시에서 곡선 생성"""
        try:
            if not hasattr(self, 'curve_optimizer') or not self.curve_optimizer:
                self.log_message("inputCurveOptimizer 래퍼를 사용할 수 없습니다")
                return
            
            # 메시 이름 가져오기
            mesh_name = self.mesh_input.text().strip()
            if not mesh_name:
                # 선택된 오브젝트 사용
                selection = cmds.ls(selection=True)
                if not selection:
                    self.log_message("메시를 선택하거나 이름을 입력해주세요")
                    return
                mesh_name = selection[0]
                self.mesh_input.setText(mesh_name)
            
            # 곡선 생성
            result_curve = self.curve_optimizer.workflow_mesh_to_curve(
                mesh_name=mesh_name,
                optimization_mode=self.optimization_mode_combo.currentText(),
                curvature_threshold=self.curvature_threshold_spin.value(),
                max_control_points=self.max_control_points_spin.value()
            )
            
            if result_curve:
                self.curve_input.setText(result_curve)
                self.workflow_status_label.setText(f"워크플로우 상태: 곡선 생성 완료 - {result_curve}")
                self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724;")
                self.log_message(f"곡선 생성 성공: {result_curve}")
            else:
                self.workflow_status_label.setText("워크플로우 상태: 곡선 생성 실패")
                self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;")
                self.log_message("곡선 생성 실패")
                
        except Exception as e:
            self.log_message(f"곡선 생성 중 오류: {e}")
            self.workflow_status_label.setText(f"워크플로우 상태: 오류 - {str(e)}")
            self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;")

    def apply_deformer_workflow(self):
        """워크플로우를 통한 디포머 적용"""
        try:
            if not hasattr(self, 'offset_deformer') or not self.offset_deformer:
                self.log_message("offsetCurveDeformer 래퍼를 사용할 수 없습니다")
                return
            
            # 입력값 가져오기
            mesh_name = self.mesh_input.text().strip()
            curve_name = self.curve_input.text().strip()
            
            if not mesh_name or not curve_name:
                self.log_message("메시와 곡선 이름을 모두 입력해주세요")
                return
            
            # 디포머 생성 및 바인딩
            deformer_name = self.offset_deformer.workflow_create_and_bind(
                mesh_name=mesh_name,
                curve_names=[curve_name],
                offset_mode=self.workflow_offset_mode_combo.currentText(),
                falloff_radius=self.workflow_falloff_spin.value(),
                max_influences=self.workflow_max_influences_spin.value()
            )
            
            if deformer_name:
                self.workflow_status_label.setText(f"워크플로우 상태: 디포머 적용 완료 - {deformer_name}")
                self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724;")
                self.log_message(f"디포머 적용 성공: {deformer_name}")
                
                # 고급 설정 버튼 활성화
                self.apply_advanced_btn.setEnabled(True)
            else:
                self.workflow_status_label.setText("워크플로우 상태: 디포머 적용 실패")
                self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;")
                self.log_message("디포머 적용 실패")
                
        except Exception as e:
            self.log_message(f"디포머 적용 중 오류: {e}")
            self.workflow_status_label.setText(f"워크플로우 상태: 오류 - {str(e)}")
            self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;")

    def apply_advanced_settings(self):
        """고급 설정 적용"""
        try:
            if not hasattr(self, 'offset_deformer') or not self.offset_deformer:
                self.log_message("offsetCurveDeformer 래퍼를 사용할 수 없습니다")
                return
            
            # 디포머 이름 찾기
            mesh_name = self.mesh_input.text().strip()
            deformer_name = f"{mesh_name}_offsetDeformer"
            
            if not cmds.objExists(deformer_name):
                self.log_message(f"디포머를 찾을 수 없습니다: {deformer_name}")
                return
            
            # 고급 설정 적용
            success = self.offset_deformer.workflow_advanced_deformation(
                deformer_name=deformer_name,
                volume_strength=self.volume_strength_spin.value(),
                slide_effect=self.slide_effect_spin.value(),
                rotation_dist=self.rotation_dist_spin.value(),
                scale_dist=self.scale_dist_spin.value(),
                twist_dist=self.twist_dist_spin.value()
            )
            
            if success:
                self.workflow_status_label.setText("워크플로우 상태: 고급 설정 적용 완료")
                self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724;")
                self.log_message("고급 설정 적용 완료")
            else:
                self.workflow_status_label.setText("워크플로우 상태: 고급 설정 적용 실패")
                self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;")
                self.log_message("고급 설정 적용 실패")
                
        except Exception as e:
            self.log_message(f"고급 설정 적용 중 오류: {e}")
            self.workflow_status_label.setText(f"워크플로우 상태: 오류 - {str(e)}")
            self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;")

    def run_full_workflow(self):
        """전체 워크플로우 실행"""
        try:
            self.log_message("전체 워크플로우 실행 시작")
            
            # 1단계: 곡선 생성
            self.generate_curve_from_mesh()
            
            # 2단계: 디포머 적용
            self.apply_deformer_workflow()
            
            # 3단계: 고급 설정
            self.apply_advanced_settings()
            
            self.workflow_status_label.setText("워크플로우 상태: 전체 워크플로우 완료!")
            self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460;")
            self.log_message("전체 워크플로우 완료")
            
        except Exception as e:
            self.log_message(f"전체 워크플로우 실행 중 오류: {e}")
            self.workflow_status_label.setText(f"워크플로우 상태: 오류 - {str(e)}")
            self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;")

    def test_workflow(self):
        """워크플로우 테스트 실행"""
        try:
            self.log_message("워크플로우 테스트 시작")
            
            # 테스트 스크립트 실행
            import subprocess
            import sys
            
            test_script = os.path.join(os.path.dirname(__file__), "..", "test_integrated_workflow.py")
            
            if os.path.exists(test_script):
                result = subprocess.run([sys.executable, test_script], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.workflow_status_label.setText("워크플로우 상태: 테스트 성공!")
                    self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724;")
                    self.log_message("워크플로우 테스트 성공")
                else:
                    self.workflow_status_label.setText("워크플로우 상태: 테스트 실패")
                    self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24;")
                    self.log_message(f"워크플로우 테스트 실패: {result.stderr}")
            else:
                self.log_message("테스트 스크립트를 찾을 수 없습니다")
                
        except Exception as e:
            self.log_message(f"워크플로우 테스트 중 오류: {e}")

    def cleanup_workflow(self):
        """워크플로우 정리"""
        try:
            self.log_message("워크플로우 정리 시작")
            
            # 입력 필드 초기화
            self.mesh_input.clear()
            self.curve_input.clear()
            
            # 상태 초기화
            self.workflow_status_label.setText("워크플로우 상태: 대기 중")
            self.workflow_status_label.setStyleSheet("margin: 10px; padding: 5px; background-color: #f0f0f0; border: 1px solid #ccc;")
            
            # 고급 설정 버튼 비활성화
            self.apply_advanced_btn.setEnabled(False)
            
            self.log_message("워크플로우 정리 완료")
            
        except Exception as e:
            self.log_message(f"워크플로우 정리 중 오류: {e}")

if __name__ == "__main__":
    # Maya에서 실행할 때
    try:
        import maya.cmds as cmds
        window = MayaMainWindow()
        window.show()
    except ImportError:
        # 독립 실행
        from PySide2.QtWidgets import QApplication
        app = QApplication(sys.argv)
        window = MayaMainWindow()
        window.show()
        sys.exit(app.exec_())
