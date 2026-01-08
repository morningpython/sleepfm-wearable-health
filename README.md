# SleepFM-Wearable-Health

## 📌 프로젝트 개요
이 프로젝트는 **SleepFM (Sleep Foundation Model)**을 기반으로 웨어러블 기기 데이터를 활용해  
수면 분석 및 질병 위험 예측을 연구하는 프로토타입입니다.

- **연구 목적**: 수면 데이터로 다양한 질환 위험을 조기 예측
- **적용 범위**: 웨어러블 기기(ECG, PPG, 호흡, 가속도 등) 데이터
- **타겟 플랫폼**: 
  - 🍎 **Apple Watch** (watchOS + iOS 앱)
  - ⌚ **Samsung Galaxy Watch** (Wear OS + Android 앱)
- **결과물**: 연구용 모바일/웨어러블 앱 및 추론 서비스

---

## 💤 배경: SleepFM 논문 요약

### 연구 핵심
- **SleepFM**: 65,000명 이상, 총 58만 시간 이상의 PSG 데이터로 학습된 멀티모달 수면 기반 파운데이션 모델
- **대조 학습(Contrastive Learning)** 기법을 적용해 다양한 PSG 환경에서도 일반화 가능
- **출처**: [Nature Medicine, 2026](https://www.nature.com/articles/s41591-025-04133-4)

### 주요 성과
- **질병 예측**: 단 하루 밤의 수면 데이터로 130개 질환 예측 (C-Index ≥ 0.75)
  - 파킨슨병: 0.93
  - 치매: 0.85
  - 심근경색: 0.81
  - 심부전: 0.80
  - 만성 신장질환: 0.79
  - 뇌졸중: 0.78
- **수면 분석**: 수면 단계 분류(F1 0.70–0.78), 수면무호흡증 분류 정확도 0.87
- **기존 모델 대비**: 단순 인구통계 기반 모델이나 End-to-End PSG 모델보다 5–17% 성능 향상

### 웨어러블 기기 활용 가능성
- 매일 밤 자동으로 질병 위험 예측 업데이트 → 조기 경고 시스템
- 파킨슨병, 치매 같은 신경퇴행성 질환 조기 탐지
- 심혈관 질환 위험도 예측 → 병원 방문 전 선제적 대응
- 비침습적이고 실시간 건강 모니터링 가능
- 저비용·대규모 모니터링으로 의료 접근성 확대

---

## ⚙️ 주요 기능

### 백엔드 (ML 모델 서비스)
- **데이터 전처리**: 웨어러블 신호를 128Hz로 리샘플링, 5초 윈도우 토큰화
- **멀티모달 임베딩 추출**: CNN 토크나이저 + 채널/시간 어텐션 풀링
- **질병 위험 예측**: Linear/LSTM 기반 CoxPH 헤드로 다중 질환 위험 스코어 산출
- **수면 분석**: 수면 단계 분류, 무호흡 탐지
- **추론 서비스**: FastAPI 기반 REST API

### 모바일/웨어러블 앱
- **Apple Watch (watchOS)**:
  - HealthKit을 통한 수면 데이터, 심박수, 호흡률 수집
  - 백그라운드 센서 데이터 기록
  - 실시간 건강 알림
  
- **Samsung Galaxy Watch (Wear OS)**:
  - Samsung Health SDK를 통한 생체 신호 수집
  - SpO2, 심박수, 수면 단계 데이터 추출
  - Kotlin/Compose 기반 UI

- **모바일 앱 (iOS/Android)**:
  - 수면 분석 대시보드
  - 질병 위험 스코어 시각화
  - 주간/월간 건강 리포트
  - 워치 데이터 동기화 및 서버 전송

---

## 📂 프로젝트 구조

```
sleepfm-wearable/
├─ backend/                         # ML 백엔드 서비스
│  ├─ env.yml                       # Python 환경 설정
│  ├─ configs/                      # 모델 설정 파일
│  │  ├─ inference_wearable.yaml
│  │  └─ finetune_wearable.yaml
│  ├─ models/                       # SleepFM 인코더, 헤드
│  │  ├─ sleepfm_encoder.py
│  │  ├─ pooling.py
│  │  ├─ transformer.py
│  │  └─ heads.py
│  ├─ data/                         # 공개 데이터셋 로더
│  │  ├─ shhs/
│  │  └─ samples/
│  ├─ scripts/                      # 전처리, 임베딩 추출, 파인튜닝
│  │  ├─ preprocess_wearable.py
│  │  ├─ extract_embeddings.py
│  │  ├─ finetune_linear.py
│  │  └─ infer_risk.py
│  └─ api/                          # REST API 서버
│     ├─ server.py                  # FastAPI 서버
│     ├─ routes/
│     └─ services/
│
├─ mobile/                          # 모바일 앱
│  ├─ ios/                          # iOS 앱 (Swift/SwiftUI)
│  │  ├─ SleepFM.xcodeproj
│  │  ├─ SleepFM/
│  │  │  ├─ Views/                  # UI 컴포넌트
│  │  │  ├─ Models/                 # 데이터 모델
│  │  │  ├─ Services/               # API, HealthKit 서비스
│  │  │  └─ Utils/
│  │  └─ SleepFMWatch/              # Apple Watch 앱
│  │     ├─ Views/
│  │     ├─ Services/               # HealthKit, 센서 데이터 수집
│  │     └─ Complications/          # 워치페이스 컴플리케이션
│  │
│  └─ android/                      # Android 앱 (Kotlin/Jetpack Compose)
│     ├─ app/
│     │  ├─ src/main/
│     │  │  ├─ java/com/sleepfm/
│     │  │  │  ├─ ui/               # Compose UI
│     │  │  │  ├─ data/             # Repository, Models
│     │  │  │  ├─ services/         # API, Samsung Health SDK
│     │  │  │  └─ viewmodels/
│     │  │  └─ res/
│     │  └─ build.gradle
│     └─ wear/                      # Wear OS 앱
│        ├─ src/main/
│        │  ├─ java/com/sleepfm/wear/
│        │  │  ├─ ui/               # Wear Compose UI
│        │  │  ├─ sensors/          # 센서 데이터 수집
│        │  │  └─ services/
│        │  └─ res/
│        └─ build.gradle
│
├─ docs/                            # 문서
│  ├─ api/                          # API 문서
│  ├─ architecture/                 # 아키텍처 다이어그램
│  └─ design/                       # 앱 디자인 가이드
│
└─ README.md
```

---

## 🚀 시작하기

### 백엔드 설정
```bash
# Conda 환경 생성
cd backend
conda env create -f env.yml
conda activate sleepfm

# 공식 저장소 클론 (참조 및 가중치용)
git clone https://github.com/zou-group/sleepfm-clinical
```

### 데이터 준비
- **공개 데이터셋**: SHHS, MrOS, MESA, SSC 등 공개 수면 데이터셋 다운로드
  - 각 데이터셋의 Data Use Agreement(DUA) 준수 필요
  - 연구 목적으로만 사용 가능
- **웨어러블 신호**: ECG, PPG, 호흡, 가속도 등 데이터 전처리

### API 서버 실행
```bash
cd backend/api
uvicorn server:app --reload
```

### 모바일 앱 개발

#### iOS 앱 (Xcode 필요)
```bash
cd mobile/ios
open SleepFM.xcodeproj
# Xcode에서 빌드 및 시뮬레이터 실행
```

**필수 요구사항:**
- Xcode 15.0+
- iOS 17.0+ / watchOS 10.0+
- Apple Developer 계정 (HealthKit 권한 필요)

#### Android 앱 (Android Studio 필요)
```bash
cd mobile/android
./gradlew build
# Android Studio에서 프로젝트 열기
```

**필수 요구사항:**
- Android Studio Hedgehog+
- Android SDK 34+
- Wear OS SDK (Wear OS 앱 개발용)
- Samsung Health SDK 등록 필요

---

## 🔧 기술적 세부사항

### 모델 구조
- **멀티모달 입력**: PSG에서 얻은 다양한 생리 신호(뇌파, 심전도, 호흡, 근전도 등)를 동시에 처리
- **파운데이션 모델**: 대규모 데이터로 학습된 범용 기반 모델
- **표현 학습**: 수면 데이터의 잠재적 패턴을 추출해 질병 예측에 활용

### 학습 방식
- **대조 학습**: 서로 다른 PSG 환경에서도 일반화 가능
- **전이학습**: 새로운 데이터셋에 적용했을 때도 성능 유지
- **다중 작업 학습**: 수면 단계 분류, 무호흡증 탐지, 질병 예측을 동시에 학습

### 채널-불문(Channel-Agnostic) 설계
- 어떤 모달이 비어도 성능 유지
- 채널/시간 어텐션 풀링 레이어를 통한 강건성
- 웨어러블 데이터의 채널 누락/변동에도 대응 가능

---

## 📊 연구 활용

### 사용 가능 범위
- ✅ 연구 목적으로만 사용 가능
- ✅ 공개 코드 및 사전학습 가중치 활용 가능
- ✅ 공개 데이터셋(SHHS, MrOS, MESA, SSC) 활용 가능 (DUA 준수)
- ⚠️ BioSerenity 데이터는 별도 계약 필요
- ❌ 상용화 전에는 별도 라이선스 및 임상 검증 필수

### 개발 로드맵

#### Phase 1: ML 백엔드 구축
1. **목표 범위 확정**: 수면 단계 + 무호흡 탐지부터 시작, 3–5개 핵심 질환 카테고리 위험 스코어 제공
2. **데이터 적합화**: 웨어러블 신호로 소규모 파인튜닝, PSG→웨어러블 도메인 적응
3. **모델 경량화**:
   - 임베딩 고정 + 선형 헤드로 추론 비용 최소화
   - 컨텍스트 축소: 5분 → 1–2분 윈도우로 지연/메모리 절감
4. **API 개발**: FastAPI 기반 REST API 구축, 인증/보안 추가

#### Phase 2: 모바일/웨어러블 앱 개발
1. **iOS/watchOS 앱**:
   - HealthKit 통합 (수면 데이터, 심박수, 호흡률)
   - SwiftUI 기반 대시보드 UI
   - Apple Watch 센서 데이터 수집 및 백그라운드 처리
   - 로컬 데이터 저장 및 서버 동기화
   
2. **Android/Wear OS 앱**:
   - Samsung Health SDK 통합
   - Jetpack Compose 기반 UI
   - Wear OS 센서 데이터 수집
   - Room DB 로컬 캐싱

#### Phase 3: 통합 및 테스트
1. **검증**: 내부 테스트 → 공개 데이터 교차검증
2. **배포**: CI/CD로 모델 버전 관리, 추론 로깅/모니터링
3. **규제/윤리**: 연구용 라벨, 비진단 고지, 개인정보 보호 설계
4. **베타 테스트**: 실제 사용자 피드백 수집

---

## 🔮 향후 계획
- ✅ 웨어러블 데이터 기반 경량화 모델 개발
- ✅ Apple Watch 및 Samsung Galaxy Watch 네이티브 앱 개발
- 🔄 개인 맞춤형 건강 관리 대시보드 (모바일 앱)
- 🔄 실시간 건강 알림 시스템 (워치 컴플리케이션)
- 📅 의료 시스템과의 연계 가능성 탐색
- 📅 클라우드 기반 데이터 분석 파이프라인 구축
- 📅 다국어 지원 (한국어, 영어)
- 📅 Apple Health 및 Samsung Health 데이터 내보내기 지원

---

## ⚠️ 주의사항
- 본 프로젝트는 **연구용 프로토타입**입니다.
- **의료 진단이나 치료 목적으로 사용할 수 없습니다**.
- 모든 위험 스코어는 참고용이며, 전문가 상담을 권장합니다.
- 개인정보 보호 및 데이터 보안을 최우선으로 고려해야 합니다.

---

## 📚 참고자료
- [SleepFM 논문 (Nature Medicine, 2026)](https://www.nature.com/articles/s41591-025-04133-4)
- [SleepFM 공식 GitHub 저장소](https://github.com/zou-group/sleepfm-clinical)
- 공개 수면 데이터셋: SHHS, MrOS, MESA, SSC

---

## 🤝 기여
연구 목적의 기여를 환영합니다. 이슈 및 풀 리퀘스트를 통해 참여해 주세요.

---

## 📝 라이선스
본 프로젝트는 연구 목적으로만 사용 가능합니다. 상용화를 위해서는 별도의 라이선스 및 임상 검증이 필요합니다.
