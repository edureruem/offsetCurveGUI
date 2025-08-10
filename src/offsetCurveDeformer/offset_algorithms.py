#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
오프셋 알고리즘 구현체들
다양한 오프셋 생성 알고리즘을 제공
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
import math

class BaseOffsetAlgorithm(ABC):
    """오프셋 알고리즘 기본 클래스"""
    
    @abstractmethod
    def generate_offset(self, points: List[Tuple[float, float]], 
                       distance: float, parameters: Dict[str, Any]) -> Optional[List[Tuple[float, float]]]:
        """포인트로부터 오프셋 커브 생성"""
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]):
        """파라미터 유효성 검증"""
        pass

class ParallelOffsetAlgorithm(BaseOffsetAlgorithm):
    """평행 오프셋 알고리즘"""
    
    def generate_offset(self, points: List[Tuple[float, float]], 
                       distance: float, parameters: Dict[str, Any]) -> Optional[List[Tuple[float, float]]]:
        """평행 오프셋 커브 생성"""
        if len(points) < 2:
            return None
        
        smooth_curves = parameters.get('smooth_curves', True)
        corner_handling = parameters.get('corner_handling', 'adaptive')
        
        # 각 세그먼트에 대한 법선 벡터 계산
        normals = self._calculate_normals(points)
        
        # 오프셋 포인트 생성
        offset_points = []
        for i, point in enumerate(points):
            if i == 0 or i == len(points) - 1:
                # 시작점과 끝점은 단순 이동
                normal = normals[i] if i < len(normals) else normals[i-1]
                offset_point = (point[0] + normal[0] * distance, point[1] + normal[1] * distance)
            else:
                # 중간점은 두 세그먼트의 평균 법선 사용
                prev_normal = normals[i-1]
                curr_normal = normals[i]
                
                # 법선 벡터 평균화
                avg_normal_x = (prev_normal[0] + curr_normal[0]) / 2
                avg_normal_y = (prev_normal[1] + curr_normal[1]) / 2
                
                # 정규화
                mag = math.sqrt(avg_normal_x**2 + avg_normal_y**2)
                if mag > 0:
                    avg_normal_x /= mag
                    avg_normal_y /= mag
                
                offset_point = (point[0] + avg_normal_x * distance, point[1] + avg_normal_y * distance)
            
            offset_points.append(offset_point)
        
        # 모서리 처리
        if corner_handling != 'none':
            offset_points = self._handle_corners(offset_points, corner_handling, parameters)
        
        # 부드럽게 처리
        if smooth_curves:
            offset_points = self._smooth_offset_curve(offset_points, parameters)
        
        return offset_points
    
    def validate_parameters(self, parameters: Dict[str, Any]):
        """파라미터 유효성 검증"""
        corner_handling = parameters.get('corner_handling', 'adaptive')
        if corner_handling not in ['none', 'round', 'adaptive']:
            raise ValueError(f"지원하지 않는 모서리 처리 방식입니다: {corner_handling}")
    
    def _calculate_normals(self, points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """각 세그먼트의 법선 벡터 계산"""
        normals = []
        
        for i in range(len(points) - 1):
            p1, p2 = points[i], points[i + 1]
            
            # 세그먼트 벡터
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            
            # 법선 벡터 (시계 반대 방향)
            normal_x = -dy
            normal_y = dx
            
            # 정규화
            mag = math.sqrt(normal_x**2 + normal_y**2)
            if mag > 0:
                normal_x /= mag
                normal_y /= mag
            
            normals.append((normal_x, normal_y))
        
        return normals
    
    def _handle_corners(self, points: List[Tuple[float, float]], 
                        handling: str, parameters: Dict[str, Any]) -> List[Tuple[float, float]]:
        """모서리 처리"""
        if handling == 'none' or len(points) < 3:
            return points
        
        if handling == 'round':
            return self._round_corners(points, parameters)
        elif handling == 'adaptive':
            return self._adaptive_corner_handling(points, parameters)
        
        return points
    
    def _round_corners(self, points: List[Tuple[float, float]], 
                       parameters: Dict[str, Any]) -> List[Tuple[float, float]]:
        """모서리 둥글게 처리"""
        if len(points) < 3:
            return points
        
        rounded_points = [points[0]]  # 시작점
        
        for i in range(1, len(points) - 1):
            prev_point = points[i - 1]
            curr_point = points[i]
            next_point = points[i + 1]
            
            # 각도 계산
            angle = self._calculate_angle(prev_point, curr_point, next_point)
            
            # 각도가 임계값보다 작으면 둥글게 처리
            threshold = parameters.get('corner_threshold', math.pi / 6)  # 30도
            if angle < threshold:
                # 베지어 곡선으로 둥글게 처리
                rounded = self._create_rounded_corner(prev_point, curr_point, next_point, parameters)
                rounded_points.extend(rounded)
            else:
                rounded_points.append(curr_point)
        
        rounded_points.append(points[-1])  # 끝점
        return rounded_points
    
    def _adaptive_corner_handling(self, points: List[Tuple[float, float]], 
                                 parameters: Dict[str, Any]) -> List[Tuple[float, float]]:
        """적응형 모서리 처리"""
        if len(points) < 3:
            return points
        
        # 곡률 기반으로 모서리 처리 방식 결정
        curvature_threshold = parameters.get('curvature_threshold', 0.5)
        
        processed_points = [points[0]]
        
        for i in range(1, len(points) - 1):
            prev_point = points[i - 1]
            curr_point = points[i]
            next_point = points[i + 1]
            
            # 곡률 계산
            curvature = self._calculate_curvature(prev_point, curr_point, next_point)
            
            if curvature > curvature_threshold:
                # 높은 곡률: 둥글게 처리
                rounded = self._create_rounded_corner(prev_point, curr_point, next_point, parameters)
                processed_points.extend(rounded)
            else:
                # 낮은 곡률: 그대로 유지
                processed_points.append(curr_point)
        
        processed_points.append(points[-1])
        return processed_points
    
    def _smooth_offset_curve(self, points: List[Tuple[float, float]], 
                            parameters: Dict[str, Any]) -> List[Tuple[float, float]]:
        """오프셋 커브 부드럽게 처리"""
        if len(points) < 3:
            return points
        
        smoothing_factor = parameters.get('smoothing_factor', 0.3)
        iterations = parameters.get('smoothing_iterations', 2)
        
        smoothed_points = points.copy()
        
        for _ in range(iterations):
            smoothed_points = self._apply_smoothing(smoothed_points, smoothing_factor)
        
        return smoothed_points
    
    def _calculate_angle(self, p1: Tuple[float, float], p2: Tuple[float, float], 
                        p3: Tuple[float, float]) -> float:
        """세 점으로 이루어진 각도 계산"""
        v1 = (p1[0] - p2[0], p1[1] - p2[1])
        v2 = (p3[0] - p2[0], p3[1] - p2[1])
        
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = math.sqrt(v1[0]**2 + v1[1]**2)
        mag2 = math.sqrt(v2[0]**2 + v2[1]**2)
        
        if mag1 > 0 and mag2 > 0:
            cos_angle = max(-1.0, min(1.0, dot_product / (mag1 * mag2)))
            return math.acos(cos_angle)
        
        return 0.0
    
    def _calculate_curvature(self, p1: Tuple[float, float], p2: Tuple[float, float], 
                            p3: Tuple[float, float]) -> float:
        """곡률 계산"""
        # 삼각형 면적 기반 곡률 추정
        area = abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])) / 2
        
        # 세그먼트 길이
        len1 = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        len2 = math.sqrt((p3[0] - p2[0])**2 + (p3[1] - p2[1])**2)
        
        if len1 > 0 and len2 > 0:
            # 곡률 = 면적 / (길이1 * 길이2)
            return min(1.0, area / (len1 * len2))
        
        return 0.0
    
    def _create_rounded_corner(self, p1: Tuple[float, float], p2: Tuple[float, float], 
                              p3: Tuple[float, float], parameters: Dict[str, Any]) -> List[Tuple[float, float]]:
        """둥근 모서리 생성"""
        # 간단한 베지어 곡선으로 둥글게 처리
        control_points = 3
        rounded = []
        
        for i in range(1, control_points):
            t = i / control_points
            
            # 베지어 곡선 계산
            x = (1-t)**2 * p1[0] + 2*(1-t)*t * p2[0] + t**2 * p3[0]
            y = (1-t)**2 * p1[1] + 2*(1-t)*t * p2[1] + t**2 * p3[1]
            
            rounded.append((x, y))
        
        return rounded
    
    def _apply_smoothing(self, points: List[Tuple[float, float]], factor: float) -> List[Tuple[float, float]]:
        """스무딩 적용"""
        if len(points) < 3:
            return points
        
        smoothed = [points[0]]
        
        for i in range(1, len(points) - 1):
            prev_point = points[i - 1]
            curr_point = points[i]
            next_point = points[i + 1]
            
            # 가중 평균으로 스무딩
            smooth_x = curr_point[0] * (1 - factor) + (prev_point[0] + next_point[0]) * factor / 2
            smooth_y = curr_point[1] * (1 - factor) + (prev_point[1] + next_point[1]) * factor / 2
            
            smoothed.append((smooth_x, smooth_y))
        
        smoothed.append(points[-1])
        return smoothed

