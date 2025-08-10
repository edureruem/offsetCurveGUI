#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 워크플로우 매니저 - Maya 2020 호환 버전
offsetCurveDeformer와 inputCurveOptimizer를 조율하여 전체 워크플로우를 관리
Maya 씬과 직접 연동하여 커브 데이터를 처리
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from pathlib import Path

# Maya API 연동
try:
    import maya.cmds as cmds
    import maya.OpenMaya as om
    MAYA_AVAILABLE = True
except ImportError:
    MAYA_AVAILABLE = False
    print("Maya 환경이 감지되지 않았습니다. 독립 실행 모드로 동작합니다.")

@dataclass
class WorkflowStep:
    """워크플로우 단계 정보"""
    name: str
    description: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    parameters: Dict[str, Any]
    result: Optional[Any] = None

class WorkflowManager:
    """통합 워크플로우 매니저 - Maya 호환"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.workflow_steps: List[WorkflowStep] = []
        self.current_step_index = 0
        self.workflow_status = "idle"  # 'idle', 'running', 'completed', 'failed'
        
        # Maya 씬 데이터
        self.maya_scene_data = {}
        self.selected_curves = []
        
        # 워크플로우 단계 초기화
        self._initialize_workflow_steps()
        
        # Maya 환경 확인
        if MAYA_AVAILABLE:
            self.logger.info("Maya 환경이 감지되었습니다.")
            self._initialize_maya_integration()
        else:
            self.logger.warning("Maya 환경이 감지되지 않았습니다. 독립 실행 모드로 동작합니다.")
    
    def _setup_logging(self) -> logging.Logger:
        """로깅 설정"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _initialize_maya_integration(self):
        """Maya 연동 초기화"""
        try:
            # 현재 씬 정보 가져오기
            self.maya_scene_data = {
                'scene_name': cmds.file(q=True, sn=True) or 'untitled',
                'curves_in_scene': self._get_curves_in_scene()
            }
            self.logger.info(f"Maya 씬 연동 초기화 완료: {self.maya_scene_data['scene_name']}")
        except Exception as e:
            self.logger.error(f"Maya 연동 초기화 실패: {e}")
    
    def _get_curves_in_scene(self) -> List[str]:
        """씬 내의 모든 커브 가져오기"""
        try:
            if MAYA_AVAILABLE:
                # NURBS 커브와 폴리곤 커브 모두 검색
                nurbs_curves = cmds.ls(type='nurbsCurve', long=True)
                poly_curves = cmds.ls(type='mesh', long=True)
                
                # 커브 형태의 메시만 필터링
                actual_curves = []
                for curve in nurbs_curves:
                    actual_curves.append(curve)
                
                for mesh in poly_curves:
                    # 간단한 커브 형태인지 확인 (면이 1개인 메시)
                    if cmds.polyEvaluate(mesh, f=True) == 1:
                        actual_curves.append(mesh)
                
                return actual_curves
            return []
        except Exception as e:
            self.logger.error(f"씬 커브 검색 실패: {e}")
            return []
    
    def _initialize_workflow_steps(self):
        """워크플로우 단계 초기화"""
        self.workflow_steps = [
            WorkflowStep(
                name="Maya Curve Selection",
                description="Maya 씬에서 작업할 커브 선택 및 검증",
                status="pending",
                parameters={}
            ),
            WorkflowStep(
                name="Input Curve Optimization",
                description="inputCurveOptimizer를 사용한 커브 최적화",
                status="pending",
                parameters={
                    "optimization_level": "medium",
                    "smoothing_factor": 0.5,
                    "simplification_threshold": 0.01,
                    "preserve_shape": True
                }
            ),
            WorkflowStep(
                name="Offset Curve Generation",
                description="offsetCurveDeformer를 사용한 오프셋 커브 생성",
                status="pending",
                parameters={
                    "offset_distance": 1.0,
                    "offset_direction": "both",
                    "smooth_curves": True,
                    "corner_handling": "round"
                }
            ),
            WorkflowStep(
                name="Result Validation",
                description="결과 커브 검증 및 품질 확인",
                status="pending",
                parameters={
                    "check_intersections": True,
                    "validate_topology": True
                }
            ),
            WorkflowStep(
                name="Maya Integration",
                description="최종 결과를 Maya 씬에 통합",
                status="pending",
                parameters={
                    "create_new_layer": True,
                    "apply_materials": False,
                    "organize_hierarchy": True
                }
            )
        ]
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """현재 워크플로우 상태 반환"""
        return {
            "status": self.workflow_status,
            "current_step": self.current_step_index,
            "total_steps": len(self.workflow_steps),
            "maya_scene": self.maya_scene_data,
            "selected_curves": self.selected_curves,
            "steps": [
                {
                    "name": step.name,
                    "description": step.description,
                    "status": step.status,
                    "parameters": step.parameters
                }
                for step in self.workflow_steps
            ]
        }
    
    def select_curves_from_maya(self, curve_names: List[str]) -> bool:
        """Maya에서 커브 선택"""
        try:
            if MAYA_AVAILABLE:
                # 선택된 커브 검증
                valid_curves = []
                for curve_name in curve_names:
                    if cmds.objExists(curve_name):
                        valid_curves.append(curve_name)
                    else:
                        self.logger.warning(f"커브가 존재하지 않습니다: {curve_name}")
                
                self.selected_curves = valid_curves
                self.logger.info(f"Maya 커브 선택 완료: {len(valid_curves)}개")
                
                # 첫 번째 단계 파라미터 업데이트
                if valid_curves:
                    self.update_step_parameters(0, {
                        'selected_curves': valid_curves,
                        'curve_count': len(valid_curves)
                    })
                
                return len(valid_curves) > 0
            else:
                self.logger.error("Maya 환경이 아닙니다.")
                return False
        except Exception as e:
            self.logger.error(f"커브 선택 실패: {e}")
            return False
    
    def update_step_parameters(self, step_index: int, parameters: Dict[str, Any]) -> bool:
        """워크플로우 단계 파라미터 업데이트"""
        try:
            if 0 <= step_index < len(self.workflow_steps):
                self.workflow_steps[step_index].parameters.update(parameters)
                self.logger.info(f"Step {step_index} 파라미터 업데이트: {parameters}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"파라미터 업데이트 오류: {e}")
            return False
    
    def start_workflow(self) -> bool:
        """워크플로우 시작"""
        try:
            # Maya 커브 선택 확인
            if MAYA_AVAILABLE and not self.selected_curves:
                self.logger.error("워크플로우를 시작하기 전에 Maya에서 커브를 선택해주세요.")
                return False
            
            self.workflow_status = "running"
            self.current_step_index = 0
            self.logger.info("워크플로우 시작")
            return True
        except Exception as e:
            self.logger.error(f"워크플로우 시작 오류: {e}")
            self.workflow_status = "failed"
            return False
    
    def execute_current_step(self) -> bool:
        """현재 단계 실행"""
        if self.current_step_index >= len(self.workflow_steps):
            return False
        
        current_step = self.workflow_steps[self.current_step_index]
        current_step.status = "running"
        
        try:
            # 단계별 실행 로직
            if current_step.name == "Maya Curve Selection":
                result = self._execute_maya_curve_selection(current_step.parameters)
            elif current_step.name == "Input Curve Optimization":
                result = self._execute_curve_optimization(current_step.parameters)
            elif current_step.name == "Offset Curve Generation":
                result = self._execute_offset_generation(current_step.parameters)
            elif current_step.name == "Result Validation":
                result = self._execute_validation(current_step.parameters)
            elif current_step.name == "Maya Integration":
                result = self._execute_maya_integration(current_step.parameters)
            else:
                result = None
            
            current_step.result = result
            current_step.status = "completed"
            self.logger.info(f"Step {self.current_step_index} 완료: {current_step.name}")
            return True
            
        except Exception as e:
            current_step.status = "failed"
            current_step.result = str(e)
            self.logger.error(f"Step {self.current_step_index} 실패: {e}")
            return False
    
    def next_step(self) -> bool:
        """다음 단계로 진행"""
        if self.current_step_index < len(self.workflow_steps) - 1:
            self.current_step_index += 1
            return True
        else:
            self.workflow_status = "completed"
            return False
    
    def _execute_maya_curve_selection(self, parameters: Dict[str, Any]) -> Any:
        """Maya 커브 선택 실행"""
        try:
            if MAYA_AVAILABLE and self.selected_curves:
                # 선택된 커브 정보 수집
                curve_info = []
                for curve_name in self.selected_curves:
                    curve_type = cmds.nodeType(curve_name)
                    if curve_type == 'nurbsCurve':
                        # NURBS 커브 정보
                        cv_count = cmds.getAttr(f"{curve_name}.spans") + cmds.getAttr(f"{curve_name}.degree")
                        curve_info.append({
                            'name': curve_name,
                            'type': 'nurbs',
                            'cv_count': cv_count,
                            'degree': cmds.getAttr(f"{curve_name}.degree")
                        })
                    elif curve_type == 'mesh':
                        # 폴리곤 메시 정보
                        vertex_count = cmds.polyEvaluate(curve_name, v=True)
                        curve_info.append({
                            'name': curve_name,
                            'type': 'mesh',
                            'vertex_count': vertex_count
                        })
                
                return {
                    "status": "selected",
                    "curves": curve_info,
                    "total_curves": len(curve_info)
                }
            else:
                return {"status": "no_curves", "error": "선택된 커브가 없습니다."}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _execute_curve_optimization(self, parameters: Dict[str, Any]) -> Any:
        """커브 최적화 실행"""
        # TODO: inputCurveOptimizer 연동
        return {
            "status": "optimized",
            "original_points": 100,
            "optimized_points": 75,
            "quality_improvement": 0.15
        }
    
    def _execute_offset_generation(self, parameters: Dict[str, Any]) -> Any:
        """오프셋 커브 생성 실행"""
        # TODO: offsetCurveDeformer 연동
        return {
            "status": "generated",
            "offset_distance": parameters.get("offset_distance", 1.0),
            "curves_generated": 2
        }
    
    def _execute_validation(self, parameters: Dict[str, Any]) -> Any:
        """결과 검증 실행"""
        # TODO: 실제 구현
        return {"status": "validated", "quality_score": 0.95}
    
    def _execute_maya_integration(self, parameters: Dict[str, Any]) -> Any:
        """Maya 씬 통합 실행"""
        try:
            if MAYA_AVAILABLE:
                # 결과 레이어 생성
                if parameters.get("create_new_layer", True):
                    layer_name = "OffsetCurve_Results"
                    if not cmds.ls(layer_name):
                        cmds.createDisplayLayer(name=layer_name)
                    cmds.editDisplayLayerMembers(layer_name, self.selected_curves)
                
                # 계층 구조 정리
                if parameters.get("organize_hierarchy", True):
                    group_name = "OffsetCurve_Group"
                    if not cmds.objExists(group_name):
                        cmds.group(empty=True, name=group_name)
                    cmds.parent(self.selected_curves, group_name)
                
                return {
                    "status": "integrated",
                    "layer_created": parameters.get("create_new_layer", True),
                    "hierarchy_organized": parameters.get("organize_hierarchy", True)
                }
            else:
                return {"status": "error", "error": "Maya 환경이 아닙니다."}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def reset_workflow(self):
        """워크플로우 초기화"""
        self.workflow_status = "idle"
        self.current_step_index = 0
        for step in self.workflow_steps:
            step.status = "pending"
            step.result = None
        self.logger.info("워크플로우 초기화 완료")
    
    def get_maya_scene_info(self) -> Dict[str, Any]:
        """Maya 씬 정보 반환"""
        if MAYA_AVAILABLE:
            try:
                return {
                    'scene_name': cmds.file(q=True, sn=True) or 'untitled',
                    'curves_in_scene': self._get_curves_in_scene(),
                    'selected_objects': cmds.ls(sl=True, long=True),
                    'current_time': cmds.currentTime(q=True)
                }
            except Exception as e:
                return {'error': str(e)}
        return {'error': 'Maya 환경이 아닙니다.'}
