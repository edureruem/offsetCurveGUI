"""
Offset Curve Deformer Plugin Wrapper

이 모듈은 Maya의 offsetCurveDeformer C++ 플러그인을 Python에서 사용할 수 있게 해주는 래퍼입니다.
C++ 플러그인의 실제 기능들을 Python 메서드로 래핑하여 제공합니다.

실제 C++ 플러그인 파라미터들:
✅ aOffsetMode - Arc Segment vs B-Spline
✅ aFalloffRadius - 영향 반경
✅ aMaxInfluences - 최대 영향 수
✅ aVolumeStrength - 볼륨 보존 강도
✅ aSlideEffect - 슬라이딩 효과
✅ aRotationDistribution, aScaleDistribution, aTwistDistribution
✅ aAxialSliding - 축 방향 슬라이딩
✅ aUseParallel - 병렬 처리
✅ aDebugDisplay - 디버그 표시
✅ aRebindMesh, aRebindCurves - 리바인딩 기능
✅ aEnablePoseBlend, aPoseTarget, aPoseWeight - 포즈 블렌딩
"""

import maya.cmds as cmds
import maya.mel as mel
from typing import List, Dict, Any, Optional, Tuple
import logging

# 로깅 설정
logger = logging.getLogger(__name__)


class OffsetCurveDeformerWrapper:
    """
    offsetCurveDeformer C++ 플러그인을 Python에서 사용하기 위한 래퍼 클래스
    
    이 클래스는 C++ 플러그인의 실제 메서드들을 Python에서 호출할 수 있게 해줍니다.
    """
    
    def __init__(self):
        """OffsetCurveDeformer 래퍼 초기화"""
        self.plugin_name = "offsetCurveDeformer"
        self.node_type = "offsetCurveDeformer"
        self._ensure_plugin_loaded()
        
        # C++ 플러그인의 실제 파라미터 기본값들
        self.default_params = {
            'offset_mode': 0,           # 0: Arc Segment, 1: B-Spline
            'falloff_radius': 10.0,     # 영향 반경
            'max_influences': 4,        # 최대 영향 수
            'volume_strength': 1.0,     # 볼륨 보존 강도
            'slide_effect': 0.0,        # 슬라이딩 효과
            'rotation_distribution': 1.0,  # 회전 분포
            'scale_distribution': 1.0,     # 스케일 분포
            'twist_distribution': 1.0,     # 꼬임 분포
            'axial_sliding': 0.0,          # 축 방향 슬라이딩
            'use_parallel': False,         # 병렬 처리
            'debug_display': False,        # 디버그 표시
            'enable_pose_blend': False,    # 포즈 블렌딩
            'pose_weight': 0.0             # 포즈 가중치
        }
    
    def _ensure_plugin_loaded(self) -> bool:
        """필요한 플러그인이 로드되어 있는지 확인하고, 필요시 로드"""
        try:
            if not cmds.pluginInfo(self.plugin_name, query=True, loaded=True):
                logger.info(f"{self.plugin_name} 플러그인 로드 중...")
                cmds.loadPlugin(self.plugin_name)
                logger.info(f"{self.plugin_name} 플러그인 로드 완료")
            return True
        except Exception as e:
            logger.error(f"{self.plugin_name} 플러그인 로드 실패: {e}")
            return False
    
    def create_deformer(self, 
                       mesh_path: str, 
                       curve_paths: List[str],
                       deformer_name: str = None) -> Optional[str]:
        """
        오프셋 커브 디포머 생성 및 메시에 적용
        
        Args:
            mesh_path: 디포머를 적용할 메시의 경로
            curve_paths: 오프셋에 사용할 커브들의 경로 리스트
            deformer_name: 생성할 디포머의 이름 (None이면 자동 생성)
            
        Returns:
            생성된 디포머 노드의 이름 또는 None (실패시)
        """
        try:
            if not deformer_name:
                deformer_name = f"{mesh_path}_offsetCurveDeformer"
            
            # 디포머 노드 생성
            deformer_node = cmds.deformer(
                mesh_path, 
                type=self.node_type, 
                name=deformer_name
            )
            
            if not deformer_node:
                logger.error("디포머 노드 생성 실패")
                return None
            
            # 커브 연결
            if curve_paths:
                self.connect_curves(deformer_node[0], curve_paths)
            
            # 기본 파라미터 설정
            self.set_default_parameters(deformer_node[0])
            
            logger.info(f"디포머 생성 완료: {deformer_node[0]}")
            return deformer_node[0]
            
        except Exception as e:
            logger.error(f"디포머 생성 중 오류 발생: {e}")
            return None
    
    def connect_curves(self, deformer_node: str, curve_paths: List[str]) -> bool:
        """
        디포머에 커브들을 연결 (C++ 플러그인의 aOffsetCurves 속성)
        
        Args:
            deformer_node: 디포머 노드의 이름
            curve_paths: 연결할 커브들의 경로 리스트
            
        Returns:
            연결 성공 여부
        """
        try:
            # aOffsetCurves 속성에 커브들을 연결
            for i, curve_path in enumerate(curve_paths):
                cmds.connectAttr(
                    f"{curve_path}.worldSpace[0]", 
                    f"{deformer_node}.offsetCurves[{i}]"
                )
            
            logger.info(f"{len(curve_paths)}개 커브를 디포머에 연결 완료")
            return True
            
        except Exception as e:
            logger.error(f"커브 연결 중 오류 발생: {e}")
            return False
    
    def set_default_parameters(self, deformer_node: str) -> bool:
        """디포머의 기본 파라미터들을 설정"""
        try:
            for param_name, value in self.default_params.items():
                self._set_parameter(deformer_node, param_name, value)
            logger.info("기본 파라미터 설정 완료")
            return True
        except Exception as e:
            logger.error(f"기본 파라미터 설정 중 오류: {e}")
            return False
    
    def _set_parameter(self, deformer_node: str, param_name: str, value: Any) -> bool:
        """개별 파라미터 설정 (내부 메서드)"""
        try:
            # C++ 플러그인의 실제 속성 이름으로 매핑
            attr_mapping = {
                'offset_mode': 'offsetMode',
                'falloff_radius': 'falloffRadius',
                'max_influences': 'maxInfluences',
                'volume_strength': 'volumeStrength',
                'slide_effect': 'slideEffect',
                'rotation_distribution': 'rotationDistribution',
                'scale_distribution': 'scaleDistribution',
                'twist_distribution': 'twistDistribution',
                'axial_sliding': 'axialSliding',
                'use_parallel': 'useParallelComputation',
                'debug_display': 'debugDisplay',
                'enable_pose_blend': 'enablePoseBlend',
                'pose_weight': 'poseWeight'
            }
            
            if param_name in attr_mapping:
                attr_name = attr_mapping[param_name]
                cmds.setAttr(f"{deformer_node}.{attr_name}", value)
                return True
            else:
                logger.warning(f"알 수 없는 파라미터: {param_name}")
                return False
                
        except Exception as e:
            logger.error(f"파라미터 {param_name} 설정 중 오류: {e}")
            return False
    
    def set_offset_mode(self, deformer_node: str, mode: int) -> bool:
        """
        오프셋 모드 설정 (C++ 플러그인의 aOffsetMode 속성)
        
        Args:
            deformer_node: 디포머 노드의 이름
            mode: 오프셋 모드 (0: Arc Segment, 1: B-Spline)
            
        Returns:
            설정 성공 여부
        """
        try:
            cmds.setAttr(f"{deformer_node}.offsetMode", mode)
            mode_name = "Arc Segment" if mode == 0 else "B-Spline"
            logger.info(f"오프셋 모드 설정 완료: {mode_name}")
            return True
            
        except Exception as e:
            logger.error(f"오프셋 모드 설정 중 오류 발생: {e}")
            return False
    
    def set_falloff_radius(self, deformer_node: str, radius: float) -> bool:
        """
        영향 반경 설정 (C++ 플러그인의 aFalloffRadius 속성)
        
        Args:
            deformer_node: 디포머 노드의 이름
            radius: 영향 반경 값 (0.001-100.0)
            
        Returns:
            설정 성공 여부
        """
        try:
            cmds.setAttr(f"{deformer_node}.falloffRadius", radius)
            logger.info(f"영향 반경 설정 완료: {radius}")
            return True
            
        except Exception as e:
            logger.error(f"영향 반경 설정 중 오류 발생: {e}")
            return False
    
    def set_max_influences(self, deformer_node: str, max_count: int) -> bool:
        """
        최대 영향 곡선 수 설정 (C++ 플러그인의 aMaxInfluences 속성)
        
        Args:
            deformer_node: 디포머 노드의 이름
            max_count: 최대 영향 수 (1-10)
            
        Returns:
            설정 성공 여부
        """
        try:
            cmds.setAttr(f"{deformer_node}.maxInfluences", max_count)
            logger.info(f"최대 영향 수 설정 완료: {max_count}")
            return True
            
        except Exception as e:
            logger.error(f"최대 영향 수 설정 중 오류 발생: {e}")
            return False
    
    def set_volume_strength(self, deformer_node: str, strength: float) -> bool:
        """
        볼륨 보존 강도 설정 (C++ 플러그인의 aVolumeStrength 속성)
        
        Args:
            deformer_node: 디포머 노드의 이름
            strength: 볼륨 보존 강도 (0.0-5.0)
            
        Returns:
            설정 성공 여부
        """
        try:
            cmds.setAttr(f"{deformer_node}.volumeStrength", strength)
            logger.info(f"볼륨 보존 강도 설정 완료: {strength}")
            return True
            
        except Exception as e:
            logger.error(f"볼륨 보존 강도 설정 중 오류 발생: {e}")
            return False
    
    def set_slide_effect(self, deformer_node: str, effect: float) -> bool:
        """
        슬라이딩 효과 설정 (C++ 플러그인의 aSlideEffect 속성)
        
        Args:
            deformer_node: 디포머 노드의 이름
            effect: 슬라이딩 효과 (-2.0-2.0)
            
        Returns:
            설정 성공 여부
        """
        try:
            cmds.setAttr(f"{deformer_node}.slideEffect", effect)
            logger.info(f"슬라이딩 효과 설정 완료: {effect}")
            return True
            
        except Exception as e:
            logger.error(f"슬라이딩 효과 설정 중 오류 발생: {e}")
            return False
    
    def set_distribution_parameters(self, 
                                  deformer_node: str,
                                  rotation_dist: float = 1.0,
                                  scale_dist: float = 1.0,
                                  twist_dist: float = 1.0) -> bool:
        """
        변형 분포 파라미터 설정 (C++ 플러그인의 분포 속성들)
        
        Args:
            deformer_node: 디포머 노드의 이름
            rotation_dist: 회전 분포 (0.0-2.0)
            scale_dist: 스케일 분포 (0.0-2.0)
            twist_dist: 꼬임 분포 (0.0-2.0)
            
        Returns:
            설정 성공 여부
        """
        try:
            cmds.setAttr(f"{deformer_node}.rotationDistribution", rotation_dist)
            cmds.setAttr(f"{deformer_node}.scaleDistribution", scale_dist)
            cmds.setAttr(f"{deformer_node}.twistDistribution", twist_dist)
            
            logger.info(f"변형 분포 설정 완료: R={rotation_dist}, S={scale_dist}, T={twist_dist}")
            return True
            
        except Exception as e:
            logger.error(f"변형 분포 설정 중 오류 발생: {e}")
            return False
    
    def set_axial_sliding(self, deformer_node: str, sliding: float) -> bool:
        """
        축 방향 슬라이딩 설정 (C++ 플러그인의 aAxialSliding 속성)
        
        Args:
            deformer_node: 디포머 노드의 이름
            sliding: 축 방향 슬라이딩 (-1.0-1.0)
            
        Returns:
            설정 성공 여부
        """
        try:
            cmds.setAttr(f"{deformer_node}.axialSliding", sliding)
            logger.info(f"축 방향 슬라이딩 설정 완료: {sliding}")
            return True
            
        except Exception as e:
            logger.error(f"축 방향 슬라이딩 설정 중 오류 발생: {e}")
            return False
    
    def set_parallel_processing(self, deformer_node: str, enabled: bool) -> bool:
        """
        병렬 처리 사용 여부 설정 (C++ 플러그인의 aUseParallel 속성)
        
        Args:
            deformer_node: 디포머 노드의 이름
            enabled: 병렬 처리 사용 여부
            
        Returns:
            설정 성공 여부
        """
        try:
            cmds.setAttr(f"{deformer_node}.useParallelComputation", enabled)
            logger.info(f"병렬 처리 설정 완료: {enabled}")
            return True
            
        except Exception as e:
            logger.error(f"병렬 처리 설정 중 오류 발생: {e}")
            return False
    
    def set_debug_display(self, deformer_node: str, enabled: bool) -> bool:
        """
        디버그 표시 설정 (C++ 플러그인의 aDebugDisplay 속성)
        
        Args:
            deformer_node: 디포머 노드의 이름
            enabled: 디버그 표시 사용 여부
            
        Returns:
            설정 성공 여부
        """
        try:
            cmds.setAttr(f"{deformer_node}.debugDisplay", enabled)
            logger.info(f"디버그 표시 설정 완료: {enabled}")
            return True
            
        except Exception as e:
            logger.error(f"디버그 표시 설정 중 오류 발생: {e}")
            return False
    
    def set_pose_blending(self, deformer_node: str, enabled: bool, target_mesh: str = None, weight: float = 0.0) -> bool:
        """
        포즈 블렌딩 설정 (C++ 플러그인의 포즈 블렌딩 속성들)
        
        Args:
            deformer_node: 디포머 노드의 이름
            enabled: 포즈 블렌딩 활성화 여부
            target_mesh: 포즈 타겟 메시 (None이면 비활성화)
            weight: 포즈 가중치 (0.0-1.0)
            
        Returns:
            설정 성공 여부
        """
        try:
            # 포즈 블렌딩 활성화/비활성화
            cmds.setAttr(f"{deformer_node}.enablePoseBlend", enabled)
            
            if enabled and target_mesh:
                # 포즈 타겟 메시 연결
                cmds.connectAttr(f"{target_mesh}.worldMesh[0]", f"{deformer_node}.poseTarget")
                # 포즈 가중치 설정
                cmds.setAttr(f"{deformer_node}.poseWeight", weight)
                logger.info(f"포즈 블렌딩 설정 완료: 타겟={target_mesh}, 가중치={weight}")
            else:
                # 포즈 블렌딩 비활성화시 연결 해제
                try:
                    cmds.disconnectAttr(f"{deformer_node}.poseTarget")
                except:
                    pass  # 연결이 없었을 수 있음
                logger.info("포즈 블렌딩 비활성화 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"포즈 블렌딩 설정 중 오류 발생: {e}")
            return False
    
    def rebind_mesh(self, deformer_node: str) -> bool:
        """
        메시 리바인딩 (C++ 플러그인의 aRebindMesh 속성)
        
        Args:
            deformer_node: 디포머 노드의 이름
            
        Returns:
            리바인딩 성공 여부
        """
        try:
            # aRebindMesh 속성 트리거 (True로 설정하면 자동으로 False로 돌아감)
            cmds.setAttr(f"{deformer_node}.rebindMesh", True)
            logger.info("메시 리바인딩 완료")
            return True
            
        except Exception as e:
            logger.error(f"메시 리바인딩 중 오류 발생: {e}")
            return False
    
    def rebind_curves(self, deformer_node: str) -> bool:
        """
        커브 리바인딩 (C++ 플러그인의 aRebindCurves 속성)
        
        Args:
            deformer_node: 디포머 노드의 이름
            
        Returns:
            리바인딩 성공 여부
        """
        try:
            # aRebindCurves 속성 트리거 (True로 설정하면 자동으로 False로 돌아감)
            cmds.setAttr(f"{deformer_node}.rebindCurves", True)
            logger.info("커브 리바인딩 완료")
            return True
            
        except Exception as e:
            logger.error(f"커브 리바인딩 중 오류 발생: {e}")
            return False
    
    # === 🚀 워크플로우 메서드들 ===
    
    def workflow_create_and_bind(self, mesh_name, curve_names, deformer_name=None, 
                                offset_mode="arc", falloff_radius=1.0, max_influences=10):
        """
        디포머를 생성하고 메시와 곡선을 바인딩하는 완전한 워크플로우
        
        Args:
            mesh_name (str): 디포머를 적용할 메시 이름
            curve_names (list): 오프셋 곡선 이름들의 리스트
            deformer_name (str): 생성할 디포머 이름 (None이면 자동 생성)
            offset_mode (str): 오프셋 모드 ("arc" 또는 "bspline")
            falloff_radius (float): 영향 반경
            max_influences (int): 최대 영향 수
            
        Returns:
            str: 생성된 디포머 이름 또는 None
        """
        try:
            logger.info(f"디포머 생성 및 바인딩 워크플로우 시작: {mesh_name}")
            
            # 디포머 생성
            if deformer_name is None:
                deformer_name = f"{mesh_name}_offsetDeformer"
            
            deformer_node = self.create_deformer(mesh_name, deformer_name)
            if not deformer_node:
                logger.error("디포머 생성 실패")
                return None
            
            # 기본 파라미터 설정
            mode_value = 0 if offset_mode == "arc" else 1
            self.set_offset_mode(deformer_node, mode_value)
            self.set_falloff_radius(deformer_node, falloff_radius)
            self.set_max_influences(deformer_node, max_influences)
            
            # 곡선 연결
            for curve_name in curve_names:
                self.connect_curves(deformer_node, [curve_name]) # curve_name은 이미 문자열이므로 리스트로 변환
                logger.info(f"곡선 연결 완료: {curve_name}")
            
            logger.info(f"디포머 생성 및 바인딩 완료: {deformer_node}")
            return deformer_node
            
        except Exception as e:
            logger.error(f"디포머 생성 및 바인딩 워크플로우 실패: {e}")
            return None

    def workflow_advanced_deformation(self, deformer_name, volume_strength=1.0, 
                                     slide_effect=0.5, rotation_dist=1.0, 
                                     scale_dist=1.0, twist_dist=1.0):
        """
        고급 디포머 파라미터를 설정하는 워크플로우
        
        Args:
            deformer_name (str): 디포머 이름
            volume_strength (float): 볼륨 보존 강도
            slide_effect (float): 슬라이딩 효과
            rotation_dist (float): 회전 분포
            scale_dist (float): 스케일 분포
            twist_dist (float): 트위스트 분포
            
        Returns:
            bool: 설정 성공 여부
        """
        try:
            logger.info(f"고급 디포머 파라미터 설정 시작: {deformer_name}")
            
            # 볼륨 및 슬라이딩 설정
            self.set_volume_strength(deformer_name, volume_strength)
            self.set_slide_effect(deformer_name, slide_effect)
            
            # 분포 파라미터 설정
            self.set_distribution_parameters(deformer_name, rotation_dist, scale_dist, twist_dist)
            
            # 축 방향 슬라이딩 활성화
            self.set_axial_sliding(deformer_name, True)
            
            # 병렬 처리 활성화
            self.set_parallel_processing(deformer_name, True)
            
            logger.info("고급 디포머 파라미터 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"고급 디포머 파라미터 설정 실패: {e}")
            return False

    def workflow_pose_blending(self, deformer_name, pose_target, pose_weight=0.5):
        """
        포즈 블렌딩을 설정하는 워크플로우
        
        Args:
            deformer_name (str): 디포머 이름
            pose_target (str): 타겟 포즈 메시 이름
            pose_weight (float): 포즈 블렌딩 가중치 (0.0 ~ 1.0)
            
        Returns:
            bool: 설정 성공 여부
        """
        try:
            logger.info(f"포즈 블렌딩 설정 시작: {deformer_name}")
            
            # 포즈 블렌딩 활성화 및 설정
            success = self.set_pose_blending(deformer_name, True, pose_target, pose_weight)
            
            if success:
                logger.info(f"포즈 블렌딩 설정 완료: 타겟={pose_target}, 가중치={pose_weight}")
                return True
            else:
                logger.error("포즈 블렌딩 설정 실패")
                return False
                
        except Exception as e:
            logger.error(f"포즈 블렌딩 워크플로우 실패: {e}")
            return False

    def workflow_rebinding(self, deformer_name, new_mesh=None, new_curves=None):
        """
        메시와 곡선을 재바인딩하는 워크플로우
        
        Args:
            deformer_name (str): 디포머 이름
            new_mesh (str): 새로운 메시 이름 (None이면 현재 메시 유지)
            new_curves (list): 새로운 곡선 이름들의 리스트 (None이면 현재 곡선 유지)
            
        Returns:
            bool: 재바인딩 성공 여부
        """
        try:
            logger.info(f"재바인딩 워크플로우 시작: {deformer_name}")
            
            # 메시 재바인딩
            if new_mesh:
                self.rebind_mesh(deformer_name)
                logger.info(f"메시 재바인딩 완료: {new_mesh}")
            
            # 곡선 재바인딩
            if new_curves:
                for curve_name in new_curves:
                    self.rebind_curves(deformer_name)
                    logger.info(f"곡선 재바인딩 완료: {curve_name}")
            
            logger.info("재바인딩 워크플로우 완료")
            return True
            
        except Exception as e:
            logger.error(f"재바인딩 워크플로우 실패: {e}")
            return False

    def workflow_debug_and_optimization(self, deformer_name, enable_debug=True, 
                                       parallel_processing=True):
        """
        디버그 및 최적화 설정을 위한 워크플로우
        
        Args:
            deformer_name (str): 디포머 이름
            enable_debug (bool): 디버그 표시 활성화 여부
            parallel_processing (bool): 병렬 처리 활성화 여부
            
        Returns:
            bool: 설정 성공 여부
        """
        try:
            logger.info(f"디버그 및 최적화 설정 시작: {deformer_name}")
            
            # 디버그 표시 설정
            self.set_debug_display(deformer_name, enable_debug)
            
            # 병렬 처리 설정
            self.set_parallel_processing(deformer_name, parallel_processing)
            
            logger.info("디버그 및 최적화 설정 완료")
            return True
            
        except Exception as e:
            logger.error(f"디버그 및 최적화 설정 실패: {e}")
            return False

    def get_workflow_status(self, deformer_name):
        """현재 워크플로우 상태를 반환합니다."""
        try:
            if not deformer_name:
                return {"status": "no_deformer", "error": "디포머 이름이 지정되지 않음"}
            
            # 디포머 파라미터 조회
            params = self.get_deformer_parameters(deformer_name)
            
            # 연결된 곡선 조회
            curves = self.get_connected_curves(deformer_name)
            
            status = {
                "deformer_name": deformer_name,
                "parameters": params,
                "connected_curves": curves,
                "status": "active" if params else "inactive"
            }
            
            return status
            
        except Exception as e:
            logger.error(f"워크플로우 상태 확인 실패: {e}")
            return {"status": "error", "error": str(e)}

    def cleanup_workflow(self, deformer_name):
        """워크플로우 정리 및 디포머 제거"""
        try:
            if deformer_name and cmds.objExists(deformer_name):
                cmds.delete(deformer_name)
                logger.info(f"워크플로우 정리 완료: {deformer_name}")
            else:
                logger.info("정리할 디포머가 없습니다")
        except Exception as e:
            logger.error(f"워크플로우 정리 실패: {e}")

    def get_deformer_parameters(self, deformer_node: str) -> Dict[str, Any]:
        """
        디포머의 현재 파라미터 값들을 가져오기
        
        Args:
            deformer_node: 디포머 노드의 이름
            
        Returns:
            파라미터 값들을 담은 딕셔너리
        """
        try:
            params = {}
            
            # 기본 속성들
            params['offset_mode'] = cmds.getAttr(f"{deformer_node}.offsetMode")
            params['falloff_radius'] = cmds.getAttr(f"{deformer_node}.falloffRadius")
            params['max_influences'] = cmds.getAttr(f"{deformer_node}.maxInfluences")
            
            # 아티스트 제어 속성들
            params['volume_strength'] = cmds.getAttr(f"{deformer_node}.volumeStrength")
            params['slide_effect'] = cmds.getAttr(f"{deformer_node}.slideEffect")
            params['rotation_distribution'] = cmds.getAttr(f"{deformer_node}.rotationDistribution")
            params['scale_distribution'] = cmds.getAttr(f"{deformer_node}.scaleDistribution")
            params['twist_distribution'] = cmds.getAttr(f"{deformer_node}.twistDistribution")
            params['axial_sliding'] = cmds.getAttr(f"{deformer_node}.axialSliding")
            
            # 옵션 속성들
            params['use_parallel'] = cmds.getAttr(f"{deformer_node}.useParallelComputation")
            params['debug_display'] = cmds.getAttr(f"{deformer_node}.debugDisplay")
            
            # 포즈 블렌딩 속성들
            params['enable_pose_blend'] = cmds.getAttr(f"{deformer_node}.enablePoseBlend")
            params['pose_weight'] = cmds.getAttr(f"{deformer_node}.poseWeight")
            
            logger.info("디포머 파라미터 조회 완료")
            return params
            
        except Exception as e:
            logger.error(f"디포머 파라미터 조회 중 오류 발생: {e}")
            return {}
    
    def get_connected_curves(self, deformer_node: str) -> List[str]:
        """
        디포머에 연결된 커브들의 경로를 가져오기
        
        Args:
            deformer_node: 디포머 노드의 이름
            
        Returns:
            연결된 커브들의 경로 리스트
        """
        try:
            # offsetCurves 속성에 연결된 커브들 조회
            connections = cmds.listConnections(
                f"{deformer_node}.offsetCurves", 
                source=True, 
                destination=False
            )
            
            if connections:
                # worldSpace[0]에서 커브 이름 추출
                curve_paths = []
                for conn in connections:
                    if '.worldSpace[' in conn:
                        curve_name = conn.split('.')[0]
                        curve_paths.append(curve_name)
                
                logger.info(f"연결된 커브 {len(curve_paths)}개 조회 완료")
                return curve_paths
            else:
                logger.info("연결된 커브가 없습니다")
                return []
                
        except Exception as e:
            logger.error(f"연결된 커브 조회 중 오류 발생: {e}")
            return []
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """플러그인 정보 반환"""
        try:
            info = cmds.pluginInfo(self.plugin_name, query=True)
            return {
                "name": self.plugin_name,
                "loaded": cmds.pluginInfo(self.plugin_name, query=True, loaded=True),
                "version": info.get("version", "Unknown"),
                "vendor": info.get("vendor", "Unknown"),
                "node_type": self.node_type
            }
        except Exception as e:
            logger.error(f"플러그인 정보 조회 실패: {e}")
            return {"name": self.plugin_name, "loaded": False, "error": str(e)}


# 사용 예시
if __name__ == "__main__":
    # 래퍼 인스턴스 생성
    deformer = OffsetCurveDeformerWrapper()
    
    # 플러그인 정보 확인
    info = deformer.get_plugin_info()
    print(f"플러그인 상태: {info}")
    
    # 선택된 오브젝트들 확인
    selection = cmds.ls(selection=True)
    if len(selection) >= 2:
        mesh = selection[0]
        curves = selection[1:]
        
        # 디포머 생성
        deformer_node = deformer.create_deformer(mesh, curves)
        if deformer_node:
            print(f"디포머 생성 성공: {deformer_node}")
            
            # 파라미터 설정
            deformer.set_offset_mode(deformer_node, 0)  # Arc Segment
            deformer.set_falloff_radius(deformer_node, 10.0)
            deformer.set_max_influences(deformer_node, 4)
            deformer.set_volume_strength(deformer_node, 1.0)
            
            # 현재 파라미터 조회
            params = deformer.get_deformer_parameters(deformer_node)
            print(f"현재 파라미터: {params}")
        else:
            print("디포머 생성 실패")
    else:
        print("메시와 커브를 선택해주세요")
