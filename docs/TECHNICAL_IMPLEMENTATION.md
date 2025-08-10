# 기술적 구현 세부사항

## 1. 코드 구조 및 아키텍처

### 1.1 프로젝트 구조
```
offsetCurveGUI/
├── src/
│   ├── __init__.py
│   ├── main.py                          # 메인 진입점
│   ├── integratedWorkflow/
│   │   ├── __init__.py
│   │   └── workflow_manager.py          # 워크플로우 관리자
│   ├── inputCurveOptimizer/
│   │   └── __init__.py                  # 커브 최적화 엔진 (구현 예정)
│   └── offsetCurveDeformer/
│       └── __init__.py                  # 오프셋 생성 엔진 (구현 예정)
├── ui/
│   ├── __init__.py
│   ├── main_window.py                   # 메인 윈도우 UI
│   ├── advancedOptions/
│   │   ├── __init__.py
│   │   └── advanced_panel.py            # 고급 옵션 패널
│   ├── basicWorkflow/
│   │   └── __init__.py                  # 기본 워크플로우 UI (구현 예정)
│   └── contextAware/
│       ├── __init__.py
│       └── context_tools.py             # 컨텍스트 인식 도구
├── resources/                            # 리소스 파일 (이미지, 아이콘 등)
├── docs/                                # 문서
├── requirements.txt                      # Python 의존성
└── README.md                            # 프로젝트 개요
```

### 1.2 핵심 클래스 다이어그램

```python
# 주요 클래스 관계
WorkflowManager
├── workflow_steps: List[WorkflowStep]
├── current_step_index: int
├── workflow_status: str
└── logger: logging.Logger

MainWindow
├── workflow_manager: WorkflowManager
├── update_timer: Optional[Any]
└── UI 컴포넌트들

AdvancedOptionsPanel
├── parent: tk.Widget
├── on_apply: Callable
└── options: Dict[str, Any]

ContextAwareTools
├── parent: tk.Widget
├── on_apply_suggestions: Callable
└── curve_analysis: Dict[str, Any]
```

## 2. 핵심 컴포넌트 구현

### 2.1 WorkflowManager 클래스

#### 2.1.1 클래스 정의
```python
@dataclass
class WorkflowStep:
    """워크플로우 단계 정보"""
    name: str
    description: str
    status: str  # 'pending', 'running', 'completed', 'failed'
    parameters: Dict[str, Any]
    result: Optional[Any] = None

class WorkflowManager:
    """통합 워크플로우 매니저"""
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.workflow_steps: List[WorkflowStep] = []
        self.current_step_index = 0
        self.workflow_status = "idle"
```

#### 2.1.2 워크플로우 초기화
```python
def _initialize_workflow_steps(self):
    """워크플로우 단계 초기화"""
    steps_config = [
        {
            'name': 'Input Curve Loading',
            'description': '입력 커브 파일 로드 및 파싱',
            'parameters': {'file_path': '', 'file_format': ''}
        },
        {
            'name': 'Input Curve Optimization',
            'description': '입력 커브 품질 최적화',
            'parameters': {
                'optimization_level': 5,
                'target_point_count': 100,
                'smoothness_factor': 0.5,
                'complexity_reduction': 0.3
            }
        },
        {
            'name': 'Offset Curve Generation',
            'description': '오프셋 커브 생성',
            'parameters': {
                'offset_distance': 10.0,
                'offset_algorithm': 'parallel',
                'quality_level': 7,
                'corner_handling': 'round'
            }
        },
        {
            'name': 'Result Validation',
            'description': '결과 품질 검증',
            'parameters': {'validation_level': 'standard'}
        },
        {
            'name': 'Export Results',
            'description': '결과 내보내기',
            'parameters': {
                'output_format': 'SVG',
                'output_path': '',
                'include_metadata': True
            }
        }
    ]
    
    for step_config in steps_config:
        step = WorkflowStep(
            name=step_config['name'],
            description=step_config['description'],
            status='pending',
            parameters=step_config['parameters']
        )
        self.workflow_steps.append(step)
```

