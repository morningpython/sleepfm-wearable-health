//
//  DashboardView.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI

/// 대시보드 화면
struct DashboardView: View {
    @EnvironmentObject var authManager: AuthManager
    @EnvironmentObject var healthKitManager: HealthKitManager
    @State private var sleepScore: Double = 78
    @State private var lastNightSleep: SleepSummaryData?
    @State private var isLoading = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                // 배경
                Color.sleepBackground
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: SleepSpacing.lg) {
                        // 인사말
                        greetingSection
                        
                        // 수면 점수 카드
                        sleepScoreCard
                        
                        // HealthKit 권한 요청 배너
                        if !healthKitManager.isAuthorized {
                            healthKitBanner
                        }
                        
                        // 어젯밤 수면 요약
                        if let sleep = lastNightSleep {
                            lastNightSummaryCard(sleep: sleep)
                        }
                        
                        // 빠른 분석 버튼
                        quickAnalysisSection
                        
                        // 최근 인사이트
                        recentInsightsSection
                    }
                    .padding(.horizontal, SleepSpacing.lg)
                    .padding(.bottom, SleepSpacing.xxl)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Text("SleepFM")
                        .font(SleepTypography.title2)
                        .foregroundColor(.sleepTextPrimary)
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button {
                        // TODO: 알림
                    } label: {
                        Image(systemName: "bell.fill")
                            .foregroundColor(.sleepTextSecondary)
                    }
                }
            }
            .onAppear {
                loadData()
            }
        }
    }
    
    // MARK: - Greeting Section
    
    private var greetingSection: some View {
        VStack(alignment: .leading, spacing: SleepSpacing.xs) {
            Text(greeting)
                .font(SleepTypography.headline)
                .foregroundColor(.sleepTextSecondary)
            
            Text(authManager.currentUser?.fullName ?? authManager.currentUser?.username ?? "사용자님")
                .font(SleepTypography.title1)
                .foregroundColor(.sleepTextPrimary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(.top, SleepSpacing.md)
    }
    
    private var greeting: String {
        let hour = Calendar.current.component(.hour, from: Date())
        switch hour {
        case 5..<12: return "좋은 아침이에요 ☀️"
        case 12..<17: return "좋은 오후에요 🌤"
        case 17..<21: return "좋은 저녁이에요 🌙"
        default: return "편안한 밤이에요 🌟"
        }
    }
    
    // MARK: - Sleep Score Card
    
    private var sleepScoreCard: some View {
        VStack(spacing: SleepSpacing.lg) {
            // 제목
            HStack {
                Text("수면 점수")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextSecondary)
                
                Spacer()
                
                Text("오늘")
                    .font(SleepTypography.caption1)
                    .foregroundColor(.sleepTextDisabled)
            }
            
            // 점수
            HStack(alignment: .bottom, spacing: SleepSpacing.xs) {
                Text("\(Int(sleepScore))")
                    .font(SleepTypography.numberLarge)
                    .foregroundStyle(SleepGradients.sleepScore(score: sleepScore))
                
                Text("/ 100")
                    .font(SleepTypography.title3)
                    .foregroundColor(.sleepTextDisabled)
                    .padding(.bottom, SleepSpacing.sm)
            }
            
            // 점수 평가
            HStack(spacing: SleepSpacing.xs) {
                Image(systemName: scoreIcon)
                    .foregroundColor(scoreColor)
                
                Text(scoreDescription)
                    .font(SleepTypography.subheadline)
                    .foregroundColor(scoreColor)
            }
            
            // 프로그레스 바
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.sleepTextDisabled.opacity(0.2))
                        .frame(height: 8)
                    
                    RoundedRectangle(cornerRadius: 4)
                        .fill(SleepGradients.sleepScore(score: sleepScore))
                        .frame(width: geometry.size.width * (sleepScore / 100), height: 8)
                }
            }
            .frame(height: 8)
        }
        .sleepGradientCard()
    }
    
    private var scoreIcon: String {
        switch sleepScore {
        case 80...100: return "star.fill"
        case 60..<80: return "hand.thumbsup.fill"
        case 40..<60: return "exclamationmark.triangle.fill"
        default: return "xmark.circle.fill"
        }
    }
    
    private var scoreColor: Color {
        switch sleepScore {
        case 80...100: return .sleepSuccess
        case 60..<80: return .sleepInfo
        case 40..<60: return .sleepWarning
        default: return .sleepDanger
        }
    }
    
    private var scoreDescription: String {
        switch sleepScore {
        case 80...100: return "훌륭한 수면이에요!"
        case 60..<80: return "좋은 수면이에요"
        case 40..<60: return "수면 개선이 필요해요"
        default: return "수면 관리가 필요해요"
        }
    }
    
    // MARK: - HealthKit Banner
    
    private var healthKitBanner: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack(spacing: SleepSpacing.sm) {
                Image(systemName: "heart.fill")
                    .font(.title2)
                    .foregroundColor(.sleepDanger)
                
                VStack(alignment: .leading, spacing: SleepSpacing.xxs) {
                    Text("건강 데이터 연결")
                        .font(SleepTypography.headline)
                        .foregroundColor(.sleepTextPrimary)
                    
                    Text("Apple Health와 연결하여 더 정확한 분석을 받으세요")
                        .font(SleepTypography.caption1)
                        .foregroundColor(.sleepTextSecondary)
                }
                
                Spacer()
            }
            
            Button("연결하기") {
                Task {
                    await healthKitManager.requestAuthorization()
                }
            }
            .buttonStyle(SecondaryButtonStyle())
        }
        .sleepCard()
    }
    
    // MARK: - Last Night Summary
    
    private func lastNightSummaryCard(sleep: SleepSummaryData) -> some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Text("어젯밤 수면")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
                
                NavigationLink {
                    // TODO: 상세 보기
                } label: {
                    Text("상세보기")
                        .font(SleepTypography.caption1)
                        .foregroundColor(.sleepPrimary)
                }
            }
            
            HStack(spacing: SleepSpacing.lg) {
                StatItem(
                    icon: "bed.double.fill",
                    title: "수면 시간",
                    value: formatDuration(sleep.totalSleepMinutes)
                )
                
                StatItem(
                    icon: "moon.fill",
                    title: "효율",
                    value: "\(Int(sleep.efficiency))%"
                )
                
                StatItem(
                    icon: "chart.bar.fill",
                    title: "깊은 수면",
                    value: formatDuration(sleep.deepSleepMinutes)
                )
            }
        }
        .sleepCard()
    }
    
    private func formatDuration(_ minutes: Double) -> String {
        let hours = Int(minutes) / 60
        let mins = Int(minutes) % 60
        return "\(hours)시간 \(mins)분"
    }
    
    // MARK: - Quick Analysis Section
    
    private var quickAnalysisSection: some View {
        VStack(alignment: .leading, spacing: SleepSpacing.md) {
            Text("빠른 분석")
                .font(SleepTypography.headline)
                .foregroundColor(.sleepTextPrimary)
            
            HStack(spacing: SleepSpacing.md) {
                QuickActionCard(
                    icon: "waveform.path.ecg",
                    title: "수면 단계",
                    color: .sleepPrimary
                ) {
                    // TODO: 수면 단계 분석
                }
                
                QuickActionCard(
                    icon: "lungs.fill",
                    title: "무호흡",
                    color: .sleepSecondary
                ) {
                    // TODO: 무호흡 분석
                }
                
                QuickActionCard(
                    icon: "heart.text.square.fill",
                    title: "건강 위험",
                    color: .sleepInfo
                ) {
                    // TODO: 건강 위험 분석
                }
            }
        }
    }
    
    // MARK: - Recent Insights Section
    
    private var recentInsightsSection: some View {
        VStack(alignment: .leading, spacing: SleepSpacing.md) {
            HStack {
                Text("최근 인사이트")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
                
                Button("더보기") {
                    // TODO: 모든 인사이트 보기
                }
                .font(SleepTypography.caption1)
                .foregroundColor(.sleepPrimary)
            }
            
            VStack(spacing: SleepSpacing.sm) {
                InsightCard(
                    icon: "lightbulb.fill",
                    title: "취침 시간 일관성",
                    description: "이번 주 취침 시간이 30분 이상 차이나는 날이 3일 있었어요. 일정한 취침 시간을 유지해보세요.",
                    type: .suggestion
                )
                
                InsightCard(
                    icon: "arrow.up.circle.fill",
                    title: "깊은 수면 증가",
                    description: "지난주 대비 깊은 수면이 15% 증가했어요!",
                    type: .positive
                )
            }
        }
    }
    
    // MARK: - Data Loading
    
    private func loadData() {
        isLoading = true
        
        // 샘플 데이터 (실제로는 API에서 가져옴)
        lastNightSleep = SleepSummaryData(
            totalSleepMinutes: 420,
            efficiency: 85,
            deepSleepMinutes: 90
        )
        
        Task {
            if healthKitManager.isAuthorized {
                await healthKitManager.fetchRecentSleepData()
            }
            isLoading = false
        }
    }
}

