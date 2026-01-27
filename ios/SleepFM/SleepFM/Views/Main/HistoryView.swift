//
//  HistoryView.swift
//  SleepFM
//
//  Created by SleepFM Team on 2026/01/27.
//

import SwiftUI

/// 수면 기록 화면
struct HistoryView: View {
    @EnvironmentObject var authManager: AuthManager
    @State private var selectedPeriod: TimePeriod = .week
    @State private var sessions: [SessionHistoryItem] = []
    @State private var isLoading = false
    @State private var selectedSession: SessionHistoryItem?
    
    enum TimePeriod: String, CaseIterable {
        case week = "주간"
        case month = "월간"
        case year = "연간"
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                // 배경
                Color.sleepBackground
                    .ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // 기간 선택
                    periodPicker
                    
                    // 요약 카드
                    summaryCard
                    
                    // 세션 목록
                    sessionList
                }
            }
            .navigationTitle("수면 기록")
            .navigationBarTitleDisplayMode(.large)
            .toolbarBackground(Color.sleepBackground, for: .navigationBar)
            .onAppear {
                loadSessions()
            }
        }
    }
    
    // MARK: - Period Picker
    
    private var periodPicker: some View {
        HStack(spacing: SleepSpacing.xs) {
            ForEach(TimePeriod.allCases, id: \.self) { period in
                Button {
                    withAnimation {
                        selectedPeriod = period
                        loadSessions()
                    }
                } label: {
                    Text(period.rawValue)
                        .font(SleepTypography.subheadline)
                        .foregroundColor(selectedPeriod == period ? .sleepTextPrimary : .sleepTextSecondary)
                        .padding(.horizontal, SleepSpacing.md)
                        .padding(.vertical, SleepSpacing.sm)
                        .background(
                            selectedPeriod == period ?
                            Color.sleepPrimary.opacity(0.2) : Color.clear
                        )
                        .cornerRadius(SleepCornerRadius.medium)
                }
            }
        }
        .padding(.horizontal, SleepSpacing.lg)
        .padding(.vertical, SleepSpacing.md)
    }
    
    // MARK: - Summary Card
    
    private var summaryCard: some View {
        VStack(spacing: SleepSpacing.md) {
            HStack {
                Text("기간 요약")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
                
                Spacer()
            }
            
            HStack(spacing: SleepSpacing.lg) {
                SummaryStatItem(
                    title: "평균 수면",
                    value: "7시간 12분",
                    trend: .up,
                    trendValue: "+15분"
                )
                
                Divider()
                    .background(Color.sleepTextDisabled.opacity(0.3))
                
                SummaryStatItem(
                    title: "평균 점수",
                    value: "76점",
                    trend: .up,
                    trendValue: "+3점"
                )
                
                Divider()
                    .background(Color.sleepTextDisabled.opacity(0.3))
                
                SummaryStatItem(
                    title: "기록 일수",
                    value: "\(sessions.count)일",
                    trend: nil,
                    trendValue: nil
                )
            }
        }
        .sleepCard()
        .padding(.horizontal, SleepSpacing.lg)
    }
    
    // MARK: - Session List
    
    private var sessionList: some View {
        ScrollView {
            LazyVStack(spacing: SleepSpacing.sm) {
                if isLoading {
                    ProgressView()
                        .tint(.sleepPrimary)
                        .padding(.top, SleepSpacing.xxl)
                } else if sessions.isEmpty {
                    emptyState
                } else {
                    ForEach(sessions) { session in
                        SessionCard(session: session)
                            .onTapGesture {
                                selectedSession = session
                            }
                    }
                }
            }
            .padding(.horizontal, SleepSpacing.lg)
            .padding(.top, SleepSpacing.md)
            .padding(.bottom, SleepSpacing.xxl)
        }
        .sheet(item: $selectedSession) { session in
            SessionDetailSheet(session: session)
        }
    }
    
    // MARK: - Empty State
    
    private var emptyState: some View {
        VStack(spacing: SleepSpacing.md) {
            Image(systemName: "moon.zzz")
                .font(.system(size: 60))
                .foregroundColor(.sleepTextDisabled)
            
            Text("기록된 수면 데이터가 없습니다")
                .font(SleepTypography.headline)
                .foregroundColor(.sleepTextSecondary)
            
            Text("수면 추적을 시작하여 건강한 수면 습관을 만들어보세요")
                .font(SleepTypography.subheadline)
                .foregroundColor(.sleepTextDisabled)
                .multilineTextAlignment(.center)
        }
        .padding(.top, SleepSpacing.xxl)
    }
    
    // MARK: - Data Loading
    
    private func loadSessions() {
        isLoading = true
        
        // 샘플 데이터 (실제로는 API에서 가져옴)
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            sessions = generateSampleSessions()
            isLoading = false
        }
    }
    
    private func generateSampleSessions() -> [SessionHistoryItem] {
        let calendar = Calendar.current
        var items: [SessionHistoryItem] = []
        
        let days = selectedPeriod == .week ? 7 : selectedPeriod == .month ? 30 : 365
        
        for i in 0..<min(days, 10) {
            guard let date = calendar.date(byAdding: .day, value: -i, to: Date()) else { continue }
            
            items.append(SessionHistoryItem(
                id: i,
                date: date,
                sleepDuration: Double.random(in: 5...9),
                sleepScore: Int.random(in: 50...95),
                bedtime: "23:\(Int.random(in: 0...59))",
                wakeTime: "07:\(Int.random(in: 0...59))",
                deepSleepPercentage: Double.random(in: 10...25),
                remSleepPercentage: Double.random(in: 15...30)
            ))
        }
        
        return items
    }
}

