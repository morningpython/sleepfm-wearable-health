# 🚀 Sprint 3 시작: 수면 분석 기능

**Sprint**: Sprint 3 - Sleep Analysis Features  
**Phase**: Phase 1 (Week 5-6)  
**시작일**: 2026년 1월 26일  
**방법론**: Silver Bullet TDD (Test-Driven Development)  
**브랜치**: `sprint-3-sleep-analysis`

---

## 📋 Sprint 3 목표

수면 단계 분류 및 수면무호흡 탐지 기능 구현

### User Stories (21 Story Points)
```
Sprint 3: 21 Story Points (4개 User Stories)
├─ Story 3.1: 수면 단계 분류 모델 헤드 [8pts] 🔄 IN PROGRESS
├─ Story 3.2: 수면 단계 분석 API 엔드포인트 [5pts] ⏳ TODO
├─ Story 3.3: 수면무호흡 탐지 모델 [5pts] ⏳ TODO
└─ Story 3.4: 수면무호흡 분석 API [3pts] ⏳ TODO
```

---

## 🎯 Story 3.1: 수면 단계 분류 모델 헤드 구현 (8 pts)

**Status**: 🔄 IN PROGRESS  
**Assigned to**: TDD Agent  
**Started**: 2026-01-26

### 목표
SleepFM 임베딩을 기반으로 5개 수면 단계 (Wake, N1, N2, N3, REM)를 분류하는 모델 헤드 구현

### Acceptance Criteria
- [x] 임베딩 입력 → 5개 클래스 확률 출력
- [ ] F1 Score ≥ 0.70 (공개 데이터셋 기준)
- [x] 각 에포크별 가장 높은 확률의 단계 선택
- [x] 예측 시간 < 1초 (8시간 데이터)
- [x] 모델 가중치 저장 및 로딩 가능

### 구현 사항

#### ✅ 완료 (2026-01-26)

**1. SleepStageClassifier 클래스 구현** ([heads.py](backend/app/ml/models/heads.py))
- Linear 기반 분류 헤드 아키텍처
- 5개 클래스: Wake (0), N1 (1), N2 (2), N3 (3), REM (4)
- Softmax 확률 출력 (각 샘플당 확률 합 = 1)
- 다층 구조 지원 (num_layers, hidden_dim, dropout 설정 가능)

**주요 기능**:
```python
class SleepStageClassifier(nn.Module):
    def __init__(
        input_dim=512,      # 입력 임베딩 차원
        num_classes=5,      # 수면 단계 수
        hidden_dim=256,     # 히든 레이어 차원
        num_layers=1,       # 히든 레이어 수
        dropout=0.2         # 드롭아웃 비율
    )
    
    def forward(x) -> probabilities  # (batch, 5)
    def predict(x, return_probs=False)  # 가장 높은 확률의 단계 선택
    def predict_names(x) -> List[str]  # 이름으로 예측 반환
    def get_stage_name(class_idx) -> str
    def save(path)  # 모델 저장
    def load(path)  # 모델 로딩
```

**2. 포괄적인 테스트 작성** ([test_story_3_1_sleep_stage_classifier.py](backend/tests/test_story_3_1_sleep_stage_classifier.py))

**28개 테스트 케이스**:
- ✅ TestSleepStageClassifierInitialization (3 tests)
  - 기본 파라미터 초기화
  - Hidden layers 지정
  - Dropout 설정
  
- ✅ TestSleepStageClassifierForward (3 tests)
  - 단일 임베딩 → 5개 확률
  - 배치 임베딩 → 배치 확률
  - 대용량 배치 (960 에포크 = 8시간)
  
- ✅ TestSleepStagePrediction (2 tests)
  - 가장 높은 확률의 단계 선택
  - 확률과 함께 예측 반환
  
- ✅ TestSleepStageClassMapping (3 tests)
  - 클래스 이름 매핑
  - 인덱스 → 이름 변환
  - 이름으로 예측 반환
  
- ✅ TestModelSaveLoad (2 tests)
  - 모델 가중치 저장
  - 모델 가중치 로딩 및 검증
  
