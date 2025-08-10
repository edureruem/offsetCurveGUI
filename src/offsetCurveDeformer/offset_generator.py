#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
오프셋 커브 생성 메인 클래스
다양한 오프셋 알고리즘을 조율하여 오프셋 커브 생성
"""

import time
from typing import Dict, Any, List, Tuple
import math

from ..core.interfaces import IOffsetGenerator, CurveData, OffsetResult
from ..core.exceptions import OffsetGenerationError
from .offset_algorithms import (
    ParallelOffsetAlgorithm,
    PerpendicularOffsetAlgorithm,
    AdaptiveOffsetAlgorithm
)

class OffsetGenerator(IOffsetGenerator):
    """오프셋 커브 생성 메인 클래스"""
    
    def __init__(self):
        self.algorithms = {
            'parallel': ParallelOffsetAlgorithm(),
            'perpendicular': PerpendicularOffsetAlgorithm(),
            'adaptive': AdaptiveOffsetAlgorithm()
        }
    
    def generate_offset(self, curve: CurveData, parameters: Dict[str, Any]) -> OffsetResult:
        """오프셋 커브 생성 수행"""
        start_time = time.time()
        
        try:
            # 파라미터 검증
            self._validate_parameters(parameters)
            
            # 오프셋 알고리즘 선택
            algorithm_name = parameters.get('algorithm', 'parallel')
            if algorithm_name not in self.algorithms:
                raise OffsetGenerationError(f"지원하지 않는 알고리즘입니다: {algorithm_name}")
            
            algorithm = self.algorithms[algorithm_name]
            
            # 오프셋 거리 및 방향 설정
            offset_distance = parameters.get('offset_distance', 1.0)
            offset_direction = parameters.get('offset_direction', 'both')
            
            # 오프셋 커브 생성
            offset_curves = []
            
            if offset_direction in ['left', 'both']:
                left_curve = algorithm.generate_offset(curve.points, -offset_distance, parameters)
                if left_curve:
                    left_curve_data = CurveData(
                        points=left_curve,
                        metadata={
                            **curve.metadata,
                            'offset_direction': 'left',
                            'offset_distance': offset_distance,
                            'algorithm': algorithm_name
                        },
                        format=curve.format,
                        source_path=curve.source_path
                    )
                    offset_curves.append(left_curve_data)
            
            if offset_direction in ['right', 'both']:
                right_curve = algorithm.generate_offset(curve.points, offset_distance, parameters)
                if right_curve:
                    right_curve_data = CurveData(
                        points=right_curve,
                        metadata={
                            **curve.metadata,
                            'offset_direction': 'right',
                            'offset_distance': offset_distance,
                            'algorithm': algorithm_name
                        },
                        format=curve.format,
                        source_path=curve.source_path
                    )
                    offset_curves.append(right_curve_data)
            
            # 품질 메트릭 계산
            quality_metrics = self._calculate_quality_metrics(curve.points, offset_curves)
            
            processing_time = time.time() - start_time
            
            return OffsetResult(
                offset_curves=offset_curves,
                offset_distance=offset_distance,
                quality_metrics=quality_metrics,
                processing_time=processing_time
            )
            
        except Exception as e:
            if isinstance(e, OffsetGenerationError):
                raise
            raise OffsetGenerationError(f"오프셋 커브 생성 중 오류가 발생했습니다: {e}")
    
    def get_offset_parameters(self) -> Dict[str, Any]:
        """오프셋 파라미터 스키마 반환"""
        return {
            'algorithm': {
                'type': 'choice',
                'options': ['parallel', 'perpendicular', 'adaptive'],
                'default': 'parallel',
                'description': '오프셋 알고리즘 선택'
            },
            'offset_distance': {
                'type': 'float',
                'min': 0.01,
                'max': 100.0,
                'default': 1.0,
                'description': '오프셋 거리'
            },
            'offset_direction': {
                'type': 'choice',
                'options': ['left', 'right', 'both'],
                'default': 'both',
                'description': '오프셋 방향'
            },
            'smooth_curves': {
                'type': 'bool',
                'default': True,
                'description': '커브 부드럽게 처리'
            },
            'corner_handling': {
                'type': 'choice',
                'options': ['none', 'round', 'adaptive'],
                'default': 'adaptive',
                'description': '모서리 처리 방식'
            },
            'quality': {
                'type': 'choice',
                'options': ['low', 'medium', 'high', 'ultra'],
                'default': 'high',
                'description': '오프셋 품질'
            }
        }
    
    def validate_offset_parameters(self, parameters: Dict[str, Any]) -> bool:
        """오프셋 파라미터 유효성 검증"""
        try:
            self._validate_parameters(parameters)
            return True
        except OffsetGenerationError:
            return False
    
    def _validate_parameters(self, parameters: Dict[str, Any]):
        """파라미터 유효성 검증"""
        required_params = ['algorithm', 'offset_distance']
        for param in required_params:
            if param not in parameters:
                raise OffsetGenerationError(f"필수 파라미터가 누락되었습니다: {param}")
        
        # 알고리즘 검증
        algorithm = parameters.get('algorithm')
        if algorithm not in self.algorithms:
            raise OffsetGenerationError(f"지원하지 않는 알고리즘입니다: {algorithm}")
        
        # 오프셋 거리 검증
        offset_distance = parameters.get('offset_distance')
        if not isinstance(offset_distance, (int, float)) or offset_distance <= 0:
            raise OffsetGenerationError("오프셋 거리는 양수여야 합니다")
        
        # 알고리즘별 추가 검증
        self.algorithms[algorithm].validate_parameters(parameters)
    
    def _calculate_quality_metrics(self, original_points: List[Tuple[float, float]], 
                                 offset_curves: List[CurveData]) -> Dict[str, float]:
        """품질 메트릭 계산"""
        if not offset_curves:
            return {'quality_score': 0.0, 'accuracy': 0.0, 'smoothness': 0.0}
        
        # 정확도 계산 (원본과의 거리 일관성)
        accuracy_scores = []
        for curve_data in offset_curves:
            if len(curve_data.points) == len(original_points):
                distances = []
                for i, (orig, offset) in enumerate(zip(original_points, curve_data.points)):
                    dist = math.sqrt((orig[0] - offset[0])**2 + (orig[1] - offset[1])**2)
                    distances.append(dist)
                
                # 거리 표준편차가 작을수록 정확도 높음
                avg_dist = sum(distances) / len(distances)
                variance = sum((d - avg_dist)**2 for d in distances) / len(distances)
                std_dev = math.sqrt(variance)
                accuracy = max(0.0, 1.0 - std_dev / avg_dist) if avg_dist > 0 else 1.0
                accuracy_scores.append(accuracy)
        
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores) if accuracy_scores else 0.0
        
        # 부드러움 계산 (포인트 간 각도 변화)
        smoothness_scores = []
        for curve_data in offset_curves:
            if len(curve_data.points) >= 3:
                angles = []
                for i in range(1, len(curve_data.points) - 1):
                    p1, p2, p3 = curve_data.points[i-1], curve_data.points[i], curve_data.points[i+1]
                    
                    v1 = (p2[0] - p1[0], p2[1] - p1[1])
                    v2 = (p3[0] - p2[0], p3[1] - p2[1])
                    
                    dot_product = v1[0] * v2[0] + v1[1] * v2[1]
                    mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
                    mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
                    
                    if mag1 > 0 and mag2 > 0:
                        cos_angle = max(-1.0, min(1.0, dot_product / (mag1 * mag2)))
                        angle = math.acos(cos_angle)
                        angles.append(angle)
                
                if angles:
                    # 각도 변화가 작을수록 부드러움 높음
                    avg_angle = sum(angles) / len(angles)
                    smoothness = max(0.0, 1.0 - avg_angle / math.pi)
                    smoothness_scores.append(smoothness)
        
        avg_smoothness = sum(smoothness_scores) / len(smoothness_scores) if smoothness_scores else 0.0
        
        # 종합 품질 점수
        quality_score = (avg_accuracy * 0.6 + avg_smoothness * 0.4)
        
        return {
            'quality_score': max(0.0, min(1.0, quality_score)),
            'accuracy': avg_accuracy,
            'smoothness': avg_smoothness
        }
