//
//  SleepStageChart.swift
//  SleepFM
//
//  수면 단계 타임라인 차트 - Swift Charts 활용
//

import SwiftUI
import Charts

/// 수면 단계 데이터 포인트
struct SleepStageDataPoint: Identifiable {
    let id = UUID()
    let time: Date
    let stage: SleepStage
    let epochIndex: Int
    
    var stageValue: Int {
        switch stage {
        case .wake: return 4
        case .rem: return 3
        case .n1: return 2
        case .n2: return 1
        case .n3: return 0
        }
    }
}

/// 수면 단계 타임라인 차트
struct SleepStageChart: View {
    let data: [SleepStageDataPoint]
    let startTime: Date
    let endTime: Date
    var showXAxisLabels: Bool = true
    var height: CGFloat = 200
    
    var body: some View {
        VStack(alignment: .leading, spacing: SleepSpacing.sm) {
            if !data.isEmpty {
                Chart {
                    ForEach(data) { point in
                        AreaMark(
                            x: .value("Time", point.time),
                            y: .value("Stage", point.stageValue)
                        )
                        .foregroundStyle(stageGradient)
                        .interpolationMethod(.stepEnd)
                        
                        LineMark(
                            x: .value("Time", point.time),
                            y: .value("Stage", point.stageValue)
                        )
                        .foregroundStyle(Color.sleepPrimary)
                        .interpolationMethod(.stepEnd)
                        .lineStyle(StrokeStyle(lineWidth: 2))
                    }
                }
                .chartXScale(domain: startTime...endTime)
                .chartYScale(domain: 0...4)
                .chartYAxis {
                    AxisMarks(values: [0, 1, 2, 3, 4]) { value in
                        AxisGridLine(stroke: StrokeStyle(lineWidth: 0.5, dash: [5]))
                            .foregroundStyle(Color.sleepTextDisabled.opacity(0.3))
                        AxisValueLabel {
                            if let intValue = value.as(Int.self) {
                                Text(stageLabelForValue(intValue))
                                    .font(.system(size: 10))
                                    .foregroundColor(.sleepTextSecondary)
                            }
                        }
                    }
                }
                .chartXAxis {
                    if showXAxisLabels {
                        AxisMarks(values: .stride(by: .hour, count: 2)) { value in
                            AxisGridLine(stroke: StrokeStyle(lineWidth: 0.5, dash: [5]))
                                .foregroundStyle(Color.sleepTextDisabled.opacity(0.3))
                            AxisValueLabel(format: .dateTime.hour())
                                .foregroundStyle(Color.sleepTextSecondary)
                        }
                    }
                }
                .frame(height: height)
            } else {
                // 빈 상태
                VStack(spacing: SleepSpacing.md) {
                    Image(systemName: "chart.xyaxis.line")
                        .font(.system(size: 40))
                        .foregroundColor(.sleepTextDisabled)
                    
                    Text("수면 데이터가 없습니다")
                        .font(SleepTypography.body)
                        .foregroundColor(.sleepTextSecondary)
                }
                .frame(height: height)
                .frame(maxWidth: .infinity)
            }
            
            // 범례
            legendView
        }
    }
    
    // MARK: - Helpers
    
    private var stageGradient: LinearGradient {
        LinearGradient(
            colors: [
                Color.sleepPrimary.opacity(0.3),
                Color.sleepPrimary.opacity(0.1)
            ],
            startPoint: .top,
            endPoint: .bottom
        )
    }
    
    private func stageLabelForValue(_ value: Int) -> String {
        switch value {
        case 0: return "N3"
        case 1: return "N2"
        case 2: return "N1"
        case 3: return "REM"
        case 4: return "W"
        default: return ""
        }
    }
    
    private var legendView: some View {
        HStack(spacing: SleepSpacing.lg) {
            ForEach([SleepStage.wake, .rem, .n1, .n2, .n3], id: \.self) { stage in
                HStack(spacing: 4) {
                    Circle()
                        .fill(colorForStage(stage))
                        .frame(width: 8, height: 8)
                    
                    Text(stage.shortName)
                        .font(.system(size: 10))
                        .foregroundColor(.sleepTextSecondary)
                }
            }
        }
        .padding(.top, SleepSpacing.xs)
    }
    
    private func colorForStage(_ stage: SleepStage) -> Color {
        switch stage {
        case .wake: return .orange
        case .rem: return .purple
        case .n1: return .blue.opacity(0.5)
        case .n2: return .blue.opacity(0.7)
        case .n3: return .blue
        }
    }
}

// MARK: - 수면 단계 막대 차트 (요약용)

struct SleepStageBarChart: View {
    let stageDurations: [SleepStage: TimeInterval]
    
    private var totalDuration: TimeInterval {
        stageDurations.values.reduce(0, +)
    }
    
    var body: some View {
        GeometryReader { geometry in
            HStack(spacing: 2) {
                ForEach([SleepStage.n3, .n2, .n1, .rem, .wake], id: \.self) { stage in
                    if let duration = stageDurations[stage], duration > 0 {
                        let width = (duration / totalDuration) * geometry.size.width
                        
                        RoundedRectangle(cornerRadius: 4)
                            .fill(colorForStage(stage))
                            .frame(width: max(width, 4))
                    }
                }
            }
        }
        .frame(height: 24)
    }
    
    private func colorForStage(_ stage: SleepStage) -> Color {
        switch stage {
        case .wake: return .orange
        case .rem: return .purple
        case .n1: return .blue.opacity(0.5)
        case .n2: return .blue.opacity(0.7)
        case .n3: return .blue
        }
    }
}

// MARK: - Preview

#Preview {
    VStack(spacing: 20) {
        // 샘플 데이터 생성
        let startTime = Calendar.current.date(bySettingHour: 23, minute: 0, second: 0, of: Date().addingTimeInterval(-86400))!
        let endTime = Calendar.current.date(bySettingHour: 7, minute: 0, second: 0, of: Date())!
        
        let sampleData: [SleepStageDataPoint] = (0..<960).map { i in
            let time = startTime.addingTimeInterval(Double(i) * 30) // 30초 에포크
            let stages: [SleepStage] = [.n1, .n2, .n3, .n2, .rem, .wake]
            let stage = stages[i % stages.count]
            return SleepStageDataPoint(time: time, stage: stage, epochIndex: i)
        }
        
        SleepStageChart(
            data: sampleData,
            startTime: startTime,
            endTime: endTime
        )
        .padding()
        .background(Color.sleepCardBackground)
        .cornerRadius(16)
        
        SleepStageBarChart(stageDurations: [
            .n3: 90 * 60,
            .n2: 180 * 60,
            .n1: 30 * 60,
            .rem: 120 * 60,
            .wake: 20 * 60
        ])
        .padding()
    }
    .padding()
    .background(Color.sleepBackground)
}
