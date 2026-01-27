//
//  SleepSession.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import Foundation

/// 수면 세션 모델
struct SleepSession: Codable, Identifiable, Equatable {
    let id: String
    let date: Date
    let startTime: Date
    let endTime: Date
    let durationHours: Double
    var analysisStatus: AnalysisStatus?
    var hasResults: Bool = false
    
    /// 분석 상태
    enum AnalysisStatus: String, Codable {
        case pending
        case processing
        case completed
        case failed
    }
    
    /// 포맷된 날짜 문자열
    var formattedDate: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ko_KR")
        formatter.dateFormat = "M월 d일 (E)"
        return formatter.string(from: date)
    }
    
    /// 포맷된 시간 범위
    var formattedTimeRange: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return "\(formatter.string(from: startTime)) - \(formatter.string(from: endTime))"
    }
    
    /// 포맷된 수면 시간
    var formattedDuration: String {
        let hours = Int(durationHours)
        let minutes = Int((durationHours - Double(hours)) * 60)
        return "\(hours)시간 \(minutes)분"
    }
}

/// 수면 단계
enum SleepStage: Int, Codable, CaseIterable {
    case wake = 0
    case n1 = 1
    case n2 = 2
    case n3 = 3
    case rem = 4
    
    var name: String {
        switch self {
        case .wake: return "각성"
        case .n1: return "얕은 수면 1"
        case .n2: return "얕은 수면 2"
        case .n3: return "깊은 수면"
        case .rem: return "REM 수면"
        }
    }
    
    var shortName: String {
        switch self {
        case .wake: return "Wake"
        case .n1: return "N1"
        case .n2: return "N2"
        case .n3: return "N3"
        case .rem: return "REM"
        }
    }
    
    var color: String {
        switch self {
        case .wake: return "stageWake"
        case .n1: return "stageN1"
        case .n2: return "stageN2"
        case .n3: return "stageN3"
        case .rem: return "stageREM"
        }
    }
}

/// 수면 분석 결과
struct SleepAnalysisResult: Codable, Identifiable {
    let id: Int
    let sessionId: Int
    let analysisType: String
    let resultData: AnalysisResultData
    let createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case sessionId = "session_id"
        case analysisType = "analysis_type"
        case resultData = "result_data"
        case createdAt = "created_at"
    }
}

/// 분석 결과 데이터
struct AnalysisResultData: Codable {
    // 수면 단계 분석
    var sleepEfficiency: Double?
    var totalSleepTimeMinutes: Double?
    var stageDurations: [String: Double]?
    
    // 무호흡 분석
    var ahi: Double?
    var severity: String?
    var eventCount: Int?
    
    // 질병 위험
    var predictions: [DiseasePrediction]?
    
    enum CodingKeys: String, CodingKey {
        case sleepEfficiency = "sleep_efficiency"
        case totalSleepTimeMinutes = "total_sleep_time_minutes"
        case stageDurations = "stage_durations"
        case ahi
        case severity
        case eventCount = "event_count"
        case predictions
    }
}

/// 질병 예측 결과
struct DiseasePrediction: Codable, Identifiable {
    var id: String { disease }
    let disease: String
    let diseaseNameKo: String
    let riskScore: Double
    let category: String
    let confidenceInterval: ConfidenceInterval
    let recommendations: [String]?
    
    enum CodingKeys: String, CodingKey {
        case disease
        case diseaseNameKo = "disease_name_ko"
        case riskScore = "risk_score"
        case category
        case confidenceInterval = "confidence_interval"
        case recommendations
    }
}

/// 신뢰 구간
struct ConfidenceInterval: Codable {
    let lower: Double
    let upper: Double
}