#### 2.1.3 워크플로우 실행 메서드
```python
def start_workflow(self) -> bool:
    """워크플로우 시작"""
    try:
        self.workflow_status = "running"
        self.current_step_index = 0
        self.logger.info("워크플로우 시작됨")
        return True
    except Exception as e:
        self.logger.error(f"워크플로우 시작 실패: {e}")
        self.workflow_status = "failed"
        return False

def execute_current_step(self) -> bool:
    """현재 단계 실행"""
    if self.current_step_index >= len(self.workflow_steps):
        return False
    
    current_step = self.workflow_steps[self.current_step_index]
    current_step.status = "running"
    
    try:
        # 단계별 실행 로직
        if current_step.name == "Input Curve Loading":
            success = self._execute_input_curve_loading(current_step)
        elif current_step.name == "Input Curve Optimization":
            success = self._execute_input_curve_optimization(current_step)
        elif current_step.name == "Offset Curve Generation":
            success = self._execute_offset_curve_generation(current_step)
        elif current_step.name == "Result Validation":
            success = self._execute_result_validation(current_step)
        elif current_step.name == "Export Results":
            success = self._execute_export_results(current_step)
        else:
            success = False
        
        if success:
            current_step.status = "completed"
            self.logger.info(f"단계 '{current_step.name}' 완료됨")
        else:
            current_step.status = "failed"
            self.logger.error(f"단계 '{current_step.name}' 실패함")
        
        return success
        
    except Exception as e:
        current_step.status = "failed"
        self.logger.error(f"단계 '{current_step.name}' 실행 중 오류: {e}")
        return False
```

### 2.2 MainWindow 클래스

#### 2.2.1 UI 초기화
```python
def setup_ui(self):
    """UI 컴포넌트 설정"""
    # 메인 프레임
    main_frame = ttk.Frame(self.root, padding="10")
    main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    # 그리드 가중치 설정
    self.root.columnconfigure(0, weight=1)
    self.root.rowconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.rowconfigure(3, weight=1)
    
    # UI 섹션 생성
    self.setup_title_section(main_frame, 0)
    self.setup_workflow_section(main_frame, 1)
    self.setup_parameters_section(main_frame, 2)
    self.setup_log_section(main_frame, 3)
```

#### 2.2.2 워크플로우 섹션
```python
def setup_workflow_section(self, parent, row):
    """워크플로우 진행 상황 및 제어 섹션"""
    # 워크플로우 프레임
    workflow_frame = ttk.LabelFrame(parent, text="워크플로우 진행 상황", padding="10")
    workflow_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    workflow_frame.columnconfigure(1, weight=1)
    
    # 진행 표시줄
    self.progress_var = tk.DoubleVar()
    self.progress_bar = ttk.Progressbar(
        workflow_frame, 
        variable=self.progress_var, 
        maximum=100
    )
    self.progress_bar.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
    
    # 단계별 상태 표시
    self.setup_step_status_display(workflow_frame, 1)
    
    # 제어 버튼
    self.setup_control_buttons(workflow_frame, 2)
```

#### 2.2.3 파라미터 설정 섹션
```python
def setup_parameters_section(self, parent, row):
    """파라미터 설정 섹션"""
    # 노트북 위젯으로 탭 생성
    self.param_notebook = ttk.Notebook(parent)
    self.param_notebook.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
    
    # 기본 파라미터 탭
    basic_frame = ttk.Frame(self.param_notebook)
    self.param_notebook.add(basic_frame, text="기본 설정")
    self.setup_basic_parameters(basic_frame)
    
    # 고급 옵션 탭
    advanced_frame = ttk.Frame(self.param_notebook)
    self.param_notebook.add(advanced_frame, text="고급 옵션")
    self.advanced_panel = AdvancedOptionsPanel(advanced_frame, self.apply_advanced_options)
    
    # 컨텍스트 인식 도구 탭
    context_frame = ttk.Frame(self.param_notebook)
    self.param_notebook.add(context_frame, text="컨텍스트 인식 도구")
    self.context_tools = ContextAwareTools(context_frame, self.apply_context_suggestions)
```

