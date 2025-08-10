#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Offset Curve Deformer & Input Curve Optimizer 통합 GUI
메인 애플리케이션 진입점
"""

import sys
from pathlib import Path
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTimer

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.maya_main_window import MayaOffsetCurveGUI
from src.integratedWorkflow.workflow_manager import WorkflowManager

def main():
    """메인 애플리케이션 실행"""
    try:
        # 워크플로우 매니저 초기화
        workflow_manager = WorkflowManager()
        
        # PySide2 애플리케이션 생성
        app = QApplication(sys.argv)
        
        # 메인 윈도우 생성
        window = MayaOffsetCurveGUI()
        window.show()
        
        # 애플리케이션 실행
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"애플리케이션 실행 중 오류가 발생했습니다:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
