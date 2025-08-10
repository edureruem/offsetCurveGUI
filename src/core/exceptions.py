#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
커스텀 예외 클래스들
애플리케이션 전반에서 사용되는 예외 정의
"""

class OffsetCurveGUIError(Exception):
    """기본 예외 클래스"""
    pass

class OptimizationError(OffsetCurveGUIError):
    """커브 최적화 관련 오류"""
    pass

class OffsetGenerationError(OffsetCurveGUIError):
    """오프셋 커브 생성 관련 오류"""
    pass

class WorkflowError(OffsetCurveGUIError):
    """워크플로우 실행 관련 오류"""
    pass

class ValidationError(OffsetCurveGUIError):
    """데이터 검증 관련 오류"""
    pass

class ConfigurationError(OffsetCurveGUIError):
    """설정 관련 오류"""
    pass