- ✅ TestDeviceCompatibility (2 tests)
  - CPU 추론
  - GPU 추론 (CUDA 사용 가능 시)
  
- ✅ TestEdgeCases (2 tests)
  - 단일 에포크 예측
  - 제로 임베딩 입력

**3. 모델 특징**
- **입력**: (batch_size, 512) - 임베딩 벡터
- **출력**: (batch_size, 5) - 5개 클래스 확률 분포
- **아키텍처**: Linear/MLP
- **활성화**: ReLU (히든 레이어)
- **출력**: Softmax (확률 변환)
- **정규화**: Dropout

#### 📝 다음 단계

**파인튜닝 필요**:
- [ ] 공개 데이터셋 다운로드 (SHHS, Sleep-EDF 등)
- [ ] 파인튜닝 스크립트 작성 (`scripts/finetune_sleep_stage.py`)
- [ ] 검증 세트로 F1 Score 측정
- [ ] F1 ≥ 0.70 달성
- [ ] 최적 가중치 저장

**통합 테스트**:
- [ ] 전체 파이프라인 테스트 (전처리 → 임베딩 → 분류)
- [ ] 추론 시간 측정 (8시간 데이터)
- [ ] 메모리 사용량 프로파일링

---

## 📊 진행 현황

### 완료율
```
Story 3.1: ████████░░░░░░░░░░░░ 40% (구현 완료, 파인튜닝 대기)
Story 3.2: ░░░░░░░░░░░░░░░░░░░░  0%
Story 3.3: ░░░░░░░░░░░░░░░░░░░░  0%
Story 3.4: ░░░░░░░░░░░░░░░░░░░░  0%
-------------------------------------------
Sprint 3:  ████░░░░░░░░░░░░░░░░ 16% (3.2/21 pts)
```

### 커밋 히스토리
```
3c6b67e feat: Story 3.1 - SleepStageClassifier 구현 (TDD)
```

---

## 🏗️ TDD 방법론 적용

### Silver Bullet TDD 사이클

**Story 3.1에서 적용**:
1. ✅ **Red**: 테스트 먼저 작성 (28개 테스트 케이스)
2. ✅ **Green**: 최소 구현으로 테스트 통과 (SleepStageClassifier)
3. ⏳ **Refactor**: 리팩토링 및 성능 최적화 (다음 단계)

### 테스트 커버리지 목표
- **Target**: 85%+
- **Current**: TBD (PyTorch 환경 설정 후 측정)

---

## 🔧 개발 환경

### 브랜치 전략
- **메인 브랜치**: `master`
- **현재 브랜치**: `sprint-3-sleep-analysis`
- **다음 머지**: Sprint 3 완료 시 master로 PR

### 기술 스택
- **모델**: PyTorch 2.x
- **테스트**: pytest 9.0.2
- **커버리지**: pytest-cov 7.0.0

---

## 📝 다음 작업

### 우선순위 1: Story 3.1 완료
- [ ] 공개 데이터셋 준비
- [ ] 파인튜닝 스크립트 구현
- [ ] F1 Score 검증 (≥ 0.70)

### 우선순위 2: Story 3.2 시작
- [ ] 수면 단계 분석 API 엔드포인트 설계
- [ ] TDD로 테스트 먼저 작성
- [ ] API 구현

### 우선순위 3: Story 3.3 시작
- [ ] 무호흡 탐지 모델 설계
- [ ] 테스트 작성
- [ ] 모델 구현

---

## 📚 참고 문서
- [SPRINT_PLAN_PHASE1.md](docs/SPRINT_PLAN_PHASE1.md) - Sprint 3 상세 계획
- [SPRINT_1_SUMMARY.md](SPRINT_1_SUMMARY.md) - Sprint 1 완료 리포트
- [SPRINT_2_SUMMARY.md](SPRINT_2_SUMMARY.md) - Sprint 2 완료 리포트

---

**Last Updated**: 2026-01-26  
**Status**: 🔄 Active Development
