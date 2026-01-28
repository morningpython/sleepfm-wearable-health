//
//  DashboardViewModel.swift
//  SleepFM
//
//  대시보드 화면 ViewModel
//

import Foundation
import Combine

/// 대시보드 뷰모델
@MainActor
final class DashboardViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    /// 로딩 상태
    @Published var isLoading = false
    
    /// 에러 메시지
    @Published var errorMessage: String?
    
    /// 마지막 수면 세션
    @Published var lastSession: SleepSessionDetail?
    
    /// 수면 점수
    @Published var sleepScore: Double = 0
    
    /// 수면 효율
    @Published var sleepEfficiency: Double = 0
    
    /// 총 수면 시간 (초)
    @Published var totalSleepTime: TimeInterval = 0
    
    /// 취침 시간
    @Published var bedTime: Date?
    
    /// 기상 시간
    @Published var wakeTime: Date?
    
    /// 수면 단계별 시간
    @Published var stageDurations: [SleepStage: TimeInterval] = [:]
    
    /// 수면 단계 데이터 포인트 (차트용)
    @Published var sleepStageData: [SleepStageDataPoint] = []
    
    /// 질병 위험 예측
    @Published var diseaseRisks: [DiseaseRiskItem] = []
    
    /// Watch 동기화 상태
    @Published var watchSyncStatus: WatchSyncStatus = .unknown
    
    // MARK: - Private Properties
    
    private let apiService: APIService
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Initialization
    
    init(apiService: APIService = .shared) {
        self.apiService = apiService
    }
    
    // MARK: - Public Methods
    
    /// 대시보드 데이터 로드
    func loadDashboardData() async {
        isLoading = true
        errorMessage = nil
        
        do {
            // 마지막 세션 가져오기
            try await loadLastSession()
            
            // 질병 위험 데이터 로드
            try await loadDiseaseRisks()
            
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    /// 새로고침
    func refresh() async {
        await loadDashboardData()
    }
    
    // MARK: - Private Methods
    
    private func loadLastSession() async throws {
        // 실제 API 호출 시도
        do {
            guard let userId = await getCurrentUserId() else {
                throw APIError.unauthorized
            }
            
            let response = try await apiService.getSessions(userId: userId, limit: 1)
            
            if let latestSession = response.sessions.first, latestSession.hasResults {
                // 세션 결과 가져오기
                let results = try await apiService.getSessionResults(sessionId: latestSession.id)
                updateFromSessionResults(results)
            } else {
                // 분석 결과 없으면 더미 데이터
                loadDummySessionData()
            }
        } catch {
            // API 실패 시 더미 데이터로 폴백
            print("⚠️ API 호출 실패, 더미 데이터 사용: \(error)")
            loadDummySessionData()
        }
    }
    
    private func getCurrentUserId() async -> Int? {
        // AuthViewModel에서 현재 사용자 ID 가져오기
        return AuthViewModel.shared.currentUser?.id
    }
    
    private func updateFromSessionResults(_ results: SessionResultsResponse) {
        // 분석 결과에서 데이터 추출
        for analysis in results.analyses {
            switch analysis.type {
            case "sleep_stages":
                if let stageDurationsDict = analysis.result["stage_durations"]?.value as? [String: Double] {
                    stageDurations = parseStageDurations(stageDurationsDict)
                }
                
            case "sleep_summary":
                if let efficiency = analysis.result["sleep_efficiency"]?.value as? Double {
                    sleepEfficiency = efficiency
                }
                if let totalMinutes = analysis.result["total_sleep_time_minutes"]?.value as? Double {
                    totalSleepTime = totalMinutes * 60
                }
                
            case "disease_risk":
                // 질병 위험 분석은 별도 처리
                break
                
            default:
                break
            }
        }
        
        // 세션 날짜로 시간 설정
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        if let sessionDate = dateFormatter.date(from: results.sessionDate) {
            bedTime = Calendar.current.date(bySettingHour: 23, minute: 0, second: 0, of: sessionDate)
            if let duration = results.durationHours {
                wakeTime = bedTime?.addingTimeInterval(duration * 3600)
            }
        }
        
        // 수면 점수 계산 (효율 기반)
        sleepScore = calculateSleepScore()
        
        // 차트 데이터 생성
        generateSleepStageChartData()
    }
    
    private func parseStageDurations(_ dict: [String: Double]) -> [SleepStage: TimeInterval] {
        var result: [SleepStage: TimeInterval] = [:]
        
        for (key, minutes) in dict {
            let stage: SleepStage
            switch key.lowercased() {
            case "n3", "deep": stage = .n3
            case "n2", "light": stage = .n2
            case "n1": stage = .n1
            case "rem": stage = .rem
            case "wake", "awake": stage = .wake
            default: continue
            }
            result[stage] = minutes * 60 // 분 -> 초
        }
        
        return result
    }
    
    private func calculateSleepScore() -> Double {
        // 수면 점수 = 효율 * 0.4 + 깊은수면비율 * 0.3 + REM비율 * 0.3
        let totalStageTime = stageDurations.values.reduce(0, +)
        guard totalStageTime > 0 else { return sleepEfficiency }
        
        let deepRatio = (stageDurations[.n3] ?? 0) / totalStageTime
        let remRatio = (stageDurations[.rem] ?? 0) / totalStageTime
        
        let score = sleepEfficiency * 0.4 + (deepRatio * 100) * 0.3 + (remRatio * 100) * 0.3
        return min(100, max(0, score))
    }
    
    private func loadDummySessionData() {
        // 더미 데이터 설정
        let now = Date()
        let yesterday = Calendar.current.date(byAdding: .day, value: -1, to: now)!
        
        bedTime = Calendar.current.date(bySettingHour: 23, minute: 15, second: 0, of: yesterday)
        wakeTime = Calendar.current.date(bySettingHour: 6, minute: 45, second: 0, of: now)
        
        if let bed = bedTime, let wake = wakeTime {
            totalSleepTime = wake.timeIntervalSince(bed)
        }
        
        sleepScore = Double.random(in: 70...92)
        sleepEfficiency = Double.random(in: 80...95)
        
        // 수면 단계 더미 데이터
        stageDurations = [
            .n3: Double.random(in: 80...110) * 60,
            .n2: Double.random(in: 150...200) * 60,
            .n1: Double.random(in: 20...40) * 60,
            .rem: Double.random(in: 90...130) * 60,
            .wake: Double.random(in: 10...30) * 60
        ]
        
        // 수면 단계 차트 데이터 생성
        generateSleepStageChartData()
    }
    
    private func generateSleepStageChartData() {
        guard let start = bedTime, let end = wakeTime else { return }
        
        var data: [SleepStageDataPoint] = []
        var currentTime = start
        var epochIndex = 0
        let epochDuration: TimeInterval = 30 // 30초 에포크
        
        // 수면 사이클 시뮬레이션 (약 90분 주기)
        let stages: [[SleepStage]] = [
            [.wake, .n1, .n2, .n3, .n3, .n2, .rem],  // 첫 사이클
            [.n1, .n2, .n3, .n2, .rem, .rem],        // 두번째 사이클
            [.n1, .n2, .n2, .rem, .rem, .rem],       // 세번째 사이클
            [.n1, .n2, .rem, .rem, .n1, .wake]       // 마지막 사이클
        ]
        
        var cycleIndex = 0
        var stageInCycleIndex = 0
        let epochsPerStage = 60 // 각 단계당 약 30분 (60 에포크 × 30초)
        
        while currentTime < end {
            let currentCycle = stages[cycleIndex % stages.count]
            let stage = currentCycle[stageInCycleIndex % currentCycle.count]
            
            data.append(SleepStageDataPoint(
                time: currentTime,
                stage: stage,
                epochIndex: epochIndex
            ))
            
            currentTime = currentTime.addingTimeInterval(epochDuration)
            epochIndex += 1
            
            // 단계 진행
            if epochIndex % epochsPerStage == 0 {
                stageInCycleIndex += 1
                if stageInCycleIndex >= currentCycle.count {
                    stageInCycleIndex = 0
                    cycleIndex += 1
                }
            }
        }
        
        sleepStageData = data
    }
    
    private func loadDiseaseRisks() async throws {
        // 실제 API에서 마지막 세션의 질병 위험 가져오기
        do {
            guard let userId = await getCurrentUserId() else {
                loadDummyDiseaseRisks()
                return
            }
            
            let sessions = try await apiService.getSessions(userId: userId, limit: 1)
            
            if let latestSession = sessions.sessions.first {
                let riskResponse = try await apiService.analyzeDiseaseRisk(sessionId: latestSession.id)
                diseaseRisks = riskResponse.predictions.map { prediction in
                    DiseaseRiskItem(
                        disease: prediction.disease,
                        diseaseNameKo: diseaseNameInKorean(prediction.disease),
                        score: prediction.score,
                        category: RiskCategory(from: prediction.category),
                        trend: .stable // 트렌드는 히스토리에서 계산 필요
                    )
                }
            } else {
                loadDummyDiseaseRisks()
            }
        } catch {
            print("⚠️ 질병 위험 API 호출 실패, 더미 데이터 사용: \(error)")
            loadDummyDiseaseRisks()
        }
    }
    
    private func diseaseNameInKorean(_ disease: String) -> String {
        switch disease.lowercased() {
        case "parkinsons", "parkinson": return "파킨슨병"
        case "dementia", "alzheimer": return "치매"
        case "myocardial_infarction", "heart_attack": return "심근경색"
        case "heart_failure": return "심부전"
        case "stroke": return "뇌졸중"
        default: return disease
        }
    }
    
    private func loadDummyDiseaseRisks() {
        // 더미 데이터
        diseaseRisks = [
            DiseaseRiskItem(
                disease: "parkinsons",
                diseaseNameKo: "파킨슨병",
                score: Double.random(in: 15...45),
                category: .moderate,
                trend: .down
            ),
            DiseaseRiskItem(
                disease: "dementia",
                diseaseNameKo: "치매",
                score: Double.random(in: 10...30),
                category: .low,
                trend: .stable
            ),
            DiseaseRiskItem(
                disease: "myocardial_infarction",
                diseaseNameKo: "심근경색",
                score: Double.random(in: 20...50),
                category: .moderate,
                trend: .up
            ),
            DiseaseRiskItem(
                disease: "heart_failure",
                diseaseNameKo: "심부전",
                score: Double.random(in: 15...40),
                category: .low,
                trend: .down
            ),
            DiseaseRiskItem(
                disease: "stroke",
                diseaseNameKo: "뇌졸중",
                score: Double.random(in: 25...55),
                category: .moderate,
                trend: .stable
            )
        ]
    }
}

// MARK: - Supporting Types

/// 수면 세션 상세
struct SleepSessionDetail {
    let id: String
    let date: Date
    let startTime: Date
    let endTime: Date
    let sleepScore: Double
    let efficiency: Double
    let stages: [SleepStageDataPoint]
}

/// 질병 위험 아이템
struct DiseaseRiskItem: Identifiable {
    var id: String { disease }
    let disease: String
    let diseaseNameKo: String
    let score: Double
    let category: RiskCategory
    let trend: TrendDirection
}

/// Watch 동기화 상태
enum WatchSyncStatus {
    case unknown
    case syncing
    case synced(Date)
    case failed(String)
    
    var statusText: String {
        switch self {
        case .unknown: return "연결 대기 중"
        case .syncing: return "동기화 중..."
        case .synced(let date):
            let formatter = RelativeDateTimeFormatter()
            formatter.locale = Locale(identifier: "ko_KR")
            return formatter.localizedString(for: date, relativeTo: Date())
        case .failed(let error): return "오류: \(error)"
        }
    }
}