### 2.3 AdvancedOptionsPanel 클래스

#### 2.3.1 UI 구성
```python
def setup_ui(self):
    """UI 컴포넌트 설정"""
    # 메인 프레임
    main_frame = ttk.Frame(self.parent)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 노트북 위젯으로 탭 생성
    self.notebook = ttk.Notebook(main_frame)
    self.notebook.pack(fill=tk.BOTH, expand=True)
    
    # Input Curve Optimizer 고급 옵션 탭
    optimizer_frame = ttk.Frame(self.notebook)
    self.notebook.add(optimizer_frame, text="Input Curve Optimizer")
    self.setup_optimizer_options(optimizer_frame)
    
    # Offset Curve Deformer 고급 옵션 탭
    deformer_frame = ttk.Frame(self.notebook)
    self.notebook.add(deformer_frame, text="Offset Curve Deformer")
    self.setup_deformer_options(deformer_frame)
    
    # 성능 설정 탭
    performance_frame = ttk.Frame(self.notebook)
    self.notebook.add(performance_frame, text="성능 설정")
    self.setup_performance_options(performance_frame)
    
    # 적용 버튼
    apply_button = ttk.Button(main_frame, text="설정 적용", command=self.apply_options)
    apply_button.pack(pady=(10, 0))
```

#### 2.3.2 최적화 옵션 설정
```python
def setup_optimizer_options(self, parent):
    """Input Curve Optimizer 고급 옵션 설정"""
    # 곡률 기반 최적화 프레임
    curvature_frame = ttk.LabelFrame(parent, text="곡률 기반 최적화", padding="10")
    curvature_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # 곡률 임계값
    ttk.Label(curvature_frame, text="곡률 임계값:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
    self.curvature_threshold_var = tk.DoubleVar(value=0.1)
    curvature_scale = ttk.Scale(
        curvature_frame, 
        from_=0.0, 
        to=1.0, 
        variable=self.curvature_threshold_var,
        orient=tk.HORIZONTAL
    )
    curvature_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
    ttk.Label(curvature_frame, textvariable=self.curvature_threshold_var).grid(row=0, column=2)
    
    # 적응형 샘플링
    self.adaptive_sampling_var = tk.BooleanVar(value=True)
    adaptive_check = ttk.Checkbutton(
        curvature_frame, 
        text="적응형 샘플링", 
        variable=self.adaptive_sampling_var
    )
    adaptive_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
    
    # 특징 보존 수준
    ttk.Label(curvature_frame, text="특징 보존 수준:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
    self.preserve_features_var = tk.DoubleVar(value=0.8)
    features_scale = ttk.Scale(
        curvature_frame, 
        from_=0.0, 
        to=1.0, 
        variable=self.preserve_features_var,
        orient=tk.HORIZONTAL
    )
    features_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(10, 0))
    ttk.Label(curvature_frame, textvariable=self.preserve_features_var).grid(row=2, column=2, pady=(10, 0))
```

### 2.4 ContextAwareTools 클래스

#### 2.4.1 커브 특성 분석
```python
def analyze_curve(self, curve_data: Dict[str, Any]) -> Dict[str, Any]:
    """커브 특성 분석"""
    try:
        # 기본 특성 분석
        basic_analysis = self._analyze_basic_characteristics(curve_data)
        
        # 고급 특성 분석
        advanced_analysis = self._analyze_advanced_characteristics(curve_data)
        
        # 분석 결과 통합
        self.curve_analysis = {
            'basic': basic_analysis,
            'advanced': advanced_analysis,
            'timestamp': time.time()
        }
        
        # 자동 설정 제안 생성
        suggestions = self._generate_automatic_suggestions()
        self.curve_analysis['suggestions'] = suggestions
        
        # UI 업데이트
        self.display_analysis_results()
        self.display_suggestions()
        
        return self.curve_analysis
        
    except Exception as e:
        messagebox.showerror("분석 오류", f"커브 특성 분석 중 오류가 발생했습니다:\n{str(e)}")
        return {}
```

