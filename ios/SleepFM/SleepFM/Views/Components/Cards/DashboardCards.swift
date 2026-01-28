//
//  DashboardCards.swift
//  SleepFM
//
//  대시보드용 카드 컴포넌트
//

import SwiftUI

// MARK: - 수면 요약 카드

/// 수면 요약 카드
struct SleepSummaryCard: View {
    let totalSleepTime: TimeInterval
    let efficiency: Double
    let sleepScore: Double
    let bedTime: Date
    let wakeTime: Date
    var onTap: (() -> Void)?
    
    var body: some View {
        Button(action: { onTap?() }) {
            VStack(spacing: SleepSpacing.md) {
                // 헤더
                HStack {
                    HStack(spacing: SleepSpacing.xs) {
                        Image(systemName: "moon.stars.fill")
                            .foregroundColor(.sleepPrimary)
                        
                        Text("어젯밤 수면")
                            .font(SleepTypography.headline)
                            .foregroundColor(.sleepTextPrimary)
                    }
                    
                    Spacer()
                    
                    Image(systemName: "chevron.right")
                        .font(.system(size: 14))
                        .foregroundColor(.sleepTextSecondary)
                }
                
                HStack(alignment: .top, spacing: SleepSpacing.lg) {
                    // 수면 점수 링
                    SleepScoreRing(score: sleepScore, size: 100, lineWidth: 10)
                    
                    // 상세 정보
                    VStack(alignment: .leading, spacing: SleepSpacing.sm) {
                        SummaryRow(icon: "clock.fill", title: "수면 시간", value: formattedDuration)
                        SummaryRow(icon: "percent", title: "수면 효율", value: "\(Int(efficiency))%")
                        SummaryRow(icon: "bed.double.fill", title: "취침", value: formattedTime(bedTime))
                        SummaryRow(icon: "sun.max.fill", title: "기상", value: formattedTime(wakeTime))
                    }
                }
            }
            .padding(SleepSpacing.lg)
            .background(Color.sleepCardBackground)
            .cornerRadius(SleepCornerRadius.large)
        }
        .buttonStyle(.plain)
    }
    
    private var formattedDuration: String {
        let hours = Int(totalSleepTime / 3600)
        let minutes = Int((totalSleepTime.truncatingRemainder(dividingBy: 3600)) / 60)
        return "\(hours)시간 \(minutes)분"
    }
    
    private func formattedTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm"
        return formatter.string(from: date)
    }
}

/// 요약 행
struct SummaryRow: View {
    let icon: String
    let title: String
    let value: String
    
    var body: some View {
        HStack(spacing: SleepSpacing.sm) {
            Image(systemName: icon)
                .font(.system(size: 12))
                .foregroundColor(.sleepTextSecondary)
                .frame(width: 16)
            
            Text(title)
                .font(SleepTypography.caption1)
                .foregroundColor(.sleepTextSecondary)
            
            Spacer()
            
            Text(value)
                .font(SleepTypography.subheadline)
                .fontWeight(.medium)
                .foregroundColor(.sleepTextPrimary)
        }
    }
}

// MARK: - 수면 단계 카드

/// 수면 단계 요약 카드
struct SleepStagesSummaryCard: View {
    let stageDurations: [SleepStage: TimeInterval]
    var onTap: (() -> Void)?
    
    private var totalDuration: TimeInterval {
        stageDurations.values.reduce(0, +)
    }
    
    var body: some View {
        Button(action: { onTap?() }) {
            VStack(spacing: SleepSpacing.md) {
                // 헤더
                HStack {
                    Text("수면 단계")
                        .font(SleepTypography.headline)
                        .foregroundColor(.sleepTextPrimary)
                    
                    Spacer()
                    
                    Image(systemName: "chevron.right")
                        .font(.system(size: 14))
                        .foregroundColor(.sleepTextSecondary)
                }
                
                // 막대 차트
                SleepStageBarChart(stageDurations: stageDurations)
                
                // 단계별 시간
                VStack(spacing: SleepSpacing.xs) {
                    ForEach([SleepStage.n3, .n2, .n1, .rem, .wake], id: \.self) { stage in
                        if let duration = stageDurations[stage], duration > 0 {
                            StageTimeRow(
                                stage: stage,
                                duration: duration,
                                percentage: duration / totalDuration * 100
                            )
                        }
                    }
                }
            }
            .padding(SleepSpacing.lg)
            .background(Color.sleepCardBackground)
            .cornerRadius(SleepCornerRadius.large)
        }
        .buttonStyle(.plain)
    }
}

/// 단계 시간 행
struct StageTimeRow: View {
    let stage: SleepStage
    let duration: TimeInterval
    let percentage: Double
    
    var body: some View {
        HStack {
            Circle()
                .fill(colorForStage(stage))
                .frame(width: 8, height: 8)
            
            Text(stage.name)
                .font(SleepTypography.caption1)
                .foregroundColor(.sleepTextSecondary)
            
            Spacer()
            
            Text(formattedDuration)
                .font(SleepTypography.subheadline)
                .foregroundColor(.sleepTextPrimary)
            
            Text("(\(Int(percentage))%)")
                .font(SleepTypography.caption2)
                .foregroundColor(.sleepTextSecondary)
                .frame(width: 40, alignment: .trailing)
        }
    }
    
