# Story 2.1: SleepFM 모델 로딩 및 초기화

**상태**: ✅ 완료  
**점수**: 5점  
**검증**: 6/6 통과

---

## 개요

PyTorch 기반 SleepFM 파운데이션 모델 구현 및 로딩 시스템 개발.

**핵심 기능**:
- ✅ SleepFM 인코더 구현 (CNN 토크나이저 + Transformer + Attention Pooling)
- ✅ 모델 가중치 HuggingFace에서 자동 다운로드
- ✅ GPU/CPU 자동 감지 및 배치
- ✅ 입출력 검증 (형상 및 데이터 타입)
- ✅ 싱글톤 패턴으로 모델 인스턴스 캐싱

---

## Acceptance Criteria

| AC | 상태 | 설명 |
|---|---|---|
| AC 2.1.1 | ✅ | SleepFM 아키텍처 구현 (CNN + Transformer) |
| AC 2.1.2 | ✅ | 모델 가중치 로딩 (HuggingFace) |
| AC 2.1.3 | ✅ | GPU/CPU 자동 감지 |
| AC 2.1.4 | ✅ | 모델 검증 (shape: (batch, 3, 640) → (batch, 512)) |
| AC 2.1.5 | ✅ | 메모리 최적화 (eval 모드, no_grad) |

---

## 구현 상세

### 1. SleepFMEncoder 클래스 (sleepfm_encoder.py)

**아키텍처**:
```
입력: (batch, 3, 640)
  ↓
[CNN 토크나이저]
  Conv1d(3, 64, kernel_size=5) + ReLU
  Conv1d(64, 128, kernel_size=5) + ReLU
  Conv1d(128, 512, kernel_size=5) + ReLU
  → (batch, 512, 620)
  ↓
[Transformer 인코더]
  4개 Transformer 인코더 레이어 (8개 헤드)
  → (batch, 512, 620)
  ↓
[Attention Pooling]
  시간 차원 가중치 계산 및 풀링
  → (batch, 512)
```

**AttentionPooling**:
- 가중치: (batch, time_steps, 1)
- 소프트맥스 정규화
- 가중 평균: 시간 차원 축소

### 2. 모델 로딩 시스템

**load_sleepfm_model()**:
```python
model, device = load_sleepfm_model(
    model_name="sleepfm-emb",
    download_dir="~/.cache/sleepfm",
)

# 자동 처리:
# 1. HuggingFace에서 가중치 다운로드
# 2. GPU/CPU 자동 감지
# 3. 평가 모드 설정
# 4. 가중치 검증
```

### 3. ModelManager 싱글톤

**특징**:
- 프로세스당 단 1개 모델 인스턴스 (메모리 효율)
- LRU 캐싱으로 반복 접근 최적화
- 상태 추적: 초기화 여부, 모델 준비 상태

```python
manager = get_model_manager()
manager.initialize()
model = manager.model
device = manager.device
```

---

## 테스트 커버리지

**파일**: `backend/tests/test_story_2_1_sleepfm_loading.py`  
**테스트**: 13개

### 테스트 목록

1. **TestSleepFMEncoder** (6개)
   - 모델 구성 요소 검증
   - Forward pass
   - 출력 shape 검증
   - 입력 검증

2. **TestModelLoading** (3개)
   - 모델 로드 성공
   - GPU/CPU 지원
   - 가중치 검증

3. **TestModelValidation** (3개)
   - 입출력 shape
   - 데이터 타입
   - 수치 안정성

4. **TestGPUMemory** (1개)
   - 메모리 사용량

---

## 검증 결과

```
[1] SleepFMEncoder 클래스 검증...
    ✓ SleepFMEncoder 클래스 완성
[2] 모델 로딩 함수 검증...
    ✓ load_sleepfm_model() 함수 완성
[3] ModelManager 싱글톤 검증...
    ✓ ModelManager 싱글톤 완성
[4] 모델 가중치 검증...
    ✓ HuggingFace 통합 완성
[5] 검증 함수 검증...
    ✓ 입출력 검증 함수 완성
[6] 테스트 파일 검증...
    ✓ 13개 테스트 완성

검증 결과: 6/6 통과
============================================================

✅ Story 2.1 모든 검증 완료!
```

---

## 코드 통계

| 지표 | 값 |
|---|---|
| sleepfm_encoder.py | 400+ 라인 |
| model_manager.py | 100+ 라인 |
| test_story_2_1_sleepfm_loading.py | 300+ 라인 |
| 클래스 | 3개 |
| 함수 | 5개 |
| 테스트 | 13개 |

---

## 설정

```python
SLEEPFM_CONFIG = {
    "model_name": "sleepfm-emb",
    "input_channels": 3,
    "embedding_dim": 512,
    "kernel_size": 5,
    "num_layers": 4,
    "num_heads": 8,
}
```

---

## 파일 목록

- `backend/app/ml/sleepfm_encoder.py`
- `backend/app/ml/model_manager.py`
- `backend/tests/test_story_2_1_sleepfm_loading.py`
- `backend/scripts/init_sleepfm_model.py`
- `backend/scripts/verify_story_2_1.py`

---

## 다음 스토리: Story 2.2

Story 2.2: 신호 전처리 파이프라인 (8점)
- 리샘플링, 필터링, 토큰화, 정규화 구현
- 6단계 전처리 파이프라인 통합
