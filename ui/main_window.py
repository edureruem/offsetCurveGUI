#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메인 윈도우 UI - Maya 2020 호환 PySide2 버전
offsetCurveDeformer와 inputCurveOptimizer 통합 워크플로우를 위한 메인 인터페이스
Maya의 UI 스타일과 통합성을 고려하여 설계
"""

import sys
import os
from typing import Dict, Any, Optional
import time

# Maya 환경 확인 및 PySide2 임포트
try:
    import maya.cmds as cmds
    import maya.OpenMaya as om
    MAYA_AVAILABLE = True
    
    # Maya 2020에서 제공하는 PySide2 사용
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
        from PySide2.QtCore import Qt, QTimer, Signal
        from PySide2.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                     QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                                     QProgressBar, QTabWidget, QGroupBox, QSlider, 
                                     QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
                                     QTextEdit, QListWidget, QMessageBox, QFileDialog,
                                     QSplitter, QFrame, QScrollArea)
        from PySide2.QtGui import QFont, QPalette, QColor, QIcon
    except ImportError:
        print("Maya에서 PySide2를 찾을 수 없습니다.")
        MAYA_AVAILABLE = False
        
except ImportError:
    MAYA_AVAILABLE = False
    print("Maya 환경이 감지되지 않았습니다.")

from src.integratedWorkflow.workflow_manager import WorkflowManager

class MayaStyleSheet:
    """Maya 스타일과 유사한 스타일시트"""
    
    @staticmethod
    def get_stylesheet():
        return """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
            font-family: "Arial", sans-serif;
            font-size: 9pt;
        }
        
        QGroupBox {
            border: 1px solid #555555;
            border-radius: 3px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: #cccccc;
        }
        
        QPushButton {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 5px 15px;
            min-height: 20px;
            color: #ffffff;
        }
        
        QPushButton:hover {
            background-color: #505050;
            border-color: #666666;
        }
        
        QPushButton:pressed {
            background-color: #303030;
        }
        
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #666666;
        }
        
        QProgressBar {
            border: 1px solid #555555;
            border-radius: 3px;
            text-align: center;
            background-color: #404040;
        }
        
        QProgressBar::chunk {
            background-color: #0078d4;
            border-radius: 2px;
        }
        
        QTabWidget::pane {
            border: 1px solid #555555;
            background-color: #2b2b2b;
        }
        
        QTabBar::tab {
            background-color: #404040;
            border: 1px solid #555555;
            padding: 8px 16px;
            margin-right: 2px;
            color: #ffffff;
        }
        
        QTabBar::tab:selected {
            background-color: #0078d4;
            border-color: #0078d4;
        }
        
        QTabBar::tab:hover:!selected {
            background-color: #505050;
        }
        
        QSlider::groove:horizontal {
            border: 1px solid #555555;
            height: 8px;
            background-color: #404040;
            border-radius: 4px;
        }
        
        QSlider::handle:horizontal {
            background-color: #0078d4;
            border: 1px solid #0078d4;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
        
        QSpinBox, QDoubleSpinBox {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 3px;
            color: #ffffff;
        }
        
        QComboBox {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 3px;
            color: #ffffff;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #ffffff;
        }
        
        QCheckBox {
            spacing: 8px;
            color: #ffffff;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #555555;
            background-color: #404040;
        }
        
        QCheckBox::indicator:checked {
            background-color: #0078d4;
            border-color: #0078d4;
        }
        
        QTextEdit {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 3px;
            color: #ffffff;
        }
        
        QListWidget {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 3px;
            color: #ffffff;
        }
        
        QListWidget::item:selected {
            background-color: #0078d4;
        }
        
        QListWidget::item:hover:!selected {
            background-color: #505050;
        }
        """

class MainWindow(QMainWindow):
    """메인 윈도우 클래스 - Maya 호환"""
    
    # 시그널 정의
    workflow_started = Signal()
    workflow_completed = Signal()
    workflow_failed = Signal(str)
    
    def __init__(self, workflow_manager: WorkflowManager):
        super().__init__()
        
        self.workflow_manager = workflow_manager
        self.update_timer = None
        
        # UI 초기화
        self.setup_ui()
        self.setup_connections()
        
        # 상태 업데이트 타이머 시작
        self.start_status_updates()
        
        # Maya 스타일 적용
        self.setStyleSheet(MayaStyleSheet.get_stylesheet())
    
    def setup_ui(self):
        """UI 컴포넌트 설정"""
        self.setWindowTitle("Offset Curve Deformer & Input Curve Optimizer - Maya 2020")
        self.setGeometry(100, 100, 900, 700)
        
        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 제목 섹션
        self.setup_title_section(main_layout)
        
        # Maya 씬 정보 섹션
        self.setup_maya_scene_section(main_layout)
        
        # 워크플로우 진행 상황 섹션
        self.setup_workflow_progress_section(main_layout)
        
        # 워크플로우 제어 섹션
        self.setup_workflow_controls_section(main_layout)
        
        # 파라미터 설정 섹션 (탭 위젯)
        self.setup_parameters_section(main_layout)
        
        # 로그 및 상태 표시 섹션
        self.setup_log_section(main_layout)
    
    def setup_title_section(self, parent_layout):
        """제목 섹션 설정"""
        title_frame = QFrame()
        title_layout = QHBoxLayout(title_frame)
        
        # 제목 라벨
        title_label = QLabel("Offset Curve Deformer & Input Curve Optimizer")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #0078d4;")
        
        # Maya 상태 표시
        maya_status = "Maya 2020" if MAYA_AVAILABLE else "독립 실행 모드"
        status_label = QLabel(f"({maya_status})")
        status_label.setStyleSheet("color: #888888; font-size: 10pt;")
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(status_label)
        
        parent_layout.addWidget(title_frame)
    
    def setup_maya_scene_section(self, parent_layout):
        """Maya 씬 정보 섹션 설정"""
        scene_group = QGroupBox("Maya 씬 정보")
        scene_layout = QGridLayout(scene_group)
        
        # 씬 이름
        scene_layout.addWidget(QLabel("씬 이름:"), 0, 0)
        self.scene_name_label = QLabel("로딩 중...")
        scene_layout.addWidget(self.scene_name_label, 0, 1)
        
        # 씬 내 커브 수
        scene_layout.addWidget(QLabel("씬 내 커브:"), 1, 0)
        self.curves_count_label = QLabel("0개")
        scene_layout.addWidget(self.curves_count_label, 1, 1)
        
        # 선택된 커브
        scene_layout.addWidget(QLabel("선택된 커브:"), 2, 0)
        self.selected_curves_label = QLabel("없음")
        scene_layout.addWidget(self.selected_curves_label, 2, 1)
        
        # 새로고침 버튼
        refresh_button = QPushButton("씬 정보 새로고침")
        refresh_button.clicked.connect(self.refresh_maya_scene_info)
        scene_layout.addWidget(refresh_button, 3, 0, 1, 2)
        
        parent_layout.addWidget(scene_group)
    
    def setup_workflow_progress_section(self, parent_layout):
        """워크플로우 진행 상황 섹션 설정"""
        progress_group = QGroupBox("워크플로우 진행 상황")
        progress_layout = QVBoxLayout(progress_group)
        
        # 전체 진행률 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        # 현재 단계 표시
        self.current_step_label = QLabel("현재 단계: 대기 중")
        progress_layout.addWidget(self.current_step_label)
        
        # 전체 상태 표시
        self.status_label = QLabel("상태: 대기 중")
        progress_layout.addWidget(self.status_label)
        
        parent_layout.addWidget(progress_group)
    
    def setup_workflow_controls_section(self, parent_layout):
        """워크플로우 제어 섹션 설정"""
        controls_group = QGroupBox("워크플로우 제어")
        controls_layout = QHBoxLayout(controls_group)
        
        # 제어 버튼들
        self.start_button = QPushButton("워크플로우 시작")
        self.start_button.clicked.connect(self.start_workflow)
        
        self.execute_button = QPushButton("현재 단계 실행")
        self.execute_button.clicked.connect(self.execute_current_step)
        self.execute_button.setEnabled(False)
        
        self.next_button = QPushButton("다음 단계")
        self.next_button.clicked.connect(self.next_step)
        self.next_button.setEnabled(False)
        
        self.reset_button = QPushButton("워크플로우 재설정")
        self.reset_button.clicked.connect(self.reset_workflow)
        
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.execute_button)
        controls_layout.addWidget(self.next_button)
        controls_layout.addWidget(self.reset_button)
        controls_layout.addStretch()
        
        parent_layout.addWidget(controls_group)
    
    def setup_parameters_section(self, parent_layout):
        """파라미터 설정 섹션 설정"""
        # 탭 위젯 생성
        self.param_tabs = QTabWidget()
        
        # 기본 설정 탭
        basic_tab = self.create_basic_parameters_tab()
        self.param_tabs.addTab(basic_tab, "기본 설정")
        
        # 고급 옵션 탭
        advanced_tab = self.create_advanced_parameters_tab()
        self.param_tabs.addTab(advanced_tab, "고급 옵션")
        
        # 컨텍스트 인식 도구 탭
        context_tab = self.create_context_tools_tab()
        self.param_tabs.addTab(context_tab, "컨텍스트 인식 도구")
        
        parent_layout.addWidget(self.param_tabs)
    
    def create_basic_parameters_tab(self):
        """기본 파라미터 탭 생성"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Input Curve Optimizer 기본 설정
        optimizer_group = QGroupBox("Input Curve Optimizer 기본 설정")
        optimizer_layout = QGridLayout(optimizer_group)
        
        # 최적화 수준
        optimizer_layout.addWidget(QLabel("최적화 수준:"), 0, 0)
        self.optimization_level_combo = QComboBox()
        self.optimization_level_combo.addItems(["낮음", "보통", "높음"])
        self.optimization_level_combo.setCurrentText("보통")
        optimizer_layout.addWidget(self.optimization_level_combo, 0, 1)
        
        # 부드러움 계수
        optimizer_layout.addWidget(QLabel("부드러움 계수:"), 1, 0)
        self.smoothness_slider = QSlider(Qt.Horizontal)
        self.smoothness_slider.setRange(0, 100)
        self.smoothness_slider.setValue(50)
        optimizer_layout.addWidget(self.smoothness_slider, 1, 1)
        
        # 복잡도 감소
        optimizer_layout.addWidget(QLabel("복잡도 감소:"), 2, 0)
        self.complexity_slider = QSlider(Qt.Horizontal)
        self.complexity_slider.setRange(0, 100)
        self.complexity_slider.setValue(30)
        optimizer_layout.addWidget(self.complexity_slider, 2, 1)
        
        layout.addWidget(optimizer_group)
        
        # Offset Curve Deformer 기본 설정
        deformer_group = QGroupBox("Offset Curve Deformer 기본 설정")
        deformer_layout = QGridLayout(deformer_group)
        
        # 오프셋 거리
        deformer_layout.addWidget(QLabel("오프셋 거리:"), 0, 0)
        self.offset_distance_spin = QDoubleSpinBox()
        self.offset_distance_spin.setRange(0.01, 100.0)
        self.offset_distance_spin.setValue(1.0)
        self.offset_distance_spin.setSuffix(" units")
        deformer_layout.addWidget(self.offset_distance_spin, 0, 1)
        
        # 오프셋 방향
        deformer_layout.addWidget(QLabel("오프셋 방향:"), 1, 0)
        self.offset_direction_combo = QComboBox()
        self.offset_direction_combo.addItems(["양쪽", "안쪽", "바깥쪽"])
        deformer_layout.addWidget(self.offset_direction_combo, 1, 1)
        
        # 모서리 처리
        deformer_layout.addWidget(QLabel("모서리 처리:"), 2, 0)
        self.corner_handling_combo = QComboBox()
        self.corner_handling_combo.addItems(["둥글게", "각진 모양", "부드럽게"])
        deformer_layout.addWidget(self.corner_handling_combo, 2, 1)
        
        layout.addWidget(deformer_group)
        
        # 적용 버튼
        apply_button = QPushButton("설정 적용")
        apply_button.clicked.connect(self.apply_basic_parameters)
        layout.addWidget(apply_button)
        
        layout.addStretch()
        return tab_widget
    
    def create_advanced_parameters_tab(self):
        """고급 파라미터 탭 생성"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # Input Curve Optimizer 고급 옵션
        optimizer_advanced_group = QGroupBox("Input Curve Optimizer 고급 옵션")
        optimizer_advanced_layout = QGridLayout(optimizer_advanced_group)
        
        # 곡률 임계값
        optimizer_advanced_layout.addWidget(QLabel("곡률 임계값:"), 0, 0)
        self.curvature_threshold_spin = QDoubleSpinBox()
        self.curvature_threshold_spin.setRange(0.001, 1.0)
        self.curvature_threshold_spin.setValue(0.1)
        self.curvature_threshold_spin.setDecimals(3)
        optimizer_advanced_layout.addWidget(self.curvature_threshold_spin, 0, 1)
        
        # 적응형 샘플링
        self.adaptive_sampling_check = QCheckBox("적응형 샘플링")
        self.adaptive_sampling_check.setChecked(True)
        optimizer_advanced_layout.addWidget(self.adaptive_sampling_check, 1, 0, 1, 2)
        
        # 특징 보존
        optimizer_advanced_layout.addWidget(QLabel("특징 보존 수준:"), 2, 0)
        self.feature_preservation_slider = QSlider(Qt.Horizontal)
        self.feature_preservation_slider.setRange(0, 100)
        self.feature_preservation_slider.setValue(80)
        optimizer_advanced_layout.addWidget(self.feature_preservation_slider, 2, 1)
        
        layout.addWidget(optimizer_advanced_group)
        
        # Offset Curve Deformer 고급 옵션
        deformer_advanced_group = QGroupBox("Offset Curve Deformer 고급 옵션")
        deformer_advanced_layout = QGridLayout(deformer_advanced_group)
        
        # 허용 오차
        deformer_advanced_layout.addWidget(QLabel("허용 오차:"), 0, 0)
        self.tolerance_spin = QDoubleSpinBox()
        self.tolerance_spin.setRange(0.001, 1.0)
        self.tolerance_spin.setValue(0.01)
        self.tolerance_spin.setDecimals(3)
        deformer_advanced_layout.addWidget(self.tolerance_spin, 0, 1)
        
        # 최대 편차
        deformer_advanced_layout.addWidget(QLabel("최대 편차:"), 1, 0)
        self.max_deviation_spin = QDoubleSpinBox()
        self.max_deviation_spin.setRange(0.01, 10.0)
        self.max_deviation_spin.setValue(0.1)
        self.max_deviation_spin.setDecimals(2)
        deformer_advanced_layout.addWidget(self.max_deviation_spin, 1, 1)
        
        # 부드러운 전환
        self.smooth_transitions_check = QCheckBox("부드러운 전환")
        self.smooth_transitions_check.setChecked(True)
        deformer_advanced_layout.addWidget(self.smooth_transitions_check, 2, 0, 1, 2)
        
        layout.addWidget(deformer_advanced_group)
        
        # 성능 설정
        performance_group = QGroupBox("성능 설정")
        performance_layout = QGridLayout(performance_group)
        
        # 병렬 처리
        self.parallel_processing_check = QCheckBox("병렬 처리")
        self.parallel_processing_check.setChecked(True)
        performance_layout.addWidget(self.parallel_processing_check, 0, 0, 1, 2)
        
        # 스레드 수
        performance_layout.addWidget(QLabel("스레드 수:"), 1, 0)
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setRange(1, 16)
        self.thread_count_spin.setValue(4)
        performance_layout.addWidget(self.thread_count_spin, 1, 1)
        
        layout.addWidget(performance_group)
        
        # 적용 버튼
        apply_advanced_button = QPushButton("고급 설정 적용")
        apply_advanced_button.clicked.connect(self.apply_advanced_parameters)
        layout.addWidget(apply_advanced_button)
        
        layout.addStretch()
        return tab_widget
    
    def create_context_tools_tab(self):
        """컨텍스트 인식 도구 탭 생성"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        
        # 커브 특성 분석
        analysis_group = QGroupBox("커브 특성 분석")
        analysis_layout = QVBoxLayout(analysis_group)
        
        # 분석 버튼
        analyze_button = QPushButton("선택된 커브 분석")
        analyze_button.clicked.connect(self.analyze_selected_curves)
        analysis_layout.addWidget(analyze_button)
        
        # 분석 결과 표시
        self.analysis_text = QTextEdit()
        self.analysis_text.setMaximumHeight(150)
        self.analysis_text.setPlaceholderText("커브를 선택하고 분석 버튼을 클릭하세요...")
        analysis_layout.addWidget(self.analysis_text)
        
        layout.addWidget(analysis_group)
        
        # 자동 설정 제안
        suggestions_group = QGroupBox("자동 설정 제안")
        suggestions_layout = QVBoxLayout(suggestions_group)
        
        # 제안 표시
        self.suggestions_text = QTextEdit()
        self.suggestions_text.setMaximumHeight(150)
        self.suggestions_text.setPlaceholderText("분석 후 자동 설정 제안이 여기에 표시됩니다...")
        suggestions_layout.addWidget(self.suggestions_text)
        
        # 제안 적용 버튼
        apply_suggestions_button = QPushButton("제안된 설정 적용")
        apply_suggestions_button.clicked.connect(self.apply_suggested_settings)
        suggestions_layout.addWidget(apply_suggestions_button)
        
        layout.addWidget(suggestions_group)
        
        layout.addStretch()
        return tab_widget
    
    def setup_log_section(self, parent_layout):
        """로그 및 상태 표시 섹션 설정"""
        log_group = QGroupBox("로그 및 상태")
        log_layout = QVBoxLayout(log_group)
        
        # 로그 텍스트 에디터
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(120)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        # 로그 제어 버튼
        log_controls_layout = QHBoxLayout()
        
        clear_log_button = QPushButton("로그 지우기")
        clear_log_button.clicked.connect(self.clear_log)
        log_controls_layout.addWidget(clear_log_button)
        
        save_log_button = QPushButton("로그 저장")
        save_log_button.clicked.connect(self.save_log)
        log_controls_layout.addWidget(save_log_button)
        
        log_controls_layout.addStretch()
        log_layout.addLayout(log_controls_layout)
        
        parent_layout.addWidget(log_group)
    
    def setup_connections(self):
        """시그널-슬롯 연결 설정"""
        # 워크플로우 시그널 연결
        self.workflow_started.connect(self.on_workflow_started)
        self.workflow_completed.connect(self.on_workflow_completed)
        self.workflow_failed.connect(self.on_workflow_failed)
    
    def start_status_updates(self):
        """상태 업데이트 타이머 시작"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui_status)
        self.update_timer.start(100)  # 100ms마다 업데이트
    
    def update_ui_status(self):
        """UI 상태 업데이트"""
        try:
            # 워크플로우 상태 가져오기
            status = self.workflow_manager.get_workflow_status()
            
            # 진행률 업데이트
            total_steps = status['total_steps']
            current_step = status['current_step']
            if total_steps > 0:
                progress = (current_step / total_steps) * 100
                self.progress_bar.setValue(int(progress))
            
            # 현재 단계 표시
            if status['current_step'] < len(status['steps']):
                current_step_info = status['steps'][status['current_step']]
                self.current_step_label.setText(f"현재 단계: {current_step_info['name']}")
            
            # 전체 상태 표시
            self.status_label.setText(f"상태: {status['status']}")
            
            # Maya 씬 정보 업데이트
            if MAYA_AVAILABLE:
                scene_info = self.workflow_manager.get_maya_scene_info()
                if 'error' not in scene_info:
                    self.scene_name_label.setText(scene_info.get('scene_name', 'untitled'))
                    self.curves_count_label.setText(f"{len(scene_info.get('curves_in_scene', []))}개")
                    
                    selected = scene_info.get('selected_objects', [])
                    if selected:
                        self.selected_curves_label.setText(f"{len(selected)}개 선택됨")
                    else:
                        self.selected_curves_label.setText("없음")
            
        except Exception as e:
            self.log_message(f"상태 업데이트 오류: {e}")
    
    def refresh_maya_scene_info(self):
        """Maya 씬 정보 새로고침"""
        if MAYA_AVAILABLE:
            try:
                scene_info = self.workflow_manager.get_maya_scene_info()
                if 'error' not in scene_info:
                    self.log_message("Maya 씬 정보가 새로고침되었습니다.")
                else:
                    self.log_message(f"씬 정보 새로고침 실패: {scene_info['error']}")
            except Exception as e:
                self.log_message(f"씬 정보 새로고침 오류: {e}")
        else:
            self.log_message("Maya 환경이 아닙니다.")
    
    def start_workflow(self):
        """워크플로우 시작"""
        try:
            if self.workflow_manager.start_workflow():
                self.log_message("워크플로우가 시작되었습니다.")
                self.workflow_started.emit()
                self.update_button_states("running")
            else:
                self.log_message("워크플로우 시작에 실패했습니다.")
        except Exception as e:
            self.log_message(f"워크플로우 시작 오류: {e}")
    
    def execute_current_step(self):
        """현재 단계 실행"""
        try:
            if self.workflow_manager.execute_current_step():
                self.log_message("현재 단계가 실행되었습니다.")
                self.update_button_states("step_completed")
            else:
                self.log_message("현재 단계 실행에 실패했습니다.")
        except Exception as e:
            self.log_message(f"단계 실행 오류: {e}")
    
    def next_step(self):
        """다음 단계로 진행"""
        try:
            if self.workflow_manager.next_step():
                self.log_message("다음 단계로 진행되었습니다.")
                self.update_button_states("running")
            else:
                self.log_message("워크플로우가 완료되었습니다.")
                self.workflow_completed.emit()
                self.update_button_states("completed")
        except Exception as e:
            self.log_message(f"다음 단계 진행 오류: {e}")
    
    def reset_workflow(self):
        """워크플로우 재설정"""
        try:
            self.workflow_manager.reset_workflow()
            self.log_message("워크플로우가 재설정되었습니다.")
            self.update_button_states("idle")
        except Exception as e:
            self.log_message(f"워크플로우 재설정 오류: {e}")
    
    def update_button_states(self, status):
        """버튼 상태 업데이트"""
        if status == "idle":
            self.start_button.setEnabled(True)
            self.execute_button.setEnabled(False)
            self.next_button.setEnabled(False)
        elif status == "running":
            self.start_button.setEnabled(False)
            self.execute_button.setEnabled(True)
            self.next_button.setEnabled(False)
        elif status == "step_completed":
            self.start_button.setEnabled(False)
            self.execute_button.setEnabled(False)
            self.next_button.setEnabled(True)
        elif status == "completed":
            self.start_button.setEnabled(True)
            self.execute_button.setEnabled(False)
            self.next_button.setEnabled(False)
    
    def apply_basic_parameters(self):
        """기본 파라미터 적용"""
        try:
            # Input Curve Optimizer 파라미터
            optimization_level_map = {"낮음": "low", "보통": "medium", "높음": "high"}
            optimization_level = optimization_level_map.get(self.optimization_level_combo.currentText(), "medium")
            
            smoothness_factor = self.smoothness_slider.value() / 100.0
            complexity_reduction = self.complexity_slider.value() / 100.0
            
            # Offset Curve Deformer 파라미터
            offset_distance = self.offset_distance_spin.value()
            offset_direction_map = {"양쪽": "both", "안쪽": "inside", "바깥쪽": "outside"}
            offset_direction = offset_direction_map.get(self.offset_direction_combo.currentText(), "both")
            
            corner_handling_map = {"둥글게": "round", "각진 모양": "sharp", "부드럽게": "smooth"}
            corner_handling = corner_handling_map.get(self.corner_handling_combo.currentText(), "round")
            
            # 파라미터 업데이트
            self.workflow_manager.update_step_parameters(1, {
                "optimization_level": optimization_level,
                "smoothing_factor": smoothness_factor,
                "complexity_reduction": complexity_reduction
            })
            
            self.workflow_manager.update_step_parameters(2, {
                "offset_distance": offset_distance,
                "offset_direction": offset_direction,
                "corner_handling": corner_handling
            })
            
            self.log_message("기본 파라미터가 적용되었습니다.")
            
        except Exception as e:
            self.log_message(f"기본 파라미터 적용 오류: {e}")
    
    def apply_advanced_parameters(self):
        """고급 파라미터 적용"""
        try:
            # Input Curve Optimizer 고급 옵션
            curvature_threshold = self.curvature_threshold_spin.value()
            adaptive_sampling = self.adaptive_sampling_check.isChecked()
            feature_preservation = self.feature_preservation_slider.value() / 100.0
            
            # Offset Curve Deformer 고급 옵션
            tolerance = self.tolerance_spin.value()
            max_deviation = self.max_deviation_spin.value()
            smooth_transitions = self.smooth_transitions_check.isChecked()
            
            # 성능 설정
            parallel_processing = self.parallel_processing_check.isChecked()
            thread_count = self.thread_count_spin.value()
            
            # 파라미터 업데이트
            self.workflow_manager.update_step_parameters(1, {
                "curvature_threshold": curvature_threshold,
                "adaptive_sampling": adaptive_sampling,
                "feature_preservation": feature_preservation
            })
            
            self.workflow_manager.update_step_parameters(2, {
                "tolerance": tolerance,
                "max_deviation": max_deviation,
                "smooth_transitions": smooth_transitions,
                "parallel_processing": parallel_processing,
                "thread_count": thread_count
            })
            
            self.log_message("고급 파라미터가 적용되었습니다.")
            
        except Exception as e:
            self.log_message(f"고급 파라미터 적용 오류: {e}")
    
    def analyze_selected_curves(self):
        """선택된 커브 분석"""
        try:
            if MAYA_AVAILABLE:
                # Maya에서 선택된 커브 가져오기
                selected_curves = cmds.ls(sl=True, long=True)
                if selected_curves:
                    # 워크플로우 매니저에 커브 선택
                    if self.workflow_manager.select_curves_from_maya(selected_curves):
                        # 커브 정보 분석
                        curve_info = []
                        for curve in selected_curves:
                            curve_type = cmds.nodeType(curve)
                            if curve_type == 'nurbsCurve':
                                cv_count = cmds.getAttr(f"{curve}.spans") + cmds.getAttr(f"{curve}.degree")
                                curve_info.append(f"{curve}: NURBS 커브, CV 수: {cv_count}")
                            elif curve_type == 'mesh':
                                vertex_count = cmds.polyEvaluate(curve, v=True)
                                curve_info.append(f"{curve}: 메시, 버텍스 수: {vertex_count}")
                        
                        analysis_text = "선택된 커브 분석 결과:\n\n"
                        analysis_text += "\n".join(curve_info)
                        self.analysis_text.setText(analysis_text)
                        
                        # 자동 설정 제안 생성
                        self.generate_suggestions(selected_curves)
                        
                        self.log_message(f"{len(selected_curves)}개 커브가 분석되었습니다.")
                    else:
                        self.log_message("커브 선택에 실패했습니다.")
                else:
                    self.log_message("Maya에서 커브를 선택해주세요.")
            else:
                self.log_message("Maya 환경이 아닙니다.")
                
        except Exception as e:
            self.log_message(f"커브 분석 오류: {e}")
    
    def generate_suggestions(self, curves):
        """자동 설정 제안 생성"""
        try:
            suggestions = []
            
            # 커브 수에 따른 제안
            if len(curves) > 5:
                suggestions.append("• 많은 커브가 선택되었습니다. 병렬 처리를 활성화하는 것을 권장합니다.")
                suggestions.append("• 스레드 수를 6-8개로 설정하는 것을 권장합니다.")
            
            # 커브 타입에 따른 제안
            nurbs_count = sum(1 for curve in curves if cmds.nodeType(curve) == 'nurbsCurve')
            if nurbs_count > 0:
                suggestions.append("• NURBS 커브가 포함되어 있습니다. 곡률 기반 최적화를 권장합니다.")
            
            # 기본 제안
            suggestions.append("• 최적화 수준: 보통")
            suggestions.append("• 부드러움 계수: 0.5")
            suggestions.append("• 오프셋 거리: 1.0")
            
            suggestions_text = "자동 설정 제안:\n\n" + "\n".join(suggestions)
            self.suggestions_text.setText(suggestions_text)
            
        except Exception as e:
            self.log_message(f"제안 생성 오류: {e}")
    
    def apply_suggested_settings(self):
        """제안된 설정 적용"""
        try:
            # 기본 설정 적용
            self.optimization_level_combo.setCurrentText("보통")
            self.smoothness_slider.setValue(50)
            self.complexity_slider.setValue(30)
            self.offset_distance_spin.setValue(1.0)
            
            # 고급 설정 적용
            self.curvature_threshold_spin.setValue(0.1)
            self.adaptive_sampling_check.setChecked(True)
            self.feature_preservation_slider.setValue(80)
            self.tolerance_spin.setValue(0.01)
            self.max_deviation_spin.setValue(0.1)
            self.smooth_transitions_check.setChecked(True)
            self.parallel_processing_check.setChecked(True)
            self.thread_count_spin.setValue(4)
            
            # 파라미터 적용
            self.apply_basic_parameters()
            self.apply_advanced_parameters()
            
            self.log_message("제안된 설정이 적용되었습니다.")
            
        except Exception as e:
            self.log_message(f"제안된 설정 적용 오류: {e}")
    
    def log_message(self, message: str):
        """로그 메시지 추가"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        
        # 스크롤을 맨 아래로
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def clear_log(self):
        """로그 지우기"""
        self.log_text.clear()
    
    def save_log(self):
        """로그 저장"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "로그 저장", "", "텍스트 파일 (*.txt)"
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.log_message(f"로그가 저장되었습니다: {file_path}")
        except Exception as e:
            self.log_message(f"로그 저장 오류: {e}")
    
    def on_workflow_started(self):
        """워크플로우 시작 시 호출"""
        self.log_message("워크플로우가 시작되었습니다.")
    
    def on_workflow_completed(self):
        """워크플로우 완료 시 호출"""
        self.log_message("워크플로우가 완료되었습니다.")
        self.update_button_states("completed")
    
    def on_workflow_failed(self, error_message: str):
        """워크플로우 실패 시 호출"""
        self.log_message(f"워크플로우가 실패했습니다: {error_message}")
        self.update_button_states("idle")
    
    def closeEvent(self, event):
        """윈도우 닫기 이벤트"""
        if self.update_timer:
            self.update_timer.stop()
        event.accept()

def main():
    """메인 함수 - 독립 실행용"""
    app = QApplication(sys.argv)
    
    # 워크플로우 매니저 생성
    workflow_manager = WorkflowManager()
    
    # 메인 윈도우 생성
    window = MainWindow(workflow_manager)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
