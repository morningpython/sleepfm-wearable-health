# Sprint Plan - Phase 2
## 모바일/웨어러블 앱 개발 (Sprint 5-9)

**문서 버전:** 1.0  
**작성일:** 2026년 1월 8일  
**Phase 기간:** 10주 (Sprint 5-9)  
**Phase 목표:** iOS/watchOS 및 Android/Wear OS 네이티브 앱 개발

---

## 목차
1. [Phase 2 개요](#phase-2-개요)
2. [Epic 정의](#epic-정의)
3. [Sprint 5: iOS 앱 기반 구조](#sprint-5-ios-앱-기반-구조)
4. [Sprint 6: watchOS 센서 수집](#sprint-6-watchos-센서-수집)
5. [Sprint 7: iOS 대시보드 UI](#sprint-7-ios-대시보드-ui)
6. [Sprint 8: Android 앱 기반 구조](#sprint-8-android-앱-기반-구조)
7. [Sprint 9: Wear OS 및 통합](#sprint-9-wear-os-및-통합)
8. [Phase 2 완료 기준](#phase-2-완료-기준)

---

## Phase 2 개요

### 목표
사용자가 웨어러블 기기에서 데이터를 수집하고, 모바일 앱에서 분석 결과를 확인할 수 있는 네이티브 앱 개발

### 주요 결과물
- ✅ iOS 모바일 앱 (iPhone)
- ✅ watchOS 앱 (Apple Watch)
- ✅ Android 모바일 앱 (Android Phone)
- ✅ Wear OS 앱 (Samsung Galaxy Watch)
- ✅ HealthKit/Samsung Health 통합
- ✅ 건강 대시보드 UI
- ✅ 데이터 동기화 시스템

### 팀 구성
- **iOS Lead**: 1명
- **Android Lead**: 1명
- **UI/UX Designer**: 1명
- **Backend Support**: 0.5명 (파트타임)

### UI/UX 중심 개발 전략
- **Figma 디자인 우선**: 모든 화면을 Figma에서 먼저 디자인
- **컴포넌트 기반**: 재사용 가능한 UI 컴포넌트 라이브러리 구축
- **점진적 구현**: 화면별로 순차적 개발 및 테스트

---

## Epic 정의

### Epic 6: iOS 앱 개발
**설명**: iPhone용 건강 대시보드 및 데이터 관리 앱  
**비즈니스 가치**: iOS 사용자에게 수면 분석 서비스 제공  
**완료 조건**:
- SwiftUI 기반 앱 실행 가능
- HealthKit 데이터 읽기/쓰기
- API 서버 연동
- 건강 대시보드 UI 완성

---

### Epic 7: watchOS 앱 개발
**설명**: Apple Watch용 센서 데이터 수집 앱  
**비즈니스 가치**: 자동 수면 데이터 수집으로 사용자 편의성 향상  
**완료 조건**:
- 수면 중 센서 데이터 자동 수집
- iPhone 앱과 데이터 동기화
- 배터리 효율적 백그라운드 수집
- 실시간 건강 알림

---

### Epic 8: Android 앱 개발
**설명**: Android용 건강 대시보드 및 데이터 관리 앱  
**비즈니스 가치**: Android 사용자에게 수면 분석 서비스 제공  
**완료 조건**:
- Jetpack Compose 기반 앱 실행
- Samsung Health SDK 통합
- API 서버 연동
- 건강 대시보드 UI 완성 (iOS와 동일)

---

### Epic 9: Wear OS 앱 개발
**설명**: Samsung Galaxy Watch용 센서 데이터 수집 앱  
**비즈니스 가치**: Android 사용자도 자동 수면 데이터 수집 가능  
**완료 조건**:
- 수면 중 센서 데이터 자동 수집
- Android 앱과 데이터 동기화
- 배터리 효율적 백그라운드 수집

---

### Epic 10: 크로스 플랫폼 통합
**설명**: 공통 UI/UX 패턴 및 데이터 동기화 메커니즘  
**비즈니스 가치**: 일관된 사용자 경험 및 효율적 개발  
**완료 조건**:
- iOS/Android 동일한 화면 구성
- 동일한 API 응답 처리 로직
- 공통 디자인 시스템

---

## Sprint 5: iOS 앱 기반 구조
**기간**: 2주 (Week 9-10)  
**Sprint 목표**: iOS 앱 프로젝트 설정 및 기본 인증/네비게이션 구조 구축  
**총 Story Points**: 21

---

### 📱 User Story 5.1: iOS 프로젝트 초기 설정
**Epic**: Epic 6 - iOS 앱 개발  
**Story Points**: 3

**As a** iOS Developer  
**I want to** Xcode 프로젝트를 초기 설정  
**So that** 팀이 iOS 앱 개발을 시작할 수 있다

**Description**:
- Xcode 프로젝트 생성 (iOS 17.0+)
- SwiftUI 기반 앱 구조
- Swift Package Manager 의존성 관리
- SwiftLint 설정
- 프로젝트 구조 정의 (MVVM 아키텍처)

**Acceptance Criteria**:
- [ ] Xcode 프로젝트가 시뮬레이터에서 실행됨
- [ ] SwiftUI ContentView 표시
- [ ] 폴더 구조: Views/, Models/, ViewModels/, Services/, Utils/
- [ ] SwiftLint 규칙 적용
- [ ] .gitignore 설정 완료

**Tasks**:
- [ ] Xcode 프로젝트 생성 (Bundle ID: com.sleepfm.app)
- [ ] SwiftUI 앱 템플릿 설정
- [ ] 폴더 구조 생성
- [ ] SwiftLint 설정 파일 추가
- [ ] SPM 패키지 추가 (Alamofire, KeychainAccess 등)

**Testing**:
- Unit Test: N/A
- Component Test: N/A
- E2E Test: 앱 실행 및 기본 화면 표시 확인

---

### 📱 User Story 5.2: Figma 디자인 시스템 정의
**Epic**: Epic 10 - 크로스 플랫폼 통합  
**Story Points**: 5

**As a** UI/UX Designer  
**I want to** Figma에서 디자인 시스템을 정의  
**So that** 일관된 UI를 iOS/Android에 적용할 수 있다

**Description**:
- 컬러 팔레트 정의
- 타이포그래피 스타일 가이드
- 아이콘 세트
- 공통 컴포넌트 (버튼, 카드, 차트 등)
- 화면별 와이어프레임 (온보딩, 로그인, 대시보드)

**Acceptance Criteria**:
- [ ] Figma 파일 생성 및 팀 공유
- [ ] 컬러 시스템 정의 (Primary, Secondary, Background 등)
- [ ] 5개 화면 와이어프레임 완성 (온보딩, 로그인, 대시보드, 상세, 설정)
- [ ] 재사용 가능한 컴포넌트 20개 이상
- [ ] iOS/Android 개발자가 Figma에서 디자인 스펙 추출 가능

**Tasks**:
- [ ] Figma 프로젝트 생성
- [ ] 컬러 변수 정의 (Light/Dark 모드)
- [ ] 타이포그래피 스타일 정의
- [ ] 아이콘 라이브러리 구축 (SF Symbols, Material Icons)
- [ ] 주요 화면 와이어프레임 디자인
- [ ] 인터랙션 프로토타입 작성

**Testing**:
- Unit Test: N/A
- Component Test: N/A
- E2E Test: 개발자가 Figma 스펙으로 UI 구현 가능 여부 확인

---

### 📱 User Story 5.3: iOS 인증 화면 구현
**Epic**: Epic 6 - iOS 앱 개발  
**Story Points**: 5

**As a** App User  
**I want to** 앱에서 회원가입/로그인  
**So that** 내 건강 데이터를 안전하게 관리할 수 있다

**Description**:
- 온보딩 화면 (3개 페이지)
- 회원가입 화면 (이메일, 비밀번호, 프로필)
- 로그인 화면
- Apple Sign-In 통합
- JWT 토큰 Keychain 저장

**Acceptance Criteria**:
- [ ] 온보딩 화면 스와이프 가능
- [ ] 회원가입 폼 검증 (이메일 형식, 비밀번호 강도)
- [ ] 로그인 성공 시 토큰 저장 및 대시보드 이동
- [ ] Apple Sign-In 버튼 동작
- [ ] 로그인 상태 유지 (앱 재시작 시)

**Tasks**:
- [ ] OnboardingView 구현 (SwiftUI TabView)
- [ ] SignUpView 구현 (Form, TextField, SecureField)
- [ ] LoginView 구현
- [ ] AuthService 클래스 작성 (API 연동)
- [ ] Apple Sign-In 설정 (Capability, AuthenticationServices)
- [ ] KeychainService 유틸리티 작성
- [ ] 입력 검증 로직 (ViewModel)

**Testing**:
- Unit Test: 이메일/비밀번호 검증 로직
- Component Test: AuthService API 호출 (mock)
- E2E Test: 회원가입 → 로그인 → 토큰 저장 확인

---

### 📱 User Story 5.4: iOS 네비게이션 구조
**Epic**: Epic 6 - iOS 앱 개발  
**Story Points**: 3

**As a** App User  
**I want to** 앱 내에서 쉽게 화면을 이동  
**So that** 원하는 정보에 빠르게 접근할 수 있다

**Description**:
- TabView 기반 메인 네비게이션 (대시보드, 히스토리, 설정)
- NavigationStack 기반 화면 전환
- 로그인 상태에 따른 라우팅

**Acceptance Criteria**:
- [ ] 하단 탭바 3개 (Home, History, Settings)
- [ ] 각 탭 아이콘 및 레이블 표시
- [ ] 탭 전환 애니메이션 부드러움
- [ ] 미로그인 시 로그인 화면으로 리다이렉트
- [ ] 뒤로가기 네비게이션 동작

**Tasks**:
- [ ] MainTabView 구현 (TabView)
- [ ] DashboardView, HistoryView, SettingsView 스켈레톤 생성
- [ ] NavigationStack 설정
- [ ] 인증 상태 체크 로직 (@EnvironmentObject)
- [ ] 탭 아이콘 추가

**Testing**:
- Unit Test: N/A
- Component Test: 탭 전환 동작 확인
- E2E Test: 로그인 → 탭 네비게이션 → 로그아웃 → 로그인 화면 이동

---

### 📱 User Story 5.5: HealthKit 권한 요청 및 데이터 읽기
**Epic**: Epic 6 - iOS 앱 개발  
**Story Points**: 5

**As a** App User  
**I want to** HealthKit 권한을 허용  
**So that** 앱이 내 수면 데이터를 읽을 수 있다

**Description**:
- HealthKit Capability 추가
- 권한 요청 화면 (수면 분석, 심박수, 호흡률)
- HKHealthStore를 통한 데이터 읽기
- 최근 수면 세션 조회

**Acceptance Criteria**:
- [ ] HealthKit 권한 요청 다이얼로그 표시
- [ ] 수면, 심박수, 호흡률 권한 요청
- [ ] 권한 승인 후 최근 수면 데이터 읽기 성공
- [ ] 권한 거부 시 적절한 안내 메시지
- [ ] 데이터 읽기 에러 핸들링

**Tasks**:
- [ ] HealthKit Capability 추가
- [ ] Info.plist에 권한 설명 추가
- [ ] HealthKitService 클래스 작성
- [ ] 권한 요청 함수 구현 (requestAuthorization)
- [ ] 수면 데이터 쿼리 함수 (HKSampleQuery)
- [ ] 심박수, 호흡률 쿼리 함수
- [ ] 에러 처리 (권한 거부, 데이터 없음 등)

**Testing**:
- Unit Test: N/A (HealthKit은 실제 기기 필요)
- Component Test: Mock HealthKitService로 데이터 읽기 테스트
- E2E Test: 실제 기기에서 권한 요청 → 데이터 읽기 확인

---

### Sprint 5 완료 기준
- [ ] iOS 앱이 시뮬레이터/실제 기기에서 실행됨
- [ ] Figma 디자인 시스템 완성
- [ ] 로그인/회원가입 동작
- [ ] HealthKit 권한 요청 및 데이터 읽기 가능
- [ ] 코드 리뷰 완료
- [ ] 단위 테스트 커버리지 ≥ 60%

---

## Sprint 6: watchOS 센서 수집
**기간**: 2주 (Week 11-12)  
**Sprint 목표**: Apple Watch 센서 데이터 자동 수집 및 iPhone 동기화  
**총 Story Points**: 21

---

### ⌚ User Story 6.1: watchOS 프로젝트 설정
**Epic**: Epic 7 - watchOS 앱 개발  
**Story Points**: 3

**As a** iOS Developer  
**I want to** watchOS 타겟을 추가  
**So that** Apple Watch 앱을 개발할 수 있다

**Description**:
- Xcode에서 watchOS 타겟 추가
- Watch App Extension 설정
- iPhone 앱과 App Group 공유 설정
- Watch Connectivity 프레임워크 추가

**Acceptance Criteria**:
- [ ] watchOS 타겟 빌드 성공
- [ ] Watch 시뮬레이터에서 앱 실행
- [ ] App Group 설정 완료 (group.com.sleepfm.shared)
- [ ] iPhone-Watch 페어링 시뮬레이션 가능

**Tasks**:
- [ ] Xcode에서 Watch App 타겟 추가
- [ ] App Group Capability 추가
- [ ] Watch Connectivity 프레임워크 임포트
- [ ] 기본 WatchApp View 생성

**Testing**:
- Unit Test: N/A
- Component Test: N/A
- E2E Test: Watch 앱 실행 확인

---

### ⌚ User Story 6.2: Watch 센서 데이터 수집
**Epic**: Epic 7 - watchOS 앱 개발  
**Story Points**: 8

**As a** Watch App  
**I want to** 수면 중 센서 데이터를 자동 수집  
**So that** 사용자의 수면 품질을 분석할 수 있다

**Description**:
- HealthKit WorkoutSession 사용하여 백그라운드 수집
- 심박수, 호흡률, 가속도 데이터 수집
- 1Hz 빈도로 샘플링
- 로컬 SQLite에 임시 저장
- 수면 감지 자동 시작

**Acceptance Criteria**:
- [ ] 수면 감지 시 센서 수집 자동 시작
- [ ] 심박수, 호흡률, 가속도 1초마다 기록
- [ ] 데이터가 로컬 DB에 저장됨
- [ ] 수면 종료 시 수집 자동 중지
- [ ] 배터리 소모 < 15% (8시간 기준)

**Tasks**:
- [ ] SensorCollectionService 클래스 작성
- [ ] HealthKit 실시간 쿼리 설정 (HKAnchoredObjectQuery)
- [ ] 수면 상태 감지 로직 (HKCategoryType.sleepAnalysis)
- [ ] SQLite 로컬 DB 설정 (GRDB 또는 Core Data)
- [ ] 백그라운드 작업 스케줄링
- [ ] 배터리 최적화 (샘플링 레이트 동적 조정)

**Testing**:
- Unit Test: 센서 데이터 파싱 로직
- Component Test: Mock 센서 데이터 저장 확인
- E2E Test: 실제 Watch에서 수면 중 데이터 수집 확인

---

### ⌚ User Story 6.3: Watch-iPhone 데이터 동기화
**Epic**: Epic 7 - watchOS 앱 개발  
**Story Points**: 5

**As a** Watch App  
**I want to** 수집한 센서 데이터를 iPhone으로 전송  
**So that** iPhone 앱에서 서버에 업로드할 수 있다

**Description**:
- Watch Connectivity를 사용한 데이터 전송
- 백그라운드 전송 지원
- 전송 실패 시 재시도 로직
- 전송 완료 후 로컬 데이터 삭제

**Acceptance Criteria**:
- [ ] 수면 종료 후 자동으로 iPhone에 데이터 전송
- [ ] 전송 중 진행률 표시
- [ ] 전송 실패 시 3회 재시도
- [ ] iPhone 앱 미실행 시 백그라운드 전송
- [ ] 전송 완료 후 Watch 로컬 DB에서 데이터 삭제

**Tasks**:
- [ ] WCSession 설정 (Watch, iPhone 양쪽)
- [ ] 데이터 전송 함수 구현 (transferUserInfo)
- [ ] iPhone 앱에서 데이터 수신 핸들러
- [ ] 재시도 로직 구현
- [ ] 전송 상태 UI 표시

**Testing**:
- Unit Test: 데이터 직렬화/역직렬화
- Component Test: Mock WCSession으로 전송 테스트
- E2E Test: Watch → iPhone 데이터 전송 확인

---

### ⌚ User Story 6.4: Watch 실시간 알림
**Epic**: Epic 7 - watchOS 앱 개발  
**Story Points**: 3

**As a** Watch User  
**I want to** 건강 이상 징후 발생 시 알림 받기  
**So that** 즉시 대응할 수 있다

**Description**:
- 비정상 심박수 패턴 감지
- 장시간 무호흡 의심 감지
- 햅틱 알림 및 화면 표시

**Acceptance Criteria**:
- [ ] 심박수 < 40 또는 > 120 시 알림
- [ ] 호흡률 비정상 패턴 감지 시 알림
- [ ] 햅틱 피드백 제공
- [ ] 알림 화면에 간단한 안내 메시지
- [ ] 알림 히스토리 저장

**Tasks**:
- [ ] 이상 징후 감지 알고리즘 구현
- [ ] UNUserNotificationCenter를 통한 알림
- [ ] 햅틱 피드백 (WKInterfaceDevice.current().play)
- [ ] 알림 화면 UI 디자인

**Testing**:
- Unit Test: 이상 징후 감지 로직
- Component Test: 알림 발송 확인
- E2E Test: 실제 Watch에서 알림 수신 확인

---

### ⌚ User Story 6.5: Watch Complication
**Epic**: Epic 7 - watchOS 앱 개발  
**Story Points**: 2

**As a** Watch User  
**I want to** 워치페이스에 수면 점수를 표시  
**So that** 한눈에 건강 상태를 확인할 수 있다

**Description**:
- Complication 타임라인 제공
- 전날 밤 수면 점수 표시
- 다양한 Complication Family 지원

**Acceptance Criteria**:
- [ ] Complication이 워치페이스에 추가 가능
- [ ] 전날 밤 수면 점수 표시 (0-100)
- [ ] Circular, Rectangular Family 지원
- [ ] 탭 시 앱 실행

**Tasks**:
- [ ] ComplicationController 구현
- [ ] 타임라인 엔트리 생성
- [ ] Complication 템플릿 디자인
- [ ] 데이터 업데이트 로직

**Testing**:
- Unit Test: 타임라인 생성 로직
- Component Test: Complication 표시 확인
- E2E Test: 워치페이스에서 Complication 동작 확인

---

### Sprint 6 완료 기준
- [ ] Watch 앱에서 센서 데이터 수집 성공
- [ ] iPhone으로 데이터 동기화 확인
- [ ] 실시간 알림 동작
- [ ] Complication 표시
- [ ] 실제 기기 테스트 완료

---

## Sprint 7: iOS 대시보드 UI
**기간**: 2주 (Week 13-14)  
**Sprint 목표**: 건강 대시보드 및 수면 분석 결과 시각화  
**총 Story Points**: 21

---

### 📱 User Story 7.1: 대시보드 메인 화면
**Epic**: Epic 6 - iOS 앱 개발  
**Story Points**: 8

**As a** App User  
**I want to** 오늘의 수면 요약을 한눈에 확인  
**So that** 내 수면 품질을 빠르게 파악할 수 있다

**Description**:
- 오늘의 수면 요약 카드 (총 수면 시간, 효율성)
- 수면 단계 타임라인 차트
- 질병 위험 스코어 카드 (상위 3개)
- 새로고침 기능

**Acceptance Criteria**:
- [ ] 수면 요약 카드에 총 시간, 효율성 표시
- [ ] 수면 단계 막대 차트 (시간축)
- [ ] 질병 위험 스코어 카드 색상 구분 (Low/Medium/High)
- [ ] Pull-to-refresh 동작
- [ ] 로딩 상태 표시

**Tasks**:
- [ ] DashboardView UI 구현 (Figma 디자인 기반)
- [ ] SleepSummaryCard 컴포넌트
- [ ] SleepStageChart 컴포넌트 (Swift Charts)
- [ ] DiseaseRiskCard 컴포넌트
- [ ] DashboardViewModel 작성 (API 호출)
- [ ] 새로고침 로직

**Testing**:
- Unit Test: ViewModel 데이터 변환 로직
- Component Test: 각 카드 컴포넌트 렌더링
- E2E Test: API 호출 → 대시보드 표시 확인

---

### 📱 User Story 7.2: 수면 상세 화면
**Epic**: Epic 6 - iOS 앱 개발  
**Story Points**: 5

**As a** App User  
**I want to** 수면 분석 결과를 상세히 확인  
**So that** 내 수면 패턴을 깊이 이해할 수 있다

**Description**:
- 에포크별 수면 단계 상세 차트
- 각 수면 단계별 지속 시간 및 비율
- 수면 효율성 설명
- 권장사항 메시지

**Acceptance Criteria**:
- [ ] 대시보드에서 탭 시 상세 화면 이동
- [ ] 30초 에포크 단위 수면 단계 차트
- [ ] 각 단계별 시간 및 퍼센트 표시
- [ ] 수면 효율성 게이지 차트
- [ ] 개인화된 권장사항 텍스트

**Tasks**:
- [ ] SleepDetailView 구현
- [ ] DetailedSleepChart 컴포넌트 (선 그래프)
- [ ] SleepStageBreakdown 컴포넌트 (파이 차트)
- [ ] EfficiencyGauge 컴포넌트
- [ ] 권장사항 로직 구현

**Testing**:
- Unit Test: 권장사항 생성 로직
- Component Test: 차트 렌더링
- E2E Test: 대시보드 → 상세 화면 네비게이션

---

### 📱 User Story 7.3: 질병 위험 분석 화면
**Epic**: Epic 6 - iOS 앱 개발  
**Story Points**: 5

**As a** App User  
**I want to** 질병 위험 스코어를 상세히 확인  
**So that** 건강 위험을 인지하고 조치를 취할 수 있다

**Description**:
- 5개 질환별 위험 스코어 목록
- 각 질환별 상세 화면 (스코어, 카테고리, 신뢰 구간)
- 트렌드 차트 (주간/월간)
- 권장사항 및 대응 방법

**Acceptance Criteria**:
- [ ] 질환 목록 카드 표시 (파킨슨, 치매, 심근경색, 심부전, 뇌졸중)
- [ ] 각 카드에 스코어 및 색상 구분
- [ ] 카드 탭 시 상세 화면 이동
- [ ] 상세 화면에 트렌드 차트 표시
- [ ] 고위험 시 경고 메시지

**Tasks**:
- [ ] DiseaseRiskListView 구현
- [ ] DiseaseRiskCard 컴포넌트
- [ ] DiseaseRiskDetailView 구현
- [ ] TrendChart 컴포넌트 (선 그래프)
- [ ] 권장사항 및 경고 메시지 로직

**Testing**:
- Unit Test: 위험도 분류 로직
- Component Test: 카드 및 차트 렌더링
- E2E Test: 목록 → 상세 화면 네비게이션

---

### 📱 User Story 7.4: 히스토리 화면
**Epic**: Epic 6 - iOS 앱 개발  
**Story Points**: 3

**As a** App User  
**I want to** 과거 수면 기록을 확인  
**So that** 장기 트렌드를 파악할 수 있다

**Description**:
- 캘린더 뷰로 수면 기록 표시
- 날짜별 수면 점수 색상 구분
- 특정 날짜 탭 시 해당 날짜 분석 결과 표시
- 월간/주간 뷰 전환

**Acceptance Criteria**:
- [ ] 캘린더 그리드에 수면 점수 표시
- [ ] 점수에 따른 색상 구분 (녹색/노란색/빨간색)
- [ ] 날짜 탭 시 해당 날짜 상세 화면 이동
- [ ] 월간/주간 뷰 토글 버튼
- [ ] 데이터 없는 날짜는 회색 표시

**Tasks**:
- [ ] HistoryView 구현
- [ ] CalendarGrid 컴포넌트
- [ ] 날짜별 데이터 로딩 로직
- [ ] 뷰 모드 전환 로직

**Testing**:
- Unit Test: 날짜별 데이터 필터링 로직
- Component Test: 캘린더 렌더링
- E2E Test: 히스토리 → 날짜 선택 → 상세 화면

---

### Sprint 7 완료 기준
- [ ] 대시보드 모든 화면 Figma 디자인과 일치
- [ ] 차트 애니메이션 부드러움
- [ ] API 연동 완료
- [ ] UI 테스트 통과
- [ ] 다크 모드 지원

---

## Sprint 8: Android 앱 기반 구조
**기간**: 2주 (Week 15-16)  
**Sprint 목표**: Android 앱 프로젝트 설정 및 iOS와 동일한 인증/네비게이션 구조 구축  
**총 Story Points**: 21

---

### 🤖 User Story 8.1: Android 프로젝트 초기 설정
**Epic**: Epic 8 - Android 앱 개발  
**Story Points**: 3

**As an** Android Developer  
**I want to** Android Studio 프로젝트를 초기 설정  
**So that** 팀이 Android 앱 개발을 시작할 수 있다

**Description**:
- Android Studio 프로젝트 생성 (Kotlin, Jetpack Compose)
- Gradle 의존성 관리
- Ktlint 설정
- MVVM + Clean Architecture 구조

**Acceptance Criteria**:
- [ ] 프로젝트가 에뮬레이터에서 실행됨
- [ ] Jetpack Compose UI 표시
- [ ] 폴더 구조: ui/, data/, domain/, di/
- [ ] Ktlint 적용
- [ ] .gitignore 설정

**Tasks**:
- [ ] Android Studio 프로젝트 생성
- [ ] build.gradle 의존성 추가 (Compose, Retrofit, Room, Hilt)
- [ ] 폴더 구조 생성
- [ ] Ktlint 설정
- [ ] Hilt DI 설정

**Testing**:
- Unit Test: N/A
- Component Test: N/A
- E2E Test: 앱 실행 확인

---

### 🤖 User Story 8.2: Android 인증 화면 구현
**Epic**: Epic 8 - Android 앱 개발  
**Story Points**: 5

**As an** App User  
**I want to** Android 앱에서 회원가입/로그인  
**So that** iOS와 동일한 방식으로 인증할 수 있다

**Description**:
- 온보딩 화면 (HorizontalPager)
- 회원가입 화면 (Composable Form)
- 로그인 화면
- Google Sign-In 통합
- JWT 토큰 EncryptedSharedPreferences 저장

**Acceptance Criteria**:
- [ ] 온보딩 화면 스와이프 가능
- [ ] 회원가입 폼 검증 (이메일, 비밀번호)
- [ ] 로그인 성공 시 토큰 저장 및 대시보드 이동
- [ ] Google Sign-In 동작
- [ ] iOS와 동일한 UI/UX

**Tasks**:
- [ ] OnboardingScreen Composable
- [ ] SignUpScreen Composable
- [ ] LoginScreen Composable
- [ ] AuthRepository 및 AuthViewModel
- [ ] Google Sign-In SDK 통합
- [ ] EncryptedSharedPreferences 유틸리티
- [ ] 입력 검증 로직

**Testing**:
- Unit Test: 이메일/비밀번호 검증
- Component Test: AuthRepository API 호출 (mock)
- E2E Test: 회원가입 → 로그인 → 토큰 저장

---

### 🤖 User Story 8.3: Android 네비게이션 구조
**Epic**: Epic 8 - Android 앱 개발  
**Story Points**: 3

**As an** App User  
**I want to** Android 앱 내에서 쉽게 화면 이동  
**So that** iOS와 동일한 네비게이션 경험을 얻을 수 있다

**Description**:
- Navigation Compose 기반 라우팅
- BottomNavigation (대시보드, 히스토리, 설정)
- 인증 상태 기반 라우팅

**Acceptance Criteria**:
- [ ] 하단 네비게이션 바 3개 탭
- [ ] 탭 전환 애니메이션
- [ ] 미로그인 시 로그인 화면 리다이렉트
- [ ] 뒤로가기 네비게이션

**Tasks**:
- [ ] NavHost 설정 (Navigation Compose)
- [ ] BottomNavigationBar Composable
- [ ] DashboardScreen, HistoryScreen, SettingsScreen 스켈레톤
- [ ] 인증 상태 체크 로직
- [ ] 네비게이션 아이콘

**Testing**:
- Unit Test: N/A
- Component Test: 네비게이션 동작 확인
- E2E Test: 로그인 → 탭 전환 → 로그아웃

---

### 🤖 User Story 8.4: Samsung Health SDK 통합
**Epic**: Epic 8 - Android 앱 개발  
**Story Points**: 5

**As an** App User  
**I want to** Samsung Health 권한을 허용  
**So that** 앱이 내 건강 데이터를 읽을 수 있다

**Description**:
- Samsung Health SDK 설정
- 권한 요청 (수면, 심박수, SpO2)
- 데이터 읽기 (HealthDataResolver)
- 최근 수면 세션 조회

**Acceptance Criteria**:
- [ ] Samsung Health 앱 설치 확인
- [ ] 권한 요청 다이얼로그 표시
- [ ] 수면, 심박수, SpO2 데이터 읽기 성공
- [ ] 권한 거부 시 안내 메시지
- [ ] 에러 핸들링

**Tasks**:
- [ ] Samsung Health SDK 의존성 추가
- [ ] AndroidManifest.xml 권한 추가
- [ ] SamsungHealthService 클래스 작성
- [ ] 권한 요청 로직
- [ ] 수면 데이터 쿼리 함수
- [ ] 심박수, SpO2 쿼리 함수

**Testing**:
- Unit Test: N/A (실제 기기 필요)
- Component Test: Mock SamsungHealthService
- E2E Test: 실제 기기에서 권한 → 데이터 읽기

---

### 🤖 User Story 8.5: Android 대시보드 기본 UI
**Epic**: Epic 8 - Android 앱 개발  
**Story Points**: 5

**As an** App User  
**I want to** Android에서 iOS와 동일한 대시보드 확인  
**So that** 플랫폼에 관계없이 일관된 경험을 얻을 수 있다

**Description**:
- 대시보드 메인 화면 (iOS와 동일)
- 수면 요약 카드
- 수면 단계 차트 (MPAndroidChart 또는 Compose Charts)
- 질병 위험 카드

**Acceptance Criteria**:
- [ ] iOS와 동일한 레이아웃
- [ ] 수면 요약 카드 표시
- [ ] 수면 단계 막대 차트
- [ ] 질병 위험 카드 (상위 3개)
- [ ] Pull-to-refresh

**Tasks**:
- [ ] DashboardScreen Composable
- [ ] SleepSummaryCard Composable
- [ ] SleepStageChart Composable
- [ ] DiseaseRiskCard Composable
- [ ] DashboardViewModel
- [ ] API 연동

**Testing**:
- Unit Test: ViewModel 로직
- Component Test: 각 컴포넌트 렌더링
- E2E Test: API → 대시보드 표시

---

### Sprint 8 완료 기준
- [ ] Android 앱 실행 및 인증 동작
- [ ] Samsung Health 데이터 읽기 성공
- [ ] 대시보드 기본 UI 표시
- [ ] iOS와 UI 일관성 확인
- [ ] 단위 테스트 커버리지 ≥ 60%

---

## Sprint 9: Wear OS 및 통합
**기간**: 2주 (Week 17-18)  
**Sprint 목표**: Wear OS 앱 개발 및 전체 플랫폼 통합  
**총 Story Points**: 21

---

### ⌚ User Story 9.1: Wear OS 프로젝트 설정
**Epic**: Epic 9 - Wear OS 앱 개발  
**Story Points**: 3

**As an** Android Developer  
**I want to** Wear OS 모듈을 추가  
**So that** Samsung Galaxy Watch 앱을 개발할 수 있다

**Description**:
- Wear OS 모듈 생성
- Wear Compose 설정
- 휴대폰 앱과 데이터 공유 설정

**Acceptance Criteria**:
- [ ] Wear 모듈 빌드 성공
- [ ] Wear 에뮬레이터에서 앱 실행
- [ ] 휴대폰 앱과 연결 가능
- [ ] Wear Compose UI 표시

**Tasks**:
- [ ] Wear OS 모듈 추가
- [ ] build.gradle 설정 (Wear Compose)
- [ ] Data Layer API 설정
- [ ] 기본 WearApp Screen

**Testing**:
- Unit Test: N/A
- Component Test: N/A
- E2E Test: Wear 앱 실행 확인

---

### ⌚ User Story 9.2: Wear 센서 데이터 수집
**Epic**: Epic 9 - Wear OS 앱 개발  
**Story Points**: 8

**As a** Wear App  
**I want to** 수면 중 센서 데이터를 자동 수집  
**So that** watchOS와 동일한 기능을 제공할 수 있다

**Description**:
- Samsung Privileged Health SDK 사용
- 심박수, PPG, 가속도, SpO2 수집
- 1Hz 샘플링
- 로컬 Room DB 저장
- 수면 감지 자동 시작

**Acceptance Criteria**:
- [ ] 수면 감지 시 자동 수집 시작
- [ ] 센서 데이터 1초마다 기록
- [ ] Room DB에 저장
- [ ] 배터리 소모 < 15%
- [ ] watchOS 앱과 동일한 기능

**Tasks**:
- [ ] Samsung Health SDK 권한 요청
- [ ] SensorCollectionService 구현
- [ ] Room DB 설정
- [ ] 수면 감지 로직
- [ ] 백그라운드 작업 스케줄링

**Testing**:
- Unit Test: 센서 데이터 파싱
- Component Test: DB 저장 확인
- E2E Test: 실제 Watch에서 수집 확인

---

### ⌚ User Story 9.3: Wear-Phone 데이터 동기화
**Epic**: Epic 9 - Wear OS 앱 개발  
**Story Points**: 5

**As a** Wear App  
**I want to** 수집한 데이터를 휴대폰으로 전송  
**So that** 서버에 업로드할 수 있다

**Description**:
- Data Layer API로 데이터 전송
- 백그라운드 전송
- 재시도 로직
- 전송 완료 후 로컬 삭제

**Acceptance Criteria**:
- [ ] 수면 종료 후 자동 전송
- [ ] 전송 진행률 표시
- [ ] 실패 시 3회 재시도
- [ ] 백그라운드 전송 지원
- [ ] 전송 완료 후 DB 삭제

**Tasks**:
- [ ] Data Layer API 설정
- [ ] 데이터 전송 함수 (DataClient)
- [ ] 휴대폰 앱 수신 핸들러
- [ ] 재시도 로직
- [ ] UI 진행률 표시

**Testing**:
- Unit Test: 데이터 직렬화
- Component Test: Mock DataClient
- E2E Test: Wear → Phone 전송 확인

---

### 🔗 User Story 9.4: 전체 플랫폼 데이터 플로우 통합
**Epic**: Epic 10 - 크로스 플랫폼 통합  
**Story Points**: 3

**As a** System  
**I want to** iOS/Android 플랫폼 모두에서 동일한 데이터 플로우 동작  
**So that** 사용자 경험을 일관되게 유지할 수 있다

**Description**:
- 웨어러블 → 모바일 → 서버 데이터 플로우 검증
- 양 플랫폼에서 동일한 API 응답 처리
- 에러 핸들링 통일
- 오프라인 모드 지원

**Acceptance Criteria**:
- [ ] iOS/Android 모두 동일한 API 엔드포인트 사용
- [ ] 응답 파싱 로직 동일
- [ ] 네트워크 에러 시 동일한 재시도 정책
- [ ] 오프라인 시 로컬 캐싱
- [ ] 온라인 복귀 시 자동 동기화

**Tasks**:
- [ ] iOS/Android API Service 코드 리뷰 및 통일
- [ ] 에러 코드 및 메시지 통일
- [ ] 오프라인 모드 로직 구현 (양 플랫폼)
- [ ] 동기화 로직 검증

**Testing**:
- Unit Test: 에러 핸들링 로직
- Component Test: API 응답 파싱
- E2E Test: 전체 플로우 (센서 수집 → 서버 업로드 → 결과 조회)

---

### 🎨 User Story 9.5: UI/UX 최종 검수
**Epic**: Epic 10 - 크로스 플랫폼 통합  
**Story Points**: 2

**As a** UI/UX Designer  
**I want to** iOS/Android 앱의 UI를 최종 검수  
**So that** Figma 디자인과 일치하고 일관성을 유지할 수 있다

**Description**:
- Figma 디자인과 실제 앱 비교
- 색상, 폰트, 간격 확인
- 애니메이션 및 전환 효과 검수
- 접근성 검사 (VoiceOver, TalkBack)

**Acceptance Criteria**:
- [ ] 모든 화면이 Figma 디자인과 ≥ 95% 일치
- [ ] 다크 모드 정상 동작 (양 플랫폼)
- [ ] 애니메이션 부드러움 (60 FPS)
- [ ] VoiceOver/TalkBack 레이블 모두 설정
- [ ] 다이나믹 타입/폰트 크기 조절 지원

**Tasks**:
- [ ] iOS/Android 앱 스크린샷과 Figma 비교
- [ ] 색상 값 검증 (hex code)
- [ ] 간격 및 정렬 확인
- [ ] 접근성 레이블 추가
- [ ] 애니메이션 최적화

**Testing**:
- Unit Test: N/A
- Component Test: 각 화면 렌더링 테스트
- E2E Test: 실제 기기에서 전체 플로우 UI 확인

---

### Sprint 9 완료 기준
- [ ] Wear OS 앱 센서 수집 및 동기화 성공
- [ ] iOS/Android 양 플랫폼 데이터 플로우 검증
- [ ] UI/UX Figma 디자인 일치
- [ ] 접근성 기능 모두 동작
- [ ] 크로스 플랫폼 E2E 테스트 통과

---

## Phase 2 완료 기준

### 기능적 완료 기준
- [x] iOS 앱 (iPhone) 실행 가능
- [x] watchOS 앱 (Apple Watch) 센서 수집
- [x] Android 앱 (Phone) 실행 가능
- [x] Wear OS 앱 (Galaxy Watch) 센서 수집
- [x] 모든 플랫폼에서 인증 동작
- [x] HealthKit/Samsung Health 데이터 읽기
- [x] 대시보드 UI 완성 (iOS/Android 동일)
- [x] 웨어러블 → 모바일 → 서버 데이터 플로우 검증

### 비기능적 완료 기준
- [x] 단위 테스트 커버리지 ≥ 60%
- [x] UI 테스트 작성 (주요 화면)
- [x] E2E 테스트 통과 (전체 플로우)
- [x] 배터리 소모 < 15% (8시간 수면)
- [x] UI 프레임 레이트 ≥ 60 FPS
- [x] 앱 크래시율 < 0.1%

### 문서화 완료 기준
- [x] 사용자 가이드 작성
- [x] 개발자 문서 (앱 아키텍처)
- [x] Figma 디자인 시스템 완성
- [x] API 연동 가이드

### 품질 기준
- [x] 코드 리뷰 완료
- [x] SwiftLint/Ktlint 규칙 준수
- [x] 접근성 검증 완료
- [x] 다크 모드 지원

---

## 다음 단계
Phase 2 완료 후 **Phase 3: 통합 및 테스트**로 진행합니다.  
상세 계획은 `SPRINT_PLAN_PHASE3.md` 참조.

---

## 부록

### A. Figma 디자인 체크리스트
- [ ] 컬러 시스템 (Light/Dark)
- [ ] 타이포그래피 (SF Pro, Roboto)
- [ ] 아이콘 세트 (SF Symbols, Material Icons)
- [ ] 컴포넌트 라이브러리 (버튼, 카드, 차트)
- [ ] 화면 와이어프레임 (10개 이상)
- [ ] 인터랙션 프로토타입

### B. 플랫폼별 특이사항

**iOS/watchOS:**
- SwiftUI, HealthKit
- Watch Connectivity
- Keychain Services
- SF Symbols

**Android/Wear OS:**
- Jetpack Compose, Samsung Health SDK
- Data Layer API
- EncryptedSharedPreferences
- Material Design 3

### C. 변경 이력
| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0 | 2026-01-08 | Phase 2 Sprint Plan 초안 작성 | Development Team |

---

**문서 승인:**
- [ ] 프로젝트 매니저
- [ ] iOS Lead
- [ ] Android Lead
- [ ] UI/UX Designer

**다음 Sprint Planning 미팅:** Sprint 5 시작 전
