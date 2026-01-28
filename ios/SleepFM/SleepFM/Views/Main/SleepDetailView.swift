//
//  SleepDetailView.swift
//  SleepFM
//
//  수면 분석 상세 화면 (Story 7.2)
//

import SwiftUI
import Charts

/// 수면 상세 화면
struct SleepDetailView: View {
    let sessionId: String?
    let date: Date
    
    @StateObject private var viewModel = SleepDetailViewModel()
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            Color.sleepBackground
                .ignoresSafeArea()
            
            if viewModel.isLoading {
                loadingView
            } else {
                contentView
            }
        }
        .navigationTitle("수면 분석")
        .navigationBarTitleDisplayMode(.inline)
        .toolbarBackground(Color.sleepBackground, for: .navigationBar)
        .task {
            await viewModel.loadSleepDetail(for: date)
        }
    }
    
    // MARK: - Loading View
    
    private var loadingView: some View {
        VStack(spacing: SleepSpacing.md) {
            ProgressView()
                .scaleEffect(1.5)
            
            Text("수면 데이터 불러오는 중...")
                .font(SleepTypography.body)
                .foregroundColor(.sleepTextSecondary)
        }
    }
    
    // MARK: - Content View
    
    private var contentView: some View {
        ScrollView {
            VStack(spacing: SleepSpacing.lg) {
                // 날짜 및 요약
                dateHeaderSection
                
                // 수면 점수 및 효율
                scoreSection
                
                // 수면 시간 요약
                sleepTimeSection
                
                // 수면 단계 차트
                sleepStageChartSection
                
                // 수면 단계 분석
                sleepStageBreakdownSection
                
                // 권장사항
                recommendationsSection
            }
            .padding(.horizontal, SleepSpacing.lg)
            .padding(.bottom, SleepSpacing.xxl)
        }
    }
    
    // MARK: - Date Header
    
    private var dateHeaderSection: some View {
        VStack(spacing: SleepSpacing.xs) {
            Text(formattedDate)
                .font(SleepTypography.title2)
                .foregroundColor(.sleepTextPrimary)
            
            if let bed = viewModel.bedTime, let wake = viewModel.wakeTime {
                Text("\(formattedTime(bed)) - \(formattedTime(wake))")
                    .font(SleepTypography.body)
                    .foregroundColor(.sleepTextSecondary)
            }
        }
        .frame(maxWidth: .infinity)
        .padding(.top, SleepSpacing.md)
    }
    
    // MARK: - Score Section
    
    private var scoreSection: some View {
        HStack(spacing: SleepSpacing.xl) {
            // 수면 점수
            VStack(spacing: SleepSpacing.sm) {
                SleepScoreRing(score: viewModel.sleepScore, size: 140, lineWidth: 14)
            }
            
            // 수면 효율
            VStack(spacing: SleepSpacing.sm) {
                SleepEfficiencyGauge(efficiency: viewModel.sleepEfficiency, size: 140)
            }
        }
        .padding(.vertical, SleepSpacing.md)
    }
    
    // MARK: - Sleep Time Section
    
    private var sleepTimeSection: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Text("수면 시간")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
            }
            
            HStack(spacing: SleepSpacing.lg) {
                TimeStatCard(
                    icon: "bed.double.fill",
                    title: "취침",
                    time: viewModel.bedTime,
                    color: .sleepPrimary
                )
                
                TimeStatCard(
                    icon: "sun.max.fill",
                    title: "기상",
                    time: viewModel.wakeTime,
                    color: .orange
                )
                
                TimeStatCard(
                    icon: "clock.fill",
                    title: "총 시간",
                    duration: viewModel.totalSleepTime,
                    color: .sleepSecondary
                )
            }
        }
        .padding(SleepSpacing.lg)
        .background(Color.sleepCardBackground)
        .cornerRadius(SleepCornerRadius.large)
    }
    
    // MARK: - Sleep Stage Chart Section
    
    private var sleepStageChartSection: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Text("수면 단계 타임라인")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
            }
            
            if let bed = viewModel.bedTime, let wake = viewModel.wakeTime {
                SleepStageChart(
                    data: viewModel.sleepStageData,
                    startTime: bed,
                    endTime: wake,
                    height: 180
                )
            }
        }
        .padding(SleepSpacing.lg)
        .background(Color.sleepCardBackground)
        .cornerRadius(SleepCornerRadius.large)
    }
    
    // MARK: - Sleep Stage Breakdown Section
    
    private var sleepStageBreakdownSection: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Text("수면 단계 분석")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
            }
            
            // 파이 차트
            sleepStagePieChart
            
            Divider()
                .background(Color.sleepTextDisabled.opacity(0.3))
            
            // 각 단계별 상세
            VStack(spacing: SleepSpacing.sm) {
                ForEach([SleepStage.n3, .n2, .n1, .rem, .wake], id: \.self) { stage in
                    if let duration = viewModel.stageDurations[stage], duration > 0 {
                        SleepStageDetailRow(
                            stage: stage,
                            duration: duration,
                            percentage: stagePercentage(stage),
                            recommendation: stageRecommendation(stage)
                        )
                    }
                }
            }
        }
        .padding(SleepSpacing.lg)
        .background(Color.sleepCardBackground)
        .cornerRadius(SleepCornerRadius.large)
    }
    
    private var sleepStagePieChart: some View {
        let totalDuration = viewModel.stageDurations.values.reduce(0, +)
        
        return Chart {
            ForEach([SleepStage.n3, .n2, .n1, .rem, .wake], id: \.self) { stage in
                if let duration = viewModel.stageDurations[stage], duration > 0 {
                    SectorMark(
                        angle: .value("Duration", duration),
                        innerRadius: .ratio(0.5),
                        outerRadius: .ratio(1.0)
                    )
                    .foregroundStyle(colorForStage(stage))
                    .annotation(position: .overlay) {
                        if duration / totalDuration > 0.1 {
                            Text(stage.shortName)
                                .font(.system(size: 10, weight: .bold))
                                .foregroundColor(.white)
                        }
                    }
                }
            }
        }
        .frame(height: 200)
    }
    
    // MARK: - Recommendations Section
    
    private var recommendationsSection: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Image(systemName: "lightbulb.fill")
                    .foregroundColor(.yellow)
                
                Text("맞춤 권장사항")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
            }
            
            ForEach(viewModel.recommendations, id: \.self) { recommendation in
                RecommendationRow(text: recommendation)
            }
        }
        .padding(SleepSpacing.lg)
        .background(Color.sleepCardBackground)
        .cornerRadius(SleepCornerRadius.large)
    }
    
    // MARK: - Helpers
    
    private var formattedDate: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ko_KR")
        formatter.dateFormat = "M월 d일 EEEE"
        return formatter.string(from: date)
    }
    
    private func formattedTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: date)
    }
    
    private func stagePercentage(_ stage: SleepStage) -> Double {
        let total = viewModel.stageDurations.values.reduce(0, +)
        guard total > 0, let duration = viewModel.stageDurations[stage] else { return 0 }
        return (duration / total) * 100
    }
    
    private func stageRecommendation(_ stage: SleepStage) -> String? {
        let percentage = stagePercentage(stage)
        
        switch stage {
        case .n3:
            if percentage < 15 { return "깊은 수면이 부족해요. 규칙적인 운동을 추천드려요." }
        case .rem:
            if percentage < 20 { return "REM 수면이 부족해요. 스트레스 관리가 필요해요." }
        case .wake:
            if percentage > 10 { return "수면 중 각성이 잦아요. 수면 환경을 점검해보세요." }
        default:
            break
        }
        return nil
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

// MARK: - Supporting Views

struct TimeStatCard: View {
    let icon: String
    let title: String
    var time: Date?
    var duration: TimeInterval?
    let color: Color
    
    var body: some View {
        VStack(spacing: SleepSpacing.xs) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)
            
            Text(title)
                .font(SleepTypography.caption1)
                .foregroundColor(.sleepTextSecondary)
            
            if let time = time {
                Text(formattedTime(time))
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
            } else if let duration = duration {
                Text(formattedDuration(duration))
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
            }
        }
        .frame(maxWidth: .infinity)
    }
    
    private func formattedTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: date)
    }
    
    private func formattedDuration(_ seconds: TimeInterval) -> String {
        let hours = Int(seconds / 3600)
        let minutes = Int((seconds.truncatingRemainder(dividingBy: 3600)) / 60)
        return "\(hours)h \(minutes)m"
    }
}