class PerpendicularOffsetAlgorithm(BaseOffsetAlgorithm):
    """수직 오프셋 알고리즘"""
    
    def generate_offset(self, points: List[Tuple[float, float]], 
                       distance: float, parameters: Dict[str, Any]) -> Optional[List[Tuple[float, float]]]:
        """수직 오프셋 커브 생성"""
        if len(points) < 2:
            return None
        
        # 각 포인트에서 수직 방향으로 오프셋
        offset_points = []
        
        for i, point in enumerate(points):
            if i == 0:
                # 시작점: 첫 번째 세그먼트의 수직 방향
                next_point = points[i + 1]
                dx = next_point[0] - point[0]
                dy = next_point[1] - point[1]
                
                # 수직 벡터 (시계 반대 방향)
                normal_x = -dy
                normal_y = dx
            elif i == len(points) - 1:
                # 끝점: 마지막 세그먼트의 수직 방향
                prev_point = points[i - 1]
                dx = point[0] - prev_point[0]
                dy = point[1] - prev_point[1]
                
                # 수직 벡터 (시계 반대 방향)
                normal_x = -dy
                normal_y = dx
            else:
                # 중간점: 두 세그먼트의 평균 수직 방향
                prev_point = points[i - 1]
                next_point = points[i + 1]
                
                # 이전 세그먼트 수직 벡터
                dx1 = point[0] - prev_point[0]
                dy1 = point[1] - prev_point[1]
                normal1_x = -dy1
                normal1_y = dx1
                
                # 다음 세그먼트 수직 벡터
                dx2 = next_point[0] - point[0]
                dy2 = next_point[1] - point[1]
                normal2_x = -dy2
                normal2_y = dx2
                
                # 평균 수직 벡터
                normal_x = (normal1_x + normal2_x) / 2
                normal_y = (normal1_y + normal2_y) / 2
            
            # 정규화
            mag = math.sqrt(normal_x**2 + normal_y**2)
            if mag > 0:
                normal_x /= mag
                normal_y /= mag
            
            # 오프셋 포인트 생성
            offset_point = (point[0] + normal_x * distance, point[1] + normal_y * distance)
            offset_points.append(offset_point)
        
        return offset_points
    
    def validate_parameters(self, parameters: Dict[str, Any]):
        """파라미터 유효성 검증"""
        # 수직 오프셋은 특별한 파라미터가 필요하지 않음
        pass

