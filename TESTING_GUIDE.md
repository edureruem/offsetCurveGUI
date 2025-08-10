# 🧪 Offset Curve Deformer System - Testing Guide

이 가이드는 Offset Curve Deformer 시스템의 테스트 방법을 설명합니다.

## 📋 테스트 개요

### 테스트 목표
- C++ 플러그인과 Python 래퍼의 연동 확인
- GUI 기능의 정상 작동 검증
- 전체 워크플로우의 통합 테스트
- 에러 처리 및 예외 상황 대응 확인

### 테스트 환경 요구사항
- Maya 2020 이상
- `inputCurveOptimizer` 플러그인 로드됨
- `offsetCurveDeformer` 플러그인 로드됨
- Python 2.7 또는 3.x

## 🚀 테스트 실행 방법

### 방법 1: 간단한 테스트 스크립트 (권장)

1. **Maya Script Editor 열기**
   - Maya에서 `Windows > General Editors > Script Editor` 선택

2. **테스트 스크립트 실행**
   ```python
   # maya_test_script.py의 내용을 복사하여 붙여넣기
   exec(open("path/to/maya_test_script.py").read())
   ```

3. **결과 확인**
   - Script Editor의 History 탭에서 테스트 결과 확인
   - 성공/실패 항목 및 에러 메시지 확인

### 방법 2: GUI 테스트 도구

1. **GUI 테스트 스크립트 실행**
   ```python
   # maya_gui_test.py의 내용을 복사하여 붙여넣기
   exec(open("path/to/maya_gui_test.py").read())
   ```

2. **테스트 GUI 사용**
   - 플러그인 상태 확인
   - Python 래퍼 테스트
   - 테스트 씬 생성 및 정리
   - 워크플로우 통합 테스트

### 방법 3: 통합 워크플로우 테스트

1. **전체 테스트 스크립트 실행**
   ```python
   # test_integrated_workflow.py의 내용을 복사하여 붙여넣기
   exec(open("path/to/test_integrated_workflow.py").read())
   ```

2. **상세 테스트 결과 확인**
   - 각 단계별 테스트 결과
   - 성공률 계산
   - 문제점 식별

## 🔍 단계별 테스트 항목

### 1단계: 플러그인 가용성 테스트
- [ ] `inputCurveOptimizer` 플러그인 로드 상태
- [ ] `offsetCurveDeformer` 플러그인 로드 상태
- [ ] 플러그인 에러 메시지 확인

### 2단계: Python 래퍼 가용성 테스트
- [ ] 소스 디렉토리 경로 설정
- [ ] `InputCurveOptimizerWrapper` 임포트
- [ ] `OffsetCurveDeformerWrapper` 임포트
- [ ] 래퍼 클래스 인스턴스 생성

### 3단계: 기본 기능 테스트
- [ ] 워크플로우 상태 확인
- [ ] 기본 메서드 호출
- [ ] 에러 처리 검증

### 4단계: 워크플로우 통합 테스트
- [ ] 테스트 씬 생성
- [ ] inputCurveOptimizer 워크플로우
- [ ] offsetCurveDeformer 워크플로우
- [ ] 엔드투엔드 워크플로우

### 5단계: 정리 및 검증
- [ ] 테스트 오브젝트 정리
- [ ] 메모리 누수 확인
- [ ] 최종 결과 요약

## 📊 테스트 결과 해석

### 성공률 기준
- **80% 이상**: 🎉 EXCELLENT - 시스템이 완벽하게 작동
- **60-79%**: 👍 GOOD - 대부분의 기능이 정상 작동
- **40-59%**: ⚠️ FAIR - 일부 기능에 문제가 있음
- **40% 미만**: ❌ NEEDS IMPROVEMENT - 상당한 문제가 있음

### 일반적인 문제점 및 해결방법

#### 1. 플러그인이 로드되지 않는 경우
```
❌ inputCurveOptimizer: Not loaded
❌ offsetCurveDeformer: Not loaded
```

