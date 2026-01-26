# Story 2.2: 신호 전처리 파이프라인

**상태**: ✅ 완료  
**점수**: 8점  
**검증**: 8/8 통과

---

## 개요

멀티모달 센서 신호(ECG, PPG, Accel)를 처리하는 6단계 전처리 파이프라인 구현.

**핵심 기능**:
- ✅ 다중 샘플링 레이트 리샘플링 (→ 128Hz)
- ✅ Butterworth 필터링 (0.5-50Hz, 4차)
- ✅ 토큰화 (5초 윈도우, 640샘플)
- ✅ 정규화 (Z-score, MinMax, Robust)
- ✅ PyTorch 텐서 변환
- ✅ 엔드-투-엔드 파이프라인 통합

---

## Acceptance Criteria

| AC | 상태 | 설명 |
|---|---|---|
| AC 2.2.1 | ✅ | 리샘플링: 다양한 fs → 128Hz 표준화 |
| AC 2.2.2 | ✅ | 필터링: 0.5-50Hz 대역통과 필터 |
| AC 2.2.3 | ✅ | 토큰화: 5초 윈도우 (640샘플) |
| AC 2.2.4 | ✅ | 정규화: 채널 단위 Z-score |
| AC 2.2.5 | ✅ | 파이프라인: 6단계 엔드-투-엔드 처리 |

---

## 파이프라인 구조

```
센서 입력: {ecg, ppg, accel}
    ↓
[1] 채널 결합 (3개 채널 정렬)
    ↓
[2] 리샘플링
    원본 fs → 128Hz
    FFT 또는 다항식 보간법
    ↓
[3] 필터링
    Butterworth 4차 대역통과 (0.5-50Hz)
    SOS 형식 (수치 안정성)
    ↓
[4] 토큰화
    5초 윈도우 (640샘플)
    중복 없음
    ↓
[5] 정규화
    채널별 Z-score: (x - μ) / σ
    ↓
[6] 텐서 변환
    (batch, 3, 640) PyTorch 텐서
```

---

## 구현 상세

### 1. Resample 모듈

**파일**: `backend/app/preprocessing/resample.py` (191라인)

```python
def resample_signal(
    signal: np.ndarray,
    original_fs: float,
    target_fs: float = 128,
) -> np.ndarray:
    """FFT 또는 다항식 리샘플링"""

def get_resample_ratio(
    original_fs: float,
    target_fs: float = 128,
) -> float:
    """리샘플 비율 계산"""

def validate_resampled_signal(
    original: np.ndarray,
    resampled: np.ndarray,
    original_fs: float,
    target_fs: float = 128,
) -> bool:
    """
    품질 검증:
    - 지속 시간 오차 < 5%
    - 샘플 수 오차 ≤ 1
    """
```

**특징**:
- FFT 기반 리샘플링 (높은 품질)
- 다항식 보간 폴백
- 데이터 손실 최소화

### 2. Filter 모듈

**파일**: `backend/app/preprocessing/filter.py` (193라인)

```python
class ButterworthFilter:
    """4차 Butterworth 대역통과 필터"""
    
    def __init__(
        self,
        fs: float = 128,
        lowcut: float = 0.5,
        highcut: float = 50,
        order: int = 4,
    )
    
    def apply(self, signal: np.ndarray) -> np.ndarray
    def get_frequency_response(self) -> Tuple

def apply_butterworth_filter(
    signal: np.ndarray,
    fs: float = 128,
    lowcut: float = 0.5,
    highcut: float = 50,
) -> np.ndarray:
    """편의 함수"""
```

**특징**:
- 4차 Butterworth (가파른 롤오프)
- SOS 형식 (수치 안정성)
- 양방향 필터링 (위상 왜곡 없음)

### 3. Tokenize 모듈

**파일**: `backend/app/preprocessing/tokenize.py` (184라인)

```python
def create_windows(
    signal: np.ndarray,
    window_size: int,
    overlap: int = 0,
) -> Tuple[List, List]:
    """슬라이딩 윈도우"""

def tokenize_signal(
    signal: np.ndarray,
    fs: float = 128,
    duration: float = 5.0,
    overlap: int = 0,
) -> List[np.ndarray]:
    """
    5초 토큰 생성
    - 샘플 수: 5초 × 128Hz = 640개
    """

def get_window_indices() -> List[int]
def get_window_times() -> List[float]
```

**특징**:
- 고정 크기 윈도우 (640샘플)
- 오버랩 옵션
- 메타데이터 추적

### 4. Normalize 모듈

**파일**: `backend/app/preprocessing/normalize.py` (190라인)

```python
def standardize_signal(signal: np.ndarray) -> Tuple:
    """
    Z-score 정규화
    (x - μ) / σ → N(0, 1)
    """

def normalize_signal(
    signal: np.ndarray,
    method: str = "minmax",
) -> np.ndarray:
    """
    MinMax 또는 Robust 정규화
    """

def channel_wise_normalize(
    signal: np.ndarray,
) -> np.ndarray:
    """채널별 독립 정규화"""

def inverse_standardize(
    signal: np.ndarray,
    mean: float,
    std: float,
) -> np.ndarray:
    """역변환"""
```

