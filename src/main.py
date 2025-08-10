#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Offset Curve Deformer & Input Curve Optimizer 통합 GUI
메인 애플리케이션 진입점
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ui.main_window import MainWindow
from src.integratedWorkflow.workflow_manager import WorkflowManager

def main():
    """메인 애플리케이션 실행"""
    try:
        root = tk.Tk()
        root.title("Offset Curve Deformer & Input Curve Optimizer")
        root.geometry("1200x800")
        
        # 워크플로우 매니저 초기화
        workflow_manager = WorkflowManager()
        
        # 메인 윈도우 생성
        app = MainWindow(root, workflow_manager)
        
        # 애플리케이션 실행
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("오류", f"애플리케이션 실행 중 오류가 발생했습니다:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