class AdaptiveOffsetAlgorithm(BaseOffsetAlgorithm):
    """적응형 오프셋 알고리즘"""
    
    def generate_offset(self, points: List[Tuple[float, float]], 
                       distance: float, parameters: Dict[str, Any]) -> Optional[List[Tuple[float, float]]]:
        """적응형 오프셋 커브 생성"""
        if len(points) < 2:
            return None
        
        # 곡률 기반으로 오프셋 거리 조정
        curvature_threshold = parameters.get('curvature_threshold', 0.3)
        max_distance_factor = parameters.get('max_distance_factor', 2.0)
        
        offset_points = []
        
        for i, point in enumerate(points):
            if i == 0 or i == len(points) - 1:
                # 시작점과 끝점은 기본 거리 사용
                adjusted_distance = distance
            else:
                # 중간점은 곡률에 따라 거리 조정
                curvature = self._calculate_point_curvature(points, i)
                
                if curvature > curvature_threshold:
                    # 높은 곡률: 거리 감소
                    adjusted_distance = distance * (1 - curvature * 0.5)
                else:
                    # 낮은 곡률: 거리 증가 (최대 제한)
                    adjusted_distance = min(distance * max_distance_factor, 
                                        distance * (1 + (1 - curvature) * 0.3))
            
            # 수직 방향 계산
            if i == 0:
                next_point = points[i + 1]
                dx = next_point[0] - point[0]
                dy = next_point[1] - point[1]
            elif i == len(points) - 1:
                prev_point = points[i - 1]
                dx = point[0] - prev_point[0]
                dy = point[1] - prev_point[1]
            else:
                # 두 세그먼트의 평균 방향
                prev_point = points[i - 1]
                next_point = points[i + 1]
                dx = (next_point[0] - prev_point[0]) / 2
                dy = (next_point[1] - prev_point[1]) / 2
            
            # 수직 벡터
            normal_x = -dy
            normal_y = dx
            
            # 정규화
            mag = math.sqrt(normal_x**2 + normal_y**2)
            if mag > 0:
                normal_x /= mag
                normal_y /= mag
            
            # 오프셋 포인트 생성
            offset_point = (point[0] + normal_x * adjusted_distance, 
                          point[1] + normal_y * adjusted_distance)
            offset_points.append(offset_point)
        
        return offset_points
    
    def validate_parameters(self, parameters: Dict[str, Any]):
        """파라미터 유효성 검증"""
        curvature_threshold = parameters.get('curvature_threshold', 0.3)
        if not (0.0 <= curvature_threshold <= 1.0):
            raise ValueError("곡률 임계값은 0.0과 1.0 사이여야 합니다")
        
        max_distance_factor = parameters.get('max_distance_factor', 2.0)
        if max_distance_factor <= 1.0:
            raise ValueError("최대 거리 계수는 1.0보다 커야 합니다")
    
    def _calculate_point_curvature(self, points: List[Tuple[float, float]], index: int) -> float:
        """특정 포인트의 곡률 계산"""
        if index == 0 or index == len(points) - 1:
            return 0.0
        
        prev_point = points[index - 1]
        curr_point = points[index]
        next_point = points[index + 1]
        
        # 삼각형 면적 기반 곡률
        area = abs((curr_point[0] - prev_point[0]) * (next_point[1] - prev_point[1]) - 
                   (next_point[0] - prev_point[0]) * (curr_point[1] - prev_point[1])) / 2
        
        # 세그먼트 길이
        len1 = math.sqrt((curr_point[0] - prev_point[0])**2 + (curr_point[1] - prev_point[1])**2)
        len2 = math.sqrt((next_point[0] - curr_point[0])**2 + (next_point[1] - curr_point[1])**2)
        
        if len1 > 0 and len2 > 0:
            return min(1.0, area / (len1 * len2))
        
        return 0.0
