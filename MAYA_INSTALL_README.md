# OffsetCurveGUI Maya 설치 및 사용 가이드

## 🚀 빠른 시작

### 1. Maya에서 바로 실행 (설치 없이)
```python
# Maya Script Editor에서 실행
import sys
sys.path.append('path/to/offsetCurveGUI')
from ui.maya_main_window import MayaOffsetCurveGUI

window = MayaOffsetCurveGUI()
window.show()
```

### 2. Maya에 영구 설치
```python
# Maya Script Editor에서 실행
exec(open('path/to/offsetCurveGUI/install_maya.py').read())
```

## 📁 프로젝트 구조

```
offsetCurveGUI/
├── external/                    # 외부 모듈 (서브모듈)
│   ├── offsetCurveDeformer/    # 오프셋 커브 생성
│   └── inputCurveOptimizer/    # 커브 최적화
├── src/                        # 핵심 기능
├── ui/                         # Maya GUI
├── docs/                       # 문서
├── install_maya.py             # Maya 설치 스크립트
└── requirements.txt            # Python 의존성
```

## 🔧 설치 방법

### 방법 1: 자동 설치 (권장)
1. `install_maya.py` 파일을 Maya Script Editor에서 실행
2. "Maya에 설치" 버튼 클릭
3. Maya 재시작
4. 메뉴에서 "OffsetCurveGUI" 찾기

### 방법 2: 수동 설치
1. `offsetCurveGUI` 폴더를 Maya 사용자 스크립트 폴더에 복사
2. Maya Script Editor에서 Python 경로 추가:
```python
import sys
sys.path.append('path/to/maya/scripts/offsetCurveGUI')
```

## 🎯 주요 기능

### Offset Curve Deformer
- **평행 오프셋**: 커브와 평행한 오프셋 생성
- **수직 오프셋**: 커브에 수직인 오프셋 생성
- **적응형 오프셋**: 커브 특성에 따른 자동 오프셋

### Input Curve Optimizer
- **품질 기반 최적화**: 품질을 유지하면서 포인트 수 줄이기
- **포인트 감소**: Douglas-Peucker 알고리즘
- **스무딩**: 커브를 부드럽게 만들기

## 📖 사용법

### 1. 커브 선택
Maya에서 오프셋을 생성할 커브를 선택합니다.

### 2. GUI 열기
- 메뉴: `OffsetCurveGUI` → `Offset Curve Deformer`
- 또는 직접 실행: `MayaOffsetCurveGUI().show()`

### 3. 파라미터 설정
- **오프셋 모드**: Arc Segment (빠름) vs B-Spline (정확함)
- **영향 반경**: 메시 정점이 커브로부터 받는 영향의 범위
- **최대 영향 수**: 한 정점이 받을 수 있는 최대 커브 영향 수
- **볼륨 보존**: 메시의 원래 부피를 유지하는 강도
- **슬라이딩 효과**: 커브를 따라 미끄러지는 효과의 강도
- **회전/스케일/꼬임 분포**: 변형의 각 성분별 분포 조절

### 4. 실행
- "오프셋 커브 생성" 버튼 클릭
- "커브 최적화" 버튼 클릭

## 🐛 문제 해결

### Import 오류
```python
# Python 경로 확인
import sys
print(sys.path)

# 경로 추가
sys.path.append('path/to/offsetCurveGUI')
```

### Maya 버전 호환성
- Maya 2020 이상 지원
- PySide2 사용 (Maya 2020 기본)

### 권한 문제
- Maya 사용자 스크립트 폴더에 쓰기 권한 확인
- 관리자 권한으로 Maya 실행

## 🔄 업데이트

### 서브모듈 업데이트
```bash
# 프로젝트 폴더에서
git submodule update --remote

# 특정 모듈만 업데이트
git submodule update --remote external/offsetCurveDeformer
```

### 전체 프로젝트 업데이트
```bash
git pull origin main
git submodule update --init --recursive
```

## 📚 추가 문서

- [디자인 명세서](docs/DESIGN_SPECIFICATION.md)
- [기술 구현서](docs/TECHNICAL_IMPLEMENTATION.md)
- [사용자 가이드](docs/USER_GUIDE.md)

## 🤝 지원

문제가 발생하거나 질문이 있으면:
1. GitHub Issues 확인
2. 문서 참조
3. 개발팀에 문의

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
