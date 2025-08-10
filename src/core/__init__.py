#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
핵심 모듈
인터페이스, 데이터 모델, 공통 유틸리티를 포함
"""

from .interfaces import (
    ICurveLoader,
    ICurveOptimizer,
    IOffsetGenerator,
    IResultValidator,
    IResultExporter,
    IWorkflowExecutor,
    IProgressReporter,
    IConfigurationManager,
    ILogger,
    CurveData,
    OptimizationResult,
    OffsetResult,
    WorkflowStep
)

from .configuration import ConfigurationManager
from .logger import Logger, WorkflowLogger
from .exceptions import (
    OffsetCurveGUIException,
    ConfigurationError,
    FileFormatError,
    ValidationError,
    WorkflowError,
    OptimizationError,
    OffsetGenerationError,
    ExportError,
    DependencyError,
    ResourceError
)

__all__ = [
    # 인터페이스
    'ICurveLoader',
    'ICurveOptimizer',
    'IOffsetGenerator',
    'IResultValidator',
    'IResultExporter',
    'IWorkflowExecutor',
    'IProgressReporter',
    'IConfigurationManager',
    'ILogger',
    
    # 데이터 모델
    'CurveData',
    'OptimizationResult',
    'OffsetResult',
    'WorkflowStep',
    
    # 구현체
    'ConfigurationManager',
    'Logger',
    'WorkflowLogger',
    
    # 예외
    'OffsetCurveGUIException',
    'ConfigurationError',
    'FileFormatError',
    'ValidationError',
    'WorkflowError',
    'OptimizationError',
    'OffsetGenerationError',
    'ExportError',
    'DependencyError',
    'ResourceError'
]
