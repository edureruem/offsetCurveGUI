#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maya용 OffsetCurveGUI 설치 스크립트
Maya에서 offsetCurveGUI를 쉽게 설치하고 실행할 수 있습니다.
"""

import os
import sys
import shutil
import maya.cmds as cmds
import maya.mel as mel

def install_offset_curve_gui():
    """Maya에 offsetCurveGUI 설치"""
    
    # 현재 스크립트 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Maya 스크립트 경로
    maya_scripts_dir = cmds.internalVar(userScriptDir=True)
    
    # 설치할 폴더
    install_dir = os.path.join(maya_scripts_dir, "offsetCurveGUI")
    
    try:
        # 기존 설치 제거
        if os.path.exists(install_dir):
            shutil.rmtree(install_dir)
        
        # 새로 설치
        shutil.copytree(current_dir, install_dir, ignore=shutil.ignore_patterns(
            '*.git*', 'build*', '*.pyc', '__pycache__', '.gitmodules'
        ))
        
        # Maya 스크립트 경로에 추가
        if install_dir not in sys.path:
            sys.path.append(install_dir)
        
        # Maya 메뉴에 추가
        add_to_maya_menu(install_dir)
        
        cmds.confirmDialog(
            title="설치 완료",
            message=f"offsetCurveGUI가 성공적으로 설치되었습니다!\n\n설치 경로: {install_dir}\n\nMaya를 재시작한 후 메뉴에서 'OffsetCurveGUI'를 찾을 수 있습니다.",
            button="확인"
        )
        
        return True
        
    except Exception as e:
        cmds.confirmDialog(
            title="설치 실패",
            message=f"설치 중 오류가 발생했습니다:\n{str(e)}",
            button="확인"
        )
        return False

def add_to_maya_menu(install_dir):
    """Maya 메뉴에 offsetCurveGUI 추가"""
    
    try:
        # 메뉴 생성
        if not cmds.menu('offsetCurveGUIMenu', exists=True):
            cmds.menu('offsetCurveGUIMenu', label='OffsetCurveGUI', parent='MayaWindow')
        
        # 메뉴 아이템 추가
        cmds.menuItem(
            'offsetCurveGUIMain',
            label='Offset Curve Deformer',
            command='import sys; sys.path.append(r"{}"); from ui.maya_main_window import MayaOffsetCurveGUI; window = MayaOffsetCurveGUI(); window.show()'.format(install_dir)
        )
        
        cmds.menuItem(divider=True)
        
        cmds.menuItem(
            'offsetCurveGUIOpen',
            label='Open GUI',
            command='import sys; sys.path.append(r"{}"); from ui.maya_main_window import MayaOffsetCurveGUI; window = MayaOffsetCurveGUI(); window.show()'.format(install_dir)
        )
        
        cmds.menuItem(
            'offsetCurveGUIHelp',
            label='Documentation',
            command='import webbrowser; webbrowser.open(r"{}")'.format(os.path.join(install_dir, 'docs'))
        )
        
    except Exception as e:
        print(f"메뉴 추가 중 오류: {e}")

def run_offset_curve_gui():
    """offsetCurveGUI 실행"""
    
    try:
        # 현재 스크립트 경로
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Python 경로에 추가
        if current_dir not in sys.path:
            sys.path.append(current_dir)
        
        # GUI 실행
        from ui.maya_main_window import MayaOffsetCurveGUI
        window = MayaOffsetCurveGUI()
        window.show()
        
        return True
        
    except Exception as e:
        cmds.confirmDialog(
            title="실행 오류",
            message=f"offsetCurveGUI 실행 중 오류가 발생했습니다:\n{str(e)}",
            button="확인"
        )
        return False

def create_installer_ui():
    """설치 UI 생성"""
    
    if cmds.window('offsetCurveGUIInstaller', exists=True):
        cmds.deleteUI('offsetCurveGUIInstaller')
    
    window = cmds.window('offsetCurveGUIInstaller', title='OffsetCurveGUI Maya 설치', width=400, height=300)
    
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnOffset=['both', 10])
    
    cmds.text(label='OffsetCurveGUI Maya 설치 도구', font='boldLabelFont')
    cmds.text(label='Maya에서 offsetCurveGUI를 쉽게 사용할 수 있도록 설치합니다.')
    
    cmds.separator(height=20)
    
    cmds.button(
        label='Maya에 설치',
        command=lambda x: install_offset_curve_gui(),
        backgroundColor=[0.2, 0.6, 0.2]
    )
    
    cmds.button(
        label='지금 실행 (설치 없이)',
        command=lambda x: run_offset_curve_gui(),
        backgroundColor=[0.2, 0.4, 0.8]
    )
    
    cmds.separator(height=20)
    
    cmds.text(label='설치 후 Maya를 재시작하면 메뉴에 "OffsetCurveGUI"가 추가됩니다.')
    cmds.text(label='설치 경로: Maya 사용자 스크립트 폴더')
    
    cmds.button(
        label='닫기',
        command=lambda x: cmds.deleteUI('offsetCurveGUIInstaller'),
        backgroundColor=[0.6, 0.6, 0.6]
    )
    
    cmds.showWindow(window)

# 메인 실행
if __name__ == "__main__":
    create_installer_ui()
