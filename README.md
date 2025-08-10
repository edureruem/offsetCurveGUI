# Offset Curve Deformer & Input Curve Optimizer GUI

offsetCurveDeformer와 inputCurveOptimizer를 통합하여 사용할 수 있는 직관적인 GUI 애플리케이션입니다.

## 🚀 주요 기능

### 🔧 통합 워크플로우
- **단계별 처리**: 입력 커브 로딩 → 최적화 → 오프셋 생성 → 검증 → 내보내기
- **자동화된 파이프라인**: 복잡한 설정 없이도 원클릭으로 전체 프로세스 실행
- **진행률 모니터링**: 실시간 워크플로우 진행 상황 확인

### 🎯 Input Curve Optimizer
- **스마트 최적화**: 곡률 기반 자동 포인트 최적화
- **품질 조절**: low/medium/high 최적화 레벨 선택
- **스무딩 제어**: 커브 부드러움 정도 조절
- **단순화 임계값**: 불필요한 포인트 자동 제거

### 📐 Offset Curve Deformer
- **다양한 오프셋**: left/right/both 방향 지원
- **거리 조절**: 정밀한 오프셋 거리 설정
- **품질 옵션**: low부터 ultra까지 품질 선택
- **충돌 해결**: 자동 오프셋 충돌 감지 및 해결

### 🧠 컨텍스트 인식 도구
- **자동 분석**: 입력 커브 특성 자동 감지
- **스마트 제안**: 커브 특성에 맞는 최적 설정 자동 제안
- **품질 최적화**: 커브 복잡도에 따른 자동 파라미터 조정

### ⚙️ 고급 옵션
- **알고리즘 선택**: parallel, perpendicular, adaptive 오프셋 방식
- **성능 최적화**: 병렬 처리, 메모리 제한, 캐시 설정
- **품질 우선순위**: speed, balanced, quality 중 선택

## 📋 시스템 요구사항

- **Python**: 3.8 이상
- **운영체제**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **메모리**: 최소 4GB RAM (권장 8GB+)
- **디스플레이**: 1280x720 이상 해상도

## 🛠️ 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/yourusername/offsetCurveGUI.git
cd offsetCurveGUI
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 또는
venv\Scripts\activate     # Windows
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

## 🚀 사용 방법

### 기본 실행
```bash
python src/main.py
```

### 워크플로우 사용법

1. **워크플로우 시작**
   - "워크플로우 시작" 버튼 클릭
   - 자동으로 첫 번째 단계(입력 커브 로딩) 실행

2. **단계별 실행**
   - "현재 단계 실행" 버튼으로 각 단계 수동 실행
   - "다음 단계" 버튼으로 다음 단계로 진행

3. **파라미터 설정**
   - 각 단계별 파라미터를 UI에서 조정
   - "파라미터 적용" 버튼으로 설정 저장

4. **결과 확인**
   - 로그 패널에서 실행 결과 확인
   - 진행률 바로 전체 진행 상황 모니터링

### 고급 사용법

#### 컨텍스트 인식 도구
1. "커브 분석 실행" 버튼 클릭
2. 자동으로 커브 특성 분석
3. "제안된 설정 적용"으로 최적 설정 자동 적용

#### 고급 옵션 설정
1. 고급 옵션 패널에서 세부 설정 조정
2. 알고리즘, 품질, 성능 옵션 선택
3. "고급 옵션 적용" 버튼으로 설정 저장

## 📁 프로젝트 구조

```
offsetCurveGUI/
├── src/                          # 소스 코드
│   ├── main.py                   # 메인 애플리케이션 진입점
│   ├── integratedWorkflow/       # 통합 워크플로우 관리
│   │   └── workflow_manager.py   # 워크플로우 매니저
│   ├── offsetCurveDeformer/      # 오프셋 커브 디포머
│   └── inputCurveOptimizer/      # 입력 커브 최적화
├── ui/                           # 사용자 인터페이스
│   ├── main_window.py            # 메인 윈도우
│   ├── advancedOptions/          # 고급 옵션
│   │   └── advanced_panel.py     # 고급 옵션 패널
│   ├── basicWorkflow/            # 기본 워크플로우
│   └── contextAware/             # 컨텍스트 인식 도구
│       └── context_tools.py      # 컨텍스트 인식 도구
├── resources/                     # 리소스 파일
├── docs/                         # 문서
├── requirements.txt               # Python 의존성
└── README.md                     # 프로젝트 설명서
```

## 🔧 개발자 가이드

### 새로운 기능 추가
1. `src/` 디렉토리에 새로운 모듈 생성
2. `ui/` 디렉토리에 해당 UI 컴포넌트 추가
3. `workflow_manager.py`에 새로운 워크플로우 단계 추가

### 테스트 실행
```bash
# 단위 테스트
pytest tests/

# 코드 품질 검사
flake8 src/ ui/
black src/ ui/
```

### 빌드 및 배포
```bash
# 실행 파일 생성 (PyInstaller 사용)
pyinstaller --onefile --windowed src/main.py

# 배포 패키지 생성
python setup.py sdist bdist_wheel
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원 및 문의

- **이슈 리포트**: [GitHub Issues](https://github.com/yourusername/offsetCurveGUI/issues)
- **문의**: your.email@example.com
- **문서**: [Wiki](https://github.com/yourusername/offsetCurveGUI/wiki)

## 🙏 감사의 말

- offsetCurveDeformer 개발팀
- inputCurveOptimizer 개발팀
- 이 프로젝트에 기여해주신 모든 분들

---

**참고**: 이 프로젝트는 개발 중인 상태입니다. 프로덕션 환경에서 사용하기 전에 충분한 테스트를 진행해주세요.
