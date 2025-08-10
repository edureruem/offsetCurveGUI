#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
설정 관리 모듈
애플리케이션 전반의 설정을 중앙에서 관리
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .interfaces import IConfigurationManager
from .exceptions import ConfigurationError

class ConfigurationManager(IConfigurationManager):
    """설정 관리자 구현체"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".offsetCurveGUI" / "config.json"
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        
        # 기본 설정 초기화
        self._initialize_default_config()
        
        # 설정 파일 로드 시도
        if self.config_path.exists():
            self.load_config(self.config_path)
        else:
            # 설정 디렉토리 생성 및 기본 설정 저장
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self.save_config(self.config_path)
    
    def _initialize_default_config(self):
        """기본 설정 초기화"""
        self.config = {
            "general": {
                "language": "ko",
                "theme": "default",
                "auto_save": True,
                "max_recent_files": 10
            },
            "workflow": {
                "auto_advance": False,
                "show_progress": True,
                "enable_validation": True,
                "enable_auto_save": True
            },
            "optimization": {
                "default_optimization_level": "medium",
                "default_smoothing_factor": 0.5,
                "default_simplification_threshold": 0.01,
                "quality_threshold": 0.8
            },
            "offset": {
                "default_offset_mode": "arc_segment",
                "default_falloff_radius": 10.0,
                "default_max_influences": 4,
                "default_volume_strength": 1.0,
                "default_slide_effect": 0.0,
                "default_rotation_distribution": 0.5,
                "default_scale_distribution": 0.5,
                "default_twist_distribution": 0.5,
                "default_axial_sliding": 0.0,
                "enable_parallel_processing": True,
                "enable_debug_display": False
            },
            "export": {
                "default_format": "svg",
                "include_metadata": True,
                "output_directory": "output",
                "filename_template": "{original_name}_processed_{timestamp}"
            },
            "performance": {
                "max_memory_usage": "2GB",
                "enable_parallel_processing": True,
                "thread_count": 4,
                "cache_size": "100MB"
            },
            "logging": {
                "level": "INFO",
                "file_enabled": True,
                "console_enabled": True,
                "max_file_size": "10MB",
                "backup_count": 5
            }
        }
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """설정값 조회 (점 표기법 지원: 'general.language')"""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            if default is not None:
                return default
            raise ConfigurationError(f"설정 키를 찾을 수 없습니다: {key}")
    
    def set_config(self, key: str, value: Any) -> bool:
        """설정값 저장 (점 표기법 지원: 'general.language')"""
        try:
            keys = key.split('.')
            config = self.config
            
            # 마지막 키 전까지 탐색
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 마지막 키에 값 설정
            config[keys[-1]] = value
            
            # 자동 저장이 활성화된 경우 즉시 저장
            if self.get_config("general.auto_save", True):
                self.save_config(self.config_path)
            
            self.logger.info(f"설정 업데이트: {key} = {value}")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 저장 실패: {key} = {value}, 오류: {e}")
            return False
    
    def load_config(self, config_path: Path) -> bool:
        """설정 파일 로드"""
        try:
            if not config_path.exists():
                self.logger.warning(f"설정 파일이 존재하지 않습니다: {config_path}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # 기존 설정과 병합 (기본값 유지)
            self._merge_config(loaded_config)
            
            self.logger.info(f"설정 파일 로드 완료: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 파일 로드 실패: {config_path}, 오류: {e}")
            return False
    
    def save_config(self, config_path: Path) -> bool:
        """설정 파일 저장"""
        try:
            # 디렉토리 생성
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"설정 파일 저장 완료: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"설정 파일 저장 실패: {config_path}, 오류: {e}")
            return False
    
    def _merge_config(self, new_config: Dict[str, Any]):
        """설정 병합 (재귀적)"""
        for key, value in new_config.items():
            if key in self.config and isinstance(self.config[key], dict) and isinstance(value, dict):
                self._merge_config(value)
            else:
                self.config[key] = value
    
    def get_all_config(self) -> Dict[str, Any]:
        """전체 설정 반환"""
        return self.config.copy()
    
    def reset_to_defaults(self):
        """기본 설정으로 초기화"""
        self._initialize_default_config()
        self.save_config(self.config_path)
        self.logger.info("설정을 기본값으로 초기화했습니다.")
    
    def export_config(self, export_path: Path) -> bool:
        """설정 내보내기"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            self.logger.info(f"설정 내보내기 완료: {export_path}")
            return True
        except Exception as e:
            self.logger.error(f"설정 내보내기 실패: {export_path}, 오류: {e}")
            return False
