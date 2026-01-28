# Sprint 7 완료 보고서: iOS 대시보드 UI

## 📋 스프린트 개요

| 항목 | 내용 |
|------|------|
| **스프린트** | Sprint 7 - iOS 대시보드 UI |
| **Phase** | Phase 2 - 모바일/웨어러블 앱 개발 |
| **기간** | 2주 |
| **총 스토리 포인트** | 21 SP |
| **완료 스토리 포인트** | 21 SP |
| **완료율** | 100% |

---

## ✅ 완료된 User Stories

### Story 7.1: 대시보드 메인 화면 (8 SP) ✅

**구현 내용:**
- 수면 요약 카드 (총 수면 시간, 효율성, 취침/기상 시간)
- 수면 단계 타임라인 차트 (Swift Charts)
- 질병 위험 스코어 카드 (상위 3개)
- Pull-to-refresh 기능

**주요 컴포넌트:**
- `SleepSummaryCard` - 어젯밤 수면 요약
- `SleepScoreRing` - 수면 점수 원형 차트
- `SleepStageBarChart` - 수면 단계 막대 차트
- `DiseaseRiskMiniCard` - 질병 위험 미니 카드

**주요 파일:**
- `Views/Components/Cards/DashboardCards.swift`
- `ViewModels/DashboardViewModel.swift`

---

### Story 7.2: 수면 상세 화면 (5 SP) ✅

**구현 내용:**
- 30초 에포크 단위 수면 단계 타임라인 차트
- 각 수면 단계별 지속 시간 및 비율 (파이 차트)
- 수면 효율성 게이지 차트
- 맞춤형 권장사항 메시지

**주요 컴포넌트:**
- `SleepStageChart` - 수면 단계 타임라인 (Area + Line Mark)
- `SleepEfficiencyGauge` - 반원형 효율 게이지
- `SleepStageDetailRow` - 단계별 상세 정보
- `RecommendationRow` - 권장사항 표시

**주요 파일:**
- `Views/Main/SleepDetailView.swift`
- `ViewModels/SleepDetailViewModel.swift`
- `Views/Components/Charts/SleepStageChart.swift`
- `Views/Components/Charts/SleepEfficiencyGauge.swift`

---

### Story 7.3: 질병 위험 분석 화면 (5 SP) ✅

**구현 내용:**
- 5개 질환별 위험 스코어 목록 (파킨슨, 치매, 심근경색, 심부전, 뇌졸중)
- 질환별 상세 화면 (스코어, 카테고리, 트렌드)
- 주간/월간 트렌드 차트
- 질환별 맞춤 권장사항

**주요 컴포넌트:**
- `DiseaseRiskGaugeChart` - 원형 위험도 게이지
- `DiseaseRiskTrendChart` - 트렌드 라인 차트
- `DiseaseRiskCard` - 질환 위험 카드
- `RiskCategoryBadge` - 위험 등급 배지

**주요 파일:**
- `Views/Main/DiseaseRiskView.swift`
- `ViewModels/DiseaseRiskViewModel.swift`
- `Views/Components/Charts/DiseaseRiskChart.swift`

---

### Story 7.4: 히스토리 화면 (3 SP) ✅

**구현 내용:**
- 캘린더 그리드로 수면 점수 표시
- 점수에 따른 색상 구분 (녹색/노란색/빨간색)
- 날짜 탭 시 상세 화면 이동
- 월간/주간 뷰 토글
- 주간/월간 통계 요약

**주요 컴포넌트:**
- `SleepCalendarView` - 월간 캘린더 뷰
- `WeeklyCalendarView` - 주간 캘린더 뷰
- `DayCell` / `WeekDayCell` - 날짜 셀
- `SessionListRow` - 세션 목록 행

**주요 파일:**
- `Views/Main/HistoryCalendarView.swift`
- `ViewModels/HistoryViewModel.swift`
- `Views/Components/Calendar/CalendarView.swift`

---

## 📁 생성된 파일 구조

```
ios/SleepFM/SleepFM/
├── ViewModels/
│   ├── DashboardViewModel.swift      # 대시보드 VM
│   ├── SleepDetailViewModel.swift    # 수면 상세 VM
│   ├── DiseaseRiskViewModel.swift    # 질병 위험 VM
│   └── HistoryViewModel.swift        # 히스토리 VM
├── Views/
│   ├── Main/
│   │   ├── SleepDetailView.swift     # 수면 상세 화면
│   │   ├── DiseaseRiskView.swift     # 질병 위험 화면
│   │   └── HistoryCalendarView.swift # 캘린더 히스토리
│   └── Components/
│       ├── Charts/
│       │   ├── SleepStageChart.swift     # 수면 단계 차트
│       │   ├── SleepEfficiencyGauge.swift # 효율 게이지
│       │   └── DiseaseRiskChart.swift     # 위험도 차트
│       ├── Cards/
│       │   └── DashboardCards.swift       # 대시보드 카드들
│       └── Calendar/
│           └── CalendarView.swift         # 캘린더 컴포넌트
```

