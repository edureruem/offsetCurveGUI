#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Maya 2020용 Offset Curve Deformer & Input Curve Optimizer 설치 스크립트

이 스크립트는 다음을 수행합니다:
1. C++ 플러그인 컴파일 (CMake 사용)
2. Python GUI 및 의존성 설치
3. Maya 플러그인 경로 설정
4. 설치 상태 확인
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

class MayaPluginInstaller:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.external_dir = self.project_root / "external"
        self.src_dir = self.project_root / "src"
        
        # Maya 버전별 설정
        self.maya_version = "2020"
        self.maya_arch = "x64"
        
        # 플랫폼별 설정
        self.is_windows = platform.system() == "Windows"
        self.is_macos = platform.system() == "Darwin"
        self.is_linux = platform.system() == "Linux"
        
        print(f"🚀 Maya Plugin Installer 시작")
        print(f"📁 프로젝트 루트: {self.project_root}")
        print(f"🔌 Maya 버전: {self.maya_version}")
        print(f"💻 플랫폼: {platform.system()} {platform.machine()}")
    
    def check_prerequisites(self):
        """필수 도구들 확인"""
        print("\n🔍 필수 도구 확인 중...")
        
        # CMake 확인
        try:
            result = subprocess.run(['cmake', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ CMake: {result.stdout.strip().split('\n')[0]}")
            else:
                print("❌ CMake를 찾을 수 없습니다")
                return False
        except FileNotFoundError:
            print("❌ CMake가 설치되지 않았습니다")
            print("   CMake를 설치하세요: https://cmake.org/download/")
            return False
        
        # Visual Studio (Windows) 또는 컴파일러 확인
        if self.is_windows:
            try:
                # Visual Studio 2019/2022 확인
                vs_paths = [
                    r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat",
                    r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat",
                    r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
                ]
                
                vs_found = False
                for vs_path in vs_paths:
                    if os.path.exists(vs_path):
                        print(f"✅ Visual Studio: {vs_path}")
                        vs_found = True
                        break
                
                if not vs_found:
                    print("⚠️ Visual Studio를 찾을 수 없습니다")
                    print("   Visual Studio 2019 또는 2022 Community Edition을 설치하세요")
                    return False
                    
            except Exception as e:
                print(f"⚠️ Visual Studio 확인 중 오류: {e}")
        
        # Maya Python 확인
        try:
            import maya.cmds as cmds
            print(f"✅ Maya Python: {sys.version}")
        except ImportError:
            print("⚠️ Maya Python을 찾을 수 없습니다")
            print("   Maya 2020에서 이 스크립트를 실행하세요")
        
        return True
    
    def build_plugin(self, plugin_name):
        """개별 플러그인 빌드"""
        plugin_dir = self.external_dir / plugin_name
        build_dir = plugin_dir / f"build.{self.maya_version}"
        
        print(f"\n🔨 {plugin_name} 플러그인 빌드 중...")
        print(f"   소스: {plugin_dir}")
        print(f"   빌드: {build_dir}")
        
        try:
            # 빌드 디렉토리 생성
            build_dir.mkdir(parents=True, exist_ok=True)
            
            # CMake 구성
            cmake_cmd = [
                'cmake',
                '-S', str(plugin_dir),
                '-B', str(build_dir),
                f'-DMAYA_VERSION={self.maya_version}',
                '-DCMAKE_BUILD_TYPE=Release'
            ]
            
            print(f"   CMake 구성: {' '.join(cmake_cmd)}")
            result = subprocess.run(cmake_cmd, cwd=build_dir, check=True)
            
            # 빌드
            build_cmd = ['cmake', '--build', str(build_dir), '--config', 'Release']
            print(f"   빌드: {' '.join(build_cmd)}")
            result = subprocess.run(build_cmd, cwd=build_dir, check=True)
            
            print(f"✅ {plugin_name} 빌드 완료")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ {plugin_name} 빌드 실패: {e}")
            return False
        except Exception as e:
            print(f"❌ {plugin_name} 빌드 중 오류: {e}")
            return False
    
    def build_all_plugins(self):
        """모든 플러그인 빌드"""
        print("\n🔨 모든 플러그인 빌드 시작...")
        
        plugins = ["offsetCurveDeformer", "inputCurveOptimizer"]
        success_count = 0
        
        for plugin in plugins:
            if self.build_plugin(plugin):
                success_count += 1
        
        print(f"\n📊 빌드 결과: {success_count}/{len(plugins)} 성공")
        return success_count == len(plugins)
    
    def find_compiled_plugins(self):
        """컴파일된 플러그인 파일들 찾기"""
        print("\n🔍 컴파일된 플러그인 검색 중...")
        
        found_plugins = {}
        
        for plugin_name in ["offsetCurveDeformer", "inputCurveOptimizer"]:
            plugin_dir = self.external_dir / plugin_name
            build_dir = plugin_dir / f"build.{self.maya_version}"
            
            # Windows: .mll 파일
            if self.is_windows:
                plugin_ext = ".mll"
                search_paths = [
                    build_dir / "x64" / "Release",
                    build_dir / "Release",
                    build_dir
                ]
            # macOS: .bundle 파일
            elif self.is_macos:
                plugin_ext = ".bundle"
                search_paths = [
                    build_dir / "src",
                    build_dir
                ]
            # Linux: .so 파일
            else:
                plugin_ext = ".so"
                search_paths = [
                    build_dir / "src",
                    build_dir
                ]
            
            plugin_found = None
            for search_path in search_paths:
                if search_path.exists():
                    for file in search_path.iterdir():
                        if file.is_file() and file.suffix == plugin_ext:
                            plugin_found = file
                            break
                    if plugin_found:
                        break
            
            if plugin_found:
                found_plugins[plugin_name] = plugin_found
                print(f"✅ {plugin_name}: {plugin_found}")
            else:
                print(f"❌ {plugin_name}: 컴파일된 파일을 찾을 수 없음")
        
        return found_plugins
    
    def install_to_maya(self, plugins):
        """Maya에 플러그인 설치"""
        print("\n📦 Maya에 플러그인 설치 중...")
        
        # Maya 플러그인 디렉토리 찾기
        maya_plugin_dir = self.find_maya_plugin_directory()
        if not maya_plugin_dir:
            print("❌ Maya 플러그인 디렉토리를 찾을 수 없습니다")
            return False
        
        print(f"   Maya 플러그인 디렉토리: {maya_plugin_dir}")
        
        # 플러그인 복사
        for plugin_name, plugin_path in plugins.items():
            try:
                dest_path = maya_plugin_dir / plugin_path.name
                shutil.copy2(plugin_path, dest_path)
                print(f"✅ {plugin_name} 설치됨: {dest_path}")
            except Exception as e:
                print(f"❌ {plugin_name} 설치 실패: {e}")
                return False
        
        return True
    
    def find_maya_plugin_directory(self):
        """Maya 플러그인 디렉토리 찾기"""
        # 사용자 Maya 디렉토리
        user_maya_dir = Path.home() / "maya" / self.maya_version / "plug-ins"
        if user_maya_dir.exists():
            return user_maya_dir
        
        # 시스템 Maya 디렉토리 (Windows)
        if self.is_windows:
            system_paths = [
                Path("C:/Program Files/Autodesk/Maya2020/bin/plug-ins"),
                Path("C:/Program Files/Autodesk/Maya2020/plug-ins"),
                Path("C:/Program Files/Autodesk/Maya2020/scripts/plug-ins")
            ]
            
            for path in system_paths:
                if path.exists():
                    return path
        
        # macOS
        elif self.is_macos:
            mac_paths = [
                Path("/Applications/Autodesk/maya2020/Maya.app/Contents/plug-ins"),
                Path("/Applications/Autodesk/maya2020/plug-ins")
            ]
            
            for path in mac_paths:
                if path.exists():
                    return path
        
        # Linux
        else:
            linux_paths = [
                Path("/usr/autodesk/maya2020/plug-ins"),
                Path("/opt/autodesk/maya2020/plug-ins")
            ]
            
            for path in linux_paths:
                if path.exists():
                    return path
        
        return None
    
    def create_maya_user_setup(self):
        """Maya 사용자 설정 파일 생성"""
        print("\n⚙️ Maya 사용자 설정 생성 중...")
        
        # Maya 사용자 디렉토리
        user_maya_dir = Path.home() / "maya" / self.maya_version
        user_maya_dir.mkdir(parents=True, exist_ok=True)
        
        # Maya.env 파일 생성
        maya_env_file = user_maya_dir / "Maya.env"
        
        env_content = f"""# Offset Curve Deformer Plugin Environment
MAYA_PLUG_IN_PATH={self.project_root}/external/offsetCurveDeformer/build.{self.maya_version}/x64/Release
MAYA_PLUG_IN_PATH+={self.project_root}/external/inputCurveOptimizer/build.{self.maya_version}/x64/Release
MAYA_SCRIPT_PATH+={self.project_root}/src
PYTHONPATH+={self.project_root}/src
"""
        
        try:
            with open(maya_env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print(f"✅ Maya.env 파일 생성됨: {maya_env_file}")
        except Exception as e:
            print(f"❌ Maya.env 파일 생성 실패: {e}")
            return False
        
        return True
    
    def test_installation(self):
        """설치 테스트"""
        print("\n🧪 설치 테스트 중...")
        
        try:
            # Maya에서 플러그인 로드 테스트
            import maya.cmds as cmds
            
            # offsetCurveDeformer 테스트
            try:
                cmds.loadPlugin("offsetCurveDeformer")
                print("✅ offsetCurveDeformer 플러그인 로드 성공")
                cmds.unloadPlugin("offsetCurveDeformer")
            except Exception as e:
                print(f"❌ offsetCurveDeformer 플러그인 로드 실패: {e}")
            
            # inputCurveOptimizer 테스트
            try:
                cmds.loadPlugin("inputCurveOptimizer")
                print("✅ inputCurveOptimizer 플러그인 로드 성공")
                cmds.unloadPlugin("inputCurveOptimizer")
            except Exception as e:
                print(f"❌ inputCurveOptimizer 플러그인 로드 실패: {e}")
                
        except ImportError:
            print("⚠️ Maya Python을 사용할 수 없어 플러그인 테스트를 건너뜁니다")
        
        return True
    
    def run(self):
        """메인 설치 프로세스 실행"""
        print("=" * 60)
        print("🎯 Maya Plugin Installer")
        print("=" * 60)
        
        # 1. 필수 도구 확인
        if not self.check_prerequisites():
            print("\n❌ 필수 도구가 설치되지 않았습니다")
            return False
        
        # 2. 플러그인 빌드
        if not self.build_all_plugins():
            print("\n❌ 플러그인 빌드에 실패했습니다")
            return False
        
        # 3. 컴파일된 플러그인 찾기
        plugins = self.find_compiled_plugins()
        if not plugins:
            print("\n❌ 컴파일된 플러그인을 찾을 수 없습니다")
            return False
        
        # 4. Maya에 설치
        if not self.install_to_maya(plugins):
            print("\n❌ Maya에 플러그인 설치에 실패했습니다")
            return False
        
        # 5. Maya 사용자 설정
        if not self.create_maya_user_setup():
            print("\n⚠️ Maya 사용자 설정 생성에 실패했습니다")
        
        # 6. 설치 테스트
        self.test_installation()
        
        print("\n" + "=" * 60)
        print("🎉 설치 완료!")
        print("=" * 60)
        print("\n📋 다음 단계:")
        print("1. Maya 2020을 재시작하세요")
        print("2. Plugin Manager에서 플러그인이 로드되었는지 확인하세요")
        print("3. Python Script Editor에서 GUI를 실행하세요:")
        print("   import sys")
        print("   sys.path.append('C:/Users/edurm/divkitBase/plug-ins/plug-ins/offsetCurveGUI/src')")
        print("   from ui.maya_main_window import OffsetCurveDeformerGUI")
        print("   gui = OffsetCurveDeformerGUI()")
        print("   gui.show()")
        
        return True

if __name__ == "__main__":
    installer = MayaPluginInstaller()
    success = installer.run()
    
    if not success:
        print("\n❌ 설치에 실패했습니다")
        sys.exit(1)
    else:
        print("\n✅ 설치가 성공적으로 완료되었습니다!")
