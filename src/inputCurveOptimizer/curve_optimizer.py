#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
커브 최적화 메인 클래스
다양한 최적화 알고리즘을 조율하여 커브 최적화 수행
"""

import time
from typing import Dict, Any, List, Tuple
import math

from ..core.interfaces import ICurveOptimizer, CurveData, OptimizationResult
from ..core.exceptions import OptimizationError
from .optimization_algorithms import (
    QualityBasedOptimizer,
    PointReductionOptimizer,
    SmoothingOptimizer
)

class CurveOptimizer(ICurveOptimizer):
    """커브 최적화 메인 클래스"""
    
    def __init__(self):
        self.optimizers = {
            'quality': QualityBasedOptimizer(),
            'reduction': PointReductionOptimizer(),
            'smoothing': SmoothingOptimizer()
        }
    
    def optimize_curve(self, curve: CurveData, parameters: Dict[str, Any]) -> OptimizationResult:
        """커브 최적화 수행"""
        start_time = time.time()
        
        try:
            # 파라미터 검증
            self._validate_parameters(parameters)
            
            # 최적화 알고리즘 선택
            algorithm_name = parameters.get('algorithm', 'quality')
            if algorithm_name not in self.optimizers:
                raise OptimizationError(f"지원하지 않는 최적화 알고리즘입니다: {algorithm_name}")
            
            optimizer = self.optimizers[algorithm_name]
            
            # 원본 포인트 수 저장
            original_point_count = len(curve.points)
            
            # 최적화 수행
            optimized_points = optimizer.optimize(curve.points, parameters)
            
            if not optimized_points:
                raise OptimizationError("최적화 결과가 비어있습니다")
            
            # 최적화된 커브 데이터 생성
            optimized_curve = CurveData(
                points=optimized_points,
                metadata={
                    **curve.metadata,
                    'optimization_algorithm': algorithm_name,
                    'original_point_count': original_point_count,
                    'optimized_point_count': len(optimized_points),
                    'reduction_ratio': 1.0 - (len(optimized_points) / original_point_count)
                },
                format=curve.format,
                source_path=curve.source_path
            )
            
            # 품질 메트릭 계산
            quality_metrics = self._calculate_quality_metrics(curve.points, optimized_points)
            
            processing_time = time.time() - start_time
            
            return OptimizationResult(
                optimized_curve=optimized_curve,
                original_point_count=original_point_count,
                optimized_point_count=len(optimized_points),
                quality_metrics=quality_metrics,
                processing_time=processing_time
            )
            
        except Exception as e:
            if isinstance(e, OptimizationError):
                raise
            raise OptimizationError(f"커브 최적화 중 오류가 발생했습니다: {e}")
    
    def get_optimization_parameters(self) -> Dict[str, Any]:
        """최적화 파라미터 스키마 반환"""
        return {
            'algorithm': {
                'type': 'choice',
                'options': ['quality', 'reduction', 'smoothing'],
                'default': 'quality',
                'description': '최적화 알고리즘 선택'
            },
            'target_quality': {
                'type': 'float',
                'min': 0.1,
                'max': 1.0,
                'default': 0.8,
                'description': '목표 품질 (높을수록 더 정확)'
            },
            'smoothing_factor': {
                'type': 'float',
                'min': 0.0,
                'max': 1.0,
                'default': 0.5,
                'description': '스무딩 강도'
            },
            'max_point_reduction': {
                'type': 'float',
                'min': 0.1,
                'max': 0.9,
                'default': 0.5,
                'description': '최대 포인트 감소 비율'
            },
            'preserve_shape': {
                'type': 'bool',
                'default': True,
                'description': '원본 형태 보존'
            },
            'corner_detection': {
                'type': 'bool',
                'default': True,
                'description': '모서리 포인트 감지 및 보존'
            }
        }
    
    def validate_optimization_parameters(self, parameters: Dict[str, Any]) -> bool:
        """최적화 파라미터 유효성 검증"""
        try:
            self._validate_parameters(parameters)
            return True
        except OptimizationError:
            return False
    
    def _validate_parameters(self, parameters: Dict[str, Any]):
        """파라미터 유효성 검증"""
        required_params = ['algorithm']
        for param in required_params:
            if param not in parameters:
                raise OptimizationError(f"필수 파라미터가 누락되었습니다: {param}")
        
        # 알고리즘 검증
        algorithm = parameters.get('algorithm')
        if algorithm not in self.optimizers:
            raise OptimizationError(f"지원하지 않는 최적화 알고리즘입니다: {algorithm}")
        
        # 알고리즘별 추가 검증
        self.optimizers[algorithm].validate_parameters(parameters)
    
    def _calculate_quality_metrics(self, original_points: List[Tuple[float, float]], 
                                 optimized_points: List[Tuple[float, float]]) -> Dict[str, float]:
        """품질 메트릭 계산"""
        if not optimized_points:
            return {'quality_score': 0.0, 'shape_preservation': 0.0, 'smoothness': 0.0}
        
        # 형태 보존도 계산
        shape_preservation = self._calculate_shape_preservation(original_points, optimized_points)
        
        # 부드러움 계산
        smoothness = self._calculate_smoothness(optimized_points)
        
        # 종합 품질 점수
        quality_score = (shape_preservation * 0.7 + smoothness * 0.3)
        
        return {
            'quality_score': max(0.0, min(1.0, quality_score)),
            'shape_preservation': shape_preservation,
            'smoothness': smoothness
        }
    
    def _calculate_shape_preservation(self, original_points: List[Tuple[float, float]], 
                                    optimized_points: List[Tuple[float, float]]) -> float:
        """형태 보존도 계산"""
        if len(original_points) < 2 or len(optimized_points) < 2:
            return 0.0
        
        # 원본과 최적화된 커브 간의 거리 계산
        # 간단한 방법: 각 원본 포인트에서 가장 가까운 최적화된 포인트까지의 거리
        total_distance = 0.0
        valid_points = 0
        
        for orig_point in original_points:
            min_distance = float('inf')
            
            for opt_point in optimized_points:
                dist = math.sqrt((orig_point[0] - opt_point[0])**2 + (orig_point[1] - opt_point[1])**2)
                min_distance = min(min_distance, dist)
            
            if min_distance != float('inf'):
                total_distance += min_distance
                valid_points += 1
        
        if valid_points == 0:
            return 0.0
        
        avg_distance = total_distance / valid_points
        
        # 거리가 작을수록 형태 보존도 높음
        # 임계값 기반으로 정규화 (거리 1.0을 기준으로)
        shape_preservation = max(0.0, 1.0 - avg_distance)
        
        return shape_preservation
    
    def _calculate_smoothness(self, points: List[Tuple[float, float]]) -> float:
        """부드러움 계산"""
        if len(points) < 3:
            return 0.0
        
        # 포인트 간 각도 변화 계산
        angles = []
        for i in range(1, len(points) - 1):
            p1, p2, p3 = points[i-1], points[i], points[i+1]
            
            v1 = (p2[0] - p1[0], p2[1] - p1[1])
            v2 = (p3[0] - p2[0], p3[1] - p2[1])
            
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = max(-1.0, min(1.0, dot_product / (mag1 * mag2)))
                angle = math.acos(cos_angle)
                angles.append(angle)
        
        if not angles:
            return 0.0
        
        # 각도 변화가 작을수록 부드러움 높음
        avg_angle = sum(angles) / len(angles)
        smoothness = max(0.0, 1.0 - avg_angle / math.pi)
        
        return smoothness