#### 2.4.2 특성 분석 메서드
```python
def _analyze_basic_characteristics(self, curve_data: Dict[str, Any]) -> Dict[str, Any]:
    """기본 특성 분석"""
    points = curve_data.get('points', [])
    
    if not points:
        return {}
    
    # 포인트 수 및 밀도
    point_count = len(points)
    
    # 바운딩 박스 계산
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    width = max_x - min_x
    height = max_y - min_y
    area = width * height
    
    # 전체 길이 계산
    total_length = self._calculate_perimeter(points)
    
    # 밀도 계산
    density = point_count / area if area > 0 else 0
    
    return {
        'point_count': point_count,
        'bounding_box': {
            'width': width,
            'height': height,
            'area': area
        },
        'total_length': total_length,
        'density': density
    }

def _analyze_advanced_characteristics(self, curve_data: Dict[str, Any]) -> Dict[str, Any]:
    """고급 특성 분석"""
    points = curve_data.get('points', [])
    
    if len(points) < 3:
        return {}
    
    # 곡률 분석
    curvature_analysis = self._analyze_curvature_distribution(points)
    
    # 복잡도 지수 계산
    complexity_index = self._calculate_complexity_index(points)
    
    # 대칭성 분석
    symmetry_analysis = self._analyze_symmetry(points)
    
    # 특징점 식별
    feature_points = self._identify_feature_points(points)
    
    return {
        'curvature': curvature_analysis,
        'complexity_index': complexity_index,
        'symmetry': symmetry_analysis,
        'feature_points': feature_points
    }
```

## 3. 데이터 흐름 및 상태 관리

### 3.1 워크플로우 상태 전이

```python
# 워크플로우 상태 전이 다이어그램
idle → running → completed/failed
  ↑         ↓
  └── reset_workflow()
```

### 3.2 데이터 전달 흐름

```python
# 데이터 전달 흐름
Input Curve → WorkflowManager → Input Curve Optimizer → 
Offset Curve Deformer → Result Validator → Export Manager
```

### 3.3 이벤트 처리

```python
def start_status_updates(self):
    """워크플로우 상태 업데이트 타이머 시작"""
    def update_status():
        try:
            self.update_workflow_status()
            self.update_button_states()
            self.update_progress()
        except Exception as e:
            print(f"상태 업데이트 오류: {e}")
        finally:
            # 100ms마다 업데이트
            self.update_timer = self.root.after(100, update_status)
    
    update_status()
```

## 4. 성능 최적화 기법

### 4.1 비동기 처리
```python
def execute_workflow_async(self):
    """비동기 워크플로우 실행"""
    def run_workflow():
        try:
            self.workflow_manager.start_workflow()
            while self.workflow_manager.workflow_status == "running":
                if not self.workflow_manager.execute_current_step():
                    break
                self.workflow_manager.next_step()
                time.sleep(0.1)  # UI 업데이트를 위한 지연
        except Exception as e:
            self.log_message(f"워크플로우 실행 오류: {e}")
    
    # 별도 스레드에서 실행
    workflow_thread = threading.Thread(target=run_workflow, daemon=True)
    workflow_thread.start()
```

### 4.2 메모리 관리
```python
def cleanup_memory(self):
    """메모리 정리"""
    import gc
    
    # 가비지 컬렉션 실행
    gc.collect()
    
    # 임시 데이터 정리
    if hasattr(self, 'temp_data'):
        del self.temp_data
        self.temp_data = None
    
    # 로그 메시지 제한
    if hasattr(self, 'log_messages') and len(self.log_messages) > 1000:
        self.log_messages = self.log_messages[-500:]
```

## 5. 오류 처리 및 로깅