// MARK: - Supporting Views

struct SummaryStatItem: View {
    let title: String
    let value: String
    let trend: Trend?
    let trendValue: String?
    
    enum Trend {
        case up, down
        
        var color: Color {
            self == .up ? .sleepSuccess : .sleepDanger
        }
        
        var icon: String {
            self == .up ? "arrow.up" : "arrow.down"
        }
    }
    
    var body: some View {
        VStack(spacing: SleepSpacing.xs) {
            Text(title)
                .font(SleepTypography.caption2)
                .foregroundColor(.sleepTextDisabled)
            
            Text(value)
                .font(SleepTypography.headline)
                .foregroundColor(.sleepTextPrimary)
            
            if let trend = trend, let trendValue = trendValue {
                HStack(spacing: SleepSpacing.xxs) {
                    Image(systemName: trend.icon)
                    Text(trendValue)
                }
                .font(SleepTypography.caption2)
                .foregroundColor(trend.color)
            }
        }
        .frame(maxWidth: .infinity)
    }
}

struct SessionHistoryItem: Identifiable {
    let id: Int
    let date: Date
    let sleepDuration: Double
    let sleepScore: Int
    let bedtime: String
    let wakeTime: String
    let deepSleepPercentage: Double
    let remSleepPercentage: Double
    
    var formattedDate: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "ko_KR")
        formatter.dateFormat = "M월 d일 (E)"
        return formatter.string(from: date)
    }
    
    var formattedDuration: String {
        let hours = Int(sleepDuration)
        let minutes = Int((sleepDuration - Double(hours)) * 60)
        return "\(hours)시간 \(minutes)분"
    }
}

struct SessionCard: View {
    let session: SessionHistoryItem
    
    var body: some View {
        HStack(spacing: SleepSpacing.md) {
            // 점수 원형
            ZStack {
                Circle()
                    .stroke(Color.sleepTextDisabled.opacity(0.2), lineWidth: 4)
                    .frame(width: 56, height: 56)
                
                Circle()
                    .trim(from: 0, to: Double(session.sleepScore) / 100)
                    .stroke(scoreColor, lineWidth: 4)
                    .frame(width: 56, height: 56)
                    .rotationEffect(.degrees(-90))
                
                Text("\(session.sleepScore)")
                    .font(SleepTypography.headline)
                    .foregroundColor(.sleepTextPrimary)
            }
            
            // 정보
            VStack(alignment: .leading, spacing: SleepSpacing.xs) {
                Text(session.formattedDate)
                    .font(SleepTypography.subheadline.bold())
                    .foregroundColor(.sleepTextPrimary)
                
                HStack(spacing: SleepSpacing.md) {
                    Label(session.formattedDuration, systemImage: "bed.double.fill")
                    Label("\(session.bedtime) - \(session.wakeTime)", systemImage: "clock.fill")
                }
                .font(SleepTypography.caption1)
                .foregroundColor(.sleepTextSecondary)
            }
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .foregroundColor(.sleepTextDisabled)
        }
        .sleepCard()
    }
    
    private var scoreColor: Color {
        switch session.sleepScore {
        case 80...100: return .sleepSuccess
        case 60..<80: return .sleepInfo
        case 40..<60: return .sleepWarning
        default: return .sleepDanger
        }
    }
}

struct SessionDetailSheet: View {
    let session: SessionHistoryItem
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationStack {
            ZStack {
                Color.sleepBackground
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: SleepSpacing.lg) {
                        // 점수 카드
                        VStack(spacing: SleepSpacing.md) {
                            Text("\(session.sleepScore)")
                                .font(SleepTypography.numberLarge)
                                .foregroundStyle(SleepGradients.sleepScore(score: Double(session.sleepScore)))
                            
                            Text("수면 점수")
                                .font(SleepTypography.headline)
                                .foregroundColor(.sleepTextSecondary)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, SleepSpacing.xl)
                        .sleepGradientCard()
                        
                        // 상세 정보
                        VStack(spacing: SleepSpacing.md) {
                            DetailRow(title: "취침 시간", value: session.bedtime)
                            DetailRow(title: "기상 시간", value: session.wakeTime)
                            DetailRow(title: "총 수면 시간", value: session.formattedDuration)
                            DetailRow(title: "깊은 수면", value: String(format: "%.0f%%", session.deepSleepPercentage))
                            DetailRow(title: "REM 수면", value: String(format: "%.0f%%", session.remSleepPercentage))
                        }
                        .sleepCard()
                    }
                    .padding(SleepSpacing.lg)
                }
            }
            .navigationTitle(session.formattedDate)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("닫기") {
                        dismiss()
                    }
                    .foregroundColor(.sleepPrimary)
                }
            }
        }
    }
}

struct DetailRow: View {
    let title: String
    let value: String
    
    var body: some View {
        HStack {
            Text(title)
                .font(SleepTypography.body)
                .foregroundColor(.sleepTextSecondary)
            
            Spacer()
            
            Text(value)
                .font(SleepTypography.body.bold())
                .foregroundColor(.sleepTextPrimary)
        }
    }
}

// MARK: - Preview

#Preview {
    HistoryView()
        .environmentObject(AuthManager())
}
