//
//  DiseaseRiskChart.swift
//  SleepFM
//
//  질병 위험 스코어 차트 및 트렌드
//

import SwiftUI
import Charts

/// 질병 위험 데이터 포인트 (트렌드용)
struct RiskTrendDataPoint: Identifiable {
    let id = UUID()
    let date: Date
    let score: Double
}

/// 질병 위험 게이지 차트
struct DiseaseRiskGaugeChart: View {
    let score: Double
    let category: RiskCategory
    var size: CGFloat = 120
    
    var body: some View {
        ZStack {
            // 배경 원
            Circle()
                .stroke(
                    Color.sleepTextDisabled.opacity(0.2),
                    lineWidth: 12
                )
            
            // 진행 원
            Circle()
                .trim(from: 0, to: min(score / 100, 1))
                .stroke(
                    category.color,
                    style: StrokeStyle(lineWidth: 12, lineCap: .round)
                )
                .rotationEffect(.degrees(-90))
                .animation(.easeInOut(duration: 0.8), value: score)
            
            // 중앙 텍스트
            VStack(spacing: 2) {
                Text("\(Int(score))")
                    .font(.system(size: size * 0.28, weight: .bold))
                    .foregroundColor(category.color)
                
                Text(category.label)
                    .font(.system(size: size * 0.1))
                    .foregroundColor(.sleepTextSecondary)
            }
        }
        .frame(width: size, height: size)
    }
}

/// 위험 카테고리
enum RiskCategory: String, Codable {
    case low = "Low"
    case moderate = "Moderate"
    case high = "High"
    case veryHigh = "Very High"
    
    /// API 응답 문자열에서 초기화
    init(from string: String) {
        switch string.lowercased() {
        case "low", "낮음": self = .low
        case "moderate", "보통": self = .moderate
        case "high", "높음": self = .high
        case "very high", "veryhigh", "매우 높음": self = .veryHigh
        default: self = RiskCategory.fromScore(0)
        }
    }
    
    var label: String {
        switch self {
        case .low: return "낮음"
        case .moderate: return "보통"
        case .high: return "높음"
        case .veryHigh: return "매우 높음"
        }
    }
    
    var color: Color {
        switch self {
        case .low: return .green
        case .moderate: return .yellow
        case .high: return .orange
        case .veryHigh: return .red
        }
    }
    
    static func fromScore(_ score: Double) -> RiskCategory {
        switch score {
        case 0..<25: return .low
        case 25..<50: return .moderate
        case 50..<75: return .high
        default: return .veryHigh
        }
    }
}

/// 질병 위험 트렌드 차트
struct DiseaseRiskTrendChart: View {
    let data: [RiskTrendDataPoint]
    let disease: String
    var height: CGFloat = 150
    
    private var averageScore: Double {
        guard !data.isEmpty else { return 0 }
        return data.map(\.score).reduce(0, +) / Double(data.count)
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: SleepSpacing.sm) {
            // 헤더
            HStack {
                Text("트렌드")
                    .font(SleepTypography.subheadline)
                    .foregroundColor(.sleepTextSecondary)
                
                Spacer()
                
                Text("평균 \(Int(averageScore))점")
                    .font(SleepTypography.caption1)
                    .foregroundColor(.sleepTextSecondary)
            }
            
            if !data.isEmpty {
                Chart {
                    // 위험 영역 표시
                    RectangleMark(
                        xStart: nil,
                        xEnd: nil,
                        yStart: .value("", 50),
                        yEnd: .value("", 100)
                    )
                    .foregroundStyle(Color.red.opacity(0.1))
                    
                    RectangleMark(
                        xStart: nil,
                        xEnd: nil,
                        yStart: .value("", 25),
                        yEnd: .value("", 50)
                    )
                    .foregroundStyle(Color.orange.opacity(0.1))
                    
                    // 라인 차트
                    ForEach(data) { point in
                        LineMark(
                            x: .value("Date", point.date),
                            y: .value("Score", point.score)
                        )
                        .foregroundStyle(Color.sleepPrimary)
                        .lineStyle(StrokeStyle(lineWidth: 2))
                        
                        AreaMark(
                            x: .value("Date", point.date),
                            y: .value("Score", point.score)
                        )
                        .foregroundStyle(
                            LinearGradient(
                                colors: [Color.sleepPrimary.opacity(0.3), Color.clear],
                                startPoint: .top,
                                endPoint: .bottom
                            )
                        )
                        
                        PointMark(
                            x: .value("Date", point.date),
                            y: .value("Score", point.score)
                        )
                        .foregroundStyle(Color.sleepPrimary)
                        .symbolSize(30)
                    }
                }
                .chartYScale(domain: 0...100)
                .chartYAxis {
                    AxisMarks(values: [0, 25, 50, 75, 100]) { value in
                        AxisGridLine(stroke: StrokeStyle(lineWidth: 0.5, dash: [3]))
                            .foregroundStyle(Color.sleepTextDisabled.opacity(0.3))
                        AxisValueLabel()
                            .foregroundStyle(Color.sleepTextSecondary)
                    }
                }
                .chartXAxis {
                    AxisMarks { value in
                        AxisValueLabel(format: .dateTime.day().month())
                            .foregroundStyle(Color.sleepTextSecondary)
                    }
                }
                .frame(height: height)
            } else {
                // 빈 상태
                VStack(spacing: SleepSpacing.sm) {
                    Image(systemName: "chart.line.uptrend.xyaxis")
                        .font(.system(size: 30))
                        .foregroundColor(.sleepTextDisabled)
                    
                    Text("트렌드 데이터가 부족합니다")
                        .font(SleepTypography.caption1)
                        .foregroundColor(.sleepTextSecondary)
                }
                .frame(height: height)
                .frame(maxWidth: .infinity)
            }
        }
    }
}

/// 질병 위험 미니 바 (카드용)
struct DiseaseRiskMiniBar: View {
    let score: Double
    let category: RiskCategory
    
    var body: some View {
        GeometryReader { geometry in
            ZStack(alignment: .leading) {
                // 배경
                RoundedRectangle(cornerRadius: 4)
                    .fill(Color.sleepTextDisabled.opacity(0.2))
                
                // 진행
                RoundedRectangle(cornerRadius: 4)
                    .fill(category.color)
                    .frame(width: geometry.size.width * (score / 100))
            }
        }
        .frame(height: 6)
    }
}

// MARK: - Preview

#Preview {
    ScrollView {
        VStack(spacing: 30) {
            // 게이지 차트
            HStack(spacing: 20) {
                DiseaseRiskGaugeChart(score: 25, category: .low)
                DiseaseRiskGaugeChart(score: 45, category: .moderate)
                DiseaseRiskGaugeChart(score: 72, category: .high, size: 80)
            }
            
            // 트렌드 차트
            let sampleTrend: [RiskTrendDataPoint] = (0..<7).map { i in
                RiskTrendDataPoint(
                    date: Calendar.current.date(byAdding: .day, value: -6 + i, to: Date())!,
                    score: Double.random(in: 20...60)
                )
            }
            
            DiseaseRiskTrendChart(data: sampleTrend, disease: "파킨슨병")
                .padding()
                .background(Color.sleepCardBackground)
                .cornerRadius(16)
            
            // 미니 바
            VStack(spacing: 10) {
                DiseaseRiskMiniBar(score: 25, category: .low)
                DiseaseRiskMiniBar(score: 55, category: .moderate)
                DiseaseRiskMiniBar(score: 78, category: .high)
            }
            .padding()
        }
        .padding()
    }
    .background(Color.sleepBackground)
}