**해결방법:**
- Maya 플러그인 매니저에서 플러그인 로드
- 플러그인 파일 경로 확인
- Maya 버전 호환성 확인

#### 2. Python 래퍼 임포트 실패
```
❌ InputCurveOptimizerWrapper: No module named 'inputCurveOptimizer'
```

**해결방법:**
- `src` 디렉토리 경로 확인
- Python 경로 설정 확인
- 파일 권한 및 존재 여부 확인

#### 3. 워크플로우 실행 실패
```
⚠️ Mesh to curve workflow: Failed to create optimizer node
```

**해결방법:**
- C++ 플러그인 상태 재확인
- Maya 씬 상태 확인
- 오브젝트 선택 상태 확인

## 🛠️ 고급 테스트

### 성능 테스트
```python
import time

# 워크플로우 실행 시간 측정
start_time = time.time()
result = optimizer.workflow_mesh_to_curve(mesh)
end_time = time.time()

execution_time = end_time - start_time
print(f"Execution time: {execution_time:.2f} seconds")
```

### 메모리 사용량 테스트
```python
import gc
import sys

# 메모리 사용량 확인
def check_memory():
    gc.collect()
    return sys.getsizeof(globals())

initial_memory = check_memory()
# 워크플로우 실행
final_memory = check_memory()
print(f"Memory usage: {final_memory - initial_memory} bytes")
```

### 스트레스 테스트
```python
# 반복 실행으로 안정성 테스트
for i in range(100):
    try:
        result = optimizer.workflow_mesh_to_curve(mesh)
        if not result['success']:
            print(f"Test {i} failed: {result['message']}")
    except Exception as e:
        print(f"Test {i} exception: {e}")
```

## 📝 테스트 결과 기록

### 테스트 결과 템플릿
```
테스트 날짜: [YYYY-MM-DD]
Maya 버전: [버전]
테스트 환경: [OS, Python 버전 등]

테스트 결과:
- 플러그인 가용성: ✅/❌
- Python 래퍼: ✅/❌
- 기본 기능: ✅/❌
- 워크플로우 통합: ✅/❌
- 정리: ✅/❌

성공률: [XX.X]%
전체 결과: [EXCELLENT/GOOD/FAIR/NEEDS IMPROVEMENT]

발견된 문제점:
1. [문제 설명]
2. [문제 설명]

해결 방안:
1. [해결 방법]
2. [해결 방법]

추가 테스트 필요사항:
- [ ] [테스트 항목]
- [ ] [테스트 항목]
```

## 🔧 문제 해결 가이드

### 일반적인 문제 해결 순서
1. **플러그인 상태 확인**
   - Maya 플러그인 매니저에서 상태 확인
   - 에러 로그 확인

2. **Python 환경 확인**
   - Python 경로 설정 확인
   - 모듈 임포트 경로 확인

3. **Maya 씬 상태 확인**
   - 선택된 오브젝트 확인
   - 씬 파일 상태 확인

4. **권한 및 파일 확인**
   - 파일 읽기/쓰기 권한 확인
   - 파일 경로 정확성 확인

### 디버깅 팁
- Maya Script Editor의 History 탭 활용
- Python 예외 처리 및 로깅 추가
- 단계별 테스트로 문제점 분리
- Maya 내장 도구 활용 (Node Editor, Attribute Editor 등)

## 📞 지원 및 문의

테스트 중 문제가 발생하거나 추가 지원이 필요한 경우:
1. 에러 메시지 전체 복사
2. Maya 버전 및 환경 정보
3. 테스트 스크립트 실행 결과
4. 재현 가능한 단계별 설명

이 정보를 바탕으로 문제 해결을 도와드리겠습니다.

---

**🎯 테스트 목표: 완벽하게 작동하는 Offset Curve Deformer 시스템 구축!**