    private var formattedDuration: String {
        let hours = Int(duration / 3600)
        let minutes = Int((duration.truncatingRemainder(dividingBy: 3600)) / 60)
        if hours > 0 {
            return "\(hours)시간 \(minutes)분"
        } else {
            return "\(minutes)분"
        }
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

// MARK: - 질병 위험 카드

/// 질병 위험 카드
struct DiseaseRiskCard: View {
    let disease: String
    let diseaseNameKo: String
    let score: Double
    let category: RiskCategory
    var trend: TrendDirection?
    var onTap: (() -> Void)?
    
    var body: some View {
        Button(action: { onTap?() }) {
            HStack(spacing: SleepSpacing.md) {
                // 게이지
                DiseaseRiskGaugeChart(score: score, category: category, size: 60)
                
                // 정보
                VStack(alignment: .leading, spacing: SleepSpacing.xxs) {
                    Text(diseaseNameKo)
                        .font(SleepTypography.headline)
                        .foregroundColor(.sleepTextPrimary)
                    
                    HStack(spacing: SleepSpacing.xs) {
                        Text(category.label)
                            .font(SleepTypography.caption1)
                            .foregroundColor(category.color)
                        
                        if let trend = trend {
                            TrendBadge(direction: trend)
                        }
                    }
                }
                
                Spacer()
                
                // 점수
                VStack(alignment: .trailing, spacing: 2) {
                    Text("\(Int(score))")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(category.color)
                    
                    Text("점")
                        .font(SleepTypography.caption2)
                        .foregroundColor(.sleepTextSecondary)
                }
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14))
                    .foregroundColor(.sleepTextSecondary)
            }
            .padding(SleepSpacing.md)
            .background(Color.sleepCardBackground)
            .cornerRadius(SleepCornerRadius.large)
        }
        .buttonStyle(.plain)
    }
}

/// 질병 위험 미니 카드 (대시보드용)
struct DiseaseRiskMiniCard: View {
    let diseaseNameKo: String
    let score: Double
    let category: RiskCategory
    var onTap: (() -> Void)?
    
    var body: some View {
        Button(action: { onTap?() }) {
            VStack(alignment: .leading, spacing: SleepSpacing.sm) {
                HStack {
                    Text(diseaseNameKo)
                        .font(SleepTypography.caption1)
                        .foregroundColor(.sleepTextSecondary)
                    
                    Spacer()
                    
                    Text("\(Int(score))")
                        .font(SleepTypography.headline)
                        .foregroundColor(category.color)
                }
                
                DiseaseRiskMiniBar(score: score, category: category)
            }
            .padding(SleepSpacing.md)
            .background(Color.sleepCardBackground.opacity(0.5))
            .cornerRadius(SleepCornerRadius.medium)
        }
        .buttonStyle(.plain)
    }
}

// MARK: - 트렌드 방향

enum TrendDirection {
    case up
    case down
    case stable
    
    var icon: String {
        switch self {
        case .up: return "arrow.up.right"
        case .down: return "arrow.down.right"
        case .stable: return "arrow.right"
        }
    }
    
    var color: Color {
        switch self {
        case .up: return .red
        case .down: return .green
        case .stable: return .gray
        }
    }
}

/// 트렌드 배지
struct TrendBadge: View {
    let direction: TrendDirection
    var value: String?
    
    var body: some View {
        HStack(spacing: 2) {
            Image(systemName: direction.icon)
                .font(.system(size: 10, weight: .bold))
            
            if let value = value {
                Text(value)
                    .font(.system(size: 10, weight: .medium))
            }
        }
        .foregroundColor(direction.color)
        .padding(.horizontal, 6)
        .padding(.vertical, 3)
        .background(direction.color.opacity(0.15))
        .cornerRadius(4)
    }
}

// MARK: - Preview

#Preview {
    ScrollView {
        VStack(spacing: 16) {
            SleepSummaryCard(
                totalSleepTime: 7.5 * 3600,
                efficiency: 87,
                sleepScore: 82,
                bedTime: Calendar.current.date(bySettingHour: 23, minute: 30, second: 0, of: Date())!,
                wakeTime: Calendar.current.date(bySettingHour: 7, minute: 0, second: 0, of: Date())!
            )
            
            SleepStagesSummaryCard(stageDurations: [
                .n3: 90 * 60,
                .n2: 180 * 60,
                .n1: 30 * 60,
                .rem: 120 * 60,
                .wake: 20 * 60
            ])
            
            DiseaseRiskCard(
                disease: "parkinsons",
                diseaseNameKo: "파킨슨병",
                score: 35,
                category: .moderate,
                trend: .down
            )
            
            HStack(spacing: 12) {
                DiseaseRiskMiniCard(
                    diseaseNameKo: "치매",
                    score: 22,
                    category: .low
                )
                
                DiseaseRiskMiniCard(
                    diseaseNameKo: "심근경색",
                    score: 58,
                    category: .high
                )
            }
        }
        .padding()
    }
    .background(Color.sleepBackground)
}
