# Offset Curve Deformer & Input Curve Optimizer GUI

Maya 2020 호환 오프셋 커브 디포머 및 입력 커브 최적화 GUI 시스템입니다.

## 🚀 주요 기능

### 1. Input Curve Optimizer
- **메시 기반 커브 생성**: 메시 오브젝트에서 최적화된 커브 자동 생성
- **스켈레톤 기반 커브 생성**: 조인트 체인을 따라 최적화된 커브 생성
- **기존 커브 최적화**: NURBS 커브의 제어점 수 최적화 및 부드러움 개선
- **품질 기반 최적화**: 곡률과 형태를 고려한 지능형 최적화

### 2. Offset Curve Deformer
- **Arc Segment 방식**: 세그먼트를 호(arc)로 근사하여 오프셋 생성
- **B-Spline 방식**: B-Spline 곡선 기반 정밀한 오프셋 생성
- **적응형 오프셋**: 곡률에 따라 거리를 자동 조정하는 오프셋
- **모서리 처리**: 둥근 모서리, 적응형 모서리 처리 지원

### 3. 통합 워크플로우
- **Maya 씬 연동**: Maya 2020과 직접 연동하여 커브 데이터 처리
- **워크플로우 기반**: 단계별 작업 진행 및 상태 관리
- **자동화**: 선택된 오브젝트에서 자동으로 커브 생성 및 최적화

## 🛠️ 설치 및 실행

### 필수 요구사항
- Maya 2020
- Python 2.7 (Maya 2020 기본)
- PySide2 (Maya 2020 기본 제공)

### 설치 방법

1. **프로젝트 클론**
```bash
git clone <repository-url>
cd offsetCurveGUI
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **Maya에서 실행**
```python
# Maya 스크립트 에디터에서
exec(open("src/main.py").read())
```

## 🎨 GUI 사용법

### Scene Objects 관리
- **Curves**: 씬의 모든 커브를 리스트로 표시
- **Meshes**: 씬의 모든 메시를 리스트로 표시  
- **Joints**: 씬의 모든 조인트를 리스트로 표시
- **Add/Del**: 수동으로 오브젝트 추가/제거

### Offset Deformer 설정
- **Arc Segment**: 세그먼트 수, 허용오차 설정
- **B-Spline**: 차수, 노트 타입 설정
- **Deformer Options**: 가중치 페인팅 모드, 자동 업데이트

### Binding & Connections
- **자동 감지**: 커브의 custom attributes에서 연결된 디포머 노드 자동 찾기
- **Bind Selected**: 선택된 커브와 메시를 바인딩
- **Paint Weights**: 바인딩된 메시의 가중치 페인팅 모드 활성화

## 🔧 기술적 특징

### Arc Segment 방식
- 각 세그먼트를 호(arc)로 근사
- 세그먼트 수와 허용오차 조정 가능
- 빠른 처리 속도와 안정성

### B-Spline 방식
- 정밀한 B-Spline 곡선 기반
- 차수와 노트 타입 선택 가능
- Uniform, Chord Length, Centripetal 노트 지원

### 적응형 오프셋
- 곡률 기반 거리 자동 조정
- 높은 곡률에서는 거리 감소
- 낮은 곡률에서는 거리 증가

## 📁 프로젝트 구조

```
offsetCurveGUI/
├── src/
│   ├── core/                 # 핵심 시스템
│   ├── inputCurveOptimizer/  # 입력 커브 최적화
│   ├── offsetCurveDeformer/  # 오프셋 커브 디포머
│   └── integratedWorkflow/   # 통합 워크플로우
├── ui/                       # GUI 인터페이스
├── external/                 # 외부 플러그인
└── docs/                     # 문서
```

## 🎯 사용 시나리오

### 1. 캐릭터 의상 커브 생성
```
1. 스커트 메시 선택
2. Input Curve Optimizer로 최적화된 커브 생성
3. Arc Segment 방식으로 내부/외부 경계선 오프셋
4. 바인딩 및 가중치 페인팅
```

### 2. 건축 디자인 커브
```
1. 건물 외곽선 메시 선택
2. B-Spline 방식으로 정밀한 오프셋 생성
3. 적응형 오프셋으로 곡률에 따른 거리 조정
4. 결과 커브를 건축 도면에 활용
```

## 🔍 문제 해결

### 일반적인 문제들
- **커브가 생성되지 않음**: 메시 선택 확인, Maya 버전 호환성 체크
- **오프셋이 부정확함**: 허용오차 조정, 세그먼트 수 증가
- **바인딩 실패**: 커브와 메시 선택 순서 확인

### 성능 최적화
- **대용량 메시**: 세그먼트 수 줄이기, 허용오차 증가
- **복잡한 커브**: B-Spline 차수 조정, 노트 타입 변경

## 📞 지원 및 문의

- **이슈 리포트**: GitHub Issues
- **기능 요청**: Feature Request 템플릿 사용
- **문서 개선**: Pull Request 환영

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**Maya 호환성**: 2020+  
**Python 버전**: 2.7 (Maya 2020), 3.7+ (독립 실행)

더 자세한 정보는 `docs/` 폴더의 문서를 참조하세요.