### 5.1 구조화된 로깅
```python
def _setup_logging(self) -> logging.Logger:
    """로깅 설정"""
    logger = logging.getLogger('OffsetCurveGUI')
    logger.setLevel(logging.INFO)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 파일 핸들러
    log_file = Path("logs/offset_curve_gui.log")
    log_file.parent.mkdir(exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # 포맷터
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

### 5.2 예외 처리 전략
```python
def safe_execute(self, func: Callable, *args, **kwargs) -> Tuple[bool, Any]:
    """안전한 함수 실행"""
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        self.logger.error(f"함수 실행 오류: {func.__name__}, 오류: {e}")
        return False, str(e)
```

## 6. 확장성 고려사항

### 6.1 플러그인 아키텍처
```python
class PluginManager:
    """플러그인 관리자"""
    
    def __init__(self):
        self.plugins = {}
        self.plugin_dirs = []
    
    def register_plugin(self, name: str, plugin_class: type):
        """플러그인 등록"""
        self.plugins[name] = plugin_class()
    
    def get_plugin(self, name: str):
        """플러그인 가져오기"""
        return self.plugins.get(name)
    
    def list_plugins(self) -> List[str]:
        """등록된 플러그인 목록"""
        return list(self.plugins.keys())
```

### 6.2 설정 관리 시스템
```python
class ConfigurationManager:
    """설정 관리자"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"설정 파일 로드 오류: {e}")
        
        return self.get_default_config()
    
    def save_config(self):
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"설정 파일 저장 오류: {e}")
```

## 7. 테스트 및 디버깅

### 7.1 단위 테스트 예시
```python
import unittest
from unittest.mock import Mock, patch

class TestWorkflowManager(unittest.TestCase):
    """WorkflowManager 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        self.workflow_manager = WorkflowManager()
    
    def test_workflow_initialization(self):
        """워크플로우 초기화 테스트"""
        self.assertEqual(len(self.workflow_manager.workflow_steps), 5)
        self.assertEqual(self.workflow_manager.current_step_index, 0)
        self.assertEqual(self.workflow_manager.workflow_status, "idle")
    
    def test_start_workflow(self):
        """워크플로우 시작 테스트"""
        result = self.workflow_manager.start_workflow()
        self.assertTrue(result)
        self.assertEqual(self.workflow_manager.workflow_status, "running")
        self.assertEqual(self.workflow_manager.current_step_index, 0)
    
    def test_execute_current_step(self):
        """현재 단계 실행 테스트"""
        self.workflow_manager.start_workflow()
        result = self.workflow_manager.execute_current_step()
        # 실제 구현에서는 True가 반환되어야 함
        self.assertIsInstance(result, bool)
```

### 7.2 디버그 모드
```python
class DebugMode:
    """디버그 모드 관리"""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.debug_info = {}
    
    def log_debug_info(self, key: str, value: Any):
        """디버그 정보 기록"""
        if self.enabled:
            self.debug_info[key] = value
    
    def get_debug_info(self) -> Dict[str, Any]:
        """디버그 정보 반환"""
        return self.debug_info.copy()
    
    def clear_debug_info(self):
        """디버그 정보 초기화"""
        self.debug_info.clear()
```

## 8. 배포 및 패키징

### 8.1 PyInstaller 설정
```python
# build.spec 파일 예시
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('docs', 'docs'),
        ('requirements.txt', '.'),
        ('README.md', '.')
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OffsetCurveGUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico'
)
```

### 8.2 가상 환경 설정
```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화 (Windows)
venv\Scripts\activate

# 가상 환경 활성화 (Linux/Mac)
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 개발 의존성 설치
pip install pytest black flake8
```

---

이 문서는 Offset Curve Deformer & Input Curve Optimizer GUI의 기술적 구현 세부사항을 다룹니다. 실제 개발 시에는 이 문서를 참고하여 코드를 구현하고, 필요에 따라 설계를 조정할 수 있습니다.