// MARK: - Supporting Types

struct SleepSummaryData {
    let totalSleepMinutes: Double
    let efficiency: Double
    let deepSleepMinutes: Double
}

struct StatItem: View {
    let icon: String
    let title: String
    let value: String
    
    var body: some View {
        VStack(spacing: SleepSpacing.xs) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(.sleepPrimary)
            
            Text(title)
                .font(SleepTypography.caption2)
                .foregroundColor(.sleepTextDisabled)
            
            Text(value)
                .font(SleepTypography.subheadline.bold())
                .foregroundColor(.sleepTextPrimary)
        }
        .frame(maxWidth: .infinity)
    }
}

struct QuickActionCard: View {
    let icon: String
    let title: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: SleepSpacing.sm) {
                ZStack {
                    Circle()
                        .fill(color.opacity(0.2))
                        .frame(width: 48, height: 48)
                    
                    Image(systemName: icon)
                        .font(.title3)
                        .foregroundColor(color)
                }
                
                Text(title)
                    .font(SleepTypography.caption1)
                    .foregroundColor(.sleepTextPrimary)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, SleepSpacing.md)
            .background(Color.sleepCardBackground)
            .cornerRadius(SleepCornerRadius.medium)
        }
    }
}

struct InsightCard: View {
    let icon: String
    let title: String
    let description: String
    let type: InsightType
    
    enum InsightType {
        case positive, negative, suggestion
        
        var color: Color {
            switch self {
            case .positive: return .sleepSuccess
            case .negative: return .sleepWarning
            case .suggestion: return .sleepInfo
            }
        }
    }
    
    var body: some View {
        HStack(alignment: .top, spacing: SleepSpacing.sm) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(type.color)
                .frame(width: 32)
            
            VStack(alignment: .leading, spacing: SleepSpacing.xxs) {
                Text(title)
                    .font(SleepTypography.subheadline.bold())
                    .foregroundColor(.sleepTextPrimary)
                
                Text(description)
                    .font(SleepTypography.caption1)
                    .foregroundColor(.sleepTextSecondary)
                    .lineLimit(3)
            }
            
            Spacer()
        }
        .sleepCard()
    }
}

// MARK: - Preview

#Preview {
    DashboardView()
        .environmentObject(AuthManager())
        .environmentObject(HealthKitManager())
}