---

## 🎨 UI 컴포넌트 라이브러리

### 차트 컴포넌트 (Swift Charts 활용)

| 컴포넌트 | 용도 |
|---------|------|
| `SleepStageChart` | 수면 단계 타임라인 (Area + Line) |
| `SleepStageBarChart` | 수면 단계 요약 막대 |
| `SleepScoreRing` | 수면 점수 원형 프로그레스 |
| `SleepEfficiencyGauge` | 효율성 반원형 게이지 |
| `DiseaseRiskGaugeChart` | 위험도 원형 게이지 |
| `DiseaseRiskTrendChart` | 위험도 트렌드 라인 |
| `DiseaseRiskMiniBar` | 미니 위험도 바 |

### 카드 컴포넌트

| 컴포넌트 | 용도 |
|---------|------|
| `SleepSummaryCard` | 수면 요약 (점수, 시간, 효율) |
| `SleepStagesSummaryCard` | 수면 단계 요약 |
| `DiseaseRiskCard` | 질병 위험 카드 |
| `DiseaseRiskMiniCard` | 미니 질병 위험 카드 |
| `TrendBadge` | 트렌드 방향 배지 |

### 캘린더 컴포넌트

| 컴포넌트 | 용도 |
|---------|------|
| `SleepCalendarView` | 월간 캘린더 |
| `WeeklyCalendarView` | 주간 캘린더 |
| `DayCell` | 월간 날짜 셀 |
| `WeekDayCell` | 주간 날짜 셀 |

---

## 🏗️ 아키텍처

### MVVM 패턴

```
┌───────────────────────────────────────────────────────────┐
│                      View Layer                           │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────┐    │
│  │ Dashboard   │ │ SleepDetail  │ │  DiseaseRisk    │    │
│  │    View     │ │    View      │ │     View        │    │
│  └──────┬──────┘ └──────┬───────┘ └────────┬────────┘    │
└─────────│───────────────│──────────────────│─────────────┘
          │               │                  │
          ▼               ▼                  ▼
┌───────────────────────────────────────────────────────────┐
│                   ViewModel Layer                         │
│  ┌─────────────┐ ┌──────────────┐ ┌─────────────────┐    │
│  │ Dashboard   │ │ SleepDetail  │ │  DiseaseRisk    │    │
│  │  ViewModel  │ │  ViewModel   │ │   ViewModel     │    │
│  └──────┬──────┘ └──────┬───────┘ └────────┬────────┘    │
└─────────│───────────────│──────────────────│─────────────┘
          │               │                  │
          └───────────────┴──────────────────┘
                          │
                          ▼
┌───────────────────────────────────────────────────────────┐
│                    Service Layer                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                    APIService                        │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

### 데이터 흐름

```
API Response → ViewModel (데이터 변환) → Published Properties → View (렌더링)
       ↑                                                              │
       └──────────────────── User Action ────────────────────────────┘
```

---

## 📊 Swift Charts 활용

### 사용된 Mark 타입

- `LineMark` - 트렌드 라인
- `AreaMark` - 영역 채우기
- `PointMark` - 데이터 포인트
- `SectorMark` - 파이 차트
- `RectangleMark` - 위험 영역 표시

### 차트 커스터마이징

```swift
// 수면 단계 타임라인 예시
Chart {
    ForEach(data) { point in
        AreaMark(
            x: .value("Time", point.time),
            y: .value("Stage", point.stageValue)
        )
        .foregroundStyle(stageGradient)
        .interpolationMethod(.stepEnd)
    }
}
.chartYScale(domain: 0...4)
.chartYAxis { ... }
.chartXAxis { ... }
```

---

## 🎨 디자인 시스템 적용

### 색상

- 수면 점수별 색상 구분
- 위험도별 색상 (Low: 녹색, Moderate: 노란색, High: 주황색, Very High: 빨간색)
- 수면 단계별 색상 (Wake: 주황, REM: 보라, N1/N2/N3: 파란색 계열)

### 타이포그래피

- `SleepTypography` 시스템 활용
- 숫자 강조 (`numberLarge`, `headline`)
- 캡션 및 설명 텍스트

### 스페이싱 및 코너

- `SleepSpacing` 일관된 간격
- `SleepCornerRadius` 통일된 모서리

---

## 📝 다음 스프린트 준비사항

### Sprint 8: Android 앱 기반 구조 예고
1. Android 프로젝트 초기 설정 (Kotlin + Jetpack Compose)
2. Android 인증 화면 구현
3. Android HealthConnect 통합
4. Android 네비게이션 구조

---

## ✨ Sprint 7 완료!

iOS 대시보드 UI가 완성되었습니다. Swift Charts를 활용한 풍부한 데이터 시각화와 MVVM 패턴 기반의 깔끔한 아키텍처로 구현되었습니다.
