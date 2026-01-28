//
//  SleepDetailViewModel.swift
//  SleepFM
//
//  수면 상세 화면 ViewModel
//

import Foundation

/// 수면 상세 뷰모델
@MainActor
final class SleepDetailViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    @Published var sleepScore: Double = 0
    @Published var sleepEfficiency: Double = 0
    @Published var totalSleepTime: TimeInterval = 0
    @Published var bedTime: Date?
    @Published var wakeTime: Date?
    @Published var stageDurations: [SleepStage: TimeInterval] = [:]
    @Published var sleepStageData: [SleepStageDataPoint] = []
    @Published var recommendations: [String] = []
    
    // MARK: - Public Methods
    
    func loadSleepDetail(for date: Date) async {
        isLoading = true
        errorMessage = nil
        
        do {
            // TODO: 실제 API 호출
            try await Task.sleep(nanoseconds: 800_000_000)
            
            // 더미 데이터
            let calendar = Calendar.current
            let yesterday = calendar.date(byAdding: .day, value: -1, to: date)!
            
            bedTime = calendar.date(bySettingHour: 23, minute: Int.random(in: 0...45), second: 0, of: yesterday)
            wakeTime = calendar.date(bySettingHour: Int.random(in: 6...8), minute: Int.random(in: 0...59), second: 0, of: date)
            
            if let bed = bedTime, let wake = wakeTime {
                totalSleepTime = wake.timeIntervalSince(bed)
            }
            
            sleepScore = Double.random(in: 65...95)
            sleepEfficiency = Double.random(in: 75...95)
            
            stageDurations = [
                .n3: Double.random(in: 70...120) * 60,
                .n2: Double.random(in: 150...220) * 60,
                .n1: Double.random(in: 15...45) * 60,
                .rem: Double.random(in: 80...140) * 60,
                .wake: Double.random(in: 5...35) * 60
            ]
            
            generateSleepStageData()
            generateRecommendations()
            
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    // MARK: - Private Methods
    
    private func generateSleepStageData() {
        guard let start = bedTime, let end = wakeTime else { return }
        
        var data: [SleepStageDataPoint] = []
        var currentTime = start
        var epochIndex = 0
        let epochDuration: TimeInterval = 30
        
        let cycles: [[SleepStage]] = [
            [.wake, .n1, .n2, .n3, .n3, .n2, .rem],
            [.n1, .n2, .n3, .n2, .rem, .rem],
            [.n1, .n2, .n2, .rem, .rem, .rem],
            [.n1, .n2, .rem, .rem, .n1, .wake]
        ]
        
        var cycleIndex = 0
        var stageIndex = 0
        let epochsPerStage = Int.random(in: 40...80)
        
        while currentTime < end {
            let cycle = cycles[cycleIndex % cycles.count]
            let stage = cycle[stageIndex % cycle.count]
            
            data.append(SleepStageDataPoint(
                time: currentTime,
                stage: stage,
                epochIndex: epochIndex
            ))
            
            currentTime = currentTime.addingTimeInterval(epochDuration)
            epochIndex += 1
            
            if epochIndex % epochsPerStage == 0 {
                stageIndex += 1
                if stageIndex >= cycle.count {
                    stageIndex = 0
                    cycleIndex += 1
                }
            }
        }
        
        sleepStageData = data
    }
    
    private func generateRecommendations() {
        var recs: [String] = []
        
        // 수면 효율 기반
        if sleepEfficiency < 85 {
            recs.append("취침 30분 전에는 스마트폰 사용을 자제해보세요.")
        }
        
        // 수면 점수 기반
        if sleepScore < 75 {
            recs.append("규칙적인 수면 스케줄을 유지하는 것이 좋아요.")
        }
        
        // 깊은 수면 비율 기반
        let totalDuration = stageDurations.values.reduce(0, +)
        if let n3Duration = stageDurations[.n3], totalDuration > 0 {
            let n3Percentage = (n3Duration / totalDuration) * 100
            if n3Percentage < 15 {
                recs.append("낮에 30분 정도 가벼운 운동을 하면 깊은 수면에 도움이 됩니다.")
            }
        }
        
        // REM 수면 기반
        if let remDuration = stageDurations[.rem], totalDuration > 0 {
            let remPercentage = (remDuration / totalDuration) * 100
            if remPercentage < 20 {
                recs.append("스트레스를 줄이면 REM 수면이 개선될 수 있어요.")
            }
        }
        
        // 기본 권장사항
        recs.append("매일 같은 시간에 잠자리에 드는 습관을 유지해보세요.")
        recs.append("취침 전 카페인과 알코올 섭취를 피해주세요.")
        
        recommendations = Array(recs.prefix(4))
    }
}
