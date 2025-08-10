#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
핵심 인터페이스 정의
모듈 간 결합도를 낮추고 확장성을 높이는 추상화 계층
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass

# ============================================================================
# 데이터 모델
# ============================================================================

@dataclass
class CurveData:
    """커브 데이터 구조체"""
    points: List[tuple]  # (x, y) 좌표 리스트
    metadata: Dict[str, Any]  # 메타데이터
    format: str  # 원본 파일 형식
    source_path: Optional[Path] = None

@dataclass
class OptimizationResult:
    """최적화 결과 구조체"""
    optimized_curve: CurveData
    original_point_count: int
    optimized_point_count: int
    quality_metrics: Dict[str, float]
    processing_time: float

@dataclass
class OffsetResult:
    """오프셋 생성 결과 구조체"""
    offset_curves: List[CurveData]
    offset_distance: float
    quality_metrics: Dict[str, float]
    processing_time: float

@dataclass
class WorkflowStep:
    """워크플로우 단계 정보"""
    name: str
    description: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    parameters: Dict[str, Any]
    result: Optional[Any] = None
    error_message: Optional[str] = None

# ============================================================================
# 핵심 인터페이스
# ============================================================================

class ICurveLoader(ABC):
    """커브 로더 인터페이스"""
    
    @abstractmethod
    def load_curve(self, file_path: Path) -> CurveData:
        """커브 파일 로드"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """지원하는 파일 형식 반환"""
        pass
    
    @abstractmethod
    def validate_file(self, file_path: Path) -> bool:
        """파일 유효성 검증"""
        pass

class ICurveOptimizer(ABC):
    """커브 최적화 인터페이스"""
    
    @abstractmethod
    def optimize_curve(self, curve: CurveData, parameters: Dict[str, Any]) -> OptimizationResult:
        """커브 최적화 수행"""
        pass
    
    @abstractmethod
    def get_optimization_parameters(self) -> Dict[str, Any]:
        """최적화 파라미터 스키마 반환"""
        pass
    
    @abstractmethod
    def estimate_quality(self, curve: CurveData) -> float:
        """커브 품질 점수 추정"""
        pass

class IOffsetGenerator(ABC):
    """오프셋 생성 인터페이스"""
    
    @abstractmethod
    def generate_offset(self, curve: CurveData, parameters: Dict[str, Any]) -> OffsetResult:
        """오프셋 커브 생성"""
        pass
    
    @abstractmethod
    def get_offset_parameters(self) -> Dict[str, Any]:
        """오프셋 파라미터 스키마 반환"""
        pass
    
    @abstractmethod
    def validate_offset_parameters(self, parameters: Dict[str, Any]) -> bool:
        """오프셋 파라미터 유효성 검증"""
        pass

class IResultValidator(ABC):
    """결과 검증 인터페이스"""
    
    @abstractmethod
    def validate_result(self, original: CurveData, result: Union[OptimizationResult, OffsetResult]) -> Dict[str, Any]:
        """결과 검증 수행"""
        pass
    
    @abstractmethod
    def get_validation_criteria(self) -> Dict[str, Any]:
        """검증 기준 반환"""
        pass

class IResultExporter(ABC):
    """결과 내보내기 인터페이스"""
    
    @abstractmethod
    def export_result(self, result: Union[OptimizationResult, OffsetResult], 
                     output_path: Path, format: str) -> bool:
        """결과 내보내기"""
        pass
    
    @abstractmethod
    def get_supported_export_formats(self) -> List[str]:
        """지원하는 내보내기 형식 반환"""
        pass

class IWorkflowExecutor(ABC):
    """워크플로우 실행 인터페이스"""
    
    @abstractmethod
    def execute_step(self, step: WorkflowStep) -> bool:
        """워크플로우 단계 실행"""
        pass
    
    @abstractmethod
    def get_step_dependencies(self, step_name: str) -> List[str]:
        """단계별 의존성 반환"""
        pass
    
    @abstractmethod
    def can_execute_step(self, step_name: str, completed_steps: List[str]) -> bool:
        """단계 실행 가능 여부 확인"""
        pass

class IProgressReporter(ABC):
    """진행률 보고 인터페이스"""
    
    @abstractmethod
    def report_progress(self, step_name: str, progress: float, message: str):
        """진행률 보고"""
        pass
    
    @abstractmethod
    def report_error(self, step_name: str, error: Exception):
        """오류 보고"""
        pass
    
    @abstractmethod
    def report_completion(self, step_name: str, result: Any):
        """완료 보고"""
        pass

# ============================================================================
# 설정 및 설정 관리
# ============================================================================

class IConfigurationManager(ABC):
    """설정 관리 인터페이스"""
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """설정값 조회"""
        pass
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> bool:
        """설정값 저장"""
        pass
    
    @abstractmethod
    def load_config(self, config_path: Path) -> bool:
        """설정 파일 로드"""
        pass
    
    @abstractmethod
    def save_config(self, config_path: Path) -> bool:
        """설정 파일 저장"""
        pass

class ILogger(ABC):
    """로깅 인터페이스"""
    
    @abstractmethod
    def log_info(self, message: str):
        """정보 로그"""
        pass
    
    @abstractmethod
    def log_warning(self, message: str):
        """경고 로그"""
        pass
    
    @abstractmethod
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """오류 로그"""
        pass
    
    @abstractmethod
    def log_debug(self, message: str):
        """디버그 로그"""
        pass
