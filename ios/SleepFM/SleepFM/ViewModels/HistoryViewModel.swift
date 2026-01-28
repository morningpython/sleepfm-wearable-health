//
//  HistoryViewModel.swift
//  SleepFM
//
//  히스토리 화면 ViewModel
//

import Foundation

/// 히스토리 뷰모델
@MainActor
final class HistoryViewModel: ObservableObject {
    
    // MARK: - Published Properties
    
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var calendarData: [Date: CalendarDaySleepData] = [:]
    @Published var sessions: [SleepHistorySession] = []
    
    // MARK: - Computed Properties
    
    var sortedSessions: [SleepHistorySession] {
        sessions.sorted { $0.date > $1.date }
    }
    
    var weeklyAverageScore: Double {
        let weekSessions = sessionsInCurrentWeek
        guard !weekSessions.isEmpty else { return 0 }
        return weekSessions.map(\.score).reduce(0, +) / Double(weekSessions.count)
    }
    
    var weeklyAverageDuration: TimeInterval {
        let weekSessions = sessionsInCurrentWeek
        guard !weekSessions.isEmpty else { return 0 }
        return weekSessions.map(\.duration).reduce(0, +) / Double(weekSessions.count)
    }
    
    var formattedWeeklyAverageDuration: String {
        let hours = Int(weeklyAverageDuration / 3600)
        let minutes = Int((weeklyAverageDuration.truncatingRemainder(dividingBy: 3600)) / 60)
        return "\(hours)h \(minutes)m"
    }
    
    var weeklyRecordedDays: Int {
        sessionsInCurrentWeek.count
    }
    
    var monthlyHighScore: Double {
        let monthSessions = sessionsInCurrentMonth
        return monthSessions.map(\.score).max() ?? 0
    }
    
    var monthlyLowScore: Double {
        let monthSessions = sessionsInCurrentMonth
        return monthSessions.map(\.score).min() ?? 0
    }
    
    var streakDays: Int {
        calculateStreak()
    }
    
    private var sessionsInCurrentWeek: [SleepHistorySession] {
        let calendar = Calendar.current
        let startOfWeek = calendar.date(from: calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: Date()))!
        return sessions.filter { $0.date >= startOfWeek }
    }
    
    private var sessionsInCurrentMonth: [SleepHistorySession] {
        let calendar = Calendar.current
        let startOfMonth = calendar.date(from: calendar.dateComponents([.year, .month], from: Date()))!
        return sessions.filter { $0.date >= startOfMonth }
    }
    
    // MARK: - Public Methods
    
    func loadHistoryData() async {
        isLoading = true
        errorMessage = nil
        
        do {
            // TODO: 실제 API 호출
            try await Task.sleep(nanoseconds: 500_000_000)
            
            generateDummyData()
            
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
    
    func getSleepData(for date: Date) -> CalendarDaySleepData? {
        let calendar = Calendar.current
        let normalizedDate = calendar.startOfDay(for: date)
        return calendarData[normalizedDate]
    }
    
    // MARK: - Private Methods
    
    private func generateDummyData() {
        let calendar = Calendar.current
        var data: [Date: CalendarDaySleepData] = [:]
        var sessionList: [SleepHistorySession] = []
        
        // 지난 60일 데이터 생성
        for i in 0..<60 {
            guard let date = calendar.date(byAdding: .day, value: -i, to: Date()) else { continue }
            let normalizedDate = calendar.startOfDay(for: date)
            
            // 랜덤하게 데이터 있음/없음 결정 (80% 확률로 있음)
            let hasData = Double.random(in: 0...1) < 0.8
            
            if hasData {
                let score = Double.random(in: 45...98)
                let duration = Double.random(in: 5...9) * 3600
                
                data[normalizedDate] = CalendarDaySleepData(
                    date: normalizedDate,
                    score: score,
                    hasData: true
                )
                
                sessionList.append(SleepHistorySession(
                    id: UUID().uuidString,
                    date: normalizedDate,
                    score: score,
                    duration: duration,
                    bedTime: calendar.date(bySettingHour: 23, minute: Int.random(in: 0...59), second: 0, of: date)!,
                    wakeTime: calendar.date(bySettingHour: Int.random(in: 6...8), minute: Int.random(in: 0...59), second: 0, of: date)!
                ))
            } else {
                data[normalizedDate] = CalendarDaySleepData(
                    date: normalizedDate,
                    score: nil,
                    hasData: false
                )
            }
        }
        
        calendarData = data
        sessions = sessionList
    }
    
    private func calculateStreak() -> Int {
        let calendar = Calendar.current
        var streak = 0
        var checkDate = Date()
        
        while true {
            let normalizedDate = calendar.startOfDay(for: checkDate)
            
            if let data = calendarData[normalizedDate], data.hasData {
                streak += 1
                checkDate = calendar.date(byAdding: .day, value: -1, to: checkDate)!
            } else {
                break
            }
        }
        
        return streak
    }
}

// MARK: - Supporting Types

/// 수면 히스토리 세션
struct SleepHistorySession: Identifiable {
    let id: String
    let date: Date
    let score: Double
    let duration: TimeInterval
    let bedTime: Date
    let wakeTime: Date
    
    var scoreCategory: ScoreCategory {
        ScoreCategory.fromScore(score)
    }
    
    var dayString: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ko_KR")
        formatter.dateFormat = "d"
        return formatter.string(from: date)
    }
    
    var dateString: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ko_KR")
        formatter.dateFormat = "M월"
        return formatter.string(from: date)
    }
    
    var formattedDuration: String {
        let hours = Int(duration / 3600)
        let minutes = Int((duration.truncatingRemainder(dividingBy: 3600)) / 60)
        return "\(hours)시간 \(minutes)분"
    }
}