struct SleepStageDetailRow: View {
    let stage: SleepStage
    let duration: TimeInterval
    let percentage: Double
    var recommendation: String?
    
    var body: some View {
        VStack(alignment: .leading, spacing: SleepSpacing.xs) {
            HStack {
                Circle()
                    .fill(colorForStage(stage))
                    .frame(width: 12, height: 12)
                
                Text(stage.name)
                    .font(SleepTypography.subheadline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
                
                Text(formattedDuration)
                    .font(SleepTypography.subheadline)
                    .foregroundColor(.sleepTextPrimary)
                
                Text("(\(Int(percentage))%)")
                    .font(SleepTypography.caption1)
                    .foregroundColor(.sleepTextSecondary)
                    .frame(width: 45, alignment: .trailing)
            }
            
            if let rec = recommendation {
                Text(rec)
                    .font(SleepTypography.caption1)
                    .foregroundColor(.sleepWarning)
                    .padding(.leading, 20)
            }
        }
        .padding(.vertical, SleepSpacing.xs)
    }
    
    private var formattedDuration: String {
        let hours = Int(duration / 3600)
        let minutes = Int((duration.truncatingRemainder(dividingBy: 3600)) / 60)
        if hours > 0 {
            return "\(hours)시간 \(minutes)분"
        }
        return "\(minutes)분"
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

struct RecommendationRow: View {
    let text: String
    
    var body: some View {
        HStack(alignment: .top, spacing: SleepSpacing.sm) {
            Image(systemName: "checkmark.circle.fill")
                .foregroundColor(.sleepSuccess)
                .font(.system(size: 14))
            
            Text(text)
                .font(SleepTypography.body)
                .foregroundColor(.sleepTextSecondary)
                .fixedSize(horizontal: false, vertical: true)
        }
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        SleepDetailView(sessionId: nil, date: Date())
    }
}
