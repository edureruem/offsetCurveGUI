# Maya GUI 사용 가이드

## 📋 목차
1. [시작하기](#시작하기)
2. [GUI 로드 방법](#gui-로드-방법)
3. [플러그인 상태 확인](#플러그인-상태-확인)
4. [기본 작업 흐름](#기본-작업-흐름)
5. [고급 기능](#고급-기능)
6. [문제 해결](#문제-해결)
7. [팁과 모범 사례](#팁과-모범-사례)

## 🚀 시작하기

### 필수 요구사항
- Maya 2020 이상
- Python 2.7 또는 3.x
- PySide2 (Maya에 포함됨)
- `inputCurveOptimizer` 플러그인
- `offsetCurveDeformer` 플러그인

### 지원되는 Maya 버전
- Maya 2020
- Maya 2022
- Maya 2023
- Maya 2024

## 🔌 GUI 로드 방법

### 방법 1: Maya 스크립트 에디터에서 실행

1. **Maya 실행**
   - Maya를 시작합니다

2. **스크립트 에디터 열기**
   - `Window > General Editors > Script Editor` 메뉴 선택
   - 또는 `Ctrl + Shift + E` 단축키 사용

3. **Python 탭 선택**
   - 스크립트 에디터에서 `Python` 탭 클릭

4. **GUI 실행 코드 입력**
   ```python
   import sys
   import os
   
   # GUI 경로 추가
   gui_path = r"C:\Users\edurm\divkitBase\plug-ins\plug-ins\offsetCurveGUI\src"
   if gui_path not in sys.path:
       sys.path.append(gui_path)
   
   # GUI 실행
   from ui.maya_main_window import MayaMainWindow
   from PySide2.QtWidgets import QApplication
   
   # Maya의 QApplication 인스턴스 가져오기
   app = QApplication.instance()
   if not app:
       app = QApplication(sys.argv)
   
   # GUI 창 생성 및 표시
   window = MayaMainWindow()
   window.show()
   ```

5. **실행**
   - 코드를 입력한 후 `Ctrl + Enter` 또는 실행 버튼 클릭

### 방법 2: Maya Shelf에 추가

1. **Shelf 생성**
   - Maya에서 `Window > UI Elements > Shelf` 선택
   - 새 Shelf 생성 (예: "OffsetCurveGUI")

2. **Python 스크립트 추가**
   - Shelf에서 마우스 우클릭
   - `New Tab` 선택하여 새 탭 생성
   - `New Shelf Item` 선택

3. **스크립트 설정**
   - **Label**: `OffsetCurveGUI`
   - **Icon**: 원하는 아이콘 선택
   - **Command**: 위의 Python 코드 입력

4. **저장**
   - `Save All Shelves` 클릭

### 방법 3: Maya User Setup에 자동 로드

1. **Maya User Setup 폴더 찾기**
   ```
   Windows: C:\Users\[사용자명]\Documents\maya\[버전]\scripts
   macOS: ~/Library/Preferences/Autodesk/maya/[버전]/scripts
   Linux: ~/maya/[버전]/scripts
   ```

2. **자동 로드 스크립트 생성**
   - `userSetup.py` 파일 생성
   - 위의 GUI 실행 코드 추가

3. **Maya 재시작**
   - Maya를 재시작하면 자동으로 GUI가 로드됩니다

## 🔍 플러그인 상태 확인

### 자동 확인
- GUI가 로드되면 자동으로 필수 플러그인 상태를 확인합니다
- 플러그인이 로드되지 않은 경우 경고 다이얼로그가 표시됩니다

### 수동 확인
1. **Plugin Status 탭 선택**
   - GUI의 상단 탭에서 `Plugin Status` 클릭

2. **상태 확인**
   - ✅ **초록색**: 플러그인이 정상적으로 로드됨
   - ❌ **빨간색**: 플러그인이 로드되지 않음
   - ⚠️ **주황색**: 일부 플러그인 누락

3. **플러그인 로드**
   - `Load Plugins Manually` 버튼 클릭
   - 또는 Maya의 `Window > Settings/Preferences > Plug-in Manager`에서 수동 로드

4. **상태 새로고침**
   - `Refresh Status` 버튼 클릭하여 최신 상태 확인

## 🎯 기본 작업 흐름

### 1. 씬 객체 준비
1. **커브 생성/선택**
   - NURBS 커브 또는 베지어 커브 준비
   - 커브를 선택한 상태에서 GUI 실행

2. **메시 준비**
   - 오프셋을 적용할 메시 오브젝트 준비
   - 메시를 선택한 상태에서 작업

### 2. 오프셋 디포머 설정
1. **Offset Deformer Settings 탭 선택**
2. **기본 파라미터 설정**
   - **Offset Mode**: Arc Segment (빠름) 또는 B-Spline (정확함) 선택
   - **Falloff Radius**: 영향 반경 설정
   - **Max Influences**: 최대 영향 곡선 수 설정

3. **고급 파라미터 설정**
   - **Volume Strength**: 볼륨 보존 강도 (0.0-2.0)
   - **Slide Effect**: 슬라이딩 효과 (-1.0-1.0)
   - **Rotation/Scale/Twist Distribution**: 각 변형 성분의 분포 조절
   - **Axial Sliding**: 축 방향 슬라이딩 효과

### 3. 바인딩 및 연결
1. **Binding & Connections 탭 선택**
2. **커브와 메시 선택**
   - 커브를 먼저 선택
   - 메시를 선택 (Shift 키로 다중 선택)
3. **Bind Selected 버튼 클릭**
   - 자동으로 오프셋 디포머 생성 및 바인딩

### 4. 가중치 조정
1. **Paint Weights 버튼 클릭**
   - Maya의 가중치 페인팅 도구 활성화
2. **가중치 페인팅**
   - 브러시 크기 및 강도 조정
   - 메시의 각 부분에 가중치 적용

## ⚙️ 고급 기능

### 커브 최적화
1. **Input Curve Optimizer 탭 선택**
2. **최적화 알고리즘 선택**
   - **Simplify**: 단순화 알고리즘
   - **Smooth**: 스무딩 알고리즘
   - **Refine**: 정교화 알고리즘
3. **파라미터 조정**
4. **Apply Optimization 버튼 클릭**

### 통합 워크플로우
1. **Integrated Workflow 탭 선택**
2. **워크플로우 선택**
   - **Standard**: 표준 워크플로우
   - **Advanced**: 고급 워크플로우
   - **Custom**: 사용자 정의 워크플로우
3. **자동화된 작업 실행**

## 🛠️ 문제 해결

### 일반적인 문제들

#### 1. 플러그인이 로드되지 않음
**증상**: 경고 메시지 "필수 플러그인이 로드되지 않았습니다"
**해결 방법**:
1. Maya의 Plug-in Manager 확인
2. 플러그인 파일 경로 확인
3. 플러그인 의존성 확인
4. Maya 재시작

#### 2. GUI가 표시되지 않음
**증상**: Python 코드 실행 후 아무 반응 없음
**해결 방법**:
1. Python 경로 확인
2. PySide2 모듈 확인
3. 에러 메시지 확인
4. Maya 버전 호환성 확인

#### 3. 바인딩 실패
**증상**: "Bind Selected" 버튼 클릭 후 오류
**해결 방법**:
1. 객체 선택 순서 확인 (커브 → 메시)
2. 객체 타입 확인
3. 씬 상태 확인
4. 로그 메시지 확인

#### 4. 성능 문제
**증상**: 작업이 느리거나 멈춤
**해결 방법**:
1. 메시 폴리곤 수 줄이기
2. 반복 횟수 조정
3. 허용 오차 증가
4. Maya 설정 최적화

### 디버깅 팁
1. **로그 확인**
   - GUI 하단의 로그 영역에서 메시지 확인
   - 에러 및 경고 메시지 주의 깊게 읽기

2. **Maya 스크립트 에디터 확인**
   - Python 에러 메시지 확인
   - 스택 트레이스 분석

3. **플러그인 상태 모니터링**
   - Plugin Status 탭에서 실시간 상태 확인
   - 상태 변경 시 로그 메시지 확인

## 💡 팁과 모범 사례

### 성능 최적화
1. **작업 전 준비**
   - 불필요한 히스토리 정리
   - 씬 최적화
   - 메모리 정리

2. **파라미터 조정**
   - 작은 값부터 시작하여 점진적으로 증가
   - 허용 오차와 반복 횟수 균형 조정

3. **워크플로우 최적화**
   - 자주 사용하는 설정 저장
   - 배치 작업 활용

### 데이터 관리
1. **백업**
   - 작업 전 씬 파일 백업
   - 중요한 설정값 기록

2. **버전 관리**
   - 작업 단계별 씬 파일 저장
   - 설정값 변경 이력 관리

### 사용자 정의
1. **단축키 설정**
   - 자주 사용하는 기능에 단축키 할당
   - Maya의 Hotkey Editor 활용

2. **프리셋 저장**
   - 자주 사용하는 파라미터 조합 저장
   - 프로젝트별 설정 관리

## 📚 추가 리소스

### 문서
- `DESIGN_SPECIFICATION.md`: 설계 명세서
- `TECHNICAL_IMPLEMENTATION.md`: 기술 구현 문서
- `USER_GUIDE.md`: 사용자 가이드

### 예제 파일
- `examples/` 폴더의 샘플 씬 파일들
- `tutorials/` 폴더의 단계별 튜토리얼

### 지원
- GitHub Issues: 버그 리포트 및 기능 요청
- Wiki: 추가 문서 및 FAQ
- Community: 사용자 커뮤니티

---

**참고**: 이 가이드는 Maya 2020 이상 버전을 기준으로 작성되었습니다. 다른 버전에서는 일부 기능이 다를 수 있습니다.
