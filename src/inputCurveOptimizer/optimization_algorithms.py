#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
커브 최적화 알고리즘 구현체들
다양한 최적화 알고리즘을 제공
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
import math

class BaseOptimizationAlgorithm(ABC):
    """최적화 알고리즘 기본 클래스"""
    
    @abstractmethod
    def optimize(self, points: List[Tuple[float, float]], 
                parameters: Dict[str, Any]) -> Optional[List[Tuple[float, float]]]:
        """포인트 최적화 수행"""
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]):
        """파라미터 유효성 검증"""
        pass

class QualityBasedOptimizer(BaseOptimizationAlgorithm):
    """품질 기반 최적화 알고리즘"""
    
    def optimize(self, points: List[Tuple[float, float]], 
                parameters: Dict[str, Any]) -> Optional[List[Tuple[float, float]]]:
        """품질 기반 최적화 수행"""
        if len(points) < 3:
            return points
        
        target_quality = parameters.get('target_quality', 0.8)
        preserve_shape = parameters.get('preserve_shape', True)
        corner_detection = parameters.get('corner_detection', True)
        
        # 1단계: 모서리 포인트 감지 및 보존
        if corner_detection:
            corner_indices = self._detect_corners(points)
        else:
            corner_indices = set()
        
        # 2단계: 품질 기반 포인트 선택
        optimized_points = self._quality_based_selection(points, target_quality, corner_indices)
        
        # 3단계: 형태 보존 최적화
        if preserve_shape:
            optimized_points = self._preserve_shape_optimization(points, optimized_points)
        
        return optimized_points
    
    def validate_parameters(self, parameters: Dict[str, Any]):
        """파라미터 유효성 검증"""
        target_quality = parameters.get('target_quality', 0.8)
        if not (0.1 <= target_quality <= 1.0):
            raise ValueError("목표 품질은 0.1과 1.0 사이여야 합니다")
    
    def _detect_corners(self, points: List[Tuple[float, float]]) -> set:
        """모서리 포인트 감지"""
        if len(points) < 3:
            return set()
        
        corner_indices = set()
        angle_threshold = math.pi / 4  # 45도
        
        for i in range(1, len(points) - 1):
            p1, p2, p3 = points[i-1], points[i], points[i+1]
            
            # 각도 계산
            v1 = (p1[0] - p2[0], p1[1] - p2[1])
            v2 = (p3[0] - p2[0], p3[1] - p2[1])
            
            dot_product = v1[0] * v2[0] + v1[1] * v2[1]
            mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
            mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
            
            if mag1 > 0 and mag2 > 0:
                cos_angle = max(-1.0, min(1.0, dot_product / (mag1 * mag2)))
                angle = math.acos(cos_angle)
                
                # 각도가 임계값보다 작으면 모서리로 간주
                if angle < angle_threshold:
                    corner_indices.add(i)
        
        # 시작점과 끝점도 모서리로 간주
        corner_indices.add(0)
        corner_indices.add(len(points) - 1)
        
        return corner_indices
    
    def _quality_based_selection(self, points: List[Tuple[float, float]], 
                                target_quality: float, corner_indices: set) -> List[Tuple[float, float]]:
        """품질 기반 포인트 선택"""
        if len(points) <= 2:
            return points
        
        # 품질 점수 계산
        quality_scores = []
        for i, point in enumerate(points):
            if i in corner_indices:
                # 모서리 포인트는 높은 점수
                quality_scores.append((i, 1.0))
            else:
                # 중간 포인트는 곡률 기반 점수
                quality_score = self._calculate_point_quality(points, i)
                quality_scores.append((i, quality_score))
        
        # 품질 점수로 정렬
        quality_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 목표 품질에 따라 포인트 선택
        target_count = max(2, int(len(points) * target_quality))
        selected_indices = set()
        
        # 모서리 포인트 우선 선택
        for i in corner_indices:
            selected_indices.add(i)
            if len(selected_indices) >= target_count:
                break
        
        # 나머지는 품질 점수 순으로 선택
        for i, score in quality_scores:
            if i not in selected_indices and len(selected_indices) < target_count:
                selected_indices.add(i)
        
        # 인덱스 순서대로 정렬하여 반환
        selected_points = [points[i] for i in sorted(selected_indices)]
        return selected_points
    
    def _calculate_point_quality(self, points: List[Tuple[float, float]], index: int) -> float:
        """특정 포인트의 품질 점수 계산"""
        if index == 0 or index == len(points) - 1:
            return 1.0
        
        p1, p2, p3 = points[index-1], points[index], points[index+1]
        
        # 곡률 기반 품질 점수
        v1 = (p2[0] - p1[0], p2[1] - p1[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if mag1 > 0 and mag2 > 0:
            cos_angle = max(-1.0, min(1.0, dot_product / (mag1 * mag2)))
            angle = math.acos(cos_angle)
            
            # 각도가 클수록 곡률이 높고 품질이 높음
            quality = angle / math.pi
            return quality
        
        return 0.5
    
    def _preserve_shape_optimization(self, original_points: List[Tuple[float, float]], 
                                   optimized_points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """형태 보존 최적화"""
        if len(optimized_points) <= 2:
            return optimized_points
        
        # 원본 커브의 형태를 보존하기 위해 추가 포인트 삽입
        final_points = []
        
        for i in range(len(optimized_points) - 1):
            p1 = optimized_points[i]
            p2 = optimized_points[i + 1]
            
            final_points.append(p1)
            
            # 두 포인트 사이의 거리가 너무 크면 중간점 추가
            distance = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
            
            if distance > 1.0:  # 임계값
                # 원본 커브에서 가장 가까운 중간점 찾기
                mid_point = self._find_best_midpoint(original_points, p1, p2)
                if mid_point:
                    final_points.append(mid_point)
        
        final_points.append(optimized_points[-1])
        return final_points
    
    def _find_best_midpoint(self, original_points: List[Tuple[float, float]], 
                           p1: Tuple[float, float], p2: Tuple[float, float]) -> Optional[Tuple[float, float]]:
        """두 포인트 사이의 최적 중간점 찾기"""
        if len(original_points) < 2:
            return None
        
        # 두 포인트의 중점
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        
        # 원본 커브에서 가장 가까운 포인트 찾기
        min_distance = float('inf')
        best_point = None
        
        for point in original_points:
            dist = math.sqrt((point[0] - mid_x)**2 + (point[1] - mid_y)**2)
            if dist < min_distance:
                min_distance = dist
                best_point = point
        
        # 거리가 너무 멀면 중점 사용
        if min_distance > 0.5:
            return (mid_x, mid_y)
        
        return best_point

class PointReductionOptimizer(BaseOptimizationAlgorithm):
    """포인트 감소 최적화 알고리즘"""
    
    def optimize(self, points: List[Tuple[float, float]], 
                parameters: Dict[str, Any]) -> Optional[List[Tuple[float, float]]]:
        """포인트 감소 최적화 수행"""
        if len(points) < 3:
            return points
        
        max_reduction = parameters.get('max_point_reduction', 0.5)
        preserve_shape = parameters.get('preserve_shape', True)
        
        # 목표 포인트 수 계산
        target_count = max(2, int(len(points) * (1.0 - max_reduction)))
        
        # Douglas-Peucker 알고리즘 기반 포인트 감소
        optimized_points = self._douglas_peucker_reduction(points, target_count)
        
        # 형태 보존 최적화
        if preserve_shape:
            optimized_points = self._shape_preservation_optimization(points, optimized_points)
        
        return optimized_points
    
    def validate_parameters(self, parameters: Dict[str, Any]):
        """파라미터 유효성 검증"""
        max_reduction = parameters.get('max_point_reduction', 0.5)
        if not (0.1 <= max_reduction <= 0.9):
            raise ValueError("최대 포인트 감소 비율은 0.1과 0.9 사이여야 합니다")
    
    def _douglas_peucker_reduction(self, points: List[Tuple[float, float]], 
                                  target_count: int) -> List[Tuple[float, float]]:
        """Douglas-Peucker 알고리즘 기반 포인트 감소"""
        if len(points) <= target_count:
            return points
        
        # 허용 오차 계산 (목표 포인트 수에 따라 조정)
        tolerance = self._calculate_adaptive_tolerance(points, target_count)
        
        # 재귀적으로 포인트 감소
        optimized_indices = self._douglas_peucker_recursive(points, 0, len(points) - 1, tolerance)
        optimized_indices.add(0)
        optimized_indices.add(len(points) - 1)
        
        # 인덱스 순서대로 정렬하여 반환
        optimized_points = [points[i] for i in sorted(optimized_indices)]
        
        # 목표 포인트 수에 맞게 조정
        if len(optimized_points) > target_count:
            optimized_points = self._reduce_to_target_count(optimized_points, target_count)
        
        return optimized_points
    
    def _calculate_adaptive_tolerance(self, points: List[Tuple[float, float]], 
                                    target_count: int) -> float:
        """적응형 허용 오차 계산"""
        if len(points) <= target_count:
            return 0.0
        
        # 전체 커브의 크기 계산
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        
        curve_size = max(max_x - min_x, max_y - min_y)
        
        # 목표 포인트 수에 따라 허용 오차 조정
        reduction_ratio = 1.0 - (target_count / len(points))
        tolerance = curve_size * reduction_ratio * 0.1
        
        return max(0.001, tolerance)
    
    def _douglas_peucker_recursive(self, points: List[Tuple[float, float]], 
                                  start: int, end: int, tolerance: float) -> set:
        """Douglas-Peucker 재귀 알고리즘"""
        if end - start <= 1:
            return set()
        
        # 시작점과 끝점을 연결하는 선분
        start_point = points[start]
        end_point = points[end]
        
        # 최대 거리를 가진 포인트 찾기
        max_distance = 0.0
        max_index = start
        
        for i in range(start + 1, end):
            distance = self._point_to_line_distance(points[i], start_point, end_point)
            if distance > max_distance:
                max_distance = distance
                max_index = i
        
        result_indices = set()
        
        # 허용 오차보다 큰 거리를 가진 포인트가 있으면 재귀
        if max_distance > tolerance:
            result_indices.add(max_index)
            result_indices.update(self._douglas_peucker_recursive(points, start, max_index, tolerance))
            result_indices.update(self._douglas_peucker_recursive(points, max_index, end, tolerance))
        
        return result_indices
    
    def _point_to_line_distance(self, point: Tuple[float, float], 
                               line_start: Tuple[float, float], 
                               line_end: Tuple[float, float]) -> float:
        """점에서 선분까지의 거리 계산"""
        x0, y0 = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # 선분의 길이
        line_length = (x2 - x1)**2 + (y2 - y1)**2
        
        if line_length == 0:
            return math.sqrt((x0 - x1)**2 + (y0 - y1)**2)
        
        # 점에서 선분까지의 최단 거리
        t = max(0.0, min(1.0, ((x0 - x1) * (x2 - x1) + (y0 - y1) * (y2 - y1)) / line_length))
        
        # 선분 위의 가장 가까운 점
        closest_x = x1 + t * (x2 - x1)
        closest_y = y1 + t * (y2 - y1)
        
        return math.sqrt((x0 - closest_x)**2 + (y0 - closest_y)**2)
    
    def _reduce_to_target_count(self, points: List[Tuple[float, float]], 
                               target_count: int) -> List[Tuple[float, float]]:
        """목표 포인트 수에 맞게 감소"""
        if len(points) <= target_count:
            return points
        
        # 균등하게 샘플링
        step = len(points) / (target_count - 1)
        result = []
        
        for i in range(target_count):
            index = int(round(i * step))
            index = min(index, len(points) - 1)
            result.append(points[index])
        
        return result
    
    def _shape_preservation_optimization(self, original_points: List[Tuple[float, float]], 
                                       optimized_points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """형태 보존 최적화"""
        # 간단한 형태 보존: 원본 커브의 중요한 특징 포인트 추가
        if len(original_points) < 3 or len(optimized_points) < 2:
            return optimized_points
        
        # 원본 커브의 곡률이 높은 부분 감지
        high_curvature_indices = self._detect_high_curvature_regions(original_points)
        
        # 최적화된 커브에 중요한 포인트 추가
        enhanced_points = optimized_points.copy()
        
        for idx in high_curvature_indices:
            if idx not in [0, len(original_points) - 1]:  # 시작점과 끝점 제외
                # 최적화된 커브에서 가장 가까운 위치에 포인트 추가
                self._insert_point_at_best_location(enhanced_points, original_points[idx])
        
        return enhanced_points
    
    def _detect_high_curvature_regions(self, points: List[Tuple[float, float]]) -> set:
        """높은 곡률 영역 감지"""
        if len(points) < 3:
            return set()
        
        high_curvature_indices = set()
        curvature_threshold = 0.3
        
        for i in range(1, len(points) - 1):
            curvature = self._calculate_point_curvature(points, i)
            if curvature > curvature_threshold:
                high_curvature_indices.add(i)
        
        return high_curvature_indices
    
    def _calculate_point_curvature(self, points: List[Tuple[float, float]], index: int) -> float:
        """특정 포인트의 곡률 계산"""
        if index == 0 or index == len(points) - 1:
            return 0.0
        
        p1, p2, p3 = points[index-1], points[index], points[index+1]
        
        # 삼각형 면적 기반 곡률
        area = abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])) / 2
        
        # 세그먼트 길이
        len1 = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        len2 = math.sqrt((p3[0] - p2[0])**2 + (p3[1] - p2[1])**2)
        
        if len1 > 0 and len2 > 0:
            return min(1.0, area / (len1 * len2))
        
        return 0.0
    
    def _insert_point_at_best_location(self, points: List[Tuple[float, float]], 
                                     new_point: Tuple[float, float]):
        """최적 위치에 포인트 삽입"""
        if len(points) < 2:
            points.append(new_point)
            return
        
        # 가장 가까운 세그먼트 찾기
        min_distance = float('inf')
        best_index = 0
        
        for i in range(len(points) - 1):
            distance = self._point_to_line_distance(new_point, points[i], points[i + 1])
            if distance < min_distance:
                min_distance = distance
                best_index = i
        
        # 해당 위치에 포인트 삽입
        points.insert(best_index + 1, new_point)

class SmoothingOptimizer(BaseOptimizationAlgorithm):
    """스무딩 최적화 알고리즘"""
    
    def optimize(self, points: List[Tuple[float, float]], 
                parameters: Dict[str, Any]) -> Optional[List[Tuple[float, float]]]:
        """스무딩 최적화 수행"""
        if len(points) < 3:
            return points
        
        smoothing_factor = parameters.get('smoothing_factor', 0.5)
        preserve_shape = parameters.get('preserve_shape', True)
        iterations = parameters.get('smoothing_iterations', 3)
        
        # 스무딩 적용
        smoothed_points = points.copy()
        
        for _ in range(iterations):
            smoothed_points = self._apply_smoothing(smoothed_points, smoothing_factor)
        
        # 형태 보존 최적화
        if preserve_shape:
            smoothed_points = self._preserve_shape_after_smoothing(points, smoothed_points)
        
        return smoothed_points
    
    def validate_parameters(self, parameters: Dict[str, Any]):
        """파라미터 유효성 검증"""
        smoothing_factor = parameters.get('smoothing_factor', 0.5)
        if not (0.0 <= smoothing_factor <= 1.0):
            raise ValueError("스무딩 강도는 0.0과 1.0 사이여야 합니다")
        
        iterations = parameters.get('smoothing_iterations', 3)
        if not (1 <= iterations <= 10):
            raise ValueError("스무딩 반복 횟수는 1과 10 사이여야 합니다")
    
    def _apply_smoothing(self, points: List[Tuple[float, float]], 
                        factor: float) -> List[Tuple[float, float]]:
        """스무딩 적용"""
        if len(points) < 3:
            return points
        
        smoothed = [points[0]]  # 시작점
        
        for i in range(1, len(points) - 1):
            prev_point = points[i - 1]
            curr_point = points[i]
            next_point = points[i + 1]
            
            # 가중 평균으로 스무딩
            smooth_x = curr_point[0] * (1 - factor) + (prev_point[0] + next_point[0]) * factor / 2
            smooth_y = curr_point[1] * (1 - factor) + (prev_point[1] + next_point[1]) * factor / 2
            
            smoothed.append((smooth_x, smooth_y))
        
        smoothed.append(points[-1])  # 끝점
        return smoothed
    
    def _preserve_shape_after_smoothing(self, original_points: List[Tuple[float, float]], 
                                      smoothed_points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """스무딩 후 형태 보존"""
        if len(original_points) != len(smoothed_points):
            return smoothed_points
        
        # 원본 커브의 중요한 특징 포인트 보존
        preserved_points = []
        
        for i, (orig_point, smooth_point) in enumerate(zip(original_points, smoothed_points)):
            if i == 0 or i == len(original_points) - 1:
                # 시작점과 끝점은 원본 유지
                preserved_points.append(orig_point)
            else:
                # 중간점은 스무딩된 포인트 사용하되, 원본과의 차이가 너무 크면 조정
                distance = math.sqrt((orig_point[0] - smooth_point[0])**2 + (orig_point[1] - smooth_point[1])**2)
                
                if distance > 0.5:  # 임계값
                    # 원본과 스무딩된 포인트의 중간값 사용
                    adjusted_x = (orig_point[0] + smooth_point[0]) / 2
                    adjusted_y = (orig_point[1] + smooth_point[1]) / 2
                    preserved_points.append((adjusted_x, adjusted_y))
                else:
                    preserved_points.append(smooth_point)
        
        return preserved_points
