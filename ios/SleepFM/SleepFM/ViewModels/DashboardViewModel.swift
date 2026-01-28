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
        // TODO: 실제 API 호출로 교체
        // 현재는 더미 데이터 사용
        
        // 시뮬레이션 딜레이
        try await Task.sleep(nanoseconds: 500_000_000)
        
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
        // TODO: 실제 API 호출로 교체
        
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
