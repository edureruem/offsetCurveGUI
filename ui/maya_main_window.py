#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maya 2020 호환 PySide2 메인 윈도우
간단한 버전으로 offsetCurveGUI의 핵심 기능 구현
"""

import sys
import time
from typing import Dict, Any, List, Tuple, Optional

# Maya 환경 확인
try:
    import maya.cmds as cmds
    import maya.OpenMaya as om
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False

# PySide2 임포트
try:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
except ImportError:
    print("PySide2를 찾을 수 없습니다.")
    sys.exit(1)

class MayaOffsetCurveGUI(QMainWindow):
    """Maya 호환 오프셋 커브 GUI"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_maya_integration()
    
    def setup_ui(self):
        """UI 설정"""
        self.setWindowTitle("Offset Curve Deformer - Maya 2020")
        self.setGeometry(100, 100, 800, 600)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 메인 레이아웃
        layout = QVBoxLayout(central_widget)
        
        # 제목
        title = QLabel("Offset Curve Deformer & Input Curve Optimizer")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0078d4; margin: 10px;")
        layout.addWidget(title)
        
        # Maya 상태
        status_text = "Maya 2020" if MAYA_AVAILABLE else "독립 실행 모드"
        status_label = QLabel(f"상태: {status_text}")
        status_label.setStyleSheet("color: #888888; margin: 5px;")
        layout.addWidget(status_label)
        
        # 씬 정보 그룹
        scene_group = QGroupBox("Maya 씬 정보")
        scene_layout = QGridLayout(scene_group)
        
        self.scene_name_label = QLabel("로딩 중...")
        self.curves_count_label = QLabel("0개")
        self.selected_curves_label = QLabel("없음")
        
        scene_layout.addWidget(QLabel("씬 이름:"), 0, 0)
        scene_layout.addWidget(self.scene_name_label, 0, 1)
        scene_layout.addWidget(QLabel("씬 내 커브:"), 1, 0)
        scene_layout.addWidget(self.curves_count_label, 1, 1)
        scene_layout.addWidget(QLabel("선택된 커브:"), 2, 0)
        scene_layout.addWidget(self.selected_curves_label, 2, 1)
        
        refresh_button = QPushButton("씬 정보 새로고침")
        refresh_button.clicked.connect(self.refresh_scene_info)
        scene_layout.addWidget(refresh_button, 3, 0, 1, 2)
        
        layout.addWidget(scene_group)
        
        # 파라미터 그룹
        params_group = QGroupBox("오프셋 파라미터")
        params_layout = QGridLayout(params_group)
        
        # 오프셋 거리
        params_layout.addWidget(QLabel("오프셋 거리:"), 0, 0)
        self.offset_distance = QDoubleSpinBox()
        self.offset_distance.setRange(0.01, 100.0)
        self.offset_distance.setValue(1.0)
        self.offset_distance.setSuffix(" units")
        params_layout.addWidget(self.offset_distance, 0, 1)
        
        # 오프셋 방향
        params_layout.addWidget(QLabel("오프셋 방향:"), 1, 0)
        self.offset_direction = QComboBox()
        self.offset_direction.addItems(["양쪽", "안쪽", "바깥쪽"])
        params_layout.addWidget(self.offset_direction, 1, 1)
        
        # 최적화 수준
        params_layout.addWidget(QLabel("최적화 수준:"), 2, 0)
        self.optimization_level = QComboBox()
        self.optimization_level.addItems(["낮음", "보통", "높음"])
        self.optimization_level.setCurrentText("보통")
        params_layout.addWidget(self.optimization_level, 2, 1)
        
        layout.addWidget(params_group)
        
        # 제어 버튼들
        controls_layout = QHBoxLayout()
        
        self.create_offset_button = QPushButton("오프셋 커브 생성")
        self.create_offset_button.clicked.connect(self.create_offset_curves)
        controls_layout.addWidget(self.create_offset_button)
        
        self.optimize_button = QPushButton("커브 최적화")
        self.optimize_button.clicked.connect(self.optimize_curves)
        controls_layout.addWidget(self.optimize_button)
        
        self.reset_button = QPushButton("재설정")
        self.reset_button.clicked.connect(self.reset_parameters)
        controls_layout.addWidget(self.reset_button)
        
        layout.addLayout(controls_layout)
        
        # 진행 상황
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # 로그
        log_group = QGroupBox("로그")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        clear_log_button = QPushButton("로그 지우기")
        clear_log_button.clicked.connect(self.clear_log)
        log_layout.addWidget(clear_log_button)
        
        layout.addWidget(log_group)
        
        # Maya 스타일 적용
        self.apply_maya_style()
    
    def apply_maya_style(self):
        """Maya 스타일 적용"""
        style = """
        QMainWindow, QWidget {
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
        
        QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 3px;
            padding: 3px;
            color: #ffffff;
        }
        
        QTextEdit {
            background-color: #404040;
            border: 1px solid #555555;
            border-radius: 3px;
            color: #ffffff;
        }
        """
        self.setStyleSheet(style)
    
    def setup_maya_integration(self):
        """Maya 연동 설정"""
        if MAYA_AVAILABLE:
            self.log_message("Maya 환경이 감지되었습니다.")
            self.refresh_scene_info()
        else:
            self.log_message("Maya 환경이 감지되지 않았습니다. 독립 실행 모드로 동작합니다.")
    
    def refresh_scene_info(self):
        """씬 정보 새로고침"""
        if MAYA_AVAILABLE:
            try:
                # 씬 이름
                scene_name = cmds.file(q=True, sn=True) or "untitled"
                self.scene_name_label.setText(scene_name)
                
                # 씬 내 커브 수
                nurbs_curves = cmds.ls(type='nurbsCurve', long=True)
                poly_curves = [mesh for mesh in cmds.ls(type='mesh', long=True) 
                             if cmds.polyEvaluate(mesh, f=True) == 1]
                total_curves = len(nurbs_curves) + len(poly_curves)
                self.curves_count_label.setText(f"{total_curves}개")
                
                # 선택된 커브
                selected = cmds.ls(sl=True, long=True)
                if selected:
                    self.selected_curves_label.setText(f"{len(selected)}개 선택됨")
                else:
                    self.selected_curves_label.setText("없음")
                
                self.log_message("씬 정보가 새로고침되었습니다.")
                
            except Exception as e:
                self.log_message(f"씬 정보 새로고침 오류: {e}")
        else:
            self.log_message("Maya 환경이 아닙니다.")
    
    def create_offset_curves(self):
        """오프셋 커브 생성"""
        if not MAYA_AVAILABLE:
            self.log_message("Maya 환경이 아닙니다.")
            return
        
        try:
            selected_curves = cmds.ls(sl=True, long=True)
            if not selected_curves:
                self.log_message("Maya에서 커브를 선택해주세요.")
                return
            
            # 진행 상황 표시
            self.progress_bar.setValue(25)
            
            # 파라미터 가져오기
            offset_dist = self.offset_distance.value()
            direction = self.offset_direction.currentText()
            
            # Maya 방향을 내부 방향으로 변환
            direction_map = {
                "양쪽": "both",
                "안쪽": "left", 
                "바깥쪽": "right"
            }
            internal_direction = direction_map.get(direction, "both")
            
            # 오프셋 커브 생성
            for curve in selected_curves:
                self.log_message(f"커브 '{curve}'에 대한 오프셋 생성 중...")
                
                # Maya 커브 데이터 추출
                curve_data = self._extract_maya_curve_data(curve)
                if not curve_data:
                    self.log_message(f"커브 '{curve}' 데이터 추출 실패")
                    continue
                
                # 오프셋 파라미터 설정
                offset_params = {
                    'algorithm': 'parallel',  # 기본 알고리즘
                    'offset_distance': offset_dist,
                    'offset_direction': internal_direction,
                    'smooth_curves': True,
                    'corner_handling': 'adaptive'
                }
                
                # 오프셋 생성
                try:
                    from src.offsetCurveDeformer import OffsetGenerator
                    offset_gen = OffsetGenerator()
                    
                    # CurveData 객체 생성
                    from src.core.interfaces import CurveData
                    curve_obj = CurveData(
                        points=curve_data['points'],
                        metadata=curve_data['metadata'],
                        format='maya',
                        source_path=curve
                    )
                    
                    # 오프셋 생성
                    result = offset_gen.generate_offset(curve_obj, offset_params)
                    
                    if result and result.offset_curves:
                        # Maya에 오프셋 커브 생성
                        for i, offset_curve_data in enumerate(result.offset_curves):
                            # Maya 커브 생성
                            offset_curve_name = f"{curve}_offset_{i+1}"
                            self._create_maya_curve_from_points(
                                offset_curve_data.points, 
                                offset_curve_name
                            )
                            
                            # 방향에 따른 이름 설정
                            if internal_direction == "both":
                                if i == 0:
                                    cmds.rename(offset_curve_name, f"{curve}_offset_left")
                                else:
                                    cmds.rename(offset_curve_name, f"{curve}_offset_right")
                            elif internal_direction == "left":
                                cmds.rename(offset_curve_name, f"{curve}_offset_left")
                            else:
                                cmds.rename(offset_curve_name, f"{curve}_offset_right")
                        
                        self.log_message(f"커브 '{curve}'에 대한 오프셋 커브 {len(result.offset_curves)}개 생성 완료")
                    else:
                        self.log_message(f"커브 '{curve}'에 대한 오프셋 커브 생성 실패")
                
                except ImportError:
                    # 백엔드 모듈을 찾을 수 없는 경우 기본 Maya 명령 사용
                    self.log_message("백엔드 모듈을 찾을 수 없어 기본 Maya 명령을 사용합니다.")
                    self._create_basic_offset_curve(curve, offset_dist, direction)
                
                except Exception as e:
                    self.log_message(f"오프셋 생성 오류: {e}")
                    # 오류 발생 시 기본 Maya 명령 사용
                    self._create_basic_offset_curve(curve, offset_dist, direction)
            
            self.progress_bar.setValue(100)
            self.log_message(f"{len(selected_curves)}개 커브에 대한 오프셋 커브 생성 완료")
            
        except Exception as e:
            self.log_message(f"오프셋 커브 생성 오류: {e}")
            self.progress_bar.setValue(0)
    
    def optimize_curves(self):
        """커브 최적화"""
        if not MAYA_AVAILABLE:
            self.log_message("Maya 환경이 아닙니다.")
            return
        
        try:
            selected_curves = cmds.ls(sl=True, long=True)
            if not selected_curves:
                self.log_message("Maya에서 커브를 선택해주세요.")
                return
            
            # 진행 상황 표시
            self.progress_bar.setValue(25)
            
            # 최적화 수준
            level = self.optimization_level.currentText()
            
            # 최적화 수준을 내부 파라미터로 변환
            level_map = {
                "낮음": {"algorithm": "quality", "target_quality": 0.6, "smoothing_factor": 0.3},
                "보통": {"algorithm": "quality", "target_quality": 0.8, "smoothing_factor": 0.5},
                "높음": {"algorithm": "quality", "target_quality": 0.9, "smoothing_factor": 0.7}
            }
            optimization_params = level_map.get(level, level_map["보통"])
            
            for curve in selected_curves:
                self.log_message(f"커브 '{curve}' 최적화 중...")
                
                curve_type = cmds.nodeType(curve)
                
                if curve_type == 'nurbsCurve':
                    # NURBS 커브 최적화
                    try:
                        # 백엔드 최적화 시도
                        from src.inputCurveOptimizer import CurveOptimizer
                        
                        # Maya 커브 데이터 추출
                        curve_data = self._extract_maya_curve_data(curve)
                        if curve_data:
                            # CurveData 객체 생성
                            from src.core.interfaces import CurveData
                            curve_obj = CurveData(
                                points=curve_data['points'],
                                metadata=curve_data['metadata'],
                                format='maya',
                                source_path=curve
                            )
                            
                            # 최적화 수행
                            optimizer = CurveOptimizer()
                            result = optimizer.optimize_curve(curve_obj, optimization_params)
                            
                            if result and result.optimized_curve:
                                # 최적화된 커브로 Maya 커브 업데이트
                                self._update_maya_curve_from_points(curve, result.optimized_curve.points)
                                self.log_message(f"커브 '{curve}' 백엔드 최적화 완료 (포인트: {result.original_point_count} → {result.optimized_point_count})")
                            else:
                                # 백엔드 최적화 실패 시 기본 Maya 명령 사용
                                self._apply_basic_maya_optimization(curve, curve_type, level)
                        else:
                            # 데이터 추출 실패 시 기본 Maya 명령 사용
                            self._apply_basic_maya_optimization(curve, curve_type, level)
                    
                    except ImportError:
                        # 백엔드 모듈을 찾을 수 없는 경우 기본 Maya 명령 사용
                        self.log_message("백엔드 모듈을 찾을 수 없어 기본 Maya 명령을 사용합니다.")
                        self._apply_basic_maya_optimization(curve, curve_type, level)
                    
                    except Exception as e:
                        self.log_message(f"백엔드 최적화 오류: {e}")
                        # 오류 발생 시 기본 Maya 명령 사용
                        self._apply_basic_maya_optimization(curve, curve_type, level)
                
                elif curve_type == 'mesh':
                    # 폴리곤 메시 최적화
                    self._apply_basic_maya_optimization(curve, curve_type, level)
            
            self.progress_bar.setValue(100)
            self.log_message(f"{len(selected_curves)}개 커브 최적화 완료")
            
        except Exception as e:
            self.log_message(f"커브 최적화 오류: {e}")
            self.progress_bar.setValue(0)
    
    def reset_parameters(self):
        """파라미터 재설정"""
        self.offset_distance.setValue(1.0)
        self.offset_direction.setCurrentText("양쪽")
        self.optimization_level.setCurrentText("보통")
        self.progress_bar.setValue(0)
        self.log_message("파라미터가 재설정되었습니다.")
    
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
    
    def _extract_maya_curve_data(self, curve_name: str) -> Optional[Dict[str, Any]]:
        """Maya 커브에서 데이터 추출"""
        try:
            curve_type = cmds.nodeType(curve_name)
            
            if curve_type == 'nurbsCurve':
                # NURBS 커브 데이터 추출
                cv_positions = cmds.getAttr(f"{curve_name}.cv[*]")
                points = [(pos[0], pos[1], pos[2]) for pos in cv_positions]
                
                # 2D로 변환 (Z=0 평면)
                points_2d = [(p[0], p[1]) for p in points]
                
                metadata = {
                    'type': 'nurbs',
                    'degree': cmds.getAttr(f"{curve_name}.degree"),
                    'spans': cmds.getAttr(f"{curve_name}.spans"),
                    'form': cmds.getAttr(f"{curve_name}.form")
                }
                
            elif curve_type == 'mesh':
                # 폴리곤 메시 데이터 추출
                vertices = cmds.ls(f"{curve_name}.vtx[*]", fl=True)
                points = []
                for vtx in vertices:
                    pos = cmds.pointPosition(vtx, world=True)
                    points.append((pos[0], pos[1], pos[2]))
                
                # 2D로 변환 (Z=0 평면)
                points_2d = [(p[0], p[1]) for p in points]
                
                metadata = {
                    'type': 'mesh',
                    'vertex_count': len(vertices),
                    'face_count': cmds.polyEvaluate(curve_name, face=True)
                }
            
            else:
                self.log_message(f"지원하지 않는 커브 타입: {curve_type}")
                return None
            
            return {
                'points': points_2d,
                'metadata': metadata
            }
            
        except Exception as e:
            self.log_message(f"커브 데이터 추출 오류: {e}")
            return None
    
    def _create_maya_curve_from_points(self, points: List[Tuple[float, float]], curve_name: str):
        """포인트로부터 Maya 커브 생성"""
        try:
            # 3D 포인트로 변환 (Z=0)
            points_3d = [(p[0], p[1], 0) for p in points]
            
            # NURBS 커브 생성
            curve = cmds.curve(p=points_3d, degree=3, name=curve_name)
            
            # 커브 속성 설정
            cmds.setAttr(f"{curve}.form", 2)  # Open form
            
            return curve
            
        except Exception as e:
            self.log_message(f"Maya 커브 생성 오류: {e}")
            return None
    
    def _update_maya_curve_from_points(self, curve_name: str, points: List[Tuple[float, float]]):
        """기존 Maya 커브를 새로운 포인트로 업데이트"""
        try:
            # 3D 포인트로 변환 (Z=0)
            points_3d = [(p[0], p[1], 0) for p in points]
            
            # 기존 커브 삭제
            cmds.delete(curve_name)
            
            # 새 커브 생성
            new_curve = cmds.curve(p=points_3d, degree=3, name=curve_name)
            
            # 커브 속성 설정
            cmds.setAttr(f"{new_curve}.form", 2)  # Open form
            
            return new_curve
            
        except Exception as e:
            self.log_message(f"Maya 커브 업데이트 오류: {e}")
            return None
    
    def _create_basic_offset_curve(self, curve_name: str, distance: float, direction: str):
        """기본 Maya 명령을 사용한 오프셋 커브 생성"""
        try:
            if direction == "양쪽":
                # 양쪽 방향 오프셋
                offset_curve1 = cmds.duplicate(curve_name, rr=True)[0]
                cmds.rename(offset_curve1, f"{curve_name}_offset_left")
                cmds.move(-distance, 0, 0, offset_curve1, relative=True)
                
                offset_curve2 = cmds.duplicate(curve_name, rr=True)[0]
                cmds.rename(offset_curve2, f"{curve_name}_offset_right")
                cmds.move(distance, 0, 0, offset_curve2, relative=True)
                
            elif direction == "안쪽":
                # 안쪽 방향 오프셋
                offset_curve = cmds.duplicate(curve_name, rr=True)[0]
                cmds.rename(offset_curve, f"{curve_name}_offset_left")
                cmds.move(-distance, 0, 0, offset_curve, relative=True)
                
            else:  # 바깥쪽
                # 바깥쪽 방향 오프셋
                offset_curve = cmds.duplicate(curve_name, rr=True)[0]
                cmds.rename(offset_curve, f"{curve_name}_offset_right")
                cmds.move(distance, 0, 0, offset_curve, relative=True)
                
        except Exception as e:
            self.log_message(f"기본 오프셋 커브 생성 오류: {e}")
    
    def _apply_basic_maya_optimization(self, curve_name: str, curve_type: str, level: str):
        """기본 Maya 명령을 사용한 커브 최적화"""
        try:
            if curve_type == 'nurbsCurve':
                if level == "높음":
                    # CV 수 줄이기
                    spans = cmds.getAttr(f"{curve_name}.spans")
                    if spans > 4:
                        new_spans = max(4, spans // 2)
                        cmds.rebuildCurve(curve_name, spans=new_spans, degree=3, keepRange=2)
                elif level == "보통":
                    # 부드러운 커브로 만들기
                    cmds.smoothCurve(curve_name, smoothness=0.5)
                    
            elif curve_type == 'mesh':
                if level == "높음":
                    # 폴리곤 수 줄이기
                    cmds.polyReduce(curve_name, percentage=50, keepQuads=True)
                elif level == "보통":
                    # 부드럽게 만들기
                    cmds.polySmooth(curve_name, divisions=1)
                    
        except Exception as e:
            self.log_message(f"기본 Maya 최적화 오류: {e}")

def main():
    """메인 함수"""
    app = QApplication(sys.argv)
    
    # 메인 윈도우 생성
    window = MayaOffsetCurveGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
