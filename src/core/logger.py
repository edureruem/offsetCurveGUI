#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로깅 시스템 모듈
애플리케이션 전반의 로그를 표준화하여 관리
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from .interfaces import ILogger
from .configuration import ConfigurationManager

class Logger(ILogger):
    """로깅 시스템 구현체"""
    
    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.logger = logging.getLogger("OffsetCurveGUI")
        self._setup_logging()
    
    def _setup_logging(self):
        """로깅 설정"""
        # 로그 레벨 설정
        log_level = getattr(logging, self.config_manager.get_config("logging.level", "INFO"))
        self.logger.setLevel(log_level)
        
        # 기존 핸들러 제거
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 콘솔 핸들러 설정
        if self.config_manager.get_config("logging.console_enabled", True):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # 파일 핸들러 설정
        if self.config_manager.get_config("logging.file_enabled", True):
            log_dir = Path.home() / ".offsetCurveGUI" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / "offsetCurveGUI.log"
            
            # 로테이팅 파일 핸들러
            max_bytes = self._parse_size(self.config_manager.get_config("logging.max_file_size", "10MB"))
            backup_count = self.config_manager.get_config("logging.backup_count", 5)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # 로거 전파 방지
        self.logger.propagate = False
    
    def _parse_size(self, size_str: str) -> int:
        """크기 문자열을 바이트로 변환"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def log_info(self, message: str):
        """정보 로그"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """경고 로그"""
        self.logger.warning(message)
    
    def log_error(self, message: str, exception: Optional[Exception] = None):
        """오류 로그"""
        if exception:
            self.logger.error(f"{message}: {exception}", exc_info=True)
        else:
            self.logger.error(message)
    
    def log_debug(self, message: str):
        """디버그 로그"""
        self.logger.debug(message)
    
    def log_critical(self, message: str, exception: Optional[Exception] = None):
        """치명적 오류 로그"""
        if exception:
            self.logger.critical(f"{message}: {exception}", exc_info=True)
        else:
            self.logger.critical(message)
    
    def set_level(self, level: str):
        """로그 레벨 설정"""
        try:
            log_level = getattr(logging, level.upper())
            self.logger.setLevel(log_level)
            
            # 모든 핸들러의 레벨도 업데이트
            for handler in self.logger.handlers:
                handler.setLevel(log_level)
            
            self.log_info(f"로그 레벨이 {level.upper()}로 설정되었습니다.")
            
        except AttributeError:
            self.log_error(f"잘못된 로그 레벨입니다: {level}")
    
    def get_log_file_path(self) -> Optional[Path]:
        """로그 파일 경로 반환"""
        log_dir = Path.home() / ".offsetCurveGUI" / "logs"
        log_file = log_dir / "offsetCurveGUI.log"
        return log_file if log_file.exists() else None
    
    def clear_logs(self):
        """로그 파일 정리"""
        try:
            log_dir = Path.home() / ".offsetCurveGUI" / "logs"
            for log_file in log_dir.glob("*.log*"):
                log_file.unlink()
            self.log_info("로그 파일이 정리되었습니다.")
        except Exception as e:
            self.log_error(f"로그 파일 정리 실패: {e}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """특정 이름의 로거 반환"""
        return logging.getLogger(f"OffsetCurveGUI.{name}")

class WorkflowLogger:
    """워크플로우 전용 로거"""
    
    def __init__(self, logger: Logger, workflow_name: str):
        self.logger = logger
        self.workflow_name = workflow_name
        self.workflow_logger = logger.get_logger(f"workflow.{workflow_name}")
    
    def log_step_start(self, step_name: str, parameters: dict):
        """단계 시작 로그"""
        self.workflow_logger.info(f"워크플로우 '{self.workflow_name}' 단계 '{step_name}' 시작")
        self.workflow_logger.debug(f"파라미터: {parameters}")
    
    def log_step_complete(self, step_name: str, result: any, duration: float):
        """단계 완료 로그"""
        self.workflow_logger.info(f"워크플로우 '{self.workflow_name}' 단계 '{step_name}' 완료 (소요시간: {duration:.2f}초)")
        self.workflow_logger.debug(f"결과: {result}")
    
    def log_step_error(self, step_name: str, error: Exception):
        """단계 오류 로그"""
        self.workflow_logger.error(f"워크플로우 '{self.workflow_name}' 단계 '{step_name}' 오류: {error}")
    
    def log_workflow_start(self):
        """워크플로우 시작 로그"""
        self.workflow_logger.info(f"워크플로우 '{self.workflow_name}' 시작")
    
    def log_workflow_complete(self, total_duration: float):
        """워크플로우 완료 로그"""
        self.workflow_logger.info(f"워크플로우 '{self.workflow_name}' 완료 (총 소요시간: {total_duration:.2f}초)")
    
    def log_workflow_error(self, error: Exception):
        """워크플로우 오류 로그"""
        self.workflow_logger.error(f"워크플로우 '{self.workflow_name}' 오류: {error}")
