#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
컨텍스트 인식 도구
입력 커브의 특성을 분석하여 자동으로 최적의 설정을 제안하는 도구
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, List, Tuple
import math

class ContextAwareTools:
    """컨텍스트 인식 도구 클래스"""
    
    def __init__(self, parent: tk.Widget, on_apply_suggestions: Callable[[Dict[str, Any]], None]):
        self.parent = parent
        self.on_apply_suggestions = on_apply_suggestions
        self.curve_analysis = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """UI 컴포넌트 설정"""
        # 메인 프레임
        self.main_frame = ttk.LabelFrame(self.parent, text="컨텍스트 인식 도구", padding="10")
        
        # 커브 분석 섹션
        self.setup_analysis_section()
        
        # 자동 설정 제안 섹션
        self.setup_suggestions_section()
        
        # 적용 버튼
        apply_button = ttk.Button(
            self.main_frame,
            text="제안된 설정 적용",
            command=self.apply_suggestions
        )
        apply_button.grid(row=2, column=0, columnspan=2, pady=(20, 0))
    
    def setup_analysis_section(self):
        """커브 분석 섹션 설정"""
        analysis_frame = ttk.LabelFrame(
            self.main_frame, 
            text="커브 특성 분석", 
            padding="5"
        )
        analysis_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 분석 실행 버튼
        analyze_button = ttk.Button(
            analysis_frame,
            text="커브 분석 실행",
            command=self.analyze_curve
        )
        analyze_button.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 분석 결과 표시
        self.analysis_text = tk.Text(analysis_frame, height=8, width=40, state=tk.DISABLED)
        analysis_scrollbar = ttk.Scrollbar(analysis_frame, orient=tk.VERTICAL, command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=analysis_scrollbar.set)
        
        self.analysis_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        analysis_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(1, weight=1)
    
    def setup_suggestions_section(self):
        """자동 설정 제안 섹션 설정"""
        suggestions_frame = ttk.LabelFrame(
            self.main_frame, 
            text="자동 설정 제안", 
            padding="5"
        )
        suggestions_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 제안된 설정 표시
        self.suggestions_text = tk.Text(suggestions_frame, height=8, width=40, state=tk.DISABLED)
        suggestions_scrollbar = ttk.Scrollbar(suggestions_frame, orient=tk.VERTICAL, command=self.suggestions_text.yview)
        self.suggestions_text.configure(yscrollcommand=suggestions_scrollbar.set)
        
        self.suggestions_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        suggestions_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        suggestions_frame.columnconfigure(0, weight=1)
        suggestions_frame.rowconfigure(0, weight=1)
    
    def analyze_curve(self):
        """커브 분석 실행"""
        try:
            # TODO: 실제 커브 데이터 로드 및 분석
            # 현재는 샘플 데이터로 분석 시뮬레이션
            
            # 샘플 커브 데이터 (실제로는 파일에서 로드)
            sample_curve = self._generate_sample_curve_data()
            
            # 커브 특성 분석
            self.curve_analysis = self._analyze_curve_characteristics(sample_curve)
            
            # 분석 결과 표시
            self._display_analysis_results()
            
            # 자동 설정 제안 생성
            suggestions = self._generate_automatic_suggestions()
            self._display_suggestions(suggestions)
            
            messagebox.showinfo("분석 완료", "커브 분석이 완료되었습니다.")
            
        except Exception as e:
            messagebox.showerror("분석 오류", f"커브 분석 중 오류가 발생했습니다:\n{str(e)}")
    
    def _generate_sample_curve_data(self) -> List[Tuple[float, float]]:
        """샘플 커브 데이터 생성 (테스트용)"""
        # 간단한 원형 커브 데이터
        points = []
        for i in range(0, 360, 10):
            angle = math.radians(i)
            x = 100 * math.cos(angle)
            y = 100 * math.sin(angle)
            points.append((x, y))
        return points
    
    def _analyze_curve_characteristics(self, curve_points: List[Tuple[float, float]]) -> Dict[str, Any]:
        """커브 특성 분석"""
        if not curve_points:
            return {}
        
        # 기본 통계
        x_coords = [p[0] for p in curve_points]
        y_coords = [p[1] for p in curve_points]
        
        # 경계 계산
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        width = max_x - min_x
        height = max_y - min_y
        
        # 곡률 분석 (간단한 근사)
        total_curvature = 0
        for i in range(1, len(curve_points) - 1):
            p1 = curve_points[i-1]
            p2 = curve_points[i]
            p3 = curve_points[i+1]
            
            # 삼각형 면적을 이용한 곡률 근사
            area = abs((p2[0] - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (p2[1] - p1[1])) / 2
            total_curvature += area
        
        avg_curvature = total_curvature / len(curve_points) if curve_points else 0
        
        # 복잡도 분석
        complexity = len(curve_points) / (width + height) if (width + height) > 0 else 0
        
        return {
            "point_count": len(curve_points),
            "dimensions": {"width": width, "height": height},
            "area": width * height,
            "perimeter": self._calculate_perimeter(curve_points),
            "curvature": avg_curvature,
            "complexity": complexity,
            "is_closed": self._is_curve_closed(curve_points),
            "symmetry": self._analyze_symmetry(curve_points)
        }
    
    def _calculate_perimeter(self, points: List[Tuple[float, float]]) -> float:
        """커브 둘레 계산"""
        if len(points) < 2:
            return 0
        
        perimeter = 0
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            perimeter += math.sqrt(dx*dx + dy*dy)
        
        return perimeter
    
    def _is_curve_closed(self, points: List[Tuple[float, float]]) -> bool:
        """커브가 닫혀있는지 확인"""
        if len(points) < 3:
            return False
        
        first = points[0]
        last = points[-1]
        distance = math.sqrt((last[0] - first[0])**2 + (last[1] - first[1])**2)
        return distance < 1.0  # 임계값
    
    def _analyze_symmetry(self, points: List[Tuple[float, float]]) -> Dict[str, Any]:
        """커브 대칭성 분석"""
        if len(points) < 2:
            return {"horizontal": False, "vertical": False, "rotational": False}
        
        # 중심점 계산
        center_x = sum(p[0] for p in points) / len(points)
        center_y = sum(p[1] for p in points) / len(points)
        
        # 대칭성 검사 (간단한 근사)
        horizontal_sym = True
        vertical_sym = True
        
        for point in points:
            # 수평 대칭
            reflected_x = 2 * center_x - point[0]
            if not any(abs(p[0] - reflected_x) < 1.0 for p in points):
                horizontal_sym = False
            
            # 수직 대칭
            reflected_y = 2 * center_y - point[1]
            if not any(abs(p[1] - reflected_y) < 1.0 for p in points):
                vertical_sym = False
        
        return {
            "horizontal": horizontal_sym,
            "vertical": vertical_sym,
            "rotational": horizontal_sym and vertical_sym
        }
    
    def _display_analysis_results(self):
        """분석 결과 표시"""
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete("1.0", tk.END)
        
        if not self.curve_analysis:
            self.analysis_text.insert(tk.END, "분석 결과가 없습니다.")
            self.analysis_text.config(state=tk.DISABLED)
            return
        
        # 분석 결과 포맷팅
        result_text = "=== 커브 특성 분석 결과 ===\n\n"
        
        result_text += f"포인트 수: {self.curve_analysis['point_count']}\n"
        result_text += f"크기: {self.curve_analysis['dimensions']['width']:.1f} x {self.curve_analysis['dimensions']['height']:.1f}\n"
        result_text += f"면적: {self.curve_analysis['area']:.1f}\n"
        result_text += f"둘레: {self.curve_analysis['perimeter']:.1f}\n"
        result_text += f"평균 곡률: {self.curve_analysis['curvature']:.3f}\n"
        result_text += f"복잡도: {self.curve_analysis['complexity']:.3f}\n"
        result_text += f"닫힌 커브: {'예' if self.curve_analysis['is_closed'] else '아니오'}\n\n"
        
        # 대칭성 정보
        sym = self.curve_analysis['symmetry']
        result_text += "=== 대칭성 분석 ===\n"
        result_text += f"수평 대칭: {'예' if sym['horizontal'] else '아니오'}\n"
        result_text += f"수직 대칭: {'예' if sym['vertical'] else '아니오'}\n"
        result_text += f"회전 대칭: {'예' if sym['rotational'] else '아니오'}\n"
        
        self.analysis_text.insert(tk.END, result_text)
        self.analysis_text.config(state=tk.DISABLED)
    
    def _generate_automatic_suggestions(self) -> Dict[str, Any]:
        """자동 설정 제안 생성"""
        if not self.curve_analysis:
            return {}
        
        suggestions = {}
        
        # 입력 커브 최적화 제안
        suggestions["optimizer"] = self._suggest_optimizer_settings()
        
        # 오프셋 커브 디포머 제안
        suggestions["deformer"] = self._suggest_deformer_settings()
        
        # 성능 설정 제안
        suggestions["performance"] = self._suggest_performance_settings()
        
        return suggestions
    
    def _suggest_optimizer_settings(self) -> Dict[str, Any]:
        """최적화 설정 제안"""
        point_count = self.curve_analysis.get("point_count", 100)
        complexity = self.curve_analysis.get("complexity", 1.0)
        curvature = self.curve_analysis.get("curvature", 0.5)
        
        # 포인트 수에 따른 최적화 레벨
        if point_count > 500:
            opt_level = "high"
            smoothing = 0.7
            simplification = 0.02
        elif point_count > 200:
            opt_level = "medium"
            smoothing = 0.5
            simplification = 0.01
        else:
            opt_level = "low"
            smoothing = 0.3
            simplification = 0.005
        
        # 복잡도에 따른 조정
        if complexity > 2.0:
            smoothing *= 0.8
            simplification *= 1.5
        
        # 곡률에 따른 조정
        if curvature > 1.0:
            smoothing *= 1.2
        
        return {
            "optimization_level": opt_level,
            "smoothing_factor": min(1.0, max(0.0, smoothing)),
            "simplification_threshold": min(0.1, max(0.001, simplification)),
            "curvature_based": True,
            "multires_optimization": point_count > 300,
            "optimization_iterations": 3 if point_count > 200 else 2
        }
    
    def _suggest_deformer_settings(self) -> Dict[str, Any]:
        """디포머 설정 제안"""
        dimensions = self.curve_analysis.get("dimensions", {"width": 100, "height": 100})
        area = self.curve_analysis.get("area", 10000)
        is_closed = self.curve_analysis.get("is_closed", True)
        
        # 크기에 따른 오프셋 거리 제안
        avg_size = (dimensions["width"] + dimensions["height"]) / 2
        suggested_offset = avg_size * 0.1  # 크기의 10%
        
        # 영역에 따른 품질 설정
        if area > 50000:
            quality = "ultra"
        elif area > 20000:
            quality = "high"
        elif area > 10000:
            quality = "medium"
        else:
            quality = "low"
        
        return {
            "offset_distance": suggested_offset,
            "offset_direction": "both" if is_closed else "right",
            "smooth_curves": True,
            "offset_algorithm": "parallel" if is_closed else "perpendicular",
            "offset_quality": quality,
            "auto_offset_adjustment": True,
            "collision_resolution": True
        }
    
    def _suggest_performance_settings(self) -> Dict[str, Any]:
        """성능 설정 제안"""
        point_count = self.curve_analysis.get("point_count", 100)
        complexity = self.curve_analysis.get("complexity", 1.0)
        
        # 복잡도에 따른 우선순위
        if complexity > 2.0:
            priority = "quality"
        elif complexity > 1.0:
            priority = "balanced"
        else:
            priority = "speed"
        
        # 포인트 수에 따른 메모리 제한
        if point_count > 1000:
            memory_limit = 1024
        elif point_count > 500:
            memory_limit = 768
        else:
            memory_limit = 512
        
        return {
            "processing_priority": priority,
            "parallel_processing": point_count > 100,
            "memory_limit": memory_limit,
            "use_cache": point_count > 200
        }
    
    def _display_suggestions(self, suggestions: Dict[str, Any]):
        """제안된 설정 표시"""
        self.suggestions_text.config(state=tk.NORMAL)
        self.suggestions_text.delete("1.0", tk.END)
        
        if not suggestions:
            self.suggestions_text.insert(tk.END, "제안된 설정이 없습니다.")
            self.suggestions_text.config(state=tk.DISABLED)
            return
        
        # 제안된 설정 포맷팅
        suggestions_text = "=== 자동 설정 제안 ===\n\n"
        
        for category, settings in suggestions.items():
            suggestions_text += f"--- {category.upper()} ---\n"
            for key, value in settings.items():
                suggestions_text += f"{key}: {value}\n"
            suggestions_text += "\n"
        
        self.suggestions_text.insert(tk.END, suggestions_text)
        self.suggestions_text.config(state=tk.DISABLED)
    
    def apply_suggestions(self):
        """제안된 설정 적용"""
        try:
            if not self.curve_analysis:
                messagebox.showwarning("경고", "먼저 커브를 분석해주세요.")
                return
            
            suggestions = self._generate_automatic_suggestions()
            if suggestions:
                self.on_apply_suggestions(suggestions)
                messagebox.showinfo("적용 완료", "제안된 설정이 성공적으로 적용되었습니다.")
            else:
                messagebox.showwarning("경고", "적용할 설정이 없습니다.")
                
        except Exception as e:
            messagebox.showerror("적용 오류", f"설정 적용 중 오류가 발생했습니다:\n{str(e)}")
    
    def get_widget(self) -> tk.Widget:
        """메인 위젯 반환"""
        return self.main_frame
    
    def get_analysis_results(self) -> Dict[str, Any]:
        """분석 결과 반환"""
        return self.curve_analysis.copy()
