# Sprint 4 Summary: 질병 위험 예측 API

## 스프린트 개요

- **기간**: Sprint 4
- **목표**: 질병 위험 예측 API 구현
- **총 Story Points**: 21 SP
- **상태**: ✅ 완료

## User Stories 완료 현황

### Story 4.1: 질병 위험 예측 모델 (8 SP) ✅

CoxPH(Cox Proportional Hazards) 기반 5개 질환 위험 예측 모델 구현

**구현 내용:**
- `DiseaseRiskPredictor`: 5개 질환에 대한 통합 예측 모델
- `CoxPHHead`: 개별 질환별 Cox 비례 위험 모델 헤드
- Monte Carlo Dropout 기반 불확실성 추정 (95% 신뢰 구간)
- 위험 스코어 카테고리화: Low (<30), Medium (30-60), High (>60)

**대상 질환:**
| 영문명 | 한글명 |
|--------|--------|
| parkinsons | 파킨슨병 |
| dementia | 치매 |
| myocardial_infarction | 심근경색 |
| heart_failure | 심부전 |
| stroke | 뇌졸중 |

**주요 파일:**
- [app/ml/models/disease_risk.py](backend/app/ml/models/disease_risk.py)
- [app/ml/analysis/disease_risk_analyzer.py](backend/app/ml/analysis/disease_risk_analyzer.py)

---

### Story 4.2: 질병 위험 예측 API 엔드포인트 (5 SP) ✅

질병 위험 예측 REST API 엔드포인트 구현

**엔드포인트:**
```
POST /api/v1/analyze/disease-risk
```

**요청:**
```json
{
  "session_id": 1
}
```

**응답:**
```json
{
  "analysis_id": 1,
  "session_id": 1,
  "predictions": [
    {
      "disease": "parkinsons",
      "disease_name_ko": "파킨슨병",
      "risk_score": 45.2,
      "category": "Medium",
      "confidence_interval": {
        "lower": 35.1,
        "upper": 55.3
      },
      "recommendations": null
    },
    {
      "disease": "dementia",
      "disease_name_ko": "치매",
      "risk_score": 72.5,
      "category": "High",
      "confidence_interval": {
        "lower": 65.0,
        "upper": 80.0
      },
      "recommendations": [
        "전문의 상담을 즉시 권장합니다.",
        "인지 기능 검사를 정기적으로 받으세요.",
        "..."
      ]
    }
  ],
  "created_at": "2026-01-25T10:00:00Z"
}
```

**주요 파일:**
- [app/routes/analysis.py](backend/app/routes/analysis.py) (disease-risk 엔드포인트)
- [app/schemas/disease_risk.py](backend/app/schemas/disease_risk.py)

---

### Story 4.3: 통합 분석 API (5 SP) ✅

모든 분석을 한 번에 수행하는 통합 API 구현

**엔드포인트:**
```
POST /api/v1/analyze
GET /api/v1/analyze/{session_id}/status
```

**통합 분석 요청:**
```json
{
  "session_id": 1,
  "analysis_types": ["sleep_stages", "apnea", "disease_risk"]  // optional
}
```

**통합 분석 응답:**
```json
{
  "session_id": 1,
  "analysis_status": "completed",
  "created_at": "2026-01-25T10:00:00Z",
  "sleep_summary": {
    "total_time_minutes": 480,
    "total_sleep_time_minutes": 420,
    "sleep_efficiency": 87.5,
    "sleep_onset_latency": 15.0,
    "wake_after_sleep_onset": 30.0
  },
  "sleep_stages": {
    "stages": [...],
    "stage_durations": {
      "Wake": 60.0,
      "N1": 45.0,
      "N2": 200.0,
      "N3": 80.0,
      "REM": 95.0
    }
  },
  "apnea": {
    "ahi": 5.2,
    "severity": "Mild",
    "event_count": 42,
    "recommendations": [...]
  },
  "disease_risk": {
    "predictions": [...]
  }
}
```

**분석 상태 응답:**
```json
{
  "session_id": 1,
  "status": "completed",
  "completed_analyses": ["sleep_stage", "apnea", "disease_risk"]
}
```

---

### Story 4.4: 분석 히스토리 및 결과 조회 (3 SP) ✅

사용자의 수면 세션 및 분석 결과 히스토리 조회 API

**엔드포인트:**
```
GET /api/v1/users/{user_id}/sessions
GET /api/v1/sessions/{session_id}/results
```

**세션 목록 조회:**
```
GET /api/v1/users/1/sessions?limit=10&offset=0&start_date=2026-01-01&end_date=2026-01-31
```

**세션 결과 조회:**
```json
{
  "session_id": 1,
  "session_date": "2026-01-25T22:00:00Z",
  "duration_hours": 8,
  "analysis_status": "completed",
  "analyses": [
    {
      "id": 1,
      "type": "sleep_stage",
      "result": {...},
      "created_at": "2026-01-26T06:00:00Z"
    },
    {
      "id": 2,
      "type": "apnea",
      "result": {...},
      "created_at": "2026-01-26T06:01:00Z"
    },
    {
      "id": 3,
      "type": "disease_risk",
      "result": {...},
      "created_at": "2026-01-26T06:02:00Z"
    }
  ]
}
```

**주요 파일:**
- [app/routes/history.py](backend/app/routes/history.py)

---

## 테스트 결과

```
tests/test_story_4_1_disease_risk_model.py    - 19 passed
tests/test_story_4_2_disease_risk_api.py      - 13 passed
tests/test_story_4_3_integrated_analysis_api.py - 20 passed
tests/test_story_4_4_analysis_history.py      - 19 passed
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sprint 4 Total: 71 tests passed
Overall: 391 tests passed, 7 skipped
Coverage: 90%
```

---

## 성능 요구사항 충족

| API | 요구사항 | 결과 |
|-----|----------|------|
| POST /api/v1/analyze/disease-risk | < 4초 | ✅ 통과 |
| POST /api/v1/analyze (통합) | < 15초 | ✅ 통과 |
| GET /api/v1/users/{id}/sessions | < 500ms | ✅ 통과 |
| GET /api/v1/sessions/{id}/results | < 500ms | ✅ 통과 |

---

## 파일 변경 내역

### 신규 파일
- `backend/app/ml/models/disease_risk.py` - 질병 위험 예측 모델
- `backend/app/ml/analysis/disease_risk_analyzer.py` - 분석기
- `backend/app/routes/history.py` - 히스토리 API
- `backend/app/schemas/disease_risk.py` - Pydantic 스키마
- `backend/tests/test_story_4_*.py` - 테스트 파일들 (4개)

### 수정 파일
- `backend/app/main.py` - 라우터 등록
- `backend/app/ml/models/__init__.py` - export 추가
- `backend/app/ml/analysis/__init__.py` - export 추가
- `backend/app/routes/analysis.py` - 통합 분석 엔드포인트 추가

---

## TDD 방법론 준수

### Red Phase (테스트 작성)
- 4개 User Story에 대한 71개 테스트 먼저 작성
- 모든 테스트 실패 확인 (ModuleNotFoundError)

### Green Phase (구현)
- 테스트를 통과하기 위한 최소 구현
- Story 4.1 → 4.2 → 4.3 → 4.4 순차 구현

### Refactor Phase
- 신뢰구간 계산 버그 수정
- Pydantic .dict() → .model_dump() 호환성 개선

---

## 다음 스프린트 준비

Sprint 5 (Phase 2)로 이동할 준비 완료:
- 프론트엔드 웹 대시보드 개발
- 사용자 인터페이스 구현
- 시각화 차트 컴포넌트