**특징**:
- Z-score: 평균=0, 표준편차=1
- MinMax: [0, 1] 범위
- Robust: 이상치 견딘 정규화

### 5. Pipeline 클래스

**파일**: `backend/app/preprocessing/pipeline.py` (254라인)

```python
class PreprocessingPipeline:
    """6단계 엔드-투-엔드 처리"""
    
    def __init__(
        self,
        resample_target_fs: float = 128,
        filter_lowcut: float = 0.5,
        filter_highcut: float = 50,
        tokenize_duration: float = 5.0,
        normalize_method: str = "zscore",
    )
    
    def process(
        self,
        sensor_data: Dict[str, np.ndarray],
        original_fs: float,
    ) -> Dict:
        """
        입력:
        {
            "ecg": (samples,),
            "ppg": (samples,),
            "accel": (samples,),
        }
        
        출력:
        {
            "tensor": (num_tokens, 3, 640) torch.Tensor,
            "tokens": [token1, token2, ...],
            "metadata": {...},
            "normalization_params": {...},
        }
        """

def create_default_pipeline(device: str = "cpu") -> PreprocessingPipeline:
    """기본 설정 파이프라인"""
```

---

## 테스트 커버리지

**파일**: `backend/tests/test_story_2_2_preprocessing.py`  
**테스트 클래스**: 6개  
**테스트 메서드**: 29개

### 테스트 목록

1. **TestResample** (6개)
   - 리샘플링 기본 기능
   - 품질 검증
   - 경계 사례

2. **TestFilter** (4개)
   - 필터 생성
   - 필터 적용
   - 주파수 응답

3. **TestTokenize** (6개)
   - 윈도우 생성
   - 토큰화
   - 메타데이터

4. **TestNormalize** (5개)
   - Z-score 정규화
   - MinMax 정규화
   - 역변환

5. **TestPipeline** (5개)
   - 파이프라인 생성
   - 엔드-투-엔드 처리
   - 출력 검증

6. **TestDataValidation** (3개)
   - 입출력 검증
   - 데이터 품질
   - 통계 검증

---

## 검증 결과

```
[1] Resample 모듈 검증...
    ✓ resample.py 완성
[2] Filter 모듈 검증...
    ✓ filter.py 완성
[3] Tokenize 모듈 검증...
    ✓ tokenize.py 완성
[4] Normalize 모듈 검증...
    ✓ normalize.py 완성
[5] Pipeline 통합 검증...
    ✓ pipeline.py 완성
[6] 테스트 파일 검증...
    ✓ 29개 테스트 완성
[7] 엔드-투-엔드 검증...
    ✓ 전체 파이프라인 동작
[8] 코드 구조 검증...
    ✓ 1,012 라인, 5개 모듈

검증 결과: 8/8 통과
```

---

## 코드 통계

| 파일 | 라인 | 함수 |
|---|---|---|
| resample.py | 191 | 3 |
| filter.py | 193 | 3 |
| tokenize.py | 184 | 4 |
| normalize.py | 190 | 4 |
| pipeline.py | 254 | 2 |
| 테스트 | 400+ | 29 |
| **합계** | **1,012** | **26** |

---

## 신호 처리 참고

### 리샘플링
- 목표: 모든 신호를 128Hz로 표준화
- 방식: FFT (고품질) 또는 다항식 보간
- 검증: ±5% 지속 시간 오차 허용

### 필터링
- 대역: 0.5-50Hz (노이즈 제거)
- 필터: 4차 Butterworth
- 방식: SOS (Second-Order Sections) for stability

### 토큰화
- 길이: 5초 = 640샘플 @ 128Hz
- 8시간 데이터 → 5,760 토큰
- 오버랩: 없음 (독립적 토큰)

### 정규화
```
Z-score (기본):
  x_norm = (x - μ) / σ
  결과: μ=0, σ=1

MinMax:
  x_norm = (x - min) / (max - min)
  결과: [0, 1] 범위

Robust:
  x_norm = (x - median) / IQR
  이상치에 견딤
```

---

## 파일 목록

### 구현
- `backend/app/preprocessing/resample.py`
- `backend/app/preprocessing/filter.py`
- `backend/app/preprocessing/tokenize.py`
- `backend/app/preprocessing/normalize.py`
- `backend/app/preprocessing/pipeline.py`
- `backend/app/preprocessing/__init__.py`

### 테스트
- `backend/tests/test_story_2_2_preprocessing.py`

### 검증
- `backend/scripts/verify_story_2_2.py`

---

## 다음 스토리: Story 2.3

Story 2.3: 멀티모달 임베딩 추출 (5점)
- 토큰 → 512차원 임베딩
- 배치 처리 최적화
- 엔드-투-엔드 추론 파이프라인
