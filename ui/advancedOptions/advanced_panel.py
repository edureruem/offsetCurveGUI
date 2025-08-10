#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
고급 옵션 패널
offsetCurveDeformer와 inputCurveOptimizer의 고급 설정을 위한 UI 컴포넌트
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Callable

class AdvancedOptionsPanel:
    """고급 옵션 설정 패널"""
    
    def __init__(self, parent: tk.Widget, on_apply: Callable[[Dict[str, Any]], None]):
        self.parent = parent
        self.on_apply = on_apply
        self.options = {}
        
        self.setup_ui()
        self.initialize_defaults()
    
    def setup_ui(self):
        """UI 컴포넌트 설정"""
        # 메인 프레임
        self.main_frame = ttk.LabelFrame(self.parent, text="고급 옵션", padding="10")
        
        # 입력 커브 최적화 고급 옵션
        self.setup_optimizer_advanced_options()
        
        # 오프셋 커브 디포머 고급 옵션
        self.setup_deformer_advanced_options()
        
        # 성능 및 품질 옵션
        self.setup_performance_options()
        
        # 적용 버튼
        apply_button = ttk.Button(
            self.main_frame,
            text="고급 옵션 적용",
            command=self.apply_advanced_options
        )
        apply_button.grid(row=3, column=0, columnspan=2, pady=(20, 0))
    
    def setup_optimizer_advanced_options(self):
        """입력 커브 최적화 고급 옵션"""
        optimizer_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Input Curve Optimizer 고급 옵션", 
            padding="5"
        )
        optimizer_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 곡률 기반 최적화
        self.curvature_based_var = tk.BooleanVar(value=True)
        curvature_check = ttk.Checkbutton(
            optimizer_frame,
            text="곡률 기반 최적화",
            variable=self.curvature_based_var
        )
        curvature_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # 곡률 임계값
        ttk.Label(optimizer_frame, text="곡률 임계값:").grid(row=1, column=0, sticky=tk.W)
        self.curvature_threshold_var = tk.DoubleVar(value=0.1)
        curvature_scale = ttk.Scale(
            optimizer_frame,
            from_=0.01,
            to=1.0,
            variable=self.curvature_threshold_var,
            orient=tk.HORIZONTAL
        )
        curvature_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # 다중 해상도 최적화
        self.multires_optimization_var = tk.BooleanVar(value=False)
        multires_check = ttk.Checkbutton(
            optimizer_frame,
            text="다중 해상도 최적화",
            variable=self.multires_optimization_var
        )
        multires_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # 최적화 반복 횟수
        ttk.Label(optimizer_frame, text="최적화 반복:").grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        self.optimization_iterations_var = tk.IntVar(value=3)
        iterations_spin = ttk.Spinbox(
            optimizer_frame,
            from_=1,
            to=10,
            textvariable=self.optimization_iterations_var,
            width=10
        )
        iterations_spin.grid(row=3, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        optimizer_frame.columnconfigure(1, weight=1)
    
    def setup_deformer_advanced_options(self):
        """오프셋 커브 디포머 고급 옵션"""
        deformer_frame = ttk.LabelFrame(
            self.main_frame, 
            text="Offset Curve Deformer 고급 옵션", 
            padding="5"
        )
        deformer_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 오프셋 알고리즘 선택
        ttk.Label(deformer_frame, text="오프셋 알고리즘:").grid(row=0, column=0, sticky=tk.W)
        self.offset_algorithm_var = tk.StringVar(value="parallel")
        algorithm_combo = ttk.Combobox(
            deformer_frame,
            textvariable=self.offset_algorithm_var,
            values=["parallel", "perpendicular", "adaptive"],
            state="readonly"
        )
        algorithm_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 오프셋 품질 설정
        ttk.Label(deformer_frame, text="오프셋 품질:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.offset_quality_var = tk.StringVar(value="high")
        quality_combo = ttk.Combobox(
            deformer_frame,
            textvariable=self.offset_quality_var,
            values=["low", "medium", "high", "ultra"],
            state="readonly"
        )
        quality_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        # 자동 오프셋 조정
        self.auto_offset_adjustment_var = tk.BooleanVar(value=True)
        auto_adjust_check = ttk.Checkbutton(
            deformer_frame,
            text="자동 오프셋 조정",
            variable=self.auto_offset_adjustment_var
        )
        auto_adjust_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # 오프셋 충돌 해결
        self.collision_resolution_var = tk.BooleanVar(value=True)
        collision_check = ttk.Checkbutton(
            deformer_frame,
            text="오프셋 충돌 해결",
            variable=self.collision_resolution_var
        )
        collision_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        deformer_frame.columnconfigure(1, weight=1)
    
    def setup_performance_options(self):
        """성능 및 품질 옵션"""
        performance_frame = ttk.LabelFrame(
            self.main_frame, 
            text="성능 및 품질 설정", 
            padding="5"
        )
        performance_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 처리 우선순위
        ttk.Label(performance_frame, text="처리 우선순위:").grid(row=0, column=0, sticky=tk.W)
        self.processing_priority_var = tk.StringVar(value="balanced")
        priority_combo = ttk.Combobox(
            performance_frame,
            textvariable=self.processing_priority_var,
            values=["speed", "balanced", "quality"],
            state="readonly"
        )
        priority_combo.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # 병렬 처리
        self.parallel_processing_var = tk.BooleanVar(value=True)
        parallel_check = ttk.Checkbutton(
            performance_frame,
            text="병렬 처리 사용",
            variable=self.parallel_processing_var
        )
        parallel_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # 메모리 사용량 제한
        ttk.Label(performance_frame, text="메모리 제한 (MB):").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.memory_limit_var = tk.IntVar(value=512)
        memory_spin = ttk.Spinbox(
            performance_frame,
            from_=128,
            to=2048,
            increment=128,
            textvariable=self.memory_limit_var,
            width=10
        )
        memory_spin.grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        # 캐시 사용
        self.use_cache_var = tk.BooleanVar(value=True)
        cache_check = ttk.Checkbutton(
            performance_frame,
            text="중간 결과 캐시",
            variable=self.use_cache_var
        )
        cache_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        performance_frame.columnconfigure(1, weight=1)
    
    def initialize_defaults(self):
        """기본값 초기화"""
        self.options = {
            "optimizer": {
                "curvature_based": True,
                "curvature_threshold": 0.1,
                "multires_optimization": False,
                "optimization_iterations": 3
            },
            "deformer": {
                "offset_algorithm": "parallel",
                "offset_quality": "high",
                "auto_offset_adjustment": True,
                "collision_resolution": True
            },
            "performance": {
                "processing_priority": "balanced",
                "parallel_processing": True,
                "memory_limit": 512,
                "use_cache": True
            }
        }
    
    def get_current_options(self) -> Dict[str, Any]:
        """현재 설정된 옵션 반환"""
        return {
            "optimizer": {
                "curvature_based": self.curvature_based_var.get(),
                "curvature_threshold": self.curvature_threshold_var.get(),
                "multires_optimization": self.multires_optimization_var.get(),
                "optimization_iterations": self.optimization_iterations_var.get()
            },
            "deformer": {
                "offset_algorithm": self.offset_algorithm_var.get(),
                "offset_quality": self.offset_quality_var.get(),
                "auto_offset_adjustment": self.auto_offset_adjustment_var.get(),
                "collision_resolution": self.collision_resolution_var.get()
            },
            "performance": {
                "processing_priority": self.processing_priority_var.get(),
                "parallel_processing": self.parallel_processing_var.get(),
                "memory_limit": self.memory_limit_var.get(),
                "use_cache": self.use_cache_var.get()
            }
        }
    
    def apply_advanced_options(self):
        """고급 옵션 적용"""
        try:
            options = self.get_current_options()
            self.on_apply(options)
            messagebox.showinfo("알림", "고급 옵션이 성공적으로 적용되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"고급 옵션 적용 중 오류가 발생했습니다:\n{str(e)}")
    
    def get_widget(self) -> tk.Widget:
        """메인 위젯 반환"""
        return self.main_frame
    
    def update_options(self, new_options: Dict[str, Any]):
        """외부에서 옵션 업데이트"""
        try:
            if "optimizer" in new_options:
                opt = new_options["optimizer"]
                self.curvature_based_var.set(opt.get("curvature_based", True))
                self.curvature_threshold_var.set(opt.get("curvature_threshold", 0.1))
                self.multires_optimization_var.set(opt.get("multires_optimization", False))
                self.optimization_iterations_var.set(opt.get("optimization_iterations", 3))
            
            if "deformer" in new_options:
                defo = new_options["deformer"]
                self.offset_algorithm_var.set(defo.get("offset_algorithm", "parallel"))
                self.offset_quality_var.set(defo.get("offset_quality", "high"))
                self.auto_offset_adjustment_var.set(defo.get("auto_offset_adjustment", True))
                self.collision_resolution_var.set(defo.get("collision_resolution", True))
            
            if "performance" in new_options:
                perf = new_options["performance"]
                self.processing_priority_var.set(perf.get("processing_priority", "balanced"))
                self.parallel_processing_var.set(perf.get("parallel_processing", True))
                self.memory_limit_var.set(perf.get("memory_limit", 512))
                self.use_cache_var.set(perf.get("use_cache", True))
                
        except Exception as e:
            print(f"옵션 업데이트 오류: {e}")
