#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
오프셋 알고리즘 구현체들
다양한 오프셋 생성 알고리즘을 제공
"""

import numpy as np
from typing import List, Tuple, Optional, Union
import math

class OffsetCurveAlgorithm:
    """오프셋 커브 생성 알고리즘의 기본 클래스"""
    
    def __init__(self):
        self.tolerance = 0.01
        self.max_iterations = 100
    
    def generate_offset(self, curve_points: np.ndarray, offset_distance: float, 
                       **kwargs) -> np.ndarray:
        """오프셋 커브 생성 (추상 메서드)"""
        raise NotImplementedError("Subclasses must implement generate_offset")

class ArcSegmentOffsetAlgorithm(OffsetCurveAlgorithm):
    """Arc Segment 방식 오프셋 알고리즘"""
    
    def __init__(self, segment_count: int = 8, tolerance: float = 0.01):
        super().__init__()
        self.segment_count = segment_count
        self.tolerance = tolerance
    
    def generate_offset(self, curve_points: np.ndarray, offset_distance: float, 
                       **kwargs) -> np.ndarray:
        """
        Arc Segment 방식으로 오프셋 커브 생성
        
        Args:
            curve_points: 원본 커브의 제어점들 (N x 3)
            offset_distance: 오프셋 거리
            **kwargs: 추가 옵션들
            
        Returns:
            오프셋 커브의 제어점들
        """
        if len(curve_points) < 2:
            return curve_points.copy()
        
        # 각 세그먼트를 호(arc)로 근사하여 오프셋 생성
        offset_points = []
        
        for i in range(len(curve_points) - 1):
            p1 = curve_points[i]
            p2 = curve_points[i + 1]
            
            # 세그먼트의 중점과 방향 벡터 계산
            mid_point = (p1 + p2) / 2
            segment_vector = p2 - p1
            segment_length = np.linalg.norm(segment_vector)
            
            if segment_length < self.tolerance:
                continue
            
            # 세그먼트에 수직인 방향 벡터 계산
            if len(p1) == 3:  # 3D
                # Z축을 기준으로 수직 벡터 계산
                if abs(segment_vector[2]) < 0.9:
                    normal = np.cross(segment_vector, [0, 0, 1])
                else:
                    normal = np.cross(segment_vector, [1, 0, 0])
            else:  # 2D
                normal = np.array([-segment_vector[1], segment_vector[0]])
            
            normal = normal / np.linalg.norm(normal)
            
            # 오프셋 포인트 생성
            offset_point = mid_point + normal * offset_distance
            offset_points.append(offset_point)
        
        # 마지막 포인트 처리
        if len(curve_points) > 1:
            last_segment_vector = curve_points[-1] - curve_points[-2]
            if len(curve_points[-1]) == 3:
                if abs(last_segment_vector[2]) < 0.9:
                    last_normal = np.cross(last_segment_vector, [0, 0, 1])
                else:
                    last_normal = np.cross(last_segment_vector, [1, 0, 0])
            else:
                last_normal = np.array([-last_segment_vector[1], last_segment_vector[0]])
            
            last_normal = last_normal / np.linalg.norm(last_normal)
            last_offset = curve_points[-1] + last_normal * offset_distance
            offset_points.append(last_offset)
        
        return np.array(offset_points)
    
    def generate_smooth_offset(self, curve_points: np.ndarray, offset_distance: float,
                              smoothing_factor: float = 0.3, **kwargs) -> np.ndarray:
        """
        부드러운 Arc Segment 오프셋 생성
        
        Args:
            curve_points: 원본 커브의 제어점들
            offset_distance: 오프셋 거리
            smoothing_factor: 스무딩 강도 (0.0 ~ 1.0)
            **kwargs: 추가 옵션들
            
        Returns:
            부드러운 오프셋 커브의 제어점들
        """
        # 기본 오프셋 생성
        base_offset = self.generate_offset(curve_points, offset_distance, **kwargs)
        
        if len(base_offset) < 3:
            return base_offset
        
        # Laplacian 스무딩 적용
        smoothed_offset = base_offset.copy()
        
        for _ in range(int(10 * smoothing_factor)):
            for i in range(1, len(smoothed_offset) - 1):
                # 이웃 포인트들의 평균 계산
                neighbor_avg = (smoothed_offset[i-1] + smoothed_offset[i+1]) / 2
                # 스무딩 적용
                smoothed_offset[i] = (1 - smoothing_factor) * smoothed_offset[i] + \
                                   smoothing_factor * neighbor_avg
        
        return smoothed_offset

class BSplineOffsetAlgorithm(OffsetCurveAlgorithm):
    """B-Spline 방식 오프셋 알고리즘"""
    
    def __init__(self, degree: int = 3, knot_type: str = "Uniform"):
        super().__init__()
        self.degree = degree
        self.knot_type = knot_type
    
    def generate_offset(self, curve_points: np.ndarray, offset_distance: float,
                       **kwargs) -> np.ndarray:
        """
        B-Spline 방식으로 오프셋 커브 생성
        
        Args:
            curve_points: 원본 커브의 제어점들
            offset_distance: 오프셋 거리
            **kwargs: 추가 옵션들
            
        Returns:
            오프셋 커브의 제어점들
        """
        if len(curve_points) < self.degree + 1:
            return curve_points.copy()
        
        # B-Spline 노트 벡터 생성
        knots = self._generate_knots(len(curve_points), self.degree)
        
        # 각 제어점에서의 접선 벡터 계산
        tangent_vectors = self._calculate_tangents(curve_points, knots, self.degree)
        
        # 오프셋 포인트 생성
        offset_points = []
        for i, (point, tangent) in enumerate(zip(curve_points, tangent_vectors)):
            if np.linalg.norm(tangent) > self.tolerance:
                # 접선에 수직인 방향 벡터 계산
                if len(point) == 3:  # 3D
                    # 임의의 벡터와 cross product로 수직 벡터 생성
                    if abs(tangent[2]) < 0.9:
                        normal = np.cross(tangent, [0, 0, 1])
                    else:
                        normal = np.cross(tangent, [1, 0, 0])
                else:  # 2D
                    normal = np.array([-tangent[1], tangent[0]])
                
                normal = normal / np.linalg.norm(normal)
                offset_point = point + normal * offset_distance
                offset_points.append(offset_point)
            else:
                offset_points.append(point)
        
        return np.array(offset_points)
    
    def _generate_knots(self, num_points: int, degree: int) -> np.ndarray:
        """B-Spline 노트 벡터 생성"""
        num_knots = num_points + degree + 1
        
        if self.knot_type == "Uniform":
            # 균등 노트 벡터
            knots = np.linspace(0, 1, num_knots)
        elif self.knot_type == "Chord Length":
            # 코드 길이 기반 노트 벡터
            knots = self._chord_length_knots(num_points, degree)
        elif self.knot_type == "Centripetal":
            # 중심력 기반 노트 벡터
            knots = self._centripetal_knots(num_points, degree)
        else:
            knots = np.linspace(0, 1, num_knots)
        
        return knots
    
    def _chord_length_knots(self, num_points: int, degree: int) -> np.ndarray:
        """코드 길이 기반 노트 벡터"""
        # 실제 구현에서는 제어점 간 거리를 계산해야 함
        # 여기서는 간단한 예시로 구현
        knots = np.zeros(num_points + degree + 1)
        
        # 내부 노트들
        for i in range(degree + 1, num_points):
            knots[i] = knots[i-1] + 1.0 / (num_points - degree)
        
        # 끝 노트들
        knots[num_points:] = 1.0
        
        return knots
    
    def _centripetal_knots(self, num_points: int, degree: int) -> np.ndarray:
        """중심력 기반 노트 벡터"""
        # 실제 구현에서는 제어점 간 거리의 제곱근을 계산해야 함
        knots = np.zeros(num_points + degree + 1)
        
        # 내부 노트들
        for i in range(degree + 1, num_points):
            knots[i] = knots[i-1] + 1.0 / (num_points - degree)
        
        # 끝 노트들
        knots[num_points:] = 1.0
        
        return knots
    
    def _calculate_tangents(self, points: np.ndarray, knots: np.ndarray, 
                           degree: int) -> List[np.ndarray]:
        """B-Spline 제어점에서의 접선 벡터 계산"""
        tangents = []
        
        for i in range(len(points)):
            if i == 0:
                # 첫 번째 포인트
                tangent = points[1] - points[0]
            elif i == len(points) - 1:
                # 마지막 포인트
                tangent = points[-1] - points[-2]
            else:
                # 중간 포인트들
                tangent = (points[i+1] - points[i-1]) / 2
            
            # 정규화
            norm = np.linalg.norm(tangent)
            if norm > self.tolerance:
                tangent = tangent / norm
            else:
                tangent = np.zeros_like(tangent)
            
            tangents.append(tangent)
        
        return tangents

class AdaptiveOffsetAlgorithm(OffsetCurveAlgorithm):
    """적응형 오프셋 알고리즘"""
    
    def __init__(self, curvature_threshold: float = 0.1):
        super().__init__()
        self.curvature_threshold = curvature_threshold
    
    def generate_offset(self, curve_points: np.ndarray, offset_distance: float,
                       **kwargs) -> np.ndarray:
        """
        곡률에 따라 거리를 자동 조정하는 적응형 오프셋 생성
        
        Args:
            curve_points: 원본 커브의 제어점들
            offset_distance: 기본 오프셋 거리
            **kwargs: 추가 옵션들
            
        Returns:
            적응형 오프셋 커브의 제어점들
        """
        if len(curve_points) < 3:
            return curve_points.copy()
        
        # 각 포인트에서의 곡률 계산
        curvatures = self._calculate_curvatures(curve_points)
        
        # 곡률에 따른 적응형 거리 계산
        adaptive_distances = []
        for curvature in curvatures:
            if curvature > self.curvature_threshold:
                # 높은 곡률에서는 거리를 줄임
                factor = max(0.1, 1.0 - curvature / self.curvature_threshold)
                adaptive_distances.append(offset_distance * factor)
            else:
                # 낮은 곡률에서는 기본 거리 사용
                adaptive_distances.append(offset_distance)
        
        # 적응형 거리로 오프셋 생성
        offset_points = []
        for i, (point, distance) in enumerate(zip(curve_points, adaptive_distances)):
            if i == 0 or i == len(curve_points) - 1:
                # 끝점들은 이웃과의 방향으로 오프셋
                if i == 0:
                    direction = curve_points[1] - point
                else:
                    direction = point - curve_points[i-1]
            else:
                # 중간점들은 이웃들의 평균 방향으로 오프셋
                direction = (curve_points[i+1] - curve_points[i-1]) / 2
            
            if np.linalg.norm(direction) > self.tolerance:
                direction = direction / np.linalg.norm(direction)
                
                # 수직 방향 계산
                if len(point) == 3:  # 3D
                    if abs(direction[2]) < 0.9:
                        normal = np.cross(direction, [0, 0, 1])
                    else:
                        normal = np.cross(direction, [1, 0, 0])
                else:  # 2D
                    normal = np.array([-direction[1], direction[0]])
                
                normal = normal / np.linalg.norm(normal)
                offset_point = point + normal * distance
                offset_points.append(offset_point)
            else:
                offset_points.append(point)
        
        return np.array(offset_points)
    
    def _calculate_curvatures(self, points: np.ndarray) -> List[float]:
        """포인트에서의 곡률 계산"""
        curvatures = []
        
        for i in range(len(points)):
            if i == 0 or i == len(points) - 1:
                # 끝점들은 0 곡률
                curvatures.append(0.0)
            else:
                # 중간점들의 곡률 계산
                p1 = points[i-1]
                p2 = points[i]
                p3 = points[i+1]
                
                # 두 벡터
                v1 = p2 - p1
                v2 = p3 - p2
                
                # 벡터 길이
                l1 = np.linalg.norm(v1)
                l2 = np.linalg.norm(v2)
                
                if l1 > self.tolerance and l2 > self.tolerance:
                    # 정규화
                    v1_norm = v1 / l1
                    v2_norm = v2 / l2
                    
                    # 각도 계산
                    cos_angle = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)
                    angle = np.arccos(cos_angle)
                    
                    # 곡률 (각도 / 거리)
                    curvature = angle / ((l1 + l2) / 2)
                else:
                    curvature = 0.0
                
                curvatures.append(curvature)
        
        return curvatures

class OffsetCurveFactory:
    """오프셋 커브 알고리즘 팩토리 클래스"""
    
    @staticmethod
    def create_algorithm(algorithm_type: str, **kwargs) -> OffsetCurveAlgorithm:
        """
        알고리즘 타입에 따라 적절한 오프셋 알고리즘 생성
        
        Args:
            algorithm_type: 알고리즘 타입 ("arc_segment", "bspline", "adaptive")
            **kwargs: 알고리즘별 설정 파라미터들
            
        Returns:
            오프셋 알고리즘 인스턴스
        """
        if algorithm_type == "arc_segment":
            return ArcSegmentOffsetAlgorithm(
                segment_count=kwargs.get('segment_count', 8),
                tolerance=kwargs.get('tolerance', 0.01)
            )
        elif algorithm_type == "bspline":
            return BSplineOffsetAlgorithm(
                degree=kwargs.get('degree', 3),
                knot_type=kwargs.get('knot_type', 'Uniform')
            )
        elif algorithm_type == "adaptive":
            return AdaptiveOffsetAlgorithm(
                curvature_threshold=kwargs.get('curvature_threshold', 0.1)
            )
        else:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")

# 기존 코드 유지
class OffsetCurveGenerator:
    """오프셋 커브 생성기"""
    
    def __init__(self, algorithm: OffsetCurveAlgorithm):
        self.algorithm = algorithm
    
    def generate_offset_curve(self, curve_points: np.ndarray, offset_distance: float,
                             **kwargs) -> np.ndarray:
        """오프셋 커브 생성"""
        return self.algorithm.generate_offset(curve_points, offset_distance, **kwargs)
    
    def generate_smooth_offset_curve(self, curve_points: np.ndarray, offset_distance: float,
                                   smoothing_factor: float = 0.3, **kwargs) -> np.ndarray:
        """부드러운 오프셋 커브 생성"""
        if hasattr(self.algorithm, 'generate_smooth_offset'):
            return self.algorithm.generate_smooth_offset(curve_points, offset_distance, 
                                                      smoothing_factor, **kwargs)
        else:
            # 기본 오프셋 생성 후 스무딩 적용
            base_offset = self.algorithm.generate_offset(curve_points, offset_distance, **kwargs)
            return self._apply_smoothing(base_offset, smoothing_factor)
    
    def _apply_smoothing(self, points: np.ndarray, smoothing_factor: float) -> np.ndarray:
        """포인트에 스무딩 적용"""
        if len(points) < 3:
            return points
        
        smoothed = points.copy()
        
        for _ in range(5):  # 5회 반복
            for i in range(1, len(smoothed) - 1):
                neighbor_avg = (smoothed[i-1] + smoothed[i+1]) / 2
                smoothed[i] = (1 - smoothing_factor) * smoothed[i] + \
                             smoothing_factor * neighbor_avg
        
        return smoothed

# 사용 예시
def create_offset_curve_example():
    """오프셋 커브 생성 예시"""
    # 샘플 커브 포인트 (2D)
    curve_points = np.array([
        [0, 0], [1, 1], [2, 0], [3, 1], [4, 0],
        [5, 1], [6, 0], [7, 1], [8, 0], [9, 1]
    ])
    
    # Arc Segment 방식
    arc_algorithm = OffsetCurveFactory.create_algorithm("arc_segment", segment_count=8)
    arc_generator = OffsetCurveGenerator(arc_algorithm)
    arc_offset = arc_generator.generate_offset_curve(curve_points, 0.5)
    
    # B-Spline 방식
    bspline_algorithm = OffsetCurveFactory.create_algorithm("bspline", degree=3)
    bspline_generator = OffsetCurveGenerator(bspline_algorithm)
    bspline_offset = bspline_generator.generate_offset_curve(curve_points, 0.5)
    
    # 적응형 방식
    adaptive_algorithm = OffsetCurveFactory.create_algorithm("adaptive", curvature_threshold=0.1)
    adaptive_generator = OffsetCurveGenerator(adaptive_algorithm)
    adaptive_offset = adaptive_generator.generate_offset_curve(curve_points, 0.5)
    
    return {
        'arc_segment': arc_offset,
        'bspline': bspline_offset,
        'adaptive': adaptive_offset
    }

if __name__ == "__main__":
    # 테스트 실행
    results = create_offset_curve_example()
    print("Offset curves generated successfully!")
    print(f"Arc Segment: {len(results['arc_segment'])} points")
    print(f"B-Spline: {len(results['bspline'])} points")
    print(f"Adaptive: {len(results['adaptive'])} points")
